"""SQLite v3 canonical migration reader. No implicit reset or schema drift."""
import os, sqlite3, hashlib
from pathlib import Path
from contextlib import contextmanager
ROOT=Path(__file__).resolve().parent.parent
DEFAULT_DB=ROOT/'data'/'viral.db'
MIGRATIONS=[('001', '001_schema.sql'), ('002', '002_controls.sql'), ('003', '003_creative.sql'), ('004', '004_m1_m3.sql'), ('005', '005_studio.sql'), ('006','006_m21_director.sql'),('007','007_m22_creative.sql'),('008','008_m3_publishing.sql'),('009','009_m23_intelligence.sql'),('010','010_m31_analytics.sql'),('011','011_m24_localization.sql'),('012','012_m32_acceptance.sql')]

def path():
    return Path(os.environ.get('VIRALOS_DB', str(DEFAULT_DB))).resolve()

def connect():
    f=path();f.parent.mkdir(parents=True,exist_ok=True)
    c=sqlite3.connect(str(f),timeout=10)
    c.row_factory=sqlite3.Row;c.execute('PRAGMA foreign_keys=ON');c.execute('PRAGMA busy_timeout=5000')
    return c

@contextmanager
def read():
    c=connect()
    try:yield c
    finally:c.close()

@contextmanager
def transaction():
    c=connect()
    try:
        c.execute('BEGIN IMMEDIATE')
        yield c
        c.commit()
    except Exception:
        c.rollback();raise
    finally:c.close()

def initialize():
    with read() as c:
        c.execute('PRAGMA journal_mode=WAL')
        for num, name in MIGRATIONS:
            sql=(ROOT/'sql'/name).read_text(encoding='utf8')
            checksum=hashlib.sha256(sql.encode()).hexdigest()
            if num!='001':
                row=c.execute('SELECT checksum_sha256 FROM schema_migrations WHERE version=?',(num,)).fetchone()
                if row:
                    if row['checksum_sha256']!=checksum:raise RuntimeError(f'Migration checksum mismatch {num}')
                    continue
            else:
                table=c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='schema_migrations'").fetchone()
                if table:
                    row=c.execute('SELECT checksum_sha256 FROM schema_migrations WHERE version=?',(num,)).fetchone()
                    if row:
                        if row['checksum_sha256']!=checksum:raise RuntimeError('Migration checksum mismatch 001')
                        continue
            c.executescript(sql)
            c.execute('INSERT INTO schema_migrations (version,applied_at,checksum_sha256) VALUES (?,datetime(\'now\'),?)',(num,checksum))
            c.commit()
        # Never auto-enable high-risk/future domains. Sports only for launch.
        domains=('newsroom','science','technology','business','gaming','history','space','learning','sports','career','productivity','culture')
        for d in domains:
            c.execute('INSERT OR IGNORE INTO domains(domain_id,dossier_path,enabled) VALUES (?,?,?)',(d,f'domains/{d}',1 if d=='sports' else 0))
        c.commit()

def one(c,sql,args=()):
    row=c.execute(sql,args).fetchone()
    return dict(row) if row else None

def many(c,sql,args=()):
    return [dict(r) for r in c.execute(sql,args).fetchall()]
