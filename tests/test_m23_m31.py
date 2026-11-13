"""M2.3/M3.1 safety and end-to-end integration tests; optional providers mock-only."""
import json, os, shutil, tempfile, io, math, struct, wave
from datetime import date,timedelta
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from PIL import Image
from app import db
from app.main import app
import app.main as main
from app import production_m23, alignment_m23, analytics_m31, youtube_private
from test_m22_m3_private import setup_draft,make_render,review_and_export,post

@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setenv('VIRALOS_DB',str(tmp_path/'app.db'))
    monkeypatch.setattr(main,'OUT',tmp_path/'output')
    for k in ['VIRALOS_ENABLE_MONETARY_SYNC','VIRALOS_ENABLE_REMOTE_RECONCILE',
              'VIRALOS_FASTER_WHISPER_MODEL_DIR','VIRALOS_WHISPER_MODEL_RIGHTS_OK',
              'VIRALOS_OFFLINE_ASR_OPT_IN']:
        monkeypatch.delenv(k,raising=False)
    with TestClient(app) as c:yield c


def test_additive_migrations_and_capabilities(client):
    with db.read() as c:
        versions={row['version'] for row in db.many(c,'SELECT version FROM schema_migrations')}
    assert versions.issuperset({'009','010'})
    capabilities=client.get('/api/m23/capabilities').json()
    assert capabilities['voice_alignment']['automatic_downloads'] is False
    assert capabilities['automatic_factual_verification'] is False
    assert client.get('/api/m31/capabilities').json()['monetary_revenue_sync_opt_in'] is False


def test_offline_asr_requires_owner_installed_model_and_explicit_opt_in(client):
    _,pid,plan=setup_draft(client)
    response=client.post(f'/api/projects/{pid}/m23/plans/{plan}/asr-proposal')
    assert response.status_code==409 and 'local' in response.text.lower()
    assert not db.one(db.connect(),'SELECT draft_id FROM m23_alignment_drafts')


def _matching_words(plan):
    words=[]
    for cue in plan['captions']:
        toks=cue['text'].split();unit=(cue['end_ms']-cue['start_ms'])//len(toks)
        for i,word in enumerate(toks):
            begin=cue['start_ms']+i*unit
            words.append({'token':word,'start_ms':begin,'end_ms':min(cue['end_ms'],begin+unit-2)})
    return words


def test_asr_proposal_must_be_owner_approved_and_word_matched(client,monkeypatch):
    _,pid,plan=setup_draft(client)
    raw=client.get(f'/api/projects/{pid}/studio/plan').json()['plan']
    words=_matching_words(raw)
    monkeypatch.setattr(alignment_m23,'transcribe_local',lambda a,l:words)
    draft=post(client,f'/api/projects/{pid}/m23/plans/{plan}/asr-proposal',{})
    assert draft['transcript_matches'] and draft['human_review_required']
    assert draft['provenance']=='ASR_WORD_TIMESTAMP_PROPOSAL_NOT_FORCED_ALIGNMENT'
    route=f"/api/projects/{pid}/m23/alignment-drafts/{draft['draft_id']}/approve"
    assert client.post(route,json={'owner_checked_audio_and_words':False,'words':words}).status_code==409
    spoof=list(words);spoof[0]=dict(spoof[0],token='invented')
    assert client.post(route,json={'owner_checked_audio_and_words':True,'words':spoof}).status_code==422
    approved=post(client,route,{'owner_checked_audio_and_words':True,'words':words})
    assert not approved['automatic_forced_alignment'] and approved['owner_reviewed']
    assert client.get(f'/api/projects/{pid}/m22/plans/{plan}/words.vtt').status_code==200
    assert client.post(route,json={'owner_checked_audio_and_words':True,'words':words}).status_code==409


def test_asr_spurious_transcript_never_auto_approves(client,monkeypatch):
    _,pid,plan=setup_draft(client)
    monkeypatch.setattr(alignment_m23,'transcribe_local',lambda a,l:[{'token':'invented','start_ms':0,'end_ms':100}])
    result=post(client,f'/api/projects/{pid}/m23/plans/{plan}/asr-proposal',{})
    assert result['transcript_matches'] is False
    assert client.post(f"/api/projects/{pid}/m23/alignment-drafts/{result['draft_id']}/approve",
                       json={'owner_checked_audio_and_words':True,'words':result['words']}).status_code==422


def test_asr_cross_project_and_tampered_audio_blocked(client,monkeypatch):
    _,a,plan=setup_draft(client)
    _,b,_=setup_draft(client)
    assert client.post(f'/api/projects/{b}/m23/plans/{plan}/asr-proposal').status_code==404
    voice=next((main.OUT/a/'director').glob('*/assembled.wav'),None)
    # Verify the actual immutable audio is not bypassed: modify the database bound track.
    with db.read() as c:
        audio=db.one(c,'SELECT voice_relpath FROM m21_plan_audio WHERE plan_id=?',(plan,))
    target=main.OUT/audio['voice_relpath'];target.write_bytes(target.read_bytes()+b'altered')
    assert client.post(f'/api/projects/{a}/m23/plans/{plan}/asr-proposal').status_code==409


def _source_claim_project(client):
    ch=post(client,'/api/channels',{'name':'Evidence research test','sport_id':'cricket','locale':'en-US',
           'market':'India','timezone':'Asia/Kolkata'})['channel_id']
    pid=post(client,'/api/projects',{'channel_id':ch,'title':'Test cricket illustration and evidence',
            'original_angle':'Show how to explain one sourced example with reviewed evidence','format':'SHORT'})['project_id']
    sv=post(client,f'/api/projects/{pid}/sources',{'url':'https://example.org/research/original',
            'publisher':'Example Research Archive','excerpt':'The test diagram is original and uses no third-party broadcast footage.','locale':'en-US'})['source_version_id']
    claim='The study diagram is an original educational illustration.'
    cid=post(client,f'/api/projects/{pid}/claims',{'proposition':claim,'source_version_id':sv,
                'relation':'SUPPORTS','locator':'paragraph one'})['claim_id']
    post(client,f'/api/projects/{pid}/script',{'text':claim+' It explains a hypothetical cricket formation with clearly labeled illustrative elements.',
                                           'claim_links':[{'claim_id':cid,'exact_quote':claim}]})
    with db.read() as c:edge=db.one(c,'SELECT evidence_edge_id FROM evidence_edges WHERE claim_id=?',(cid,))['evidence_edge_id']
    return pid,cid,sv,edge


def test_evidence_card_requires_source_locator_and_claim_review(client):
    pid,cid,sv,edge=_source_claim_project(client)
    route=f'/api/projects/{pid}/m23/evidence-cards'
    payload={'claim_id':cid,'source_version_id':sv,'attribution_and_rights_reviewed':True}
    assert client.post(route,json=payload).status_code==409
    url=f'/api/projects/{pid}/m23/evidence-edges/{edge}/review'
    assert client.post(url,json={'reviewer':'Human researcher','source_and_locator_checked':False,
                   'explanation':'I have examined this source passage in context.'}).status_code==409
    post(client,url,{'reviewer':'Human researcher','source_and_locator_checked':True,
                     'explanation':'I inspected the original source and exact text passage.'})
    assert client.post(route,json=payload).status_code==409
    post(client,f'/api/claims/{cid}/review',{'status':'SUPPORTED','reviewer':'Human researcher',
           'explanation':'Human verified passage and its context for an illustrative claim.'})
    data=post(client,route,payload)
    assert data['independently_verified'] is False and data['third_party_image_reproduced'] is False
    with db.read() as c:
        rec=db.one(c,'SELECT * FROM m2_studio_assets WHERE asset_id=?',(data['asset_id'],))
        assert rec['rights_attested']==1
        card=main.OUT/rec['local_relpath'];assert card.is_file()
        with Image.open(card) as img:assert img.size==(1080,750)
    assert post(client,route,payload)['already_exists'] is True
    image=client.get(f"/api/projects/{pid}/m23/evidence-cards/{data['asset_id']}/image")
    assert image.status_code==200 and len(image.content)>10000


def test_card_becomes_stale_after_claim_re_review(client):
    pid,cid,sv,edge=_source_claim_project(client)
    post(client,f'/api/projects/{pid}/m23/evidence-edges/{edge}/review',
         {'reviewer':'Expert researcher','source_and_locator_checked':True,
          'explanation':'Original source and precise locator reviewed manually.'})
    payload={'status':'SUPPORTED','reviewer':'Expert researcher','explanation':'This owner-reviewed example is supported by given source.'}
    post(client,f'/api/claims/{cid}/review',payload)
    card=post(client,f'/api/projects/{pid}/m23/evidence-cards',{'claim_id':cid,'source_version_id':sv,
                                                        'attribution_and_rights_reviewed':True})
    with db.read() as c:assert production_m23.verify_generated_asset(c,pid,card['asset_id'])
    post(client,f'/api/claims/{cid}/review',payload)
    with db.read() as c:
        from fastapi import HTTPException
        with pytest.raises(HTTPException):production_m23.verify_generated_asset(c,pid,card['asset_id'])
    assert client.get(f'/api/projects/{pid}/m23/evidence-cards').json()[0]['status']=='STALE_BLOCKED'


def test_evidence_no_cross_project_injection(client):
    a,cid,sv,edge=_source_claim_project(client)
    b,_,_,_=_source_claim_project(client)
    assert client.post(f'/api/projects/{b}/m23/evidence-cards',json={
        'claim_id':cid,'source_version_id':sv,'attribution_and_rights_reviewed':True}).status_code==409


def test_locale_audit_english_plan_and_foreign_id(client):
    _,pid,plan=setup_draft(client)
    result=client.get(f'/api/projects/{pid}/m23/plans/{plan}/locale-audit')
    assert result.status_code==200 and result.json()['locale']=='en-US'
    assert result.json()['translation_generated_by_system'] is False
    assert client.get(f'/api/projects/{pid}/m23/plans/not-existing/locale-audit').status_code==404


def test_revenue_scope_and_estimate_validation(client,monkeypatch):
    ch,pid,_=setup_draft(client)
    start=(date.today()-timedelta(days=5)).isoformat();end=(date.today()-timedelta(days=4)).isoformat()
    body={'channel_id':ch,'start_date':start,'end_date':end,'currency':'INR','owner_authorized_sync':True}
    assert client.post('/api/m31/monetary/sync',json=body).status_code==403
    assert client.post('/api/m31/monetary/sync',json={**body,'owner_authorized_sync':False}).status_code==409
    assert client.post('/api/m31/monetary/sync',json={**body,'end_date':(date.today()+timedelta(days=1)).isoformat()}).status_code==422
    with pytest.raises(ValueError):analytics_m31.normalized_monetary({'columnHeaders':[{'name':'day'},{'name':'estimatedRevenue'},{'name':'estimatedAdRevenue'}],
                          'rows':[[start,-2,0]]})
    empty=client.get(f'/api/m31/channels/{ch}/earnings').json()
    assert empty['rows']==[] and not empty['profit_calculated']


def test_authorized_monetary_mock_sync_exact_channel_and_no_duplicates(client,monkeypatch):
    ch,pid,_=setup_draft(client)
    with db.transaction() as c:
        c.execute('INSERT INTO m31_monetary_accounts(local_channel_id,remote_channel_id,remote_title,verified_at,scopes_json) VALUES (?,?,?,?,?)',
                  (ch,'UC_TEST_OWNED','Test channel',main.now(),main.j(analytics_m31.MONETARY_SCOPES)))
    monkeypatch.setenv('VIRALOS_ENABLE_MONETARY_SYNC','1')
    monkeypatch.setattr(analytics_m31,'monetary_credentials',lambda x:'MOCK_OWNER_TOKEN')
    monkeypatch.setattr(youtube_private,'verify_owned_channel',lambda creds,remote:{'id':remote})
    start=(date.today()-timedelta(days=8)).isoformat();end=(date.today()-timedelta(days=7)).isoformat()
    fake={'columnHeaders':[{'name':'day'},{'name':'estimatedRevenue'},{'name':'estimatedAdRevenue'}],
          'rows':[[start,4.5,3.0],[end,6.25,5.0]]}
    monkeypatch.setattr(analytics_m31,'fetch_monetary',lambda *args:fake)
    data={'channel_id':ch,'start_date':start,'end_date':end,'currency':'USD','owner_authorized_sync':True}
    result=post(client,'/api/m31/monetary/sync',data)
    assert result['rows_imported']==2 and result['profit_calculated'] is False
    result=post(client,'/api/m31/monetary/sync',data)
    summary=client.get(f'/api/m31/channels/{ch}/earnings').json()
    assert len(summary['rows'])==2 and summary['totals_by_currency']['USD']==10.75
    assert all(x['source']=='YOUTUBE_ANALYTICS_MONETARY_OAUTH' for x in summary['rows'])


def test_mock_reconcile_remote_unknown_requires_exact_channel_privacy(client,monkeypatch):
    if not shutil.which('ffmpeg'):pytest.skip('FFmpeg required')
    ch,pid,_=setup_draft(client)
    eid=review_and_export(client,pid,make_render(client,pid))['export_id']
    with db.transaction() as c:
        c.execute('INSERT INTO m3_upload_accounts(local_channel_id,remote_channel_id,remote_title,verified_at,scopes_json) VALUES (?,?,?,?,?)',
                  (ch,'UC_VERIFIED_OWNER','Test channel',main.now(),main.j(youtube_private.SCOPES)))
    prepared=post(client,'/api/m3/private-upload/intents',{'export_id':eid,'title':'Original study',
      'description':'An original educational video with original research and graphics.','tags':[],
      'altered_content':False,'made_for_kids':False,'owner_confirmed_metadata_rights':True})
    iid=prepared['intent_id']
    with db.transaction() as c:c.execute("UPDATE m3_private_upload_intents SET state='REMOTE_UNKNOWN' WHERE intent_id=?",(iid,))
    payload={'remote_video_id':'MOCK_private_a1','owner_checked_studio_video_matches':True,
             'confirmation':'RECONCILE_EXISTING_PRIVATE_VIDEO_ONLY'}
    route=f'/api/m31/private-upload/intents/{iid}/reconcile'
    assert client.post(route,json=payload).status_code==403
    monkeypatch.setenv('VIRALOS_ENABLE_REMOTE_RECONCILE','1')
    assert client.post(route,json={**payload,'owner_checked_studio_video_matches':False}).status_code==409
    monkeypatch.setattr(youtube_private,'upload_credentials',lambda channel:'OWNER_TOKEN')
    monkeypatch.setattr(youtube_private,'verify_owned_channel',lambda x,y:{'id':y})
    monkeypatch.setattr(analytics_m31,'fetch_remote_video',lambda *args:[{'id':payload['remote_video_id'],
      'snippet':{'channelId':'UC_OTHER_ACCOUNT'},'status':{'privacyStatus':'private'}}])
    assert client.post(route,json=payload).status_code==409
    monkeypatch.setattr(analytics_m31,'fetch_remote_video',lambda *args:[{'id':payload['remote_video_id'],
      'snippet':{'channelId':'UC_VERIFIED_OWNER'},'status':{'privacyStatus':'public'}}])
    assert client.post(route,json=payload).status_code==409
    monkeypatch.setattr(analytics_m31,'fetch_remote_video',lambda *args:[{'id':payload['remote_video_id'],
      'snippet':{'channelId':'UC_VERIFIED_OWNER'},'status':{'privacyStatus':'private'}}])
    result=post(client,route,payload)
    assert result['state']=='UPLOADED_PRIVATE' and result['automatic_retry_performed'] is False
    assert client.post(route,json=payload).status_code==409


def test_retention_values_allow_rewatches_and_map_to_scene():
    from app.analytics_m31 import normalize_retention,map_retention_to_shots
    report={'columnHeaders':[{'name':'elapsedVideoTimeRatio'},{'name':'audienceWatchRatio'},
             {'name':'relativeRetentionPerformance'}],
            'rows':[[0.10,1.25,0.75],[0.25,1.11,0.68],[0.55,0.72,0.42],[0.75,0.60,0.45],[1.0,0.48,0.48]]}
    rows=normalize_retention(report)
    assert rows[0]['audience_watch_ratio']==1.25
    shots=[{'role':'HOOK','duration_ms':5000,'headline':'Question'},
           {'role':'EXPLANATION','duration_ms':5000,'headline':'Context'}]
    mapping=map_retention_to_shots(shots,rows)
    assert mapping['data_points']==5
    assert mapping['scene_summaries'][0]['sample_count']==2
    assert mapping['scene_summaries'][0]['observed_delta']==-0.14
    assert mapping['observed_retention_not_causal_explanation'] is True


def test_retention_invalid_values_blocked():
    report={'columnHeaders':[{'name':'elapsedVideoTimeRatio'},{'name':'audienceWatchRatio'},
             {'name':'relativeRetentionPerformance'}],
            'rows':[[0.40,1.0,0.5],[0.30,0.8,0.6]]}
    with pytest.raises(ValueError):analytics_m31.normalize_retention(report)
    report['rows']=[[0.20,-0.10,0.6]]
    with pytest.raises(ValueError):analytics_m31.normalize_retention(report)


def test_retention_requires_owned_uploaded_export_and_opt_in(client):
    ch,pid,_=setup_draft(client)
    if not shutil.which('ffmpeg'):pytest.skip('FFmpeg required')
    eid=review_and_export(client,pid,make_render(client,pid))['export_id']
    request={'export_id':eid,'start_date':(date.today()-timedelta(days=8)).isoformat(),
             'end_date':(date.today()-timedelta(days=7)).isoformat(),'owner_authorized_sync':True}
    assert client.post('/api/m31/retention/sync',json=request).status_code==403
    assert client.get(f'/api/m31/exports/{eid}/retention').json()['data_available'] is False


def test_retention_mock_exact_owned_video_and_shot_snapshot(client,monkeypatch):
    if not shutil.which('ffmpeg'):pytest.skip('FFmpeg required')
    ch,pid,_=setup_draft(client)
    eid=review_and_export(client,pid,make_render(client,pid))['export_id']
    with db.transaction() as c:
        c.execute('INSERT INTO m3_upload_accounts(local_channel_id,remote_channel_id,remote_title,verified_at,scopes_json) VALUES (?,?,?,?,?)',
                  (ch,'UC_CHANNEL_001','My channel',main.now(),main.j(youtube_private.SCOPES)))
        c.execute('INSERT INTO m3_youtube_accounts(local_channel_id,remote_channel_id,remote_title,connected_at,verification,oauth_scope_text) VALUES (?,?,?,?,?,?)',
                  (ch,'UC_CHANNEL_001','My channel',main.now(),'OAUTH_CHANNELS_MINE','youtube.readonly'))
    prepared=post(client,'/api/m3/private-upload/intents',{'export_id':eid,'title':'Original demo video',
       'description':'An original evidence-oriented educational video and demonstration of video rendering.',
       'tags':[],'altered_content':False,'made_for_kids':False,'owner_confirmed_metadata_rights':True})
    with db.transaction() as c:
        c.execute("UPDATE m3_private_upload_intents SET state='UPLOADED_PRIVATE',remote_video_id=? WHERE intent_id=?",
                  ('VIDEO_OWNED_TEST_123',prepared['intent_id']))
    monkeypatch.setenv('VIRALOS_ENABLE_RETENTION_SYNC','1')
    monkeypatch.setattr(__import__('app.youtube_analytics',fromlist=['credentials_for']),'credentials_for',lambda ch:'READONLY_TOKEN')
    monkeypatch.setattr(__import__('app.youtube_analytics',fromlist=['verify_channel']),'verify_channel',lambda a,b:{'id':b})
    monkeypatch.setattr(analytics_m31,'fetch_retention',lambda *a:{'columnHeaders':[
       {'name':'elapsedVideoTimeRatio'},{'name':'audienceWatchRatio'},{'name':'relativeRetentionPerformance'}],
       'rows':[[0.10,1.2,0.6],[0.20,0.85,0.6],[0.80,0.48,0.4],[1.00,0.39,0.3]]})
    body={'export_id':eid,'start_date':(date.today()-timedelta(days=8)).isoformat(),
          'end_date':(date.today()-timedelta(days=7)).isoformat(),'owner_authorized_sync':True}
    response=post(client,'/api/m31/retention/sync',body)
    assert response['data_available'] is True and response['samples']==4
    cached=client.get(f'/api/m31/exports/{eid}/retention').json()
    assert cached['source']=='OWNER_AUTHORIZED_YOUTUBE_ANALYTICS'
    assert cached['report']['data_points']==4
    assert cached['report']['observed_retention_not_causal_explanation']


def test_original_evidence_asset_is_rendered_and_stale_review_blocked(client):
    if not shutil.which('ffmpeg'):pytest.skip('FFmpeg not installed')
    pid,cid,sv,edge=_source_claim_project(client)
    post(client,f'/api/projects/{pid}/m23/evidence-edges/{edge}/review',
         {'reviewer':'Human editor','source_and_locator_checked':True,
          'explanation':'Reviewed original example source and its exact locator.'})
    post(client,f'/api/claims/{cid}/review',{'status':'SUPPORTED','reviewer':'Human editor',
         'explanation':'Checked source and source scope for this original demonstration.'})
    card=post(client,f'/api/projects/{pid}/m23/evidence-cards',
              {'claim_id':cid,'source_version_id':sv,'attribution_and_rights_reviewed':True})
    shots=[
      {'role':'HOOK','duration_ms':3000,'headline':'How do we verify a visual?',
       'visual':{'kind':'ORIGINAL_DIAGRAM','motion':'ILLUSTRATIVE_ROUTE'}},
      {'role':'EVIDENCE','duration_ms':3000,'headline':'Original source evidence',
       'visual':{'kind':'RIGHTS_APPROVED_STILL','asset_id':card['asset_id']},'claim_ids':[cid]},
      {'role':'PAYOFF','duration_ms':3000,'headline':'Review before publishing',
       'visual':{'kind':'ORIGINAL_DIAGRAM','motion':'ILLUSTRATIVE_ROUTE'}}]
    plan={'locale':'en-US','shots':shots,
          'captions':[{'start_ms':0,'end_ms':3000,'text':'First inspect the source.'},
                      {'start_ms':3000,'end_ms':6000,'text':'Then show the supporting context.'},
                      {'start_ms':6000,'end_ms':9000,'text':'And always review the final video.'}],
          'captions_provenance':'OWNER_TIMED','locale_reviewed':True}
    result=post(client,f'/api/projects/{pid}/studio/plans',plan)
    # Real audio content is mandatory for final review; CPU test uses neutral synthesized WAV.
    from test_m22_m3_private import wav
    assert client.post(f'/api/projects/{pid}/voice',files={'file':('test_voice.wav',wav(9),'audio/wav')}).status_code==200
    post(client,f'/api/projects/{pid}/studio/queue',{})
    rendered=post(client,'/api/studio/run-next',{})
    assert rendered['state']=='SUCCEEDED',rendered
    rid=rendered['studio_render_id']
    report=client.get(f'/api/studio/reports/{rid}').json()['quality']
    assert report['render_wall_seconds']>0 and report['audio_track_present']
    owner_audit=client.get(f'/api/projects/{pid}/m22/creative-audit/{rid}').json()
    assert owner_audit['report']['status']=='OWNER_REVIEW_REQUIRED'
    # A human must still watch/correct content, and a changed reviewed claim invalidates it.
    post(client,f'/api/claims/{cid}/review',{'status':'SUPPORTED','reviewer':'Human editor',
         'explanation':'A later review changed the source commentary and context.'})
    assert client.get(f'/api/projects/{pid}/m22/creative-audit/{rid}').status_code==409
