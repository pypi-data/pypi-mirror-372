import re
from typing import Literal
from questions_cli_app.services.llm import LLMClient


def _heuristic(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return False
    if t.endswith("?"):
        return True
    if re.match(r"^(who|what|when|where|why|how|can|does|is|are|should)\b", t, re.I):
        return True
    return False


def is_complete_question(text: str) -> bool:
    try:
        client = LLMClient()
        label: Literal["question", "keyword"] = client.classify_text(text)
        return label == "question"
    except Exception:
        return _heuristic(text) 