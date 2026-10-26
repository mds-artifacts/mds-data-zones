"""
Step 2 - Turn the raw extraction cells into clean, countable categories.

Every rule is a transparent keyword rule so a reviewer can audit it.
Each study can carry several labels in a dimension (e.g. Style + Social-context);
these are stored as '; '-joined strings in studies_clean.csv and exploded into
long tables (one row per study x label) for counting.

Outputs
  data/studies_clean.csv            one row per study, normalised columns
  data/long_<dimension>.csv         study x label tables
  output/tables/coding_audit.csv    values that matched no rule (check these!)
  output/tables/possible_duplicates.csv
"""
from __future__ import annotations

import re
import unicodedata

import numpy as np
import pandas as pd

import config as C
from load_extractions import load

# ----------------------------------------------------------------------------
# Keyword lexicons:  label -> regex (case-insensitive, matched on the cell)
# ----------------------------------------------------------------------------
APPROACH = {
    "Style-based": r"style|content[- ]based|linguistic",
    "Knowledge-based": r"knowledge|fact[- ]?check|evidence|\bnli\b|verification",
    "Social-context": r"social[- ]?context|stance|user comment|crowd",
    "Source-based": r"source|speaker|publisher|credibility of user",
    "Propagation-based": r"propagation|cascade|diffusion|retweet",
    "Other": r"discourse|temporal",
}

# Model families: what kind of model does the detection?
MODEL_FAMILY = {
    "LLM / LVLM": r"\bllms?\b|lvlm|large language models?|gpt-?[34o]|chatgpt|llama|mistral|vicuna|gemini|claude|"
                  r"qwen|flan-?t5|\bagent",
    "Transformer / PLM": r"transformer|\bplm\b|bert|roberta|deberta|xlnet|electra|albert|distil|\bt5\b|\bbart\b|"
                         r"\bclip\b|\bvit\b|longformer|bigbird|pre-?trained language",
    "Deep learning": r"\bdl\b|deep|neural|\bcnn|\brnn|lstm|gru|\bgnn|\bgcn|\bgat\b|graph neural|attention|"
                     r"autoencoder|\bvae\b|capsule|\bmlp\b|perceptron|resnet|vgg|reservoir",
    "Classical ML": r"\bml\b|machine learning|svm|support vector|random forest|\brf\b|naive bayes|\bnb\b|"
                    r"logistic|decision tree|\bknn\b|xgboost|adaboost|gradient boost|lightgbm|catboost|"
                    r"bagging|boosting|\blr\b|\bdt\b|passive aggressive|svm-rank",
    "Other": r"statistic|graph algorithm|cluster|metaheuristic|stochastic|point process|social graph|"
             r"rule|heuristic|hypothesis|discourse",
}
FAMILY_PRIORITY = ["LLM / LVLM", "Transformer / PLM", "Deep learning", "Classical ML", "Other"]

# Named model architectures (for the "which models" figure).
ARCHITECTURE = {
    "SVM": r"\bsvm|support vector", "Logistic regression": r"logistic|\blr\b",
    "Naive Bayes": r"naive bayes|\bnb\b|multinomialnb", "Random forest": r"random forest|\brf\b",
    "Decision tree": r"decision tree|\bdt\b|\bcart\b|\bj48\b", "k-NN": r"\bk-?nn\b|nearest neighbo",
    "Gradient boosting": r"xgboost|lightgbm|catboost|gradient boost|adaboost|\bgbm\b|boosting",
    "CNN": r"\bcnn|\brcnn|convolution", "LSTM / BiLSTM": r"lstm|\bcsi\b", "GRU / BiGRU": r"\bgru|bigru",
    "RNN (vanilla)": r"\brnn\b|recurrent", "Attention / HAN": r"attention|\bhan\b",
    "GNN (GCN / GAT)": r"\bgnn|\bgcn|\bgat\b|graph (neural|conv|attention)",
    "Autoencoder / VAE": r"autoencoder|\bvae\b", "MLP": r"\bmlp\b|perceptron|feed-?forward",
    "BERT family": r"\bbert|roberta|distil|albert|deberta|electra|xlnet|ct-bert|covid-twitter-bert|bigbird|factcc|summac",
    "T5 / BART": r"\bt5\b|\bbart\b|flan", "CLIP / ViT": r"\bclip\b|\bvit\b",
    "VGG / ResNet": r"vgg|resnet|inception|efficientnet",
    "GPT family": r"gpt|chatgpt|davinci", "LLaMA / Mistral / open LLMs": r"llama|mistral|vicuna|qwen|gemma|falcon",
    "Ensemble / stacking": r"ensemble|stacking|voting|bagging",
    "Other linear classifiers": r"passive.?aggressive|\bsgd\b|linear classifier",
    "Adversarial nets (GAN / DANN)": r"\bdann\b|\bgan\b|adversarial net|generative adversarial",
    "Graph / network algorithms": r"pagerank|graph optim|graph algorithm|social graph|centrality|newscp",
    "Statistical / probabilistic models": r"stochastic|point process|probabilistic|hypothesis|gini|decision rule|"
                                          r"bayesian network|statistical",
    "Matrix factorisation / topic models": r"\blsa\b|\bsvd\b|matrix factori|\blda\b|topic model|trifn|vector space",
}

# Which model class each named model belongs to (used by RQ1 and the taxonomy).
ARCH_FAMILY = {
    "SVM": "Classical ML", "Logistic regression": "Classical ML", "Naive Bayes": "Classical ML",
    "Random forest": "Classical ML", "Decision tree": "Classical ML", "k-NN": "Classical ML",
    "Gradient boosting": "Classical ML", "Ensemble / stacking": "Classical ML",
    "Other linear classifiers": "Classical ML",
    "CNN": "Deep learning", "LSTM / BiLSTM": "Deep learning", "GRU / BiGRU": "Deep learning",
    "RNN (vanilla)": "Deep learning", "Attention / HAN": "Deep learning", "GNN (GCN / GAT)": "Deep learning",
    "Autoencoder / VAE": "Deep learning", "MLP / DNN": "Deep learning", "VGG / ResNet": "Deep learning",
    "Adversarial nets (GAN / DANN)": "Deep learning",
    "BERT family": "Transformer / PLM", "T5 / BART": "Transformer / PLM", "CLIP / ViT": "Transformer / PLM",
    "GPT family": "LLM / LVLM", "LLaMA / Mistral / open LLMs": "LLM / LVLM",
    "Graph / network algorithms": "Statistical / graph", "Statistical / probabilistic models": "Statistical / graph",
    "Matrix factorisation / topic models": "Statistical / graph",
}

LEARNING = {
    "Supervised": r"(?<!semi-)(?<!semi )(?<!un)(?<!weakly )(?<!self-)(?<!self )supervis(ed|ion)|fine[- ]?tun|\bsft\b",
    "Transfer learning": r"transfer|fine[- ]?tun|pre-?trained",
    "Ensemble learning": r"ensemble|bagging|stacking|voting",
    "Semi-supervised": r"semi[- ]?supervis|self-training|co-train|pseudo",
    "Unsupervised": r"\bunsupervis|cluster",
    "Weakly supervised": r"weakly",
    "In-context: zero-shot": r"zero[- ]?shot",
    "In-context: few-shot": r"few[- ]?shot|in-context learning(?!.*zero)",
    "Agentic / tool use": r"agent",
    "Multitask learning": r"multi-?task",
    "Adversarial / domain adaptation": r"adversarial|domain adapt|domain-invariant|event-invariant",
    "Contrastive / self-supervised": r"contrastive|self-supervis",
    "Federated learning": r"federated",
    "Reinforcement learning": r"reinforcement",
    "Metaheuristic optimisation": r"metaheuristic|swarm|genetic|evolutionary",
    "Online / incremental": r"online|incremental|prequential|iterative",
}

KNOWLEDGE_ZONE = {
    "Labelled data zone": r"label+ed data zone",
    "Partial knowledge zone": r"partial",
    "No label zone": r"no label",
}

TEMPORALITY = {
    "Update-streaming": r"stream|updat|live|online|preq",
    "Temporal": r"temporal|chronolog|early time",
    "Static snapshot": r"static",
}

DATASETS = {
    "LIAR / LIAR-PLUS": r"\bliar", "FakeNewsNet (PolitiFact/GossipCop)": r"fakenewsnet|fake ?news ?net|gossipcop",
    "ISOT": r"\bisot", "Kaggle fake-news sets": r"kaggle|mcintire|news\.csv",
    "BuzzFeed / BuzzFace": r"buzzfeed|buzzface", "FEVER family": r"\bfever|feverous|hover\b",
    "PHEME": r"pheme", "Twitter15/16": r"twitter ?1[56]", "Weibo (Ma et al. / Weibo21)": r"weibo",
    "CoAID / COVID sets": r"coaid|constraint|covid|recovery|mm-covid|fakecovid|cmu-?miscov",
    "FakeNewsCorpus / NELA": r"fakenewscorpus|nela", "Fakeddit": r"fakeddit",
    "NewsCLIPpings / VERITE": r"newsclippings|verite|cosmos", "SciFact / health claims": r"scifact|pubhealth|healthfeedback|monant",
    "FNC-1 / Emergent": r"fnc|emergent", "Custom / newly collected": r"collected|crawl|scrap|own dataset|new dataset|built|constructed",
}

FEATURES = {
    "Bag-of-words / TF-IDF / n-grams": r"bag|bow\b|tf-?idf|\btf\b|term frequen|n-?gram|count vector|unigram|bigram|one-hot|word-frequency",
    "Static word embeddings": r"glove|word2vec|fasttext|doc2vec|word embedding",
    "Contextual embeddings (PLM)": r"bert|roberta|transformer|contextual|sentence-?bert|sbert|\bclip\b|tokeni[sz]",
    "Learned / task-specific embeddings": r"learned embedding|non-static|bigbird|prompt embedding|embedding layer",
    "Hand-crafted features": r"manual fe|hand-?craft|manual feature|engineered",
    "Linguistic / stylometric": r"lexicon|linguistic|pos\b|part-of-speech|readab|syntac|lexical|stylo|liwc|psycholing|complexity",
    "Sentiment / emotion": r"sentiment|emotion|affect|polarity",
    "User / profile": r"user|profile|follower|account|speaker|author",
    "Propagation / network": r"propagation|network|graph|retweet|cascade|diffusion",
    "Temporal": r"temporal|time|timestamp",
    "Visual (image / video)": r"image|visual|vgg|resnet|video|ocr|vit\b",
    "External evidence / retrieval": r"evidence|retriev|search|wikipedia|knowledge graph|fact-check|web",
    "Metadata / source": r"metadata|source|publisher|url|domain|credit history",
}

METRICS = {
    "Accuracy": r"met_acc|accura", "F1-score": r"met_f1|\bf1|f-measure|f-score",
    "Precision": r"met_p\b|precision", "Recall": r"met_r\b|recall|sensitiv|met_sens|tpr",
    "Macro-F1": r"macro[ _-]?f1|met_macro_f1", "AUC (ROC / PR)": r"auc|auroc|roc",
    "Loss": r"loss", "Runtime / efficiency": r"runtime|time|latency|flops|cost|model_size",
    "Confusion matrix": r"confusion", "Ranking (NDCG / P@k / MAP)": r"ndcg|p@k|precision@|map\b",
    "Human evaluation": r"human", "Specificity / FPR": r"spec|fpr|false positive",
}

EVALUATION = {
    "Random split": r"random|stratified|\d\d ?% ?(train|test)|\d\d ?%[^,;]{0,25}\d\d ?%|\d\d[/:]\d\d|\d:\d:\d|hold-?out|held_out_test|train/test split|train-test split",
    "Predefined / official split": r"predefined|official|standard split|provided|benchmark split|original split|standard (train|test)",
    "k-fold cross-validation": r"k-?fold|\d+-fold|cross-?valid|kfold|leave-one-out",
    "Cross-dataset / cross-domain": r"cross[_ -]?(dataset|domain)|out-of-distribution|ood",
    "Temporal / held-out events": r"chronolog|temporal|held[_ -]?out[_ -]?event|leave-one-event|loeo|early[_ ]window|prequential|post-?cut",
    "Zero-shot test": r"zero[_ -]?shot",
    "Human / user study": r"human|user (study|trial)|amt",
    "Bootstrap / repeated runs": r"bootstrap|repeat",
}

FACTCHECKERS = {
    "PolitiFact": r"politifact|liar", "Snopes": r"snopes", "GossipCop": r"gossipcop",
    "FactCheck.org": r"factcheck\.org|factcheck", "Full Fact": r"full ?fact", "BuzzFeed News": r"buzzfeed",
    "IFCN / Poynter": r"ifcn|poynter", "Washington Post Fact Checker": r"washington post",
    "Reuters Fact Check": r"reuters", "AFP Fact Check": r"\bafp\b", "Health Feedback": r"health ?feedback",
    "Several fact-checkers": r"multiple_fact|multiple fact|several",
}


# ----------------------------------------------------------------------------
def match_all(text, lexicon: dict[str, str]) -> list[str]:
    if text is None or (isinstance(text, float) and np.isnan(text)):
        return []
    t = str(text).lower()
    return [lab for lab, pat in lexicon.items() if re.search(pat, t)]


def codes(text, prefix: str | None = None) -> list[str]:
    if text is None or (isinstance(text, float) and np.isnan(text)):
        return []
    found = re.findall(r"\b[A-Z][A-Z0-9]*_[A-Z0-9_]+\+?", str(text))
    found = [f.rstrip("_") for f in found]
    if prefix:
        found = [f for f in found if f.startswith(prefix)]
    return list(dict.fromkeys(found))  # unique, keep order


def code_label(code: str) -> str:
    if code in C.CODE_LABELS:
        return C.CODE_LABELS[code]
    body = re.sub(r"^(AI|DATA|SYS|GT|OPP|O|DOM|PLT|GTP|GTH|MET|EVAL|BL|RSN)_", "", code)
    words = body.lower().split("_")
    words = [w.upper() if w in C.ACRONYMS else w for w in words]
    s = " ".join(words)
    return s[:1].upper() + s[1:]


def swot_category(code: str) -> str:
    return {"AI": "AI / model", "DATA": "Data", "SYS": "System", "GT": "Ground truth"}.get(
        code.split("_", 1)[0], "Other")


def year_bin(y) -> str | None:
    try:
        y = int(str(y)[:4])
    except ValueError:
        return None
    for lo, hi, lab in C.YEAR_BINS:
        if lo <= y <= hi:
            return lab
    return None


def _surname(a) -> str:
    a = re.sub(r"^\[\d+\]\s*", "", str(a or ""))
    a = unicodedata.normalize("NFKD", a).encode("ascii", "ignore").decode()
    a = re.sub(r"\(.*?\)", "", a)
    first = re.split(r",| and |&|;| et al", a)[0].strip()
    parts = [p for p in re.split(r"[\s.]+", first) if len(p) > 1]
    if not parts:
        return ""
    return parts[-1].lower() if re.match(r"^[A-Z]\.", first) else parts[0].lower()


# ----------------------------------------------------------------------------
def build() -> dict[str, pd.DataFrame]:
    df = load(C.WORKBOOK)
    for ps, fix in getattr(C, "MANUAL_FIXES", {}).items():
        hit = df["ps_id"].astype(str).str.replace(" ", "") == ps
        for field, value in fix.items():
            if hit.any() and (df.loc[hit, field].isna().all() or field != "year"):
                df.loc[hit, field] = str(value)
    df["seq"] = df.groupby("review").cumcount() + 1
    df["uid"] = df["review"] + "#" + df["seq"].astype(str)
    # a row with an empty PS# cell would break every PS# list: give it a visible placeholder and warn
    ps = df["ps_id"].astype(object)
    missing = ps.isna() | (ps.map(lambda v: str(v).strip()) == "")
    for _, r in df[missing].iterrows():
        print(f"  WARNING: row with no PS# in sheet '{r.get('sheet', '?')}': {str(r.get('title', ''))[:70]!r}"
              " - add its PS number in the workbook")
    df["ps_id"] = ps.where(~missing, "PS?(" + df["uid"] + ")").map(lambda v: str(v).strip())
    df["ps_id"] = df["ps_id"].str.replace(r"^P\s*S?\s*(\d+)$", r"PS\1", regex=True)   # e.g. "P136" -> "PS136"
    df["year"] = pd.to_numeric(df["year"].astype(str).str.extract(r"((?:19|20)\d\d)")[0], errors="coerce")
    df["year_bin"] = df["year"].map(year_bin)

    # ---- RQ1: methods ------------------------------------------------------
    df["approach_set"] = df["approach"].map(lambda v: match_all(v, APPROACH))
    if getattr(C, "DROP_ONE_OFF_APPROACHES", False):
        df["approach_set"] = df["approach_set"].map(lambda s: [a for a in s if a != "Other"])
    model_text = df[["model_class", "model", "learning"]].fillna("").agg(" ".join, axis=1)
    fam_from_class = df["model_class"].map(lambda v: match_all(v, MODEL_FAMILY))
    fam_from_text = model_text.map(lambda v: match_all(v, MODEL_FAMILY))
    # model class column is authoritative; model text adds Transformer/LLM detail
    df["model_family_set"] = [
        sorted(set(a) | ({x for x in b if x in ("Transformer / PLM", "LLM / LVLM")}),
               key=FAMILY_PRIORITY.index) for a, b in zip(fam_from_class, fam_from_text)]
    df["model_family_primary"] = df["model_family_set"].map(
        lambda s: next((f for f in FAMILY_PRIORITY if f in s), "Not reported"))
    arch_text = df[["model", "architecture", "title", "model_class"]].fillna("").agg(" ".join, axis=1)
    df["architecture_set"] = arch_text.map(lambda v: match_all(v, ARCHITECTURE))
    df["learning_set"] = df["learning"].map(lambda v: match_all(v, LEARNING))

    # ---- RQ2: information --------------------------------------------------
    df["knowledge_zone_n"] = df["knowledge_zone"].map(
        lambda v: (match_all(v, KNOWLEDGE_ZONE) or ["Not reported"])[0])
    for c in ("train_temporality", "test_temporality"):
        df[c + "_n"] = df[c].map(lambda v: (match_all(v, TEMPORALITY) or ["Not reported"])[0])
    dom = df["domains"].map(lambda v: codes(v, "DOM_"))
    df["domain_set"] = dom.map(lambda s: [c for c in s if c != "DOM_MIXED"] or s)
    df["platform_set"] = df["domains"].map(lambda v: codes(v, "PLT_"))
    gt = df["ground_truth"].fillna("").str.replace(r"\bTP_FACTCHECK", "GTP_FACTCHECK", regex=True)
    df["gt_provenance_set"] = gt.map(lambda v: codes(v, "GTP_"))
    df["gt_hops_set"] = gt.map(lambda v: ["GTH_3+" if c.startswith("GTH_3") else c for c in codes(v, "GTH_")])
    df["dataset_set"] = df["datasets"].map(lambda v: match_all(v, DATASETS))
    df["feature_set"] = df[["features"]].fillna("").agg(" ".join, axis=1).map(lambda v: match_all(v, FEATURES))
    df["factchecker_set"] = df[["factcheck_orgs", "ground_truth", "datasets"]].fillna("").agg(" ".join, axis=1) \
        .map(lambda v: match_all(v, FACTCHECKERS))

    # ---- RQ3: pros & cons --------------------------------------------------
    for f in ("S", "W", "O", "T"):
        df[f + "_set"] = df[f].map(codes)
    df["metric_set"] = df["metrics"].map(lambda v: match_all(v, METRICS))
    eval_text = df[["evaluation", "S", "W"]].fillna("").agg(" ".join, axis=1)
    df["evaluation_set"] = df["evaluation"].map(lambda v: match_all(v, EVALUATION))
    # random split is also coded as a weakness; keep the two consistent
    df["evaluation_set"] = [sorted(set(e) | ({"Random split"} if "DATA_RANDOM_SPLIT_EVAL" in w else set()))
                            for e, w in zip(df["evaluation_set"], df["W_set"])]
    df["baseline_set"] = df["baselines"].map(lambda v: codes(v, "BL_"))

    # ---- duplicates --------------------------------------------------------
    df["dup_key"] = df["author"].map(_surname) + "_" + df["year"].fillna(0).astype(int).astype(str)
    dups = df[df.duplicated("dup_key", keep=False) & (df["dup_key"].str.len() > 6)] \
        .sort_values("dup_key")[["dup_key", "uid", "review", "author", "year", "title", "model"]]
    dups.to_csv(C.TAB_DIR / "possible_duplicates.csv", index=False)
    df = df[~df["uid"].isin(C.DROP_DUPLICATES + C.EXCLUDE_NOT_PRIMARY)].reset_index(drop=True)

    # ---- audit: cells that no rule matched ---------------------------------
    audit = []
    for raw, col in [("approach", "approach_set"), ("model_class", "model_family_set"),
                     ("learning", "learning_set"), ("knowledge_zone", "knowledge_zone_n"),
                     ("datasets", "dataset_set"), ("features", "feature_set"),
                     ("metrics", "metric_set"), ("evaluation", "evaluation_set")]:
        miss = df[df[raw].notna() & df[col].map(lambda s: s in ([], "Not reported"))]
        for _, r in miss.iterrows():
            audit.append({"field": raw, "uid": r["uid"], "value": r[raw]})
    pd.DataFrame(audit).to_csv(C.TAB_DIR / "coding_audit.csv", index=False)

    # ---- save --------------------------------------------------------------
    set_cols = [c for c in df.columns if c.endswith("_set")]
    flat = df.copy()
    for c in set_cols:
        flat[c] = flat[c].map(lambda s: "; ".join(s))
    flat.to_csv(C.DATA / "studies_clean.csv", index=False)

    longs = {}
    for c in set_cols:
        lg = df[["uid", "review", "year", "year_bin", "model_family_primary", c]].explode(c).dropna(subset=[c])
        lg = lg.rename(columns={c: "label"})
        lg.to_csv(C.DATA / f"long_{c.replace('_set', '')}.csv", index=False)
        longs[c] = lg
    return {"studies": df, **longs}


def load_clean() -> pd.DataFrame:
    """Load studies_clean.csv with list columns restored.
    Rebuilds it first if it is missing or older than the workbook (so scripts can run alone)."""
    csv = C.DATA / "studies_clean.csv"
    if not csv.exists() or (C.WORKBOOK.exists() and C.WORKBOOK.stat().st_mtime > csv.stat().st_mtime):
        print("  (re)building data/studies_clean.csv from the workbook ...")
        build()
    df = pd.read_csv(csv)
    for c in [c for c in df.columns if c.endswith("_set")]:
        df[c] = df[c].fillna("").map(lambda s: [x for x in s.split("; ") if x])
    return df


if __name__ == "__main__":
    C.use_workbook_arg()
    out = build()
    d = out["studies"]
    print(f"Studies: {len(d)}")
    for c in ["approach_set", "model_family_set", "learning_set", "dataset_set", "feature_set",
              "metric_set", "evaluation_set"]:
        cov = (d[c].map(len) > 0).mean() * 100
        print(f"  {c:20s} coded for {cov:5.1f}% of studies")
    print("Audit rows:", len(pd.read_csv(C.TAB_DIR / 'coding_audit.csv')))
