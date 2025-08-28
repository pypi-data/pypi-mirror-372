import os
import orjson
from typing import Dict, Any, Optional
from loguru import logger
from tqdm import tqdm
import pandas as pd
from questions_cli_app.core.csv_io import read_csv_rows, write_csv_with_column
from questions_cli_app.core.classify import is_complete_question
from questions_cli_app.core.generate import generate_mcq_from_question, generate_mcqs_from_keyword, generate_topic_metadata
from questions_cli_app.core.ingest import build_topic_doc_from_generated, build_question_doc_from_generated
from questions_cli_app.core.subjects import load_subjects, choose_subject
from questions_cli_app.services.mongo import MongoRepo
from questions_cli_app.utils import ensure_runs_dir, setup_logging, utc_iso
from questions_cli_app import config
from questions_cli_app.subject_settings import subject_illustration_lookup, subject_list



def process_csv(input_csv: str, delimiter: str = ",", dry_run: bool = False, limit: int | None = None, subjects_file: Optional[str] = None) -> Dict[str, Any]:
    ts = utc_iso().replace(":", "-")
    runs_path = ensure_runs_dir(ts)
    setup_logging(ts, runs_path)

    totals = {"rows": 0, "questions": 0, "keywords": 0, "errors": 0, "generated": 0, "inserted_topics": 0, "inserted_questions": 0}
    classified_jsonl = os.path.join(runs_path, "classified.jsonl")
    generated_jsonl = os.path.join(runs_path, "generated.jsonl")
    labeled_csv = os.path.join(runs_path, "labeled.csv")

    labels = []
    inserted_topic_ids: list[str] = []
    inserted_question_ids: list[str] = []

    try:
        total_rows = len(pd.read_csv(input_csv, delimiter=delimiter))
        if limit is not None:
            total_rows = min(total_rows, limit)
    except Exception:
        total_rows = None

    subjects_map = None
    subjects_hint = None
    if subjects_file:
        subjects_map = load_subjects(subjects_file)
    else:
        subjects_map = {name: subject_illustration_lookup.get(name, []) for name in subject_list}
    if subjects_map:
        subject_names_sorted = sorted(subjects_map.keys())
        subjects_hint = ", ".join([f'"{s}"' for s in subject_names_sorted])

    logger.info(f"Starting classification+generation for {input_csv} using model={os.getenv('LLM_MODEL') or config.MODEL_NAME}")

    def _process_rows(repo: Optional[MongoRepo]):
        nonlocal totals, labels, inserted_topic_ids, inserted_question_ids
        with open(classified_jsonl, "wb") as cf, open(generated_jsonl, "wb") as gf:
            with tqdm(total=total_rows, desc="Processing", unit="row") as pbar:
                for row in read_csv_rows(input_csv, delimiter=delimiter, limit=limit):
                    totals["rows"] += 1
                    text = row.get("input", "")
                    try:
                        is_q = is_complete_question(text)
                        label = "question" if is_q else "keyword"
                        labels.append(label)
                        totals["questions" if is_q else "keywords"] += 1

                        cf.write(orjson.dumps({**row, "label": label}))
                        cf.write(b"\n")

                        items = []
                        if is_q:
                            data = generate_mcq_from_question(text)
                            items = [data]
                        else:
                            items = generate_mcqs_from_keyword(text, n=config.NUM_QUESTIONS)

                        gf.write(orjson.dumps({"row_index": row["row_index"], "input": text, "items": items}))
                        gf.write(b"\n")
                        totals["generated"] += len(items)

                        if not dry_run and repo:
                            for it in items:
                                topic_meta = generate_topic_metadata(it.get("question", text), subjects_hint=subjects_hint)
                                topic_name = topic_meta.get("topic") or it.get("topic_name") or "General"
                                topic_def = topic_meta.get("definition") or ""
                                topic_doc = build_topic_doc_from_generated(topic_name, topic_def, source="search_query")
                                if subjects_map:
                                    core_topic = topic_meta.get("core_topic") or ""
                                    chosen_subject = choose_subject(subjects_map, core_topic, context_text=topic_name)
                                    if chosen_subject:
                                        topic_doc["subject"] = chosen_subject
                                        topic_doc["department"] = chosen_subject
                                        topic_doc["subjectIllustrations"] = subjects_map.get(chosen_subject, [])
                                topic_id = repo.insert_topic(topic_doc)
                                totals["inserted_topics"] += 1
                                inserted_topic_ids.append(str(topic_id))

                                q_doc = build_question_doc_from_generated(
                                    item=it,
                                    topic_id=topic_id,
                                    topic_name=topic_name,
                                    topic_definition=topic_def,
                                    source="search_query",
                                )
                                q_id = repo.insert_question(q_doc)
                                totals["inserted_questions"] += 1
                                inserted_question_ids.append(str(q_id))
                    except Exception as e:
                        totals["errors"] += 1
                        if labels:
                            labels[-1] = "error"
                        logger.error(f"Row {row.get('row_index')}: {e}")
                    finally:
                        pbar.update(1)

    if dry_run:
        _process_rows(None)
    else:
        with MongoRepo() as repo:
            logger.info(f"Writing to MongoDB db={repo.db.name}")
            _process_rows(repo)

    try:
        write_csv_with_column(input_csv, delimiter, labeled_csv, "label", labels)
    except Exception as e:
        logger.error(f"Failed writing labeled CSV: {e}")

    summary = {
        "input": input_csv,
        "runs_path": runs_path,
        **totals,
        "inserted_topic_ids": inserted_topic_ids,
        "inserted_question_ids": inserted_question_ids,
    }
    with open(os.path.join(runs_path, "summary.json"), "wb") as s:
        s.write(orjson.dumps(summary, option=orjson.OPT_INDENT_2))

    ids_path = os.path.join(runs_path, "inserted_ids.json")
    with open(ids_path, "wb") as f:
        f.write(orjson.dumps({
            "topic_ids": inserted_topic_ids,
            "question_ids": inserted_question_ids,
        }, option=orjson.OPT_INDENT_2))

    logger.info(
        f"Done. Rows={totals['rows']} Questions={totals['questions']} Keywords={totals['keywords']} Generated={totals['generated']} InsertedQ={totals['inserted_questions']} InsertedT={totals['inserted_topics']} Errors={totals['errors']}"
    )
    return summary