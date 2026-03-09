from __future__ import annotations

import json
from pathlib import Path
import time
from datetime import datetime, timezone
from typing import Any

from pymongo import MongoClient
from pymongo.collection import Collection

DEBUG_LOG_PATH = Path(__file__).resolve().parent.parent / "debug-efdcc3.log"
DEBUG_SESSION_ID = "efdcc3"
DEBUG_RUN_ID = "pre-fix"


def _safe_uri_meta(uri: str) -> dict[str, Any]:
    scheme = "unknown"
    if "://" in uri:
        scheme = uri.split("://", 1)[0]
    host_part = uri.split("@")[-1] if "@" in uri else uri
    host = host_part.split("/")[0].split("?")[0]
    return {
        "scheme": scheme,
        "is_srv": uri.startswith("mongodb+srv://"),
        "host_preview": host[:40],
        "has_atlas_host": ".mongodb.net" in uri,
    }


def _debug_log(hypothesis_id: str, location: str, message: str, data: dict[str, Any]) -> None:
    payload = {
        "sessionId": DEBUG_SESSION_ID,
        "runId": DEBUG_RUN_ID,
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data,
        "timestamp": int(time.time() * 1000),
    }
    try:
        with DEBUG_LOG_PATH.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=True) + "\n")
    except Exception:
        pass


def get_collection(uri: str, db_name: str, collection_name: str) -> Collection:
    # region agent log
    _debug_log(
        "H1",
        "services/mongo_logger.py:get_collection",
        "Creating MongoClient",
        {
            "db_name": db_name,
            "collection_name": collection_name,
            "uri_meta": _safe_uri_meta(uri),
            "serverSelectionTimeoutMS": 5000,
        },
    )
    # endregion
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    # region agent log
    _debug_log(
        "H3",
        "services/mongo_logger.py:get_collection",
        "MongoClient object created",
        {"lazy_connect_expected": True},
    )
    # endregion
    return client[db_name][collection_name]


def log_chat_turn(
    uri: str,
    db_name: str,
    collection_name: str,
    user_query: str,
    assistant_answer: str,
    model: str,
    source_docs: list[str],
    latency_ms: int,
    status: str = "ok",
    error: str | None = None,
) -> None:
    # region agent log
    _debug_log(
        "H3",
        "services/mongo_logger.py:log_chat_turn",
        "log_chat_turn entry",
        {
            "status": status,
            "model": model,
            "source_docs_count": len(source_docs),
            "incoming_latency_ms": latency_ms,
        },
    )
    # endregion
    collection = get_collection(uri, db_name, collection_name)
    payload: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc),
        "user_query": user_query,
        "assistant_answer": assistant_answer,
        "model": model,
        "source_docs": source_docs,
        "latency_ms": latency_ms,
        "status": status,
    }
    if error:
        payload["error"] = error
    try:
        result = collection.insert_one(payload)
        # region agent log
        _debug_log(
            "H3",
            "services/mongo_logger.py:log_chat_turn",
            "insert_one success",
            {"inserted_id_present": bool(result.inserted_id)},
        )
        # endregion
    except Exception as exc:
        # region agent log
        _debug_log(
            "H2",
            "services/mongo_logger.py:log_chat_turn",
            "insert_one failed",
            {"error_type": type(exc).__name__, "error_text": str(exc)[:500]},
        )
        # endregion
        raise


def fetch_recent_logs(
    uri: str,
    db_name: str,
    collection_name: str,
    limit: int = 20,
) -> list[dict[str, Any]]:
    collection = get_collection(uri, db_name, collection_name)
    try:
        cursor = collection.find().sort("timestamp", -1).limit(limit)
        items = list(cursor)
        # region agent log
        _debug_log(
            "H4",
            "services/mongo_logger.py:fetch_recent_logs",
            "fetch_recent_logs success",
            {"limit": limit, "result_count": len(items)},
        )
        # endregion
        return items
    except Exception as exc:
        # region agent log
        _debug_log(
            "H4",
            "services/mongo_logger.py:fetch_recent_logs",
            "fetch_recent_logs failed",
            {"error_type": type(exc).__name__, "error_text": str(exc)[:500]},
        )
        # endregion
        raise
