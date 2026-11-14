"""Synthetic Piper CLI tests: never use or claim a real trained model."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import wave

import pytest
from tools import run_local_piper as p
from tools.audio_acceptance import EvidenceError


def _wav(path: Path, *, silence=False):
    import math
    with wave.open(str(path), 'wb') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(16000)
        pcm = bytearray()
        for i in range(16000):
            value = 0 if silence else round(math.sin(i * 2 * math.pi * 220 / 16000) * 5000)
            pcm += int(value).to_bytes(2, 'little', signed=True)
        f.writeframes(pcm)


def _fixture(tmp_path, locale='hi-IN'):
    private = tmp_path / 'PRIVATE'
    private.mkdir()
    binary = private / 'piper.exe'
    binary.write_bytes(b'test synthetic piper shim; never executed')
    model = private / 'voice.onnx'
    model.write_bytes(b'synthetic fake model - not a real neural network')
    (private / 'voice.onnx.json').write_text(json.dumps({
        'language': {'code': 'hi_IN' if locale == 'hi-IN' else 'en_US'},
    }), encoding='utf-8')
    text = private / 'script.txt'
    text.write_text('यह क्रिकेट का मूल विश्लेषण है। यह एक परीक्षण है।' if locale == 'hi-IN'
                    else 'This is an original local voice quality experiment.', encoding='utf-8')
    return dict(piper_exe=binary, model=model, locale=locale, text_file=text,
                sample_id='pilot-hi', out_dir=private / 'samples',
                license_name='Test-only owner reviewed stub licence', rights_reviewed=True)


def test_synthetic_local_cli_generates_private_unapproved_artifacts(tmp_path, monkeypatch):
    args = _fixture(tmp_path)
    calls = []
    def simulate(cmd, **kw):
        calls.append((cmd,kw))
        if '--model' in cmd:
            assert type(kw['input']) is bytes and 'क्रिकेट'.encode('utf-8') in kw['input']
            assert kw['env']['HF_HUB_OFFLINE'] == '1'
            _wav(Path(cmd[cmd.index('--output_file') + 1]))
        else:
            assert '-ar' in cmd and cmd[cmd.index('-ar') + 1] == '16000'
            _wav(Path(cmd[-1]))
        return subprocess.CompletedProcess(cmd, 0, stdout=b'', stderr=b'')
    monkeypatch.setattr(p.subprocess, 'run', simulate)
    monkeypatch.setattr(p.shutil, 'which', lambda cmd: 'ffmpeg' if cmd=='ffmpeg' else None)
    result = p.run_sample(**args)
    assert result['status'] == 'PENDING_HUMAN_REVIEW_AND_ALIGNMENT'
    assert result['publish_ready'] is False
    assert result['duration_ms'] == 1000
    folder = Path(result['private_sample_dir'])
    data = json.loads((folder / 'local-run-report.json').read_text(encoding='utf-8'))
    manifest = json.loads((folder / 'voice-evaluation-UNAPPROVED.json').read_text(encoding='utf-8'))
    assert data['synthesis_wall_seconds'] >= 0
    assert data['word_level_alignment_performed'] is False
    assert data['real_voice_naturalness_verified'] is False
    assert data['peak_ram_measured'] is False
    assert manifest['model']['owner_approved_license'] is True # operator attested only
    assert manifest['alignment']['candidate_words'] == []
    assert manifest['review']['full_audio_listened'] is False
    assert manifest['local_run_provenance']['owner_supplied_local_executable_invoked'] is True
    assert manifest['local_run_provenance']['model_inference_independently_verified'] is False
    assert manifest['model']['voice_weights_sha256'] == hashlib.sha256(args['model'].read_bytes()).hexdigest()
    assert len(calls) == 2
    with pytest.raises(EvidenceError,match='never overwritten'):
        p.run_sample(**args)


def test_en_us_matches_metadata_and_works(tmp_path, monkeypatch):
    args = _fixture(tmp_path, locale='en-US')
    def sim(cmd, **kw):
        _wav(Path(cmd[-1] if cmd[0]=='ffmpeg' else cmd[cmd.index('--output_file')+1]))
        return subprocess.CompletedProcess(cmd, 0)
    monkeypatch.setattr(p.subprocess,'run',sim)
    monkeypatch.setattr(p.shutil,'which',lambda a:'ffmpeg')
    assert p.run_sample(**args)['status']=='PENDING_HUMAN_REVIEW_AND_ALIGNMENT'


def test_mismatch_locale_blocks_without_running(tmp_path,monkeypatch):
    args = _fixture(tmp_path,locale='hi-IN')
    args['locale'] = 'en-US'
    monkeypatch.setattr(p.subprocess,'run', lambda *a,**k: pytest.fail('Executed Piper before validation'))
    with pytest.raises(EvidenceError,match='does not match'):
        p.run_sample(**args)


@pytest.mark.parametrize('patch', [{'rights_reviewed':False}, {'license_name':'unknown'},
                                    {'locale':'fr-FR'}, {'sample_id':'../bad'}])
def test_license_locale_and_sample_id_fail_closed(tmp_path,monkeypatch,patch):
    args={**_fixture(tmp_path), **patch}
    monkeypatch.setattr(p.subprocess,'run',lambda *a,**k:pytest.fail('unexpected model invocation'))
    with pytest.raises(EvidenceError):p.run_sample(**args)


def test_private_script_and_private_output_required(tmp_path, monkeypatch):
    args = _fixture(tmp_path)
    monkeypatch.setattr(p.subprocess, 'run', lambda *a,**k: pytest.fail('run called'))
    args['out_dir'] = p._inside_repo.__globals__['ROOT'] / 'private'
    with pytest.raises(EvidenceError,match='outside'):
        p.run_sample(**args)
    args = _fixture(tmp_path / 'another') if False else _fixture_other(tmp_path)
    args['text_file'] = p._inside_repo.__globals__['ROOT'] / 'README.md'
    with pytest.raises(EvidenceError,match='outside'):
        p.run_sample(**args)


def _fixture_other(tmp_path):
    d = tmp_path / 'new'
    d.mkdir()
    return _fixture(d)


def test_model_config_invalid_json_rejects(tmp_path, monkeypatch):
    args=_fixture(tmp_path)
    (args['model'].parent/'voice.onnx.json').write_text('{ invalid',encoding='utf-8')
    monkeypatch.setattr(p.subprocess,'run',lambda *a,**k:pytest.fail('run called'))
    with pytest.raises(EvidenceError,match='valid UTF-8 JSON'):
        p.run_sample(**args)


def test_piper_failure_and_timeout_cleanup(tmp_path,monkeypatch):
    args=_fixture(tmp_path)
    def fail(cmd,**kw):return subprocess.CompletedProcess(cmd, 1)
    monkeypatch.setattr(p.subprocess,'run',fail)
    with pytest.raises(EvidenceError,match='Piper process failed'):
        p.run_sample(**args)
    assert not (args['out_dir']/args['sample_id']).exists()
    def timeout(cmd,**kw):raise subprocess.TimeoutExpired(cmd,kw.get('timeout',20))
    monkeypatch.setattr(p.subprocess,'run',timeout)
    with pytest.raises(EvidenceError,match='timed out'):
        p.run_sample(**args)
    assert not (args['out_dir']/args['sample_id']).exists()


def test_ffmpeg_missing_rejects_and_removes_partial_sample(tmp_path,monkeypatch):
    args=_fixture(tmp_path)
    def produce(cmd,**kw):
        _wav(Path(cmd[cmd.index('--output_file')+1]));return subprocess.CompletedProcess(cmd,0)
    monkeypatch.setattr(p.subprocess,'run',produce)
    monkeypatch.setattr(p.shutil,'which',lambda x:None)
    with pytest.raises(EvidenceError,match='FFmpeg missing'):
        p.run_sample(**args)
    assert not (args['out_dir']/args['sample_id']).exists()


def test_silent_output_is_explicitly_blocked(tmp_path,monkeypatch):
    args=_fixture(tmp_path)
    def sim(cmd,**kw):
        _wav(Path(cmd[-1] if cmd[0]=='ffmpeg' else cmd[cmd.index('--output_file')+1]),silence=True)
        return subprocess.CompletedProcess(cmd,0)
    monkeypatch.setattr(p.subprocess,'run',sim)
    monkeypatch.setattr(p.shutil,'which',lambda _: 'ffmpeg')
    r=p.run_sample(**args)
    assert r['status']=='BLOCKED_AUDIO_QC'
    assert 'SILENT_OR_NEAR_SILENT_AUDIO' in r['blockers']
    assert r['publish_ready'] is False


def test_text_too_long_does_not_invoke_piper(tmp_path,monkeypatch):
    args=_fixture(tmp_path)
    args['text_file'].write_text('A'*1500,encoding='utf-8')
    monkeypatch.setattr(p.subprocess,'run',lambda *a,**k:pytest.fail('unexpected'))
    with pytest.raises(EvidenceError,match='12–1400'):
        p.run_sample(**args)

@pytest.mark.skipif(__import__('sys').platform == 'win32', reason='synthetic shim is a Unix shebang; Windows subprocess is mock-tested')
def test_real_ffmpeg_normalization_using_synthetic_executable_not_a_model(tmp_path):
    """Exercises actual local process + real FFmpeg, never trained-model voice inference."""
    if not shutil.which('ffmpeg'):
        pytest.skip('FFmpeg not installed')
    args = _fixture(tmp_path, locale='en-US')
    shim = args['piper_exe']
    shim.write_text('''#!/usr/bin/env python3
import sys, wave, math
argv=sys.argv
out=argv[argv.index('--output_file')+1]
text=sys.stdin.buffer.read().decode('utf-8')
assert 'original' in text
with wave.open(out,'wb') as f:
    f.setnchannels(1);f.setsampwidth(2);f.setframerate(48000)
    b=bytearray()
    for i in range(24000):
        x=round(math.sin(i*2*math.pi*220/48000)*5000)
        b.extend(int(x).to_bytes(2,'little',signed=True))
    f.writeframes(b)
''',encoding='utf-8')
    shim.chmod(0o755)
    result=p.run_sample(**args)
    assert result['status']=='PENDING_HUMAN_REVIEW_AND_ALIGNMENT'
    assert result['duration_ms'] == 500
    with wave.open(str(Path(result['private_sample_dir'])/'voice-16k.wav'),'rb') as f:
        assert f.getframerate()==16000 and f.getnchannels()==1 and f.getsampwidth()==2
    report=json.loads(Path(result['private_report']).read_text(encoding='utf-8'))
    assert report['real_voice_naturalness_verified'] is False
    assert report['word_level_alignment_performed'] is False