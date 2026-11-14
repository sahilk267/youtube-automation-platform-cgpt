# ViralOS M2.5 — Opt-in local Piper execution, private sample and QA handoff

**Release scope:** This is a new, runnable **owner-invoked local process workflow** that executes an already installed Piper CLI and an already owned/licensed language-matched `.onnx` voice model. It does not install, download, select, authenticate, translate, align words, upload to YouTube or certify naturalness. `docs/M2_5_VOICE_ALIGNMENT_ACCEPTANCE.md` defines the separate next human+alignment evidence gate.

## Why this exists

Before this increment, ViralOS had an optional Piper adapter and a stand-alone WAV/alignment evaluator, but no repeatable operator command that (1) chooses **one specific** installed model and language, (2) records the voice/executable/config/text SHA-256s, (3) measures actual local synthesis wall-clock time, (4) converts raw audio to an evaluator-compatible 16-kHz PCM16 mono WAV, and (5) produces an explicitly **unapproved** private evaluation manifest. The pipeline now connects those stages without providing any unknown model or fabricated acceptance score.

## Prerequisites and trust boundary

- First clone/pull current GitHub `main`; install Python 3.12 and FFmpeg from sources you trust, test `ffmpeg -version` and `python -V`.
- Install your own **trusted Piper executable** and a corresponding voice model `*.onnx` and `*.onnx.json` sidecar **outside the public repository**. Both voice/model rights and voice-cloning consent remain the owner's responsibility. Check commercial/YouTube permissions in the model licence yourself. The model sidecar must contain `language.code` matching `hi_IN` or `en_US`.
- Read the model's explicit licence and allowed use before providing `-LicenseReviewed`; the code records an **owner assertion**, not independent licence verification.
- Put your input narration text in an **UTF-8 private text file outside the repository**, 12–1400 characters; do not put research material, token credentials, personal voices, model weights or locally generated clips in public Git.
- This tool never intentionally makes HTTP requests or downloads models. **It cannot sandbox or independently audit an arbitrary executable supplied by the operator.** Run only trusted Piper distributions. Disconnect from networks / use your OS firewall if an offline guarantee is needed.

## Windows example

From the cloned repository folder after creating `.venv` and installing requirements:

```powershell
# PRIVATE input: create this file manually outside the Git repository.
# The Hindi model is only an example path; no model is bundled or downloaded.
powershell -ExecutionPolicy Bypass -File .\tools\run_voice_local_windows.ps1 `
  -PiperExe 'C:\LocalApps\Piper\piper.exe' `
  -Model 'C:\VoiceModels\hi_IN\owner-reviewed.onnx' `
  -TextFile "$HOME\ViralOSPrivateVoiceSamples\script-hi.txt" `
  -Locale hi-IN `
  -SampleId cricket-hi-001 `
  -LicenseName 'YOUR-ACTUAL-REVIEWED-MODEL-LICENSE' `
  -LicenseReviewed
```

For English use the appropriate reviewed **en_US** model, `-Locale en-US` and a unique sample ID. Licence names must be real; placeholders are not approval. If your environment uses `python` instead of the PowerShell wrapper, see `python -m tools.run_local_piper --help` (same validation and output).

The wrapper deliberately **fails** if the owner omits the `-LicenseReviewed` switch. A model/config/locale mismatch, invalid/private paths, missing FFmpeg, failed CLI, timeout or repeated sample ID also fails without silently accepting an old result.

## Private output structure

Each new sample is written under `$HOME\ViralOSPrivateVoiceSamples\<sample-id>`:

| Output | Meaning |
|---|---|
| `voice-raw.wav` | Direct Piper CLI output, unreviewed |
| `voice-16k.wav` | FFmpeg 16-kHz mono PCM16 version for metrics and optional aligner |
| `voice-evaluation-UNAPPROVED.json` | SHA-bound *unfinished* M2.5 evaluation manifest (reference/candidate words and listener ratings empty) |
| `local-run-report.json` | Technical measurements, digests, measured wall-clock synthesis/normalization durations, explicit missing-review flags |

On Unix private files are mode `0600`; Windows file privacy depends on your user-folder NTFS ACLs. Paths to private WAV/model/text, and plaintext script, must not be uploaded to GitHub. The report uses digests but is also kept private. If a run crashes or normalization fails, the newly created sample directory is removed rather than leaving an ambiguous partial artifact; sample IDs are never overwritten.

**No fake proofs:** `owner_supplied_local_executable_invoked=true` means only that a selected local command returned successfully. It is not independent proof of neural inference, voice naturalness, copyright compliance or model identity. A synthetic CLI shim can satisfy technical tests; **no actual local trained-model execution is verified by GitHub CI.** RAM, GPU and owner-machine thermal benchmarks are not measured here and are clearly false/absent in the report.

## Actual acceptance after generation

1. Confirm original audio is intelligible and suited to the locale, pronounce Cricket/NFL names and code-switched Hindi/English naturally; listen to **all** of the WAV and keep your subjective quality scores private.
2. Run a real, locally installed language-compatible forced aligner (such as the existing opt-in WhisperX adapter) against an **accurate reviewed script**, with network/download disabled. Check transcription equivalence and spoken timestamps. Generated WAV duration is **not** word alignment.
3. Complete `voice-evaluation-UNAPPROVED.json`: replace the real project `source_script_sha256`, add actual aligner SHA/model info, human timed reference words and model candidate words, `candidate_source=LOCAL_MODEL_OUTPUT` **only when truthful**, owner listener/rights/pronunciation checks and full-audio listener score.
4. Run `python -m tools.audio_acceptance "<PRIVATE-PATH-TO-MANIFEST>"` to calculate word-boundary MAE/p95 and audio blockers. Passing means only owner-supplied evidence fits deterministic thresholds, **not** a professional publishing approval.
5. Store all WAVs, reports and model files separately from Git. Record a **sanitized** summary in GitHub Issue #2 only after actual owner-PC run. Then create and personally review 30–60-second original Cricket Hindi and NFL English videos before considering real publishing.

## Verification boundary

Unit/negative tests in `tests/test_run_local_piper.py` use **fake executable and model-file fixtures** and one real FFmpeg conversion of a synthetic tone (on Linux). They verify command arguments, private file boundaries, offline flags, locale metadata, SHA provenance, audio normalization, silent-audio blocking and fail-closed cases. **No trained Piper voice, real Hindi pronunciation, WhisperX model, real owner PC or YouTube channel has been validated in CI.**

**Tracking:** [Issue #2](https://github.com/sahilk267/youtube-automation-platform-cgpt/issues/2), `docs/IMPLEMENTATION_STATUS.md`, `docs/ROADMAP.md`, `docs/CURRENT_CHECKPOINT.md`.

## Next integration: local word-alignment proposal

Once the owner has a real **Piper output WAV and original text** in a private sample folder, use [the M2.5 local CPU WhisperX alignment runner](M2_5_LOCAL_ALIGNMENT_RUNNER.md) to obtain *unreviewed* model candidate boundaries. An optional installed aligner is required; no model downloads occur. The original voice manifest is untouched. The runner creates a separate manifest that still needs human reference timings and full audio review before `tools.audio_acceptance` can evaluate evidence.
