"""Actual CPU studio verification plus negative rights, timing and stale-job cases."""
import io, json, os, shutil, wave
from pathlib import Path
import pytest
from PIL import Image
from fastapi.testclient import TestClient
from app import db
from app.main import app
import app.main as main

@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setenv('VIRALOS_DB',str(tmp_path/'viralos.db'))
    monkeypatch.setattr(main,'OUT',tmp_path/'outputs')
    with TestClient(app) as c:yield c


def post(c,url,obj):
    r=c.post(url,json=obj);assert r.status_code==200,(r.status_code,r.text)
    return r.json()


def seed(c,locale='en-US',sport='nfl'):
    ch=post(c,'/api/channels',{'name':'M2 '+sport+' test','sport_id':sport,'locale':locale,'market':'USA' if sport=='nfl' else 'India','timezone':'America/New_York' if sport=='nfl' else 'Asia/Kolkata'})
    p=post(c,'/api/projects',{'channel_id':ch['channel_id'],'title':'Original game decisions explained',
          'original_angle':'Use original diagrams and no match footage to show tactical concepts','format':'SHORT'})
    post(c,f"/api/projects/{p['project_id']}/script",{'text':'This is an original manual tactical explanation with a hook and clear payoff. No verified real match facts are asserted.','claim_links':[]})
    return p['project_id']


def plan(locale='en-US'):
    return {'locale':locale,'locale_reviewed':False,'music_asset_id':None,
            'shots':[{'role':'HOOK','duration_ms':2000,'headline':'What changed the play?',
                      'visual':{'kind':'ORIGINAL_DIAGRAM'},'claim_ids':[],
                      'overlays':[{'text':'Observe the formation','start_ms':200,'end_ms':1550,'anchor':'CENTER','style':'CALLOUT'}]},
                     {'role':'PAYOFF','duration_ms':2000,'headline':'The answer is positioning',
                      'visual':{'kind':'ORIGINAL_DIAGRAM'},'claim_ids':[],
                      'overlays':[{'text':'An original diagram','start_ms':200,'end_ms':1750,'anchor':'CENTER','style':'STAT'}]}],
            'captions':[], 'captions_provenance':'NOT_PROVIDED'}


def wav(seconds=4):
    b=io.BytesIO()
    with wave.open(b,'wb') as f:
        f.setnchannels(1);f.setsampwidth(2);f.setframerate(16000)
        f.writeframes(b'\x00\x00'*int(16000*seconds))
    return b.getvalue()


def test_migration_and_capability_scope(client):
    with db.read() as c:
        assert {r['version'] for r in db.many(c,'SELECT version FROM schema_migrations')}=={'001','002','003','004','005','006','007','008','009','010','011','012'}
    cap=client.get('/api/studio/capabilities').json()
    assert cap['timed_overlays'] and cap['youtube_upload'] is False and cap['forced_alignment'] is False


def test_timing_and_locale_fail_closed(client):
    p=seed(client);bad=plan();bad['shots'][0]['overlays'][0]['end_ms']=2400
    assert client.post(f'/api/projects/{p}/studio/plans',json=bad).status_code==422
    bad=plan();bad['captions']=[{'text':'This is overlapping','start_ms':0,'end_ms':1500},
                                {'text':'Second overlapping caption','start_ms':1400,'end_ms':2500}];bad['captions_provenance']='OWNER_TIMED'
    assert client.post(f'/api/projects/{p}/studio/plans',json=bad).status_code==422
    bad=plan('hi-IN')
    assert client.post(f'/api/projects/{p}/studio/plans',json=bad).status_code==409
    good=plan('hi-IN');good['locale_reviewed']=True
    r=post(client,f'/api/projects/{p}/studio/plans',good)
    assert r['publish_ready'] is False


def test_unauthorized_image_and_cross_project_asset(client):
    p1=seed(client);p2=seed(client,locale='hi-IN',sport='cricket')
    im=Image.new('RGB',(100,120),(120,35,67));b=io.BytesIO();im.save(b,'PNG')
    args={'origin':'Owner drawing source','license_note':'I produced this original diagram','rights_attested':'true'}
    denied=client.post(f'/api/projects/{p1}/studio/assets/still',data={**args,'rights_attested':'false'},files={'file':('test.png',b.getvalue(),'image/png')})
    assert denied.status_code==422
    saved=client.post(f'/api/projects/{p1}/studio/assets/still',data=args,files={'file':('test.png',b.getvalue(),'image/png')})
    assert saved.status_code==200,saved.text
    aid=saved.json()['asset_id'];bad=plan('hi-IN');bad['shots'][0]['visual']={'kind':'RIGHTS_APPROVED_STILL','asset_id':aid}
    assert client.post(f'/api/projects/{p2}/studio/plans',json=bad).status_code==422
    denied_music=client.post(f'/api/projects/{p1}/studio/assets/music',data=args,files={'file':('track.wav',b'not wav','audio/wav')})
    assert denied_music.status_code==422


def test_cpu_timed_layers_wav_and_job_idempotency(client):
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):pytest.skip('FFmpeg missing')
    p=seed(client)
    r=client.post(f'/api/projects/{p}/voice',files={'file':('owner.wav',wav(),'audio/wav')})
    assert r.status_code==200
    body=plan();body['captions_provenance']='OWNER_TIMED'
    body['captions']=[{'start_ms':0,'end_ms':1900,'text':'The field positions matter'},
                      {'start_ms':2100,'end_ms':3900,'text':'The explanation is visible'}]
    first=post(client,f'/api/projects/{p}/studio/plans',body)
    duplicate=post(client,f'/api/projects/{p}/studio/plans',body)
    assert duplicate['already_exists'] and duplicate['plan_id']==first['plan_id']
    a=post(client,f'/api/projects/{p}/studio/queue',{})
    b=post(client,f'/api/projects/{p}/studio/queue',{})
    assert a['job_id']==b['job_id'] and b['already_exists']
    done=client.post('/api/studio/run-next').json()
    assert done['state']=='SUCCEEDED',done
    assert done['publish_ready'] is False
    report=client.get(done['report_url']).json()
    assert report['quality']['caption_alignment']=='OWNER_TIMED_NOT_MEASURED'
    assert report['quality']['audio_track_present'] and not report['quality']['publish_ready']
    result=client.get(done['preview_url'])
    assert result.status_code==200 and len(result.content)>5000
    assert client.post('/api/studio/run-next').json()['state']=='EMPTY'


def test_stale_studio_job_after_voice_revision(client):
    p=seed(client)
    post(client,f'/api/projects/{p}/studio/plans',plan())
    post(client,f'/api/projects/{p}/studio/queue',{})
    resp=client.post(f'/api/projects/{p}/voice',files={'file':('voice.wav',wav(),'audio/wav')})
    assert resp.status_code==200
    done=client.post('/api/studio/run-next').json()
    assert done['state']=='FAILED' and 'changed' in done['error']


def test_mismatched_narration_duration_blocks_render(client):
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):pytest.skip('FFmpeg missing')
    p=seed(client)
    assert client.post(f'/api/projects/{p}/voice',files={'file':('voice.wav',wav(1),'audio/wav')}).status_code==200
    post(client,f'/api/projects/{p}/studio/plans',plan())
    post(client,f'/api/projects/{p}/studio/queue',{})
    done=client.post('/api/studio/run-next').json()
    assert done['state']=='FAILED' and 'must match timeline' in done['error']

def test_approved_still_picture_in_picture_and_music_mix(client):
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):pytest.skip('FFmpeg missing')
    p=seed(client)
    art=Image.new('RGB',(480,300),(20,105,92));buf=io.BytesIO();art.save(buf,'PNG')
    meta={'origin':'Self-created illustration','license_note':'Original image drawn and owned locally','rights_attested':'true'}
    still=client.post(f'/api/projects/{p}/studio/assets/still',data=meta,files={'file':('original.png',buf.getvalue(),'image/png')})
    assert still.status_code==200,still.text
    sid=still.json()['asset_id']
    music=client.post(f'/api/projects/{p}/studio/assets/music',data=meta,files={'file':('original.wav',wav(2),'audio/wav')})
    assert music.status_code==200,music.text
    mid=music.json()['asset_id']
    assert client.post(f'/api/projects/{p}/voice',files={'file':('voice.wav',wav(),'audio/wav')}).status_code==200
    body=plan()
    body['shots'][0]['overlays'].append({'text':'Owner approved still','style':'IMAGE_INSERT','image_asset_id':sid,
                                        'anchor':'LOWER_THIRD','start_ms':400,'end_ms':1700})
    body['music_asset_id']=mid
    post(client,f'/api/projects/{p}/studio/plans',body)
    post(client,f'/api/projects/{p}/studio/queue',{})
    result=client.post('/api/studio/run-next').json()
    assert result['state']=='SUCCEEDED',result
    qc=client.get(result['report_url']).json()
    assert qc['quality']['audio_track_present'] and qc['quality']['voice_present']
    assert mid in qc['manifest']['asset_sha256'] and sid in qc['manifest']['asset_sha256']
    assert 'may be silent' in ' '.join(qc['quality']['warnings'])


def test_identical_plan_after_script_revision_is_new_plan(client):
    p=seed(client)
    orig=post(client,f'/api/projects/{p}/studio/plans',plan())
    post(client,f'/api/projects/{p}/script',{'text':'A second original explanatory script with new version and evidence review requirement.','claim_links':[]})
    newer=post(client,f'/api/projects/{p}/studio/plans',plan())
    assert newer['plan_id']!=orig['plan_id'] and newer['already_exists'] is False
    assert post(client,f'/api/projects/{p}/studio/plans',plan())['already_exists'] is True


def test_same_anchor_overlay_overlap_rejected(client):
    p=seed(client)
    bad=plan();bad['shots'][0]['overlays'].append({'text':'Colliding label','start_ms':400,'end_ms':1400,'anchor':'CENTER','style':'LABEL'})
    r=client.post(f'/api/projects/{p}/studio/plans',json=bad)
    assert r.status_code==422

def test_interrupted_local_studio_job_marked_failed_on_restart(client):
    p=seed(client)
    post(client,f'/api/projects/{p}/studio/plans',plan())
    job=post(client,f'/api/projects/{p}/studio/queue',{})
    with db.transaction() as c:
        c.execute("UPDATE jobs SET state='RUNNING' WHERE job_id=?",(job['job_id'],))
    # Run the actual lifespan startup as a new process would, against same DB.
    from app.main import lifespan,app as actual_app
    import asyncio
    async def run():
        async with lifespan(actual_app):
            with db.read() as c:
                x=db.one(c,'SELECT state,error_code FROM jobs WHERE job_id=?',(job['job_id'],))
                assert x['state']=='FAILED' and x['error_code']=='INTERRUPTED_ON_STARTUP'
    asyncio.run(run())
    assert client.post(f"/api/jobs/{job['job_id']}/retry").status_code==200
