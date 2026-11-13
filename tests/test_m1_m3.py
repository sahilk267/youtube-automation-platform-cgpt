"""Executable regression tests. None use real external APIs or imply monetization approval."""
import io, json, shutil, wave, zipfile
from datetime import date
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app import db
import app.main as main

@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setenv('VIRALOS_DB',str(tmp_path/'test.db'))
    monkeypatch.setattr(main,'OUT',tmp_path/'outputs')
    with TestClient(app) as c:yield c

def post(c,url,data):
    r=c.post(url,json=data)
    assert r.status_code==200,(url,r.status_code,r.text)
    return r.json()

def project(c,name='Cricket'):
    ch=post(c,'/api/channels',{'name':name,'sport_id':'cricket','locale':'hi-IN','market':'India','timezone':'Asia/Kolkata'})
    p=post(c,'/api/projects',{'channel_id':ch['channel_id'],'title':'Original Test Video '+name,
          'original_angle':'Using original diagrams to demonstrate match tactics in a clear and verifiable way',
          'format':'SHORT'})
    return ch['channel_id'],p['project_id']

def source(c,p):
    return post(c,f'/api/projects/{p}/sources',{'url':'https://example.org/match-report','publisher':'Example',
        'excerpt':'This illustrative test text does not represent any real cricket match.'})['source_version_id']

def seed_renderable(c,p):
    post(c,f'/api/projects/{p}/script',{'text':'What happened here? We show the original field illustration, explain a strategic option, and finish with a takeaway.','claim_links':[]})
    post(c,f'/api/projects/{p}/scenes',{'text':'How the field setup changes','duration_seconds':1.5,'claim_ids':[]})
    post(c,f'/api/projects/{p}/scenes',{'text':'Here is the visual takeaway','duration_seconds':1.5,'claim_ids':[]})

def test_rss_owner_supplied_and_no_external_claims(client):
    ch,p=project(client)
    xml='''<?xml version="1.0"?><rss version="2.0"><channel><title>A feed</title>
    <item><title>Report A</title><link>https://example.com/a</link><pubDate>Wed, 12 Nov 2026 00:00:00 GMT</pubDate></item>
    <item><title>Report A duplicate</title><link>https://example.com/a</link></item>
    <item><title>Internal File</title><link>file:///etc/passwd</link></item>
    </channel></rss>'''
    r=post(client,f'/api/projects/{p}/rss-import',{'feed_url':'https://example.com/rss','title':'Manual RSS test','xml_text':xml})
    assert len(r['entries'])==1
    assert r['fetched_remotely'] is False and r['fact_verified'] is False
    denied=client.post(f'/api/projects/{p}/rss-import',json={'feed_url':'https://example.com/rss','title':'Unsafe feed','xml_text':'<!DOCTYPE foo [<!ENTITY x SYSTEM "file:///etc/passwd">]><rss></rss>'})
    assert denied.status_code==422
    report=client.get(f'/api/projects/{p}/research-audit').json()
    assert report['independent_verification']=='NOT_PERFORMED'
    assert report['sources_bound']==0

def test_cross_project_source_must_be_bound(client):
    _,p1=project(client,'One');_,p2=project(client,'Two')
    sv=source(client,p1)
    claim={'proposition':'Claim based on cited fixture material for test only','source_version_id':sv,'locator':'section one'}
    denied=client.post(f'/api/projects/{p2}/claims',json=claim)
    assert denied.status_code==409
    post(client,f'/api/projects/{p2}/bind-source',{'source_version_id':sv})
    ok=post(client,f'/api/projects/{p2}/claims',claim)
    assert ok['verification_status']=='UNREVIEWED'
    audit=client.get(f'/api/projects/{p2}/research-audit').json()
    assert audit['sources_bound']==1
    assert len(audit['gaps'])>=1

def test_timed_story_locale_and_stale_plan(client):
    ch,p=project(client);seed_renderable(client,p)
    v=post(client,f'/api/projects/{p}/story-plan',{})
    t=v['story']
    assert t['beat_count']==2 and t['total_duration_ms']==3000
    assert t['beats'][0]['role']=='HOOK' and t['beats'][-1]['role']=='PAYOFF'
    cap=client.get(f'/api/projects/{p}/captions/hi-IN')
    assert cap.status_code==200 and '00:00:00,000 --> 00:00:01,500' in cap.text
    assert cap.headers['x-caption-timing']=='SCENE_APPROXIMATION_NOT_WORD_ALIGNED'
    post(client,f'/api/projects/{p}/locales',{'locale':'en-US','localized_scenes':['How did the field change?','Here is the result.'],'owner_checked':True})
    assert 'How did the field change?' in client.get(f'/api/projects/{p}/captions/en-US').text
    assert client.get(f'/api/projects/{p}/captions/es-ES').status_code==404
    post(client,f'/api/projects/{p}/scenes',{'text':'Third original scene','duration_seconds':1,'claim_ids':[]})
    assert client.get(f'/api/projects/{p}/captions/en-US').status_code==409

def test_analytics_provenance_and_missing_revenue(client):
    ch,p=project(client)
    a=post(client,'/api/analytics/owner-entry',{'channel_id':ch,'report_date':'2026-11-09','format':'SHORT','views':1250,'watch_hours':None})
    assert a['youtube_api_verified'] is False
    obs=client.get(f'/api/analytics/{ch}').json()['observations']
    assert obs[0]['views']==1250 and obs[0]['estimated_revenue'] is None
    assert obs[0]['provenance']=='OWNER_ENTERED_NOT_VERIFIED'
    invalid=client.post('/api/analytics/owner-entry',json={'channel_id':ch,'report_date':'2026-11-09','format':'SHORT','views':2000,'estimated_revenue':500})
    assert invalid.status_code==422
    assert client.get('/api/youtube/capabilities').json()['youtube_upload_enabled'] is False
    assert client.post('/api/youtube/upload').status_code==403

def test_private_review_export_is_not_publish_package(client):
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):pytest.skip('FFmpeg missing')
    ch,p=project(client);seed_renderable(client,p)
    post(client,f'/api/projects/{p}/story-plan',{})
    post(client,f'/api/projects/{p}/queue-preview',{})
    done=client.post('/api/jobs/run-next').json()
    assert done['state']=='SUCCEEDED',done
    view=client.get(f'/api/projects/{p}').json()
    rid=view['renders'][0]['render_attempt_id']
    assert client.post(f'/api/projects/{p}/review-video',json={'render_attempt_id':rid,'reviewer':'Owner',
        'rights_attested':False,'claims_attested':True,'watched_full_video':True,
        'notes':'This video was examined for production risks.'}).status_code==409
    review=post(client,f'/api/projects/{p}/review-video',{'render_attempt_id':rid,'reviewer':'Owner',
        'rights_attested':True,'claims_attested':True,'watched_full_video':True,
        'notes':'This is a synthetic local test and original graphics.'})
    assert review['publication_ready'] is False
    result=post(client,f'/api/projects/{p}/export-review-packet',{})
    assert result['status']=='REVIEW_ONLY'
    data=client.get(result['download_url'])
    assert data.status_code==200
    with zipfile.ZipFile(io.BytesIO(data.content)) as zipdata:
        assert 'technical_preview.mp4' in zipdata.namelist()
        assert 'approximate_scene_cards.srt' in zipdata.namelist()
        manifest=json.loads(zipdata.read('review_manifest.json'))
        assert manifest['publication_authorized'] is False
    # A material new script revision invalidates prior approval even when packet exists.
    post(client,f'/api/projects/{p}/script',{'text':'A new version with different analysis which must invalidate the previous approval.','claim_links':[]})
    assert client.post(f'/api/projects/{p}/export-review-packet').status_code==409

def test_youtube_analytics_header_based_normalization_without_network():
    from app.youtube_analytics import normalize_report
    report={'columnHeaders':[{'name':x} for x in ['views','day','subscribersGained','estimatedMinutesWatched']],
            'rows':[[150,'2026-11-08',3,90.0],[200,'2026-11-09',2,120.0]]}
    data=normalize_report(report)
    assert data[0]=={'report_date':'2026-11-08','views':150,'watch_hours':1.5,'subscribers_gained':3}
    assert data[1]['views']==200
    with pytest.raises(ValueError):normalize_report({'columnHeaders':[{'name':'views'}],'rows':[[123]]})


def test_no_silent_piper_install_or_network_fetch(client,monkeypatch):
    ch,p=project(client)
    from app.source_connectors import registry,fetch_approved
    monkeypatch.delenv('VIRALOS_APPROVED_FEEDS_FILE',raising=False)
    assert registry()=={}
    with pytest.raises(ValueError):fetch_approved('unconfigured')
    assert client.get('/api/research/approved-feeds').json()['default']=='DISABLED'
    assert client.get('/api/voice/piper-capabilities').json()['auto_voice_available'] is False
    assert client.post(f'/api/projects/{p}/voice/opt-in-piper').status_code==404
    assert client.post('/api/youtube/analytics/sync',json={'local_channel_id':ch,'start_date':'2026-11-01','end_date':'2026-11-20'}).status_code==404


def test_quality_report_is_fail_closed_for_unreviewed_project(client):
    ch,p=project(client)
    q=client.get(f'/api/projects/{p}/quality-report').json()
    assert q['status']=='BLOCKED_FOR_PUBLICATION'
    assert 'No narration audio' in q['issues']
    assert 'No playable render' in q['issues']
    assert q['research']['independent_verification']=='NOT_PERFORMED'


def test_m1_source_project_isolation_and_job_dedupe(client):
    _,p1=project(client,'One');_,p2=project(client,'Two')
    seed_renderable(client,p1);seed_renderable(client,p2)
    a=post(client,f'/api/projects/{p1}/queue-preview',{})
    b=post(client,f'/api/projects/{p2}/queue-preview',{})
    assert a['job_id']!=b['job_id']  # same script and storyboard across projects must not be merged
