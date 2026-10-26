"""
Central configuration: paths, figure sizes, palette, readable labels and
manual decisions (e.g. confirmed duplicates). Edit THIS file, not the
analysis scripts, when you want to change how something is counted or shown.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
WORKBOOK = DATA / "SLR_extractions.xlsx"
FIG_DIR = ROOT / "output" / "figures"
TAB_DIR = ROOT / "output" / "tables"
for d in (DATA, FIG_DIR, TAB_DIR):
    d.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------------------------------
# Manual decisions
# --------------------------------------------------------------------------
# Row ids (column `uid` in data/studies_clean.csv) that are confirmed
# duplicates of another extracted study. Check output/tables/
# possible_duplicates.csv, then list the copies to DROP here, e.g.
#   DROP_DUPLICATES = ["Darnoto#5", "Alkomah & Sheldon#4"]
DROP_DUPLICATES: list[str] = ["LLM survey#2"]   # Kumar et al. 2024 coded twice (as PS103 and PS101); keep PS101

# Rows that are not primary studies (e.g. a review that slipped into an
# extraction tab). They are removed from every analysis.
EXCLUDE_NOT_PRIMARY: list[str] = ["Bashaddadh#31"]   # Garcia Lozano et al. 2019 - an SLR

# Drop one-off approach labels ("Discourse Based", "Temporal" -> "Other") everywhere,
# so only the five core detection approaches are counted.
DROP_ONE_OFF_APPROACHES = True

# Manual fixes applied on top of the workbook (PS# -> {field: value}).
# Prefer fixing the Excel file; keep only what is not yet fixed there.
MANUAL_FIXES = {
    "PS107": {"year": 2024},   # Li, Zhang & Malthouse - FactAgent, arXiv 2405.01593 (May 2024); year blank in workbook
}

# How the agent stages are told apart (matched, case-insensitive, on MODEL CLASS):
#   'Agentic LLM' stage = model class matches AGENTIC_LLM_CLASS
#   'LLM agent'  stage  = any other agent / agentic-reasoning study
# To also count "Agentic RAG" (PS114) as an agentic LLM, use r"agentic (llm|rag)".
AGENTIC_LLM_CLASS = r"agentic llm"

# Year bins for "change over time" figures.
YEAR_BINS = [(0, 2016, "≤2016"), (2017, 2018, "2017–18"), (2019, 2020, "2019–20"),
             (2021, 2022, "2021–22"), (2023, 2024, "2023–24"), (2025, 2100, "2025–26")]

# --------------------------------------------------------------------------
# Figure geometry (inches). Typical journal columns: IEEE 3.5 / 7.16,
# Elsevier 3.54 / 7.48, ACM 3.33 / 7.0, Springer 3.31 / 6.93.
# --------------------------------------------------------------------------
SINGLE_COL = 3.5
DOUBLE_COL = 7.16
FONT_FAMILY = ["Inter", "Helvetica Neue", "Helvetica", "Arial", "Liberation Sans", "DejaVu Sans"]
BASE_FONT_SIZE = 10         # pt - large enough to read when a figure is scaled into a 2-column paper
SAVE_FORMATS = ("pdf", "png", "svg")
PNG_DPI = 400

# --------------------------------------------------------------------------
# Palette (validated categorical order; CVD-safe on adjacent pairs).
# --------------------------------------------------------------------------
CATEGORICAL = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100",
               "#e87ba4", "#008300", "#6250d6", "#e34948"]
SEQUENTIAL = ["#f4f8fd", "#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5",
              "#256abf", "#184f95", "#0d366b"]          # one hue, light -> dark
NEUTRAL = "#8a8984"          # "other / not reported"
INK = "#0b0b0b"
INK_2 = "#52514e"
INK_3 = "#8a8984"
GRID = "#e4e3df"
SURFACE = "#ffffff"

# Fixed colour per entity - colour follows the entity in EVERY figure.
APPROACH_ORDER = ["Style-based", "Knowledge-based", "Social-context", "Source-based",
                  "Propagation-based", "Other"]
MODEL_ORDER = ["Classical ML", "Deep learning", "Transformer / PLM", "LLM / LVLM", "Other"]
LEARNING_ORDER = None   # ordered by frequency
SWOT_CATEGORY_ORDER = ["AI / model", "Data", "System", "Ground truth", "Other"]

COLOR = {
    # model families (ordered by era)
    "Classical ML": CATEGORICAL[0], "Deep learning": CATEGORICAL[1],
    "Transformer / PLM": CATEGORICAL[2], "LLM / LVLM": CATEGORICAL[6],
    # approaches
    "Style-based": CATEGORICAL[0], "Knowledge-based": CATEGORICAL[1],
    "Social-context": CATEGORICAL[2], "Source-based": CATEGORICAL[3],
    "Propagation-based": CATEGORICAL[4],
    # SWOT code categories
    "AI / model": CATEGORICAL[0], "Data": CATEGORICAL[1], "System": CATEGORICAL[2],
    "Ground truth": CATEGORICAL[3],
    # temporality
    "Static snapshot": CATEGORICAL[0], "Temporal": CATEGORICAL[2],
    "Update-streaming": CATEGORICAL[1],
    # knowledge zones
    "Labelled data zone": CATEGORICAL[0], "Partial knowledge zone": CATEGORICAL[3],
    "No label zone": CATEGORICAL[6],
    # fallbacks
    "Other": NEUTRAL, "Not reported": "#c3c2b7",
}

# --------------------------------------------------------------------------
# Readable labels for codes. Anything not listed is auto-formatted
# (prefix removed, underscores -> spaces, sentence case).
# --------------------------------------------------------------------------
CODE_LABELS = {
    # Domains / platforms
    "DOM_GENERAL_NEWS": "General news", "DOM_POLITICS": "Politics", "DOM_HEALTH": "Health",
    "DOM_CRISIS_EVENT": "Crisis events", "DOM_CELEBRITY": "Celebrity / entertainment",
    "DOM_ENCYCLOPEDIC": "Encyclopedic", "DOM_FINANCE": "Finance", "DOM_MIXED": "Mixed (unspecified)",
    "DOM_UNSPECIFIED": "Not reported", "DOM_NO_EVALUATION": "Not reported",
    "PLT_NEWS_WEB": "News websites", "PLT_TWITTER": "Twitter / X", "PLT_FACTCHECK_WEB": "Fact-checking sites",
    "PLT_MIXED": "Mixed platforms", "PLT_WEIBO": "Weibo", "PLT_WIKIPEDIA": "Wikipedia",
    "PLT_REDDIT": "Reddit", "PLT_FACEBOOK": "Facebook", "PLT_VIDEO": "Video platforms",
    "PLT_VIDEO_INSTAGRAM": "Instagram / video", "PLT_NOT_REPORTED": "Not reported",
    # Ground truth provenance / hops
    "GTP_INHERITED": "Inherited from a prior dataset", "GTP_FACTCHECK_ORG": "Fact-checking organisation",
    "GTP_SOURCE_LEVEL": "Source-level (outlet reputation)", "GTP_AUTHORS": "Labelled by the authors",
    "GTP_BY_CONSTRUCTION": "By construction (synthetic)", "GTP_CROWD": "Crowd workers",
    "GTP_EXPERTS": "Domain experts", "GTP_NOT_REPORTED": "Not reported",
    "GTP_ORACLE_AT_RUNTIME": "Live oracle at inference",
    "GTH_0": "0 – authors judged", "GTH_1": "1 – scraped fact-checker verdicts",
    "GTH_2": "2 – packaged dataset", "GTH_3+": "3+ – re-split / augmented dataset",
    "GTH_UNKNOWN": "Unknown version",
    # Frequent strengths
    "AI_FEATURE_FUSION_ABLATED": "Ablation of fused features",
    "AI_NO_HANDCRAFTED_FEATURES": "No hand-crafted features",
    "SYS_LOW_DEPENDENCY_STACK": "Low-dependency stack",
    "AI_CROSS_DATASET_GENERALIZATION": "Cross-dataset generalisation tested",
    "AI_STRUCTURE_OVER_KEYWORDS": "Uses structure, not just keywords",
    "DATA_BALANCED_CLASSES": "Balanced classes",
    "DATA_JOURNALIST_ANNOTATED": "Journalist-annotated labels",
    "AI_EARLY_DETECTION_EVALUATED": "Early detection evaluated",
    "DATA_THREE_INDEPENDENT_SETS": "Train / validation / test sets",
    "SYS_LOW_LATENCY": "Low latency", "AI_EXPLAINABLE_BY_CONSTRUCTION": "Explainable by design",
    "AI_SMALL_INTERPRETABLE_FEATURE_SET": "Small interpretable feature set",
    "SYS_CLIENT_DEPLOYMENT": "Deployed to end users", "AI_THEORETICAL_GROUNDING": "Theoretically grounded",
    "AI_UNSEEN_GENERALIZATION": "Generalises to unseen events",
    "AI_INTERPRETABILITY_ATTEMPTED": "Interpretability analysis",
    "DATA_NO_LABELS_REQUIRED": "No labels required",
    # Frequent weaknesses
    "AI_NO_ABSTENTION": "No abstention (always forces a verdict)",
    "DATA_RANDOM_SPLIT_EVAL": "Random split only",
    "DATA_INHERITED_LABELS": "Inherited, unverified labels",
    "DATA_SOURCE_LEVEL_LABELS": "Source-level, not claim-level, labels",
    "SYS_NO_DEPLOYMENT_PATH": "No deployment path",
    "SYS_TRAINING_LATENCY": "High training cost / latency",
    "DATA_BINARY_ONLY": "Binary labels only",
    "DATA_SMALL_CORPUS": "Small corpus", "DATA_TINY_CORPUS": "Very small corpus",
    "DATA_SINGLE_TOPIC_SINGLE_COUNTRY": "Single topic / country",
    "SYS_BATCH_LATENCY": "Batch-only (needs data to accumulate)",
    "DATA_AGED_BENCHMARK": "Ageing benchmark",
    "GT_CREDIBILITY_NOT_TRUTH": "Credibility ≠ truth",
    "SYS_CENTRAL_SERVER_BOTTLENECK": "Central-server bottleneck",
    "AI_OPAQUE_LATENT_SPACE": "Opaque latent space",
    "SYS_MANUAL_ANNOTATION_REQUIRED": "Manual annotation required",
    "GT_TINY_LABEL_BASE": "Tiny labelled base",
    # Frequent threats
    "DATA_BENCHMARK_SATURATION": "Benchmark saturation", "AI_STYLE_DRIFT": "Writing-style drift",
    "AI_LLM_STYLE_TRANSFER": "LLM style transfer evades detectors", "AI_MODEL_DRIFT": "Model / concept drift",
    "DATA_PLATFORM_ACCESS": "Loss of platform data access", "AI_LLM_RHETORIC_GEN": "LLM-generated rhetoric",
    "SYS_API_DEPRECATION": "API deprecation", "DATA_DOMAIN_GAP_WIDENS": "Widening domain gap",
    "DATA_URL_ROT": "URL / link rot", "AI_ASTROTURFING": "Astroturfing",
    # Frequent opportunities
    "SYS_CONFIDENCE_GATE": "Confidence gate / abstention",
    "MODEL_DISTILLATION_SERVING": "Distilled model serving",
    "CROSS_TASK_INVARIANT_TESTS": "Cross-task invariance tests",
    "SYS_EDGE_INFERENCE": "Edge inference", "EARLY_DETECTION_SLA": "Early-detection SLA",
    "O_STREAMING_PIPELINE": "Streaming pipeline", "HELD_OUT_EVENT_HARNESS": "Held-out-event test harness",
}

ACRONYMS = {"llm", "lvlm", "kg", "api", "url", "ocr", "gt", "ui", "sla", "nli", "ai", "ml", "dl", "cnn", "gnn", "ttl"}


def use_workbook_arg(argv=None):
    """If the first command-line argument is an .xlsx file, copy it in as the workbook to use.
    Lets every script run on its own:  python scripts/<script>.py "path/to/workbook.xlsx" """
    import shutil
    import sys
    argv = sys.argv if argv is None else argv
    for a in list(argv[1:]):
        if a.lower().endswith((".xlsx", ".xlsm")):
            src = Path(a)
            if not src.exists():
                sys.exit(f"Workbook not found: {src}")
            if src.resolve() != WORKBOOK.resolve():
                shutil.copy(src, WORKBOOK)
            print(f"Using workbook: {src}")
            argv.remove(a)
            return WORKBOOK
    if not WORKBOOK.exists():
        sys.exit('No workbook yet. Run:  python scripts/<script>.py "path/to/workbook.xlsx"')
    return WORKBOOK
