"""List candidate chat models for the LLM benchmark: Groq (all, minus non-chat
models) and OpenRouter (only the :free ones, per project decision to only
benchmark providers with a perpetual free tier, not an expiring credit)."""

import os

from dotenv import load_dotenv
from groq import Groq
from openai import OpenAI

load_dotenv()

GROQ_EXCLUDE_KEYWORDS = ("whisper", "orpheus", "prompt-guard", "guard", "safeguard")


def groq_chat_models() -> list[str]:
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    models = client.models.list().data
    return sorted(
        m.id for m in models if not any(kw in m.id.lower() for kw in GROQ_EXCLUDE_KEYWORDS)
    )


OPENROUTER_EXCLUDE_KEYWORDS = ("content-safety", "guard")


def openrouter_free_models() -> list[str]:
    client = OpenAI(api_key=os.environ["OPENROUTER_API_KEY"], base_url="https://openrouter.ai/api/v1")
    models = client.models.list().data
    return sorted(
        m.id
        for m in models
        if m.id.endswith(":free") and not any(kw in m.id.lower() for kw in OPENROUTER_EXCLUDE_KEYWORDS)
    )


if __name__ == "__main__":
    groq = groq_chat_models()
    openrouter = openrouter_free_models()

    print(f"Groq — {len(groq)} modelos de chat:")
    for m in groq:
        print(f"  {m}")

    print(f"\nOpenRouter — {len(openrouter)} modelos :free:")
    for m in openrouter:
        print(f"  {m}")
