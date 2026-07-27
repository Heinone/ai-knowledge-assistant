from app.constants import REFUSAL_TEXT


def is_refusal(answer: str) -> bool:
    return REFUSAL_TEXT.lower() in answer.lower()


def validate_answer(
    question: str,
    answer: str,
    sources: list[dict],
) -> dict:
    if not answer.strip():
        return {
            "valid": False,
            "reason": "empty_answer",
            "safe_answer": REFUSAL_TEXT,
        }

    if is_refusal(answer):
        return {
            "valid": True,
            "reason": "refusal",
            "safe_answer": answer,
        }

    if not sources:
        return {
            "valid": False,
            "reason": "answer_without_sources",
            "safe_answer": REFUSAL_TEXT,
        }

    question_lower = question.lower()
    source_text = " ".join(
        source.get("text", "")
        for source in sources
    ).lower()

    risky_topics = [
        "medical advice",
        "legal advice",
        "financial advice",
    ]

    for topic in risky_topics:
        if topic in question_lower and topic not in source_text:
            return {
                "valid": False,
                "reason": f"unsupported_topic:{topic}",
                "safe_answer": REFUSAL_TEXT,
            }

    return {
        "valid": True,
        "reason": "ok",
        "safe_answer": answer,
    }