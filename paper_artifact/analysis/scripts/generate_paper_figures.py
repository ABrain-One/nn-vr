#!/usr/bin/env python3
"""Render existing Figure 3-6 evidence offline, without model/runtime execution.

Data-equivalent presentation reproductions; original V3.2 TikZ source is retained
in provenance/manuscript/figures.tex for exact layout inspection. Figure 5 adapts
the authors' original V3.1 scatter rendering formulas. No new scientific analysis.
"""
import csv
import math
import os
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUTPUT=ROOT/'analysis/reproduced_outputs'
# Keep any plotting cache external to release inputs; no network or downloads.
os.environ.setdefault('MPLCONFIGDIR', '/tmp/nnvr-artifact-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.text import Text
import numpy as np


def rows(path):
    with (ROOT/path).open() as stream:return list(csv.DictReader(stream))


def save(fig,name):
    # Pin Matplotlib's own fonts by file, avoiding nondeterministic selection of
    # installed Latin Modern optical sizes when the font cache is rebuilt.
    fonts=Path(matplotlib.get_data_path())/'fonts/ttf'
    for artist in fig.findobj(Text):
        bold=artist.get_fontweight() in ('bold','heavy',700,800,900)
        artist.set_fontproperties(FontProperties(fname=str(fonts/('DejaVuSerif-Bold.ttf' if bold else 'DejaVuSerif.ttf')),size=artist.get_fontsize()))
    fig.savefig(OUTPUT/name,bbox_inches='tight',metadata={'CreationDate':None,'ModDate':None})
    plt.close(fig)


def main():
    if not (OUTPUT/'compatibility.csv').exists():
        raise SystemExit('Run reproduce_paper_results.py first.')
    plt.rcParams.update({'font.size':8,'font.family':'DejaVu Serif','mathtext.fontset':'dejavuserif','pdf.fonttype':42,'ps.fonttype':42})
    # Figure 3: retain exact matrix counts, rows A and columns B.
    fig,axes=plt.subplots(1,2,figsize=(7,2.6),constrained_layout=True)
    for ax,r in zip(axes,rows('analysis/reproduced_outputs/compatibility.csv')):
        data=np.array([[int(r['pp']),int(r['pf'])],[int(r['fp']),int(r['ff'])]])
        ax.imshow(data,cmap='Blues',aspect='auto',vmin=0,vmax=1100)
        for i in range(2):
            for j in range(2):ax.text(j,i,str(data[i,j]),ha='center',va='center',fontsize=12,color='white' if data[i,j]>700 else 'black')
        ax.set_xticks([0,1],['Sentis PASS','Sentis FAIL']);ax.set_yticks([0,1],['Barracuda PASS','Barracuda FAIL'])
        ax.set_title(r['population'].upper()+f" (n={r['n']})")
    save(fig,'figure3_transitions.pdf')
    # Figure 4: exact retained endpoints, never ambiguous asymmetric error bars.
    architecture={r['label']:r for r in rows('architecture/architecture_comparison.csv')}
    labels=['MobileNet-like','Residual connections','Transformer-like','ResNet-like']
    fig,ax=plt.subplots(figsize=(6.5,3.2),constrained_layout=True)
    for i,label in enumerate(labels):
        r=architecture[label]
        for runtime,offset,color in [('a',.13,'#cd7829'),('b',-.13,'#2f7b5d')]:
            y=i+offset;point=100*float(r[f'{runtime}_success_rate']);low=100*float(r[f'{runtime}_wilson_low']);high=100*float(r[f'{runtime}_wilson_high'])
            ax.plot([low,high],[y,y],color=color);ax.plot([low,high],[y,y],'|',color=color);ax.plot(point,y,'o',color=color,markersize=4,label=('Barracuda' if runtime=='a' else 'Sentis 2.6.1') if i==0 else None)
    ax.set_yticks(range(4),[f"{label} (n={architecture[label]['population']})" for label in labels]);ax.set_xlim(45,102);ax.set_xlabel('Strict runtime success (%)');ax.legend();ax.grid(axis='x',alpha=.2)
    save(fig,'figure4_architecture.pdf')
    # Figure 5: same points, log axes, extents, aspect and styling as original helper.
    paired=rows('timing/paired_latency_comparison.csv')
    fig,axes=plt.subplots(1,2,figsize=(7,3.25),constrained_layout=True)
    for ax,backend in zip(axes,['cpu','gpu']):
        x=[float(r[f'a_{backend}_ms']) for r in paired];y=[float(r[f'b_{backend}_ms']) for r in paired]
        lower=10**(math.floor(math.log10(min(x+y)))-1);upper=10**(math.ceil(math.log10(max(x+y)))+1)
        ax.scatter(x,y,s=8,c='#2f7b5d',alpha=.24,linewidths=0);ax.plot([lower,upper],[lower,upper],color='#535f6e',lw=1,ls='--',label='y = x')
        ax.set_xscale('log');ax.set_yscale('log');ax.set_xlim(lower,upper);ax.set_ylim(lower,upper);ax.set_aspect('equal',adjustable='box');ax.grid(True,which='both',color='#d8dce1',lw=.4)
        ax.set_title(f'{backend.upper()} (n={len(paired):,})',fontweight='bold');ax.set_xlabel('Barracuda per-model campaign mean (ms)');ax.set_ylabel('Sentis per-model campaign mean (ms)');ax.legend(loc='upper left',frameon=False,handlelength=2)
    save(fig,'figure5_paired_latency.pdf')
    # Figure 6: published two-decimal presentation of independently aggregated CVs.
    repro={(r['runtime'],r['backend']):r for r in rows('analysis/reproduced_outputs/reproducibility.csv')}
    fig,ax=plt.subplots(figsize=(5.5,3),constrained_layout=True)
    for runtime,offset,color in [('A',-.18,'#cd7829'),('B',.18,'#2f7b5d')]:
        vals=[round(float(repro[(runtime,backend)][key]),2) for backend in ['cpu','gpu'] for key in ['median_percent','p95_percent']]
        bars=ax.bar(np.arange(4)+offset,vals,.36,color=color,label='Barracuda' if runtime=='A' else 'Sentis 2.6.1');ax.bar_label(bars,labels=[f'{v:.2f}' for v in vals],fontsize=7,padding=2)
    ax.set_xticks(range(4),['CPU median','CPU p95','GPU median','GPU p95']);ax.set_ylim(0,95);ax.set_ylabel('Cross-runtime-campaign CV (%)');ax.legend()
    save(fig,'figure6_reproducibility.pdf')
    print('Rendered Figure 3-6 evidence into analysis/reproduced_outputs/')


if __name__=='__main__':main()
