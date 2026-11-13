# Windows 10/11 setup — CPU-only first

**Baseline:** Intel i7 8th generation, 32 GB RAM, no GPU; Python 3.12, Git, FFmpeg (`ffprobe` alongside), internet only for explicit dependency install. Development only, not a hosted service.

```powershell
# One-time: install Python 3.12 and FFmpeg manually from trusted upstream sources.
# Verify:
py -3.12 --version
git --version
ffmpeg -version
ffprobe -version

# Clone after repository source files are present:
git clone https://github.com/sahilk267/youtube-automation-platform-cgpt.git
cd youtube-automation-platform-cgpt
powershell -ExecutionPolicy Bypass -File .\tools\start_windows.ps1
```

Script creates `.venv`, installs `requirements.txt`, runs local environment check, full automated tests and then serves on `127.0.0.1:8000`. Browser: `http://127.0.0.1:8000`; API docs: `http://127.0.0.1:8000/docs`.

### Manual troubleshooting

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe tools\check_environment.py
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

`tools/verify_package.py` may refer to a **historical ZIP packaging manifest**; it is not a Git checkout integrity validator. See `docs/SOURCE_SYNC_STATUS.md`. For Git checkouts use normal `git status`, tests and CI. Any failures should be reported exactly, not overridden.

**Optional** licensed Piper voice and compatible WhisperX/ASR are NOT bundled; install voluntarily, verify local model rights and language compatibility, document source/hash/model version. English/Hindi TTS and forced alignment are not proven by adapter tests. Google OAuth requires owner's desktop consent and sensitive secrets remain private. Never upload automatically to public.

### Performance acceptance

On owner PC measure: cold start, RAM idle/peak, one source/research project, 10–30s original Shorts preview, 16:9 video, FFmpeg wall time, actual audio/caption timing and failures. Baseline in GitHub cannot guarantee performance.
