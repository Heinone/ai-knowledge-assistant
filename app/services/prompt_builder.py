def build_rag_prompt(
    question: str,
    context_chunks: list[dict],
    company_name: str,
) -> str:
    context_text = ""

    for i, chunk in enumerate(context_chunks, start=1):
        source = chunk.get("source", "unknown")
        text = chunk.get("text", "")

        context_text += f"\n[Source {i}: {source}]\n{text}\n"

    return f"""


Context:
{context_text}

Question:
{question}

Answer:
""".strip()