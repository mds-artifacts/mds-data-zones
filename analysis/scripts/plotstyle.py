"""
Shared, publication-quality figure style + reusable chart builders.

Design rules applied everywhere:
  * one sans typeface (Inter if installed), 7-9 pt, sized to journal columns
  * recessive axes: no top/right spines, light value grid, no chart junk
  * colour follows the entity (config.COLOR) - never re-coloured per figure
  * every bar carries its value, so identity/magnitude never rely on colour alone
  * saved as vector PDF + SVG (for LaTeX/Word) and 400-dpi PNG
"""
from __future__ import annotations

import textwrap

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import PathPatch
from matplotlib.path import Path as MPath

import config as C


def setup():
    from matplotlib import font_manager
    available = {f.name for f in font_manager.fontManager.ttflist}
    family = next((f for f in C.FONT_FAMILY if f in available), "DejaVu Sans")
    fs = C.BASE_FONT_SIZE
    mpl.rcParams.update({
        "font.family": family, "font.size": fs,
        "axes.titlesize": fs + 1, "axes.titleweight": "semibold", "axes.titlelocation": "left",
        "axes.titlepad": 8, "axes.labelsize": fs, "axes.labelcolor": C.INK_2,
        "xtick.labelsize": fs - 0.5, "ytick.labelsize": fs - 0.5,
        "xtick.color": C.INK_2, "ytick.color": C.INK, "axes.edgecolor": C.INK_3,
        "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0,
        "xtick.major.size": 2.5, "ytick.major.size": 0,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": False, "grid.color": C.GRID, "grid.linewidth": 0.6,
        "legend.fontsize": fs - 0.5, "legend.frameon": False, "legend.handlelength": 1.0,
        "legend.handleheight": 0.8, "legend.borderaxespad": 0.2,
        "figure.facecolor": C.SURFACE, "axes.facecolor": C.SURFACE, "savefig.facecolor": C.SURFACE,
        "savefig.bbox": "tight", "savefig.pad_inches": 0.04,
        "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none",   # editable text
    })
    return family


def save(fig, name: str):
    for ext in C.SAVE_FORMATS:
        kw = {"dpi": C.PNG_DPI} if ext == "png" else {}
        fig.savefig(C.FIG_DIR / f"{name}.{ext}", **kw)
    plt.close(fig)
    print(f"  saved figures/{name}.[{','.join(C.SAVE_FORMATS)}]")


def pair(height, ratios=None, gap=0.35):
    """Two panels stacked vertically at full page width, so labels can be large (replaces 1 x 2 side by side)."""
    fig, (a, b) = plt.subplots(2, 1, figsize=(C.DOUBLE_COL, 2 * height + gap))
    return fig, (a, b)


def wrap(s: str, width: int = 28) -> str:
    return "\n".join("\n".join(textwrap.wrap(line, width, break_long_words=False)) or line
                     for line in str(s).split("\n"))


def panel_label(ax, letter: str, title: str | None = None):
    """Bold (a) panel letter + title, left-aligned above the axes."""
    t = f"({letter})" + (f"  {title}" if title else "")
    ax.set_title(t, loc="left", fontweight="semibold", color=C.INK)


def value_grid(ax, axis="x"):
    ax.grid(axis=axis, color=C.GRID, linewidth=0.6)
    ax.set_axisbelow(True)


def color_of(label, default=None):
    return C.COLOR.get(label, default or C.CATEGORICAL[0])


# ----------------------------------------------------------------------------
# Horizontal bar with "n (x%)" labels
# ----------------------------------------------------------------------------
def hbar(ax, labels, values, total, colors=None, wrap_at=46, show_pct=True, xlabel="Studies"):
    labels = list(labels)[::-1]
    values = np.asarray(list(values))[::-1]
    if colors is None:
        colors = [C.CATEGORICAL[0]] * len(values)
    else:
        colors = list(colors)[::-1]
    y = np.arange(len(values))
    ax.barh(y, values, height=0.66, color=colors, edgecolor=C.SURFACE, linewidth=0.8, zorder=2)
    ax.set_yticks(y, [wrap(l, max(wrap_at, 44)) for l in labels])
    vmax = values.max() if len(values) else 1
    for yi, v in zip(y, values):
        txt = f"{int(v)}" + (f" ({100 * v / total:.0f}%)" if show_pct and total else "")
        ax.text(v + vmax * 0.015, yi, txt, va="center", ha="left", fontsize=C.BASE_FONT_SIZE - 1,
                color=C.INK_2)
    ax.set_xlim(0, vmax * 1.28)
    ax.set_ylim(-0.6, len(values) - 0.4)
    ax.set_xlabel(xlabel)
    ax.spines["left"].set_visible(False)
    value_grid(ax, "x")
    return ax


def lollipop(ax, labels, values, total, colors=None, wrap_at=46, xlabel="Studies (%)", pct=True):
    labels = list(labels)[::-1]
    vals = np.asarray(list(values), dtype=float)[::-1]
    show = 100 * vals / total if pct else vals
    colors = (list(colors)[::-1] if colors is not None else [C.CATEGORICAL[0]] * len(vals))
    y = np.arange(len(vals))
    ax.hlines(y, 0, show, color=colors, linewidth=1.6, zorder=2)
    ax.scatter(show, y, s=26, color=colors, edgecolor=C.SURFACE, linewidth=1.0, zorder=3)
    for yi, s, v in zip(y, show, vals):
        ax.text(s + show.max() * 0.03, yi, f"{s:.0f}%" if pct else f"{int(v)}", va="center",
                fontsize=C.BASE_FONT_SIZE - 1, color=C.INK_2)
    ax.set_yticks(y, [wrap(l, max(wrap_at, 44)) for l in labels])
    ax.set_xlim(0, show.max() * 1.22)
    ax.set_ylim(-0.6, len(vals) - 0.4)
    ax.set_xlabel(xlabel)
    ax.spines["left"].set_visible(False)
    value_grid(ax, "x")


# ----------------------------------------------------------------------------
# Heatmap (sequential, one hue) with readable cell annotations
# ----------------------------------------------------------------------------
SEQ_CMAP = LinearSegmentedColormap.from_list("seq_blue", C.SEQUENTIAL)


def heatmap(ax, M, row_labels, col_labels, fmt="{:.0f}", vmax=None, annot=None, cbar_label=None,
            wrap_rows=46, wrap_cols=14, rotate_cols=30, mask_zero=True):
    M = np.asarray(M, dtype=float)
    vmax = vmax or (np.nanmax(M) if np.nanmax(M) > 0 else 1)
    show = np.where((M == 0) & mask_zero, np.nan, M)
    im = ax.imshow(show, cmap=SEQ_CMAP, vmin=0, vmax=vmax, aspect="auto", interpolation="nearest")
    ax.set_facecolor("#f7f6f3")
    rotate_cols = rotate_cols or (30 if max(len(str(c).split("\n")[0]) for c in col_labels) > 7 else 0)
    ax.set_xticks(range(len(col_labels)), [wrap(c, max(wrap_cols, 18)) for c in col_labels],
                  rotation=rotate_cols, ha="right" if rotate_cols else "center",
                  rotation_mode="anchor")
    ax.set_yticks(range(len(row_labels)), [wrap(r, max(wrap_rows, 44)) for r in row_labels])
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    # white cell gaps
    ax.set_xticks(np.arange(-.5, len(col_labels), 1), minor=True)
    ax.set_yticks(np.arange(-.5, len(row_labels), 1), minor=True)
    ax.grid(which="minor", color=C.SURFACE, linewidth=1.6)
    ax.tick_params(which="minor", length=0)
    A = M if annot is None else annot
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            if mask_zero and M[i, j] == 0:
                continue
            dark = M[i, j] / vmax > 0.55
            ax.text(j, i, fmt.format(A[i, j]), ha="center", va="center",
                    fontsize=C.BASE_FONT_SIZE - 1.2, color="white" if dark else C.INK)
    if cbar_label:
        cb = plt.colorbar(im, ax=ax, fraction=0.035, pad=0.02)
        cb.outline.set_visible(False)
        cb.ax.tick_params(labelsize=C.BASE_FONT_SIZE - 1.5, length=2, width=0.5)
        cb.set_label(cbar_label, fontsize=C.BASE_FONT_SIZE - 1, color=C.INK_2)
    return im


# ----------------------------------------------------------------------------
# UpSet plot (set intersections) - the modern replacement for Venn diagrams
# ----------------------------------------------------------------------------
def upset(fig, membership: list[list[str]], sets: list[str], max_bars=12, min_size=1,
          set_colors=None, title=None):
    """UpSet plot: bars = studies with exactly that combination; dots = which sets.
    Set totals are printed in the row labels, so no separate set-size panel is needed."""
    from collections import Counter
    combos = Counter(tuple(s for s in sets if s in m) for m in membership if m)
    combos = [(k, v) for k, v in combos.most_common() if v >= min_size and k][:max_bars]
    set_sizes = [sum(1 for m in membership if s in m) for s in sets]
    gs = fig.add_gridspec(2, 1, height_ratios=[2.0, 1.15], hspace=0.05)
    ax_bar = fig.add_subplot(gs[0])
    ax_mat = fig.add_subplot(gs[1], sharex=ax_bar)
    x = np.arange(len(combos))
    vals = [v for _, v in combos]
    ax_bar.bar(x, vals, width=0.6, color=C.INK_2, zorder=2)
    for xi, v in zip(x, vals):
        ax_bar.text(xi, v + max(vals) * 0.02, str(v), ha="center", va="bottom",
                    fontsize=C.BASE_FONT_SIZE - 1.2, color=C.INK_2)
    ax_bar.set_ylabel("Studies with exactly\nthis combination")
    ax_bar.tick_params(axis="x", length=0, labelbottom=False)
    ax_bar.spines["bottom"].set_visible(False)
    value_grid(ax_bar, "y")
    ax_bar.set_ylim(0, max(vals) * 1.15)
    if title:
        ax_bar.set_title(title, loc="left")
    ny = len(sets)
    for i in range(ny):
        if i % 2 == 0:
            ax_mat.axhspan(i - 0.5, i + 0.5, color="#f4f3ef", zorder=0, linewidth=0)
    for xi, (k, _) in enumerate(combos):
        on = [sets.index(s) for s in k]
        ax_mat.scatter([xi] * ny, range(ny), s=20, color="#dcdbd6", zorder=1, linewidth=0)
        if len(on) > 1:
            ax_mat.vlines(xi, min(on), max(on), color=C.INK, linewidth=1.2, zorder=2)
        cols = [(set_colors or {}).get(sets[i], C.INK) for i in on]
        ax_mat.scatter([xi] * len(on), on, s=28, color=cols, zorder=3, edgecolor=C.INK, linewidth=0.4)
    ax_mat.set_ylim(ny - 0.5, -0.5)
    ax_mat.set_yticks(range(ny), [f"{s}  ({n})" for s, n in zip(sets, set_sizes)])
    ax_mat.tick_params(axis="both", length=0)
    ax_mat.tick_params(axis="x", labelbottom=False)
    for s in ax_mat.spines.values():
        s.set_visible(False)
    ax_mat.set_xlim(-0.6, len(combos) - 0.4)
    return ax_bar, ax_mat


# ----------------------------------------------------------------------------
# Alluvial / Sankey across ordered stages
# ----------------------------------------------------------------------------
def alluvial(ax, df, stages: list[str], stage_titles: list[str], orders: dict, gap=0.025, width=0.05):
    n = len(df)
    xs = np.linspace(0, 1, len(stages))
    pos = {}  # (stage, category) -> [y0, y1]
    for si, st in enumerate(stages):
        cats = [c for c in orders[st] if (df[st] == c).any()]
        total_gap = gap * (len(cats) - 1)
        y = 0.0
        for c in cats:
            h = (df[st] == c).sum() / n * (1 - total_gap)
            pos[(st, c)] = [y, y + h]
            y += h + gap
    # flows
    for si in range(len(stages) - 1):
        a, b = stages[si], stages[si + 1]
        out_cursor = {c: pos[(a, c)][0] for c in orders[a] if (a, c) in pos}
        in_cursor = {c: pos[(b, c)][0] for c in orders[b] if (b, c) in pos}
        flows = df.groupby([a, b]).size()
        for ca in orders[a]:
            for cb in orders[b]:
                if (ca, cb) not in flows.index:
                    continue
                h = flows[(ca, cb)] / n * (1 - gap * (len([c for c in orders[a] if (a, c) in pos]) - 1))
                y0a, y0b = out_cursor[ca], in_cursor[cb]
                out_cursor[ca] += h
                in_cursor[cb] += h
                x0, x1 = xs[si] + width / 2, xs[si + 1] - width / 2
                xm = (x0 + x1) / 2
                verts = [(x0, y0a), (xm, y0a), (xm, y0b), (x1, y0b), (x1, y0b + h), (xm, y0b + h),
                         (xm, y0a + h), (x0, y0a + h), (x0, y0a)]
                codes_ = [MPath.MOVETO, MPath.CURVE4, MPath.CURVE4, MPath.CURVE4, MPath.LINETO,
                          MPath.CURVE4, MPath.CURVE4, MPath.CURVE4, MPath.CLOSEPOLY]
                ax.add_patch(PathPatch(MPath(verts, codes_), facecolor=color_of(ca, C.NEUTRAL),
                                       alpha=0.38, edgecolor="none", zorder=1))
    # nodes + labels (labels pushed apart so small nodes never collide)
    min_gap = 0.075
    for si, st in enumerate(stages):
        items = []
        for c in orders[st]:
            if (st, c) not in pos:
                continue
            y0, y1 = pos[(st, c)]
            ax.add_patch(mpl.patches.Rectangle((xs[si] - width / 2, y0), width, y1 - y0,
                                               facecolor=color_of(c, C.NEUTRAL), edgecolor=C.SURFACE,
                                               linewidth=0.8, zorder=2))
            items.append([c, (y0 + y1) / 2, (df[st] == c).sum(), y1 - y0])
        ys = [it[1] for it in items]
        for i in range(1, len(ys)):                 # push down
            ys[i] = max(ys[i], ys[i - 1] + min_gap)
        over = ys[-1] - 0.98 if ys else 0
        if over > 0:                                # shift block up if it ran off the bottom
            ys = [y - over for y in ys]
            for i in range(len(ys) - 2, -1, -1):
                ys[i] = min(ys[i], ys[i + 1] - min_gap)
        for (c, yc, k, h), yl in zip(items, ys):
            left = si == 0
            ha, dx = ("right", -width / 2 - 0.014) if left else ("left", width / 2 + 0.014)
            big = h > 0.12
            txt = f"{c}\n{k} ({100 * k / n:.0f}%)" if big else f"{c}  {k} ({100 * k / n:.0f}%)"
            ax.text(xs[si] + dx, yl, txt, ha=ha, va="center", fontsize=C.BASE_FONT_SIZE - 1, color=C.INK,
                    linespacing=1.1, zorder=4,
                    bbox=dict(boxstyle="round,pad=0.15", fc=C.SURFACE, ec="none", alpha=0.85) if 0 < si else None)
            if abs(yl - yc) > h / 2:
                x_edge = xs[si] + (-width / 2 if left else width / 2)
                ax.plot([x_edge, xs[si] + dx * 0.8], [yc, yl], color=C.INK_3, lw=0.5, zorder=3)
        ax.text(xs[si], -0.06, stage_titles[si], ha="center", va="bottom", fontweight="semibold",
                fontsize=C.BASE_FONT_SIZE, color=C.INK)
    ax.set_xlim(-0.32, 1.32)
    ax.set_ylim(1.02, -0.1)
    ax.axis("off")
