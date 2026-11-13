"""Private manifest creation always starts unapproved (synthetic WAV fixtures)."""
import json
from pathlib import Path
import pytest
from tools import audio_acceptance as v
from tools import create_voice_manifest as maker
from test_audio_acceptance import fixture


def test_generate_missing_provenance_template(tmp_path):
    _, _, wav = fixture(tmp_path)
    dest = tmp_path / 'private' / 'draft.json'
    result = maker.create_template(wav, 'hi-IN', 'pilot-hi-test', dest)
    assert result['approved'] is False
    manifest = json.loads(dest.read_text('utf-8'))
    assert manifest['audio_sha256'] == v._hash_file(wav)
    assert manifest['alignment']['candidate_source'] == 'UNVERIFIED'
    assert manifest['model']['owner_approved_license'] is False
    assert manifest['review']['full_audio_listened'] is False
    with pytest.raises(v.EvidenceError):
        v.evaluate(dest)


def test_create_refuses_overwrite_and_repo_path(tmp_path):
    _, _, wav = fixture(tmp_path)
    dst = tmp_path / 'draft.json'
    maker.create_template(wav, 'en-US', 'abc-123', dst)
    with pytest.raises(FileExistsError):
        maker.create_template(wav, 'en-US', 'abc-123', dst)
    with pytest.raises(v.EvidenceError, match='Git repository'):
        maker.create_template(wav, 'en-US', 'abc-123', v.ROOT / 'private.json')


def test_invalid_locale_slug_and_audio(tmp_path):
    _, _, wav = fixture(tmp_path)
    dst = tmp_path / 'draft.json'
    with pytest.raises(v.EvidenceError):
        maker.create_template(wav, 'fr-FR', 'abc', dst)
    with pytest.raises(v.EvidenceError):
        maker.create_template(wav, 'hi-IN', '../abc', dst)
    wav.write_bytes(b'broken')
    with pytest.raises(v.EvidenceError):
        maker.create_template(wav, 'hi-IN', 'abc', dst)