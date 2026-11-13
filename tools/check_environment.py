"""Local diagnostics only; no internet, login or external downloads."""
import importlib.util, platform, shutil, sqlite3, sys
required=['fastapi','pydantic','PIL','multipart']
missing=[m for m in required if importlib.util.find_spec(m) is None]
print('System:',platform.platform())
print('Python:',sys.version.split()[0]);print('SQLite:',sqlite3.sqlite_version)
for exe in ['ffmpeg','ffprobe','piper','ollama']:
    print(f'{exe}:',shutil.which(exe) or 'NOT INSTALLED')
print('Python modules:', 'READY' if not missing else 'MISSING '+','.join(missing))
if missing or not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
    print('BLOCKED: install required dependencies and FFmpeg/FFprobe before creating videos')
    sys.exit(2)
print('Local CPU rendering prerequisites: present. End-to-end Windows hardware not yet verified.')
