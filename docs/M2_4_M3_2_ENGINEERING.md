# ViralOS Launch v0.7 — M2.4 Multilingual Director & M3.2 Acceptance

**Status: tested development checkpoint, NOT a professional 12-domain release.**

## Scope/architecture

Preserves all M0–M2.3/M3.1 modules, canonical SQLite migrations 001–010, and exact file-bound/source-bound approval rules. Adds immutable migrations `011` (localized video variants) and `012` (pre-upload acceptance observations). Each locale variant is version-bound to the source script; the existing shared FFmpeg Studio remains the only video compositor. Hindi and English are **different owner-reviewed content variants**, not an automatic LLM translation, and neither can be automatically uploaded from the new API.

### M2.4 contract

1. Create source channel/project/script as usual. For a locale variant, call `POST /api/projects/{project_id}/m24/variants` with `locale: hi-IN|en-US`, `reviewed_script`, human reviewer, regional notes, and both true review checkboxes.
2. Get `GET /api/projects/{project_id}/m24/variants/{variant_id}` to inspect exact segment strings. No new facts are inserted by the draft generator.
3. Upload one WAV per segment using `POST .../voice/{index}` (multipart `file`), or explicitly opt into a locally installed **license-attested** Piper voice with the correct locale. Optional owner-reviewed pronunciation hints are entered via `POST .../pronunciation` and modify *only the TTS input*, not subtitle text. **No proprietary model, synthetic voice clone or model is downloaded automatically.**
4. `POST .../render` combines measured PCM16 durations, localizes titles/labels, renders an ORIGINAL illustrative diagram, exports an MP4 and exact segment-timed SRT. A diagnostic checks peak, RMS and clipping. This is a technical preview and does not grant final-video approval.
5. Review every spoken word and graphic in the target language. The source script, voice segments, locale text and generated output are hash checked. Source script revisions invalidate old previews.

**Known limitations:** automated Hindi↔English translation does not exist. SRT is measured at segment boundaries, not individual words; eSpeak samples are robotic fixtures. Piper integration was mock-tested previously but not run with a real licensed Hindi or English model in this delivery. Localized fonts must be installed; Hindi/Latin fallback was visually inspected in the included demo. The field diagrams are fictional, not actual tracked match footage. No final publication approval route exists for M24 previews.

### Optional genuine CTC forced alignment (model not bundled)

`POST /api/projects/{project_id}/m24/plans/{plan_id}/forced-proposal` is **a local WhisperX CTC forced-alignment adapter** for an existing current M2.1 Studio plan, not for the independent M24 preview. Supply all of these yourself:

- A locally installed compatible WhisperX environment and model directory.
- `VIRALOS_WHISPERX_ALIGN_MODEL_DIR` pointing to existing model files, `VIRALOS_WHISPERX_MODEL_RIGHTS_OK=1`, `VIRALOS_OFFLINE_FORCED_ALIGN_OPT_IN=1`.
- An exact transcript and synchronized measured voice in the original Studio plan.

The module sets HF/Transformers OFFLINE flags; it never intentionally downloads a model. It calls a real CTC aligner *only if installed*. It returns **an unapproved word-timing proposal**, validates every token/shot interval, then requires a separate owner's review through `POST /api/projects/{project_id}/m23/alignment-drafts/{draft_id}/approve`. Approved timing can be exported via the existing word-level VTT endpoint. **Actual WhisperX model inference, Hindi phonetic accuracy, GPU and on-device Windows compatibility have NOT been tested.** Mock tests check route wiring and approval logic only. A library may fail on a language/model mismatch; do not bypass that error by assigning estimated timings.

### M3.2 acceptance/recovery

This is **not a new live upload system**; the previously implemented opt-in PRIVATE-only M3 uploader is retained. The new `POST /api/m32/acceptance/preflight` checks final M2.2 export fingerprint, the owner-attested local media/rights, exact upload-channel binding, Analytics/monetary account mismatch, and existing `REMOTE_UNKNOWN` uploads. With no registered upload OAuth it returns `BLOCKED`.

Remote read-only preflight is default **OFF**; it requires `VIRALOS_ENABLE_M32_REMOTE_READ=1`, `perform_remote_read_only_check=true` and `owner_consented_network_access=true`. It may then fetch the authenticated owner channel and, for a previously uploaded private video, exact video ownership and current private status. This does **not** upload, publish, schedule or automatically retry. `REMOTE_CHANNEL_VERIFIED` means owner channel verification, *not* that a video was uploaded. Remote video verification is a separately returned boolean.

**Owned-channel acceptance procedure (needs you, not performed here)**:

1. Create a Google Cloud OAuth Desktop client for the required YouTube APIs; complete Google consent setup and comply with YouTube Developer Policies. Do not paste tokens or credential JSON into chat or upload them to a public repository.
2. Connect the exact selected YouTube channel using `tools/connect_youtube_private_upload.py` (stores OAuth tokens only in supported OS keyring). Repeat with read-only Analytics scopes if needed. Monetary reports require the separate monetary OAuth scope and normally a monetized/YPP channel; a `403` can be a legitimate not-eligible result.
3. Render a **real, fully sourced, rights-reviewed** video, watch all frames, review subtitles/claims/voice and generate M2.2 owner-approved final export. M24 previews are not acceptable final exports.
4. Run **offline M3.2 preflight**. Resolve every mismatch/unknown state. If desired, explicitly enable read-only online preflight and confirm the actual remote channel ID.
5. Only after passing these gates, explicitly opt into M3 private upload using `VIRALOS_ENABLE_PRIVATE_UPLOAD=1`, confirm exact per-video metadata and the `UPLOAD_PRIVATE_NOW` user confirmation. Verify the uploaded item is PRIVATE in YouTube Studio and independently read back the privacy status using the owner's authorized OAuth session. **There is no automatic public upload here.**
6. If upload times out, leave `REMOTE_UNKNOWN`; check YouTube Studio and use the existing M3.1 reconciliation route. Never blindly retry because the remote item might already exist. Do not mistake delete/rollback for a harmless or automatic operation.
7. For actual analytics use the owner OAuth read-only report and a processed date range. YouTube reports have a documented **48–72 hour processing delay** and may truncate incomplete dates. Monetary reports are estimates and do not equal deposited income, profit or RPM guarantees.
8. Validate Windows 10/11, Python 3.12, FFmpeg, optional local voice model, 32GB RAM and i7 8th Gen CPU on the **actual owner's machine**. Record job time, voice/listening QC, rendering speed, API errors and human review notes. Those results are not present in this package.

**YouTube policy note verified 12 November 2026:** YouTube's 3 Nov 2026 revision-history entry describes a 2 Nov 2026 reversal of a legacy restriction for unverified API projects; despite that, **omitting `status.privacyStatus` defaults to PUBLIC**. ViralOS explicitly sends `private`, without relying on old default account/project behaviors. Current API docs, not past blog posts, take priority.

### Security and delivery limitations

Bound to `127.0.0.1` by the Windows startup script. There is not a production authentication/authorization layer suitable for public internet exposure. No new API credentials or tokens are included. This package does not deliver royalty-cleared sports footage, automated independent verification, natural voice quality guarantees, true auto dubbing, full 12 specialized directors, all-category cinematic generation, or verified monetization. The human approval flags are attestations; software cannot certify copyright legality.

## Verification

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\start_windows.ps1
```

Direct tests from project root: `python -m pytest -q`, `python tools/verify_package.py`, `node --check app/static/app.js` if Node exists. Extra voice/model packages are optional; do not auto-install heavy model dependencies on CPU. Demo can be regenerated in Linux from `PYTHONPATH=. python examples/create_m24_demo.py` with eSpeak (the samples supplied in `examples/` are generated technical fixtures).
