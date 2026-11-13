"""Real API + CPU-media integration tests for M2.1. No synthetic factual claims or YouTube upload."""
import io, math, struct, wave, shutil, json
from fastapi.testclient import TestClient
import pytest
from app.main import app
import app.main as main
from app import db
from app.director_m21 import make_segments

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv('VIRALOS_DB',str(tmp_path/'test.db'))
    monkeypatch.setattr(main,'OUT',tmp_path/'output')
    with TestClient(app) as c:yield c

def post(c,url,body):
    r=c.post(url,json=body)
    assert r.status_code==200,(r.status_code,r.text)
    return r.json()

def seeded(c,locale='en-US',sport='nfl',text=None):
    ch=post(c,'/api/channels',{'name':'Director channel','sport_id':sport,'locale':locale,
         'market':'USA' if sport=='nfl' else 'India','timezone':'America/New_York' if sport=='nfl' else 'Asia/Kolkata'})
    p=post(c,'/api/projects',{'channel_id':ch['channel_id'],'title':'Test original NFL visual explanation',
                            'original_angle':'Use original diagrams with independent explanation, no broadcast footage','format':'SHORT'})
    post(c,f"/api/projects/{p['project_id']}/script",{'text':text or 'Look at this original illustration. The two defensive positions explain the strategic choice clearly. The result is a tactical lesson, not a report of a real match.','claim_links':[]})
    return p['project_id']

def wav(secs=1.3,rate=16000,frequency=220):
    b=io.BytesIO();ns=round(secs*rate)
    with wave.open(b,'wb') as w:
        w.setframerate(rate);w.setnchannels(1);w.setsampwidth(2)
        w.writeframes(b''.join(struct.pack('<h',int(6000*math.sin(2*math.pi*frequency*i/rate))) for i in range(ns)))
    return b.getvalue()

def uploaded(c,p,did,segments):
    for i in range(len(segments)):
        r=c.post(f'/api/projects/{p}/director/drafts/{did}/voice/{i}',files={'file':('voice.wav',wav(1.1+i*.15),'audio/wav')})
        assert r.status_code==200,(r.status_code,r.text)
        assert r.json()['alignment']=='MEASURED_SEGMENT_DURATION_NOT_WORD_LEVEL'

def test_script_coverage_and_no_fabrication():
    original='First sentence introduces a useful question. Second sentence provides a helpful measured explanation. Third sentence gives a clear conclusion.'
    result=make_segments(original)
    assert ' '.join(result)==original
    assert len(result)==3
    assert make_segments('One useful tactical position can change an entire decision during a match without altering the actual result.')[0]
    with pytest.raises(ValueError):make_segments('Short answer.')
    with pytest.raises(ValueError):make_segments(' '.join('word' for _ in range(255)))

def test_draft_original_and_missing_voice_blocks(client):
    p=seeded(client)
    cap=client.get('/api/director/capabilities').json()
    assert cap['automatic_dubbing'] is False and cap['word_level_forced_alignment'] is False
    d=post(client,f'/api/projects/{p}/director/drafts',{'locale':'en-US'})
    assert d['notes']['claim_verification']=='NOT_PERFORMED_BY_CREATIVE_DIRECTOR'
    assert post(client,f'/api/projects/{p}/director/drafts',{'locale':'en-US'})['already_exists'] is True
    assert client.post(f"/api/projects/{p}/director/drafts/{d['draft_id']}/assemble").status_code==409
    view=client.get(f"/api/projects/{p}/director/drafts/{d['draft_id']}").json()
    assert all(not s['audio_ready'] for s in view['segments'])

def test_locale_gates_and_project_isolation(client):
    p=seeded(client)
    assert client.post(f'/api/projects/{p}/director/drafts',json={'locale':'hi-IN'}).status_code==422
    assert client.post(f'/api/projects/{p}/director/drafts',json={'locale':'hi-IN','translated_script':'Yeh asli demonstration hai, kisi real match ki recording nahi.','locale_reviewed':False}).status_code==422
    translated='यह वास्तविक मैच फुटेज नहीं है। यह एक मौलिक रणनीतिक चित्र है। हम खिलाड़ियों की स्थितियों को समझाते हैं और अंत में सीख बताते हैं।'
    d=post(client,f'/api/projects/{p}/director/drafts',{'locale':'hi-IN','translated_script':translated,'locale_reviewed':True})
    p2=seeded(client)
    assert client.get(f"/api/projects/{p2}/director/drafts/{d['draft_id']}").status_code==404
    assert client.post(f"/api/projects/{p2}/director/drafts/{d['draft_id']}/voice/0",files={'file':('a.wav',wav(),'audio/wav')}).status_code==404

def test_invalid_and_silent_wav_denied(client):
    p=seeded(client);d=post(client,f'/api/projects/{p}/director/drafts',{'locale':'en-US'})
    did=d['draft_id'];path=f'/api/projects/{p}/director/drafts/{did}/voice/0'
    assert client.post(path,files={'file':('x.wav',b'NOTWAV','audio/wav')}).status_code==422
    b=io.BytesIO()
    with wave.open(b,'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(16000);w.writeframes(b'\0\0'*16000)
    assert client.post(path,files={'file':('silent.wav',b.getvalue(),'audio/wav')}).status_code==422
    assert client.post(path,files={'file':('valid.wav',wav(2),'audio/wav')}).status_code==200
    assert client.post(f'/api/projects/{p}/director/drafts/{did}/voice/400',files={'file':('v.wav',wav(),'audio/wav')}).status_code==422

def test_stale_after_script_revision(client):
    p=seeded(client);d=post(client,f'/api/projects/{p}/director/drafts',{'locale':'en-US'})
    post(client,f'/api/projects/{p}/script',{'text':'A new original analysis has a different opening. It needs a fresh sequence and separately recorded narration to stay correct.','claim_links':[]})
    resp=client.post(f"/api/projects/{p}/director/drafts/{d['draft_id']}/voice/0",files={'file':('valid.wav',wav(),'audio/wav')})
    assert resp.status_code==409

def test_measured_audio_full_render_and_unique_plan(client):
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):pytest.skip('FFmpeg unavailable')
    p=seeded(client)
    d=post(client,f'/api/projects/{p}/director/drafts',{'locale':'en-US'})
    did=d['draft_id'];uploaded(client,p,did,d['segments'])
    result=client.post(f'/api/projects/{p}/director/drafts/{did}/assemble')
    assert result.status_code==200,result.text
    obj=result.json();assert obj['duration_ms']>2000 and obj['shot_count']==len(d['segments'])
    assert obj['caption_alignment']=='MEASURED_SEGMENT_LEVEL_NOT_WORD_LEVEL'
    assert client.post(f'/api/projects/{p}/director/drafts/{did}/assemble').status_code==409
    assert client.post(f'/api/projects/{p}/director/drafts/{did}/voice/0',files={'file':('new.wav',wav(),'audio/wav')}).status_code==409
    saved=client.get(f'/api/projects/{p}/studio/plan').json()['plan']
    assert saved['captions_provenance']=='SEGMENT_TIMED_MEASURED'
    assert len(saved['captions'])==len(d['segments'])
    assert 'Look at this' in saved['captions'][0]['text']
    q=post(client,f'/api/projects/{p}/studio/queue',{})
    done=client.post('/api/studio/run-next').json()
    assert done['state']=='SUCCEEDED',done
    qc=client.get(done['report_url']).json()
    assert qc['quality']['caption_alignment']=='MEASURED_SEGMENT_LEVEL_NOT_WORD_LEVEL'
    assert qc['quality']['publish_ready'] is False
    assert qc['quality']['voice_present'] is True
    video=client.get(done['preview_url'])
    assert video.status_code==200 and len(video.content)>20000

def test_hindi_project_variant_with_owner_voice(client):
    p=seeded(client,locale='hi-IN',sport='cricket',text='देखिए यह मैदान का मूल चित्र है। यह किसी असली मैच की रिकॉर्डिंग नहीं है। हम केवल रणनीति को समझा रहे हैं।')
    d=post(client,f'/api/projects/{p}/director/drafts',{'locale':'hi-IN'})
    uploaded(client,p,d['draft_id'],d['segments'])
    a=client.post(f"/api/projects/{p}/director/drafts/{d['draft_id']}/assemble")
    assert a.status_code==200,a.text
    plan=client.get(f'/api/projects/{p}/studio/plan').json()['plan']
    assert plan['locale']=='hi-IN' and 'देखिए' in plan['captions'][0]['text']

def test_audio_binding_tamper_rejected(client):
    p=seeded(client);d=post(client,f'/api/projects/{p}/director/drafts',{'locale':'en-US'});uploaded(client,p,d['draft_id'],d['segments'])
    obj=client.post(f"/api/projects/{p}/director/drafts/{d['draft_id']}/assemble").json()
    with db.read() as c:
        row=db.one(c,'SELECT voice_relpath FROM m21_plan_audio WHERE plan_id=?',(obj['plan_id'],))
    path=main.OUT/row['voice_relpath'];path.write_bytes(path.read_bytes()+b'corrupt')
    resp=client.post(f'/api/projects/{p}/studio/queue')
    assert resp.status_code==409

def test_piper_missing_model_blocks_without_network(client,monkeypatch):
    p=seeded(client);d=post(client,f'/api/projects/{p}/director/drafts',{'locale':'en-US'})
    for key in ('VIRALOS_PIPER_EXE','VIRALOS_PIPER_MODEL','VIRALOS_PIPER_MODEL_RIGHTS_OK','VIRALOS_PIPER_LOCALE'):
        monkeypatch.delenv(key,raising=False)
    r=client.post(f"/api/projects/{p}/director/drafts/{d['draft_id']}/synthesize-piper")
    assert r.status_code==409


def test_piper_adapter_with_mock_only(client,monkeypatch,tmp_path):
    # Validates our adapter wiring but does NOT claim a real Piper model was installed/tested.
    from app import tts
    p=seeded(client);d=post(client,f'/api/projects/{p}/director/drafts',{'locale':'en-US'})
    monkeypatch.setenv('VIRALOS_PIPER_LOCALE','en-US')
    monkeypatch.setattr(tts,'piper_config',lambda:{'installed':True,'licensed_model_reviewed':True})
    def fake_piper(text,output):
        with open(output,'wb') as f:f.write(wav(1.3))
        return {'generated':True,'source':'MOCK_TTS'}
    monkeypatch.setattr(tts,'generate',fake_piper)
    resp=client.post(f"/api/projects/{p}/director/drafts/{d['draft_id']}/synthesize-piper")
    assert resp.status_code==200,resp.text
    assert len(resp.json()['generated_segments'])==len(d['segments'])
    with db.read() as c:
        types={r['source_kind'] for r in db.many(c,'SELECT source_kind FROM m21_voice_segments WHERE draft_id=?',(d['draft_id'],))}
    assert types=={'OPT_IN_LOCAL_PIPER'}
    assembled=client.post(f"/api/projects/{p}/director/drafts/{d['draft_id']}/assemble")
    assert assembled.status_code==200,assembled.text
    assert assembled.json()['voice_sources']==['OPT_IN_LOCAL_PIPER']


def test_translation_renders_separate_localized_audio(client):
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):pytest.skip('FFmpeg unavailable')
    p=seeded(client)
    translated='यह किसी लाइव गेम की रिकॉर्डिंग नहीं है। इस मौलिक चित्र से हम खेल की रणनीति समझाते हैं। अब हम अपना निष्कर्ष देखते हैं।'
    d=post(client,f'/api/projects/{p}/director/drafts',{'locale':'hi-IN','translated_script':translated,'locale_reviewed':True})
    uploaded(client,p,d['draft_id'],d['segments'])
    a=client.post(f"/api/projects/{p}/director/drafts/{d['draft_id']}/assemble")
    assert a.status_code==200,a.text
    plan=client.get(f'/api/projects/{p}/studio/plan').json()['plan']
    assert plan['locale']=='hi-IN' and plan['locale_reviewed'] is True
    assert client.get(f"/api/projects/{p}/director/drafts/{d['draft_id']}").status_code==200
    post(client,f'/api/projects/{p}/studio/queue',{})
    r=client.post('/api/studio/run-next').json()
    assert r['state']=='SUCCEEDED',r
    assert client.get(r['preview_url']).status_code==200

def test_measured_srt_file_and_project_boundary(client):
    p=seeded(client);d=post(client,f'/api/projects/{p}/director/drafts',{'locale':'en-US'});
    uploaded(client,p,d['draft_id'],d['segments'])
    obj=client.post(f"/api/projects/{p}/director/drafts/{d['draft_id']}/assemble").json()
    resp=client.get(f"/api/projects/{p}/director/plans/{obj['plan_id']}/captions.srt")
    assert resp.status_code==200
    assert '00:00:00,000 -->' in resp.text and 'Look at this original illustration.' in resp.text
    p2=seeded(client)
    assert client.get(f"/api/projects/{p2}/director/plans/{obj['plan_id']}/captions.srt").status_code==404


def test_evidence_link_transfer_requires_exact_unique_quote(client):
    from app.director_m21 import mapped_claims
    script='A precise test phrase matters here. This is our final conclusion without any real match result.'
    segments=make_segments(script)
    links=[{'claim_id':'claim-1','span_start':2,'span_end':21}]
    mapped=mapped_claims(segments,script,links)
    assert sum(len(x) for x in mapped)==1
    # Two repeated textual matches: do not automatically assign evidence to either occurrence.
    duplicate='same phrase. same phrase.'
    ambiguous=mapped_claims(make_segments(duplicate),duplicate,[{'claim_id':'claim-2','span_start':0,'span_end':11}])
    assert not any(ambiguous)
