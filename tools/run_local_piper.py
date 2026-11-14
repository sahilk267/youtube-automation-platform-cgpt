"""M2.5 opt-in Piper operator harness: local model -> private WAV -> unapproved evidence.

Never downloads models, clones voices, approves publication, uploads to YouTube or
claims an independently-verified model licence. This is a local *execution*
workflow; tests use simulated CLI outputs, not trained-model inference.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

from tools.audio_acceptance import EvidenceError, _hash_file, _inside_repo, inspect_wave
from tools.create_voice_manifest import create_template

SUPPORTED_LOCALES = {"en-US": "en_US", "hi-IN": "hi_IN"}
MAX_TEXT_BYTES = 8192
MAX_CONFIG_BYTES = 1024 * 1024
MAX_MODEL_BYTES = 8 * 1024 * 1024 * 1024


def _outside_repo(path: Path, label: str) -> Path:
    path = path.expanduser().resolve()
    if _inside_repo(path):
        raise EvidenceError(f"{label} must stay outside the public Git repository")
    return path


def _valid_path(path: Path, label: str, limit: int) -> Path:
    path = path.expanduser().resolve()
    if not path.is_file() or not 0 < path.stat().st_size <= limit:
        raise EvidenceError(f"{label} missing, empty, or larger than allowed")
    return path


def _check_model_config(model: Path, locale: str) -> tuple[Path, str]:
    if model.suffix.lower() != ".onnx":
        raise EvidenceError("Piper voice model must be an existing .onnx file")
    config_path = _valid_path(Path(str(model) + ".json"), "Piper .onnx.json sidecar", MAX_CONFIG_BYTES)
    try:
        cfg = json.loads(config_path.read_text(encoding="utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise EvidenceError("Model config must be valid UTF-8 JSON") from exc
    if not isinstance(cfg, dict):
        raise EvidenceError("Piper model config must be an object")
    language = cfg.get("language")
    code = language.get("code") if isinstance(language, dict) else language
    if not isinstance(code, str) or code.replace("-", "_").lower() != SUPPORTED_LOCALES[locale].lower():
        raise EvidenceError(f"Model language metadata does not match requested {locale}")
    return config_path, str(code)


def _read_private_script(path: Path) -> str:
    path = _outside_repo(path, "Voice sample script")
    path = _valid_path(path, "Voice sample script", MAX_TEXT_BYTES)
    try:
        text = path.read_text(encoding="utf-8").strip()
    except UnicodeError as exc:
        raise EvidenceError("Voice sample script must be UTF-8") from exc
    if not 12 <= len(text) <= 1400:
        raise EvidenceError("Sample text must be 12–1400 Unicode characters")
    if any((ord(c) < 32 and c not in "\n\r\t") or ord(c) == 127 for c in text):
        raise EvidenceError("Voice sample contains control characters")
    return text


def run_sample(*, piper_exe: Path, model: Path, locale: str, text_file: Path,
               sample_id: str, out_dir: Path, license_name: str, rights_reviewed: bool,
               timeout_seconds: int = 180) -> dict:
    """Produce a private, never-auto-approved model run and duration metrics.

    The caller explicitly selects a locally installed executable/model, and
    acknowledges licence review. No model fetch or automatic path discovery.
    """
    if locale not in SUPPORTED_LOCALES:
        raise EvidenceError("Only hi-IN and en-US are supported in this pilot")
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,60}", sample_id):
        raise EvidenceError("sample_id must be a short safe slug")
    if rights_reviewed is not True:
        raise EvidenceError("Owner must first review the Piper voice model licence and permitted use")
    if not isinstance(license_name, str) or not 3 <= len(license_name.strip()) <= 128 or \
            license_name.strip().lower() in {"unknown", "none", "placeholder", "tbd"}:
        raise EvidenceError("Specify owner-reviewed model licence name, not a placeholder")
    if type(timeout_seconds) is not int or not 10 <= timeout_seconds <= 240:
        raise EvidenceError("Timeout must be 10..240 seconds")
    piper_exe = _valid_path(piper_exe, "Owner-installed Piper executable", 512 * 1024 * 1024)
    model = _valid_path(model, "Owner-installed Piper model", MAX_MODEL_BYTES)
    config_path, model_language = _check_model_config(model, locale)
    text = _read_private_script(text_file)
    destination = _outside_repo(out_dir, "Private sample directory")
    sample_dir = destination / sample_id
    if sample_dir.exists() or sample_dir.is_symlink():
        raise EvidenceError("Private sample ID already exists; samples are never overwritten")

    # Compute all input hashes before any side effects. No model config content
    # or private input text leaves the user-selected private output directory.
    model_sha = _hash_file(model)
    executable_sha = _hash_file(piper_exe)
    config_sha = _hash_file(config_path)
    text_sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    sample_dir.mkdir(parents=True, exist_ok=False)
    raw = sample_dir / "voice-raw.wav"
    normalized = sample_dir / "voice-16k.wav"
    manifest_path = sample_dir / "voice-evaluation-UNAPPROVED.json"
    report_path = sample_dir / "local-run-report.json"
    try:
        env = os.environ.copy()
        env.update({"HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1",
                    "HF_HUB_DISABLE_TELEMETRY": "1", "NO_COLOR": "1"})
        begin = time.perf_counter()
        try:
            result = subprocess.run(
                [str(piper_exe), "--model", str(model), "--output_file", str(raw)],
                input=(text + "\n").encode("utf-8"), stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, env=env, timeout=timeout_seconds, check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise EvidenceError("Local Piper generation timed out; no output approved") from exc
        synth_seconds = time.perf_counter() - begin
        if result.returncode != 0:
            raise EvidenceError("Local Piper process failed; inspect your local Piper installation")
        _valid_path(raw, "Generated Piper WAV", 80 * 1024 * 1024)
        if not shutil.which("ffmpeg"):
            raise EvidenceError("FFmpeg missing from PATH (required for 16 kHz normalization)")
        begin = time.perf_counter()
        try:
            ffmpeg = subprocess.run(
                ["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
                 "-i", str(raw), "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", str(normalized)],
                stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                timeout=90, check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise EvidenceError("FFmpeg audio normalization timed out") from exc
        normalize_seconds = time.perf_counter() - begin
        if ffmpeg.returncode != 0:
            raise EvidenceError("FFmpeg could not normalize Piper output to PCM16 16 kHz")
        stats = inspect_wave(normalized)
        template_info = create_template(normalized, locale, sample_id, manifest_path)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["model"]["voice_id"] = model.stem[:256]
        manifest["model"]["voice_weights_sha256"] = model_sha
        manifest["model"]["license_name"] = license_name.strip()
        # This only records the operator's licence review, not independent proof.
        manifest["model"]["license_reviewed_by"] = "LOCAL_OPERATOR_ATTESTED"
        manifest["model"]["owner_approved_license"] = True
        manifest["local_run_provenance"] = {
            "producer": "OWNER_SUPPLIED_LOCAL_PIPER",
            "input_text_sha256": text_sha,
            "piper_executable_sha256": executable_sha,
            "voice_config_sha256": config_sha,
            "model_locale_from_config": model_language,
            "synthesis_wall_seconds": round(synth_seconds, 3),
            "normalization_wall_seconds": round(normalize_seconds, 3),
            "owner_supplied_local_executable_invoked": True,
            "model_inference_independently_verified": False,
            "model_licence_independently_verified": False,
            "speech_language_acoustically_verified": False,
            "actual_peak_ram_measured": False,
        }
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        report = {
            "sample_id": sample_id, "locale": locale,
            "status": "BLOCKED_AUDIO_QC" if stats["blockers"] else "PENDING_HUMAN_REVIEW_AND_ALIGNMENT",
            "publish_ready": False, "owner_model_licence_attested_not_independently_verified": True,
            "input_text_sha256": text_sha, "voice_model_sha256": model_sha,
            "voice_config_sha256": config_sha, "piper_executable_sha256": executable_sha,
            "wav_sha256": _hash_file(normalized),
            "synthesis_wall_seconds": round(synth_seconds, 3),
            "normalization_wall_seconds": round(normalize_seconds, 3),
            "audio_technical_metrics": stats,
            "real_voice_naturalness_verified": False,
            "word_level_alignment_performed": False,
            "human_full_listen_performed": False,
            "youtube_upload_performed": False,
            "peak_ram_measured": False,
        }
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if os.name != "nt":
            for item in (raw, normalized, manifest_path, report_path):
                item.chmod(0o600)
        return {"status": report["status"], "private_sample_dir": str(sample_dir),
                "private_manifest": str(manifest_path), "private_report": str(report_path),
                "duration_ms": stats["duration_ms"], "publish_ready": False,
                "blockers": stats["blockers"]}
    except Exception:
        # Do not retain ambiguous partial outputs or unapproved authorizations.
        shutil.rmtree(sample_dir, ignore_errors=True)
        raise


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Opt-in OFFLINE owner-installed Piper voice sample; no downloads or publication")
    p.add_argument("--piper-exe", type=Path, required=True)
    p.add_argument("--model", type=Path, required=True)
    p.add_argument("--locale", choices=sorted(SUPPORTED_LOCALES), required=True)
    p.add_argument("--text-file", type=Path, required=True, help="Private UTF-8 text file OUTSIDE the Git repo")
    p.add_argument("--sample-id", required=True)
    p.add_argument("--out-dir", type=Path, default=Path.home() / "ViralOSPrivateVoiceSamples")
    p.add_argument("--license-name", required=True, help="Your reviewed model licence name")
    p.add_argument("--license-reviewed", action="store_true", help="Attest you reviewed allowed use of this model")
    p.add_argument("--timeout", type=int, default=180)
    a = p.parse_args(argv)
    try:
        result = run_sample(piper_exe=a.piper_exe, model=a.model, locale=a.locale,
                            text_file=a.text_file, sample_id=a.sample_id, out_dir=a.out_dir,
                            license_name=a.license_name, rights_reviewed=a.license_reviewed,
                            timeout_seconds=a.timeout)
        print(json.dumps(result, ensure_ascii=False))
        return 0 if not result["blockers"] else 2
    except (EvidenceError, OSError) as exc:
        print(json.dumps({"status": "NOT_EXECUTED_OR_INVALID", "reason": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())