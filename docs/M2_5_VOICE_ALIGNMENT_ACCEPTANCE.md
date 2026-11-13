# M2.5 — Offline voice and word-level alignment acceptance (partial implementation)

**Scope:** This is a privacy-aware **evidence evaluator**, not a pretrained model, synthesizer, verifier of model licences, automatic translation engine, or publication gate. Issue [#2](https://github.com/sahilk267/youtube-automation-platform-cgpt/issues/2) stays **OPEN** until actual hi-IN/en-US model inference, model licences, voice quality, genuine 30–60-second videos, and owner Windows performance are demonstrated. All code runs offline using Python's standard library.

## Current proof

- `tools/create_voice_manifest.py` creates a **NOT APPROVED** manifest from an existing owner WAV with SHA-256; it never fabricates timestamps, a model name, licence or human listening scores.
- `tools/audio_acceptance.py` checks 16-kHz mono PCM16 voice, exact audio/source hashes, model/aligner fingerprint fields, owner-attested rights, reviewer reference timing, candidate-word lexical identity (including Hindi–English code-switch), numeric word-boundary errors, pronunciation review and audio clipping/silence. It does **not** execute TTS or forced alignment.
- Reports contain metrics, digests, blockers and owner claims; **word text and private file paths are deliberately omitted**. The output is private and cannot go inside this public Git repository. Model provenance, naturalness and rights are still **owner-attested, not independently verified**.
- No new backend/publication endpoints or bypasses are enabled. Pre-existing Piper/WhisperX adapters remain separately opt-in and **not live-model verified**.

## Local Windows operator procedure

1. Clone/update `main`, install Python 3.12 requirements, and test on the actual i7 8th Gen / 32 GB Windows PC (no GPU needed for the evaluator itself). Use existing `tools/start_windows.ps1` setup instructions but keep sensitive assets **outside the repo**.
2. Obtain a **legally usable offline** Hindi or English TTS voice/model, confirm licence and usage rights, record model file SHA-256, locale and voice identity. Do not copy a real person's voice without authorization and do not silently download any model.
3. Record/render a **genuine** local 30–60-second sample using that installed model, and preserve its engine version/inference log, measured elapsed inference time, CPU/RAM and sample text. Normalize **a copy** for evaluation using licensed FFmpeg:

   ```powershell
   ffmpeg -i "$HOME\recordings\raw-hi.wav" -ar 16000 -ac 1 -sample_fmt s16 "$HOME\recordings\review-hi-16k.wav"
   ```

4. Create a private manifest template (replace path and sample ID with your actual local paths):

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\tools\voice_accept_windows.ps1 -Wav "$HOME\recordings\review-hi-16k.wav" -Locale hi-IN -SampleId cricket-hi-pilot
   ```

5. In the newly created private JSON, fill **only real values**: actual `source_script_sha256` from ViralOS project, both model SHA-256 digests, reviewed model licence/name, owner approval, `alignment.reference_words` from human-confirmed sample with exact Devanagari/Latin word text and millisecond boundaries, and `alignment.candidate_words` from a **real offline aligner** run. Record `candidate_source` as `LOCAL_MODEL_OUTPUT` **only if it is true**. Example word record: `{"text":"क्रिकेट","start_ms":125,"end_ms":450}`. Word data stays private. Provide `review` with actual listener, listening confirmation, pronunciation checks (names/code-switch) and real subjective 1–5 naturalness rating. A template with placeholders must fail.
6. Evaluate:

   ```powershell
   & .\.venv\Scripts\python.exe tools/audio_acceptance.py "$HOME\ViralOSPrivateReports\YOUR-MANIFEST.json"
   ```

   Exit codes: **0** = supplied evidence passes deterministic thresholds (still not independent professional approval); **2** = blockers; **3** = invalid/corrupted evidence. A new report is written to `$HOME\ViralOSPrivateReports\m25-<random>.json` by default; no overwrites.
7. Listen to the **entire video**, inspect the caption positions and graphics in Hindi/English, check source/rights, and record real CPU/RAM. No automated upload is authorized by this tool.

## Alignment scoring / negative gates

Word tokens use Unicode NFKC+casefold and strip only **surrounding punctuation**, **not transliteration**. Hindi `क्रिकेट` and Latin `cricket` are *not* considered identical. Both word lists must match in count and exact lexical identity, include valid ordered start/end integer milliseconds inside audio bounds, and not substantially overlap. Boundaries are checked against human-reviewed ground truth: **mean absolute start/end boundary error ≤120 ms** and **95th percentile boundary error ≤250 ms**. These are *initial engineering thresholds*, not a validated measure of perceived caption quality; review adequacy after a true sample corpus. Errors are not reported when transcripts differ.

Audio gates: mono PCM16/16-kHz, maximum 120 seconds/40 MB, RMS ≥0.007, clipping ratio ≤0.015. Human owner attestation required for audio/licensing, model hashes, entire-sample listening, reference timing, ≥1 pronunciation check, and recorded naturalness score ≥4/5. **Passing a fabricated or mistaken owner claim is possible**: this evaluator cannot verify what happened on another machine. Its output is never a public/production-ready authorization.

**Reference protocol:** record at least 2 real, separate localized samples, names/numbers/code-switch/pauses, maintain independent human labels, measure errors across the full set (not one toy fixture), run optional real model inference with downloads disabled, compare against deterministic tests, review actual speech acoustically. Use owner's private storage; Git contains only synthetic fixtures and code.

## Security / future integration

The report must be on a **private owner folder**; it cannot include raw research, WAVs, OAuth credentials, licensed weights or private source text. GitHub Actions tests exercise **synthetic sine-wave fixtures only**, with hard-coded fictitious model IDs used *solely to verify the scoring algorithm*. Do not count them as live Piper, WhisperX, third-party licensing, Google integration or natural human voice evidence.

To fully close Issue #2, still implement/validate real licensed voice model acquisition and dependency management (owner opt-in), run actual hi-IN/en-US TTS/aligner, measure owner hardware latency and RAM, full naturalness and code-switch pronunciation, real 30–60-second localized exports, and expert watch-through. Document model/version/licences in a **sanitized** public acceptance summary, while leaving private media/logs outside Git.