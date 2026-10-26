"""
Small architecture figure for the research agenda (RD1): a data-aware MDS.

    python scripts/agenda_architecture_small.py

Flow (left to right): claim -> domain identification -> zone identification (reads the evidence store)
-> orchestration layer -> detection modules -> zone-based decision
   verified -> verdict, partially verified -> explainable clues, unverified -> human verification.
Human verification feeds verdicts back into the evidence store (claims move into the verified zone).
A bottom bar lists the cross-cutting concerns from the other directions (RD2-RD6).

Black and white, one text colour, sized for full page width in a two-column paper.
Output: output/figures/fig_agenda_architecture_small.[pdf,svg,png]
"""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

import config as C
import plotstyle as P

import palette_cyan as PC

INK = PC.INK
EDGE = PC.EDGE
LIGHT, MID, DARK, PLAIN = PC.LIGHT, PC.MID, PC.DARK, PC.PLAIN
FS = 10.5


def box(ax, x, y, w, h, text, fc=PLAIN, tc=INK, bold=True, fs=FS, lw=0.6, dashed=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.06", fc=fc, ec=EDGE,
                                lw=lw, ls="--" if dashed else "-", zorder=2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=tc,
            fontweight="bold" if bold else "normal", linespacing=1.15, zorder=3)


def arrow(ax, p, q, dashed=False, rad=0.0):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=9, lw=0.9, color=INK,
                                 ls="--" if dashed else "-", connectionstyle=f"arc3,rad={rad}",
                                 shrinkA=1, shrinkB=1, zorder=1))


def main():
    P.setup()
    W, H = 7.7, 3.12                        # a little wider than the page column; scales to \textwidth
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")

    yc, bh = 2.02, 0.76
    HDR = yc + 0.97                         # shared baseline for the two column headers                     # main row centre and box height
    y0 = yc - bh / 2

    # main pipeline
    xs = {}
    specs = [("claim", "New\nclaim", 0.55, PLAIN),
             ("dom", "Domain\nidentification", 1.08, PLAIN),
             ("zone", "Zone\nidentification", 1.08, PLAIN),
             ("orch", "Orchestration\nlayer", 1.1, PLAIN)]
    x, gap = 0.04, 0.13
    for key, label, w, fc in specs:
        box(ax, x, y0, w, bh, label, fc=fc, tc=INK, fs=FS - 0.5, lw=0.6)
        xs[key] = (x, w)
        x += w + gap
    for a, b in zip(["claim", "dom", "zone"], ["dom", "zone", "orch"]):
        arrow(ax, (xs[a][0] + xs[a][1], yc), (xs[b][0], yc))

    # detection modules (stacked small boxes)
    mx, mw = x, 1.05
    mods = ["Style", "Knowledge", "Source", "Social context", "Propagation"]
    mh, mg = 0.245, 0.05
    top = yc + (len(mods) * mh + (len(mods) - 1) * mg) / 2
    ax.text(mx + mw / 2, HDR, "Detection modules", ha="center", va="center", fontsize=FS - 1.5,
            fontweight="bold", color=INK)
    for i, m in enumerate(mods):
        yy = top - (i + 1) * mh - i * mg
        box(ax, mx, yy, mw, mh, m, fs=FS - 1, bold=False, lw=0.6)
    arrow(ax, (xs["orch"][0] + xs["orch"][1], yc), (mx, yc))

    # zone-based decision (boxes leave a lane on the right for the partially-verified review path)
    dx, dw = mx + mw + gap, W - (mx + mw + gap) - 0.04
    lane = 0.16
    dbw = dw - lane
    outs = [("Verified", "verdict"), ("Partially verified", "explainable clues"), ("Unverified", "defer to experts")]
    oh, og = 0.5, 0.05
    otop = yc + (3 * oh + 2 * og) / 2
    ax.text(dx + dbw / 2, HDR, "Decision by data zone", ha="center", va="center", fontsize=FS - 1.5,
            fontweight="bold", color=INK)
    shades = [PC.DARK, PC.MID, PC.LIGHT]
    oy = {}
    for i, ((z, act), sh) in enumerate(zip(outs, shades)):
        yy = otop - (i + 1) * oh - i * og
        tc = PC.TEXT_ON.get(sh, INK)                    # white text only on the mid grey
        ax.add_patch(FancyBboxPatch((dx, yy), dbw, oh, boxstyle="round,pad=0,rounding_size=0.05", fc=sh, ec=EDGE,
                                    lw=0.6, zorder=2))
        ax.text(dx + dbw / 2, yy + oh * 0.69, z, ha="center", va="center", fontsize=FS - 0.5, fontweight="bold",
                color=tc, zorder=3)
        ax.text(dx + dbw / 2, yy + oh * 0.3, "\u2192 " + act, ha="center", va="center", fontsize=FS - 0.5, color=tc,
                zorder=3)
        oy[z] = yy
    arrow(ax, (mx + mw, yc), (dx, yc))

    # lower row: the three data zones under zone identification, human verification under the decision column
    zx, zw = xs["zone"]
    cx0, cx1 = 0.04, xs["orch"][0] + xs["orch"][1]
    cy, ch = 0.06, 1.18
    ax.add_patch(FancyBboxPatch((cx0, cy), cx1 - cx0, ch, boxstyle="round,pad=0,rounding_size=0.06",
                                fc=PC.CONTAINER, ec=EDGE, lw=0.6, zorder=1))
    ax.text((cx0 + cx1) / 2, cy + 0.17, "Data zones", ha="center", va="center", fontsize=FS - 0.5,
            fontweight="bold", color=INK, zorder=3)
    zones = [("Unverified", "open web", PC.LIGHT, INK),
             ("Partially verified", "Wikipedia, crowd,\nsocial signals", PC.MID, INK),
             ("Verified", "fact-checks,\nexpert labels", PC.DARK, INK)]
    zg = 0.1
    zbw = (cx1 - cx0 - 0.2 - 2 * zg) / 3
    zby, zbh = cy + 0.33, 0.74
    zc = {}
    for i, (z, src, sh, tc) in enumerate(zones):
        bx = cx0 + 0.1 + i * (zbw + zg)
        ax.add_patch(FancyBboxPatch((bx, zby), zbw, zbh, boxstyle="round,pad=0,rounding_size=0.05", fc=sh,
                                    ec=EDGE, lw=0.6, zorder=2))
        ax.text(bx + zbw / 2, zby + zbh * 0.74, z, ha="center", va="center", fontsize=FS - 0.5, fontweight="bold",
                color=tc, zorder=3)
        ax.text(bx + zbw / 2, zby + zbh * 0.33, src, ha="center", va="center", fontsize=FS - 1, color=tc,
                linespacing=1.05, zorder=3)
        zc[z] = bx + zbw / 2

    # zone identification -> data zones: one trunk, a horizontal bus, and a drop into each zone
    tx = zx + zw / 2
    bus = (y0 + cy + ch) / 2
    lk = dict(color=INK, lw=0.9, zorder=1, solid_capstyle="butt")
    ax.plot([tx, tx], [y0, bus], **lk)
    ax.plot([min(zc.values()), max(zc.values())], [bus, bus], **lk)
    ax.add_patch(FancyArrowPatch((tx, bus), (tx, y0), arrowstyle="-|>", mutation_scale=9, lw=0.9, color=INK,
                                 shrinkA=0, shrinkB=1, zorder=1))
    for cxz in zc.values():
        ax.add_patch(FancyArrowPatch((cxz, bus), (cxz, zby + zbh), arrowstyle="-|>", mutation_scale=9, lw=0.9,
                                     color=INK, shrinkA=0, shrinkB=1, zorder=1))

    # human verification: receives unverified and partially verified claims
    hx, hw = dx, dw
    hy, hh = zby, zbh
    box(ax, hx, hy, hw, hh, "Human verification\n(fact-checkers)", fs=FS - 0.5)
    dk = dict(color=INK, lw=0.9, ls="--", zorder=1)
    lx = dx + dbw + lane / 2
    ys = [oy[z] + oh / 2 for z in ("Partially verified", "Unverified")]
    for yy in ys:
        ax.plot([dx + dbw, lx], [yy, yy], **dk)
    ax.plot([lx, lx], [ys[0], hy + hh + 0.03], **dk)
    arrow(ax, (lx, hy + hh + 0.04), (lx, hy + hh), dashed=True)
    ax.text(lx + 0.03, (ys[1] + hy + hh) / 2, "review", ha="left", va="center", fontsize=FS - 1.5,
            style="italic", color=INK, rotation=90)

    # fact-checking moves claims into the verified zone
    vx = zc["Verified"] + zbw / 2
    arrow(ax, (hx, hy + hh / 2), (vx, hy + hh / 2), dashed=True)
    ax.text((hx + vx) / 2, hy + hh / 2 + 0.06, "fact-checking", ha="center", va="bottom",
            fontsize=FS - 1.5, color=INK, style="italic")

    P.save(fig, "fig_agenda_architecture_small")


if __name__ == "__main__":
    main()
