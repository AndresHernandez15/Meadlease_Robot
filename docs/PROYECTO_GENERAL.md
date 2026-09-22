# MEADLEASE — PROYECTO GENERAL

## 1. Contexto general

| Campo | Valor |
|---|---|
| Universidad | Universidad Tecnológica de Bolívar — Ing. Mecatrónica, Biomédica y Sistemas |
| Deadline funcional | 1 de Noviembre de 2026 |
| Nombre del proyecto | Meadlease |
| Nombre del robot | **Koda** — del japonés *kodawari*, que refleja tanto la filosofía de diseño del proyecto como el comportamiento esperado del robot: atención al detalle y ausencia de errores (ej. en una dosis de medicamento). Meadlease sigue siendo el nombre del proyecto/tesis; Koda es solo el nombre del robot |
| Formato de entrega | Prototipo/demo, no producto terminado. Sustentación en vivo de 15 minutos + posibles clips de video para autonomía de largo plazo no demostrable en vivo |
| Motivo de la reformulación | El sistema anterior se construyó módulo por módulo, optimizando cada uno en aislamiento, sin pensar en integración conjunta ni en cómo cada decisión afecta latencia/memoria/complejidad del sistema completo |

## 2. Equipo y roles

| Integrante | Perfil | Rol en esta reformulación |
|---|---|---|
| **Andrés** (líder) | Ing. Mecatrónica + Ing. Sistemas | Responsable de software: ROS2, agente, BT, HMI, percepción, integración. Trabaja de forma secuencial con apoyo de Claude (planificación/decisiones/arquitectura) y GitHub Copilot Pro (implementación de código pesado) |
| **Linda** | Ing. Biomédica + Mecatrónica | Diseño mecánico, dispensador (ya 100% funcional, ajustes en curso), firmware ESP32 Médica (con apoyo/especificación de Andrés) |
| **Sergio** | Ing. Mecatrónico | Cableado del robot, PCB de movilidad, firmware ESP32 Movilidad (con apoyo/especificación de Andrés) |
| **Juan** | Ing. Mecatrónico | Visión artificial — módulo autocontenido, mayor autonomía relativa |

**Nota de riesgo identificada y aceptada conscientemente:** la carga de software recae casi enteramente en Andrés. Mitigación: piezas paralelizables sin requerir experiencia en ROS/Python se delegan como tareas guiadas (ej. ejecutar un benchmark siguiendo pasos claros, pruebas físicas de una herramienta ya especificada) para liberar tiempo de Andrés.

## 3. Filosofía y principios de ingeniería (transversal — rige todos los módulos)

- **Reconstrucción desde cero.** Código anterior no se reutiliza (ni siquiera el HMI). Se conserva como referencia histórica de qué ya funcionó (ej. voz Azure Camila, GroqCloud, etc).
- **Diseño integrado, no módulos aislados.** Cada decisión tecnológica se evalúa por cómo encaja con el resto del sistema (latencia compartida, memoria compartida, complejidad de integración), no solo por su mérito individual.
- **Modularidad con profundidad de carpetas balanceada.** Separación clara de responsabilidades sin árboles de subcarpetas excesivos. Preferencia por organización plana y clara sobre jerarquía profunda.
- **Código legible y explicable.** Debe poder entrarse a cualquier parte, entenderla, y modificarla sin arriesgar romper otra cosa.
- **Eficiencia como principio de diseño desde el inicio**, evaluada contra el hardware real: Dell Inspiron 3421, i3-3227U (2013, sin AVX2), 12GB RAM DDR3, sin GPU.
- **Adaptabilidad a la máquina de ejecución.** El código no asume hardware fijo: si algo se paraleliza (multiprocessing, threads, workers), la cantidad de cores/hilos se detecta en tiempo de ejecución (ej. `os.cpu_count()` o equivalente), nunca se hardcodea. El mismo código debe poder correr sin cambios en el Asus, el Dell, o eventualmente una Raspberry Pi 4/5, ajustándose automáticamente a los recursos disponibles.
- **Tareas de configuración/infraestructura de una sola vez se hacen MANUALMENTE**, paso a paso (tipo tutorial), por decisión explícita de Andrés — genera conocimiento propio real. Aplica a: instalación de herramientas, creación de esquemas de BD (SQLite), configuración de entornos. NO aplica al código de aplicación normal (consultas, lógica de negocio, funciones del agente).
- **Objetivo central del producto:** que el robot se sienta autónomo, inteligente y "vivo" — no un chatbot con ruedas. Debe iniciar comportamiento sin ser llamado, tomar decisiones, y actuar con propósito propio.
- **Filtro de alcance de prototipo:** no se optimiza para robustez de largo plazo ni casos extremos de un producto terminado. Se optimiza para funcionar de forma consistente y demostrable en el entorno controlado de la sustentación.
- **Filtro aplicado a cada función definida:** cada una se etiquetó como *esencial*, *demo en vivo*, *mostrada en video*, *corre en background sin mostrarse explícitamente*, *opcional/bonus si da tiempo*, o *eliminada del alcance*.
- **Cada herramienta/acción se valida de forma aislada** (script simple, sin depender del robot completo) antes de conectarla al agente/árbol.
- **Diseño antes que código generado:** cada pieza se especifica primero en conversación con Claude (arquitectura, contratos, comportamiento esperado) antes de que Copilot la implemente.

## 4. Resumen ejecutivo de objetivos por módulo

| Módulo | Resumen de una línea | Documento detallado |
|---|---|---|
| 1 — Percepción | Detección de presencia + reconocimiento facial multiusuario + soporte a SLAM/navegación | `ROBOT_PERCEPCION.md` |
| 2 — Cognición / Agencia | Agente LLM (Pydantic AI) que propone metas + Behavior Tree (py_trees) que ejecuta y protege con reflejos | `ROBOT_COGNICION.md` |
| 3 — Movilidad y Navegación | Navegación autónoma A→B, búsqueda activa del usuario, aproximación social, regreso a base | `ROBOT_MOVILIDAD.md` |
| 4 — Interacción Conversacional | Conversación natural en español, comandos offline de emergencia, escalación a humano vía Telegram | `ROBOT_VOZ.md` |
| 5 — Salud y Cuidado Médico | Dispensación, signos vitales, emergencias (parada física/voz) | `ROBOT_COGNICION.md` (como herramientas del agente) |
| 6 — Expresividad / HMI | Comunicación de estado sin palabras, dashboard de salud, mapa interactivo, control remoto QR | `ROBOT_HMI.md` |
| 7 — Backbone físico / Comunicaciones | Comunicación en tiempo real cerebro↔actuadores, resiliencia básica, autonomía energética | `HARDWARE_FIRMWARE.md` |

## 5. Entorno y flujo de desarrollo

| Aspecto | Decisión | Justificación |
|---|---|---|
| Máquinas de trabajo | **Asus ROG Strix** (PC personal de Andrés, Ubuntu 24.04, i5 10ª gen, 16GB RAM) para desarrollo diario · **Dell Inspiron** (Ubuntu 24.04 + ROS2 Jazzy ya instalados) para pruebas que dependen de su hardware real (micrófono, latencia) y, más adelante, integración final y la demo en sí | Mismo SO/misma versión de ROS2 en ambas máquinas — evita fricción de compatibilidad. Compilación e iteración mucho más rápida en el Asus que en el i3 del Dell |
| Principio rector | **Desarrollo nativo en ROS2 desde el día uno** — nada de desarrollo Windows-first con wrappers (lección aprendida del primer ciclo de desarrollo) | Windows queda reservado solo para piezas genuinamente multiplataforma sin fricción: firmware ESP32 (PlatformIO/Arduino) y prototipos sueltos de lógica Python sin `rclpy` |
| Sincronización | GitHub como puente entre el Asus y el Dell — cada máquina con su propio `venv`, sin Remote-SSH | Se desarrolla y configura en el Asus; `git pull` en el Dell solo cuando se necesite probar algo que depende de su hardware real (micrófono, latencia) |
| Editor/IDE | **VSCode** (sobre PyCharm) | Proyecto multi-lenguaje (Python + C/C++ firmware + YAML + Markdown). Extensión PlatformIO para firmware ESP32 en el mismo editor |
| Nota STM32 | Explorar extensión oficial "STM32Cube para VSCode" para consolidar también ese firmware en el mismo editor — STM32CubeIDE queda como alternativa segura si no conviene | — |
| Estructura del repositorio | **Un solo repo** (`ros2_ws/`, `firmware/` con subcarpetas por MCU, `docs/`) — no repos separados | Desarrollo mayormente secuencial liderado por Andrés; múltiples repos añadirían fricción de coordinación sin beneficio real dado el tamaño del equipo |
| Equipo de desarrollo (metáfora operativa) | Andrés (decisiones/ejecución) + Claude (planificación/arquitectura/decisiones clave) + GitHub Copilot Pro (implementación de código pesado) ≈ equivalente funcional a equipo de 3 | Desarrollo secuencial pero con coherencia total de diseño |

### Capa 1 — Sistema Operativo y Middleware (transversal, no pertenece a un paquete específico)

| Decisión | Valor | Justificación |
|---|---|---|
| SO | **Ubuntu 24.04 LTS "Noble"** (ya instalado en el Dell) | Se evaluó Ubuntu 26.04 "Resolute" — descartado: `libfreenect2`/Kinect V2 es dependencia frágil de comunidad, alto riesgo en ecosistema recién nacido |
| Middleware | **ROS2 Jazzy Jalisco** (ya instalado en el Dell) | Se evaluó ROS2 Lyrical Luth — mismos errores de mirrors documentados, Ubuntu 24.04 es solo Tier 3 para Lyrical |
| Python | **3.12** (impuesto por Jazzy/Ubuntu 24.04, ruta Tier 1 sin compilar ROS2 desde source) | — |
| Gestión de entornos | **`venv` con `--system-site-packages`** | Patrón oficialmente documentado por ROS2 para mezclar `rclpy` con dependencias externas aisladas. Conda descartado (rompe `rclpy`). Docker descartado (overhead de RAM/CPU no disponible, DDS entre contenedores frágil) |
| Instalador | **`uv`** (Astral) en vez de pip tradicional | Instalación/resolución de dependencias más rápida |

### Capa 8 — Datos (transversal)

| Componente | Decisión |
|---|---|
| Motor | SQLite |
| Esquema | 5 tablas (usuarios, medicamentos, horarios_medicacion, signos_vitales, registros_dispensacion) + tabla de notas persistentes |
| Método de creación | **Manual, paso a paso, guiado** — no generado automáticamente |
| Acceso desde código | Vía funciones/herramientas del agente (ver `ROBOT_COGNICION.md`) |

### Convenciones de código

- **Código en inglés** (nombres, comentarios — estándar del ecosistema ROS2/Python).
- **Contenido orientado al usuario en español** (prompts del agente, textos del HMI, mensajes de Telegram).
- `.gitignore` para `build/`, `install/`, `log/`, y `.env`.
- `.env` (credenciales reales, nunca en git) + `.env.example` (plantilla sin valores) — Groq, Azure, Telegram.

### Estructura del repositorio (referencia — detalle de tareas en `ROADMAP.md`)

```
meadlease/
├── ros2_ws/
│   └── src/
│       ├── robot_bringup/       ← launch files, config Nav2/RTAB-Map, waypoints, URDF — Andrés
│       ├── robot_interfaces/    ← mensajes/servicios/acciones personalizados — Andrés
│       ├── robot_perception/    ← detección de presencia + reconocimiento facial — Juan
│       ├── robot_voice/         ← wake word, VAD, STT, TTS, filler, backchanneling — Andrés
│       ├── robot_cognition/     ← agente Pydantic AI + Behavior Tree py_trees — Andrés
│       └── robot_hmi/           ← NiceGUI + bridge a ROS2 — Andrés
├── firmware/
│   ├── stm32_backbone/          ← Andrés (STM32CubeIDE)
│   ├── esp32_movilidad/         ← Sergio (PlatformIO, sobre spec+plantilla)
│   └── esp32_medica/            ← Linda (PlatformIO, sobre spec+plantilla)
├── database/
│   ├── schema.sql                ← creado a mano, no generado
│   └── README.md                 ← pasos manuales de instalación/creación
├── docs/                          ← documentación modular
├── scripts/
│   └── benchmarks/                ← los 4 scripts de benchmark pendientes
├── simulation/                    ← mundos/modelos Gazebo (pruebas en el Asus)
├── .env.example
├── .gitignore
└── README.md
```

*(Nota: `robot_perception` como paquete separado no es solo prolijidad — es la frontera de trabajo de Juan, quien solo necesita tocar esa carpeta sin fricción de coordinación con el resto.)*

---

## Información faltante / pendiente de revisión

- **Ubicación del nombre** (HMI vs. carcasa física): pendiente de decisión de diseño físico.
- **Criterios/rúbrica de evaluación institucional:** no hay referencia a qué evalúa formalmente el jurado en la sustentación — si existe documentación de la universidad al respecto, complementar aquí.
- **Política de privacidad/retención de datos médicos en SQLite:** no se especifica cifrado en reposo ni tiempo de retención de embeddings faciales/signos vitales — relevante por ser datos biomédicos sensibles.
- **Dimensiones/layout del espacio de la demo:** no está descrito (relevante para número de waypoints y tiempos, ver `ROADMAP.md` Fase 5).
