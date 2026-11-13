"""Issue #4: offline CPU and private backup/restore negative regression."""
import json
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

from app import db
from tools import owner_acceptance as accept


@pytest.fixture
def seeded_database(tmp_path, monkeypatch):
    database = tmp_path / 'owner.sqlite3'
    monkeypatch.setenv('VIRALOS_DB', str(database))
    db.initialize()
    return database


def test_preflight_does_not_assume_owner_hardware():
    result = accept.preflight()
    assert result['owner_i7_windows_hardware_verified'] is False
    assert result['youtube_account_tested'] is False
    assert 'missing_python_modules' in result


def test_backup_integrity_and_clean_restore(seeded_database, tmp_path):
    database = seeded_database
    with sqlite3.connect(database) as connection:
        count_before = connection.execute('SELECT count(*) FROM schema_migrations').fetchone()[0]
        assert count_before == 12
    data = accept.make_backup(database, tmp_path / 'PrivateVault')
    assert data['status'] == 'BACKUP_CREATED' and not data['media_files_included']
    original, manifest, checks = accept.verify_backup(Path(data['manifest']))
    assert original.is_file() and checks['integrity'] == 'ok'
    assert checks['migrations'] == [f'{n:03}' for n in range(1, 13)]
    restored = tmp_path / 'other-profile' / 'clean.sqlite3'
    answer = accept.restore_backup(Path(data['manifest']), restored)
    assert answer['status'] == 'RESTORED_IN_CLEAN_PROFILE'
    assert answer['media_restored'] is False and answer['credentials_restored'] is False
    assert restored.is_file() and accept.database_checks(restored)['integrity'] == 'ok'
    with sqlite3.connect(restored) as c:
        assert c.execute('SELECT COUNT(*) FROM schema_migrations').fetchone()[0] == count_before
    with pytest.raises(ValueError, match='already exists'):
        accept.restore_backup(Path(data['manifest']), restored)


def test_backup_refuses_public_git_tree(seeded_database):
    with pytest.raises(ValueError, match='Git repository'):
        accept.make_backup(seeded_database, accept.ROOT / 'data' / 'backup-test')


def test_corrupted_backup_is_rejected(seeded_database, tmp_path):
    result = accept.make_backup(seeded_database, tmp_path / 'vault')
    p = Path(result['database'])
    with p.open('ab') as stream:
        stream.write(b'modified')
    with pytest.raises(ValueError, match='size mismatch'):
        accept.verify_backup(Path(result['manifest']))
    assert not (tmp_path / 'restored.sqlite3').exists()


def test_manifest_path_traversal_is_rejected(seeded_database, tmp_path):
    result = accept.make_backup(seeded_database, tmp_path / 'vault')
    manifest = Path(result['manifest'])
    payload = json.loads(manifest.read_text())
    payload['database_file'] = '../secret.sqlite3'
    manifest.write_text(json.dumps(payload), encoding='utf-8')
    with pytest.raises(ValueError, match='filename'):
        accept.verify_backup(manifest)


def test_bad_database_migration_checksum_is_rejected(seeded_database, tmp_path):
    # Reading the original must fail BEFORE creating a backup.
    with sqlite3.connect(seeded_database) as c:
        c.execute("UPDATE schema_migrations SET checksum_sha256='x' WHERE version='012'")
    with pytest.raises(ValueError, match='Migration checksum'):
        accept.make_backup(seeded_database, tmp_path / 'vault')
    assert not (tmp_path / 'vault').exists()


def test_approval_and_inflight_states_invalidated_on_restore():
    # Core SQL transition test avoids creating fabricated approved output media.
    with sqlite3.connect(':memory:') as c:
        c.executescript('''
          CREATE TABLE m22_final_exports(status TEXT);
          CREATE TABLE m3_exports(status TEXT);
          CREATE TABLE m3_private_upload_intents(state TEXT,last_error TEXT);
          INSERT INTO m22_final_exports VALUES ('OWNER_APPROVED_FINAL_EXPORT');
          INSERT INTO m22_final_exports VALUES ('INVALIDATED');
          INSERT INTO m3_exports VALUES ('READY_FOR_MANUAL_UPLOAD');
          INSERT INTO m3_private_upload_intents VALUES ('IN_FLIGHT',NULL);
          INSERT INTO m3_private_upload_intents VALUES ('UPLOADED_PRIVATE',NULL);
        ''')
        report = accept.invalidate_restored_approvals(c)
        assert report['final_exports_invalidated'] == 1
        assert report['manual_exports_invalidated'] == 1
        assert report['uncertain_uploads_marked_remote_unknown'] == 1
        assert c.execute('SELECT DISTINCT status FROM m22_final_exports').fetchone()[0] == 'INVALIDATED'
        assert c.execute('SELECT state FROM m3_private_upload_intents ORDER BY rowid').fetchall() == [
            ('REMOTE_UNKNOWN',), ('UPLOADED_PRIVATE',)]


def test_restore_refuses_existing_wal_sidecars(seeded_database, tmp_path):
    result = accept.make_backup(seeded_database, tmp_path / 'vault')
    target = tmp_path / 'profile.db'
    Path(str(target) + '-wal').write_bytes(b'NOT_A_REAL_WAL')
    with pytest.raises(ValueError, match='already exists'):
        accept.restore_backup(Path(result['manifest']), target)
    assert not target.exists()


@pytest.mark.skipif(not (shutil.which('ffmpeg') and shutil.which('ffprobe')), reason='FFmpeg unavailable')
def test_benchmark_generates_verified_video_and_audio():
    result = accept.benchmark(duration=0.75)
    assert result['status'] == 'CPU_FFMPEG_SMOKE_VERIFIED'
    assert len(result['results']) == 2
    assert {r['resolution'] for r in result['results']} == {'540x960', '960x540'}
    assert all(r['video_codec'] == 'h264' and r['audio_codec'] == 'aac' for r in result['results'])
    assert all(r['output_bytes'] > 1000 for r in result['results'])
    assert result['ram_measurement'] in ('SAMPLED_RSS_PSUTIL','NOT_MEASURED')
    if result['ram_measurement'] == 'SAMPLED_RSS_PSUTIL':
        assert result['peak_ram_bytes'] > 0


def test_cli_preflight_json_only_and_no_remote_call():
    proc = subprocess.run([sys.executable, str(accept.ROOT / 'tools' / 'owner_acceptance.py'), 'preflight'],
                          capture_output=True, text=True, timeout=20)
    assert proc.returncode in (0, 2)
    payload = json.loads(proc.stdout)
    assert payload['live_voice_models_tested'] is False
    assert payload['youtube_account_tested'] is False


def test_online_backup_captures_wal_changes(seeded_database, tmp_path):
    # Keep a live WAL connection open while taking a consistent backup.
    with sqlite3.connect(seeded_database) as connection:
        connection.execute('PRAGMA journal_mode=WAL')
        connection.execute('CREATE TABLE extra_wal_probe(value TEXT NOT NULL)')
        connection.execute("INSERT INTO extra_wal_probe VALUES ('committed')")
        connection.commit()
        backup = accept.make_backup(seeded_database, tmp_path / 'vault')
    with sqlite3.connect(backup['database']) as restored:
        assert restored.execute('SELECT value FROM extra_wal_probe').fetchone()[0] == 'committed'


def test_cli_supports_post_command_report_path(tmp_path):
    target = tmp_path / 'preflight.json'
    proc = subprocess.run([sys.executable, str(accept.ROOT / 'tools' / 'owner_acceptance.py'),
                           'preflight', '--report', str(target)],
                          capture_output=True, text=True, timeout=20)
    assert proc.returncode in (0, 2)
    assert target.is_file()
    assert json.loads(target.read_text())['youtube_account_tested'] is False