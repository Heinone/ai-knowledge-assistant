import os
from dotenv import load_dotenv

load_dotenv()

from anthropic import Anthropic

from app.llm.base import LLMProvider


class ClaudeProvider(LLMProvider):
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is missing")

        self.client = Anthropic(api_key=api_key)
        self.model = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5")

    def generate(self, prompt: str) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        print(
            {
                "provider": "claude",
                "model": self.model,
                "usage": response.usage,
            }
        )

        parts = []
        for block in response.content:
            if block.type == "text":
                parts.append(block.text)

        return "\n".join(parts)