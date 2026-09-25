"""Simple sanity check: one chat completion call against Groq."""

import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

MODEL = "openai/gpt-oss-120b"

client = Groq(api_key=os.environ["GROQ_API_KEY"])

response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "user", "content": "Responde en una sola frase: ¿qué es un behavior tree?"}
    ],
)

print(f"Modelo: {MODEL}")
print(f"Respuesta: {response.choices[0].message.content}")
print(f"Tokens: prompt={response.usage.prompt_tokens} completion={response.usage.completion_tokens}")
