import json
from pathlib import Path

from app.services.ingestion_service import build_index_from_directory
from app.services.chat_service import answer_question
from app.services.session_service import reset_greeting


REFUSAL_TEXT = "I could not find enough information"


def load_eval_cases():
    path = Path("data/evals/regression_cases.json")
    return json.loads(path.read_text(encoding="utf-8"))


def answer_contains_expected(answer: str, expected_terms: list[str]) -> bool:
    answer_lower = answer.lower()
    return all(term.lower() in answer_lower for term in expected_terms)


def has_expected_source(sources: list[dict], expected_source: str | None) -> bool:
    if expected_source is None:
        return True

    for source in sources:
        if source.get("source") == expected_source:
            return True

    return False


def refused(answer: str) -> bool:
    return REFUSAL_TEXT.lower() in answer.lower()


def run_eval_case(case: dict) -> dict:
    result = answer_question(case["question"])

    answer = result["answer"]
    sources = result["sources"]

    contains_ok = answer_contains_expected(
        answer=answer,
        expected_terms=case["expected_contains"],
    )

    source_ok = has_expected_source(
        sources=sources,
        expected_source=case["expected_source"],
    )

    refusal_ok = refused(answer) if case["should_refuse"] else not refused(answer)

    passed = contains_ok and source_ok and refusal_ok

    return {
        "id": case["id"],
        "type": case["type"],
        "question": case["question"],
        "passed": passed,
        "contains_ok": contains_ok,
        "source_ok": source_ok,
        "refusal_ok": refusal_ok,
        "answer": answer,
        "sources": [source.get("source") for source in sources],
    }


def main():
    print("Building local index...")
    build_index_from_directory(
        path="data/raw/test_fixtures/nordictrail",
        chunk_size=512,
        chunk_overlap=50,
    )

    reset_greeting()

    cases = load_eval_cases()

    results = []
    for case in cases:
        print("\n" + "=" * 80)
        print(f"Running eval: {case['id']}")

        result = run_eval_case(case)
        results.append(result)

        print("PASSED:", result["passed"])
        print("contains_ok:", result["contains_ok"])
        print("source_ok:", result["source_ok"])
        print("refusal_ok:", result["refusal_ok"])
        print("sources:", result["sources"])
        print("answer:", result["answer"])

    passed_count = sum(1 for result in results if result["passed"])
    total_count = len(results)

    print("\n" + "#" * 80)
    print(f"SUMMARY: {passed_count}/{total_count} passed")

    output_path = Path("data/evals/latest_eval_results.json")
    output_path.write_text(
        json.dumps(results, indent=2),
        encoding="utf-8",
    )

    print(f"Saved results to {output_path}")


if __name__ == "__main__":
    main()