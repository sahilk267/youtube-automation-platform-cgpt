# Security, creator rights and publishing safety

**Repository was PUBLIC at initialization.** Treat every commit and PR as publicly accessible until owner changes visibility. No API secrets, YouTube OAuth refresh/access tokens, session cookies, channel financial exports, private source interview transcripts, licensed voice models, raw copyrighted media, local databases, owner addresses or passwords in Git.

## Development controls

- Bind server to localhost by default; no remote access exposure or production authentication claims until designed and tested.
- Use OS keyring/local environment variables for credentials; never write secrets to logs. Avoid unsafe arbitrary file paths, untrusted feed text execution, shell command interpolation and auto-model downloads.
- `.gitignore` covers `.env*`, venv, caches, DB/data, build media, OAuth credential files and weights. Gitignore is not a secret scanner; search the history before making the repo public or adding data. If a secret was committed, revoke/rotate; deleting a file does not erase Git history.
- User authorized Google account is the only way to validate uploads and channel data. Match intended channel, SHA-lock the reviewed MP4, explicitly require private, read back remote state; stop and reconcile after unknown remote result. No silent retries or public upload.
- Store source and creative approver identity/decision locally with tamper-evident hashes; approval must invalidate when facts, images, narration or export bytes change.

## Evidence and media

- RSS titles or URLs do not verify factual claims. Capture primary source links, publication dates, claim scope, corrections, competing evidence and human reviewer. Use source data only subject to license/API terms.
- Original author-owned graphics and recorded assets are preferred. Rights-attested means an owner claimed right to use the material; it is not independent legal verification.
- Third-party excerpts: precise clip owner/provenance/source, legal assessment, purpose and proportion, meaningful transformation/criticism, user approval; no guarantee of fair use, copyright safety or YouTube reused-content monetization. YouTube in-app Remix/Green Screen rules do not imply permission for downloading and reuploading externally.
- Avoid unconsented voice cloning, misleading synthetic representations or allegations. Follow relevant synthetic/altered content disclosure and topic-specific editorial rules.

## Public vs private artifacts

**Public Git:** source code, schemas, redacted example scripts, generated-illustration code, tests, documentation, benchmark methods and links.
**Private owner storage:** OAuth credentials, tokens, raw licensed footage/music, personal channel stats/revenue, sensitive interview material, model binaries, current SQLite state, rendered commercial videos and private editorial notes. Back up private assets offline; Git alone cannot restore them.

## Repo governance

Run CI, human code review for external actions, source rights review and protected main branch where available. Limit collaborators to necessary access. All releases specify what was tested and where.


### Owner voice/alignment data (M2.5)

Voice/model weights, identity, owner source transcripts, reviewed reference-word timings, local audio, licence evidence and WAV/provenance manifests belong in the owner's **private** folder, never this public Git repository. The M2.5 audio evaluator writes only redacted metrics/cryptographic digests outside the tree; it cannot independently verify licences or listener testimony. No voice cloning, external downloads, YouTube actions or automatic publication are enabled. Use `docs/M2_5_VOICE_ALIGNMENT_ACCEPTANCE.md`.

### Installed Piper executable trust and private audio (M2.5)

The optional `tools/run_local_piper.py` uses a **user-selected native executable**. It passes arguments without a shell and intentionally performs no download, but **cannot guarantee that an arbitrary executable never accesses the internet**. Install only trusted verified Piper binaries and use OS firewall isolation if strict offline operation is required. Keep private script, voice weights/config, raw and normalized WAV, model/executable hashes, identity/licence notes, reviewer and aligned word-level evidence **outside this public repository**. Attestation flags are not independent legal permission or voice consent validation. No publication is authorized. See `docs/M2_5_LOCAL_PIPER_RUNNER.md`.

### M2.5 offline CPU alignment proposal and private manifests

`tools/run_local_alignment.py` invokes a user-installed WhisperX-compatible model in a child Python process with common offline environment flags and a timeout. This **is not OS-level network sandboxing**. Trust/verifiably license WhisperX/torch dependencies and the offline model; use a disconnected host or firewall if network isolation is required. Exact private input text, WAVs, word timings and licensed model files must remain **outside this PUBLIC repo**, as must proposal/manifests/reports. Only SHA fingerprints and redacted technical metrics are suitable for a sanitized GitHub Issue comment. Outputs remain **UNREVIEWED**, copied human references remain empty, and no change to YouTube upload/privacy behavior is permitted. See `docs/M2_5_LOCAL_ALIGNMENT_RUNNER.md`.
