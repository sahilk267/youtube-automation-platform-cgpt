"""Create a non-approved private M2.5 manifest skeleton from an owner's WAV.

Never infers timings, downloads model weights, assumes rights or passes QA.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import sys
from tools.audio_acceptance import (_hash_file, _inside_repo, inspect_wave,
                                    EvidenceError, SUPPORTED_LOCALES)


def create_template(wav: Path, locale: str, sample_id: str, output: Path) -> dict:
    wav = wav.expanduser().resolve()
    output = output.expanduser().resolve()
    if locale not in SUPPORTED_LOCALES:
        raise EvidenceError("Expected hi-IN or en-US")
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,60}", sample_id):
        raise EvidenceError("sample_id must be safe, short slug")
    if _inside_repo(output):
        raise EvidenceError("Private manifest cannot be written inside the Git repository")
    diag = inspect_wave(wav)
    template = {
        "schema_version": 1, "sample_id": sample_id, "locale": locale,
        "audio_path": str(wav), "audio_sha256": _hash_file(wav),
        "source_script_sha256": "REPLACE_WITH_REAL_APP_SCRIPT_SHA256",
        "model": {
            "voice_id": "REPLACE_VOICE_ID", "voice_weights_sha256": "REPLACE_WITH_ACTUAL_SHA256",
            "aligner_name": "REPLACE_ALIGNER_ID", "aligner_weights_sha256": "REPLACE_WITH_ACTUAL_SHA256",
            "license_name": "REPLACE_WITH_REVIEWED_MODEL_LICENSE", "license_reviewed_by": "",
            "owner_approved_license": False,
        },
        "alignment": {"candidate_source": "UNVERIFIED", "reference_words": [], "candidate_words": []},
        "review": {"owned_or_licensed_audio": False, "reference_timings_human_checked": False,
                   "full_audio_listened": False, "listener": "", "naturalness_1_to_5": None,
                   "pronunciation_checks": []},
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as file:
        json.dump(template, file, ensure_ascii=False, indent=2)
        file.write("\n")
    if sys.platform != "win32":
        output.chmod(0o600)
    return {"output_path": str(output), "duration_ms": diag["duration_ms"],
            "audio_blockers": diag["blockers"], "approved": False}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Private owner WAV manifest skeleton; never auto-approves")
    p.add_argument("wav", type=Path)
    p.add_argument("--locale", choices=sorted(SUPPORTED_LOCALES), required=True)
    p.add_argument("--sample-id", required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args(argv)
    try:
        print(json.dumps(create_template(a.wav, a.locale, a.sample_id, a.out), ensure_ascii=False))
        return 0
    except (EvidenceError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())