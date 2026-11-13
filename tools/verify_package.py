"""Check build file hashes after extracting package; does not test application behavior."""
from pathlib import Path
import hashlib,json,sys
root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'INTEGRITY_MANIFEST.json').read_text('utf8'))
missing=[];wrong=[]
for name,expected in manifest['files_sha256'].items():
    path=root/name
    if not path.is_file():missing.append(name)
    elif hashlib.sha256(path.read_bytes()).hexdigest()!=expected:wrong.append(name)
if missing or wrong:
    print('FAIL: missing',missing,'hash mismatches',wrong)
    sys.exit(1)
print('PASS: verified',len(manifest['files_sha256']),'package file hashes')
