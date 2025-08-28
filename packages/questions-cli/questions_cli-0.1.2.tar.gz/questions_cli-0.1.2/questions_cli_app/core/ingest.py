from typing import Dict, Any, Tuple, List
from datetime import datetime
from bson import ObjectId
from questions_cli_app.models import TopicDoc, QuestionDoc
from questions_cli_app.utils import stable_id


def build_topic_doc_from_generated(topic_name: str, definition: str, source: str) -> Dict[str, Any]:
    topic_doc = TopicDoc(
        topic=topic_name,
        definition=definition,
        subject=None,
        core=False,
        subjectIllustrations=[],
        subjectColor=None,
        department=None,
        createdAt=datetime.utcnow(),
        updatedAt=datetime.utcnow(),
        topic_hash=None,
        chapterName=None,
        timestamp=0,
    ).model_dump(by_alias=True, exclude_none=True)
    # computed additions
    topic_doc["topic_hash"] = stable_id(topic_name or "", definition or "")[:16]
    topic_doc["source"] = source
    return topic_doc


def build_question_doc_from_generated(item: Dict[str, Any], topic_id: ObjectId, topic_name: str, topic_definition: str, source: str) -> Dict[str, Any]:
    options = item.get("options", [])
    correct_letter = item.get("correct_option")
    answer_options = []
    for idx, text in enumerate(options):
        letter = chr(65 + idx)
        answer_options.append({
            "sNo": letter,
            "option": text,
            "select": False,
            "color": None,
            "answerStatus": (letter == correct_letter)
        })

    topic_hash = stable_id(topic_name or "", topic_definition or "")

    qdoc = QuestionDoc(
        topicId=str(topic_id),
        topic=topic_name,
        topicHash=topic_hash,
        question=item.get("question", ""),
        answer=answer_options,
        explanation=item.get("explanation", ""),
        validity=True,
        difficulty_level=None,
        concept1="",
        concept2="",
        concept3="",
        question_type="multiple_choice",
        cognitive_level="understand",
        hints=[],
        trivia=[],
        primary_concept_tested="",
        createdAt=datetime.utcnow(),
        updatedAt=datetime.utcnow(),
        accepted_long_answer=item.get("accepted_long_answer", ""),
        detailed_explanation=item.get("detailed_explanation", None),
    ).model_dump(by_alias=True, exclude_none=True)

    qdoc["topicId"] = topic_id
    qdoc["source"] = source

    diff = (item.get("difficulty") or "").lower().strip()
    if diff in {"easy", "medium", "hard"}:
        qdoc["difficulty_level"] = diff
    else:
        qdoc["difficulty_level"] = None
    return qdoc 