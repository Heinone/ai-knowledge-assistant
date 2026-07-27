from app.llm.openai_provider import OpenAIProvider

prompt = """
You are answering questions for NordicTrail Gear.

Use only the context below.
If the answer is not in the context, say:
"I could not find enough information in the provided documents to answer that confidently."

Context:
Refund policy:
Customers may return unused products within 30 days of purchase for a full refund.
Used hiking boots, tents, backpacks, and jackets are not eligible for a refund unless defective.
Items returned after 30 days are not eligible.

Shipping policy:
Shipping to Indonesia is available and usually takes 7 to 14 business days.

Question:
Can I return hiking boots after using them once??
"""

openai_provider = OpenAIProvider()

print("\n" + "=" * 80)
print("OPENAI:")
print(openai_provider.generate(prompt))

try:
    from app.llm.anthropic_provider import ClaudeProvider

    claude_provider = ClaudeProvider()

    print("\n" + "=" * 80)
    print("CLAUDE:")
    print(claude_provider.generate(prompt))
except RuntimeError as error:
    print("\n" + "=" * 80)
    print("CLAUDE SKIPPED:")
    print(error)