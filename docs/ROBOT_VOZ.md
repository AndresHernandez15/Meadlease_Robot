# MEADLEASE — VOZ E INTERACCIÓN CONVERSACIONAL

> **Corresponde a:** `robot_voice`


---

## Objetivos funcionales (Módulo 4 — Interacción Conversacional)

| Función | Alcance | Demo |
|---|---|---|
| Conversación natural en español | Esencial, lenguaje libre | En vivo — corazón de la demo |
| Comandos offline críticos | **Acotados solo a emergencia** ("detente", "ayuda", "emergencia") + reanudación ("reanudar") — decisión revisada: comandos rígidos de propósito general generaban falsos positivos y quitaban flexibilidad; todo lo demás pasa por el agente con lenguaje libre | Red de seguridad, no exhibición directa |
| Diálogo con memoria de turno | Esencial (ver `ROBOT_COGNICION.md`) | En vivo |
| Iniciativa conversacional | Ligada a disparadores del agente (ver `ROBOT_COGNICION.md`) | En vivo, momento clave |
| Consulta de salud/medicación con datos reales | Esencial | En vivo |
| Información general de salud | Con límites éticos (validador estructural, ver `ROBOT_COGNICION.md`) | En vivo si surge |
| Escalación a humano | **Vía bot de Telegram (real, ya funcional)** — el robot confirma verbalmente el envío | En vivo, notificación real llega al celular del presentador |
| Expresividad emocional coherente con HMI | Esencial | Constante |
| Filler / respuesta mientras procesa | Streaming de LLM a TTS frase por frase (mayor impacto real en latencia) + banco de frases cortas pre-escritas/pre-sintetizadas para cuando el agente invoca una herramienta que toma tiempo real (navegar, dispensar, medir) | Transversal |

## Decisiones técnicas (Capa 6)

| Componente | Decisión | Justificación |
|---|---|---|
| Wake word | **openWakeWord** (reemplaza Vosk-como-wake-word de decisión previa, y a Porcupine original) | Corre sobre ONNX Runtime (comparte runtime con VAD/reconocimiento facial), más preciso que Porcupine en benchmarks propios, mínimo CPU. Porcupine queda **eliminado por completo** de cualquier opción o benchmark: Picovoice eliminó su plan gratuito, no solo el límite de "1 dispositivo activo" que ya lo hacía poco práctico |
| Comandos offline | **Vosk, acotado exclusivamente a comandos de emergencia y reanudación** ("detente", "ayuda", "emergencia", "reanudar") | Decisión revisada: comandos rígidos de propósito general generaban falsos positivos y quitaban flexibilidad al robot (probado en sistema anterior). Todo lo demás pasa por el agente con lenguaje libre. "Reanudar" libera el reflejo de parada del Behavior Tree (ver `ROBOT_COGNICION.md`, Módulo 5C). Alternativa a evaluar: **sherpa-onnx** (consolidaría STT+TTS+VAD+wake word bajo un solo runtime ONNX) |
| VAD | **TEN VAD** (reemplaza recomendación inicial de Silero VAD) | Mayor precisión, ~32% menos CPU que Silero, latencia de corte de habla mucho menor (crítico para naturalidad conversacional). Cobra VAD (Picovoice) queda **eliminado por completo** de cualquier opción o benchmark, por el mismo motivo que Porcupine — Picovoice ya no tiene plan gratuito |
| STT | **Groq Whisper large-v3-turbo**, sin cambio | Confirmado como opción cloud más rápida en 2026 (~216x tiempo real, más barato que alternativas) |
| TTS | **Azure `es-PE-CamilaNeural`** (primario, probado) + **Kokoro TTS** (candidato a validar) | Kokoro: 82M parámetros, Apache 2.0, corre 100% local en CPU, soporta español. Se evalúa únicamente como alternativa a probar en el benchmark de TTS (calidad/latencia en el i3) — **no** se busca independencia de red con esta prueba: el robot es dependiente de conexión a internet para su operación conversacional normal (STT y LLM en la nube), y esa dependencia ya está contemplada como limitación aceptada del proyecto. Pendiente de benchmark real en el i3 |
| Filler / latencia percibida | Streaming LLM→TTS frase por frase (mayor impacto real) + banco de frases cortas pre-escritas para llamadas a herramientas que toman tiempo real (navegar, dispensar, medir) | Técnica documentada como estándar de producción en agentes de voz 2026 |
| Backchanneling ("mju", "ajá") | Disparado localmente por **TEN VAD** al detectar pausa breve dentro del habla del usuario que continúa — sin pasar por el LLM | Emula la retroalimentación natural humana (ocurre *mientras* el usuario habla, no como respuesta). Cero costo de red/LLM. Inspirado en el nivel de fluidez de modos de voz nativos (ChatGPT Advanced Voice, Gemini Live), logrado sin adoptar esa arquitectura |
| Voz-a-voz nativa (evaluada y descartada) | Se investigaron alternativas de voz-a-voz nativa (OpenAI Realtime API, Gemini Live, Nova Sonic) | Descartada: sin transcripción limpia (debilita el validador ético estructural), ata a un solo proveedor (rompe la resiliencia del fallback de Groq), modelo económico distinto al diseñado, y es una caja negra que contradice el principio de transparencia/control del proyecto. Se mantiene arquitectura en cascada (STT→LLM→TTS) |

## Benchmarks pendientes

Todos deben medirse en el hardware real (Dell Inspiron, micrófono real), no con cifras de benchmarks públicos ajenos. Ejecutar en Fase 1; **re-validar wake word/VAD dentro de la carcasa cerrada en Fase 3** (la acústica cambia).

| # | Benchmark | Opciones a comparar | Métrica clave |
|---|---|---|---|
| 1 | Wake word | openWakeWord (única opción — Porcupine eliminado por completo tras el cierre del plan gratuito de Picovoice) | Precisión (falsos positivos/negativos) con voz real y el nombre del robot ("Koda"), consumo CPU |
| 2 | VAD | WebRTC VAD vs Silero VAD vs TEN VAD (Cobra VAD eliminado por completo tras el cierre del plan gratuito de Picovoice) | Latencia de corte de habla, precisión con ruido ambiente real, consumo CPU |
| 3 | TTS | Azure `es-PE-CamilaNeural` vs Kokoro | Naturalidad de voz en español, latencia real en el i3, viabilidad de correr 100% local |
| 4 | STT offline (emergencia) | Vosk vs sherpa-onnx | Precisión con frases de emergencia en español, latencia, consumo |

---

## Información faltante / pendiente de revisión

- **Resultados reales de los 4 benchmarks:** aún no ejecutados — sección a llenar con números concretos tras Fase 1 y re-validación en Fase 3.
- **Manejo de UX ante pérdida total de conectividad** durante una conversación normal (más allá del "indicador discreto de conectividad" del HMI y de los comandos offline de emergencia) — no descrito.
- **Micrófono(s) específico(s):** no se indica modelo/ubicación física del micrófono usado para captura de voz, solo "micrófono real".
