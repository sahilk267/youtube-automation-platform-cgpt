"""M2.4/M3.2 release tests. Real provider models and Google accounts NOT available;
all remote/mock tests are clearly isolated from real FFmpeg CPU rendering tests.
"""
import json, shutil
import pytest
from fastapi.testclient import TestClient
from app import db, alignment_m24, multilingual_m24, acceptance_m32, youtube_private
from app.main import app
import app.main as main
from test_m22_m3_private import wav, setup_draft,make_render,review_and_export,post

@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setenv('VIRALOS_DB',str(tmp_path/'viral.db'))
    monkeypatch.setattr(main,'OUT',tmp_path/'output')
    for name in ['VIRALOS_ENABLE_M32_REMOTE_READ','VIRALOS_PIPER_EXE','VIRALOS_PIPER_MODEL',
                 'VIRALOS_PIPER_LOCALE','VIRALOS_WHISPERX_ALIGN_MODEL_DIR','VIRALOS_OFFLINE_FORCED_ALIGN_OPT_IN',
                 'VIRALOS_WHISPERX_MODEL_RIGHTS_OK']:
        monkeypatch.delenv(name,raising=False)
    with TestClient(app) as c:yield c


def setup_variant(c,language='hi-IN'):
    channel=post(c,'/api/channels',{'name':'Independent multi-locale cricket','sport_id':'cricket','locale':'en-US',
                'market':'International','timezone':'Asia/Kolkata'})['channel_id']
    pid=post(c,'/api/projects',{'channel_id':channel,'title':'Cricket positioning with original diagrams',
            'original_angle':'Illustrative, original and educational field positions only',
            'format':'SHORT'})['project_id']
    script='This original cricket diagram compares positions at the crease. It presents a hypothetical teaching example and not actual match footage.'
    post(c,f'/api/projects/{pid}/script',{'text':script,'claim_links':[]})
    if language=='hi-IN':
        reviewed='यह चित्र क्रिकेट की दो फील्ड स्थितियों की तुलना करता है। यह केवल एक काल्पनिक शैक्षिक उदाहरण है, वास्तविक मैच की फुटेज नहीं।'
    else:reviewed=script
    variant=post(c,f'/api/projects/{pid}/m24/variants',{
        'locale':language,'reviewed_script':reviewed,'reviewer':'Owner linguistic reviewer',
        'regional_notes':'Reviewed regional terms, numeric facts, pronunciation and intended cultural context.',
        'words_names_numbers_and_meaning_reviewed':True,'on_screen_language_reviewed':True})
    return channel,pid,variant['variant_id']


def test_additive_migrations_and_strict_capabilities(client):
    with db.read() as c:
        versions={x['version'] for x in db.many(c,'SELECT version FROM schema_migrations')}
    assert versions.issuperset({'011','012'})
    cap=client.get('/api/m24/capabilities').json()
    assert cap['translation']=='OWNER_SUPPLIED_AND_REVIEWED_ONLY'
    assert cap['piper_opt_in_local_model'] is False
    assert cap['optional_ctc_forced_aligner']['model_downloads_allowed'] is False
    assert not cap['licensed_piper_voice_quality_live_tested']
    assert not cap['owner_upload_automatically_enabled']
    assert not client.get('/api/m32/capabilities').json()['remote_read_only_preflight_opt_in']


def test_localization_requires_human_review(client):
    channel,pid,vid=setup_variant(client)
    text='यह एक स्थानीय खेल विवरण है और केवल शैक्षिक उदाहरण दिखाता है। दूसरे वाक्य में एक और शैक्षिक विवरण दिया गया है।'
    bad={'locale':'en-US','reviewed_script':text,'reviewer':'Responsible reviewer',
         'regional_notes':'Reviewed the local content for accuracy and cultural language choices.',
         'words_names_numbers_and_meaning_reviewed':False,'on_screen_language_reviewed':True}
    assert client.post(f'/api/projects/{pid}/m24/variants',json=bad).status_code==409
    assert client.post(f'/api/projects/{pid}/m24/variants',json={**bad,'words_names_numbers_and_meaning_reviewed':True}).status_code==200
    assert client.post(f'/api/projects/{pid}/m24/variants',json={**bad,'words_names_numbers_and_meaning_reviewed':True,'reviewed_script':text+' नया'}).status_code==409
    v=client.get(f'/api/projects/{pid}/m24/variants/{vid}').json()
    assert v['locale']=='hi-IN' and len(v['segments'])>=2


def test_glossary_is_reviewed_and_only_affects_tts_input(client):
    _,pid,vid=setup_variant(client,language='en-US')
    url=f'/api/projects/{pid}/m24/variants/{vid}/pronunciation'
    invalid={'written':'cricket','speak_as':'crick-it','reviewer':'Studio operator',
             'reviewer_checked_identity_and_meaning':False}
    assert client.post(url,json=invalid).status_code==409
    assert client.post(url,json={**invalid,'reviewer_checked_identity_and_meaning':True,'written':'absent'}).status_code==422
    item=post(client,url,{**invalid,'reviewer_checked_identity_and_meaning':True})
    assert item['caption_text_changed'] is False
    actual=multilingual_m24.locale_substitutions('Cricket is great cricket analysis',[
        {'written':'cricket','speak_as':'crick-it'}])
    assert actual=='crick-it is great crick-it analysis'


def test_audio_missing_and_cross_project_rejected(client):
    _,pid,vid=setup_variant(client)
    assert client.post(f'/api/projects/{pid}/m24/variants/{vid}/render').status_code==409
    _,other,_=setup_variant(client,language='en-US')
    assert client.get(f'/api/projects/{other}/m24/variants/{vid}').status_code==404
    assert client.post(f'/api/projects/{other}/m24/variants/{vid}/voice/0',files={'file':('a.wav',wav(),'audio/wav')}).status_code==404


def test_invalid_or_wrong_voice_asset_rejected(client):
    _,pid,vid=setup_variant(client)
    url=f'/api/projects/{pid}/m24/variants/{vid}/voice/0'
    assert client.post(url,files={'file':('bad.wav',b'not-a-wav','audio/wav')}).status_code==422
    good=client.post(url,files={'file':('okay.wav',wav(),'audio/wav')})
    assert good.status_code==200 and good.json()['duration_ms']>1200
    with db.read() as c:rec=db.one(c,'SELECT file_relpath FROM m24_voices WHERE variant_id=? AND segment_index=0',(vid,))
    path=main.OUT/rec['file_relpath'];path.write_bytes(path.read_bytes()+b'CHANGED')
    assert client.post(f'/api/projects/{pid}/m24/variants/{vid}/render').status_code==409


def test_offline_model_requires_owner_install(client,monkeypatch):
    _,pid,vid=setup_variant(client)
    assert client.post(f'/api/projects/{pid}/m24/variants/{vid}/synthesize-piper',json={
        'owner_approved_model_license':True,'owner_approved_pronunciation':True}).status_code==409
    assert not alignment_m24.config()['model_installed']
    assert client.post(f'/api/projects/{pid}/m24/plans/not-real/forced-proposal').status_code in (404,409)


def test_actual_local_hindi_cpu_render_and_srt(client):
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):pytest.skip('FFmpeg absent')
    _,pid,vid=setup_variant(client)
    detail=client.get(f'/api/projects/{pid}/m24/variants/{vid}').json()
    for seg in detail['segments']:
        r=client.post(f'/api/projects/{pid}/m24/variants/{vid}/voice/{seg["index"]}',
                      files={'file':('owner.wav',wav(1.65),'audio/wav')})
        assert r.status_code==200,r.text
    output=post(client,f'/api/projects/{pid}/m24/variants/{vid}/render',{})
    assert output['technical_qc']=='TECHNICAL_QC_PASSED_HUMAN_REVIEW_REQUIRED'
    assert not output['publishing_eligible']
    video=client.get(output['preview_url'])
    assert video.status_code==200 and len(video.content)>30000
    srt=client.get(output['captions_url'])
    assert srt.status_code==200 and 'क्रिकेट' in srt.text
    qc=client.get(f'/api/projects/{pid}/m24/previews/{output["preview_id"]}/qc').json()
    assert qc['source_script_hash'] and qc['quality']['audio_track_present']
    with db.read() as c:
        rec=db.one(c,'SELECT plan_json FROM m24_previews WHERE preview_id=?',(output['preview_id'],))
        plan=json.loads(rec['plan_json'])
        assert any('मूल' in x['text'] for sh in plan['shots'] for x in sh['overlays'])
    assert client.post(f'/api/projects/{pid}/m24/variants/{vid}/render').status_code==409
    assert client.post(f'/api/projects/{pid}/m24/variants/{vid}/voice/0',files={'file':('ok.wav',wav(),'audio/wav')}).status_code==409


def test_script_revision_invalidates_localized_variant(client):
    _,pid,vid=setup_variant(client)
    post(client,f'/api/projects/{pid}/script',{'text':'This revised document changes the source and should invalidate every previously created locale variant.','claim_links':[]})
    assert client.get(f'/api/projects/{pid}/m24/variants/{vid}').status_code==409


def _approved_export(client):
    ch,pid,plan_id=setup_draft(client)
    rid=make_render(client,pid)
    e=review_and_export(client,pid,rid)
    return ch,pid,e['export_id']


def test_acceptance_preflight_blocks_unconnected_upload_channel(client):
    ch,pid,eid=_approved_export(client)
    body={'export_id':eid,'owner_confirmed_local_video_and_rights':True,
          'owner_confirmed_target_channel':True}
    answer=post(client,'/api/m32/acceptance/preflight',body)
    assert answer['status']=='BLOCKED'
    assert 'UPLOAD_OAUTH_CHANNEL_NOT_CONNECTED' in answer['blockers']
    assert not answer['live_private_upload_executed_by_preflight']
    assert not answer['remote_access_performed']
    assert client.post('/api/m32/acceptance/preflight',json={**body,'perform_remote_read_only_check':True}).status_code==409
    assert client.post('/api/m32/acceptance/preflight',json={**body,'perform_remote_read_only_check':True,'owner_consented_network_access':True}).status_code==403
    with db.transaction() as c:
        c.execute('INSERT INTO m3_upload_accounts(local_channel_id,remote_channel_id,remote_title,verified_at,scopes_json) VALUES (?,?,?,?,?)',
                  (ch,'UC_OWNER_TEST','Simulated Account',main.now(),main.j(youtube_private.SCOPES)))
    ok=post(client,'/api/m32/acceptance/preflight',body)
    assert ok['status']=='LOCAL_READY' and ok['remote_channel_id']=='UC_OWNER_TEST'
    hist=client.get(f'/api/m32/acceptance/exports/{eid}').json()
    assert len(hist['checks'])==2
    assert all('refresh_token' not in json.dumps(x) for x in hist['checks'])


def test_preflight_mismatch_remote_and_read_only_mock(client,monkeypatch):
    ch,pid,eid=_approved_export(client)
    with db.transaction() as c:
        c.execute('INSERT INTO m3_upload_accounts(local_channel_id,remote_channel_id,remote_title,verified_at,scopes_json) VALUES (?,?,?,?,?)',
                  (ch,'UC_OWNER','Own',main.now(),main.j(youtube_private.SCOPES)))
        c.execute('INSERT INTO m3_youtube_accounts(local_channel_id,remote_channel_id,remote_title,connected_at,verification,oauth_scope_text) VALUES (?,?,?,?,?,?)',
                  (ch,'UC_DIFFERENT','Other',main.now(),'OAUTH_CHANNELS_MINE','[]'))
    b={'export_id':eid,'owner_confirmed_local_video_and_rights':True,'owner_confirmed_target_channel':True}
    result=post(client,'/api/m32/acceptance/preflight',b)
    assert 'ANALYTICS_ACCOUNT_MISMATCH' in result['blockers']
    monkeypatch.setenv('VIRALOS_ENABLE_M32_REMOTE_READ','1')
    assert client.post('/api/m32/acceptance/preflight',json={**b,'owner_consented_network_access':True,'perform_remote_read_only_check':True}).status_code==409
    with db.transaction() as c:c.execute('DELETE FROM m3_youtube_accounts WHERE local_channel_id=?',(ch,))
    monkeypatch.setattr(youtube_private,'upload_credentials',lambda _ch:'MOCK_ONLY_NO_NETWORK')
    monkeypatch.setattr(acceptance_m32,'inspect_remote',lambda cred,cid,vid=None:{'verified_channel_id':cid,'remote_video_verified':False,'remote_video_privacy':None})
    online=post(client,'/api/m32/acceptance/preflight',{**b,'owner_consented_network_access':True,'perform_remote_read_only_check':True})
    assert online['status']=='REMOTE_CHANNEL_VERIFIED' and online['remote_access_performed']
    assert not online['remote_upload_verified'] and not online['live_private_upload_executed_by_preflight']


def test_real_ctc_adapter_disabled_without_local_model(client):
    assert alignment_m24.config()['model_downloads_allowed'] is False
    with pytest.raises(RuntimeError):alignment_m24.align_transcript('fake.wav',{'locale':'hi-IN','captions':[]})


def test_remote_readback_refuses_nonprivate_or_foreign(client,monkeypatch):
    from app import analytics_m31
    monkeypatch.setattr(youtube_private,'verify_owned_channel',lambda creds,cid:{'id':cid})
    monkeypatch.setattr(analytics_m31,'fetch_remote_video',lambda creds,vid:[{
        'id':vid,'snippet':{'channelId':'UC_OTHER'},'status':{'privacyStatus':'private'}}])
    with pytest.raises(RuntimeError):acceptance_m32.inspect_remote('mock','UC_OWNER','abc')
    monkeypatch.setattr(analytics_m31,'fetch_remote_video',lambda creds,vid:[{
        'id':vid,'snippet':{'channelId':'UC_OWNER'},'status':{'privacyStatus':'public'}}])
    with pytest.raises(RuntimeError):acceptance_m32.inspect_remote('mock','UC_OWNER','abc')

def test_local_ctc_forced_proposal_review_gate_mock(client,monkeypatch):
    """Mock ONLY verifies integration/approval; it is NOT a live WhisperX model test."""
    ch,pid,plan_id=setup_draft(client)
    plan=client.get(f'/api/projects/{pid}/studio/plan').json()['plan']
    words=[]
    for cue in plan['captions']:
        tokens=cue['text'].split()
        interval=(cue['end_ms']-cue['start_ms'])//len(tokens)
        for i,token in enumerate(tokens):
            start=cue['start_ms']+i*interval
            words.append({'token':token,'start_ms':start,'end_ms':min(cue['end_ms'],start+interval-2)})
    monkeypatch.setattr(alignment_m24,'align_transcript',lambda audio,script:words)
    out=post(client,f'/api/projects/{pid}/m24/plans/{plan_id}/forced-proposal',{})
    assert out['alignment_method']=='LOCAL_CTC_FORCED_TRANSCRIPT_CONSTRAINED'
    assert out['transcript_matches_and_timing_valid'] and not out['accepted_as_final']
    assert client.post(f'/api/projects/{pid}/m23/alignment-drafts/{out["draft_id"]}/approve',json={
        'owner_checked_audio_and_words':False,'words':words}).status_code==409
    approved=post(client,f'/api/projects/{pid}/m23/alignment-drafts/{out["draft_id"]}/approve',{
        'owner_checked_audio_and_words':True,'words':words})
    assert approved['provenance']=='LOCAL_CTC_FORCED_OWNER_REVIEWED'
    assert client.get(f'/api/projects/{pid}/m22/plans/{plan_id}/words.vtt').status_code==200


def test_voice_quality_clipping_is_blocked(client):
    from app.voice_quality_m24 import inspect_pcm16_mono
    import wave,struct
    _,pid,vid=setup_variant(client)
    with db.read() as c: v=db.one(c,'SELECT * FROM m24_variants WHERE variant_id=?',(vid,))
    artifact=main.OUT/'clipped.wav';artifact.parent.mkdir(parents=True,exist_ok=True)
    with wave.open(str(artifact),'wb') as f:
        f.setnchannels(1);f.setsampwidth(2);f.setframerate(16000)
        f.writeframes(struct.pack('<'+'h'*32000,*([32767]*32000)))
    report=inspect_pcm16_mono(artifact)
    assert 'EXCESSIVE_WAVEFORM_CLIPPING' in report['blockers']
    assert report['professional_naturalness_measured'] is False
