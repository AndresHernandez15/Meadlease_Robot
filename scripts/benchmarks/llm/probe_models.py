"""Probe every candidate model (Groq + OpenRouter free) with one fixed prompt.

Not a real performance/quality benchmark yet — just validates which models
respond at all, and gives a first read on latency, before narrowing down the
list for the real benchmark.
"""

import os
import time

from dotenv import load_dotenv
from groq import Groq
from openai import OpenAI

from list_models import groq_chat_models, openrouter_free_models

load_dotenv()

PROMPT = "Responde en una sola frase: ¿qué es un behavior tree?"
DELAY_BETWEEN_CALLS_S = 2  # evita rate-limit del pool compartido de OpenRouter free


def probe(label: str, call) -> dict:
    start = time.perf_counter()
    try:
        response = call()
        elapsed = time.perf_counter() - start
        content = response.choices[0].message.content
        usage = response.usage
        return {
            "model": label,
            "ok": True,
            "elapsed_s": round(elapsed, 2),
            "prompt_tokens": usage.prompt_tokens if usage else None,
            "completion_tokens": usage.completion_tokens if usage else None,
            "preview": (content or "").strip().replace("\n", " ")[:80],
        }
    except Exception as e:
        elapsed = time.perf_counter() - start
        return {"model": label, "ok": False, "elapsed_s": round(elapsed, 2), "error": str(e)[:150]}


def main() -> None:
    groq_client = Groq(api_key=os.environ["GROQ_API_KEY"])
    openrouter_client = OpenAI(api_key=os.environ["OPENROUTER_API_KEY"], base_url="https://openrouter.ai/api/v1")

    results = []

    for model in groq_chat_models():
        results.append(
            probe(
                f"groq/{model}",
                lambda m=model: groq_client.chat.completions.create(
                    model=m, messages=[{"role": "user", "content": PROMPT}]
                ),
            )
        )
        time.sleep(DELAY_BETWEEN_CALLS_S)

    for model in openrouter_free_models():
        results.append(
            probe(
                f"openrouter/{model}",
                lambda m=model: openrouter_client.chat.completions.create(
                    model=m, messages=[{"role": "user", "content": PROMPT}]
                ),
            )
        )
        time.sleep(DELAY_BETWEEN_CALLS_S)

    ok = [r for r in results if r["ok"]]
    failed = [r for r in results if not r["ok"]]

    print(f"\n{'='*100}\nOK ({len(ok)}/{len(results)})\n{'='*100}")
    for r in ok:
        print(f"{r['model']:<45} {r['elapsed_s']:>6.2f}s  tok(p/c)={r['prompt_tokens']}/{r['completion_tokens']:<6} {r['preview']}")

    print(f"\n{'='*100}\nFALLARON ({len(failed)}/{len(results)})\n{'='*100}")
    for r in failed:
        print(f"{r['model']:<45} {r['elapsed_s']:>6.2f}s  {r['error']}")


if __name__ == "__main__":
    main()
