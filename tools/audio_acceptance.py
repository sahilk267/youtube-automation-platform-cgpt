"""Offline, non-publishing M2.5 voice and word-alignment acceptance evaluator.

Does NOT synthesize a voice, run WhisperX, translate scripts or validate a licence.
It verifies WAV and supplied candidate-versus-human reference timestamps and records
owner assertions without treating them as independent model/human quality proof.
Python standard library only; never writes private evidence into the git repo.
"""
from __future__ import annotations

import argparse
import array
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import secrets
import sys
import unicodedata
import wave

ROOT = Path(__file__).resolve().parents[1]
HASH = re.compile(r"^[0-9a-fA-F]{64}$")
SUPPORTED_LOCALES = {"hi-IN", "en-US"}
MAX_AUDIO_BYTES = 40 * 1024 * 1024
MAX_WORDS = 1500


class EvidenceError(ValueError):
    """Manifest or audio cannot be used as trustworthy evaluation evidence."""


def _hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for part in iter(lambda: f.read(1024 * 1024), b""):
            h.update(part)
    return h.hexdigest()


def _inside_repo(path: Path) -> bool:
    resolved = path.resolve()
    return resolved == ROOT or ROOT in resolved.parents


def _nonempty(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 256:
        raise EvidenceError(f"{field} must be nonempty text <=256 characters")
    return value.strip()


def _sha256(value: object, field: str) -> str:
    if not isinstance(value, str) or not HASH.fullmatch(value):
        raise EvidenceError(f"{field} must be SHA-256 hex")
    return value.lower()


def _token(text: object, field: str) -> str:
    if not isinstance(text, str) or not text.strip() or len(text) > 100:
        raise EvidenceError(f"{field} must contain one short word")
    # No romanization or translation: Devanagari and English text must match.
    norm = unicodedata.normalize("NFKC", text).casefold().strip()
    # Strip only surrounding punctuation (including danda); retain internal marks.
    while norm and unicodedata.category(norm[0]).startswith("P"):
        norm = norm[1:]
    while norm and unicodedata.category(norm[-1]).startswith("P"):
        norm = norm[:-1]
    if not norm or any(ch.isspace() for ch in norm):
        raise EvidenceError(f"{field} must represent exactly one word")
    return norm


def _words(rows: object, field: str, duration_ms: int) -> list[tuple[str, int, int]]:
    if not isinstance(rows, list) or not 1 <= len(rows) <= MAX_WORDS:
        raise EvidenceError(f"{field} must contain 1..{MAX_WORDS} timed words")
    out = []
    for i, item in enumerate(rows):
        if not isinstance(item, dict):
            raise EvidenceError(f"{field}[{i}] must be an object")
        token = _token(item.get("text"), f"{field}[{i}].text")
        start, end = item.get("start_ms"), item.get("end_ms")
        if type(start) is not int or type(end) is not int:
            raise EvidenceError(f"{field}[{i}] timestamps must be integer milliseconds")
        if start < 0 or end <= start or end > duration_ms + 30:
            raise EvidenceError(f"{field}[{i}] out of audio bounds")
        if out and start < out[-1][1]:
            raise EvidenceError(f"{field} must have nondecreasing start times")
        if out and out[-1][2] - start > 20:
            raise EvidenceError(f"{field} has substantially overlapping words")
        out.append((token, start, end))
    return out


def inspect_wave(path: Path) -> dict:
    if not path.is_file() or path.stat().st_size > MAX_AUDIO_BYTES:
        raise EvidenceError("Audio file missing or exceeds 40MB")
    try:
        with wave.open(str(path), "rb") as source:
            channels, width, rate, frames = (source.getnchannels(), source.getsampwidth(),
                                               source.getframerate(), source.getnframes())
            if channels != 1 or width != 2 or rate != 16000:
                raise EvidenceError("Expected normalized 16 kHz mono PCM16 WAV")
            if frames <= 0 or frames > 16000 * 120:
                raise EvidenceError("Audio must be >0 and <=120 seconds")
            raw = source.readframes(frames)
    except (EOFError, wave.Error, OSError) as exc:
        raise EvidenceError("WAV cannot be decoded") from exc
    if len(raw) != frames * 2:
        raise EvidenceError("WAV is truncated")
    values = array.array("h")
    values.frombytes(raw)
    if sys.byteorder != "little":
        values.byteswap()
    peak = max(abs(v) for v in values) / 32768
    rms = math.sqrt(sum(v * v for v in values) / len(values)) / 32768
    clip = sum(abs(v) >= 32680 for v in values) / len(values)
    return {
        "duration_ms": round(frames * 1000 / 16000),
        "sample_rate_hz": 16000,
        "peak_fraction": round(peak, 6),
        "rms_fraction": round(rms, 6),
        "clipping_fraction": round(clip, 6),
        "blockers": (["SILENT_OR_NEAR_SILENT_AUDIO"] if rms < 0.007 else [])
                    + (["EXCESSIVE_CLIPPING"] if clip > 0.015 else []),
    }


def _percentile(values: list[int], percentage: float) -> int:
    ordered = sorted(values)
    return ordered[min(len(values) - 1, max(0, math.ceil(percentage * len(values)) - 1))]


def evaluate(manifest_path: Path) -> dict:
    """Score owner-supplied inputs; never claim an unobserved model ran."""
    manifest_path = manifest_path.expanduser().resolve()
    if not manifest_path.is_file() or manifest_path.stat().st_size > 300 * 1024:
        raise EvidenceError("Manifest missing or larger than 300KB")
    try:
        m = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise EvidenceError("Malformed UTF-8 JSON manifest") from exc
    if not isinstance(m, dict) or type(m.get("schema_version")) is not int or m["schema_version"] != 1:
        raise EvidenceError("Unsupported M2.5 manifest schema")
    locale = m.get("locale")
    if locale not in SUPPORTED_LOCALES:
        raise EvidenceError("Only explicit hi-IN or en-US manifests are supported")
    sample_id = _nonempty(m.get("sample_id"), "sample_id")
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,60}", sample_id):
        raise EvidenceError("sample_id must be a safe non-identifying slug")
    audio_raw = _nonempty(m.get("audio_path"), "audio_path")
    audio_path = Path(audio_raw).expanduser()
    if not audio_path.is_absolute():
        audio_path = manifest_path.parent / audio_path
    audio_path = audio_path.resolve()
    actual_audio_sha = _hash_file(audio_path) if audio_path.is_file() and audio_path.stat().st_size <= MAX_AUDIO_BYTES else None
    expected_audio_sha = _sha256(m.get("audio_sha256"), "audio_sha256")
    if actual_audio_sha is None or actual_audio_sha != expected_audio_sha:
        raise EvidenceError("Voice WAV missing or hash does not match supplied approval fingerprint")
    wave_info = inspect_wave(audio_path)
    _sha256(m.get("source_script_sha256"), "source_script_sha256")

    alignment = m.get("alignment")
    if not isinstance(alignment, dict):
        raise EvidenceError("alignment object required")
    refs = _words(alignment.get("reference_words"), "reference_words", wave_info["duration_ms"])
    candidates = _words(alignment.get("candidate_words"), "candidate_words", wave_info["duration_ms"])
    model = m.get("model")
    if not isinstance(model, dict):
        raise EvidenceError("model object required")
    model_id = _nonempty(model.get("voice_id"), "model.voice_id")
    voice_sha = _sha256(model.get("voice_weights_sha256"), "model.voice_weights_sha256")
    aligner_sha = _sha256(model.get("aligner_weights_sha256"), "model.aligner_weights_sha256")
    license_name = _nonempty(model.get("license_name"), "model.license_name")
    _nonempty(model.get("license_reviewed_by"), "model.license_reviewed_by")
    _nonempty(model.get("aligner_name"), "model.aligner_name")
    reviewer = m.get("review")
    if not isinstance(reviewer, dict):
        raise EvidenceError("review object required")

    blockers = list(wave_info["blockers"])
    if not model.get("owner_approved_license") is True:
        blockers.append("MODEL_LICENSE_NOT_OWNER_APPROVED")
    if not reviewer.get("owned_or_licensed_audio") is True:
        blockers.append("AUDIO_RIGHTS_NOT_ATTESTED")
    if alignment.get("candidate_source") != "LOCAL_MODEL_OUTPUT":
        blockers.append("NO_REAL_MODEL_OUTPUT_PROVENANCE")
    if not reviewer.get("reference_timings_human_checked") is True:
        blockers.append("REFERENCE_TIMINGS_NOT_HUMAN_CHECKED")
    if not reviewer.get("full_audio_listened") is True:
        blockers.append("FULL_AUDIO_NOT_LISTENED")
    listener = reviewer.get("listener")
    if not isinstance(listener, str) or not listener.strip():
        blockers.append("VOICE_LISTENER_MISSING")
    rating = reviewer.get("naturalness_1_to_5")
    if type(rating) not in (int, float) or not math.isfinite(rating) or not 1 <= rating <= 5:
        blockers.append("NATURALNESS_RATING_UNRECORDED")
    elif rating < 4:
        blockers.append("NATURALNESS_BELOW_OWNER_THRESHOLD")
    pronunciations = reviewer.get("pronunciation_checks")
    if not isinstance(pronunciations, list) or len(pronunciations) < 1:
        blockers.append("NO_PRONUNCIATION_LISTENER_CHECKS")
        pronunciation_count = 0
    else:
        pronunciation_count = len(pronunciations)
        for j, item in enumerate(pronunciations):
            if not isinstance(item, dict) or not item.get("term") or item.get("correct") is not True:
                blockers.append(f"PRONUNCIATION_REVIEW_FAILED_{j}")
    if len(refs) != len(candidates):
        blockers.append("WORD_COUNT_MISMATCH")
    matching_tokens = len(refs) == len(candidates) and all(a[0] == b[0] for a, b in zip(refs, candidates))
    if not matching_tokens:
        blockers.append("TRANSCRIPT_WORDS_DO_NOT_MATCH_HUMAN_REFERENCE")
    errors = []
    if matching_tokens:
        for ref, candidate in zip(refs, candidates):
            errors.extend((abs(ref[1] - candidate[1]), abs(ref[2] - candidate[2])))
    p95 = _percentile(errors, 0.95) if errors else None
    mae = round(sum(errors) / len(errors), 2) if errors else None
    if p95 is not None and (p95 > 250 or mae > 120):
        blockers.append("WORD_BOUNDARY_ERROR_EXCEEDS_ACCEPTANCE_THRESHOLD")
    # Deliberately redact word text and model paths from the report.
    return {
        "schema_version": 1,
        "sample_id": sample_id,
        "locale": locale,
        "evaluated_at_utc": datetime.now(timezone.utc).isoformat(),
        "audio_sha256": actual_audio_sha,
        "source_script_sha256": m["source_script_sha256"].lower(),
        "voice_model_sha256": voice_sha,
        "aligner_model_sha256": aligner_sha,
        "voice_id": model_id,
        "license_label_owner_supplied": license_name,
        "audio": wave_info,
        "reference_word_count": len(refs),
        "candidate_word_count": len(candidates),
        "word_boundary_mae_ms": mae,
        "word_boundary_p95_ms": p95,
        "owner_review_rating": rating if type(rating) in (int, float) and math.isfinite(rating) and 1 <= rating <= 5 else None,
        "pronunciation_checks_count": pronunciation_count,
        "blockers": list(dict.fromkeys(blockers)),
        "status": "OWNER_RECORDED_ACCEPTANCE_EVIDENCE_NO_AUTOMATIC_PUBLISHING" if not blockers else "BLOCKED",
        "real_model_executed_by_this_evaluator": False,
        "model_provenance_licenses_independently_verified": False,
        "professional_quality_independently_verified": False,
        "youtube_upload_performed": False,
        "owner_windows_hardware_measured_by_this_evaluator": False,
    }


def write_private_report(report: dict, destination: Path | None = None) -> Path:
    folder = Path.home() / "ViralOSPrivateReports"
    if destination is None:
        destination = folder / ("m25-" + secrets.token_hex(8) + ".json")
    destination = destination.expanduser().resolve()
    if _inside_repo(destination):
        raise EvidenceError("Private acceptance reports cannot be written into the public Git repository")
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    with destination.open("x", encoding="utf-8") as file:
        file.write(payload)
    if os.name != "nt":
        os.chmod(destination, 0o600)
    return destination


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Offline owner-audio and forced-alignment evidence evaluator")
    parser.add_argument("manifest", type=Path, help="Private local JSON manifest (not committed)")
    parser.add_argument("--report", type=Path, help="Optional NEW report path outside git; default ~/ViralOSPrivateReports")
    args = parser.parse_args(argv)
    try:
        outcome = evaluate(args.manifest)
        report_path = write_private_report(outcome, args.report)
        print(json.dumps({"status": outcome["status"], "blockers": outcome["blockers"], "report": str(report_path)}, ensure_ascii=False))
        return 0 if not outcome["blockers"] else 2
    except (EvidenceError, OSError) as exc:
        print(json.dumps({"status": "INVALID_EVIDENCE", "reason": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())