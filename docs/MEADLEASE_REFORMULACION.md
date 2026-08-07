# MEADLEASE — DOCUMENTO MAESTRO DE REFORMULACIÓN
## Base de la nueva documentación del proyecto (v1 — pendiente de dividir en archivos específicos)

> **Fecha de esta reformulación:** Agosto 2026
> **Motivo:** Deadline extendido de 1 mayo 2026 a 1 de noviembre de 2026. Reinicio completo del proyecto desde cero — código anterior conservado solo como referencia de decisiones ya validadas, no reutilizado.
> **Naturaleza de este documento:** contiene TODAS las decisiones, objetivos, alternativas evaluadas y pendientes discutidos en la sesión de reformulación. Es el insumo crudo para reconstruir la documentación modular del proyecto.

---

## 0. CONTEXTO GENERAL

| Campo | Valor |
|---|---|
| Universidad | Universidad Tecnológica de Bolívar — Ing. Mecatrónica, Biomédica y Sistemas
| Deadline funcional | 1 de Noviembre de 2026 (extendido) |
| Nombre del proyecto | Meadlease (se mantiene) |
| Nombre del robot | **EN DEFINICIÓN** Criterio: fácil de pronunciar en español sin conocimiento de inglés, no genérico |
| Formato de entrega | **Prototipo/demo**, no producto terminado para entorno real. Sustentación en vivo de 15 minutos + posibles clips de video para autonomía de largo plazo no demostrable en vivo |
| Motivo de la reformulación | El sistema anterior se construyó módulo por módulo, optimizando cada uno en aislamiento, sin pensar en integración conjunta ni en cómo cada decisión afecta latencia/memoria/complejidad del sistema completo |

### Equipo y roles

| Integrante | Perfil | Rol en esta reformulación |
|---|---|---|
| **Andrés** (líder) | Ing. Mecatrónica + Ing. Sistemas | Responsable de **todo el software**: ROS2, agente, BT, HMI, percepción, integración. Decisión explícita y consciente — es el único del equipo con perfil de sistemas. Trabaja de forma secuencial con apoyo de Claude (planificación/decisiones/arquitectura) y GitHub Copilot Pro (implementación de código pesado) |
| **Linda** | Ing. Biomédica + Mecatrónica | Diseño mecánico, dispensador (dispensador ya 100% funcional, ajustes en curso: tornillo sin fin metálico en vez de impreso), firmware ESP32 Médica (con apoyo/especificación de Andrés — experiencia limitada en ROS/Python) |
| **Sergio** | Ing. Mecatrónico | Cableado del robot, PCB de movilidad (resolviendo falsos contactos en ultrasonidos), firmware ESP32 Movilidad (con apoyo/especificación de Andrés — experiencia limitada en ROS/Python) |
| **Juan** | Ing. Mecatrónico | Visión artificial — módulo autocontenido, mayor autonomía relativa) |

**Nota de riesgo identificada y aceptada conscientemente:** la carga de software recae casi enteramente en Andrés. Mitigación: piezas paralelizables sin requerir experiencia en ROS/Python se delegan como tareas guiadas (ej. ejecutar un benchmark siguiendo pasos claros, pruebas físicas de una herramienta ya especificada) para liberar tiempo de Andrés sin exigir experiencia que el resto del equipo no tiene.

### Estado del hardware (al momento de esta reformulación)

| Elemento | Estado |
|---|---|
| Impresión 3D | ~90% — cuerpo completo impreso incluyendo cabeza y cuello. Falta: compuertas de mantenimiento y brazo de signos vitales |
| Post-procesado | Iniciado (Todo el equipo), ~1 semana estimada una vez impresas las piezas faltantes |
| Cableado | En curso (Sergio), en paralelo al post-procesado — objetivo: robot completamente cableado antes de pegar/masillar la carcasa de forma definitiva, dejando solo las compuertas de mantenimiento como punto de acceso |
| Dispensador (pastillero) | **100% funcional**, ajustes menores en curso (Linda) — cambio de tornillo sin fin impreso en 3D por uno metálico, para mejorar tolerancias y suavidad |
| PCB de movilidad | En curso (Sergio) — resolviendo falsos contactos en sensores ultrasónicos JSN-SR04T |
| Dell Inspiron (placa) | **Desmontable** — actualmente fuera de la carcasa, en el escritorio de Andrés, con acceso total a cámara/micrófono/puertos. **Ubuntu 24.04 + ROS2 Jazzy ya instalados limpios**. La pantalla del Dell también está desmontada y en el mismo escritorio junto al equipo — todas las pruebas de desarrollo (incluido el HMI) se realizan con esa misma pantalla, de forma consistente hasta el ensamblaje final |
| PCB Médica / firmware ESP32 Médica | Pendiente, en coordinación con especificación de protocolo (ver Fase 2 de la ruta) |

---

## 1. FILOSOFÍA Y PRINCIPIOS DE INGENIERÍA (transversal — rige todos los módulos)

- **Reconstrucción desde cero.** Código anterior no se reutiliza (ni siquiera el HMI). Se conserva como referencia histórica de qué ya funcionó (ej. voz Azure Camila, GroqCoud, etc).
- **Diseño integrado, no módulos aislados.** Cada decisión tecnológica se evalúa por cómo encaja con el resto del sistema (latencia compartida, memoria compartida, complejidad de integración), no solo por su mérito individual.
- **Modularidad con profundidad de carpetas balanceada.** Separación clara de responsabilidades sin árboles de subcarpetas excesivos. Preferencia por organización plana y clara sobre jerarquía profunda.
- **Código legible y explicable.** Debe poder entrarse a cualquier parte, entenderla, y modificarla sin arriesgar romper otra cosa.
- **Eficiencia como principio de diseño desde el inicio**, evaluada contra el hardware real: Dell Inspiron 3421, i3-3227U (2013, sin AVX2), 12GB RAM DDR3, sin GPU.
- **Tareas de configuración/infraestructura de una sola vez se hacen MANUALMENTE**, paso a paso (tipo tutorial), por decisión explícita de Andrés — para generar conocimiento propio real. Aplica a: instalación de herramientas, creación de esquemas de BD (SQLite), configuración de entornos. NO aplica al código de aplicación normal (consultas, lógica de negocio, funciones del agente) — eso sí se construye como código.
- **Objetivo central del producto:** que el robot se sienta autónomo, inteligente y "vivo" — no un chatbot con ruedas. Debe iniciar comportamiento sin ser llamado, tomar decisiones, y actuar con propósito propio.
- **Filtro de alcance de prototipo:** no se optimiza para robustez de largo plazo ni casos extremos de un producto terminado (ej. "qué pasa si el usuario se cae y nadie llega"). Se optimiza para funcionar de forma consistente y demostrable en el entorno controlado de la sustentación.
- **Filtro aplicado a cada función definida:** cada una se etiquetó como *esencial*, *demo en vivo*, *mostrada en video*, *corre en background sin mostrarse explícitamente*, *opcional/bonus si da tiempo*, o *eliminada del alcance*.
- **Cada herramienta/acción se valida de forma aislada** (script simple, sin depender del robot completo) antes de conectarla al agente/árbol — evita confundir un bug de implementación con un fallo de decisión del LLM.
- **Diseño antes que código generado:** cada pieza se especifica primero en conversación con Claude (arquitectura, contratos, comportamiento esperado) antes de que Copilot la implemente — mantiene coherencia de diseño en un desarrollo mayormente secuencial.

---

## 2. OBJETIVOS FUNCIONALES POR MÓDULO

### MÓDULO 1 — Percepción

| Función | Alcance | Demo |
|---|---|---|
| Detección de presencia | Cámara Dell integrada (no Kinect, ahorro energético) — a validar calidad de cámara en Fase 1 | Background, siempre activa |
| Identificación de usuario | Acotada exclusivamente a gatear la dispensación de medicamentos. **Debe soportar 2 usuarios o más registrados simultáneamente** (ej. varios adultos mayores en el mismo hogar) — cada uno con su propio embedding facial, su propio esquema de medicación y su propio historial | Momento en vivo específico (usuario no reconocido → no dispensa; usuario reconocido → se identifica cuál es antes de dispensar) |
| Mapeo y localización propia | Esencial | Soporte de navegación |
| Detección de obstáculos/personas en movimiento | Esencial | Soporte de navegación |
| Escucha ambiental continua | **Eliminada** | — |
| Estado interno de "atención" | Explorable, no bloqueante | Bonus |
| Kinect V2 | Reservado exclusivamente a SLAM/navegación — se activa solo cuando el robot necesita moverse, no constante | — |

### MÓDULO 2 — Cognición / Agencia

- **Arquitectura híbrida:** capa reactiva (Behavior Tree, siempre activa, sin LLM) + capa deliberativa (agente con LLM, decide metas e inicia comportamiento). El agente **propone** intenciones; el árbol **dispone y protege** (ejecuta, con reflejos de mayor prioridad que pueden interrumpir).
- **Gestión de metas propias:** basada en horarios de medicación/mediciones, extendiendo esquema de BD existente.
- **Iniciativa proactiva:** nivel **moderado** — saluda/comenta espontáneamente al reconocer presencia tras ausencia, más 3 disparadores: (1) horario médico próximo/vencido, (2) valor de signos vitales fuera de rango, (3) saludo al detectar presencia.
- **Personalidad definida:** base calmada y profesional (tipo cuidador/enfermero), con humor ligero ocasional y curiosidad genuina (hace preguntas propias). Nunca payasesco ni frío.
- **Memoria:** de sesión (contexto conversacional, turnos deslizantes) + registro estructurado en BD para datos importantes (mediciones, dispensaciones, notas puntuales vía herramienta `save_note`). Recuperación proactiva de memoria entre sesiones distintas: **fuera de alcance por ahora** (bonus post-defensa).
- **Priorización de tareas en conflicto:** jerarquía fija en el Behavior Tree (emergencia > tarea médica en curso > conversación > reposo), sin arbitraje vía LLM.
- **Adaptación de urgencia:** cambio de tono/color HMI según nivel de prioridad del evento.
- **Límites éticos:** capa de validación **estructural y dura** sobre la salida del agente (nunca diagnostica, nunca prescribe, sólo da recomendaciones y deriva a supervisión humana) — implementada como validator de Pydantic AI, no como instrucción de prompt únicamente.

### MÓDULO 3 — Movilidad y Navegación

| Función | Alcance | Demo |
|---|---|---|
| Navegación autónoma A→B | Esencial, con waypoints con nombre (vía Nav2 Waypoint Follower) | En vivo — mayor impacto visual |
| Búsqueda activa del usuario | Recorrido de waypoints ordenados por cercanía, apoyada en percepción continua (Módulo 1) — sin lógica de detección propia duplicada. Flujo: navega a siguiente waypoint no visitado → percepción detecta persona (en background) → si detecta, se acerca y reconoce → si es el usuario, atiende tarea; si no, continúa → si se acaban waypoints sin encontrarlo, notifica (Telegram) y regresa a base. **Interrumpible por voz:** si durante la búsqueda el usuario llama al robot (ej. "¡Aquí estoy!"), el agente lo reconoce, detiene el recorrido a waypoints y dispara la búsqueda de persona en la posición actual en lugar de continuar al siguiente waypoint — refuerza el objetivo de que el robot se sienta atento/vivo, no en piloto automático ciego | Video (mejor que en vivo por tiempo), con el momento de interrupción por voz como posible instante en vivo |
| Aproximación social | Velocidad/distancia cómodas — reutiliza comportamiento APPROACHING | En vivo, parte natural del movimiento |
| Seguimiento (follow-me) | **Opcional/bonus** — construir solo si el tiempo alcanza, es la función más costosa de toda la lista (tracking continuo + control de velocidad en lazo cerrado) | Demo si se construye |
| Regreso a base/carga | Esencial para operación, bajo perfil en demo | Background |
| Parada de emergencia | No negociable — resuelta en hardware + reflejo de capa reactiva | Podría mostrarse en vivo |
| Bloqueo de movimiento durante dispensación | Esencial | Implícito |
| Mapa interactivo tipo Roomba en HMI | Mostrar occupancy grid de Nav2, clic para definir waypoints y estación de carga | Construcción/config, no necesariamente demo en vivo |
| Modo de mapeo | **Manual/asistido** (mover el robot mientras RTAB-Map mapea, guardar desde HMI) — exploración autónoma de frontera **descartada** por complejidad/riesgo desproporcionado para el alcance de prototipo | Config previa a la demo |
| Control remoto vía QR | Página adicional del mismo servidor NiceGUI (`/control`), QR codifica la URL, mismo WiFi que comparte el celular durante la demo. Útil para mover el robot manualmente durante mapeo | Herramienta de operación, no de demo en vivo |

### MÓDULO 4 — Interacción Conversacional

| Función | Alcance | Demo |
|---|---|---|
| Conversación natural en español | Esencial, lenguaje libre | En vivo — corazón de la demo |
| Comandos offline críticos | **Acotados solo a emergencia** ("detente", "ayuda", "emergencia") — decisión revisada: comandos rígidos de propósito general generaban falsos positivos y quitaban flexibilidad; todo lo demás pasa por el agente con lenguaje libre | Red de seguridad, no exhibición directa |
| Diálogo con memoria de turno | Esencial (ver Módulo 2) | En vivo |
| Iniciativa conversacional | Ligada a disparadores del Módulo 2 | En vivo, momento clave |
| Consulta de salud/medicación con datos reales | Esencial | En vivo |
| Información general de salud | Con límites éticos del Módulo 2 | En vivo si surge |
| Escalación a humano | **Vía bot de Telegram (real, ya funcional)** — el robot confirma verbalmente el envío | En vivo, notificación real llega al celular del presentador |
| Expresividad emocional coherente con HMI | Esencial | Constante |
| Filler / respuesta mientras procesa | Streaming de LLM a TTS frase por frase (mayor impacto real en latencia) + banco de frases cortas pre-escritas/pre-sintetizadas para cuando el agente invoca una herramienta que toma tiempo real (navegar, dispensar, medir) | Transversal |

### MÓDULO 5 — Salud y Cuidado Médico

**5A — Dispensación:** programada y bajo demanda, verificación de identidad previa (Módulo 1), confirmación real de entrega, registro y trazabilidad completa. Manejo de excepciones acotado a casos realistas de demo (usuario no reconocido, fallo de caída de pastilla) — sin manejo exhaustivo de fallos mecánicos poco probables.

**5B — Signos vitales:** medición bajo demanda y programada, registro histórico **con vista de tendencias en el tiempo** (útil para cuidador/médico — confirmado como valioso), reacción visible (tono/color) ante valores fuera de rango, sin lógica médica de interpretación sofisticada.

**5C — Emergencias:** activación por botón físico (hardware, máxima prioridad, no cancelable por voz) y por comando de voz offline — ambas esenciales. Ambas vías realizan **exclusivamente** una parada de emergencia: frenar motores/movimiento y quedar a la espera de reanudación explícita — no envían notificaciones ni ejecutan ninguna otra acción. **Detección autónoma de anomalías (sin que nadie la pida): fuera de alcance**, no es objetivo funcional de esta fase.

**Distinción importante — parada de emergencia vs. `notify_emergency_contact`:** son dos mecanismos independientes que no se disparan mutuamente. La parada de emergencia (botón físico o comando de voz offline) **solo** detiene el robot. `notify_emergency_contact` **solo** envía un aviso (Telegram) al cuidador/usuario — por ejemplo cuando no se encuentra al usuario y hay una toma pendiente, o cuando el usuario lo pide explícitamente — y **en ningún caso detiene el funcionamiento del robot**.

**Reanudación tras parada de emergencia:** se acepta cualquiera de dos vías equivalentes — un segundo press del mismo botón físico, o el comando de voz offline "reanudar" (mismo canal Vosk que los comandos de emergencia). Cualquiera de las dos libera el reflejo de parada en el Behavior Tree y permite retomar la actividad previa.

### MÓDULO 6 — Expresividad / HMI

- Comunicación de estado sin palabras — esencial.
- Coherencia emocional entre expresión visual y lo dicho/hecho.
- Dashboard de datos de salud, medicación, historial (con gráfico de tendencias de signos vitales).
- Interacción táctil (trackpad) + numpad MPR121 (ya montado en hardware — decisión pendiente es *para qué* se usa, no si se usa).
- Cierre automático de dashboard por privacidad — bonus, no bloqueante.
- Efectos de sonido de retroalimentación (ej. beep al dejar de escuchar) — capa transversal de audio, no depende del framework de HMI elegido.
- Indicador discreto de conectividad (modo online/offline).
- Indicador de batería.
- Pantalla tipo "slideshow" de capacidades del robot cuando se le pregunta qué puede hacer.
- Estado visual de "espera de confirmación" (cuando el robot pregunta algo y espera respuesta).
- Botón de parada en HMI: **descartado** — sin pantalla táctil, mover el mouse hasta el botón no es práctico; se mantiene solo el físico.
- Nombre del robot en pantalla de reposo: **probablemente innecesario** si el nombre se coloca en la carcasa física — pendiente de decisión de diseño físico.
- Pantalla de "modo cuidador" con datos médicos ampliados: **descartada**, fuera de alcance/objetivos definidos.

### MÓDULO 7 — Backbone físico / Comunicaciones

- Comunicación en tiempo real entre cerebro (agente+BT) y actuadores, sin latencia perceptible.
- Resiliencia básica: si un módulo no crítico falla (HMI, conversación), el robot mantiene funciones esenciales de seguridad y movimiento.
- Autonomía energética suficiente para la duración de la demo, con aviso proactivo de batería baja.
- Auto-diagnóstico básico de sensores.

---

## 3. HERRAMIENTAS DEL AGENTE (Pydantic AI)

Filtro aplicado: solo son "herramientas" las acciones que el LLM decide activamente invocar según contexto. Los reflejos de seguridad (parada de emergencia, evasión de obstáculos) **nunca** pasan por el agente — viven directo en el Behavior Tree.

### Funcionales

| Herramienta | Qué hace |
|---|---|
| `navigate_to(location)` | Navega a un waypoint con nombre vía Nav2 |
| `find_user()` | Dispara flujo de búsqueda por waypoints |
| `return_to_base()` | Regreso a carga |
| `dispense_medication(medication_id)` | Verifica identidad internamente, dispensa, devuelve resultado |
| `list_medications()` | Consulta medicamentos cargados |
| `measure_vitals(kind)` | Dispara medición real (bpm/spo2/temperature/all) |
| `get_last_vitals(patient_id)` | Consulta última medición guardada |
| `get_next_dose(patient_id)` | Próxima dosis y tiempo restante (cálculo en código, no en LLM — evita alucinaciones temporales) |
| `get_dose_history(patient_id, limit)` | Historial de dispensaciones |
| `save_note(patient_id, text)` | Guarda nota relevante mencionada en conversación |
| `notify_emergency_contact(reason)` | Notificación real vía Telegram al cuidador/usuario (ej. toma pendiente sin encontrar al usuario, o solicitud explícita). **No detiene el robot** — es independiente y no equivalente a la parada de emergencia (ver Módulo 5C) |

### Demostrativas (opcionales, no afectan funcionalidad núcleo)

| Herramienta | Complejidad | Nota |
|---|---|---|
| `approach_person()` | Baja | Reutiliza comportamiento APPROACHING ya construido |
| `turn_in_place(degrees, direction)` | Muy baja | Rotación pura vía odometría |
| `extend_vitals_arm()` | Trivial | Aísla movimiento del servo MG996R ya existente |
| `follow_person(duration_s)` | **Alta** | La más costosa — última prioridad |
| `greet()` | Baja | Combinación: frase + expresión facial amigable + ligero movimiento del brazo de signos vitales (el robot no tiene brazo/cuello motorizado dedicado a saludar) |

**Comportamientos compuestos (combinan herramientas atómicas, no son herramientas nuevas):** `spin_and_greet` (turn_in_place + greet, útil para arranque de demo), mostrar compartimentos de medicamentos en pantalla al usar `list_medications`.

**Nota de diseño pendiente:** `dispense_medication` recibe un `medication_id`, no el nombre hablado — la traducción de lenguaje natural ("la de la presión") al ID correcto la resuelve el LLM con el contexto de `list_medications` en su prompt. **Validación obligatoria:** el `medication_id` (y en general cualquier valor fijo proveniente de la base de datos — IDs de medicamento, de paciente, de waypoint, etc.) que el LLM incluya en una llamada a herramienta debe validarse contra la base de datos antes de ejecutar la acción, en vez de confiar en que el LLM lo generó correctamente — mismo principio del validador ético estructural (Módulo 2), aplicado aquí como validación estructural de datos.

---

## 4. ARQUITECTURA TÉCNICA POR CAPAS

### Capa 0 — Hardware físico (🔒 fijo, sin cambios)
Dell Inspiron 3421 (i3-3227U, 12GB RAM DDR3, sin GPU) · STM32F411 Blackpill · ESP32 S3 ×2 (Movilidad, Médica) · Kinect V2 · Cámara Dell integrada · Motores BLDC+ZS-X11H, steppers 28BYJ-48, servo MG996R, bomba ZT370.

### Capa 1 — Sistema Operativo y Middleware
| Decisión | Valor | Justificación |
|---|---|---|
| SO | **Ubuntu 24.04 LTS "Noble"** (ya instalado en el Dell) | Se evaluó Ubuntu 26.04 "Resolute" (LTS, ~3 meses de vida) — descartado: `libfreenect2`/Kinect V2 es dependencia frágil de comunidad, alto riesgo en ecosistema recién nacido |
| Middleware | **ROS2 Jazzy Jalisco** (ya instalado en el Dell) | Se evaluó ROS2 Lyrical Luth (LTS, ~2 meses de vida, mismos errores de mirrors documentados 9 días post-release, Ubuntu 24.04 es solo Tier 3 para Lyrical — no hay combo limpio) |
| Python | **3.12** (impuesto por Jazzy/Ubuntu 24.04, ruta Tier 1 sin compilar ROS2 desde source) | — |
| Gestión de entornos | **`venv` con `--system-site-packages`** | Patrón oficialmente documentado por ROS2 para mezclar `rclpy` con dependencias externas aisladas. Conda descartado (rompe `rclpy`, problema documentado). Docker descartado (overhead de RAM/CPU no disponible, DDS entre contenedores frágil) |
| Instalador | **`uv`** (Astral) en vez de pip tradicional | Mismo resultado, instalación/resolución de dependencias más rápida |

### Capa 2 — Comunicación PC ↔ Microcontroladores
| Decisión | Valor | Justificación |
|---|---|---|
| Arquitectura | **STM32 como puente único** (PC↔STM32↔ESP32s vía UART) | Se evaluó micro-ROS también en ESP32 (WiFi directo a PC, viable técnicamente — existe componente oficial micro-ROS para ESP-IDF) — descartado: movimiento/parada de emergencia son capa reactiva, no pueden depender de WiFi (riesgo real en demo con auditorio congestionado) |
| micro-ROS | Se mantiene en STM32F411 (USB-CDC), ya validado físicamente | Confirmado soporte oficial para Jazzy |
| Protocolo UART STM32↔ESP32 | **Trama binaria fija + CRC8** (reemplaza texto plano `"VL:...,VR:...\n"`) | Más eficiente de parsear, detecta corrupción, sigue siendo depurable (logs de valores ya decodificados). Especificación completa a definir en Fase 2 de la ruta de implementación, coordinada con Sergio (ESP32 Movilidad) y Linda (ESP32 Médica) |
| Botón físico de emergencia | Conectado como **interrupción directa al STM32** (no pasa por la trama UART normal) — el STM32, al recibir la interrupción, actualiza inmediatamente un valor/estado que se propaga a ROS2 (ej. tópico o campo de estado de alta prioridad) para que el PC (agente/BT/HMI) se entere del cambio de estado sin depender del ciclo normal de la trama | Garantiza que la parada de emergencia no compita en latencia/prioridad con el resto de los datos del protocolo binario |
| Firmware ESP32 | **PlatformIO + framework Arduino** | Balance velocidad de desarrollo/estructura de proyecto vs. ESP-IDF puro (más control pero desarrollo más lento). Implementado por Sergio/Linda sobre especificación y plantilla base entregada por Andrés |
| Firmware STM32 | STM32CubeIDE, sin cambios | Ya validado, estándar correcto para el chip. Implementado por Andrés |

### Capa 3 — Percepción
| Función | Decisión | Justificación |
|---|---|---|
| Detección de presencia | **MediaPipe Pose** (sin cambio) | Sigue siendo la mejor opción CPU-only en 2026, ya validado funcionando |
| Reconocimiento facial | **SCRFD (detección) + ArcFace (embeddings) vía ONNX Runtime**, similitud coseno | Reemplaza LBPH. Resuelve de raíz el bug de pipeline multi-usuario incompleto (agregar usuario = agregar embedding, sin reentrenar) — soporta los 2+ usuarios registrados requeridos (Módulo 1). Menos fotos necesarias (3-5 vs 200), menor sensibilidad a iluminación. Comparte runtime ONNX con VAD/wake word |
| Cámara | Cámara Dell integrada, exclusiva para percepción visual | Kinect reservado a SLAM. Ya validada informalmente en el sistema anterior (funcionó correctamente) — no es un riesgo que preocupe de momento, pero se re-confirma en Fase 1. **Plan B si no fuera suficiente:** usar el Kinect también para percepción visual, o en última instancia una webcam externa |

### Capa 4 — SLAM y Navegación
| Función | Decisión | Justificación |
|---|---|---|
| SLAM | **RTAB-Map**, actualizar a 0.21.9+ | Confirmado con paper académico 2026 sobre Jazzy — alternativas (SLAM Toolbox, Cartographer, GMapping) son LiDAR-first, no aptas para RGB-D sin conversión con costo de CPU. Versión 0.21.9 corrige bug real de sincronización `message_filters` |
| Navegación | **Nav2**, sin alternativa real mejor | Nav2 usa `BehaviorTree.CPP` internamente, pero es irrelevante para nuestra decisión de framework de BT propio — se le llama como action server externo, su árbol interno es una caja negra |
| Waypoints con nombre | **Nav2 Waypoint Follower + YAML** nombre→pose | Resuelto con herramienta nativa, no requiere código propio |

### Capa 5 — Cognición / Agencia
| Función | Decisión | Justificación |
|---|---|---|
| Framework de agencia | **Pydantic AI** (v1.0, abril 2026) | Ligero, agnóstico de proveedor/modelo, tipado fuerte (encaja con mensajes ROS2). LangGraph descartado — su fortaleza (grafos de estado complejos) es redundante porque esa complejidad ya vive en el Behavior Tree |
| Proveedor LLM | **Groq**, primario | Más rápido disponible (250-500+ tok/s), tier gratuito generoso |
| Riesgo de plataforma | Groq fue adquirida (Nvidia, inicios 2026), reducción de personal técnico, catálogo curado (~12 modelos), patrón de deprecación documentado | Mitigado por diseño: Pydantic AI agnóstico de proveedor = cambiar proveedor es config, no reescritura |
| Fallback de modelos | **3 modelos + key principal → 3 modelos + key secundaria** (técnica ya documentada del sistema anterior, se conserva) | Centralizado en una sola función con Pydantic AI en vez de código repetido por servicio |
| Plan B de proveedor | **Cerebras** (WSE-3, hasta 3,000 tok/s en algunos modelos — iguala o supera a Groq, también gratuito) | Catálogo aún más pequeño y volátil que Groq (2 modelos activos tras deprecaciones de mayo 2026) — no se usa como primario, queda documentado como fallback directo |
| Plan C de emergencia | **OpenRouter** (agregador multi-proveedor) | Red de seguridad de última instancia, añade latencia de enrutamiento propio |
| Modelo inicial | **Llama 3.3 70B Versatile** | Proveedor probado, buen soporte de español, $0.59/$0.79 por millón de tokens. Benchmarking real de alternativas (GPT-OSS, Qwen3) queda para fase de construcción |
| Framework de Behavior Tree | **py_trees + py_trees_ros** | Python nativo, mismo lenguaje que el agente (Pydantic AI) y el resto del sistema — más fácil de leer/depurar/explicar. BehaviorTree.CPP (C++) descartado por no aportar ventaja real dado que no tocamos el árbol interno de Nav2 |
| Patrón de integración agente↔BT | Agente **propone** intención (vía tool calls) → BT **ejecuta**, con ramas de mayor prioridad (emergencia, obstáculos) que pueden interrumpir sin consultar al agente | Operacionaliza la separación reactiva/deliberativa. Validado por patrón académico ROS-LLM (traducción de salida LLM a Behavior Tree) |

### Capa 6 — Conversacional / Voz
| Componente | Decisión | Justificación |
|---|---|---|
| Wake word | **openWakeWord** (reemplaza Vosk-como-wake-word de decisión previa, y a Porcupine original) | Corre sobre ONNX Runtime (comparte runtime con VAD/reconocimiento facial), más preciso que Porcupine en benchmarks propios, mínimo CPU. Porcupine descartado por límite de "1 dispositivo activo" en tier gratuito |
| Comandos offline | **Vosk, acotado exclusivamente a comandos de emergencia** ("detente", "ayuda", "emergencia") | Decisión revisada: comandos rígidos de propósito general generaban falsos positivos y quitaban flexibilidad al robot (probado en sistema anterior). Todo lo demás pasa por el agente con lenguaje libre. Alternativa a evaluar: **sherpa-onnx** (consolidaría STT+TTS+VAD+wake word bajo un solo runtime ONNX) |
| VAD | **TEN VAD** (reemplaza recomendación inicial de Silero VAD) | Mayor precisión, ~32% menos CPU que Silero, latencia de corte de habla mucho menor (crítico para naturalidad conversacional). Cobra VAD (Picovoice) descartado por ser comercial/mismo problema de licenciamiento que Porcupine |
| STT | **Groq Whisper large-v3-turbo**, sin cambio | Confirmado como opción cloud más rápida en 2026 (~216x tiempo real, más barato que alternativas) |
| TTS | **Azure `es-PE-CamilaNeural`** (primario, probado) + **Kokoro TTS** (candidato a validar) | Kokoro: 82M parámetros, Apache 2.0, corre 100% local en CPU, soporta español. Se evalúa únicamente como alternativa a probar en el benchmark de TTS (calidad/latencia en el i3) — **no** se busca independencia de red con esta prueba: el robot es dependiente de conexión a internet para su operación conversacional normal (STT y LLM en la nube), y esa dependencia ya está contemplada como limitación aceptada del proyecto. Pendiente de benchmark real en el i3 (los benchmarks públicos son en hardware más potente) |
| Filler / latencia percibida | Streaming LLM→TTS frase por frase (mayor impacto real) + banco de frases cortas pre-escritas para llamadas a herramientas que toman tiempo real (navegar, dispensar, medir) | Técnica documentada como estándar de producción en agentes de voz 2026 |
| Backchanneling ("mju", "ajá") | Disparado localmente por **TEN VAD** al detectar pausa breve dentro del habla del usuario que continúa — sin pasar por el LLM | Emula la retroalimentación natural humana (ocurre *mientras* el usuario habla, no como respuesta). Cero costo de red/LLM. Inspirado en el nivel de fluidez de modos de voz nativos (ChatGPT Advanced Voice, Gemini Live), logrado sin adoptar esa arquitectura |
| Voz-a-voz nativa (evaluada y descartada) | Se investigaron alternativas de voz-a-voz nativa (OpenAI Realtime API, Gemini Live, Nova Sonic) | Descartada: sin transcripción limpia (debilita el validador ético estructural), ata a un solo proveedor (rompe la resiliencia Groq→Cerebras→OpenRouter), modelo económico distinto al diseñado, y es una caja negra que contradice el principio de transparencia/control del proyecto. Se mantiene arquitectura en cascada (STT→LLM→TTS) |

### Capa 7 — HMI
| Componente | Decisión | Justificación |
|---|---|---|
| Framework | **NiceGUI** sobre Chromium Kiosk | Construido sobre FastAPI+WebSockets (misma base que el sistema anterior), pero toda la interfaz en Python puro — unifica lenguaje con agente/BT/nodos ROS2. Usado en producción para paneles de robots (Zauberzeug) |
| Alternativa evaluada y descartada | **Godot Engine** | Integración con ROS2 es experimental/comunidad, requiere compilar módulo C++ propio dentro del engine — mismo tipo de riesgo frágil que el driver del Kinect, no apto para deadline |
| Animación de cara | Componente canvas personalizado embebido dentro de NiceGUI (springs, ondas de audio) | NiceGUI permite insertar HTML/JS personalizado cuando hace falta |
| Efectos de sonido | Reproducción de audio estándar (Web Audio API o librería de audio Python), independiente del framework elegido | No es una limitación de NiceGUI — aclarado explícitamente |
| Mapa interactivo | Renderizado de `/map` (occupancy grid de Nav2) como imagen en canvas, clic define waypoints/estación de carga | Reutiliza Waypoint Follower de Nav2 |
| Modo de mapeo | Manual/asistido (no exploración autónoma) | Ver Módulo 3 |
| Control remoto | Página adicional del mismo servidor NiceGUI, acceso vía QR (misma red WiFi que la demo) | Sin infraestructura nueva — consecuencia de decisiones ya tomadas |
| Configuración WiFi | Página en NiceGUI + teclado virtual del sistema (`onboard` o similar de Linux) | Evita reinventar teclado en pantalla |
| Botón de parada en HMI | **Descartado** | Sin pantalla táctil, impráctico — se mantiene solo el físico |

### Capa 8 — Datos
| Componente | Decisión |
|---|---|
| Motor | SQLite |
| Esquema | Extensión del esquema ya documentado (5 tablas: pacientes, medicamentos, horarios_medicacion, signos_vitales, registros_dispensacion) + tabla de notas persistentes |
| Método de creación | **Manual, paso a paso, guiado** — no generado automáticamente (ver Sección 1, principio de configuración manual) |
| Acceso desde código | Vía funciones/herramientas del agente — código de aplicación normal |

### Capa 9 — Integraciones externas
| Componente | Decisión |
|---|---|
| Escalación a humano | Bot de Telegram — ya resuelto y funcional, confirmado |
| Otras integraciones | Ninguna adicional definida |

---

## 5. ENTORNO Y FLUJO DE DESARROLLO

| Aspecto | Decisión | Justificación |
|---|---|---|
| Máquinas de trabajo | **Asus ROG Strix** (PC personal de Andrés, Ubuntu 24.04, i5 10ª gen, 16GB RAM) para desarrollo diario · **Dell Inspiron** (Ubuntu 24.04 + ROS2 Jazzy ya instalados) para integración con hardware real y la demo en sí | Mismo SO/misma versión de ROS2 en ambas máquinas — evita fricción de compatibilidad. Compilación e iteración mucho más rápida en el Asus que en el i3 del Dell |
| Principio rector | **Desarrollo nativo en ROS2 desde el día uno** — nada de desarrollo Windows-first con wrappers (lección aprendida del primer ciclo de desarrollo) | Windows queda reservado solo para piezas genuinamente multiplataforma sin fricción: firmware ESP32 (PlatformIO/Arduino) y prototipos sueltos de lógica Python sin `rclpy` |
| Sincronización | GitHub como puente entre el Asus y el Dell — mismo repo, mismo entorno en ambos lados | `git pull` en el Dell cuando se necesite probar con hardware real |
| Editor/IDE | **VSCode** (sobre PyCharm) | Proyecto multi-lenguaje (Python + C/C++ firmware + YAML + Markdown) — terreno donde VSCode tiene ventaja documentada sobre PyCharm en comparativas 2026. Remote-SSH permite editar/depurar directo en el Dell desde el Asus. Extensión PlatformIO para firmware ESP32 en el mismo editor. Coherente con el flujo de trabajo ya establecido (Copilot + VSCode) |
| Nota STM32 | Explorar extensión oficial "STM32Cube para VSCode" para consolidar también ese firmware en el mismo editor — STM32CubeIDE queda como alternativa segura si no conviene | — |
| Estructura del repositorio | **Un solo repo** (`ros2_ws/`, `firmware/` con subcarpetas por MCU, `docs/`) — no repos separados | Desarrollo mayormente secuencial liderado por Andrés; múltiples repos añadirían fricción de coordinación sin beneficio real dado el tamaño del equipo |
| Equipo de desarrollo (metáfora operativa) | Andrés (decisiones/ejecución) + Claude (planificación/arquitectura/decisiones clave) + GitHub Copilot Pro (implementación de código pesado) ≈ equivalente funcional a equipo de 3 | Desarrollo secuencial pero con coherencia total de diseño — evita el problema del sistema anterior (módulos pensados en aislamiento) |

---

## 6. RUTA DE IMPLEMENTACIÓN (fases, sin fechas — orden lógico por dependencias)

### FASE 0 — Cimientos

**Estructura del repositorio (decidida — un solo repo, 6 paquetes ROS2):**

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
├── docs/                          ← documentación modular (dividida del documento maestro)
├── scripts/
│   └── benchmarks/                ← los 4 scripts de benchmark pendientes
├── simulation/                    ← mundos/modelos Gazebo (pruebas en el Asus)
├── .env.example                   ← plantilla de variables de entorno, sin valores reales
├── .gitignore
└── README.md
```

*(Nota: `robot_perception` como paquete separado no es solo prolijidad — es la frontera de trabajo de Juan, quien solo necesita tocar esa carpeta sin fricción de coordinación con el resto.)*

**Tareas de esta fase:**
- Crear repo en GitHub + estructura de carpetas anterior (manual, paso a paso)
- `venv --system-site-packages` + `uv` en el Dell
- VSCode + Remote-SSH configurado entre el Asus y el Dell
- Esquema SQLite creado a mano (`patient.db` + tabla de notas)
- `.gitignore` para `build/`, `install/`, `log/`, y `.env`
- `.env` (credenciales reales, nunca en git) + `.env.example` (plantilla sin valores) — Groq, Azure, Telegram, Cerebras
- Convención de idioma: **código en inglés** (nombres, comentarios — estándar del ecosistema ROS2/Python) · **contenido orientado al usuario en español** (prompts del agente, textos del HMI, mensajes de Telegram)

**Salida:** primer nodo ROS2 real corriendo desde cualquiera de las dos máquinas (Asus o Dell).

### FASE 1 — Todo lo que NO depende del robot físico ensamblado (arranca de inmediato, en paralelo al ensamblaje)
- **Percepción** con cámara Dell real: detección de presencia (MediaPipe Pose), reconocimiento facial (SCRFD+ArcFace+ONNX) — valida aquí la calidad/FOV real de la cámara
- **Voz** con micrófono real: los 4 benchmarks pendientes (wake word, VAD, TTS, STT offline) + pipeline completo integrado
- **Agente (Pydantic AI):** loop de conversación con Groq + fallback 3+3, herramientas implementadas como **stubs** primero, validador ético estructural
- **Behavior Tree (py_trees):** árbol raíz con jerarquía de prioridad, acciones como stubs al inicio
- **HMI (NiceGUI):** 16 estados + dashboard + mapa (datos de prueba) + control remoto QR — conectado a estados simulados primero, ROS2 real después
- **Base de datos:** CRUD real contra el esquema, datos de prueba
- **Telegram:** notificación real, probada de una vez (pieza más autocontenida)
- **Simulación en HP (Gazebo):** Nav2 + RTAB-Map contra robot simulado, valida lógica de navegación/búsqueda sin esperar ensamblaje físico
- **Regla:** cada herramienta/acción se prueba aislada antes de conectarla al sistema completo

**Salida:** sistema completo funcionando "en el aire" (conversando, mostrando cara, decidiendo), listo para conectar a hardware real.

### FASE 2 — Protocolo de comunicación (en paralelo a Fase 1, coordinado con Sergio y Linda)
- Especificación completa de la trama binaria+CRC8 (velocidad, sensores, dispensación, signos vitales, parada de emergencia)
- Entrega de especificación + plantilla base en C (Arduino/PlatformIO) a Sergio y Linda
- Andrés implementa el lado STM32 (puente) y valida contra la especificación

**Salida:** protocolo cerrado en papel, firmwares de Sergio/Linda avanzando en paralelo sin bloquear ni bloquearse con la Fase 1.

### FASE 3 — Integración progresiva (dependiente de hitos de hardware, en el orden en que vayan llegando)
- **PCB de movilidad lista (Sergio)** → `navigate_to`/`find_user` reales, UART Movilidad end-to-end, `esp32_bridge_node` real
- **Pastillero con ajustes terminados (Linda)** → `dispense_medication` real, UART Médica end-to-end
- **Carcasa completamente armada (post-procesado)** → montaje definitivo Dell/Kinect/cámara/parlante, validación de cableado, **re-validar benchmarks de voz dentro de la carcasa cerrada** (la acústica cambia respecto al Dell suelto en escritorio)

**Salida:** robot físico completo respondiendo a todas las herramientas del agente con hardware real, no stubs.

### FASE 4 — Validación de sistema completo
- UART STM32↔ambos ESP32 bajo carga real (movimiento + dispensación simultáneos si aplica)
- Mapeo real del espacio de la demo (modo manual/asistido)
- Flujo completo del Módulo 3 (búsqueda del usuario) de punta a punta con robot real
- Pruebas de estabilidad: batería, temperatura, comportamiento ante fallos de red (con y sin hotspot)

### FASE 5 — Preparación específica de la demo
- Guion de los 15 minutos (movimiento en vivo, dispensación pedida en el momento, consulta real a BD, momento proactivo del agente)
- Grabación de clip(s) de video para autonomía no demostrable en vivo
- Ensayo en condiciones similares al auditorio (hotspot, ruido ambiente)
- Ensayos repetidos hasta que se sienta natural, no ensayado

### FASE 6 — Documentación y cierre
- División del documento maestro en archivos modulares definitivos
- Actualización de `DECISIONES_TECNICAS.md` (formato ADR) con las decisiones de esta reformulación
- Registro de resultados finales de los 4 benchmarks con números reales

---

## 7. BENCHMARKS PENDIENTES

Todos deben medirse en el hardware real (Dell Inspiron, micrófono real), no con cifras de benchmarks públicos ajenos. Ejecutar en Fase 1; **re-validar wake word/VAD dentro de la carcasa cerrada en Fase 3** (la acústica cambia).

| # | Benchmark | Opciones a comparar | Métrica clave |
|---|---|---|---|
| 1 | Wake word | Porcupine vs openWakeWord | Precisión (falsos positivos/negativos) con voz real y nombre del robot, consumo CPU |
| 2 | VAD | WebRTC VAD vs Silero VAD vs TEN VAD vs Cobra VAD | Latencia de corte de habla, precisión con ruido ambiente real, consumo CPU |
| 3 | TTS | Azure `es-PE-CamilaNeural` vs Kokoro | Naturalidad de voz en español, latencia real en el i3, viabilidad de correr 100% local |
| 4 | STT offline (emergencia) | Vosk vs sherpa-onnx | Precisión con frases de emergencia en español, latencia, consumo |

---

## 8. DECISIONES ABIERTAS / PENDIENTES

- **Nombre del robot** — sin decidir.
- **Ubicación del nombre** — HMI vs. carcasa física (pendiente de decisión, probablemente carcasa).
- **Especificación completa de la trama binaria+CRC8** — a definir en Fase 2.
- **Diseño concreto del árbol raíz de py_trees** (ramas exactas, orden de prioridad detallado) — a resolver en Fase 1.
- **Traducción de lenguaje natural → `medication_id`** en la herramienta `dispense_medication` — a resolver con contexto de `list_medications` en el prompt del agente.
- Los 4 benchmarks de la Sección 7.

---

*Fin del documento maestro v1. Pendiente de división en documentos específicos por módulo/capa según formato de documentación anterior del proyecto.*
