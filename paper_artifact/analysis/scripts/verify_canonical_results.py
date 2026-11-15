#!/usr/bin/env python3
"""Independent input verification: recomputes fields, never reads generated output.

No network or experiment interfaces. Canonical values are immutable inputs.
Exit 1 on numerical, input-integrity or consistency mismatch.
"""
import argparse
import hashlib
import json
import math
import platform
import sys

sys.dont_write_bytecode=True

import numpy
import scipy

from reproduce_paper_results import ROOT, compute


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--check-only',action='store_true',help='Do not write a report (useful for clean extraction)')
    args=parser.parse_args()
    canonical=json.loads((ROOT/'CANONICAL_RESULTS.json').read_text())
    manifest=json.loads((ROOT/'RESULTS_MANIFEST.json').read_text())
    integrity=[]
    for source in manifest['sources']:
        p=ROOT/source['file']
        if hashlib.sha256(p.read_bytes()).hexdigest()!=source['sha256']:integrity.append(source['file'])
    actual,_=compute()
    rows=[]
    for c in canonical['checks']:
        got=actual.get(c['metric'])
        if isinstance(c['value'],(bool,int)):
            ok=type(got)==type(c['value']) and got==c['value']
        else:
            ok=isinstance(got,(float,int)) and math.isfinite(got) and math.isclose(got,c['value'],rel_tol=c.get('rtol',0),abs_tol=c.get('atol',0))
        rows.append({'id':c['id'],'metric':c['metric'],'expected':c['value'],'reproduced':got,'status':'PASS' if ok else 'FAIL','source':'; '.join(c['sources'])})
    ok=not integrity and all(r['status']=='PASS' for r in rows)
    if not args.check_only:
        lines=['# Generated reproduction report','', 'This file is intentionally regenerated. The top-level REPRODUCTION_REPORT.md remains the frozen reference report. Generated output bytes are not the cross-version scientific acceptance criterion.','', 'Command: `python analysis/scripts/reproduce_paper_results.py` then `python analysis/scripts/verify_canonical_results.py`.', '',f'Environment: Python {platform.python_version()}; NumPy {numpy.__version__}; SciPy {scipy.__version__}.', '', f'Checks: {len(rows)}; PASS: {sum(r["status"]=="PASS" for r in rows)}; FAIL: {sum(r["status"]=="FAIL" for r in rows)}; supporting-source integrity failures: {len(integrity)}.', '', 'All values are recomputed from packaged retained inputs. Summary aggregation checks do not establish raw sample completeness or numerical parity of Unity outputs. Source-semantic checks are static checks only. No canonical file is rewritten.', '', '| ID | Field | Expected | Reproduced | Status | Supporting inputs |','|---|---|---|---|---|---|']
        lines+=['| '+' | '.join(str(r[k]) for k in ['id','metric','expected','reproduced','status','source'])+' |' for r in rows]
        lines+=['','## Provenance limits','','No missing headline numerical claim was substituted. The historical 814/1732 claim is regenerated from the retained historical status projection, not reconstructed from a fresh historical run. CV distributions are regenerated from retained per-model CVs, not all original per-iteration sample vectors. Environment, timing semantics and same-host provenance remain documentary evidence. Exact byte identity of discarded ONNX artifacts and Unity numerical parity are unavailable and are not claimed.']
        output=ROOT/'analysis/reproduced_outputs'
        output.mkdir(parents=True,exist_ok=True)
        (output/'REPRODUCTION_REPORT.generated.md').write_text('\n'.join(lines)+'\n')
        (output/'verification.json').write_text(json.dumps({'passed':ok,'integrity_failures':integrity,'checks':rows},indent=2,sort_keys=True)+'\n')
    print(f'{"PASS" if ok else "FAIL"}: {sum(r["status"]=="PASS" for r in rows)}/{len(rows)} canonical checks; {len(integrity)} input-integrity failures')
    for r in rows:
        if r['status']=='FAIL':print(r['id'],r['metric'],'expected',r['expected'],'got',r['reproduced'])
    return 0 if ok else 1


if __name__=='__main__':sys.exit(main())
