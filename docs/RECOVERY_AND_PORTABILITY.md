# Disaster recovery and portability

GitHub is the source for code and non-sensitive specifications. It does **not** restore runtime state, private media, YouTube credentials, licensed model weights or actual channel revenue.

1. Clone repository to new Windows PC; check `docs/START_HERE.md`, release/commit and `docs/IMPLEMENTATION_STATUS.md`.
2. Install Python 3.12, FFmpeg/ffprobe and requirements, then run tests; confirm actual `main` and tag/commit SHA before running app.
3. From a separate **encrypted private backup**, restore the owner SQLite databases, sources/approvals, original/rights-attested assets, authored scripts, voice/model licenses, rendered works and other runtime state. Restore carefully into configured local `data/` locations; never commit backups to public Git.
4. Re-authorize Google OAuth locally; rotate lost credentials; recheck YouTube channel identity and permissions. Do not copy tokens from chats or place them inside repository.
5. Run database integrity/migration and media provenance checks before allowing publishing; cross-validate each stored approval hash against current project/export bytes; uncertain prior uploads must be reconciled via YouTube Studio.
6. Resume queued work only after identity, licensing and hardware capability checks. Never auto-retry a potentially completed remote upload.

**Recovery drill required:** on a clean Windows user account restore code+mock private DB, render an owned original technical video, inspect SRT/audio and verify project isolation. No claim of successful disaster recovery until repeated on target machine.
