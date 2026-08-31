# Meadlease_Robot

Robot asistente doméstico para acompañamiento y apoyo a personas mayores. Proyecto de grado — Universidad Tecnológica de Bolívar, Ingeniería Mecatrónica, Biomédica y Sistemas.

> Estado: en construcción activa. El proyecto pasó por una reformulación arquitectónica completa en agosto de 2026 tras detectar que el sistema anterior se había construido módulo por módulo, sin pensar en cómo cada pieza afecta al resto (latencia, memoria, complejidad de integración). Este repositorio contiene la reconstrucción desde cero.

## Qué es Meadlease

Meadlease es un robot doméstico pensado para adultos mayores que viven solos o con supervisión limitada. No busca ser un chatbot con ruedas: la idea es que el robot inicie comportamiento por su cuenta, tome decisiones y actúe con propósito propio, sin que el usuario tenga que invocarlo constantemente.

Funciones principales:

- Conversación natural en español, con memoria de turno y validación ética estructural sobre lo que el agente puede decir.
- Dispensación de medicamentos, programada o bajo demanda, con verificación de identidad previa por reconocimiento facial.
- Medición de signos vitales (frecuencia cardíaca, SpO₂, temperatura) con registro histórico y visualización de tendencias.
- Navegación autónoma dentro del hogar, incluyendo búsqueda activa del usuario cuando no está a la vista.
- Parada de emergencia por botón físico o comando de voz offline, sin dependencia de red.
- Escalación a un cuidador humano vía Telegram cuando la situación lo amerita.

Es un prototipo de tesis, no un producto terminado: las decisiones de alcance están filtradas explícitamente para funcionar de forma consistente en una sustentación en vivo de 15 minutos, no para cubrir cada caso límite de un despliegue real.

## Arquitectura

El sistema se organiza en dos capas que se comunican pero no se pisan:

- **Capa reactiva** — un Behavior Tree (`py_trees` + `py_trees_ros`) siempre activo, sin LLM en el medio, que ejecuta y protege: emergencia, obstáculos y prioridades de movimiento tienen la última palabra y pueden interrumpir sin consultar a nadie.
- **Capa deliberativa** — un agente basado en LLM (Pydantic AI) que interpreta lenguaje natural, decide metas y propone intenciones vía tool calls. El agente propone, el árbol dispone.

A nivel de hardware, un Dell Inspiron sin GPU corre Ubuntu 24.04 + ROS 2 Jazzy como único cerebro del robot. La comunicación con los actuadores pasa por un STM32 como puente único hacia dos ESP32 (movilidad y médica), vía UART con trama binaria y CRC8 — el movimiento y la parada de emergencia no dependen de WiFi bajo ninguna circunstancia.

```
Percepción (cámara + Kinect)
        │
        ▼
Behavior Tree (py_trees)  ←──────────────┐
        │                                │
        ▼                                │
   Agente LLM (Pydantic AI)  ────────────┘
        │
        ▼
STM32 (puente UART) ── ESP32 Movilidad
                    └── ESP32 Médica ── ESP32-CAM
```

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Middleware | ROS 2 Jazzy Jalisco sobre Ubuntu 24.04 LTS |
| Percepción | MediaPipe Pose (presencia), SCRFD + ArcFace vía ONNX Runtime (reconocimiento facial) |
| SLAM / navegación | RTAB-Map, Nav2 |
| Agente / cognición | Pydantic AI, Groq (Llama 3.3 70B Versatile) con fallback a Cerebras y OpenRouter |
| Árbol de comportamiento | py_trees / py_trees_ros |
| Voz | openWakeWord (wake word), TEN VAD, Groq Whisper large-v3-turbo (STT), Azure `es-PE-CamilaNeural` (TTS), Vosk acotado a comandos de emergencia offline |
| Interfaz (HMI) | NiceGUI sobre Chromium en modo kiosco |
| Firmware | STM32CubeIDE (puente STM32), PlatformIO + Arduino (ESP32 movilidad y médica) |
| Datos | SQLite |
| Notificaciones | Bot de Telegram |

Cada decisión de este stack está documentada con su alternativa evaluada y el motivo de descarte en [`docs/DECISIONES_TECNICAS.md`](docs/DECISIONES_TECNICAS.md).

## Estructura del repositorio

```
meadlease/
├── ros2_ws/
│   └── src/
│       ├── robot_bringup/       # launch files, config Nav2/RTAB-Map, waypoints, URDF
│       ├── robot_interfaces/    # mensajes/servicios/acciones personalizados
│       ├── robot_perception/    # detección de presencia + reconocimiento facial
│       ├── robot_voice/         # wake word, VAD, STT, TTS, filler, backchanneling
│       ├── robot_cognition/     # agente Pydantic AI + Behavior Tree
│       └── robot_hmi/           # NiceGUI + bridge a ROS2
├── firmware/
│   ├── stm32_backbone/          # puente STM32 (STM32CubeIDE)
│   ├── esp32_movilidad/         # firmware motores, encoders, ultrasonidos (PlatformIO)
│   └── esp32_medica/            # firmware dispensador, signos vitales (PlatformIO)
├── database/                    # esquema SQLite y notas de creación manual
├── docs/                        # documentación técnica modular
├── scripts/benchmarks/          # benchmarks de voz (wake word, VAD, TTS, STT)
├── simulation/                  # mundos y modelos Gazebo
└── .env.example
```

## Equipo

| Integrante | Área | Responsabilidad |
|---|---|---|
| Andrés | Mecatrónica + Sistemas | Arquitectura y desarrollo de todo el software: ROS 2, agente, árbol de comportamiento, HMI, integración |
| Linda | Biomédica + Mecatrónica | Diseño mecánico y firmware del dispensador de medicamentos (ESP32 Médica) |
| Sergio | Mecatrónica | Cableado, PCB de movilidad y firmware de movilidad (ESP32 Movilidad) |
| Juan | Mecatrónica | Visión artificial y post-procesado|

## Estado actual

El proyecto está en la fase posterior a la reformulación arquitectónica: las decisiones de diseño están cerradas y documentadas, y la implementación avanza en paralelo al ensamblaje físico (impresión 3D casi terminada, post-procesado con base pintada, dispensador funcional, PCB de movilidad resuelta). El detalle fase por fase vive en [`docs/ROADMAP.md`](docs/ROADMAP.md).

## Documentación

La documentación técnica completa, incluyendo el registro de decisiones de arquitectura (formato ADR) y el detalle funcional de cada módulo, está en la carpeta [`docs/`](docs/).

---

Proyecto de grado — Universidad Tecnológica de Bolívar, 2026.
