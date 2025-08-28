from loguru import logger
import hashlib
import os
from datetime import datetime

RUNS_DIR = os.path.join(os.getcwd(), "runs")


def ensure_runs_dir(ts: str) -> str:
    path = os.path.join(RUNS_DIR, ts)
    os.makedirs(path, exist_ok=True)
    return path


def stable_id(*parts: str) -> str:
    m = hashlib.sha256()
    for p in parts:
        m.update((p + "\u241F").encode("utf-8"))
    return m.hexdigest()[:24]


def utc_iso() -> str:
    return datetime.utcnow().isoformat()


def setup_logging(ts: str, runs_path: str):
    log_path = os.path.join(runs_path, "run.log")
    logger.remove()
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    logger.add(lambda msg: print(msg, end=""), level=level)
    logger.add(log_path, serialize=False, rotation="10 MB", level=level)
    return log_path
