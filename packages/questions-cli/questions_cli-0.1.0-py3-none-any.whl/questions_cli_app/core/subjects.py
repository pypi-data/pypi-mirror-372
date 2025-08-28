import os
import json
from typing import Dict, List, Optional

try:
    import yaml  # type: ignore
except Exception:
    yaml = None

import pandas as pd
import difflib


def load_subjects(path: str) -> Dict[str, List[str]]:
    if not path or not os.path.exists(path):
        raise FileNotFoundError(f"Subjects file not found: {path}")

    ext = os.path.splitext(path)[1].lower()
    if ext in [".yml", ".yaml"]:
        if yaml is None:
            raise RuntimeError("pyyaml not installed; cannot read YAML subjects file")
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if isinstance(data, dict):
            return {str(k): list(v or []) for k, v in data.items()}
        if isinstance(data, list):
            out: Dict[str, List[str]] = {}
            for item in data:
                subj = str(item.get("subject", "")).strip()
                if not subj:
                    continue
                ill = item.get("illustrations") or item.get("subjectIllustrations") or []
                out[subj] = list(ill or [])
            return out
        raise ValueError("Unsupported YAML structure for subjects")

    if ext == ".json":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return {str(k): list(v or []) for k, v in data.items()}
        if isinstance(data, list):
            out: Dict[str, List[str]] = {}
            for item in data:
                subj = str(item.get("subject", "")).strip()
                if not subj:
                    continue
                ill = item.get("illustrations") or item.get("subjectIllustrations") or []
                out[subj] = list(ill or [])
            return out
        raise ValueError("Unsupported JSON structure for subjects")

    df = pd.read_csv(path)
    if "subject" not in df.columns:
        raise ValueError("CSV subjects file must include 'subject' column")
    out: Dict[str, List[str]] = {}
    for _, row in df.fillna("").iterrows():
        subj = str(row.get("subject", "")).strip()
        if not subj:
            continue
        raw = str(row.get("illustrations", "")).strip()
        if raw:
            if "|" in raw:
                ills = [p.strip() for p in raw.split("|") if p.strip()]
            elif ";" in raw:
                ills = [p.strip() for p in raw.split(";") if p.strip()]
            else:
                ills = [p.strip() for p in raw.split(",") if p.strip()]
        else:
            ills = []
        out[subj] = ills
    return out


def choose_subject(subjects_map: Dict[str, List[str]], candidate: Optional[str], context_text: Optional[str] = None) -> Optional[str]:
    if not subjects_map:
        return None
    names = list(subjects_map.keys())
    # direct and case-insensitive match first
    if candidate:
        for n in names:
            if n == candidate:
                return n
        low = candidate.lower().strip()
        for n in names:
            if n.lower() == low:
                return n
        # fuzzy
        match = difflib.get_close_matches(candidate, names, n=1, cutoff=0.6)
        if match:
            return match[0]
    # fallback: use context_text for fuzzy clue
    if context_text:
        match = difflib.get_close_matches(context_text, names, n=1, cutoff=0.2)
        if match:
            return match[0]
    return None 