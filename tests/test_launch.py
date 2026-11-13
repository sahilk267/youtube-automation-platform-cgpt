import io, os, shutil, sqlite3, wave
from pathlib import Path
from fastapi.testclient import TestClient
import pytest
from app.main import app
from app import db
import app.main as main

@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setenv('VIRALOS_DB',str(tmp_path/'viralos.db'))
    monkeypatch.setattr(main,'OUT',tmp_path/'outputs')
    with TestClient(app) as c:yield c

def post(c,url,body):
    res=c.post(url,json=body)
    assert res.status_code==200,(url,res.text)
    return res.json()

def seed(c,sport='cricket',locale='hi-IN'):
    ch=post(c,'/api/channels',{'name':'Cricket Test' if sport=='cricket' else 'NFL Test','sport_id':sport,'locale':locale,'market':'India' if sport=='cricket' else 'USA','timezone':'Asia/Kolkata' if sport=='cricket' else 'America/New_York'})
    project=post(c,'/api/projects',{'channel_id':ch['channel_id'],'title':'Original data-backed explanation',
          'original_angle':'Demonstrate original educational sport analysis without using broadcast footage', 'format':'SHORT'})
    return project['project_id']

def source(c,p,url='https://example.org/illustrative-report'):
    return post(c,f'/api/projects/{p}/sources',{'url':url,'publisher':'Example Source',
      'excerpt':'Only synthetic test-fixture text. This is not a factual sports report or real evidence.'})

def test_spec_migration_and_status(client):
    h=client.get('/health').json()
    assert h['schema_tables']>=61 and h['publishing_enabled'] is False
    with db.connect() as con:
        versions={x[0] for x in con.execute('SELECT version FROM schema_migrations')}
        assert versions=={'001','002','003','004','005','006','007','008','009','010','011','012'}
    db.initialize()  # idempotent
    assert client.get('/api/capabilities').json()['gpu']['enabled'] is False
    assert client.get('/').status_code==200
    assert 'ViralOS' in client.get('/').text

def test_manual_source_and_fact_review_boundaries(client):
    p=seed(client)
    assert client.post(f'/api/projects/{p}/sources',json={'url':'file:///private/file','publisher':'local','excerpt':'Only test content, cannot fetch filesystem contents.'}).status_code==422
    sv=source(client,p)['source_version_id']
    cl=post(client,f'/api/projects/{p}/claims',{'proposition':'Synthetic claim for testing source provenance','source_version_id':sv,'relation':'REFUTES','locator':'paragraph 1'})
    report=client.get(f'/api/projects/{p}').json()
    assert cl['claim_id'] in report['report']['unsupported_claims']
    assert client.post(f"/api/claims/{cl['claim_id']}/review",json={'status':'SUPPORTED','reviewer':'Owner','explanation':'I manually reviewed this claim and found issues.'}).status_code==409
    review=post(client,f"/api/claims/{cl['claim_id']}/review",{'status':'REFUTED','reviewer':'Owner','explanation':'Reviewed source; cannot support this claim.'})
    assert review['review_type']=='HUMAN_ATTESTATION_ONLY'
    with db.connect() as con:
        v=con.execute('SELECT access_status,metadata_json FROM source_versions').fetchone()
        assert v[0]=='METADATA_ONLY' and 'NOT_AUTOMATED' in v[1]

def test_versioned_script_and_explicit_claim_link(client):
    p=seed(client);sv=source(client,p)['source_version_id']
    cl=post(client,f'/api/projects/{p}/claims',{'proposition':'Synthetic claim for script link only', 'source_version_id':sv,'locator':'paragraph 1'})
    text='The synthetic claim for testing is presented here, but not independently verified. This is an original script.'
    bad=client.post(f'/api/projects/{p}/script',json={'text':text,'claim_links':[{'claim_id':cl['claim_id'],'exact_quote':'never appears in the text'}]})
    assert bad.status_code==422
    good=post(client,f'/api/projects/{p}/script',{'text':text,'claim_links':[{'claim_id':cl['claim_id'],'exact_quote':'synthetic claim for testing'}]})
    assert good['links']==1
    post(client,f'/api/projects/{p}/scenes',{'text':'Original analytical title slide','duration_seconds':1,'claim_ids':[cl['claim_id']]})
    new=post(client,f'/api/projects/{p}/script',{'text':'A revised original script changes the previous storyboard and requires new video scenes.', 'claim_links':[]})
    project=client.get(f'/api/projects/{p}').json()
    assert new['revision']==2 and project['scenes']==[]
    assert cl['claim_id'] in project['report']['claims_missing_script_links']

def test_cpu_preview_with_idempotency_and_unverified_status(client):
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
        pytest.skip('FFmpeg not available in test environment')
    p=seed(client)
    assert client.post(f'/api/projects/{p}/queue-preview').status_code==404
    post(client,f'/api/projects/{p}/script',{'text':'Original text explainer, two scenes, deliberately without external source claims for technical preview.','claim_links':[]})
    post(client,f'/api/projects/{p}/scenes',{'text':'First original explanation in cricket context','duration_seconds':1,'claim_ids':[]})
    post(client,f'/api/projects/{p}/scenes',{'text':'Second original diagram description and takeaways','duration_seconds':1,'claim_ids':[]})
    a=post(client,f'/api/projects/{p}/queue-preview',{})
    b=post(client,f'/api/projects/{p}/queue-preview',{})
    assert a['job_id']==b['job_id'] and b['already_exists']
    done=client.post('/api/jobs/run-next').json()
    assert done['state']=='SUCCEEDED',done
    assert done['publish_ready'] is False and done['has_voice'] is False
    video=client.get(done['preview_url'])
    assert video.status_code==200 and len(video.content)>3000
    out=client.get(f'/api/projects/{p}').json()
    assert out['report']['publish_ready'] is False
    assert out['renders'][0]['status']=='TECHNICAL_PREVIEW'
    assert client.post('/api/jobs/run-next').json()['state']=='EMPTY'

def test_owner_wav_import_is_not_voice_verification(client):
    p=seed(client,sport='nfl',locale='en-US')
    buff=io.BytesIO()
    with wave.open(buff,'wb') as w:
        w.setframerate(16000);w.setnchannels(1);w.setsampwidth(2)
        w.writeframes(b'\x00\x00'*16000)
    resp=client.post(f'/api/projects/{p}/voice',files={'file':('owner.wav',buff.getvalue(),'audio/wav')})
    assert resp.status_code==200 and resp.json()['speech_alignment']=='NOT_MEASURED'
    assert client.get(f'/api/projects/{p}').json()['report']['has_narration'] is True
    assert client.post(f'/api/projects/{p}/voice',files={'file':('bad.wav',b'not a wave','audio/wav')}).status_code==422

def test_no_upload_endpoints(client):
    assert client.post('/api/youtube/upload',json={'id':'test'}).status_code==403
    assert client.get('/api/editions').json()['ultimate_enabled'] is False

def test_same_topic_multiple_projects_do_not_mix_claims(client):
    ch=post(client,'/api/channels',{'name':'Cricket Project Test','sport_id':'cricket','locale':'hi-IN','market':'India','timezone':'Asia/Kolkata'})
    body={'channel_id':ch['channel_id'],'title':'A repeatable cricket question','original_angle':'A separate original angle with a different research file','format':'SHORT'}
    p1=post(client,'/api/projects',body)['project_id']
    assert client.post('/api/projects',json=body).status_code==409
    p2=post(client,'/api/projects',{**body,'original_angle':'A second independent editorial angle and different research file'})['project_id']
    sv=source(client,p1)['source_version_id']
    cl=post(client,f'/api/projects/{p1}/claims',{'proposition':'This statement belongs to the first project only','source_version_id':sv,'locator':'test passage'})
    assert len(client.get(f'/api/projects/{p1}').json()['claims'])==1
    assert client.get(f'/api/projects/{p2}').json()['claims']==[]
    assert client.get(f'/api/projects/{p1}').json()['plan']['research_plan_id']!=client.get(f'/api/projects/{p2}').json()['plan']['research_plan_id']

def test_original_cricket_and_nfl_diagrams_are_distinct(tmp_path):
    from app.renderer import image_for_scene
    from PIL import Image
    a=tmp_path/'c.png';b=tmp_path/'n.png'
    image_for_scene('Original sport analysis',0,2,a,360,640,'cricket',True)
    image_for_scene('Original sport analysis',0,2,b,360,640,'nfl',True)
    assert a.read_bytes()!=b.read_bytes()
    assert Image.open(a).size==(360,640)

def test_stale_job_input_fails_closed_and_retry_is_explicit(client):
    p=seed(client)
    post(client,f'/api/projects/{p}/script',{'text':'An original educational presentation, written only to verify job hash invalidation.','claim_links':[]})
    post(client,f'/api/projects/{p}/scenes',{'text':'A scene before new voice was added','duration_seconds':1,'claim_ids':[]})
    queued=post(client,f'/api/projects/{p}/queue-preview',{})
    buff=io.BytesIO()
    with wave.open(buff,'wb') as w:
        w.setframerate(16000);w.setnchannels(1);w.setsampwidth(2)
        w.writeframes(b'\x00\x00'*16000)
    assert client.post(f'/api/projects/{p}/voice',files={'file':('added-after-queue.wav',buff.getvalue(),'audio/wav')}).status_code==200
    failed=client.post('/api/jobs/run-next').json()
    assert failed['state']=='FAILED' and 'input changed' in failed['error']
    requeued=post(client,f"/api/jobs/{queued['job_id']}/retry",{})
    assert requeued['state']=='QUEUED'
    assert client.post(f"/api/jobs/{queued['job_id']}/retry").status_code==409
    assert client.get(f'/api/projects/{p}').json()['renders']==[]

def test_cross_project_claim_link_is_blocked(client):
    p1=seed(client)
    p2=seed(client,sport='nfl',locale='en-US')
    sv=source(client,p1)['source_version_id']
    claim=post(client,f'/api/projects/{p1}/claims',{'proposition':'A claim that belongs only to the first research plan','source_version_id':sv,'locator':'section A'})
    result=client.post(f'/api/projects/{p2}/script',json={
        'text':'Another unique manual script for another domain. Citation cannot be borrowed without context.',
        'claim_links':[{'claim_id':claim['claim_id'],'exact_quote':'Another unique manual script'}]})
    assert result.status_code==404
    assert client.get(f'/api/projects/{p2}').json()['script'] is None
