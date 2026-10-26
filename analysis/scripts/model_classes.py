"""
Model-class rule used by the approach x model-class figure.

Each study is placed at its most advanced model class:
ML (feature engineering + classical ML) -> deep learning (incl. pre-trained transformers) -> LLMs -> LLM agents.
"""
import re

import config as C

AGENT_RE = r"\bagent|agentic|tool use|tool-use|\breact\b"


def era_of(row, is_agent):
    fam = row["model_family_set"]
    if re.search(C.AGENTIC_LLM_CLASS, str(row.get("model_class", "")), re.I):
        return "Agentic LLMs"
    if is_agent:
        return "LLM agents"
    if "LLM / LVLM" in fam:
        return "LLMs"
    if "Transformer / PLM" in fam or "Deep learning" in fam:   # pre-trained transformers count as deep learning
        return "Deep learning"
    return "Feature eng. + classical ML"


def eras(df):
    text = df[["model_class", "model", "learning"]].fillna("").agg(" ".join, axis=1).str.lower()
    df["agent"] = text.str.contains(AGENT_RE) | df.learning_set.map(lambda s: "Agentic / tool use" in s)
    df["era"] = [era_of(r, a) for (_, r), a in zip(df.iterrows(), df.agent)]
    return df
