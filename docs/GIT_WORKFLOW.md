# GitHub workflow — safe revisions and reviewer checkpoints

Canonical remote: `https://github.com/sahilk267/youtube-automation-platform-cgpt.git`. Initial main bootstrapped 2026-11-13; repository initially PUBLIC. Workflow: feature branches and pull requests; no force push to main. Shared Launch/Ultimate code—different configuration and policy packs, not different apps.

After cloning:

```powershell
git status
git pull --ff-only origin main
git switch -c feat/descriptive-change
# modify files and tests
python -m pytest -q
git add app sql tests docs
git commit -m "feat: describe validated change"
git push -u origin feat/descriptive-change
# Open PR; compare changed source/test/doc contracts, inspect CI.
```

Before merge, update implementation status and known gaps. Do not commit build outputs, models, `.env`, downloaded media or `data/` DB. The research and specification snapshots under `spec/` are **historical documents**, immutable unless a versioned explicit migration is created. Avoid duplicated runtime application copies.

CI runs offline Python tests with explicit FFmpeg dependency; live model tests/Google OAuth/human content review remain owner acceptance gates and are NOT established by CI.

### Files to preserve

`README.md`, `AGENTS.md`, `docs/START_HERE.md`, `docs/ARCHITECTURE.md`, `docs/IMPLEMENTATION_STATUS.md`, `docs/ROADMAP.md`, `docs/SECURITY_AND_RIGHTS.md`, source `app/`, SQL `sql/`, tests `tests/`, versioned specs `spec/`, and research `research/`. Build reports are historical evidence, not a pass guarantee on later commits.
