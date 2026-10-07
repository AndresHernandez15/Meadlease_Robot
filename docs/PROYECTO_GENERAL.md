# MEADLEASE — PROYECTO GENERAL

## Contexto

| | |
|---|---|
| Universidad | Universidad Tecnológica de Bolívar — Ing. Mecatrónica, Biomédica y Sistemas |
| Deadline funcional | 1 de noviembre de 2026 |
| Proyecto / robot | **Meadlease** es el proyecto; **Koda** es el robot. El nombre viene del japonés *kodawari*: atención al detalle y cero errores (por ejemplo, en una dosis de medicamento) |
| Entrega | Prototipo, no producto terminado. Sustentación en vivo de 15 minutos + clips de video para lo que no se puede mostrar en vivo |
| Reformulación | Agosto 2026, desde cero (ADR-001) |

## Equipo

| Integrante | Perfil | Rol |
|---|---|---|
| **Andrés** (líder) | Mecatrónica + Sistemas | Arquitectura y software: ROS 2, agente, BT, voz, HMI, firmware STM32 e integración (incluida percepción) |
| **Linda** | Biomédica + Mecatrónica | Diseño mecánico, dispensador y firmware de la ESP32 Médica |
| **Sergio** | Mecatrónica | Cableado, PCB de movilidad y firmware de la ESP32 Movilidad |
| **Juan** | Mecatrónica | Visión artificial (`robot_perception`), con bastante autonomía. Apoyó en el post-procesado |

Andrés trabaja con Claude (planificación y arquitectura) y GitHub Copilot Pro (implementación). Los firmwares de Sergio y Linda se construyen sobre especificaciones y plantillas que entrega Andrés.

**Riesgo aceptado:** casi todo el software recae en Andrés. Para aliviarlo, lo que no requiere saber ROS/Python se delega como tarea guiada (correr un benchmark, probar una herramienta ya especificada).

## Principios

1. **Desde cero y con el sistema completo en mente.** Cada tecnología se elige por cómo encaja con el resto (latencia, memoria, integración), no solo por sus méritos. El código anterior solo sirve de referencia.
2. **Arquitectura temprano, detalles al construir.** Mensajes UART, tópicos ROS 2, firmas de tools y diseño de pantallas se cierran al implementar cada parte.
3. **Eficiencia contra el hardware real:** Dell Inspiron 3421, i3-3227U (2013, sin AVX2), 12 GB DDR3, sin GPU. Nada se hardcodea al hardware: los hilos/workers se detectan en ejecución (`os.cpu_count()`), para que el mismo código corra en el Asus, el Dell o una Raspberry Pi.
4. **Código legible y modular**, con carpetas poco profundas: cualquiera debe poder entrar a una parte, entenderla y cambiarla sin romper otra.
5. **Validar cada pieza por separado** (un script simple) antes de conectarla al agente o al árbol, y diseñar cada pieza antes de generar código.
6. **La configuración de una sola vez se hace a mano**, paso a paso, para aprender de verdad: instalaciones, esquema de BD, entornos. No aplica al código de la aplicación.
7. **Que se sienta vivo, dentro del alcance de un prototipo.** Koda debe tomar la iniciativa, no ser un chatbot con ruedas. Cada función se etiquetó como esencial, demo en vivo, en video, en background, bonus o fuera de alcance; se optimiza para que la sustentación salga bien, no para cubrir cada caso límite.

## Módulos y documentos

| Módulo | Qué cubre | Documento |
|---|---|---|
| 1 — Percepción | Presencia + reconocimiento facial multiusuario | `ROBOT_PERCEPCION.md` |
| 2 — Cognición | Agente LLM que propone + Behavior Tree que ejecuta y protege | `ROBOT_COGNICION.md` |
| 3 — Movilidad | Navegación, búsqueda del usuario, aproximación, regreso a base | `ROBOT_MOVILIDAD.md` |
| 4 — Voz | Conversación en español, comandos offline de emergencia | `ROBOT_VOZ.md` |
| 5 — Salud | Dispensación, signos vitales, emergencias | `ROBOT_COGNICION.md` |
| 6 — HMI | Cara, dashboard de salud, mapa, control remoto por QR | `ROBOT_HMI.md` |
| 7 — Backbone físico | Hardware, energía, comunicación con microcontroladores | `HARDWARE_FIRMWARE.md` |
| — | Decisiones (ADR) · plan por fases · base de datos | `DECISIONES_TECNICAS.md` · `ROADMAP.md` · `database/README.md` |

## Entorno de desarrollo

- **Máquinas:** el **Asus ROG Strix** (i5 10ª gen, 16 GB) para el día a día; el **Dell Inspiron** para pruebas que dependen de su hardware (micrófono, latencia), la integración final y la demo. Las dos tienen Ubuntu 24.04 + ROS 2 Jazzy, y se sincronizan con GitHub (`git pull`, sin Remote-SSH, ADR-032).
- **ROS 2 nativo desde el día uno.** Nada de desarrollar primero en Windows con wrappers (lección del primer ciclo). Windows solo para firmware ESP32 y prototipos de Python sin `rclpy`.
- **Stack base:** Ubuntu 24.04 (ADR-002), ROS 2 Jazzy con Python 3.12 (ADR-003), `venv --system-site-packages` + `uv` (ADR-004), SQLite (`database/README.md`).
- **Editor:** VSCode (ADR-024). Por explorar: la extensión "STM32Cube para VSCode" para traer también el firmware STM32; si no conviene, se sigue con STM32CubeIDE.
- **Repo:** uno solo (ADR-025).

### Convenciones

- Código en inglés; contenido para el usuario (prompts, textos del HMI, mensajes de Telegram) en español. Excepción: los identificadores de la BD están en español (`database/README.md`).
- Credenciales en `.env` (nunca en git); la plantilla es `.env.example` (Groq ×2, Azure, Telegram).
- `.gitignore` excluye builds de ROS, `.env`, bases de datos, datos biométricos, grabaciones de voz, mapas y pesos de modelos.

### Estructura del repositorio

Planificada; ✔ = ya existe.

```
Meadlease_Robot/
├── ros2_ws/src/
│   ├── robot_bringup/       ← launch, config Nav2/RTAB-Map, waypoints, URDF — Andrés
│   ├── robot_interfaces/    ← mensajes/servicios/acciones propios — Andrés
│   ├── robot_perception/    ← presencia + reconocimiento facial — Juan
│   ├── robot_voice/         ← wake word, VAD, STT, TTS — Andrés
│   ├── robot_cognition/     ← agente + Behavior Tree — Andrés
│   └── robot_hmi/           ← NiceGUI + puente a ROS 2 — Andrés
├── firmware/
│   ├── stm32_backbone/      ← Andrés (STM32CubeIDE)
│   ├── esp32_movilidad/     ← Sergio (PlatformIO + ESP-IDF)
│   └── esp32_medica/        ← Linda (PlatformIO + ESP-IDF; incluye la ESP32-CAM)
├── database/ ✔              ← schema.sql + README
├── docs/ ✔                  ← documentación (+ archivo/ histórico)
├── scripts/benchmarks/ ✔    ← benchmarks y experimentos
├── simulation/              ← mundos Gazebo
├── .env.example ✔
└── README.md ✔
```

`robot_perception` es un paquete aparte para que Juan trabaje solo en esa carpeta sin chocar con el resto.

## Pendientes

- **Dónde va el nombre "Koda":** en la pantalla o en la carcasa (decisión de diseño físico).
- **Rúbrica de evaluación:** no se sabe qué evalúa formalmente el jurado. Si la universidad la tiene, agregarla aquí.
- **Privacidad de los datos médicos:** no hay definido cifrado ni tiempo de retención para embeddings faciales y signos vitales.
