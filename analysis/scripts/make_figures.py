"""
Re-create the four figures of the paper from the extraction spreadsheet:

    python scripts/make_figures.py                      # uses data/SLR_extractions.xlsx
    python scripts/make_figures.py path/to/file.xlsx    # or another copy of the spreadsheet

  Fig. 1  approaches_donut_minimal.py   detection approaches and their combinations
  Fig. 2  approach_models_minimal.py    detection approach x model class
  Fig. 3  zones_minimal.py              data zones and domains
  Fig. 4  agenda_architecture_small.py  architecture of a data-aware MDS (diagram, no data needed)

Figures are written to output/figures/ (PDF, PNG, SVG); supporting tables to output/tables/.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C  # noqa: E402

C.use_workbook_arg()
import approaches_donut_minimal, approach_models_minimal, zones_minimal, agenda_architecture_small  # noqa: E402

for name, mod in [("Fig. 1 detection approaches", approaches_donut_minimal),
                  ("Fig. 2 approach x model class", approach_models_minimal),
                  ("Fig. 3 data zones by domain", zones_minimal),
                  ("Fig. 4 data-aware MDS architecture", agenda_architecture_small)]:
    print(name)
    mod.main()
