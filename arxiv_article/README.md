# arXiv / Overleaf source

Upload this directory as a ZIP to Overleaf, then compile `main.tex` with pdfLaTeX and BibTeX. The article uses standard Overleaf packages only; its five figures are native TikZ/PGFPlots source in `figures.tex`.

Figure values trace to committed aggregate artifacts through `stats/reproduce_article_claims.py` in the repository root. Before submission, run:

```bash
python stats/reproduce_article_claims.py
```

The draft reports GPU measurements only as dispatch-window observations. It makes no claim of numerical parity, synchronized GPU latency, VR-headset performance, causal failure mechanisms, or a portable Unity overhead multiplier.
