# MEADLEASE — VOZ E INTERACCIÓN CONVERSACIONAL

> **Paquete:** `robot_voice` (Módulo 4)

## Funciones

| Función | Alcance | En la demo |
|---|---|---|
| Conversación natural en español | Esencial, lenguaje libre, con memoria de turno | En vivo, el corazón de la demo |
| Comandos offline | Solo "detente", "ayuda", "emergencia" y "reanudar" (ADR-017) | Red de seguridad |
| Iniciativa conversacional | Según los disparadores del agente (`ROBOT_COGNICION.md`) | En vivo, momento clave |
| Consultas de salud y medicación | Con datos reales de la BD y los límites del validador ético | En vivo |
| Escalación a humano | Telegram; el robot confirma en voz alta que avisó | En vivo, llega al celular del presentador |
| Expresividad | Coherente con la cara del HMI | Siempre |
| Respuesta mientras procesa | Ver "Decisiones" | Transversal |
| Girar hacia quien habla | Bonus, solo ángulo horizontal (ADR-033) | Si alcanza el tiempo |

## Decisiones

| Qué | Decisión | ADR |
|---|---|---|
| Micrófono | Array de 4 canales del Kinect V2 | 034 |
| Wake word | openWakeWord, con un modelo propio "Koda" por entrenar | 016 |
| Comandos offline | Vosk (provisional) | 017 |
| VAD | TEN VAD (provisional) | 018 |
| STT | Groq Whisper large-v3-turbo | 019 |
| TTS | Azure `es-PE-CamilaNeural`; Kokoro como candidato | 020 |
| Arquitectura | Cascada STT → LLM → TTS, sin voz-a-voz nativa | 021 |
| Latencia percibida | Streaming del LLM al TTS frase por frase, más frases cortas pre-sintetizadas ("déjame revisar…") mientras corre una tool lenta (navegar, dispensar, medir) | — |
| Backchanneling ("ajá", "mju") | Lo dispara el VAD en local cuando el usuario hace una pausa corta sin terminar de hablar. No pasa por el LLM ni por la red | — |

## Micrófono (Kinect V2)

- Aparece en ALSA como "Xbox NUI Sensor": S32_LE, 4 canales, 16 kHz fijos; funciona por USB 2.0.
- Probado en el Asus: la señal cruda es débil (pico ≈ -34 dB, RMS ≈ -52 dB), pero con ganancia la voz se entiende bien incluso con 3 impresoras 3D de fondo.
- Antes del wake word y el VAD hay que pasar a 16 bits mono con ganancia fija o un AGC suave (normalizar el archivo completo distorsiona la voz).
- **Pendiente:** probarlo en el Dell, dentro de la carcasa y a 2-3 m.

## Benchmarks pendientes

Se miden en el Dell con el micrófono real (Fase 1) y el wake word y el VAD se repiten dentro de la carcasa (Fase 3).

| # | Qué | Opciones | Métrica |
|---|---|---|---|
| 1 | Wake word (validación) | openWakeWord con el modelo "Koda" | Falsos positivos/negativos, CPU |
| 2 | VAD | WebRTC vs Silero vs TEN | Latencia de corte, precisión con ruido, CPU |
| 3 | TTS | Azure Camila vs Kokoro | Naturalidad, latencia en el i3 |
| 4 | STT offline | Vosk vs sherpa-onnx | Precisión con las frases de emergencia, latencia, CPU |

## Girar hacia quien habla (bonus, tentativo)

Solo si se construye (ADR-033; pruebas en `scripts/benchmarks/README.md`): el ángulo se estima sobre el audio que disparó el wake word, nunca mientras el robot habla o se mueve. El módulo de voz publica el ángulo y el árbol decide si girar con `turn_in_place`. Los umbrales se definen al implementar.

## Pendientes

- Resultados de los 4 benchmarks.
- Entrenar el wake word "Koda": datos (sintéticos o reales) y umbral de activación.
- Qué pasa en una conversación si se cae internet (más allá del indicador del HMI y los comandos offline).
