# Contributing to ViralOS

Begin with `AGENTS.md` and `docs/START_HERE.md`. Source-led PRs must include negative tests and exact compatibility impact; no API credentials, downloaded broadcasts or proprietary voices in Git. Every feature should record proof level: **specified**, **local test**, **owner Windows test**, **real model**, **real YouTube**, **editorial QA**, **business outcome**.

Local checks: Python 3.12, FFmpeg/ffprobe, `pip install -r requirements.txt`, `python -m pytest -q`; optionally run `tools/check_environment.py`. CI may pass without enabling any external APIs. No automatic public upload or promise of guaranteed monetization.

For documentation changes, keep Launch/Ultimate spec references consistent with the single runtime. Refer to `docs/GIT_WORKFLOW.md`.
