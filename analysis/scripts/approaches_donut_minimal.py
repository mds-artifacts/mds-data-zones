"""
Minimal black-and-white donut: how detection approaches are shared across studies.

    python scripts/approaches_donut_minimal.py ["path/to/workbook.xlsx"]

Inner ring = single approach vs shared (two or more approaches).
Outer ring = the exact combinations; small ones (< MIN_SLICE studies) are grouped as "Other combinations".

Output: output/figures/fig_approaches_donut_minimal.[pdf,svg,png]
        output/tables/approaches_donut.xlsx  (every combination, count, PS#, and which slice it is in)
"""
import collections

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import config as C
import plotstyle as P
from normalise import load_clean

APPROACHES = ["Style-based", "Knowledge-based", "Social-context", "Source-based", "Propagation-based"]
SHORT = {"Style-based": "Style", "Knowledge-based": "Knowledge", "Social-context": "Social context",
         "Source-based": "Source", "Propagation-based": "Propagation"}
MIN_SLICE = 6
import palette_cyan as PC
INK, INK2 = PC.INK, PC.EDGE                         # leader lines use the outline grey
SINGLE_SHADES = [PC.MID, PC.LIGHT]                   # single approaches: the shared greys (Style only, Knowledge only)
SHARED_SHADES = [PC.DARK, PC.DARK]                   # shared approaches: one colour, cyan!8 (same as inner ring)
WEDGE = dict(edgecolor=PC.EDGE, linewidth=0.6)


def name(c):
    return SHORT[c[0]] + " only" if len(c) == 1 else " + ".join(SHORT[a] for a in c)


def main():
    P.setup()
    df = load_clean()
    fs = 10.5                                   # large: readable full-width in a 2-column paper
    N = len(df)
    combo = df.approach_set.map(lambda v: tuple(a for a in APPROACHES if a in v))
    counts = collections.Counter(c for c in combo if c)
    single = sorted([c for c in counts if len(c) == 1], key=lambda c: -counts[c])
    shared = sorted([c for c in counts if len(c) > 1], key=lambda c: -counts[c])
    big_shared = [c for c in shared if counts[c] >= MIN_SLICE]
    small_shared = [c for c in shared if counts[c] < MIN_SLICE]
    big_single = [c for c in single if counts[c] >= MIN_SLICE]
    small_single = [c for c in single if counts[c] < MIN_SLICE]

    slices = []                                  # (label, value, colour, is_shared)
    for i, c in enumerate(big_single):
        slices.append((name(c), counts[c], SINGLE_SHADES[i % 2], False))
    if small_single:
        slices.append(("Other single approaches", sum(counts[c] for c in small_single), PC.WHITE, False))
    for i, c in enumerate(big_shared):
        slices.append((name(c), counts[c], SHARED_SHADES[i % 2], True))
    if small_shared:
        slices.append((f"Other combinations ({len(small_shared)} kinds)", sum(counts[c] for c in small_shared),
                       SHARED_SHADES[len(big_shared) % 2], True))
    n_single = sum(counts[c] for c in single)
    n_shared = sum(counts[c] for c in shared)

    fig, ax = plt.subplots(figsize=(C.DOUBLE_COL, 3.6))     # title/legend text goes in the caption
    fig.subplots_adjust(left=0.3, right=0.7, top=0.93, bottom=0.07)
    kw = dict(startangle=90, counterclock=False, wedgeprops=dict(edgecolor="white", linewidth=1.4))
    vals = [s[1] for s in slices]
    wedges, _ = ax.pie(vals, radius=1.0, colors=[s[2] for s in slices],
                       wedgeprops=dict(width=0.3, **WEDGE), startangle=90,
                       counterclock=False)
    inner, _ = ax.pie([n_single, n_shared], radius=0.66, colors=[PC.MID, PC.DARK],
                      wedgeprops=dict(width=0.16, **WEDGE), startangle=90,
                      counterclock=False)
    # centre: the inner-ring split
    ax.text(0, 0.1, f"{n_shared}", ha="center", va="center", fontsize=fs + 10, fontweight="bold", color=INK)
    ax.text(0, -0.13, f"shared ({n_shared / N:.0%})", ha="center", va="center", fontsize=fs, color=INK)

    # outer labels with leader lines, spaced per side so they never overlap
    items = []
    for w, (lab, v, col, sh) in zip(wedges, slices):
        ang = np.deg2rad((w.theta1 + w.theta2) / 2)
        items.append((ang, lab, v, sh))
    for side in (1, -1):
        pts = sorted([it for it in items if np.sign(np.cos(it[0]) or 1) == side], key=lambda it: -np.sin(it[0]))
        last = None
        for ang, lab, v, sh in pts:
            x0, y0 = np.cos(ang), np.sin(ang)
            ty = 1.22 * y0
            if last is not None and ty > last - 0.27:
                ty = last - 0.27
            last = ty
            tx = side * 1.25
            ax.annotate(f"{lab}  {v} ({v / N:.0%})", xy=(x0 * 1.0, y0 * 1.0), xytext=(tx, ty),
                        ha="left" if side > 0 else "right", va="center", fontsize=fs,
                        fontweight="bold" if sh else "normal", color=INK,
                        arrowprops=dict(arrowstyle="-", color=INK2, lw=0.7,
                                        connectionstyle="angle,angleA=0,angleB=90,rad=0"))
    ax.set_aspect("equal")
    P.save(fig, "fig_approaches_donut_minimal")

    big = set(big_single) | set(big_shared)
    rows = []
    for c in single + shared:
        slice_name = name(c) if c in big else ("Other single approaches" if len(c) == 1 else "Other combinations")
        rows.append([" + ".join(c), len(c), counts[c], round(100 * counts[c] / N, 1), slice_name,
                     ", ".join(df[combo == c].ps_id.map(str))])
    pd.DataFrame(rows, columns=["Combination", "No. of approaches", "Studies", "%", "Donut slice", "PS#"]) \
        .to_excel(C.TAB_DIR / "approaches_donut.xlsx", index=False)
    print("  saved tables/approaches_donut.xlsx")


if __name__ == "__main__":
    C.use_workbook_arg()
    main()
