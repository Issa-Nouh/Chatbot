from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class AppConfig:
    project_root: Path
    openai_api_key: str
    openai_model: str
    mongodb_uri: str
    mongodb_db: str
    mongodb_collection: str


def get_config() -> AppConfig:
    root = Path(__file__).resolve().parent
    return AppConfig(
        project_root=root,
        openai_api_key=os.getenv("OPENAI_API_KEY", "").strip(),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip(),
        mongodb_uri=os.getenv("MONGODB_URI", "").strip(),
        mongodb_db=os.getenv("MONGODB_DB", "chatbot_db").strip(),
        mongodb_collection=os.getenv("MONGODB_COLLECTION", "chat_logs").strip(),
    )


def missing_required_values(config: AppConfig) -> list[str]:
    missing = []
    if not config.openai_api_key:
        missing.append("OPENAI_API_KEY")
    if not config.mongodb_uri:
        missing.append("MONGODB_URI")
    return missing
