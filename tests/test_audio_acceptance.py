"""Synthetic-fixture-only tests: do not assert that any real TTS/ASR model ran."""
from __future__ import annotations
import copy
import hashlib
import json
import math
import struct
import wave
from pathlib import Path
import pytest
from tools import audio_acceptance as v


def fixture(tmp_path: Path, locale="hi-IN"):
    wav = tmp_path / "owned_synthetic_fixture.wav"
    with wave.open(str(wav), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(16000)
        f.writeframes(b"".join(struct.pack("<h", round(4800 * math.sin(2 * math.pi * 220 * i / 16000))) for i in range(32000)))
    words = ["क्रिकेट", "NFL", "का", "विश्लेषण"] if locale == "hi-IN" else ["NFL", "route", "analysis", "today"]
    reference = [{"text": name, "start_ms": j * 410 + 50, "end_ms": j * 410 + 300} for j, name in enumerate(words)]
    candidate = [dict(word, start_ms=word["start_ms"] + 20, end_ms=word["end_ms"] + 30) for word in reference]
    manifest = {
        "schema_version": 1, "sample_id": "synthetic-test-only", "locale": locale,
        "audio_path": str(wav), "audio_sha256": v._hash_file(wav), "source_script_sha256": "a" * 64,
        "model": {"voice_id": "synthetic-test-not-real-model", "voice_weights_sha256": "b" * 64,
                  "aligner_name": "synthetic-test-not-real-model", "aligner_weights_sha256": "c" * 64,
                  "license_name": "synthetic-test-fixture-not-a-voice-license", "license_reviewed_by": "test-runner", "owner_approved_license": True},
        "alignment": {"candidate_source": "LOCAL_MODEL_OUTPUT", "reference_words": reference, "candidate_words": candidate},
        "review": {"owned_or_licensed_audio": True, "reference_timings_human_checked": True,
                   "full_audio_listened": True, "listener": "synthetic-test-only", "naturalness_1_to_5": 4.4,
                   "pronunciation_checks": [{"term": words[0], "correct": True}]},
    }
    target = tmp_path / "manifest.json"
    target.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    return target, manifest, wav


def test_good_synthetic_metrics_are_not_independent_approval(tmp_path):
    path, _, _ = fixture(tmp_path)
    result = v.evaluate(path)
    assert result["blockers"] == []
    assert result["word_boundary_p95_ms"] == 30
    assert result["word_boundary_mae_ms"] == 25
    assert result["real_model_executed_by_this_evaluator"] is False
    assert result["professional_quality_independently_verified"] is False
    assert result["status"] == "OWNER_RECORDED_ACCEPTANCE_EVIDENCE_NO_AUTOMATIC_PUBLISHING"
    assert "क्रिकेट" not in json.dumps(result, ensure_ascii=False)


def test_english_and_code_switch_metrics(tmp_path):
    path, _, _ = fixture(tmp_path, "en-US")
    result = v.evaluate(path)
    assert result["locale"] == "en-US" and result["reference_word_count"] == 4


def test_tampered_audio_hash_fails_closed(tmp_path):
    path, _, wav = fixture(tmp_path)
    wav.write_bytes(wav.read_bytes() + b"extra")
    with pytest.raises(v.EvidenceError, match="hash"):
        v.evaluate(path)


def test_wrong_hindi_transliteration_not_accepted(tmp_path):
    path, m, _ = fixture(tmp_path)
    m["alignment"]["candidate_words"][0]["text"] = "cricket"
    path.write_text(json.dumps(m, ensure_ascii=False))
    outcome = v.evaluate(path)
    assert "TRANSCRIPT_WORDS_DO_NOT_MATCH_HUMAN_REFERENCE" in outcome["blockers"]
    assert outcome["word_boundary_mae_ms"] is None


def test_missing_or_added_word_blocks(tmp_path):
    path, m, _ = fixture(tmp_path)
    m["alignment"]["candidate_words"].pop()
    path.write_text(json.dumps(m, ensure_ascii=False))
    result = v.evaluate(path)
    assert "WORD_COUNT_MISMATCH" in result["blockers"]


def test_large_timing_drift_blocks(tmp_path):
    path, m, _ = fixture(tmp_path)
    for word in m["alignment"]["candidate_words"]:
        word["start_ms"] += 290
        word["end_ms"] += 290
    path.write_text(json.dumps(m, ensure_ascii=False))
    result = v.evaluate(path)
    assert "WORD_BOUNDARY_ERROR_EXCEEDS_ACCEPTANCE_THRESHOLD" in result["blockers"]
    assert result["word_boundary_p95_ms"] == 320


def test_missing_license_and_owner_reviews_block(tmp_path):
    path, m, _ = fixture(tmp_path)
    m["model"]["owner_approved_license"] = False
    m["review"]["full_audio_listened"] = False
    m["review"]["pronunciation_checks"][0]["correct"] = False
    m["alignment"]["candidate_source"] = "MANUAL_FIXTURE"
    path.write_text(json.dumps(m, ensure_ascii=False))
    blockers = v.evaluate(path)["blockers"]
    assert "MODEL_LICENSE_NOT_OWNER_APPROVED" in blockers
    assert "FULL_AUDIO_NOT_LISTENED" in blockers
    assert "NO_REAL_MODEL_OUTPUT_PROVENANCE" in blockers
    assert any(b.startswith("PRONUNCIATION_REVIEW_FAILED") for b in blockers)


def test_invalid_timestamps_overlap_and_duration_are_rejected(tmp_path):
    path, m, _ = fixture(tmp_path)
    m["alignment"]["reference_words"][1]["start_ms"] = -1
    path.write_text(json.dumps(m, ensure_ascii=False))
    with pytest.raises(v.EvidenceError, match="bounds"):
        v.evaluate(path)
    m["alignment"]["reference_words"][1]["start_ms"] = 100
    path.write_text(json.dumps(m, ensure_ascii=False))
    with pytest.raises(v.EvidenceError, match="overlapping"):
        v.evaluate(path)
    m["alignment"]["reference_words"][1]["start_ms"] = 500
    m["alignment"]["reference_words"][1]["end_ms"] = 2500
    path.write_text(json.dumps(m, ensure_ascii=False))
    with pytest.raises(v.EvidenceError, match="bounds"):
        v.evaluate(path)


def test_no_silence_or_clipped_audio_acceptance(tmp_path):
    path, m, wav = fixture(tmp_path)
    with wave.open(str(wav), 'wb') as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(16000)
        f.writeframes(b"\x00\x00" * 32000)
    m["audio_sha256"] = v._hash_file(wav)
    path.write_text(json.dumps(m, ensure_ascii=False))
    assert "SILENT_OR_NEAR_SILENT_AUDIO" in v.evaluate(path)["blockers"]
    with wave.open(str(wav), 'wb') as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(16000)
        f.writeframes(struct.pack('<h', 32767) * 32000)
    m["audio_sha256"] = v._hash_file(wav)
    path.write_text(json.dumps(m, ensure_ascii=False))
    assert "EXCESSIVE_CLIPPING" in v.evaluate(path)["blockers"]


def test_bogus_boolean_time_not_accepted(tmp_path):
    path, m, _ = fixture(tmp_path)
    m["alignment"]["reference_words"][0]["start_ms"] = True
    path.write_text(json.dumps(m, ensure_ascii=False))
    with pytest.raises(v.EvidenceError, match="integer"):
        v.evaluate(path)


def test_private_report_refuses_git_tree(tmp_path):
    path, _, _ = fixture(tmp_path)
    result = v.evaluate(path)
    with pytest.raises(v.EvidenceError, match="public Git repository"):
        v.write_private_report(result, v.ROOT / "should_not_write_audio_results.json")
    target = tmp_path / "private_report.json"
    ret = v.write_private_report(result, target)
    assert ret == target
    assert "क्रिकेट" not in target.read_text(encoding="utf-8")
    with pytest.raises(FileExistsError):
        v.write_private_report(result, target)


def test_cli_blocked_returns_nonzero_and_private_report(tmp_path, capsys):
    path, m, _ = fixture(tmp_path)
    m["review"]["naturalness_1_to_5"] = 1
    path.write_text(json.dumps(m, ensure_ascii=False))
    result_path = tmp_path / "result.json"
    assert v.main([str(path), "--report", str(result_path)]) == 2
    assert json.loads(result_path.read_text())["status"] == "BLOCKED"
    assert "NATURALNESS_BELOW_OWNER_THRESHOLD" in capsys.readouterr().out


def test_manifest_rejects_missing_invalid_locale_and_big_file(tmp_path):
    path, m, _ = fixture(tmp_path)
    m["locale"] = "unsupported"
    path.write_text(json.dumps(m, ensure_ascii=False))
    with pytest.raises(v.EvidenceError, match="hi-IN"):
        v.evaluate(path)
    path.write_bytes(b"0" * (300 * 1024 + 1))
    with pytest.raises(v.EvidenceError, match="300KB"):
        v.evaluate(path)


def test_normalization_preserves_lexical_identity_and_danda():
    assert v._token("क्रिकेट।", "test") == "क्रिकेट"
    assert v._token("NFL,", "test") == "nfl"
    with pytest.raises(v.EvidenceError, match="one word"):
        v._token("two words", "test")