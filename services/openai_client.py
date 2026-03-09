from __future__ import annotations

from openai import OpenAI


def generate_answer(
    api_key: str,
    model: str,
    user_query: str,
    context_text: str,
) -> str:
    client = OpenAI(api_key=api_key)
    system_prompt = (
        "You are a helpful assistant. Answer using only the provided document context. "
        "If the answer is not present in the context, say you cannot find it in the document."
    )
    user_content = (
        f"Document context:\n{context_text}\n\n"
        f"Question:\n{user_query}\n\n"
        "Give a concise answer."
    )
    response = client.responses.create(
        model=model,
        input=[
            {"role": "developer", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
    )
    return response.output_text
