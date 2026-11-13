"""Reconstruct exact Ultimate v3 design files from immutable Combined v3 + edition overlay.

No models, network, OAuth, secret or app runtime required. Stdlib only.
"""
import argparse,hashlib,json,shutil,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent

def materialize(output:Path):
    base=ROOT/'spec'/'combined-v3';overlay=ROOT/'spec'/'ultimate-v3-overlay'
    manifest=json.loads((overlay/'DELTA_MANIFEST.json').read_text('utf8'))
    if not base.is_dir():raise RuntimeError('Combined v3 base snapshot not found')
    if output.resolve() in (base.resolve(),overlay.resolve()):raise RuntimeError('Refusing to overwrite source snapshot')
    if output.exists():raise RuntimeError(f'Output exists: {output} (choose a fresh path)')
    shutil.copytree(base,output)
    for relative in manifest['removed_from_combined']:
        path=output/relative
        if not path.is_file():raise RuntimeError('Expected base file missing: '+relative)
        path.unlink()
    for relative in manifest['changed_or_added_files']:
        p=overlay/relative
        if not p.is_file():raise RuntimeError('Missing overlay: '+relative)
        dest=output/relative;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
    expected=manifest['ultimate_files_sha256'];actual={}
    for p in output.rglob('*'):
        if p.is_file():actual[p.relative_to(output).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
    missing=sorted(set(expected)-set(actual));extra=sorted(set(actual)-set(expected))
    wrong=sorted(k for k in expected.keys()&actual.keys() if expected[k]!=actual[k])
    if missing or extra or wrong:
        raise RuntimeError(f'Ultimate v3 reconstruction mismatch missing={missing} extra={extra} sha_mismatch={wrong}')
    print(f'PASS: Ultimate v3 exact spec reconstructed ({len(actual)} files; sha256 matched) at {output}')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=ROOT/'outputs'/'ultimate-v3-spec')
    args=parser.parse_args();materialize(args.output)
if __name__=='__main__':main()
