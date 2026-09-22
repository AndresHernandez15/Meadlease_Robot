# MEADLEASE — REGISTRO DE DECISIONES TÉCNICAS (ADR)

> Formato tipo ADR (Architecture Decision Record), conservado del proyecto anterior. Cada entrada resume: contexto, decisión, alternativas evaluadas y por qué se descartaron, estado.

---

### ADR-001 — Reinicio completo del proyecto desde cero
- **Estado:** Aceptada
- **Contexto:** El sistema anterior se construyó módulo por módulo, optimizando cada uno en aislamiento, sin pensar en integración conjunta ni en cómo cada decisión afecta latencia/memoria/complejidad del sistema completo. Deadline extendido de 1 mayo 2026 a 1 noviembre 2026.
- **Decisión:** Reconstrucción completa. El código anterior no se reutiliza; se conserva solo como referencia histórica de qué ya funcionó.

### ADR-002 — Sistema operativo: Ubuntu 24.04 LTS "Noble"
- **Estado:** Aceptada
- **Alternativa evaluada:** Ubuntu 26.04 "Resolute" (LTS, ~3 meses de vida en el momento de decidir).
- **Por qué se descartó la alternativa:** `libfreenect2`/Kinect V2 es dependencia frágil de comunidad, alto riesgo en un ecosistema recién nacido.

### ADR-003 — Middleware: ROS2 Jazzy Jalisco
- **Estado:** Aceptada
- **Alternativa evaluada:** ROS2 Lyrical Luth (LTS, ~2 meses de vida).
- **Por qué se descartó la alternativa:** mismos errores de mirrors documentados 9 días post-release; Ubuntu 24.04 es solo Tier 3 para Lyrical — no hay combo limpio con Noble.

### ADR-004 — Gestión de entornos Python: `venv --system-site-packages`
- **Estado:** Aceptada
- **Alternativas evaluadas:** Conda, Docker.
- **Por qué se descartaron:** Conda rompe `rclpy` (problema documentado). Docker tiene overhead de RAM/CPU no disponible en el hardware objetivo y DDS entre contenedores es frágil.
- **Nota:** `venv --system-site-packages` es el patrón oficialmente documentado por ROS2 para mezclar `rclpy` con dependencias externas aisladas. Instalador: `uv` (Astral) en vez de pip tradicional, por velocidad de resolución.

### ADR-005 — Puente de comunicación PC↔microcontroladores: STM32 como puente único
- **Estado:** Aceptada
- **Alternativa evaluada:** micro-ROS también en ambos ESP32 (WiFi directo a PC) — viable técnicamente, existe componente oficial micro-ROS para ESP-IDF.
- **Por qué se descartó:** movimiento/parada de emergencia son capa reactiva y no pueden depender de WiFi — riesgo real en demo con auditorio congestionado.

### ADR-006 — Protocolo UART STM32↔ESP32: trama binaria fija + CRC8
- **Estado:** Aceptada (especificación de detalle pendiente, ver Fase 2 del roadmap)
- **Alternativa previa:** texto plano (`"VL:...,VR:...\n"`).
- **Por qué se cambió:** más eficiente de parsear, detecta corrupción de datos, sigue siendo depurable (logs de valores ya decodificados).

### ADR-007 — Botón físico de emergencia como interrupción directa al STM32
- **Estado:** Aceptada
- **Decisión:** no pasa por la trama UART normal; genera un estado de alta prioridad propagado a ROS2 fuera del ciclo normal de la trama.
- **Justificación:** garantiza que la parada de emergencia no compita en latencia/prioridad con el resto de los datos del protocolo binario.

### ADR-008 — Firmware ESP32: PlatformIO + framework Arduino
- **Estado:** Aceptada
- **Alternativa evaluada:** ESP-IDF puro.
- **Por qué se descartó:** más control pero desarrollo más lento; PlatformIO+Arduino da mejor balance de velocidad de desarrollo/estructura para un equipo (Sergio/Linda) con experiencia limitada en firmware.

### ADR-009 — Reconocimiento facial: SCRFD + ArcFace vía ONNX Runtime
- **Estado:** Aceptada
- **Alternativa previa:** LBPH.
- **Por qué se cambió:** LBPH tenía un bug de pipeline multi-usuario incompleto (agregar usuario requería reentrenar). SCRFD+ArcFace soporta agregar usuarios solo agregando su embedding, necesita menos fotos (3-5 vs 200), y es menos sensible a iluminación. Comparte runtime ONNX con VAD/wake word.

### ADR-010 — SLAM: RTAB-Map (actualizado a 0.21.9+)
- **Estado:** Aceptada
- **Alternativas evaluadas:** SLAM Toolbox, Cartographer, GMapping.
- **Por qué se descartaron:** son LiDAR-first, no aptas para RGB-D sin conversión con costo de CPU adicional.
- **Nota:** confirmado con paper académico 2026 sobre Jazzy; versión 0.21.9 corrige bug real de sincronización de `message_filters`.

### ADR-011 — Navegación: Nav2
- **Estado:** Aceptada
- **Nota:** Nav2 usa `BehaviorTree.CPP` internamente, pero es irrelevante para la decisión de framework de BT propio (Capa 5) — se le llama como action server externo; su árbol interno es una caja negra que no se toca.

### ADR-012 — Framework de agencia: Pydantic AI
- **Estado:** Aceptada
- **Alternativa evaluada:** LangGraph.
- **Por qué se descartó:** su fortaleza (grafos de estado complejos) es redundante porque esa complejidad ya vive en el Behavior Tree propio.
- **Justificación de Pydantic AI:** ligero, agnóstico de proveedor/modelo, tipado fuerte — encaja con mensajes ROS2.

### ADR-013 — Proveedor LLM primario: Groq
- **Estado:** Aceptada, con mitigación de riesgo
- **Riesgo identificado:** Groq fue adquirida por Nvidia a inicios de 2026, con reducción de personal técnico y catálogo curado (~12 modelos), patrón de deprecación documentado.
- **Mitigación:** Pydantic AI es agnóstico de proveedor — cambiar proveedor es cambio de configuración, no reescritura de código.
- **Fallback:** cadena de 3 modelos con la key principal de Groq → 3 modelos con la key secundaria de Groq, suficiente sin depender de un segundo proveedor.
- **Modelo inicial:** Llama 3.3 70B Versatile.

### ADR-014 — Framework de Behavior Tree: py_trees + py_trees_ros
- **Estado:** Aceptada
- **Alternativa evaluada:** BehaviorTree.CPP.
- **Por qué se descartó:** no aporta ventaja real dado que no se toca el árbol interno de Nav2; py_trees es Python nativo, mismo lenguaje que el agente y el resto del sistema — más fácil de leer/depurar/explicar.

### ADR-015 — Patrón de integración agente↔BT: agente propone, BT dispone
- **Estado:** Aceptada
- **Decisión:** el agente propone intención vía tool calls; el BT ejecuta, con ramas de mayor prioridad (emergencia, obstáculos) que pueden interrumpir sin consultar al agente.
- **Justificación:** operacionaliza la separación reactiva/deliberativa; validado por patrón académico ROS-LLM.

### ADR-016 — Wake word: openWakeWord
- **Estado:** Aceptada
- **Alternativas evaluadas:** Vosk (usado previamente como wake word), Porcupine.
- **Por qué se descartaron:** Porcupine ya era poco práctico por su límite de "1 dispositivo activo" en tier gratuito, y quedó **eliminado por completo** como opción tras el cierre total del plan gratuito de Picovoice (actualización agosto 2026). openWakeWord corre sobre ONNX Runtime (comparte runtime con VAD/reconocimiento facial) y es más preciso en benchmarks propios con mínimo consumo de CPU.

### ADR-017 — Comandos offline: Vosk acotado solo a emergencia
- **Estado:** Aceptada (revisión de decisión previa)
- **Decisión previa:** comandos rígidos de propósito general vía Vosk.
- **Por qué se revisó:** generaban falsos positivos y quitaban flexibilidad al robot (probado en el sistema anterior). Ahora Vosk se usa exclusivamente para "detente", "ayuda", "emergencia", "reanudar"; todo lo demás pasa por el agente con lenguaje libre.
- **Alternativa a evaluar a futuro:** sherpa-onnx (consolidaría STT+TTS+VAD+wake word bajo un solo runtime ONNX).

### ADR-018 — VAD: TEN VAD
- **Estado:** Aceptada
- **Alternativa previa:** Silero VAD.
- **Alternativas evaluadas:** WebRTC VAD, Cobra VAD (Picovoice).
- **Por qué se cambió/descartaron:** TEN VAD tiene ~32% menos consumo de CPU que Silero y menor latencia de corte de habla. Cobra VAD ya era problemático por ser comercial (mismo problema de licenciamiento que Porcupine), y quedó **eliminado por completo** como opción tras el cierre total del plan gratuito de Picovoice (actualización agosto 2026).

### ADR-019 — STT: Groq Whisper large-v3-turbo
- **Estado:** Aceptada (sin cambio respecto al sistema anterior)
- **Justificación:** confirmado como opción cloud más rápida en 2026 (~216x tiempo real), más barato que alternativas.

### ADR-020 — TTS: Azure `es-PE-CamilaNeural` (primario) + Kokoro (candidato)
- **Estado:** Aceptada como primario; Kokoro en evaluación
- **Nota:** Kokoro (82M parámetros, Apache 2.0, 100% local en CPU) se evalúa solo como alternativa de benchmark de calidad/latencia — no busca independencia de red, ya que el robot depende de internet para STT y LLM de todas formas.

### ADR-021 — Voz-a-voz nativa: descartada
- **Estado:** Rechazada
- **Alternativas evaluadas:** OpenAI Realtime API, Gemini Live, Amazon Nova Sonic.
- **Por qué se descartaron:** sin transcripción limpia (debilita el validador ético estructural), atan a un solo proveedor (rompe la resiliencia del fallback de Groq), modelo económico distinto al diseñado, y son cajas negras que contradicen el principio de transparencia/control del proyecto. Se mantiene arquitectura en cascada STT→LLM→TTS.

### ADR-022 — HMI: NiceGUI sobre Chromium Kiosk
- **Estado:** Aceptada
- **Alternativa evaluada:** Godot Engine.
- **Por qué se descartó:** integración con ROS2 experimental/comunidad, requeriría compilar módulo C++ propio dentro del engine — riesgo frágil similar al driver del Kinect, no apto para el deadline.
- **Justificación de NiceGUI:** construido sobre FastAPI+WebSockets (misma base que el sistema anterior), interfaz en Python puro — unifica lenguaje con agente/BT/nodos ROS2.

### ADR-023 — Botón de parada en HMI: descartado
- **Estado:** Rechazada (la funcionalidad, no el HMI)
- **Justificación:** sin pantalla táctil, mover el mouse hasta el botón no es práctico; se mantiene solo el botón físico.

### ADR-024 — Editor/IDE: VSCode sobre PyCharm
- **Estado:** Aceptada
- **Justificación:** proyecto multi-lenguaje (Python + C/C++ firmware + YAML + Markdown), terreno donde VSCode tiene ventaja documentada sobre PyCharm en comparativas 2026. Extensión PlatformIO para firmware ESP32 en el mismo editor.

### ADR-025 — Estructura del repositorio: un solo repo (monorepo)
- **Estado:** Aceptada
- **Justificación:** desarrollo mayormente secuencial liderado por Andrés; múltiples repos añadirían fricción de coordinación sin beneficio real dado el tamaño del equipo.

### ADR-026 — Exploración autónoma de frontera (mapeo): descartada
- **Estado:** Rechazada
- **Decisión:** modo de mapeo manual/asistido (mover el robot mientras RTAB-Map mapea, guardar desde HMI).
- **Justificación:** exploración autónoma de frontera es complejidad/riesgo desproporcionado para el alcance de prototipo.

### ADR-027 — Recuperación proactiva de memoria entre sesiones: fuera de alcance
- **Estado:** Diferida (bonus post-defensa)
- **Justificación:** filtro de alcance de prototipo — se prioriza memoria de sesión + registro estructurado en BD.

### ADR-028 — Especificación completa de la trama UART STM32↔ESP32
- **Estado:** Aceptada
- **Contexto:** ADR-006 definió el formato general (trama binaria fija + CRC8) pero dejó la especificación de detalle pendiente para Fase 2 del roadmap.
- **Decisión:** Dos líneas UART físicas dedicadas (STM32↔ESP32 Movilidad, STM32↔ESP32 Médica), no bus compartido con direccionamiento. Framing: `[START 0xAA][MSG_TYPE 1B][LEN 1B][PAYLOAD][CRC8 1B][END 0x55]`, CRC8 Maxim/Dallas (polinomio 0x31) calculado sobre `MSG_TYPE+LEN+PAYLOAD`, little-endian, baudrate 115200.
- **Alternativa evaluada:** Bus UART compartido con byte de dirección para ambos ESP32.
- **Por qué se descartó:** Con USARTs libres de sobra en el STM32F411, líneas dedicadas evitan el byte de dirección, evitan arbitraje de bus, y aíslan fallos — ruido o desconexión en el link de Movilidad no puede corromper el link de Médica. Costo adicional de pines es nulo dado el margen disponible.
- **Mensajes definidos — link Movilidad:** `CMD_VELOCITY` (0x01, STM32→ESP32, 20Hz, VL/VR int16 mm/s) · `TELEMETRY` (0x81, ESP32→STM32, 50Hz, RPM izq/der + 5 distancias ultrasonido + bitmask de fallo por sensor + voltage/current del monitoreo de energía).
- **Mensajes definidos — link Médica:** `CMD_DISPENSE` (0x02) · `CMD_MEASURE_VITALS` (0x03) · `CMD_VITALS_ARM` (0x04) · `RESP_DISPENSE` (0x82, incluye resultado consolidado de verificación ESP32-CAM) · `RESP_VITALS` (0x83).
- **Decisión de telemetría de velocidad:** RPM ya calculado en el ESP32 Movilidad (no ticks crudos), reutilizando el cálculo que el ESP32 ya hace para su lazo de control PID — evita carga adicional de cómputo en el i3 del Dell.
- **Ubicación del sensor de energía (INA3221 + divisor de voltaje):** lectura directa desde el ESP32 Movilidad, reportado dentro de `TELEMETRY` — no requiere link ni trama propia.
- **Watchdog de seguridad:** si el ESP32 Movilidad no recibe `CMD_VELOCITY` en 500 ms, frena motores por su cuenta, independiente del botón físico de emergencia (ADR-007).
- **Especificación completa (tablas de payload byte a byte):** ver `HARDWARE_FIRMWARE.md`, sección "Capa 2 — Comunicación PC ↔ Microcontroladores".

### ADR-030 — Terminología: `usuarios` en vez de `pacientes`
- **Estado:** Aceptada
- **Contexto:** El esquema y las herramientas del agente usaban originalmente `pacientes`/`patient_id`, heredado de la idea inicial de un dispositivo médico.
- **Decisión:** Renombrar a `usuarios`/`usuario_id` en toda la base de datos, las tools del agente y la documentación.
- **Justificación:** Koda es un robot doméstico de acompañamiento y cuidado, no un dispositivo médico clínico — "usuarios" refleja correctamente el alcance del producto y evita expectativas de rigor clínico que el proyecto no busca cumplir.

### ADR-031 — Diseño de `horarios_medicacion`: columna discriminadora `tipo_horario`
- **Estado:** Aceptada
- **Contexto:** El horario de un medicamento puede definirse de 3 formas distintas (diario, días específicos de la semana, o cada X horas desde una hora de inicio).
- **Alternativa evaluada:** Una tabla separada por modo de horario (ej. `horarios_diarios`, `horarios_semanales`, `horarios_intervalo`).
- **Decisión:** Una sola tabla `horarios_medicacion` con columna discriminadora `tipo_horario` (`'diario'` | `'dias_semana'` | `'intervalo'`) y columnas opcionales según el modo (`hora`, `dias_semana`, `intervalo_horas`, `hora_inicio`).
- **Por qué se descartó la alternativa:** tres tablas separadas complican el cálculo de "próxima dosis" (requeriría consultar y combinar 3 tablas) y la relación N-a-N usuario↔medicamento se duplicaría en cada una, sin beneficio real para el volumen de datos de un prototipo.
- **Nota:** el cálculo de "próxima dosis" (`get_next_dose`) se resuelve en código según el valor de `tipo_horario`, nunca en el LLM — mismo principio que evita alucinaciones temporales (ver `ROBOT_COGNICION.md`). Un usuario+medicamento tiene un solo patrón de horario vigente a la vez.
- **Detalle del esquema completo:** ver `database/README.md`.

### ADR-032 — Flujo de desarrollo Asus↔Dell: `git pull`, sin Remote-SSH
- **Estado:** Aceptada (revisión de decisión previa)
- **Contexto:** El roadmap original de Fase 0 contemplaba configurar VSCode Remote-SSH entre el Asus y el Dell para editar/depurar directo sobre el Dell desde el Asus.
- **Decisión:** Se descarta Remote-SSH. Cada máquina tiene su propio `venv --system-site-packages`. El desarrollo y la configuración ocurren en el Asus; el Dell se usa vía `git pull` únicamente para pruebas que dependen de su hardware real (micrófono, latencia) y, más adelante, para integración final y la demo.
- **Por qué se descartó:** Remote-SSH añade una capa de configuración y dependencia de red sin necesidad real — ambas máquinas corren el mismo SO/misma versión de ROS2, así que un `venv` propio en cada una más `git pull` ya da paridad de entorno sin la fragilidad de mantener una sesión SSH persistente entre ellas.

---

## Información faltante / pendiente de revisión

- **Fechas de decisión** de cada ADR (el documento maestro no registra cuándo se tomó cada decisión, solo que fue "en la sesión de reformulación de agosto 2026") — si se quiere trazabilidad real tipo ADR, convendría fechar cada una.
- **Autores/participantes por decisión:** no se distingue qué decisiones fueron discutidas con todo el equipo vs. solo Andrés+Claude.
- Este archivo es una **compilación derivada** del documento maestro, no decisiones nuevas — al completar los vacíos identificados en los demás archivos (`ROBOT_COGNICION.md`, etc.), probablemente surgirán ADRs nuevos (ej. diseño del árbol py_trees) que deben añadirse aquí. **ADR-029 queda reservado** para esa decisión pendiente (árbol raíz de py_trees) cuando se cierre; ADR-030 y ADR-031 ya documentan decisiones de esquema de base de datos tomadas antes de cerrar esa.
