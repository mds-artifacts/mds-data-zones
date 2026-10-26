"""
Readable black-and-white matrix: which model classes each detection approach uses.
New model classes are added over time; older approaches (e.g. style-based) keep being used with them.

    python scripts/approach_models_minimal.py ["path/to/workbook.xlsx"]

Rows    = detection approach (a study can use several approaches -> counted in each)
Columns = model class: ML, deep learning, LLM, LLM agents (agentic LLMs counted as LLM agents);
          each study placed at its most advanced model, same rule as the evolution figures
Circle  = number of studies (area ~ count); black = the model class used most for that approach

Output: output/figures/fig_approach_models_minimal.[pdf,svg,png]
        output/tables/approach_models.xlsx  (counts, row %, PS# per cell)
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import config as C
import plotstyle as P
from model_classes import eras
from normalise import load_clean

APPROACHES = ["Style-based", "Knowledge-based", "Social-context", "Source-based", "Propagation-based"]
MODELS = ["Feature eng. + classical ML", "Deep learning", "LLMs", "LLM agents"]   # agentic LLMs merged into LLM agents
HEAD = {"Feature eng. + classical ML": "ML", "Deep learning": "Deep learning", "LLMs": "LLM",
        "LLM agents": "LLM agents"}
import palette_cyan as PC
INK, INK2, RULE = PC.INK, PC.INK, PC.RULE          # one text colour throughout


def main():
    P.setup()
    df = eras(load_clean())
    df["era"] = df["era"].replace({"Agentic LLMs": "LLM agents"})
    fs = 10.5                                   # large: readable when placed full-width in a 2-column paper
    long = df.explode("approach_set").reset_index(drop=True)
    long = long[long.approach_set.isin(APPROACHES)]
    ct = pd.crosstab(long.approach_set, long.era).reindex(index=APPROACHES, columns=MODELS, fill_value=0)
    n_app = ct.sum(axis=1)

    W, H = C.DOUBLE_COL, 3.3
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")

    x0 = 1.75
    cw = (W - x0 - 0.15) / len(MODELS)
    xs = [x0 + (i + 0.5) * cw for i in range(len(MODELS))]
    ytop, rh = H - 0.5, 0.53

    # column headers
    for x, m in zip(xs, MODELS):
        ax.text(x, H - 0.2, HEAD[m], ha="center", va="center", fontsize=fs, fontweight="bold", color=INK)

    vmax = ct.values.max()
    for r, a in enumerate(APPROACHES):
        y = ytop - (r + 0.5) * rh
        ax.plot([x0, W - 0.15], [y, y], color=RULE, lw=0.8, zorder=0)
        ax.text(x0 - 0.12, y + 0.1, a, ha="right", va="center", fontsize=fs, fontweight="bold", color=INK)
        ax.text(x0 - 0.12, y - 0.15, f"{int(n_app[a])} studies", ha="right", va="center", fontsize=fs,
                color=INK)
        top = ct.loc[a].max()
        for x, m in zip(xs, MODELS):
            k = int(ct.loc[a, m])
            if not k:
                continue
            rad = 0.08 + 0.17 * np.sqrt(k / vmax)
            best = k == top
            ax.add_patch(plt.Circle((x, y), rad, fc=PC.DARK if best else PC.SOFT, ec=PC.EDGE, lw=0.6,
                                    zorder=2))
            ax.text(x, y, f"{k}", ha="center", va="center", fontsize=fs, fontweight="bold",
                    color=INK, zorder=3)

    P.save(fig, "fig_approach_models_minimal")

    pct = ct.div(n_app, axis=0).mul(100).round(1)
    ps = long.groupby(["approach_set", "era"]).ps_id.apply(lambda s: ", ".join(s.map(str))).unstack() \
        .reindex(index=APPROACHES, columns=MODELS)
    with pd.ExcelWriter(C.TAB_DIR / "approach_models.xlsx", engine="openpyxl") as xw:
        ct.assign(Total=n_app).to_excel(xw, sheet_name="counts")
        pct.to_excel(xw, sheet_name="row %")
        ps.to_excel(xw, sheet_name="PS# per cell")
    print("  saved tables/approach_models.xlsx")
    print(ct.to_string())


if __name__ == "__main__":
    C.use_workbook_arg()
    main()
