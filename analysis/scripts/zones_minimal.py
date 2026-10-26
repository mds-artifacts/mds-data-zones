"""
Minimal grayscale knowledge-zone figure.

    python scripts/zones_minimal.py ["path/to/workbook.xlsx"]

For each knowledge zone (Labelled data / Partial knowledge / No label):
  * number of studies in the zone
  * every domain in the zone, with count and % of the zone (DOMAIN codes; a study can have several)
  * every named benchmark dataset in the zone (+ 'Other / custom datasets' and 'Not reported')

Output: output/figures/fig_zones_minimal.[pdf,svg,png]
        output/tables/zones_minimal.xlsx   (all counts and PS# behind the figure)
"""
import collections

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import FancyBboxPatch

import config as C
import plotstyle as P
from model_classes import eras
from normalise import load_clean

ZONES = [("Unverified\ndata zone", "No label zone"),               # (figure label, coded value in the data)
         ("Partially verified\ndata zone", "Partial knowledge zone"),
         ("Verified\ndata zone", "Labelled data zone")]
import palette_cyan as PC
SHADES = [PC.LIGHT, PC.MID, PC.DARK]                # darker = more verified (cyan palette)
INK, INK2, RULE = PC.INK, PC.INK, PC.RULE          # one text colour throughout
MODELS = ["Feature eng. + classical ML", "Deep learning", "LLMs", "LLM agents"]
MODEL_SHORT = {"Feature eng. + classical ML": "ML", "Deep learning": "Deep learning", "LLMs": "LLM",
               "LLM agents": "LLM agents"}
ROW = 0.25
# readable domain names for this figure; celebrity and entertainment merged (a study is counted once)
DOM_NAME = {"DOM_CELEBRITY": "Entertainment", "DOM_ENTERTAINMENT": "Entertainment", "DOM_CULTURE": "Culture",
            "DOM_REVIEWS": "Other", "DOM_OTHER": "Other"}


def dom_names(codes):
    return {DOM_NAME.get(c, C.CODE_LABELS.get(c, c)) for c in codes}

DS_SHORT = {"FakeNewsNet (PolitiFact/GossipCop)": "FakeNewsNet", "Weibo (Ma et al. / Weibo21)": "Weibo",
            "Kaggle fake-news sets": "Kaggle fake-news", "CoAID / COVID sets": "CoAID / COVID",
            "SciFact / health claims": "SciFact / health", "Custom / newly collected": "Other / custom",
            "FakeNewsCorpus / NELA": "NELA / FN Corpus"}
OTHER_DS, NO_DS = "Other / custom", "Not reported"


def ds_names(row):
    """Named benchmarks a study uses; studies with none get 'Other / custom' or 'Not reported'."""
    names = {DS_SHORT.get(d, d) for d in row.dataset_set}
    if names:
        return names
    raw = str(row.datasets) if row.datasets == row.datasets else ""
    return {OTHER_DS} if raw.strip() and raw.strip().lower() != "nan" else {NO_DS}


def ds_ranked(counter, n):
    """Named datasets by count, with the two catch-all rows always last."""
    named = [(k, v, v / n) for k, v in sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))
             if k not in (OTHER_DS, NO_DS)]
    tail = [(k, counter[k], counter[k] / n) for k in (OTHER_DS, NO_DS) if counter.get(k)]
    return named + tail


def ranked(counter, n):
    return [(k, v, v / n) for k, v in sorted(counter.items(), key=lambda kv: (kv[0] == "Other", -kv[1], kv[0]))]


def main():
    P.setup()
    df = eras(load_clean())
    df["era"] = df["era"].replace({"Agentic LLMs": "LLM agents"})
    fs = 10.5                                   # large: readable full-width in a 2-column paper
    N = len(df)
    zone_dom = {z: collections.Counter(d for v in df[df.knowledge_zone_n == z].domain_set for d in dom_names(v))
                for _, z in ZONES}
    max_dom = max(len(c) for c in zone_dom.values())
    zone_ds = {z: collections.Counter(d for _, r in df[df.knowledge_zone_n == z].iterrows() for d in ds_names(r))
               for _, z in ZONES}
    max_ds = max(len(c) for c in zone_ds.values())

    W = 7.16
    H = 0.15 + 1.0 + 0.3 + (0.3 + ROW * max_dom) + 0.1        # zones + domains
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")

    gap, left = 0.16, 0.12
    cw = (W - 2 * left - 2 * gap) / 3
    top_y, head_h = H - 0.15, 1.0
    table = []
    for i, ((label, zone), shade) in enumerate(zip(ZONES, SHADES)):
        x = left + i * (cw + gap)
        sub = df[df.knowledge_zone_n == zone]
        n = len(sub)
        tc = PC.TEXT_ON.get(shade, INK)                    # white text only on the mid grey
        ax.add_patch(FancyBboxPatch((x, top_y - head_h), cw, head_h, boxstyle="round,pad=0,rounding_size=0.05",
                                    fc=shade, ec=PC.EDGE, lw=0.6, zorder=2))
        ax.text(x + 0.14, top_y - 0.27, label.replace("\n", " "), ha="left", va="center", fontsize=fs + 0.5,
                fontweight="bold", color=tc, zorder=3)
        ax.text(x + 0.14, top_y - 0.68, f"{n} studies", ha="left", va="center", fontsize=fs + 5,
                fontweight="bold", color=tc, zorder=3)
        ax.text(x + cw - 0.14, top_y - 0.7, f"{n / N:.0%} of {N}", ha="right", va="center",
                fontsize=fs, color=tc, zorder=3)

        dom = zone_dom[zone]
        mod = collections.Counter(sub.era)
        y = top_y - head_h - 0.3
        for title, items, slots in (("Domains", ranked(dom, n), max_dom),):
            ax.text(x, y, title, ha="left", va="center", fontsize=fs, color=INK, zorder=3)
            y -= 0.08
            ax.plot([x, x + cw], [y, y], color=RULE, lw=0.7)
            y -= 0.22
            for lab, k, p in items:
                ax.text(x, y, MODEL_SHORT.get(lab, lab), ha="left", va="center", fontsize=fs, color=INK if k else INK2)
                ax.text(x + cw, y, f"{k}", ha="right", va="center", fontsize=fs,
                        fontweight="bold" if k else "normal", color=INK if k else INK2)
                y -= ROW
            y -= 0.14 + ROW * (slots - len(items))            # keep both blocks aligned across columns
        for lab, k in dom.most_common():
            ps = sub[sub.domain_set.map(lambda v, lab=lab: lab in dom_names(v))]
            table.append([zone, n, "Domain", lab, k, round(100 * k / n, 1), ", ".join(ps.ps_id.map(str))])
        for lab, k, _ in ds_ranked(zone_ds[zone], n):
            ps = sub[[lab in ds_names(r) for _, r in sub.iterrows()]]
            table.append([zone, n, "Dataset", lab, k, round(100 * k / n, 1), ", ".join(ps.ps_id.map(str))])

    P.save(fig, "fig_zones_minimal")
    pd.DataFrame(table, columns=["Zone", "Zone studies", "Dimension", "Category", "n", "%", "PS#"]) \
        .to_excel(C.TAB_DIR / "zones_minimal.xlsx", index=False)
    print("  saved tables/zones_minimal.xlsx")


if __name__ == "__main__":
    C.use_workbook_arg()
    main()
