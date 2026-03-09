from __future__ import annotations

from pathlib import Path
from typing import Any

from PyPDF2 import PdfReader


def discover_pdf_files(root_dir: Path) -> list[Path]:
    files = sorted(root_dir.glob("*.pdf"), key=lambda p: p.name.lower())
    return [path for path in files if path.is_file()]


def extract_pdf_text(file_path: Path) -> tuple[str, int]:
    reader = PdfReader(str(file_path))
    chunks: list[str] = []
    for page in reader.pages:
        chunks.append(page.extract_text() or "")
    text = "\n\n".join(chunks).strip()
    return text, len(reader.pages)


def load_documents(root_dir: Path) -> tuple[list[dict[str, Any]], list[str]]:
    docs: list[dict[str, Any]] = []
    errors: list[str] = []

    for file_path in discover_pdf_files(root_dir):
        try:
            text, page_count = extract_pdf_text(file_path)
            excerpt = (text[:500] + "...") if len(text) > 500 else text
            docs.append(
                {
                    "name": file_path.name,
                    "path": str(file_path),
                    "page_count": page_count,
                    "char_count": len(text),
                    "excerpt": excerpt,
                    "text": text,
                }
            )
        except Exception as exc:
            errors.append(f"{file_path.name}: {exc}")

    return docs, errors


def build_context_text(documents: list[dict[str, Any]], max_chars: int) -> str:
    combined = []
    used = 0

    for doc in documents:
        chunk = f"Document: {doc['name']}\n{doc['text']}\n"
        remaining = max_chars - used
        if remaining <= 0:
            break
        if len(chunk) > remaining:
            chunk = chunk[:remaining]
        combined.append(chunk)
        used += len(chunk)

    return "\n\n".join(combined).strip()
