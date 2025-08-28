from typing import Dict, Any, List, Optional
from questions_cli_app.services.llm import LLMClient
from questions_cli_app import config
import orjson


def _complete_question_prompt(question: str, lang: str = "en") -> str:
    return config.MCQ_PROMPT_FOR_COMPLETE_QUESTION.replace("{question}", question)


def _keyword_prompt(keyword: str, n: int, lang: str = "en") -> str:
    return config.MCQ_PROMPT_FOR_KEYWORD.replace("{keyword}", keyword).replace("{n}", str(n))


def _topic_prompt(question: str, subjects_hint: Optional[str] = None) -> str:
    base = config.TOPIC_GENERATION_PROMPT.replace("{question}", question)
    if subjects_hint:
        base += (
            "\nSTRICT CONSTRAINTS:" \
            "\n- 'core_topic' MUST be EXACTLY one of these (case-sensitive): [" + subjects_hint + "]" \
            "\n- Do NOT invent new subjects. If unsure, pick the closest valid subject from the list." \
            "\n- Return ONLY JSON with the exact keys specified; no commentary."
        )
    return base


def _safe_parse_json(text: str):
    try:
        return orjson.loads(text)
    except Exception:
        try:
            start = text.find("{")
            if start == -1:
                start = text.find("[")
            if start == -1:
                raise ValueError("No JSON found")
            end = max(text.rfind("}"), text.rfind("]")) + 1
            return orjson.loads(text[start:end])
        except Exception as e:
            raise e


def _normalize_mcq(item: Dict[str, Any]) -> Dict[str, Any]:
    question = str(item.get("question", "")).strip()
    options = item.get("options") or []
    if not isinstance(options, list):
        options = []
    options = [str(x) for x in options][:4]
    while len(options) < 4:
        options.append("")
    correct = str(item.get("correct_option", "")).strip().upper()
    if correct not in {"A", "B", "C", "D"}:
        correct = "A"
    explanation = item.get("explanation")
    accepted_long_answer = item.get("accepted_long_answer")
    detailed = item.get("detailed_explanation") or {}
    if isinstance(detailed, dict):
        options_map = detailed.get("options")
        if not isinstance(options_map, dict):
            detailed = {"options": {}}
    else:
        detailed = {"options": {}}
    return {
        "question": question,
        "options": options,
        "correct_option": correct,
        "explanation": explanation if isinstance(explanation, str) else "",
        "accepted_long_answer": accepted_long_answer if isinstance(accepted_long_answer, str) else "",
        "detailed_explanation": detailed,
    }


def generate_mcq_from_question(question: str, lang: str = "en") -> Dict[str, Any]:
    client = LLMClient()
    prompt = _complete_question_prompt(question, lang)
    resp = client._complete(prompt)
    data = _safe_parse_json(resp)
    if isinstance(data, dict):
        return _normalize_mcq(data)
    if isinstance(data, list) and data:
        return _normalize_mcq(data[0])
    return _normalize_mcq({})


def generate_mcqs_from_keyword(keyword: str, n: int | None = None, lang: str = "en") -> List[Dict[str, Any]]:
    client = LLMClient()
    count = n if n is not None else config.NUM_QUESTIONS
    prompt = _keyword_prompt(keyword, n=count, lang=lang)
    resp = client._complete(prompt)
    data = _safe_parse_json(resp)
    if isinstance(data, dict):
        return [_normalize_mcq(data)]
    if isinstance(data, list):
        return [_normalize_mcq(x if isinstance(x, dict) else {}) for x in data][:max(1, count)]
    return [_normalize_mcq({})]


def generate_topic_metadata(question: str, subjects_hint: Optional[str] = None) -> Dict[str, Any]:
    client = LLMClient()
    prompt = _topic_prompt(question, subjects_hint)
    resp = client._complete(prompt)
    data = _safe_parse_json(resp)
    if not isinstance(data, dict):
        return {"topic": "General", "definition": "", "prerequisites": [], "core_topic": "General"}
    # minimal normalization
    out = {
        "topic": str(data.get("topic", "General"))[:80],
        "definition": str(data.get("definition", "")),
        "prerequisites": data.get("prerequisites") if isinstance(data.get("prerequisites"), list) else [],
        "core_topic": str(data.get("core_topic", "General")),
    }
    return out 