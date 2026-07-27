import os
from collections.abc import Iterator
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

from app.llm.base import LLMProvider

load_dotenv()


class OpenAIProvider(LLMProvider):
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is missing")

        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv("DEFAULT_MODEL", "gpt-5-mini")

    def generate(self, prompt: str) -> str:
        result = self.generate_with_usage(prompt)
        return result["answer"]

    def generate_with_usage(self, prompt: str) -> dict[str, Any]:
        response = self.client.responses.create(
            model=self.model,
            reasoning={"effort": "low"},
            max_output_tokens=500,
            input=prompt,
        )

        usage = response.usage

        usage_data = {
            "model": self.model,
            "status": response.status,
            "input_tokens": usage.input_tokens if usage else None,
            "output_tokens": usage.output_tokens if usage else None,
            "total_tokens": usage.total_tokens if usage else None,
            "reasoning_tokens": (
                usage.output_tokens_details.reasoning_tokens
                if usage and usage.output_tokens_details
                else None
            ),
        }

        print(
            {
                "provider": "openai",
                **usage_data,
            }
        )

        if response.status == "incomplete":
            print(
                {
                    "incomplete_details": (
                        response.incomplete_details.model_dump()
                        if response.incomplete_details
                        else None
                    ),
                    "output_text": response.output_text,
                }
            )

            return {
                "answer": (
                    response.output_text
                    or "I was unable to complete the answer."
                ),
                "usage": usage_data,
            }

        if not response.output_text:
            print(response.model_dump_json(indent=2))

            return {
                "answer": "The model returned no visible text. Check server logs.",
                "usage": usage_data,
            }

        return {
            "answer": response.output_text,
            "usage": usage_data,
        }

    def stream(self, prompt: str) -> Iterator[str]:
        stream = self.client.responses.create(
            model=self.model,
            reasoning={"effort": "low"},
            max_output_tokens=500,
            input=prompt,
            stream=True,
        )

        for event in stream:
            if event.type == "response.output_text.delta":
                yield event.delta