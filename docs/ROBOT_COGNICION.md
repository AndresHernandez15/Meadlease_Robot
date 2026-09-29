# MEADLEASE — COGNICIÓN Y AGENCIA

> **Corresponde a:** `robot_cognition`

---

## Objetivos funcionales (Módulo 2 — Cognición / Agencia)

- **Arquitectura híbrida:** capa reactiva (Behavior Tree, siempre activa, sin LLM) + capa deliberativa (agente con LLM, decide metas e inicia comportamiento). El agente **propone** intenciones; el árbol **dispone y protege** (ejecuta, con reflejos de mayor prioridad que pueden interrumpir).
- **Gestión de metas propias:** basada en horarios de medicación/mediciones, extendiendo esquema de BD existente.
- **Iniciativa proactiva:** nivel **moderado** — saluda/comenta espontáneamente al reconocer presencia tras ausencia, más 3 disparadores: (1) horario médico próximo/vencido, (2) valor de signos vitales fuera de rango, (3) saludo al detectar presencia.
- **Personalidad definida:** base calmada y profesional (tipo cuidador/enfermero), con humor ligero ocasional y curiosidad genuina (hace preguntas propias). Nunca payasesco ni frío.
- **Memoria:** de sesión (contexto conversacional, turnos deslizantes) + registro estructurado en BD para datos importantes (mediciones, dispensaciones, notas puntuales vía herramienta `save_note`). Recuperación proactiva de memoria entre sesiones distintas: **fuera de alcance por ahora** (bonus post-defensa).
- **Priorización de tareas en conflicto:** jerarquía fija en el Behavior Tree (emergencia > tarea médica en curso > conversación > reposo), sin arbitraje vía LLM.
- **Adaptación de urgencia:** cambio de tono/color HMI según nivel de prioridad del evento.
- **Límites éticos:** capa de validación **estructural y dura** sobre la salida del agente (nunca diagnostica, nunca prescribe, sólo da recomendaciones y deriva a supervisión humana) — implementada como validator de Pydantic AI, no como instrucción de prompt únicamente.

## Objetivos funcionales (Módulo 5 — Salud y Cuidado Médico)

**5A — Dispensación:** programada y bajo demanda, verificación de identidad previa (Módulo 1), confirmación real de entrega, registro y trazabilidad completa. Manejo de excepciones acotado a casos realistas de demo (usuario no reconocido, fallo de caída de pastilla) — sin manejo exhaustivo de fallos mecánicos poco probables.

**5B — Signos vitales:** medición bajo demanda y programada, registro histórico **con vista de tendencias en el tiempo** (útil para cuidador/médico), reacción visible (tono/color) ante valores fuera de rango, sin lógica médica de interpretación sofisticada.

**5C — Emergencias:** activación por botón físico (hardware, máxima prioridad, no cancelable por voz) y por comando de voz offline — ambas esenciales. Ambas vías realizan **exclusivamente** una parada de emergencia: frenar motores/movimiento y quedar a la espera de reanudación explícita — no envían notificaciones ni ejecutan ninguna otra acción. **Detección autónoma de anomalías (sin que nadie la pida): fuera de alcance.**

**Distinción importante — parada de emergencia vs. `notify_emergency_contact`:** son dos mecanismos independientes que no se disparan mutuamente. La parada de emergencia (botón físico o comando de voz offline) **solo** detiene el robot. `notify_emergency_contact` **solo** envía un aviso (Telegram) al cuidador/usuario — por ejemplo cuando no se encuentra al usuario y hay una toma pendiente, o cuando el usuario lo pide explícitamente — y **en ningún caso detiene el funcionamiento del robot**.

**Reanudación tras parada de emergencia:** se acepta cualquiera de dos vías equivalentes — un segundo press del mismo botón físico, o el comando de voz offline "reanudar" (mismo canal Vosk que los comandos de emergencia). Cualquiera de las dos libera el reflejo de parada en el Behavior Tree y permite retomar la actividad previa.

## Decisiones técnicas (Capa 5)

| Función | Decisión | Justificación |
|---|---|---|
| Framework de agencia | **Pydantic AI** (v1.0, abril 2026) | Ligero, agnóstico de proveedor/modelo, tipado fuerte (encaja con mensajes ROS2). LangGraph descartado — su fortaleza (grafos de estado complejos) es redundante porque esa complejidad ya vive en el Behavior Tree |
| Proveedor LLM | **Groq**, primario | Más rápido disponible (250-500+ tok/s), tier gratuito generoso |
| Riesgo de plataforma | Groq fue adquirida (Nvidia, inicios 2026), reducción de personal técnico, catálogo curado (~12 modelos), patrón de deprecación documentado | Mitigado por diseño: Pydantic AI agnóstico de proveedor = cambiar proveedor es config, no reescritura |
| Fallback de modelos | **3 modelos + key principal → 3 modelos + key secundaria** (técnica ya documentada del sistema anterior, se conserva) | Centralizado en una sola función con Pydantic AI en vez de código repetido por servicio |
| Orden de fallback (3 modelos, misma key) | **1. `openai/gpt-oss-120b`** → **2. `openai/gpt-oss-20b`** → **3. `qwen/qwen3.8-27b`** | Benchmark real hecho en Fase 1 (`scripts/benchmarks/llm/`) — `Llama 3.3 70B Versatile` (decisión original) ya no existe en el catálogo de Groq. Detalle completo y parámetros por modelo (`max_completion_tokens`, `reasoning_effort`, `temperature`/`top_p`) en `DECISIONES_TECNICAS.md` ADR-013 |
| Framework de Behavior Tree | **py_trees + py_trees_ros** | Python nativo, mismo lenguaje que el agente (Pydantic AI) y el resto del sistema — más fácil de leer/depurar/explicar. BehaviorTree.CPP (C++) descartado por no aportar ventaja real dado que no tocamos el árbol interno de Nav2 |
| Patrón de integración agente↔BT | Agente **propone** intención (vía tool calls) → BT **ejecuta**, con ramas de mayor prioridad (emergencia, obstáculos) que pueden interrumpir sin consultar al agente | Operacionaliza la separación reactiva/deliberativa. Validado por patrón académico ROS-LLM (traducción de salida LLM a Behavior Tree) |

**Nota técnica — formato Harmony (gpt-oss):** los modelos `openai/gpt-oss-120b` y `openai/gpt-oss-20b` (candidatos principales de la cadena de fallback tras el benchmark en `scripts/benchmarks/llm/`) usan internamente el formato de respuesta "Harmony" de OpenAI, que define roles especiales (`developer` en vez de `system` para instrucciones, canales de razonamiento separados, etc.). **Groq maneja esta traducción automáticamente en su API** — el cliente solo manda mensajes con los roles estándar (`system`/`user`/`assistant`), igual que con cualquier otro modelo. No hay que implementar el formato Harmony a mano en `robot_cognition`.

## Capa 9 — Integraciones externas

| Componente | Decisión |
|---|---|
| Escalación a humano | Bot de Telegram — ya resuelto y funcional, confirmado |
| Otras integraciones | Ninguna adicional definida |

## Herramientas del agente (Pydantic AI)

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
| `get_last_vitals(usuario_id)` | Consulta última medición guardada |
| `get_next_dose(usuario_id)` | Próxima dosis y tiempo restante (cálculo en código, no en LLM — evita alucinaciones temporales) |
| `get_dose_history(usuario_id, limit)` | Historial de dispensaciones |
| `save_note(usuario_id, text)` | Bitácora situacional/médica puntual ("durmió mal", "se golpeó la cabeza") → tabla `notas`, timestamped, historial completo |
| `update_user_context(usuario_id, text)` | Perfil de personalidad/gustos del usuario (comida favorita, equipo de fútbol, etc.) → campo único `usuarios.contexto_relevante`. No es un historial cronológico: el agente recibe el `contexto_relevante` actual como parte del contexto de la tool call y decide si lo mantiene, lo amplía o lo reemplaza; la tool solo sobrescribe el campo con el texto final que el LLM produce, sin concatenar en código |
| `notify_emergency_contact(reason)` | Notificación real vía Telegram al cuidador/usuario. **No detiene el robot** |

### Demostrativas (opcionales, no afectan funcionalidad núcleo)

| Herramienta | Complejidad | Nota |
|---|---|---|
| `approach_person()` | Baja | Reutiliza comportamiento APPROACHING ya construido |
| `turn_in_place(degrees, direction)` | Muy baja | Rotación pura vía odometría |
| `extend_vitals_arm()` | Trivial | Aísla movimiento del servo MG996R ya existente |
| `follow_person(duration_s)` | **Alta** | La más costosa — última prioridad |
| `greet()` | Baja | Combinación: frase + expresión facial amigable + ligero movimiento del brazo de signos vitales (el robot no tiene brazo/cuello motorizado dedicado a saludar) |
| `describe_surroundings(question)` | **Exploratoria** | Responde preguntas tipo "¿cómo estoy vestido?" o "¿qué puedes ver?" tomando una foto con la cámara y usando un modelo de visión (candidato: Qwen VL vía Groq, mismo proveedor que el resto de la cadena de fallback). Depende de un benchmark aparte (calidad de descripción, latencia) todavía no hecho — ver nota abajo |

**Comportamientos compuestos (combinan herramientas atómicas, no son herramientas nuevas):** `spin_and_greet` (turn_in_place + greet, útil para arranque de demo), mostrar compartimentos de medicamentos en pantalla al usar `list_medications`. Si la feature bonus de localización de fuente sonora se construye (ver `ROBOT_VOZ.md` y ADR-033), `turn_in_place` también podría reutilizarse para orientar al robot hacia el hablante — no se crearía una tool nueva para eso.

**Nota de diseño — `describe_surroundings` (exploratoria, no decidida):** surge de aprovechar que Qwen ya es parte de la cadena de fallback de texto (`qwen/qwen3.8-27b`, tercer fallback — ver Decisiones técnicas) y también tiene una variante con reconocimiento de imágenes. Dos formas de implementarlo, todavía sin decidir cuál (o si directamente se descarta por alcance de prototipo):
1. **Dos pasos:** la tool toma la foto, Qwen VL la describe en texto, y ese texto se inyecta de vuelta al LLM principal (el que esté atendiendo la conversación) para que responda en su propia personalidad.
2. **Un paso:** se le pasa a Qwen VL la foto junto con la pregunta original del usuario y responde directamente, sin pasar por el LLM principal — más simple y potencialmente más rápido, pero la respuesta no pasa por la personalidad/validador ético estructural del agente principal a menos que se replique ahí también.

Pendiente: benchmark de calidad/latencia de Qwen VL antes de decidir cuál de las dos formas (o ninguna, si no alcanza el tiempo).

**Requisito de implementación — descripciones de parámetros ID en las 12 tools funcionales:** para cada parámetro que sea un ID proveniente de la base de datos (`medication_id`, `usuario_id`, nombres de waypoint en `location`, etc.), la `description` del JSON Schema que Pydantic AI genera para la tool debe indicar explícitamente **de dónde sale ese valor**, no solo su tipo de dato — ej. `medication_id: int` con descripción "debe ser un id devuelto por `list_medications`", no solo "id del medicamento". Esto le da al LLM la procedencia correcta del valor en el momento de decidir la tool call, en vez de que la infiera del texto de la conversación.

**Nota de diseño — traducción de lenguaje natural a `medication_id`:** `dispense_medication` recibe un `medication_id`, no el nombre hablado — la traducción de lenguaje natural ("la de la presión") al ID correcto la resuelve el LLM con el contexto de `list_medications` en su prompt. **Validación obligatoria:** el `medication_id` (y en general cualquier valor fijo proveniente de la base de datos — IDs de medicamento, de usuario, de waypoint, etc.) que el LLM incluya en una llamada a herramienta debe validarse contra la base de datos antes de ejecutar la acción, en vez de confiar en que el LLM lo generó correctamente — mismo principio del validador ético estructural, aplicado aquí como validación estructural de datos.

---

## Información faltante / pendiente de revisión

- **Diseño concreto del árbol raíz de py_trees** (ramas exactas, orden de prioridad detallado): marcado como pendiente explícito, a resolver en Fase 1.
- **Resolución final de la traducción NL → `medication_id`**: el principio está definido, falta el diseño concreto del prompt/contexto y de la validación.
- **Caso de dos usuarios detectados simultáneamente** (ver también `ROBOT_PERCEPCION.md`): no se define a cuál atiende el agente ni cómo se resuelve el conflicto de identidad.
- **Especificación exacta del validador ético estructural**: se define su propósito (nunca diagnosticar/prescribir) pero no las reglas/patrones concretos que debe rechazar, ni el mensaje de fallback cuando bloquea una respuesta.
- **Rangos de referencia de signos vitales** que disparan la reacción visual "fuera de rango" — no están enumerados (bpm, SpO2, temperatura).
- **Ubicación final del Módulo 5 y Capa 9**: se incluyeron aquí por no tener archivo dedicado en la separación solicitada — confirmar si esta ubicación es correcta o si merecen archivo propio.
- **Detalle de `save_note` y `update_user_context`**: el propósito de cada una ya está diferenciado (bitácora situacional/médica vs. perfil de personalidad), pero falta especificar límite de longitud de texto en ambas, y el mecanismo exacto para inyectar el `contexto_relevante` actual en el prompt de `update_user_context` antes de que el LLM decida el texto de reemplazo.
- **`describe_surroundings` (herramienta de visión vía Qwen VL)**: idea exploratoria, no decidida — depende de un benchmark aparte de calidad/latencia del modelo de visión que todavía no se ha hecho. Ver nota de diseño en la sección de herramientas demostrativas.
