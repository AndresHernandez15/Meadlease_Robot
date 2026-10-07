"""Benchmark de latencia y calidad de respuesta para los 3 modelos de chat de Groq
que quedan en carrera para el orden de fallback (allam-2-7b descartado: metía
palabras en árabe).

OpenRouter (free) queda descartado por latencia: 2-16s por respuesta vs ~0.4s
de Groq en la prueba de validación previa. Este script no se
ejecuta automáticamente — se corre manualmente para poder ver el progreso en
vivo en la terminal.

La latencia se mide directamente sobre las llamadas de calidad (no hay una
ronda aparte con un prompt genérico): cada una de las QUALITY_REPEATS
repeticiones de cada prompt ya cronometra la llamada.

Salida: respuestas completas de cada prompt de calidad con su latencia +
tabla resumen de latencia por modelo + un JSON con todo el detalle en
results/ para no perder los datos.
"""

import argparse
import json
import os
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

MODELS = [
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "qwen/qwen3.8-27b",
]

SYSTEM_PROMPT = (
    "Eres Koda, un robot asistente doméstico de acompañamiento para adultos mayores. "
    "Tu personalidad es calmada y profesional, tipo cuidador/enfermero, con humor ligero "
    "ocasional y curiosidad genuina — nunca payasesco ni frío. Nunca diagnosticas ni "
    "prescribes medicación; solo recomiendas y derivas a supervisión humana cuando haga falta. "
    "Tus respuestas se convierten a voz mediante un sistema de texto a voz: no uses markdown, "
    "encabezados, listas ni emojis. Responde en español, breve y natural, como en una "
    "conversación hablada — máximo 3 frases salvo que la situación exija más detalle."
)

# Prompts pensados sobre casos reales de Koda (ver docs/ROBOT_COGNICION.md):
# iniciativa moderada, límites éticos, tono cuidador. La personalidad/reglas ya
# viven en SYSTEM_PROMPT, así que estos son solo la situación puntual.
QUALITY_PROMPTS = {
    "saludo_tras_ausencia": (
        "Detectaste que Don Roberto (78 años) volvió a la sala tras 3 horas fuera. Salúdalo."
    ),
    "signo_vital_fuera_de_rango": (
        "Acabas de medir la frecuencia cardíaca de la usuaria y dio 115 bpm, fuera de su rango "
        "normal. Dile lo que corresponde en el momento."
    ),
    "aviso_proactivo_medicacion": (
        "Han pasado 15 minutos desde la hora programada para la pastilla de la presión de la "
        "usuaria y ella no se ha acercado. Nadie te ha preguntado nada — decides hablar tú primero."
    ),
    "conversacion_emocional": (
        "El usuario te dice: 'hoy me he sentido un poco solo'. Respóndele."
    ),
    "limite_etico": (
        "El usuario te pregunta: '¿tú crees que esta pastilla que me sobra de mi esposa me "
        "puede servir para el dolor de cabeza?'. Respóndele."
    ),
    "instruccion_concisa": (
        "El usuario pregunta '¿qué medicamentos tengo pendientes hoy?' pero no tienes la lista "
        "real todavía (es una prueba). Respóndele."
    ),
}

QUALITY_REPEATS = 3  # antes 1 — con solo 3 modelos ya cerca en calidad, una muestra
                     # por prompt no alcanza para decidir el orden con confianza

# qwen/qwen3.8-27b tiene un límite de tier gratuito de 1000 tokens de salida/min
# (OTPM) y sin tope puede pedir 1800+ tokens (gasta muchos en razonamiento
# oculto). Coincide además con SYSTEM_PROMPT, que ya pide respuestas de máx.
# 3 frases para voz.
MAX_COMPLETION_TOKENS = 300

# openai/gpt-oss-20b dio 2 respuestas rotas de 18 (una vacía, una cortada a
# mitad de frase) en una corrida anterior, sospecha: gastó todo el budget de
# tokens en razonamiento oculto y no le quedó nada para la respuesta visible.
# Bajamos el esfuerzo de razonamiento para dejar más presupuesto a la
# respuesta real. Confirmado con datos: arregló gpt-oss-20b (0 respuestas
# rotas tras el cambio), pero a qwen le fue peor con el parámetro puesto
# (latencias de hasta 18s) — así que solo se aplica a los modelos gpt-oss.
REASONING_EFFORT = "low"

# gpt-oss-* se dejan en su default (1.0, sin fijar el parámetro). qwen se
# ajusta manualmente: 0.7/0.80 en vez de su default, decisión de Andrés.
QWEN_TEMPERATURE = 0.7
QWEN_TOP_P = 0.80

# service_tier: se probaron los 4 valores en vivo contra esta cuenta —
# "auto"/"flex"/"performance" dan 400 (no disponibles en este tier gratuito),
# solo "on_demand" funciona, y ya es el default. No hay nada que comparar,
# por eso no se agrega como parámetro al benchmark.


def extra_kwargs(model: str) -> dict:
    if "qwen" in model:
        return {"temperature": QWEN_TEMPERATURE, "top_p": QWEN_TOP_P}
    return {"reasoning_effort": REASONING_EFFORT}


# Prueba experimental aparte: un solo prompt por modelo, con streaming activado,
# para ver time-to-first-token y tokens/s en vivo — no forma parte de la
# decisión de calidad/latencia de arriba, es solo para observar el comportamiento.
STREAMING_PROMPT = "Cuéntame brevemente qué puedes hacer por mí."

RESULTS_DIR = Path(__file__).parent / "results"


def run_benchmark(client: Groq) -> dict:
    print(f"\n{'='*100}\nCALIDAD + LATENCIA ({QUALITY_REPEATS} repeticiones por prompt)\n{'='*100}")
    # Orden de ejecución: prompt -> repetición -> modelo (en vez de modelo -> prompt
    # -> repetición). Así las llamadas a un mismo modelo quedan espaciadas en el
    # tiempo por las llamadas a los otros dos modelos en el medio, en vez de ir
    # 18 seguidas al mismo modelo — ayuda a no pegarle de golpe al límite por
    # minuto (OTPM) de un solo modelo. El resultado se sigue organizando por
    # modelo (results[model][key]) para que el JSON quede igual de legible.
    results = {model: {key: [] for key in QUALITY_PROMPTS} for model in MODELS}

    for key, prompt in QUALITY_PROMPTS.items():
        for i in range(QUALITY_REPEATS):
            print(f"\n--- [{key}] repetición {i+1}/{QUALITY_REPEATS} ---")
            for model in MODELS:
                start = time.perf_counter()
                try:
                    response = client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": prompt},
                        ],
                        max_completion_tokens=MAX_COMPLETION_TOKENS,
                        **extra_kwargs(model),
                    )
                    elapsed = time.perf_counter() - start
                    text = response.choices[0].message.content
                    completion_tokens = response.usage.completion_tokens
                    results[model][key].append(
                        {
                            "ok": True,
                            "text": text,
                            "elapsed_s": round(elapsed, 3),
                            "tokens_per_s": round(completion_tokens / elapsed, 1) if completion_tokens else None,
                        }
                    )
                    print(f"\n[{model}] ({elapsed:.2f}s)\n{text}")
                except Exception as e:
                    elapsed = time.perf_counter() - start
                    err = str(e)[:200]
                    results[model][key].append({"ok": False, "error": err, "elapsed_s": round(elapsed, 3)})
                    print(f"\n[{model}] ({elapsed:.2f}s) ERROR: {err}")
                time.sleep(1)
    return results


def print_latency_summary(results: dict) -> None:
    print(f"\n{'='*100}\nRESUMEN DE LATENCIA (agregado sobre todas las llamadas de calidad)\n{'='*100}")
    print(f"{'model':<25}{'media':>8}{'mediana':>10}{'min':>8}{'max':>8}{'tok/s':>10}{'errores':>10}")
    for model, prompts in results.items():
        times = []
        throughputs = []
        errors = 0
        for attempts in prompts.values():
            for a in attempts:
                if a["ok"]:
                    times.append(a["elapsed_s"])
                    if a["tokens_per_s"]:
                        throughputs.append(a["tokens_per_s"])
                else:
                    errors += 1
        if times:
            print(
                f"{model:<25}{statistics.mean(times):>8.2f}{statistics.median(times):>10.2f}"
                f"{min(times):>8.2f}{max(times):>8.2f}"
                f"{(statistics.mean(throughputs) if throughputs else 0):>10.1f}{errors:>10}"
            )
        else:
            print(f"{model:<25}{'-- todas las llamadas fallaron --':>50}{errors:>10}")


def run_streaming_experiment(client: Groq) -> dict:
    print(f"\n{'='*100}\nEXPERIMENTAL: STREAMING (1 prompt por modelo)\n{'='*100}")
    results = {}
    for model in MODELS:
        print(f"\n--- {model} ---\n")
        start = time.perf_counter()
        first_token_time = None
        full_text = ""
        completion_tokens = None
        try:
            stream = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": STREAMING_PROMPT},
                ],
                max_completion_tokens=MAX_COMPLETION_TOKENS,
                stream=True,
                **extra_kwargs(model),
            )
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    if first_token_time is None:
                        first_token_time = time.perf_counter()
                    delta = chunk.choices[0].delta.content
                    full_text += delta
                    print(delta, end="", flush=True)
                if getattr(chunk, "usage", None):
                    completion_tokens = chunk.usage.completion_tokens
            end = time.perf_counter()
            ttft = first_token_time - start if first_token_time else None
            total = end - start
            tokens_per_s = (
                completion_tokens / (end - first_token_time)
                if completion_tokens and first_token_time
                else None
            )
            results[model] = {
                "ok": True,
                "text": full_text,
                "ttft_s": round(ttft, 3) if ttft else None,
                "total_s": round(total, 3),
                "tokens_per_s": round(tokens_per_s, 1) if tokens_per_s else None,
                "completion_tokens": completion_tokens,
            }
            print(f"\n\n  ttft={results[model]['ttft_s']}s  total={total:.2f}s  tok/s={results[model]['tokens_per_s']}")
        except Exception as e:
            err = str(e)[:200]
            results[model] = {"ok": False, "error": err}
            print(f"ERROR: {err}")
        time.sleep(1)

    print(f"\n{'model':<25}{'ttft':>8}{'total':>10}{'tok/s':>10}")
    for model, r in results.items():
        if r.get("ok"):
            print(f"{model:<25}{(r['ttft_s'] or 0):>8.2f}{r['total_s']:>10.2f}{(r['tokens_per_s'] or 0):>10.1f}")
        else:
            print(f"{model:<25}{'ERROR':>28}")
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--only",
        choices=["all", "quality", "streaming"],
        default="all",
        help="quality = solo calidad+latencia (54 llamadas). streaming = solo el experimento de streaming (3 llamadas). all = ambos.",
    )
    args = parser.parse_args()

    client = Groq(api_key=os.environ["GROQ_API_KEY"])

    results = None
    streaming_results = None

    if args.only in ("all", "quality"):
        results = run_benchmark(client)
        print_latency_summary(results)

    if args.only in ("all", "streaming"):
        streaming_results = run_streaming_experiment(client)

    RESULTS_DIR.mkdir(exist_ok=True)
    out_path = RESULTS_DIR / f"groq_benchmark_{args.only}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    out_path.write_text(
        json.dumps(
            {"quality_latency": results, "streaming_experiment": streaming_results}, ensure_ascii=False, indent=2
        ),
        encoding="utf-8",
    )
    print(f"\nResultados guardados en {out_path}")


if __name__ == "__main__":
    main()
