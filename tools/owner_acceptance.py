"""ViralOS owner Windows/CPU acceptance and private SQLite recovery.

Offline stdlib CLI. Never contacts accounts, downloads models or includes media in
DB snapshots. A backup is sensitive; it MUST stay out of the public repository.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import secrets
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = ROOT / 'data' / 'viral.db'
BACKUP_FOLDER = Path.home() / 'ViralOSPrivateBackups'
MIGRATION_DIR = ROOT / 'sql'
MAX_MANIFEST_BYTES = 1_000_000


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_json(path: Path, payload: dict) -> None:
    temp = path.with_name(path.name + '.tmp-' + secrets.token_hex(5))
    try:
        temp.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + '\n', encoding='utf-8')
        os.chmod(temp, 0o600)
        temp.replace(path)
    finally:
        temp.unlink(missing_ok=True)


def table_exists(connection: sqlite3.Connection, name: str) -> bool:
    return connection.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)).fetchone() is not None


def database_checks(database: Path, *, expect_project_schema: bool = True) -> dict:
    if not database.is_file() or database.stat().st_size == 0:
        raise ValueError('Database missing or empty; initialize the local app first')
    try:
        with sqlite3.connect(database.as_uri() + '?mode=ro', uri=True) as connection:
            integrity = connection.execute('PRAGMA integrity_check').fetchone()[0]
            if integrity != 'ok':
                raise ValueError('SQLite integrity_check failed: ' + str(integrity)[:100])
            foreign_errors = connection.execute('PRAGMA foreign_key_check').fetchmany(1)
            if foreign_errors:
                raise ValueError('SQLite foreign_key_check failed')
            if not table_exists(connection, 'schema_migrations'):
                if expect_project_schema:
                    raise ValueError('Not a ViralOS database (missing schema_migrations)')
                return {'integrity': 'ok', 'migrations': [], 'asset_reference_counts': {}}
            migrations = {str(version): str(digest) for version, digest in connection.execute(
                'SELECT version, checksum_sha256 FROM schema_migrations')}
            if not migrations:
                raise ValueError('No canonical migrations found')
            # Detect migration corruption. Older snapshots can be migrated on a
            # separate branch; this tool intentionally rejects unknown versions.
            expected = {p.name[:3]: hashlib.sha256(p.read_text(encoding='utf-8').encode('utf-8')).hexdigest()
                        for p in MIGRATION_DIR.glob('[0-9][0-9][0-9]_*.sql')}
            if set(migrations) != set(expected):
                raise ValueError('Migration version mismatch; use matching ViralOS source revision')
            if any(migrations[k] != expected[k] for k in migrations):
                raise ValueError('Migration checksum mismatch; do not restore this snapshot')
            counts = {}
            for table in ('assets', 'm2_studio_assets', 'm21_voice_segments',
                          'm24_narration_segments', 'm22_final_exports', 'm3_private_upload_intents'):
                if table_exists(connection, table):
                    counts[table] = connection.execute('SELECT COUNT(*) FROM "' + table + '"').fetchone()[0]
            return {'integrity': 'ok', 'migrations': sorted(migrations), 'asset_reference_counts': counts}
    except sqlite3.DatabaseError as error:
        raise ValueError('Cannot read a valid SQLite database: ' + type(error).__name__) from error


def make_backup(source: Path, destination_folder: Path) -> dict:
    source = source.expanduser().resolve()
    checks = database_checks(source)
    destination_folder = destination_folder.expanduser().resolve()
    # Database snapshots must never be committed to this PUBLIC repository.
    if destination_folder == ROOT or ROOT in destination_folder.parents:
        raise ValueError('Private backups cannot be written inside the Git repository')
    destination_folder.mkdir(parents=True, exist_ok=True)
    unique = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + secrets.token_hex(4)
    database = destination_folder / ('viralos-' + unique + '.sqlite3')
    temp = destination_folder / (database.name + '.incomplete')
    manifest = destination_folder / (database.name + '.manifest.json')
    try:
        with sqlite3.connect(source.as_uri() + '?mode=ro', uri=True) as src, sqlite3.connect(temp) as dst:
            src.backup(dst, pages=128)
        os.chmod(temp, 0o600)
        database_checks(temp)
        temp.replace(database)
        payload = {
            'format': 'viralos-sqlite-backup-v1', 'created_utc': utc_now(),
            'database_file': database.name, 'database_sha256': sha256(database),
            'database_bytes': database.stat().st_size,
            'migrations': checks['migrations'],
            'asset_reference_counts': checks['asset_reference_counts'],
            'scope': 'DATABASE_ONLY', 'media_files_included': False,
            'credential_store_included': False,
            'backup_private_sensitive_data': True,
            'restored_final_exports_require_new_human_review': True,
        }
        atomic_json(manifest, payload)
        return {'status': 'BACKUP_CREATED', 'database': str(database), 'manifest': str(manifest),
                'database_sha256': payload['database_sha256'],
                'media_files_included': False, 'warning': 'Keep both files private and off GitHub'}
    finally:
        temp.unlink(missing_ok=True)


def verify_backup(manifest_file: Path) -> tuple[Path, dict, dict]:
    manifest_file = manifest_file.expanduser().resolve()
    if not manifest_file.is_file() or manifest_file.stat().st_size > MAX_MANIFEST_BYTES:
        raise ValueError('Manifest missing or invalid size')
    try:
        payload = json.loads(manifest_file.read_text(encoding='utf-8'))
    except (ValueError, UnicodeError) as error:
        raise ValueError('Invalid JSON manifest') from error
    if payload.get('format') != 'viralos-sqlite-backup-v1' or payload.get('scope') != 'DATABASE_ONLY':
        raise ValueError('Unsupported backup type')
    name = payload.get('database_file')
    if not isinstance(name, str) or name in ('.', '..') or Path(name).name != name or not name.endswith('.sqlite3'):
        raise ValueError('Invalid database filename in manifest')
    database = manifest_file.parent / name
    if database.is_symlink():
        raise ValueError('Symlink backup is not accepted')
    if not database.is_file() or database.stat().st_size != payload.get('database_bytes'):
        raise ValueError('Backup file missing or size mismatch')
    digest = payload.get('database_sha256')
    if not isinstance(digest, str) or len(digest) != 64 or sha256(database) != digest:
        raise ValueError('Backup SHA-256 mismatch; refuse restore')
    checks = database_checks(database)
    if payload.get('migrations') != checks['migrations']:
        raise ValueError('Manifest migration list mismatch')
    return database, payload, checks


def invalidate_restored_approvals(connection: sqlite3.Connection) -> dict:
    """Keep the audit record but revoke exports that cannot be trusted off-machine."""
    changes = {}
    if table_exists(connection, 'm22_final_exports'):
        count = connection.execute("UPDATE m22_final_exports SET status='INVALIDATED' "
                                   "WHERE status='OWNER_APPROVED_FINAL_EXPORT'").rowcount
        changes['final_exports_invalidated'] = count
    if table_exists(connection, 'm3_exports'):
        count = connection.execute("UPDATE m3_exports SET status='INVALIDATED' "
                                   "WHERE status='READY_FOR_MANUAL_UPLOAD'").rowcount
        changes['manual_exports_invalidated'] = count
    if table_exists(connection, 'm3_private_upload_intents'):
        count = connection.execute("UPDATE m3_private_upload_intents SET state='REMOTE_UNKNOWN', "
                                   "last_error='RESTORE_REQUIRES_REMOTE_RECONCILIATION' "
                                   "WHERE state='IN_FLIGHT'").rowcount
        changes['uncertain_uploads_marked_remote_unknown'] = count
    return changes


def restore_backup(manifest_file: Path, target_file: Path) -> dict:
    database, payload, _ = verify_backup(manifest_file)
    target = target_file.expanduser().resolve()
    if target.exists() or Path(str(target) + '-wal').exists() or Path(str(target) + '-shm').exists():
        raise ValueError('Target DB/WAL/SHM already exists; restore ONLY into a clean profile')
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_name(target.name + '.restore-incomplete-' + secrets.token_hex(5))
    try:
        # Use a fresh SQLite file, not a raw copy into a running WAL database.
        with sqlite3.connect(database.as_uri() + '?mode=ro', uri=True) as src, sqlite3.connect(temp) as dst:
            src.backup(dst)
            dst.execute('BEGIN IMMEDIATE')
            try:
                changes = invalidate_restored_approvals(dst)
                dst.commit()
            except Exception:
                dst.rollback()
                raise
        os.chmod(temp, 0o600)
        database_checks(temp)
        # No overwrite; private-data restore does not overwrite an existing profile.
        if target.exists():
            raise ValueError('Target was created during restore; refusing to overwrite')
        # O_EXCL reserve target to avoid accidental existing-file replacement.
        fd = os.open(target, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.close(fd)
        try:
            temp.replace(target)
        except Exception:
            target.unlink(missing_ok=True)
            raise
        return {'status': 'RESTORED_IN_CLEAN_PROFILE', 'target': str(target),
                'source_backup_sha256': payload['database_sha256'],
                'database_integrity': 'ok', 'actions': changes,
                'media_restored': False, 'credentials_restored': False,
                'next_steps': 'Recheck local media, reconnect owned accounts and re-review every final export'}
    finally:
        temp.unlink(missing_ok=True)


def preflight() -> dict:
    required = ('fastapi', 'pydantic', 'PIL', 'multipart', 'pytest')
    import importlib.util
    missing = [module for module in required if importlib.util.find_spec(module) is None]
    ffmpeg = shutil.which('ffmpeg')
    ffprobe = shutil.which('ffprobe')
    return {
        'time_utc': utc_now(), 'status': 'READY_FOR_CPU_SMOKE' if not missing and ffmpeg and ffprobe else 'BLOCKED',
        'host': {'system': platform.system(), 'release': platform.release(),
                 'python': platform.python_version(), 'cpu_logical_count': os.cpu_count(),
                 'dedicated_gpu_tested': False},
        'tools_present': {'ffmpeg': bool(ffmpeg), 'ffprobe': bool(ffprobe),
                          'piper_optional': bool(shutil.which('piper'))},
        'missing_python_modules': missing,
        'live_voice_models_tested': False, 'youtube_account_tested': False,
        'owner_i7_windows_hardware_verified': False,
        'warning': 'A system report is NOT an owner-device performance or professional-video acceptance',
    }


def encode_demo(size: tuple[int, int], destination: Path, duration: float) -> dict:
    ffmpeg, ffprobe = shutil.which('ffmpeg'), shutil.which('ffprobe')
    if not ffmpeg or not ffprobe:
        raise ValueError('FFmpeg and FFprobe are required')
    width, height = size
    command = [ffmpeg, '-hide_banner', '-loglevel', 'error', '-nostdin', '-y',
               '-f', 'lavfi', '-i', f'testsrc2=size={width}x{height}:rate=24',
               '-f', 'lavfi', '-i', 'sine=frequency=440:sample_rate=16000',
               '-t', str(duration), '-c:v', 'libx264', '-preset', 'ultrafast',
               '-crf', '28', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '64k',
               '-shortest', str(destination)]
    try:
        import psutil  # optional: never required for the core app
    except ImportError:
        psutil = None
    started = time.monotonic()
    with subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE) as proc:
        monitor = psutil.Process(proc.pid) if psutil is not None else None
        peak_bytes = None
        deadline = started + 120
        while proc.poll() is None:
            if time.monotonic() >= deadline:
                proc.kill()
                proc.communicate()
                raise ValueError('FFmpeg benchmark timed out')
            if monitor is not None:
                try:
                    current = monitor.memory_info().rss
                    peak_bytes = max(peak_bytes or 0, current)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            time.sleep(0.025)
        _, stderr = proc.communicate(timeout=5)
        returncode = proc.returncode
    wall_time = round(time.monotonic() - started, 3)
    if returncode != 0:
        raise ValueError('FFmpeg encode failed: ' + stderr.decode('utf-8', 'replace')[-260:])
    inspect = subprocess.run([ffprobe, '-v', 'error', '-show_streams', '-show_format',
                              '-of', 'json', str(destination)], capture_output=True, timeout=30, check=True)
    info = json.loads(inspect.stdout)
    streams = info['streams']
    video = next((s for s in streams if s['codec_type'] == 'video'), None)
    audio = next((s for s in streams if s['codec_type'] == 'audio'), None)
    if not video or not audio or video['width'] != width or video['height'] != height:
        raise ValueError('Benchmark MP4 stream verification failed')
    return {'resolution': f'{width}x{height}', 'wall_seconds': wall_time,
            'video_codec': video.get('codec_name'), 'audio_codec': audio.get('codec_name'),
            'duration_seconds': float(info['format']['duration']),
            'output_bytes': destination.stat().st_size, 'media_sha256': sha256(destination),
            'process_peak_ram_bytes': peak_bytes,
            'ram_measurement': 'SAMPLED_RSS_PSUTIL' if peak_bytes is not None else 'NOT_MEASURED'}


def benchmark(duration: float = 2.0) -> dict:
    if duration < 0.5 or duration > 15:
        raise ValueError('Duration must be between 0.5 and 15 seconds')
    with tempfile.TemporaryDirectory(prefix='viralos-cpu-benchmark-') as folder:
        directory = Path(folder)
        results = [encode_demo(size, directory / (name + '.mp4'), duration)
                   for size, name in [((540, 960), 'vertical'), ((960, 540), 'horizontal')]]
    measured = [r['process_peak_ram_bytes'] for r in results if r['process_peak_ram_bytes'] is not None]
    return {'status': 'CPU_FFMPEG_SMOKE_VERIFIED', 'generated_utc': utc_now(),
            'hardware': platform.platform(), 'results': results,
            'render_speed_is_not_professional_quality': True,
            'peak_ram_bytes': max(measured) if measured else None,
            'ram_measurement': 'SAMPLED_RSS_PSUTIL' if measured else 'NOT_MEASURED',
            'actual_owner_hardware_verified': False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='command', required=True)
    subs.add_parser('preflight', help='Offline environment diagnostics only')
    bench = subs.add_parser('benchmark', help='Generate original synthetic 9:16 and 16:9 FFmpeg smoke videos')
    bench.add_argument('--duration', type=float, default=2.0)
    back = subs.add_parser('backup', help='SQLite online backup WITHOUT media or OS credentials')
    back.add_argument('--db', type=Path, default=Path(os.getenv('VIRALOS_DB', DEFAULT_DB)))
    back.add_argument('--dir', type=Path, default=BACKUP_FOLDER)
    verify = subs.add_parser('verify', help='Verify database, backup SHA and migration integrity')
    verify.add_argument('--manifest', type=Path, required=True)
    restore = subs.add_parser('restore', help='Restore into a NONEXISTENT database with stale exports invalidated')
    restore.add_argument('--manifest', type=Path, required=True)
    restore.add_argument('--target', type=Path, required=True)
    for sub in (subs.choices.values()):
        sub.add_argument('--report', type=Path, help='Save JSON report outside the Git repository')
    args = parser.parse_args()
    try:
        if args.command == 'preflight': result = preflight()
        elif args.command == 'benchmark': result = benchmark(args.duration)
        elif args.command == 'backup': result = make_backup(args.db, args.dir)
        elif args.command == 'verify':
            database, payload, checks = verify_backup(args.manifest)
            result = {'status': 'BACKUP_VERIFIED', 'sha256': payload['database_sha256'],
                      'database_bytes': database.stat().st_size, **checks,
                      'media_files_included': False}
        else: result = restore_backup(args.manifest, args.target)
        if args.report:
            report = args.report.expanduser().resolve()
            if report == ROOT or ROOT in report.parents:
                raise ValueError('Do not write local acceptance reports inside PUBLIC repository')
            report.parent.mkdir(parents=True, exist_ok=True)
            atomic_json(report, result)
        print(json.dumps(result, indent=2))
        return 0 if result.get('status') != 'BLOCKED' else 2
    except (ValueError, OSError, subprocess.TimeoutExpired, subprocess.CalledProcessError) as error:
        print(json.dumps({'status': 'FAILED_SAFE', 'error': str(error)}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())