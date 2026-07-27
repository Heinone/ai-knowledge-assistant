# Business Knowledge Base Agent — Risks

## 1. Data privacy

Risk:
The system may process private company documents.

Mitigation:
Use backend-only API keys, avoid exposing secrets in frontend code, restrict access, and define storage/retention rules.

## 2. Hallucination

Risk:
RAG reduces hallucination but does not eliminate it.

Mitigation:
Use source-grounded prompts, citations, refusal behavior, answer validation, evals, and human escalation for sensitive cases.

## 3. Stale documents

Risk:
The agent may answer from outdated policies.

Mitigation:
Track document source, upload date, version, and re-ingestion process.

## 4. Bad retrieval

Risk:
Vector search may retrieve irrelevant chunks or miss the right chunk.

Mitigation:
Log retrieved chunks, tune chunk size, use evals, and review failed questions.

## 5. Cost spikes

Risk:
Large documents, too many chunks, or long prompts increase API cost.

Mitigation:
Limit retrieved chunks, log token usage, cap output tokens, and monitor `/usage`.

## 6. Prompt injection

Risk:
User questions or document text may try to override system rules.

Mitigation:
Treat documents as data, ignore instructions inside retrieved content, validate final answers, and test adversarial prompts.

## 7. Overpromising

Risk:
Selling this as “hallucination-free” is false.

Mitigation:
Position it as a grounded assistant that cites sources and refuses when evidence is insufficient.