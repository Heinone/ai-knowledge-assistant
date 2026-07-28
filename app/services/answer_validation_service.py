from app.config.company_config import load_company_config


def is_refusal(answer: str, refusal_message: str) -> bool:
    return refusal_message.lower() in answer.lower()


def validate_answer(
    question: str,
    answer: str,
    sources: list[dict],
) -> dict:

    company = load_company_config()
    refusal_message = company["refusal_message"]

    if not answer.strip():
        return {
            "valid": False,
            "reason": "empty_answer",
            "safe_answer": refusal_message,
        }

    if is_refusal(answer, refusal_message):
        return {
            "valid": True,
            "reason": "refusal",
            "safe_answer": answer,
        }

    if not sources:
        return {
            "valid": False,
            "reason": "answer_without_sources",
            "safe_answer": refusal_message,
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
                "safe_answer": refusal_message,
            }

    return {
        "valid": True,
        "reason": "ok",
        "safe_answer": answer,
    }