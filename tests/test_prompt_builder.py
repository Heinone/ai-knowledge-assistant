import unittest

from app.models.assistant_mode import AssistantMode
from app.services.prompt_builder import build_rag_prompt


class PromptBuilderTests(unittest.TestCase):
    def test_customer_support_prompt_contains_grounding_rules(self):
        prompt = build_rag_prompt(
            question="What is the refund policy?",
            context_chunks=[
                {
                    "source": "refunds.pdf",
                    "text": "Refunds are accepted within 30 days.",
                }
            ],
            company_name="Example Company",
            mode=AssistantMode.CUSTOMER_SUPPORT,
            fallback_message="I do not know.",
        )

        self.assertIn(
            "Act as a customer service assistant",
            prompt,
        )

        self.assertIn(
            "Refunds are accepted within 30 days.",
            prompt,
        )

        self.assertIn(
            "I do not know.",
            prompt,
        )

    def test_custom_guide_is_added(self):
        prompt = build_rag_prompt(
            question="How should I format the response?",
            context_chunks=[],
            company_name="Example Company",
            mode=AssistantMode.INTERNAL_KNOWLEDGE,
            fallback_message="No internal information found.",
            custom_guide="Use the term team member instead of employee.",
        )

        self.assertIn(
            "Use the term team member instead of employee.",
            prompt,
        )

        self.assertIn(
            "must not override the grounding and safety rules",
            prompt,
        )


if __name__ == "__main__":
    unittest.main()