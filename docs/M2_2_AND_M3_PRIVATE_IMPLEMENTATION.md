# ViralOS M2.2 / M3 — Implementation and Safety Contract (2026-11-12)

**Status:** Working local CPU code verified with automated tests; **not** proof of production quality, real YouTube upload, YouTube monetization or Windows GPU behavior.

## What was built

### M2.2 Creative Intelligence v0.5
- `app/creative_m22.py` provides **16 distinct domain/subdomain creative policy dossiers** covering 12 canonical OS and five sport subdomains. Only Cricket/NFL are active in this Launch implementation; the rest are specifications, **not working specialist agents**.
- Automated QA inspection of the current MP4 preview is bound to script revision, source/claim review status, approved asset hashes, narration hash, plan hash and project revision. Checks are objective (missing captions/voice, unsupported linked claim, wrong asset, headline length, visual repetition); not an invented creativity/virality score.
- Original **CPU illustrative moving route** overlay for Cricket and NFL, added to typed `Visual.motion`. It is original animation, **not actual player-tracking or broadcast footage**.
- Owner-reviewed word timestamps import with exact transcript-token match and per-caption time limits. Export VTT at `GET /api/projects/{id}/m22/plans/{plan_id}/words.vtt`. This is **NOT automatic forced alignment**. Measured segment-level audio continues to work.
- Four explicit human checks (complete watch, image/music/rights, claims/source review, narration/captions); approval fingerprints every consequential input. No boolean from the user is presented as external legal verification.
- A **new original final MP4 export**, without the preview watermark, after owner review. Final export is re-rendered from the same immutable plan and clips, with technical checks and hash validation. Any script/source/voice/rights changes invalidate approval and block downloads/upload.

### M3 Approved private upload v0.5
- `app/youtube_private.py` adds **opt-in PRIVATE-only** YouTube upload workflow. Does not replace existing public upload lock at `/api/youtube/upload`; there is **no route to publish PUBLIC or UNLISTED**.
- OAuth authorization: `tools/connect_youtube_private_upload.py` requires a local YouTube channel ID and an exact remote YouTube channel ID; uses an **OS keyring** for tokens and never stores OAuth secrets in SQLite or ZIP.
- Prepare intent with original title, description, tags, user-reviewed synthetic/altered content and made-for-kids flags. Server keeps one intent per final export and refuses different metadata on the same intent.
- Execution requires BOTH `VIRALOS_ENABLE_PRIVATE_UPLOAD=1` in the local server environment and the user's **`UPLOAD_PRIVATE_NOW`** action. The API explicitly passes `status.privacyStatus=private` and verifies the response.
- If a request fails after the upload might have started, server stores `REMOTE_UNKNOWN`, blocks duplicate retry and instructs owner to check YouTube Studio. If the app exits during upload, startup moves an in-flight intent to `REMOTE_UNKNOWN`.
- Existing optional read-only YouTube Analytics integration remains available at `/api/youtube/analytics/sync`, with credentials from the independent read-only connection; owner-entered analytics are labeled as such. **No financial numbers are fabricated.**

## Operator sequence

1. Use existing M1 workflow to create channel and project, source and script. Review all factual claims. M2.1 draft creates a current Studio plan with measured owner WAV or optional licensed Piper narration; **not automatic translation**.
2. Queue and run Studio preview. Open the MP4 and actually watch the complete video. Run `GET /api/projects/{project_id}/m22/creative-audit/{studio_render_id}`.
3. Resolve blocking issues. Use `POST /api/projects/{project_id}/m22/studio/renders/{studio_render_id}/review-final` with required owner review attestations; **approval is not automated**.
4. Generate `POST /api/projects/{project_id}/m22/reviews/{review_id}/export-final`. Download via `/api/m22/final-exports/{export_id}/download`. Source/asset hashes must still match. This is **owner reviewed**, not third-party certified.
5. **Optional:** To enable a real PRIVATE upload, install optional dependencies with `python -m pip install google-api-python-client google-auth-oauthlib google-auth-httplib2 keyring`. Create a Google OAuth Desktop app, enable YouTube Data API, and use:

   ```powershell
   python tools/connect_youtube_private_upload.py --local-channel-id "LOCAL_ID" --expected-youtube-channel-id "UC..." --client-secrets "C:\path\client_secret.json"
   ```

   Never commit OAuth client files or keyring contents to a repository. The user must approve scopes in the actual Google authorization browser window.
6. Start server with private opt-in only when deliberately needed:

   ```powershell
   $env:VIRALOS_ENABLE_PRIVATE_UPLOAD = "1"
   powershell -ExecutionPolicy Bypass -File .\tools\start_windows.ps1
   ```

   In dashboard M3 form: create private intent; then separately confirm upload. Never re-upload while state is `REMOTE_UNKNOWN` without manual remote reconciliation. Video becomes **PRIVATE** on YouTube, not public.

## Release gates still unresolved

- Full autonomous 12-domain research/creative experts (only sports prototype enabled); in-depth factual and rights adjudication is still human-reviewed, **not autonomous**.
- Real multilingual AI translation/dubbing, genuinely professional local voice models, verified word-level forced alignment, lip sync, and generative GPU video not implemented. Local Piper requires owner-supplied licensed voice and was mocked in tests.
- Automated objective QC does not prove retention, storytelling excellence, monetization eligibility, copyright clearance or full-video human attention. Own original narration/imagery and quality assessment remain necessary.
- **Live YouTube OAuth/private video upload and channel Analytics fetching have not been tested against an owned account in this environment.** Mock tests verify exact backend control flow, state transitions and private metadata, not the network outcome. Account authorization, API quota and policy checks are required on the owner's machine.
- Windows i7-8th-gen/32GB performance unverified, including fonts and codecs; Linux CPU rendering tests only.
- SaaS, GPU scheduling, automatic public posting and high-stakes investigative auto-approval remain outside this stage.

## Verified tests
- Existing M0–M3/M2/M2.1 regression tests plus new M2.2/M3 tests (including real FFmpeg final export, owner-reviewed word-timing VTT, animated route frame difference, post-review script invalidation, fake OAuth success, remote failure/no retry, stale upload after restart).
- `python -m pytest -q` and `python tools/verify_package.py` after extracting final ZIP.

## Official API references (verify again at deployment)
- https://developers.google.com/youtube/data/reference/rest/v3/videos/insert
- https://developers.google.com/youtube/data/guides/uploading_a_video
- https://developers.google.com/youtube/analytics/reference
- https://support.google.com/youtube/answer/1311392
- https://support.google.com/youtube/answer/14328491

## Anti-conflict note
- `sql/001`–`006` are **unmodified**; new additive `007_m22_creative.sql` and `008_m3_publishing.sql` are the only new migrations.
- `app/studio_render.py` reuses the existing CPU compositor, with optional `release` parameter and original tactical motion. No duplicate FFmpeg service.
- Research-source verification and copyright approval are never inferred from generic metadata or a human checkbox.
- Launch still supports only Cricket/NFL project creation; 12 domain creative policies are expansion guidance, not 12 running models.
