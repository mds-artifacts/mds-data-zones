# Data and scripts for "Data-Aware Misinformation Detection Systems"

This repository contains the data extraction spreadsheet for the 136 primary studies analysed in the paper,
and the Python scripts that produce its four figures.

## Contents

| Path | What it is |
|---|---|
| `data/extraction_data.xlsx` | Extraction spreadsheet: for each primary study, its detection approach, model class, data used (data zone), domain, and reported strengths and limitations |
| `scripts/make_figures.py` | Runs all four figure scripts |
| `scripts/approaches_donut_minimal.py` | Fig. 1 - detection approaches and their combinations |
| `scripts/approach_models_minimal.py` | Fig. 2 - detection approach x model class |
| `scripts/zones_minimal.py` | Fig. 3 - data zones by domain |
| `scripts/agenda_architecture_small.py` | Fig. 4 - architecture of a data-aware MDS (diagram) |
| `scripts/normalise.py`, `scripts/load_extractions.py` | Read and code the extraction sheets |
| `scripts/model_classes.py` | Rule that places each study at its most advanced model class |
| `scripts/config.py`, `scripts/plotstyle.py`, `scripts/palette_cyan.py` | Paths, figure style and colours |

## Reproduce the figures

```
pip install -r requirements.txt
python scripts/make_figures.py
```

Figures are written to `output/figures/` (PDF, PNG and SVG); the counts behind each figure are written to
`output/tables/`.

