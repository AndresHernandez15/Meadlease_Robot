# MEADLEASE — DECISIONES TÉCNICAS (ADR)

Cada entrada resume qué se decidió, qué alternativas se evaluaron y por qué. Este archivo es la única fuente de las justificaciones: los demás documentos solo nombran la decisión y enlazan aquí.

Los ADR se numeran en el orden en que se decide; no se reservan números (por eso no hay ADR-029). Si una decisión cambia, el ADR viejo se marca "Reemplazada por ADR-0XX" en vez de borrarse.

---

### ADR-001 — Reiniciar el proyecto desde cero
- **Estado:** Aceptada
- **Contexto:** el sistema anterior se construyó módulo por módulo, optimizando cada uno por separado, sin pensar en latencia, memoria ni integración del conjunto. El deadline pasó del 1 de mayo al 1 de noviembre de 2026.
- **Decisión:** reconstrucción completa. El código anterior no se reutiliza; solo sirve como referencia de qué funcionó (en los documentos aparece como "validado en el sistema anterior, por reimplementar").

### ADR-002 — Ubuntu 24.04 LTS
- **Estado:** Aceptada
- **Descartada:** Ubuntu 26.04 (tenía ~3 meses de vida). `libfreenect2` (driver del Kinect V2) es una dependencia frágil de comunidad y era riesgoso en un sistema tan nuevo.

### ADR-003 — ROS 2 Jazzy
- **Estado:** Aceptada
- **Descartada:** ROS 2 Lyrical (~2 meses de vida): errores de mirrors y solo Tier 3 en Ubuntu 24.04.
- **Consecuencia:** Python 3.12.

### ADR-004 — Entornos Python: `venv --system-site-packages` + `uv`
- **Estado:** Aceptada
- **Por qué:** es el patrón que documenta ROS 2 para mezclar `rclpy` con dependencias externas. `uv` resuelve dependencias más rápido que pip.
- **Descartadas:** Conda (rompe `rclpy`) y Docker (overhead de RAM/CPU que el Dell no tiene, DDS frágil entre contenedores).

### ADR-005 — STM32 como único puente hacia los microcontroladores
- **Estado:** Aceptada
- **Decisión:** PC ↔ STM32F411 (micro-ROS por USB-CDC, ya validado) ↔ ESP32 Movilidad y ESP32 Médica por UART.
- **Descartada:** micro-ROS directo en los ESP32 por WiFi. Es viable, pero movimiento y parada de emergencia no pueden depender del WiFi, menos en un auditorio congestionado.

### ADR-006 — UART con trama binaria + CRC8
- **Estado:** Aceptada. El contenido de los mensajes se cierra al implementar cada firmware (ADR-028).
- **Antes:** texto plano (`"VL:...,VR:...\n"`).
- **Por qué:** más rápido de parsear, detecta corrupción y sigue siendo depurable con logs decodificados.

### ADR-007 — Parada de emergencia física directa al STM32
- **Estado:** Aceptada
- **Decisión:** la parada no viaja por la trama UART: entra como interrupción al STM32 para no competir en latencia con el resto de los datos. Son dos dispositivos: botón NC (PA0), que además corta la alimentación de los motores, y sensor capacitivo TTP223 (PA1). Detalle en `HARDWARE_FIRMWARE.md`.
- **Pendiente:** cómo el STM32 avisa de la emergencia a los ESP32 y a ROS 2.

### ADR-008 — Firmware ESP32: PlatformIO + ESP-IDF
- **Estado:** Aceptada (revisada)
- **Antes:** PlatformIO + Arduino, pensando en la poca experiencia en firmware del equipo.
- **Por qué cambió:** ESP-IDF da acceso directo a los periféricos del ESP32-S3 que se usan (MCPWM para motores, PCNT para encoders, RMT para las WS2812).

### ADR-009 — Reconocimiento facial: SCRFD + ArcFace (ONNX Runtime)
- **Estado:** Aceptada
- **Antes:** LBPH, que obligaba a reentrenar para agregar un usuario.
- **Por qué:** agregar un usuario es solo agregar su embedding (soporta 2+ usuarios), necesita 3-5 fotos en vez de 200, es menos sensible a la iluminación y comparte runtime ONNX con wake word y VAD.

### ADR-010 — SLAM: RTAB-Map 0.21.9+
- **Estado:** Aceptada
- **Por qué:** soporta RGB-D de forma nativa y tiene soporte activo en Jazzy. La 0.21.9 corrige un bug de sincronización de `message_filters`.
- **Descartadas:** SLAM Toolbox, Cartographer y GMapping, pensadas para LiDAR.

### ADR-011 — Navegación: Nav2
- **Estado:** Aceptada
- **Nota:** se usa como action server externo. Que use BehaviorTree.CPP por dentro no afecta al BT propio (ADR-014). Los waypoints con nombre salen de Nav2 Waypoint Follower + un YAML nombre→pose.

### ADR-012 — Agente: Pydantic AI
- **Estado:** Aceptada
- **Por qué:** ligero, independiente del proveedor de LLM y con tipado fuerte (encaja con mensajes ROS 2).
- **Descartada:** LangGraph; su fuerte (grafos de estado) ya lo cubre el Behavior Tree.

### ADR-013 — LLM: Groq con fallback de 3 modelos × 2 keys
- **Estado:** Aceptada
- **Por qué:** el más rápido evaluado (<1 s por respuesta) con tier gratuito suficiente.
- **Riesgo:** el catálogo cambia seguido (Llama 3.3 70B, la elección original, ya salió). Se mitiga porque Pydantic AI permite cambiar de proveedor por configuración.
- **Alternativas descartadas:** OpenRouter (2-16 s por respuesta en tier gratuito); Cerebras y SambaNova (su "gratis" es un saldo que se agota, no un tier perpetuo).
- **Orden de fallback** (benchmark de septiembre 2026, detalle en `scripts/benchmarks/README.md`). Se repite igual con la key secundaria:
  1. `openai/gpt-oss-120b` — primario: el único sin respuestas vacías o cortadas.
  2. `openai/gpt-oss-20b` — el más rápido en tok/s, algo menos confiable.
  3. `qwen/qwen3.8-27b` — último recurso: rápido, pero sufre límites y colas del tier gratuito.
- **Parámetros por modelo:**
  - `max_completion_tokens=300` en los 3 (respeta el límite de qwen y la regla de "máx. 3 frases" del prompt de voz).
  - `reasoning_effort="low"` solo en los `gpt-oss-*` (evita respuestas vacías del 20b; a qwen le empeoraba la latencia).
  - `temperature=0.7`, `top_p=0.80` solo en qwen (ajuste manual); los `gpt-oss-*` en su default.

### ADR-014 — Behavior Tree: py_trees + py_trees_ros
- **Estado:** Aceptada
- **Por qué:** Python, el mismo lenguaje que el resto del sistema; más fácil de leer y depurar.
- **Descartada:** BehaviorTree.CPP; no aporta nada si no se toca el árbol interno de Nav2.

### ADR-015 — El agente propone, el árbol dispone
- **Estado:** Aceptada
- **Decisión:** el agente propone intenciones vía tool calls; el BT las ejecuta, y sus ramas de mayor prioridad (emergencia, obstáculos) pueden interrumpir sin consultar al agente.
- **Por qué:** separa planificación (LLM) de ejecución (controlador determinista), un patrón común en robótica con LLM.

### ADR-016 — Wake word: openWakeWord
- **Estado:** Aceptada; falta validarla en el hardware real y entrenar un modelo propio para "Koda".
- **Por qué:** corre sobre ONNX Runtime (compartido con VAD y reconocimiento facial) con poco CPU.
- **Descartadas:** Vosk como wake word (lo que se usaba antes) y Porcupine (Picovoice cerró su plan gratuito en agosto 2026).

### ADR-017 — Comandos offline: Vosk, solo para emergencia
- **Estado:** Provisional; se confirma o se cambia con el benchmark de STT offline (`ROBOT_VOZ.md`).
- **Decisión:** Vosk solo reconoce "detente", "ayuda", "emergencia" y "reanudar"; todo lo demás va al agente.
- **Por qué:** los comandos rígidos de propósito general del sistema anterior daban falsos positivos y quitaban flexibilidad.
- **En benchmark:** sherpa-onnx (juntaría STT, TTS, VAD y wake word en un solo runtime ONNX).

### ADR-018 — VAD: TEN VAD
- **Estado:** Provisional; se confirma o se cambia con el benchmark de VAD (`ROBOT_VOZ.md`).
- **Por qué:** reporta ~32% menos CPU que Silero y corta el habla más rápido, clave para que la conversación se sienta natural.
- **En benchmark:** WebRTC VAD y Silero. Cobra VAD (Picovoice) quedó descartado.

### ADR-019 — STT: Groq Whisper large-v3-turbo
- **Estado:** Aceptada (igual que en el sistema anterior)
- **Por qué:** rápido y barato, ya probado, y del mismo proveedor que el LLM.

### ADR-020 — TTS: Azure `es-PE-CamilaNeural` (+ Kokoro como candidato)
- **Estado:** Azure aceptada; Kokoro en evaluación.
- **Nota:** Kokoro (82M parámetros, local en CPU, soporta español) solo se compara en calidad y latencia. No se busca independencia de red: el robot ya depende de internet para STT y LLM.

### ADR-021 — Voz-a-voz nativa: descartada
- **Estado:** Rechazada
- **Evaluadas:** OpenAI Realtime API, Gemini Live, Amazon Nova Sonic.
- **Por qué no:** no dan una transcripción limpia (debilita el validador ético), atan a un solo proveedor (rompe el fallback de Groq) y son cajas negras. Se mantiene la cascada STT → LLM → TTS.

### ADR-022 — HMI: NiceGUI en Chromium (modo kiosco)
- **Estado:** Aceptada
- **Por qué:** interfaz en Python puro sobre FastAPI + WebSockets (la misma base del sistema anterior) y permite insertar HTML/JS propio, como la cara animada.
- **Descartada:** Godot; su integración con ROS 2 es experimental y exigiría compilar un módulo C++.

### ADR-023 — Botón de parada en el HMI: descartado
- **Estado:** Rechazada
- **Por qué:** sin pantalla táctil, llevar el mouse hasta el botón no es práctico. Quedan el botón NC, el TTP223 y el comando de voz.

### ADR-024 — Editor: VSCode
- **Estado:** Aceptada
- **Por qué:** un solo editor para Python, C/C++, YAML y Markdown, con PlatformIO para los ESP32.

### ADR-025 — Un solo repositorio
- **Estado:** Aceptada
- **Por qué:** el desarrollo es mayormente secuencial y el equipo es pequeño; varios repos solo agregarían coordinación.

### ADR-026 — Mapeo manual/asistido (sin exploración autónoma)
- **Estado:** Aceptada
- **Decisión:** el robot se mueve a mano (control remoto) mientras RTAB-Map mapea, y el mapa se guarda desde el HMI. La exploración autónoma de frontera es demasiado riesgo para un prototipo.

### ADR-027 — Memoria entre sesiones: fuera de alcance
- **Estado:** Diferida (bonus después de la sustentación)
- **Decisión:** solo memoria de la sesión + registro estructurado en la BD.

### ADR-028 — Arquitectura del enlace UART STM32↔ESP32
- **Estado:** Aceptada la arquitectura; los mensajes siguen en borrador (`HARDWARE_FIRMWARE.md`).
- **Decisión:**
  - Dos líneas UART dedicadas (una por ESP32), sin bus compartido.
  - Framing común: `[0xAA][MSG_TYPE][LEN][PAYLOAD][CRC8][0x55]`, con CRC8 sobre `MSG_TYPE+LEN+PAYLOAD`.
  - Watchdog en el ESP32 Movilidad: si deja de recibir comandos de velocidad durante un tiempo límite (a fijar en firmware), frena solo.
- **Descartada:** un bus compartido con byte de dirección. Al STM32F411 le sobran USARTs, y con líneas separadas un fallo en un link no afecta al otro.

### ADR-030 — "Usuarios" en vez de "pacientes"
- **Estado:** Aceptada
- **Por qué:** Koda es un robot doméstico de acompañamiento, no un dispositivo médico; "usuarios" no promete un rigor clínico que el proyecto no busca. Aplica a BD, tools y documentación.

### ADR-031 — Horarios de medicación en una sola tabla con `tipo_horario`
- **Estado:** Aceptada
- **Decisión:** una tabla `horarios_medicacion` con discriminador `tipo_horario` (`'diario'`, `'dias_semana'`, `'intervalo'`) y columnas opcionales según el modo.
- **Descartada:** una tabla por modo, que obligaría a combinar 3 tablas para calcular la próxima dosis y duplicaría la relación usuario↔medicamento.
- **Nota:** la próxima dosis se calcula en código, nunca en el LLM. Esquema completo en `database/README.md`.

### ADR-032 — Asus ↔ Dell por `git pull`, sin Remote-SSH
- **Estado:** Aceptada (reemplaza el plan inicial de Remote-SSH)
- **Decisión:** se desarrolla en el Asus; el Dell hace `git pull` solo para probar lo que depende de su hardware (micrófono, latencia) y para la integración final. Cada máquina tiene su propio `venv`.
- **Por qué:** ambas corren el mismo SO y ROS 2, así que no hace falta mantener una sesión SSH.

### ADR-033 — Localizar de dónde viene la voz (bonus)
- **Estado:** Diferida
- **Decisión:** si se hace, GCC-PHAT entre los micrófonos extremos del Kinect, solo para el ángulo horizontal. Las reglas de cuándo y cuánto girar se definen al implementar (`ROBOT_VOZ.md`).
- **Limitaciones:** no distingue adelante de atrás; es sensible a ruido y eco; la separación entre micrófonos está estimada, no medida, y el lado derecho no está validado.
- **Pruebas preliminares:** `scripts/benchmarks/README.md`.

### ADR-034 — Kinect V2: SLAM + micrófono
- **Estado:** Aceptada
- **Decisión:** el Kinect hace SLAM (RGB-D) y es el micrófono del robot. No detecta personas: eso lo hace solo la cámara Dell.
- **Consecuencias:** como escucha todo el tiempo, queda encendido casi siempre, y su consumo en el riel de 12V cuenta para la autonomía. El audio se captura por ALSA sin `libfreenect2`, pero necesita los 12V. Falta validarlo dentro de la carcasa y a 2-3 m.
