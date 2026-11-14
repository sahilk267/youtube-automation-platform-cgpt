# M2.5: Supervised local WhisperX CPU alignment proposal (partial gate)

**Status:** An executable **owner-opted-in local alignment runner** has been implemented for pre-existing private Piper sample output. It can invoke the optional local WhisperX-compatible CPU aligner against the exact spoken script, then save **unreviewed word timestamp proposals**. It has **not** run a real licensed Hindi or English aligner model in GitHub CI or on the owner's PC. It does **not** compute ground-truth accuracy, make professional audio claims or authorize publication. [Issue #2](https://github.com/sahilk267/youtube-automation-platform-cgpt/issues/2) stays open.

## What this connects

Previously, the repo had an optional `app/alignment_m24.py` adapter and the SHA-bound [M2.5 evaluator](M2_5_VOICE_ALIGNMENT_ACCEPTANCE.md), but no safe reproducible operator workflow that connects a **specific Piper-produced WAV** to an **installed local CPU aligner** and an **untouched, unapproved** evaluation manifest. The new `tools/run_local_alignment.py` plus `tools/run_alignment_windows.ps1` fills that integration gap.

The word alignment flow is not transcription or translation: the exact owner-authored spoken script is supplied and must hash-match the original Piper run. The CPU aligner estimates the **start/end of each already-known word**. An emitted timestamp is only a *proposal*, even if the aligner returns successfully. The model may fail for Hindi numerals, loanwords, rare names, punctuation or code-switching, and the tool blocks if word count, exact Unicode-normalized lexical identity or chronological timing don't match. It **never interpolates or invents missing model timestamps**.

## Trusted prerequisites (all owner-owned; outside PUBLIC Git)

1. Clone/pull current `main`, set up Python 3.12 `.venv`, FFmpeg and a **trusted source** for the optional WhisperX library and its dependencies. Do not install arbitrary models or change requirements without confirming licence, offline suitability and CPU memory budget. This tool does **not** install dependencies or download any models. Existing `app/alignment_m24.py` uses a local WhisperX alignment adapter; model/library version compatibility needs real owner testing.
2. An existing *private* sample from [M2.5 local Piper runner](M2_5_LOCAL_PIPER_RUNNER.md), e.g. `$HOME\ViralOSPrivateVoiceSamples\cricket-hi-001`, containing `voice-16k.wav` plus `voice-evaluation-UNAPPROVED.json`. No WAV/transcript/model is accepted from the public repository.
3. The **same exact-spoken** UTF-8 script private text file that generated the Piper WAV. The input SHA-256 is compared with `local_run_provenance.input_text_sha256`; changing punctuation or text requires regenerating a new Piper sample.
4. An owner-installed **local WhisperX-compatible model directory** outside the repo, with `config.json` and associated model, tokenizer/processor files. Review the actual model rights and allowed commercial use. If language metadata exists in `config.json`, it must match `hi` or `en` respectively. Merely setting the language label is NOT proof that a model understands that language.
5. For optional sampled peak process memory, install `psutil` in your own environment from a trusted source. If absent, `peak_worker_tree_rss_mb` is **null/UNMEASURED**; no guessed figures. Sampling is approximate and not a hardware maximum. Piper synthesis memory is not measured by this command.

**Offline boundary:** `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, `HF_DATASETS_OFFLINE=1` and `HF_HUB_DISABLE_TELEMETRY=1` are set before loading the model in a separate worker. The wrapper intentionally makes no network API calls. A third-party WhisperX/torch package cannot be independently sandboxed by these environment flags, so verify its installed code/licence and use an OS firewall or disconnected machine when strict no-network execution is required. Never run unknown binaries/models.

## Windows commands

Use the original Piper sample created with your own reviewed model and voice. Then from the clone folder:

```powershell
# These paths are EXAMPLES. All private inputs belong outside the Git clone.
powershell -ExecutionPolicy Bypass -File .\tools\run_alignment_windows.ps1 `
  -SampleDir "$HOME\ViralOSPrivateVoiceSamples\cricket-hi-001" `
  -ScriptFile "$HOME\ViralOSPrivateVoiceSamples\script-hi.txt" `
  -ModelDir 'C:\VoiceModels\hi-aligner\reviewed-local-model' `
  -Locale hi-IN `
  -LicenseName 'ACTUAL-REVIEWED-ALIGNER-LICENSE' `
  -LicenseReviewed `
  -TimeoutSeconds 600
```

For English use matching `en-US` Piper sample and reviewed English CTC aligner directory. You can inspect the CLI without models using `python -m tools.run_local_alignment --help`.

The script **never automatically publishes**. A missing local model/WhisperX dependency, unsigned licence review, script/audio mismatch, wrong language, timeout, missing/unrecognized words, bad timestamps or repeated output filenames **fails closed**. The subprocess is killed on timeout (process group on Linux, best-effort tree kill on Windows). Stderr/stdout from third-party code are not leaked to logs. A model or script hash changing mid-run invalidates the proposal.

## Private outputs and their trust level

All new outputs are created next to the existing sample WAV, with **no overwrites**:

| Private file | Content | Status |
|---|---|---|
| `alignment-proposal-UNREVIEWED.json` | Candidate words and timestamps, SHA-bound audio/script/model lineage | **UNREVIEWED**; contains private words |
| `voice-evaluation-WITH-PROPOSAL-UNAPPROVED.json` | New copy of the M2.5 manifest with candidate word proposals but *no fabricated human reference timings* | **UNAPPROVED** |
| `alignment-run-TECHNICAL.json` | Locale, sample/model/script digests, measured alignment time, optionally sampled peak worker RSS, counts, explicit missing-review status | Non-sensitive summary, stored privately |

The original `voice-evaluation-UNAPPROVED.json`, generated WAV and model files are unchanged on both success and failure. Partial files from failed attempts are removed. Output **cannot be created under the public Git repository**. The worker uses the optional existing `app/alignment_m24.align_transcript()` in CPU mode with a local model path; our tests replace it with synthetic responses and do not establish model quality or real inference.

## Real acceptance still required

1. Owner physically listens to **every second** of both Hindi and English voice samples and records genuine pronunciation/naturalness and licence review.
2. A human prepares independent **ground-truth word reference timings**. Do not copy model candidate timings and call them human ground truth.
3. Fill the new private `voice-evaluation-WITH-PROPOSAL-UNAPPROVED.json`: supply real `source_script_sha256` from the active ViralOS project, exact reviewer timings under `alignment.reference_words`, recorded reviewer/rights/pronunciation details under `review`. Verify the `candidate_source=LOCAL_MODEL_OUTPUT` is true, then run `python -m tools.audio_acceptance '<private-copy-path>'` to calculate human-versus-model boundary MAE/p95. This evaluator checks owner statements; independent human/model provenance cannot be inferred from synthetic tests.
4. Record actual model/library versions, licenses, CPU inference latency, sampled RSS with `psutil` if installed, and compare against owner i7 8th Gen/32GB CPU budget. Investigate Hindi numbers, Cricket/NFL names, code-switching and zero-duration/unrecognized words rather than silently changing scripts to make tests pass.
5. Review real **30–60-second** Cricket Hindi and NFL English videos including subtitles/visuals/sound and rights. No real YouTube publishing without additional owner approval and live OAuth acceptance.

## How we verify code without pretending to run a model

`tests/test_run_local_alignment.py` runs synthetic word proposals, a synthetic tone WAV and a fake model-directory fingerprint. It tests full proposal/manifest/report creation, SHA binding, exact Hindi token rejection, invalid/overlapping word timing, wrong locale, model tampering, missing licence, duplicate/timeout cleanup, private-only boundaries and the adapter invocation contract with offline flags. Actual WhisperX model weights are **never** in CI. Windows tests must remain explicit UTF-8. Full GitHub Linux + Windows test counts and merge commit will be appended to `docs/CURRENT_CHECKPOINT.md` after PR checks pass.