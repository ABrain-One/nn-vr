#!/usr/bin/env python3
"""Reproduce existing paper summaries exclusively from local retained CSVs.

Safety boundary: no network, subprocess, Unity, torch, ONNX, dataset access or
model execution. All inputs resolve inside this artifact. This is an adaptation
of the retained analysis formulas, not the original campaign runner.
"""
from __future__ import annotations

import csv
import inspect
import json
import math
from collections import Counter
from pathlib import Path
from statistics import median

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / 'analysis/reproduced_outputs'


def read_csv(relative):
    path = (ROOT / relative).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError('Input must remain inside artifact')
    with path.open(encoding='utf-8', newline='') as stream:
        return list(csv.DictReader(stream))


def truth(value):
    return str(value).lower() in ('true', '1')


def number(value):
    return float(value) if value not in ('', None) else None


def campaign_count(row, key):
    if row[key] != '':
        return int(row[key])
    # Retained B CSV omits the absent category; explicit timeout_or_skipped is 0.
    # Only this documented schema case is accepted, never a generic missing=zero.
    if key == 'failure_timeout' and row['runtime'] == 'B' and row['timeout_or_skipped'] == '0':
        return 0
    raise ValueError(f'Unexpected missing campaign value: {key}')


def wilson(k, n):
    z = 1.959963984540054
    denominator = 1 + z*z/n
    center = (k/n + z*z/(2*n))/denominator
    radius = z*math.sqrt(k/n*(1-k/n)/n + z*z/(4*n*n))/denominator
    return center-radius, center+radius


def spearman_rho(test):
    # SciPy 1.8 calls this field correlation; later versions call it statistic.
    return float(test.statistic if hasattr(test,'statistic') else test.correlation)


def compute():
    """Return flat numerical claims, plus tables; never read canonical values."""
    values, tables = {}, {}
    models = read_csv('analysis/inputs/per_model_comparison.csv')
    by_name = {r['model_name']:r for r in models}
    assert len(by_name) == len(models), 'Duplicate model identities'
    tables['compatibility'] = []
    for pop, source in [('p1','compatibility/compatibility_transition.csv'),
                        ('p2','compatibility/post_export_runtime_transition.csv')]:
        rows = read_csv(source)
        assert len({r['model_name'] for r in rows}) == len(rows)
        expected_ids = {r['model_name'] for r in models if pop=='p1' or truth(r['post_export_shared_eligible'])}
        assert {r['model_name'] for r in rows} == expected_ids
        counts = Counter()
        for r in rows:
            m=by_name[r['model_name']]
            a,b = int(m['a_valid_runs'])==6, int(m['b_valid_runs'])==6
            t = ('PASS' if a else 'FAIL')+' -> '+('PASS' if b else 'FAIL')
            assert r['transition']==t
            assert truth(m['a_repeat_stable_pass'])==a and truth(m['b_repeat_stable_pass'])==b
            counts[t]+=1
        n=len(rows); a=sum(v for k,v in counts.items() if k.startswith('PASS'));b=sum(v for k,v in counts.items() if k.endswith('PASS'))
        out={'n':n,'a_success':a,'b_success':b,'a_rate_percent':100*a/n,'b_rate_percent':100*b/n,
             'net_gain':b-a,'change_pp':100*(b-a)/n,
             'pp':counts['PASS -> PASS'],'fp':counts['FAIL -> PASS'],'pf':counts['PASS -> FAIL'],'ff':counts['FAIL -> FAIL']}
        out['mcnemar_p']=float(stats.binomtest(out['pf'],out['pf']+out['fp'],p=.5).pvalue)
        values.update({f'{pop}.{k}':v for k,v in out.items()})
        tables['compatibility'].append({'population':pop,**out})
    ae={r['model_name'] for r in models if truth(r['a_strict_runtime_eligible'])}
    be={r['model_name'] for r in models if truth(r['b_strict_runtime_eligible'])}
    for key,v in [('a',len(ae)),('b',len(be)),('common',len(ae&be)),('a_only',len(ae-be)),('b_only',len(be-ae))]:values['eligibility.'+key]=v
    for runtime in 'ab':
        values[f'compatibility.{runtime}.union']=sum(int(r[f'{runtime}_valid_runs'])>0 for r in models)
    paired=read_csv('timing/paired_latency_comparison.csv')
    assert {r['model_name'] for r in paired}=={r['model_name'] for r in models if int(r['a_valid_runs'])==int(r['b_valid_runs'])==6}
    values['timing.n']=len(paired);tables['timing']=[]
    for backend in ('cpu','gpu'):
        a=np.array([float(r[f'a_{backend}_ms']) for r in paired]);b=np.array([float(r[f'b_{backend}_ms']) for r in paired]);d=b-a
        for r in paired:
            m=by_name[r['model_name']]
            assert float(r[f'a_{backend}_ms'])==float(m[f'a_{backend}_mean_ms'])
            assert float(r[f'b_{backend}_ms'])==float(m[f'b_{backend}_mean_ms'])
            assert math.isclose(float(r[f'{backend}_difference_b_minus_a_ms']),float(r[f'b_{backend}_ms'])-float(r[f'a_{backend}_ms']),abs_tol=1e-12)
        # SciPy renamed mode to method. Both select the same automatic algorithm;
        # this changes API compatibility only, not data, formulas or tolerances.
        method_key='method' if 'method' in inspect.signature(stats.wilcoxon).parameters else 'mode'
        test=stats.wilcoxon(b,a,alternative='two-sided',zero_method='wilcox',**{method_key:'auto'})
        nonzero=d[d!=0];ranks=stats.rankdata(abs(nonzero));signed=(sum(ranks[nonzero>0])-sum(ranks[nonzero<0]))/sum(ranks)
        out={'a_median_ms':float(np.median(a)),'b_median_ms':float(np.median(b)),
             'difference_ms':float(np.median(d)),'ratio':float(np.median(b/a)),
             'b_faster':int(sum(b<a)),'b_faster_percent':100*int(sum(b<a))/len(a),
             'wilcoxon_p':float(test.pvalue),'rank_biserial':float(signed)}
        values.update({f'timing.{backend}.{k}':v for k,v in out.items()});tables['timing'].append({'backend':backend,**out})
    tables['architecture']=[]
    for reference in read_csv('architecture/architecture_comparison.csv'):
        flag=reference['flag'];members=[r for r in models if r['model_name'] in ae&be and truth(r[flag])]
        n=len(members);a=sum(int(r['a_valid_runs'])==6 for r in members);b=sum(int(r['b_valid_runs'])==6 for r in members)
        al,ah=wilson(a,n);bl,bh=wilson(b,n)
        row={'flag':flag,'n':n,'a_success':a,'b_success':b,'a_percent':100*a/n,'b_percent':100*b/n,
             'a_wilson_low_percent':100*al,'a_wilson_high_percent':100*ah,'b_wilson_low_percent':100*bl,'b_wilson_high_percent':100*bh,
             'change_pp':100*(b-a)/n,'recoveries':sum(int(r['a_valid_runs'])<6 and int(r['b_valid_runs'])==6 for r in members),
             'regressions':sum(int(r['a_valid_runs'])==6 and int(r['b_valid_runs'])<6 for r in members)}
        values.update({f'architecture.{flag}.{k}':v for k,v in row.items() if k!='flag'});tables['architecture'].append(row)
    repro=read_csv('reproducibility/per_model_reproducibility.csv');tables['reproducibility']=[]
    for runtime in 'AB':
        selected=[r for r in repro if r['runtime']==runtime]
        assert len(selected)==len(models)
        for r in selected:
            m=by_name[r['model_name']]
            for backend in ['cpu','gpu']:assert r[f'{backend}_cv']==m[f'{runtime.lower()}_{backend}_cv']
        for count in range(7):values[f'repro.{runtime}.success_runs.{count}']=sum(int(r['valid_runs'])==count for r in selected)
        for backend in ['cpu','gpu']:
            cv=[float(r[f'{backend}_cv']) for r in selected if r[f'{backend}_cv']!='']
            out={'n':len(cv),'median_percent':100*median(cv),'p95_percent':100*float(np.percentile(cv,95))}
            values.update({f'repro.{runtime}.{backend}.{k}':v for k,v in out.items()});tables['reproducibility'].append({'runtime':runtime,'backend':backend,**out})
    campaigns=read_csv('campaign_audit/campaign_audit.csv');tables['campaigns']=[]
    for r in campaigns:
        prefix=f'campaign.{r["runtime"]}{r["version"]}'
        keys=['records','valid_completed_benchmarks','export_success','export_failure','validation_failure','failure_runtime_load_execution','failure_timeout','missing_results','unexpected_results','corrupt_or_incomplete_files','duplicate_results','cleanup_failure']
        for key in keys:values[prefix+'.'+key]=campaign_count(r,key)
        rhs=sum(int(r[k]) for k in ['validation_failure','unity_success','failure_runtime_load_execution','timeout_or_skipped'])
        values[prefix+'.accounting_reconciles']=rhs==int(r['export_success'])
        assert int(r['export_failure'])+int(r['export_success'])==len(models)
        tables['campaigns'].append({'campaign':r['runtime']+r['version'],**{k:campaign_count(r,k) for k in keys}})
    failure_rows=read_csv('failures/failure_category_summary.csv');tables['failures']=[]
    categories={'export':'ONNX export','validation':'ONNX validation','runtime':'Runtime load/execution','timeout':'Timeout'}
    for runtime in 'AB':
        out={key:sum(int(r['record_failures']) for r in failure_rows if r['runtime']==runtime and r['category']==label) for key,label in categories.items()}
        for key,field in [('export','export_failure'),('validation','validation_failure'),('runtime','failure_runtime_load_execution'),('timeout','failure_timeout')]:assert out[key]==sum(campaign_count(r,field) for r in campaigns if r['runtime']==runtime)
        values.update({f'failures.{runtime}.{k}':v for k,v in out.items()});tables['failures'].append({'runtime':runtime,**out})
    tables['complexity']=[]
    for runtime in 'AB':
        selected=[r for r in models if r[f'{runtime.lower()}_cpu_mean_ms'] and all(r[k] for k in ['flops','total_params','total_layers'])]
        values[f'complexity.{runtime}.n']=len(selected)
        for backend in ['cpu','gpu']:
            for feature in ['flops','total_params','total_layers']:
                test=stats.spearmanr([float(r[feature]) for r in selected],[float(r[f'{runtime.lower()}_{backend}_mean_ms']) for r in selected])
                values[f'complexity.{runtime}.{backend}.{feature}.rho']=spearman_rho(test)
                tables['complexity'].append({'runtime':runtime,'backend':backend,'feature':feature,'n':len(selected),'rho':spearman_rho(test),'p_value':float(test.pvalue)})
    matched=read_csv('pt_context/matched_pt_a_b.csv');overlap=read_csv('pt_context/model_overlap.csv')
    assert {r['model_name'] for r in matched}=={r['model_name'] for r in overlap if truth(r['pt_a_b_identity_matched'])}
    values['pt.n']=len(matched);values['pt.shape_aligned']=sum(r['pt_input_shape_nhwc']==r['a_input_shape_nhwc'] for r in matched)
    values['pt.shape_mismatch']=len(matched)-values['pt.shape_aligned']
    tables['pt_context']=[]
    for backend in ['cpu','gpu']:
        p=np.array([float(r[f'pt_{backend}_ms']) for r in matched])
        out={'pt_median_ms':float(np.median(p))}
        ratio_arrays=[]
        for runtime in 'ab':
            u=np.array([float(r[f'{runtime}_{backend}_ms']) for r in matched]);ratios=u/p;ratio_arrays.append(ratios)
            out.update({f'{runtime}_median_ms':float(np.median(u)),f'{runtime}_ratio':float(np.median(ratios)),f'{runtime}_rho':spearman_rho(stats.spearmanr(p,u))})
            for r in matched:assert float(r[f'{runtime}_{backend}_ms'])==float(by_name[r['model_name']][f'{runtime}_{backend}_mean_ms'])
        if backend=='cpu':out['b_closer']=int(sum(abs(ratio_arrays[1]-1)<abs(ratio_arrays[0]-1)))
        values.update({f'pt.{backend}.{k}':v for k,v in out.items()});tables['pt_context'].append({'backend':backend,**out})
    historical=read_csv('provenance/historical_status.csv')
    values['historical.n']=len(historical)
    values['historical.exports']=sum(r['status']!='failed_export' for r in historical)
    values['historical.execution_completions']=sum(r['status']=='success' for r in historical)
    # Source-semantic checks are text audits; they do not execute C# or exporters.
    a=(ROOT/'provenance/runtime_source/Experiment_A_BenchmarkCLI.cs.txt').read_text()
    b=(ROOT/'provenance/runtime_source/Experiment_B_BenchmarkCLI.cs.txt').read_text()
    values['semantics.a_materializes']=all(x in a for x in ['warmupOutput.ToReadOnlyArray();','output.ToReadOnlyArray();'])
    values['semantics.b_materializes']=all(x in b for x in ['MaterializeOutput(worker, input, ref outputShape);','worker.Schedule(input);','output.DownloadToArray();'])
    return values,tables


def main():
    values,tables=compute()
    OUTPUT.mkdir(parents=True,exist_ok=True)
    (OUTPUT/'results.json').write_text(json.dumps(values,indent=2,sort_keys=True)+'\n')
    markdown=['# Reproduced paper tables','','Derived only from packaged retained evidence. No new experiment.']
    for name,rows in tables.items():
        fields=list(rows[0])
        with (OUTPUT/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:
            writer=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');writer.writeheader();writer.writerows(rows)
        markdown+=['',f'## {name}','', '| '+' | '.join(fields)+' |','|'+'|'.join(['---']*len(fields))+'|']
        markdown += ['| '+' | '.join(format(r.get(k),'.10g') if isinstance(r.get(k),float) else str(r.get(k,'')) for k in fields)+' |' for r in rows]
    (OUTPUT/'paper_tables.md').write_text('\n'.join(markdown)+'\n')
    print(f'Reproduced {len(values)} numerical/semantic fields into analysis/reproduced_outputs/')


if __name__=='__main__':main()
