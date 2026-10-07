# Benchmarks y experimentos

Scripts para medir componentes de forma aislada antes de integrarlos al sistema (principio de "validar cada pieza por separado", ver `docs/PROYECTO_GENERAL.md`). Se ejecutan a mano, no forman parte del robot.

| Script | Qué mide | Estado | Decisión asociada |
|---|---|---|---|
| `llm/benchmark_groq.py` | Latencia y calidad de los modelos de chat de Groq candidatos a la cadena de fallback | ✅ Hecho (septiembre 2026) | ADR-013 |
| `kinect_array.py` | Ángulo de llegada de la voz con el array de micrófonos del Kinect V2 (GCC-PHAT) | 🧪 Prueba preliminar | ADR-033 (bonus) |
| Benchmarks de voz (wake word, VAD, TTS, STT offline) | — | Pendientes | `docs/ROBOT_VOZ.md` |

---

## `llm/benchmark_groq.py`

Compara los 3 modelos de la cadena de fallback (`openai/gpt-oss-120b`, `openai/gpt-oss-20b`, `qwen/qwen3.8-27b`) con el system prompt de Koda: cada prompt de calidad se repite 3 veces y se cronometra cada llamada. También incluye un experimento de streaming (tiempo al primer token y tok/s).

```bash
# Requiere GROQ_API_KEY en .env
python scripts/benchmarks/llm/benchmark_groq.py --only all        # calidad+latencia (54 llamadas) + streaming
python scripts/benchmarks/llm/benchmark_groq.py --only quality
python scripts/benchmarks/llm/benchmark_groq.py --only streaming
```

Salida: respuestas completas en la terminal + JSON con todo el detalle en `llm/results/`. La decisión resultante está en ADR-013 (`docs/DECISIONES_TECNICAS.md`).

### Resultados (septiembre 2026)

Se evaluó todo el catálogo de chat de Groq y los modelos `:free` de OpenRouter.

- **Descartados antes del benchmark de calidad:** OpenRouter por latencia (2-16 s vs <1 s en Groq); Cerebras y SambaNova porque su "gratis" es un saldo fijo; `allam-2-7b` por mezclar palabras en árabe.
- **`gpt-oss-120b`:** el único sin respuestas vacías o cortadas en las 54 llamadas de calidad, y el más consistente entre repeticiones.
- **`gpt-oss-20b`:** buena calidad y el más rápido en tok/s, pero dio respuestas vacías/cortadas sin `reasoning_effort` (gastaba el presupuesto de tokens razonando). Se resolvió con `reasoning_effort="low"`.
- **`qwen3.8-27b`:** el más rápido en latencia bruta cuando responde bien, pero dio 429 por límite de tokens de salida/min (1000 OTPM) en una corrida y latencias de hasta 18 s por cola (`queue_time`) en otra. `reasoning_effort` le empeoraba la latencia.
- **`service_tier`:** solo `on_demand` está disponible en el tier gratuito (ya es el default).
- No se volvió a medir con la key secundaria.

---

## `kinect_array.py` — localización de fuente sonora (bonus)

Estima el azimut de la voz con GCC-PHAT entre los canales extremos del array del Kinect (canales 1 y 4), ventana de 0.25 s, descartando ventanas de silencio.

```bash
python scripts/benchmarks/kinect_array.py grabacion.wav   # WAV de 4 canales, S32_LE, 16 kHz
```

Parámetros en el script: velocidad del sonido `C = 343 m/s`, separación entre micrófonos extremos `D = 0.22 m`, factor de interpolación 16.

### Resultados preliminares (en el Asus, sin validación formal)

- `D ≈ 0.22 m` es una **estimación**, no una medición física verificada.
- Centro ≈ -1°; izquierda ≈ -40° y -43° (dos ventanas distintas).
- **Lado derecho no validado:** el hablante quedó casi al centro en esa prueba y dio 0.7° en vez de un ángulo claramente positivo.
- Condiciones: ruido de fondo de impresoras 3D, Kinect fuera de la carcasa.

### Cómo validarlo (pendiente, ROADMAP Fase 1 y re-validación en Fase 3)

1. Rotar el Kinect a ángulos reales conocidos y medidos (ej. -60°, -30°, 0°, 30°, 60°).
2. Tomar 10+ ventanas por posición y usar la mediana.
3. Recalibrar la separación del array con `D_nuevo = D · sin(ángulo_estimado) / sin(ángulo_real)`.
4. Repetir dentro de la carcasa cerrada (la acústica y la posición relativa de los micrófonos cambian).
