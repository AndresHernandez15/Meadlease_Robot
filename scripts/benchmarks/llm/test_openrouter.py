"""Simple sanity check: one chat completion call against OpenRouter (OpenAI-compatible API)."""

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MODEL = "nvidia/nemotron-3.5-lightning:free"

client = OpenAI(api_key=os.environ["OPENROUTER_API_KEY"], base_url="https://openrouter.ai/api/v1")

response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "user", "content": "Responde en una sola frase: ¿qué es un behavior tree?"}
    ],
)

print(f"Modelo: {MODEL}")
print(f"Respuesta: {response.choices[0].message.content}")
print(f"Tokens: prompt={response.usage.prompt_tokens} completion={response.usage.completion_tokens}")
