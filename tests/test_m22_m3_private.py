"""M2.2 and M3 real CPU render and safety-gate regression tests."""
import io, os, json, math, struct, wave, shutil
import pytest
from fastapi.testclient import TestClient
from app import db
import app.main as main
from app.main import app
from app.creative_m22 import DIRECTOR_POLICIES, word_time_check, audit
from app import youtube_private

@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setenv('VIRALOS_DB',str(tmp_path/'viral.db'))
    monkeypatch.delenv('VIRALOS_ENABLE_PRIVATE_UPLOAD',raising=False)
    monkeypatch.setattr(main,'OUT',tmp_path/'output')
    with TestClient(app) as c:yield c

def post(c,route,data):
    r=c.post(route,json=data)
    assert r.status_code==200,(route,r.status_code,r.text)
    return r.json()

def wav(secs=1.5):
    b=io.BytesIO();rate=16000
    with wave.open(b,'wb') as f:
        f.setframerate(rate);f.setnchannels(1);f.setsampwidth(2)
        arr=[int(6000*math.sin(2*math.pi*220*i/rate)) for i in range(int(secs*rate))]
        f.writeframes(struct.pack('<'+'h'*len(arr),*arr))
    return b.getvalue()

def setup_draft(c):
    ch=post(c,'/api/channels',{'name':'M22 test NFL channel','sport_id':'nfl','locale':'en-US','market':'USA','timezone':'America/New_York'})
    pid=post(c,'/api/projects',{'channel_id':ch['channel_id'],'title':'Original defensive position study','original_angle':'Explain original defensive formations without borrowed broadcasts','format':'SHORT'})['project_id']
    script='This original field diagram shows two defensive positions. We compare how the positions change an illustrative play. This is not a recording of an actual match.'
    post(c,f'/api/projects/{pid}/script',{'text':script,'claim_links':[]})
    draft=post(c,f'/api/projects/{pid}/director/drafts',{'locale':'en-US'})
    for i,text in enumerate(draft['segments']):
        r=c.post(f"/api/projects/{pid}/director/drafts/{draft['draft_id']}/voice/{i}",files={'file':('voice.wav',wav(1.45),'audio/wav')})
        assert r.status_code==200,r.text
    plan=post(c,f"/api/projects/{pid}/director/drafts/{draft['draft_id']}/assemble",{})
    return ch['channel_id'],pid,plan['plan_id']

def make_render(c,pid):
    post(c,f'/api/projects/{pid}/studio/queue',{})
    r=post(c,'/api/studio/run-next',{})
    assert r['state']=='SUCCEEDED',r
    return r['studio_render_id']

def review_and_export(c,pid,rid):
    response=post(c,f'/api/projects/{pid}/m22/studio/renders/{rid}/review-final',{
        'reviewer':'Human Owner','watched_full_video':True,'original_or_rights_reviewed':True,
        'facts_sources_reviewed':True,'narration_and_captions_reviewed':True,
        'notes':'Reviewed original diagram, narrated script, source context, caption safety and media rights manually.'})
    return post(c,f"/api/projects/{pid}/m22/reviews/{response['review_id']}/export-final",{})

def test_schemas_policies_baseline(client):
    with db.read() as c:
        assert {x['version'] for x in db.many(c,'SELECT version FROM schema_migrations')}.issuperset({'007','008'})
    cap=client.get('/api/m3/private-upload/capabilities').json()
    assert not cap['private_upload_opt_in'] and not cap['public_upload']
    policies=client.get('/api/m22/creative-policies').json()
    assert len(DIRECTOR_POLICIES)==16 and len(policies['active_launch_adapters'])==2
    assert 'newsroom' in policies['profiles'] and 'sports.cricket' in policies['profiles']

def test_invalid_word_alignment_fail_closed():
    plan={'captions':[{'text':'One two','start_ms':0,'end_ms':1000},{'text':'Three four','start_ms':1000,'end_ms':2000}]}
    word_time_check(plan,[{'token':x,'start_ms':i*500,'end_ms':i*500+300} for i,x in enumerate(['One','two','Three','four'])])
    with pytest.raises(ValueError):word_time_check(plan,[{'token':'Made-up','start_ms':0,'end_ms':1000}])
    with pytest.raises(ValueError):word_time_check(plan,[{'token':x,'start_ms':i*500,'end_ms':i*500+600} for i,x in enumerate(['One','two','Three','four'])])

def test_owner_timed_word_vtt(client):
    ch,pid,plan_id=setup_draft(client)
    plan=client.get(f'/api/projects/{pid}/studio/plan').json()['plan']
    words=[]
    for cue in plan['captions']:
        seq=cue['text'].split();slot=max(1,(cue['end_ms']-cue['start_ms'])//len(seq))
        for j,word in enumerate(seq):
            start=cue['start_ms']+slot*j
            words.append({'token':word,'start_ms':start,'end_ms':min(cue['end_ms'],start+slot-1)})
    data={'words':words,'provenance':'OWNER_TIMED_REVIEWED','owner_checked_spelling':True}
    bad={**data,'owner_checked_spelling':False}
    assert client.post(f'/api/projects/{pid}/m22/plans/{plan_id}/words',json=bad).status_code==422
    result=post(client,f'/api/projects/{pid}/m22/plans/{plan_id}/words',data)
    assert result['automatic_forced_alignment'] is False
    vtt=client.get(f'/api/projects/{pid}/m22/plans/{plan_id}/words.vtt')
    assert vtt.status_code==200 and 'WEBVTT' in vtt.text
    assert client.post(f'/api/projects/{pid}/m22/plans/{plan_id}/words',json=data).status_code==409

def test_real_review_export_and_stale_protection(client):
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):pytest.skip('FFmpeg missing')
    ch,pid,plan_id=setup_draft(client)
    rid=make_render(client,pid)
    q=client.get(f'/api/projects/{pid}/m22/creative-audit/{rid}').json()
    assert q['report']['status']=='OWNER_REVIEW_REQUIRED'
    assert q['report']['automated_professional_score'] is None
    review_url=f'/api/projects/{pid}/m22/studio/renders/{rid}/review-final'
    payload={'reviewer':'Human Owner','watched_full_video':False,'original_or_rights_reviewed':True,
             'facts_sources_reviewed':True,'narration_and_captions_reviewed':True,
             'notes':'I looked at the narration and the original illustrative graphics.'}
    assert client.post(review_url,json=payload).status_code==409
    result=review_and_export(client,pid,rid)
    eid=result['export_id']
    assert result['status']=='OWNER_APPROVED_FINAL_EXPORT' and result['youtube_uploaded'] is False
    video=client.get(f'/api/m22/final-exports/{eid}/download')
    assert video.status_code==200 and len(video.content)>20000
    with db.read() as c:
        record=db.one(c,'SELECT * FROM m22_final_exports WHERE export_id=?',(eid,))
        report=json.loads(record['manifest_json'])
        assert report['render_profile']=='OWNER_REVIEWED_FINAL'
    assert client.post('/api/m3/private-upload/intents',json={
        'export_id':eid,'title':'Original defensive analysis','description':'A fully illustrative, original tactical explanation.',
        'tags':['NFL'],'altered_content':False,'made_for_kids':False,'owner_confirmed_metadata_rights':True}).status_code==409
    # Changing project facts invalidates even a previously approved final export.
    post(client,f'/api/projects/{pid}/script',{'text':'An updated script after review means all earlier approvals and exports must expire. This is another demonstration sentence.','claim_links':[]})
    assert client.get(f'/api/m22/final-exports/{eid}/download').status_code==409

def test_private_upload_flow_mock_auth_and_unknown_no_retry(client,monkeypatch):
    if not shutil.which('ffmpeg'):pytest.skip('FFmpeg missing')
    ch,pid,plan_id=setup_draft(client)
    rid=make_render(client,pid)
    eid=review_and_export(client,pid,rid)['export_id']
    with db.transaction() as c:
        c.execute('INSERT INTO m3_upload_accounts(local_channel_id,remote_channel_id,remote_title,verified_at,scopes_json) VALUES (?,?,?,?,?)',
                  (ch,'UC_FAKE_TEST_CHANNEL','Test channel',main.now(),main.j(youtube_private.SCOPES)))
    body={'export_id':eid,'title':'Original NFL study','description':'This is an owner-reviewed original illustration, not real game footage.',
          'tags':['analysis'],'altered_content':False,'made_for_kids':False,'owner_confirmed_metadata_rights':True}
    missing={**body,'owner_confirmed_metadata_rights':False}
    assert client.post('/api/m3/private-upload/intents',json=missing).status_code==409
    prepared=post(client,'/api/m3/private-upload/intents',body)
    assert prepared['privacy']=='private'
    iid=prepared['intent_id']
    assert client.post(f'/api/m3/private-upload/intents/{iid}/execute',json={'confirmation':'UPLOAD_PRIVATE_NOW'}).status_code==403
    monkeypatch.setenv('VIRALOS_ENABLE_PRIVATE_UPLOAD','1')
    monkeypatch.setattr(youtube_private,'upload_credentials',lambda cid:'fake-creds')
    monkeypatch.setattr(youtube_private,'verify_owned_channel',lambda creds,cid:{'id':cid})
    seen={}
    def mock_upload(credentials,path,metadata):
        seen['metadata']=metadata
        return {'id':'PRIVATE_TEST_ID','privacyStatus':'private'}
    monkeypatch.setattr(youtube_private,'upload_private_video',mock_upload)
    result=post(client,f'/api/m3/private-upload/intents/{iid}/execute',{'confirmation':'UPLOAD_PRIVATE_NOW'})
    assert result['state']=='UPLOADED_PRIVATE' and result['published_public'] is False
    assert seen['metadata']['title']==body['title']
    assert client.post(f'/api/m3/private-upload/intents/{iid}/execute',json={'confirmation':'UPLOAD_PRIVATE_NOW'}).status_code==409


def test_private_upload_remote_unknown_no_auto_retry(client,monkeypatch):
    if not shutil.which('ffmpeg'):pytest.skip('FFmpeg missing')
    ch,pid,_=setup_draft(client)
    eid=review_and_export(client,pid,make_render(client,pid))['export_id']
    with db.transaction() as c:
        c.execute('INSERT INTO m3_upload_accounts(local_channel_id,remote_channel_id,remote_title,verified_at,scopes_json) VALUES (?,?,?,?,?)',
                  (ch,'UC_TEST','Test',main.now(),main.j(youtube_private.SCOPES)))
    prepared=post(client,'/api/m3/private-upload/intents',{'export_id':eid,'title':'Mock private fail',
        'description':'This original diagram is an illustrative tutorial with no footage.', 'tags':[],
        'altered_content':False,'made_for_kids':False,'owner_confirmed_metadata_rights':True})
    monkeypatch.setenv('VIRALOS_ENABLE_PRIVATE_UPLOAD','1')
    monkeypatch.setattr(youtube_private,'upload_credentials',lambda cid:'creds')
    monkeypatch.setattr(youtube_private,'verify_owned_channel',lambda c,id:{'id':id})
    def fail(*args):raise OSError('network ambiguous')
    monkeypatch.setattr(youtube_private,'upload_private_video',fail)
    url=f"/api/m3/private-upload/intents/{prepared['intent_id']}/execute"
    assert client.post(url,json={'confirmation':'UPLOAD_PRIVATE_NOW'}).status_code==503
    assert client.get(f"/api/m3/private-upload/intents/{prepared['intent_id']}").json()['state']=='REMOTE_UNKNOWN'
    assert client.post(url,json={'confirmation':'UPLOAD_PRIVATE_NOW'}).status_code==409

def test_motion_route_is_real_cpu_animation():
    from PIL import Image, ImageChops
    from app.studio_render import animate_tactical_motion
    shot={'visual':{'kind':'ORIGINAL_DIAGRAM','motion':'ILLUSTRATIVE_ROUTE'},'duration_ms':4000}
    a=Image.new('RGBA',(540,960),(12,25,40,255));b=a.copy()
    animate_tactical_motion(a,shot,'nfl',0)
    animate_tactical_motion(b,shot,'nfl',3100)
    assert ImageChops.difference(a,b).getbbox() is not None
    static={'visual':{'kind':'ORIGINAL_DIAGRAM','motion':'STATIC'},'duration_ms':4000}
    c=Image.new('RGBA',(540,960),(12,25,40,255))
    animate_tactical_motion(c,static,'nfl',3000)
    assert ImageChops.difference(c,Image.new('RGBA',(540,960),(12,25,40,255))).getbbox() is None

def test_upload_restart_marks_in_flight_remote_unknown(tmp_path,monkeypatch):
    monkeypatch.setenv('VIRALOS_DB',str(tmp_path/'test.db'))
    monkeypatch.setattr(main,'OUT',tmp_path/'output')
    with TestClient(app) as c:
        ch,pid,_=setup_draft(c)
        if not shutil.which('ffmpeg'):pytest.skip('FFmpeg missing')
        eid=review_and_export(c,pid,make_render(c,pid))['export_id']
        with db.transaction() as con:
            con.execute('INSERT INTO m3_upload_accounts(local_channel_id,remote_channel_id,remote_title,verified_at,scopes_json) VALUES (?,?,?,?,?)',
                       (ch,'UC_FAKE','User channel',main.now(),main.j(youtube_private.SCOPES)))
        p=post(c,'/api/m3/private-upload/intents',{'export_id':eid,'title':'Owner final mock','description':'This is an owner-generated original illustration.',
                 'tags':[],'altered_content':False,'made_for_kids':False,'owner_confirmed_metadata_rights':True})
        iid=p['intent_id']
        with db.transaction() as con:
            con.execute("UPDATE m3_private_upload_intents SET state='IN_FLIGHT' WHERE intent_id=?",(iid,))
    with TestClient(app) as c:
        assert c.get(f'/api/m3/private-upload/intents/{iid}').json()['state']=='REMOTE_UNKNOWN'

def test_private_metadata_disclosure_changes_are_not_silent(client):
    if not shutil.which('ffmpeg'):pytest.skip('FFmpeg missing')
    ch,pid,_=setup_draft(client)
    eid=review_and_export(client,pid,make_render(client,pid))['export_id']
    with db.transaction() as con:
        con.execute('INSERT INTO m3_upload_accounts(local_channel_id,remote_channel_id,remote_title,verified_at,scopes_json) VALUES (?,?,?,?,?)',
                   (ch,'UC_FAKE','User channel',main.now(),main.j(youtube_private.SCOPES)))
    data={'export_id':eid,'title':'Original analysis example','description':'A unique educational illustration, no sports broadcast clips.',
          'tags':[],'altered_content':False,'made_for_kids':False,'owner_confirmed_metadata_rights':True}
    post(client,'/api/m3/private-upload/intents',data)
    assert client.post('/api/m3/private-upload/intents',json={**data,'altered_content':True}).status_code==409
