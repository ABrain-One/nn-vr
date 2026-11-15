#!/usr/bin/env python3
"""Generate deterministic file manifest, SHA-256 sums and LOCAL ZIP only.

No publication, Git mutation, network or experiment functions. Run after checks
and documentation are final. ZIP is outside the artifact to avoid self-hashing.
"""
import hashlib
import argparse
import importlib.metadata
import os
import platform
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
ZIP=ROOT.with_suffix('.zip')


def files():
    selected=[]
    for directory,dirs,names in os.walk(ROOT):
        dirs[:]=sorted(d for d in dirs if d not in ('.venv','venv','.git'))
        selected.extend(Path(directory)/name for name in names)
    selected=sorted(selected)
    for p in selected:
        if p.is_symlink() or any(s in p.parts for s in ['__pycache__','.git','.DS_Store']) or p.suffix in ['.pyc','.aux','.log','.tmp','.onnx','.pth','.pt']:
            raise ValueError('Unexpected release file: '+p.relative_to(ROOT).as_posix())
    return selected


def generated(p):
    return p.relative_to(ROOT).parts[:2]==('analysis','reproduced_outputs')


def purpose(p):
    rel=p.relative_to(ROOT).as_posix()
    if rel=='REFERENCE_OUTPUT_HASHES.txt':return 'Optional pinned-environment output-byte reference; not a cross-version scientific requirement.'
    if rel=='REPRODUCTION_REPORT.md':return 'Frozen A1 reference report; verification writes a separate generated report.'
    if rel.startswith('analysis/scripts/'):return 'Offline reproduction, verification, plotting or local packaging helper / requirements.'
    if rel.startswith('analysis/reproduced_outputs/'):return 'Deterministically regenerated paper summary/table/figure or verification output.'
    if rel.startswith('provenance/analysis_source/') or rel.startswith('provenance/runtime_source/'):return 'Inert original source snapshot; provenance only, never executed by artifact workflow.'
    if rel.startswith('provenance/licenses/'):return 'Original project license notice; retained verbatim.'
    if rel.startswith('provenance/manuscript/'):return 'Frozen claim, table, diagram or scientific-source evidence copied for traceability.'
    if rel.startswith('provenance/'):return 'Original/released-file hashes, transformations or retained historical identity/status projection.'
    if rel.startswith('environment/'):return 'Recorded environment and checkout provenance; missing historical values explicitly marked.'
    if p.suffix in ['.csv','.json']:return 'Selected retained derived evidence or fixed canonical/claim metadata.'
    return 'Artifact instructions, output map, provenance, integrity, audit or citation documentation.'


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--zip-output',type=Path,default=ZIP,help='Local validation ZIP path outside the artifact; never uploaded by this script')
    parser.add_argument('--freeze-reference-outputs',action='store_true',help='Explicitly capture output hashes under the pinned reference environment only')
    args=parser.parse_args()
    reference=ROOT/'REFERENCE_OUTPUT_HASHES.txt'
    if args.freeze_reference_outputs:
        expected={'numpy':'2.2.6','scipy':'1.15.3','matplotlib':'3.10.9'}
        if platform.python_version()!='3.10.12' or any(importlib.metadata.version(k)!=v for k,v in expected.items()):
            raise SystemExit('Reference hashes require Python 3.10.12 and the exact pinned dependency versions.')
        reference.write_text('# Optional reference-render hashes: Python 3.10.12, NumPy 2.2.6, SciPy 1.15.3, Matplotlib 3.10.9.\n# These are not the scientific verification criterion across environments.\n'+''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(ROOT).as_posix()}\n' for p in files() if generated(p)))
    if not reference.exists():
        raise SystemExit('Reference hashes not yet captured; use --freeze-reference-outputs in the pinned environment.')
    manifest=ROOT/'MANIFEST.md'
    if not manifest.exists():manifest.touch()
    sums=ROOT/'SHA256SUMS'
    if not sums.exists():sums.touch()
    rows=['# Artifact file manifest','', 'Artifact version: 1.0.0. SHA256SUMS covers immutable release inputs, active scripts, provenance and release documentation, including the frozen top-level REPRODUCTION_REPORT.md. It excludes generated files under analysis/reproduced_outputs/ and itself. REFERENCE_OUTPUT_HASHES.txt separately records optional pinned-environment output hashes; it is not a cross-version scientific criterion. Local .venv/venv environments and .git metadata are not packaged. The validation ZIP is generated outside this directory; packaging performs no Git or public action.','', '| File | Integrity class | Purpose |','|---|---|---|']
    rows += [f'| `{p.relative_to(ROOT).as_posix()}` | {"generated reference output" if generated(p) else "immutable release file" if p!=sums else "integrity manifest (self excluded)"} | {purpose(p)} |' for p in files()]
    manifest.write_text('\n'.join(rows)+'\n')
    selected=files()
    sums.write_text(''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(ROOT).as_posix()}\n' for p in selected if p!=sums and not generated(p)))
    # Fixed timestamps, sorted paths, normalized permissions and compression.
    # Rebuilding unchanged files on the same zlib implementation is byte repeatable.
    target=args.zip_output.resolve()
    if target.is_relative_to(ROOT):raise SystemExit('Validation ZIP must remain outside artifact directory.')
    with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for p in files():
            item=zipfile.ZipInfo(ROOT.name+'/'+p.relative_to(ROOT).as_posix(),date_time=(2026,11,15,0,0,0))
            item.compress_type=zipfile.ZIP_DEFLATED;item.create_system=3;item.external_attr=0o100644<<16
            archive.writestr(item,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    print(f'ZIP: {target.name}; {target.stat().st_size} bytes; {len(files())} files; SHA256 {hashlib.sha256(target.read_bytes()).hexdigest()}')


if __name__=='__main__':main()
