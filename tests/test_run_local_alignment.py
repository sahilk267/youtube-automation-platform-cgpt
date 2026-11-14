"""Synthetic-only tests for opt-in local WhisperX alignment runner.

No trained models/voices and NO real WhisperX inference in these tests.
"""
import hashlib
import json
import math
from pathlib import Path
import struct
import subprocess
import sys
import wave

import pytest
from tools import run_local_alignment as a
from tools.audio_acceptance import EvidenceError, _hash_file


@pytest.fixture
def rig(tmp_path, monkeypatch):
    sample = tmp_path / 'PRIVATE' / 'cricket-hi-pilot'
    sample.mkdir(parents=True)
    text = 'क्रिकेट में गेंद स्विंग करती है'
    script = tmp_path / 'PRIVATE' / 'script.txt'
    script.write_text(text+'\n', encoding='utf-8')
    wav = sample / 'voice-16k.wav'
    with wave.open(str(wav), 'wb') as out:
        out.setnchannels(1);out.setsampwidth(2);out.setframerate(16000)
        out.writeframes(b''.join(struct.pack('<h', round(2500*math.sin(2*math.pi*220*i/16000))) for i in range(16000*3)))
    manifest = {
        'schema_version':1,'locale':'hi-IN','sample_id':'cricket-hi-pilot',
        'audio_path':str(wav.resolve()),'audio_sha256':_hash_file(wav),
        'source_script_sha256':'REPLACE_WITH_REAL_APP_SCRIPT_SHA256',
        'model': {'voice_id':'local-test','voice_weights_sha256':'a'*64,
                  'license_name':'owner-supplied','aligner_name':'REPLACE_ALIGNER_ID',
                  'aligner_weights_sha256':'REPLACE_WITH_ACTUAL_SHA256'},
        'alignment': {'candidate_source':'UNVERIFIED','reference_words':[], 'candidate_words':[]},
        'review': {'full_audio_listened':False},
        'local_run_provenance': {'producer':'OWNER_SUPPLIED_LOCAL_PIPER',
                                 'input_text_sha256':hashlib.sha256(text.encode()).hexdigest()},
    }
    (sample/'voice-evaluation-UNAPPROVED.json').write_text(json.dumps(manifest,ensure_ascii=False),encoding='utf-8')
    model=tmp_path/'PRIVATE'/'model-hi'
    model.mkdir()
    (model/'config.json').write_text('{"language":"hi"}',encoding='utf-8')
    (model/'test.safetensors').write_bytes(b'synthetic-not-a-trained-model')
    tokens=text.split()
    fake_words=[{'text':t,'start_ms':i*400,'end_ms':i*400+180} for i,t in enumerate(tokens)]
    return sample,script,model,tokens,fake_words


def fake_invoke(words):
    def invoke(**kwargs):
        kwargs['staging'].write_text(json.dumps({'schema_version':1,
           'worker':'OWNER_OPTED_IN_LOCAL_WHISPERX_CPU', 'candidate_words': words},ensure_ascii=False),encoding='utf-8')
        return {'alignment_wall_seconds':1.2,'peak_worker_tree_rss_mb':None,
                'memory_measurement':'UNAVAILABLE_PSUTIL_NOT_INSTALLED'}
    return invoke


def run(rig,monkeypatch,**kwargs):
    sample,script,model,tokens,words=rig
    monkeypatch.setattr(a,'_invoke_worker',fake_invoke(words))
    args={'sample_dir':sample,'script_file':script,'model_dir':model,
          'locale':'hi-IN','license_name':'owner-reviewed-model-license',
          'license_reviewed':True,'timeout_seconds':90}
    args.update(kwargs)
    return a.run_alignment(**args)


def test_success_creates_private_proposal_but_not_approved(rig,monkeypatch):
    result=run(rig,monkeypatch)
    assert result['publishing_authorized'] is False
    sample,script,model,tokens,words=rig
    original=json.loads((sample/'voice-evaluation-UNAPPROVED.json').read_text(encoding='utf-8'))
    assert original['alignment']['candidate_words']==[]
    proposed=json.loads((sample/a.RESULT_NAME).read_text(encoding='utf-8'))
    assert proposed['candidate_words']==words and proposed['owner_human_word_review_complete'] is False
    draft=json.loads((sample/a.MANIFEST_NAME).read_text(encoding='utf-8'))
    assert draft['alignment']['candidate_source']=='LOCAL_MODEL_OUTPUT'
    assert draft['alignment']['reference_words']==[]
    assert draft['local_alignment_provenance']['model_license_independently_verified'] is False
    report=json.loads((sample/a.REPORT_NAME).read_text(encoding='utf-8'))
    assert 'candidate_words' not in report and 'audio_path' not in report
    assert report['peak_worker_tree_rss_mb'] is None


def test_refuses_repeat_without_overwrite(rig,monkeypatch):
    run(rig,monkeypatch)
    with pytest.raises(EvidenceError,match='Prior alignment'):
        run(rig,monkeypatch)


def test_rejects_unreviewed_license(rig,monkeypatch):
    with pytest.raises(EvidenceError,match='licence'):
        run(rig,monkeypatch,license_reviewed=False)
    assert not (rig[0]/a.RESULT_NAME).exists()


def test_rejects_placeholder_license(rig,monkeypatch):
    with pytest.raises(EvidenceError,match='licence'):
        run(rig,monkeypatch,license_name='unknown')


def test_rejects_locale_mismatch(rig,monkeypatch):
    with pytest.raises(EvidenceError,match='language'):
        run(rig,monkeypatch,locale='en-US')


def test_rejects_script_mismatch(rig,monkeypatch):
    rig[1].write_text('बदल गया यह हिन्दी क्रिकेट स्क्रिप्ट',encoding='utf-8')
    with pytest.raises(EvidenceError,match='Script content'):
        run(rig,monkeypatch)


def test_rejects_wav_tamper(rig,monkeypatch):
    with rig[0].joinpath('voice-16k.wav').open('ab') as f: f.write(b'A')
    with pytest.raises(EvidenceError,match='WAV hash'):
        run(rig,monkeypatch)


def test_rejects_model_config_wrong_language(rig,monkeypatch):
    (rig[2]/'config.json').write_text('{"language":"en"}',encoding='utf-8')
    with pytest.raises(EvidenceError,match='different language'):
        run(rig,monkeypatch)


def test_rejects_model_symlink(rig,monkeypatch,tmp_path):
    if sys.platform=='win32':pytest.skip('Symlink permissions on Windows vary')
    (rig[2]/'linked').symlink_to(rig[2]/'config.json')
    with pytest.raises(EvidenceError,match='regular files'):
        run(rig,monkeypatch)


def test_missing_or_substituted_model_words_cannot_be_padded(rig,monkeypatch):
    wrong=rig[4][:-1]
    monkeypatch.setattr(a,'_invoke_worker',fake_invoke(wrong))
    sample,script,model,*_=rig
    with pytest.raises(EvidenceError,match='omitted or added'):
        a.run_alignment(sample_dir=sample,script_file=script,model_dir=model,
                        locale='hi-IN',license_name='legal model license',license_reviewed=True)
    assert not (sample/a.RESULT_NAME).exists()
    assert not list(sample.glob('.alignment-*.stage.json'))


def test_wrong_script_words_are_blocked(rig,monkeypatch):
    wrong=list(rig[4]);wrong[0]=dict(wrong[0],text='Cricket')
    monkeypatch.setattr(a,'_invoke_worker',fake_invoke(wrong))
    sample,script,model,*_=rig
    with pytest.raises(EvidenceError,match='does not match'):
        a.run_alignment(sample_dir=sample,script_file=script,model_dir=model,
                        locale='hi-IN',license_name='legal model license',license_reviewed=True)


def test_invalid_timings_and_overlaps_block(rig,monkeypatch):
    for words in ([[dict(w, start_ms=-10) if i==0 else w for i,w in enumerate(rig[4])],
                   [dict(rig[4][0]),dict(rig[4][1], start_ms=90)]+rig[4][2:]]):
        monkeypatch.setattr(a,'_invoke_worker',fake_invoke(words))
        sample,script,model,*_=rig
        with pytest.raises(EvidenceError):
            a.run_alignment(sample_dir=sample,script_file=script,model_dir=model,
                            locale='hi-IN',license_name='legal model license',license_reviewed=True)
        assert not (sample/a.RESULT_NAME).exists()


def test_timeout_cleanup_does_not_destroy_piper_sample(rig,monkeypatch):
    def fail(**kwargs):raise EvidenceError('Offline aligner exceeded operator-selected timeout')
    monkeypatch.setattr(a,'_invoke_worker',fail)
    sample,script,model,*_=rig
    with pytest.raises(EvidenceError,match='timeout'):
        a.run_alignment(sample_dir=sample,script_file=script,model_dir=model,
                        locale='hi-IN',license_name='legal model license',license_reviewed=True)
    assert (sample/'voice-16k.wav').is_file()
    assert not (sample/a.REPORT_NAME).exists()


def test_worker_invokes_adapter_in_offline_mode(rig,monkeypatch):
    from app import alignment_m24
    sample,script,model,tokens,words=rig
    captured={}
    def fake_align(wav,plan):
        captured['env']={x:__import__('os').environ[x] for x in ['HF_HUB_OFFLINE','TRANSFORMERS_OFFLINE','HF_DATASETS_OFFLINE']}
        captured['plan']=plan
        return [{'token':w['text'], 'start_ms':w['start_ms'],'end_ms':w['end_ms']} for w in words]
    monkeypatch.setattr(alignment_m24,'align_transcript',fake_align)
    out=sample/'worker-evidence.json'
    a._write_worker_result(model=model,wav=sample/'voice-16k.wav',script_file=script,
                           locale='hi-IN',destination=out)
    assert captured['env']=={'HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1','HF_DATASETS_OFFLINE':'1'}
    assert captured['plan']['locale']=='hi-IN'
    assert len(json.loads(out.read_text(encoding='utf-8'))['candidate_words'])==len(tokens)


def test_rejects_private_output_inside_public_git(monkeypatch,tmp_path,rig):
    # Even an existing valid sample path is rejected if it points inside repo root.
    monkeypatch.setattr(a,'_inside_repo',lambda p: p == rig[0].resolve())
    with pytest.raises(EvidenceError,match='private'):
        run(rig,monkeypatch)


def test_model_tamper_mid_inference_fails(rig,monkeypatch):
    def tamper(**kwargs):
        fake_invoke(rig[4])(**kwargs)
        (rig[2]/'test.safetensors').write_bytes(b'changed weights!')
        return {'alignment_wall_seconds':1.2,'peak_worker_tree_rss_mb':None,
                'memory_measurement':'UNAVAILABLE_PSUTIL_NOT_INSTALLED'}
    monkeypatch.setattr(a,'_invoke_worker',tamper)
    sample,script,model,*_=rig
    with pytest.raises(EvidenceError,match='changed during inference'):
        a.run_alignment(sample_dir=sample,script_file=script,model_dir=model,
                        locale='hi-IN',license_name='legal model license',license_reviewed=True)
    assert not (sample/a.RESULT_NAME).exists()


def test_worker_main_fails_closed_when_model_load_is_rejected(rig,monkeypatch):
    # Deterministic failure regardless of whether optional WhisperX was installed.
    sample,script,model,*_=rig
    def fail(*args,**kwargs):
        raise EvidenceError('Local model execution unavailable or incompatible')
    monkeypatch.setattr(a,'_worker_model_align',fail)
    exit_code=a._worker_main(['--wav',str(sample/'voice-16k.wav'),
                 '--script-file',str(script),'--model-dir',str(model),
                 '--locale','hi-IN','--out',str(sample/'should-not-exist.json')])
    assert exit_code != 0
    assert not (sample/'should-not-exist.json').exists()


def test_invalid_alignment_structure_fails_cleanly(rig,monkeypatch):
    sample,script,model,*_=rig
    p=sample/'voice-evaluation-UNAPPROVED.json'
    m=json.loads(p.read_text(encoding='utf-8'))
    m['alignment']=None
    p.write_text(json.dumps(m,ensure_ascii=False),encoding='utf-8')
    with pytest.raises(EvidenceError,match='alignment structure'):
        run(rig,monkeypatch)


def test_memory_monitor_does_not_fabricate_missing_psutil(rig,monkeypatch):
    result=run(rig,monkeypatch)
    report=json.loads((rig[0]/a.REPORT_NAME).read_text(encoding='utf-8'))
    assert report['peak_worker_tree_rss_mb'] is None
    assert 'PSUTIL_NOT_INSTALLED' in report['memory_measurement']


def test_real_subprocess_uses_synthetic_whisperx_shim_only(rig,monkeypatch,tmp_path):
    """Tests actual child process/IPC, NEVER a trained WhisperX model."""
    import os
    sample,script,model,tokens,words=rig
    fake_pkg=tmp_path/'fake-library'
    fake_pkg.mkdir()
    (fake_pkg/'whisperx.py').write_text('''
def load_align_model(language_code, device, model_name):
    assert device == 'cpu'
    assert model_name
    return object(), {'locale':language_code}
def load_audio(path):
    return b'SYNTHETIC_AUDIO_FIXTURE'
def align(transcript, model, metadata, audio, device, return_char_alignments=False):
    assert device == 'cpu'
    words=transcript[0]['text'].split()
    return {'word_segments':[{'word':w,'start':i*0.35,'end':i*0.35+0.20}
                             for i,w in enumerate(words)]}
''', encoding='utf-8')
    # Trusted test-only injected shim, not present in production environment.
    monkeypatch.setenv('PYTHONPATH', str(fake_pkg)+os.pathsep+str(a.ROOT if hasattr(a,'ROOT') else Path(a.__file__).resolve().parents[1]))
    result=a.run_alignment(sample_dir=sample,script_file=script,model_dir=model,
                         locale='hi-IN',license_name='test-only, not a real model',
                         license_reviewed=True,timeout_seconds=60)
    assert result['word_proposals_count']==len(tokens)
    assert result['publishing_authorized'] is False
    report=json.loads((sample/a.REPORT_NAME).read_text(encoding='utf-8'))
    assert report['human_word_reference_review_complete'] is False