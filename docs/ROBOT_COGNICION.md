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
| Plan B de proveedor | **Cerebras** (WSE-3, hasta 3,000 tok/s en algunos modelos) | Catálogo aún más pequeño y volátil que Groq (2 modelos activos tras deprecaciones de mayo 2026) — no se usa como primario, queda documentado como fallback directo |
| Plan C de emergencia | **OpenRouter** (agregador multi-proveedor) | Red de seguridad de última instancia, añade latencia de enrutamiento propio |
| Modelo inicial | **Llama 3.3 70B Versatile** | Proveedor probado, buen soporte de español, $0.59/$0.79 por millón de tokens. Benchmarking real de alternativas (GPT-OSS, Qwen3) queda para fase de construcción |
| Framework de Behavior Tree | **py_trees + py_trees_ros** | Python nativo, mismo lenguaje que el agente (Pydantic AI) y el resto del sistema — más fácil de leer/depurar/explicar. BehaviorTree.CPP (C++) descartado por no aportar ventaja real dado que no tocamos el árbol interno de Nav2 |
| Patrón de integración agente↔BT | Agente **propone** intención (vía tool calls) → BT **ejecuta**, con ramas de mayor prioridad (emergencia, obstáculos) que pueden interrumpir sin consultar al agente | Operacionaliza la separación reactiva/deliberativa. Validado por patrón académico ROS-LLM (traducción de salida LLM a Behavior Tree) |

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
| `get_last_vitals(patient_id)` | Consulta última medición guardada |
| `get_next_dose(patient_id)` | Próxima dosis y tiempo restante (cálculo en código, no en LLM — evita alucinaciones temporales) |
| `get_dose_history(patient_id, limit)` | Historial de dispensaciones |
| `save_note(patient_id, text)` | Guarda nota relevante mencionada en conversación |
| `notify_emergency_contact(reason)` | Notificación real vía Telegram al cuidador/usuario. **No detiene el robot** |

### Demostrativas (opcionales, no afectan funcionalidad núcleo)

| Herramienta | Complejidad | Nota |
|---|---|---|
| `approach_person()` | Baja | Reutiliza comportamiento APPROACHING ya construido |
| `turn_in_place(degrees, direction)` | Muy baja | Rotación pura vía odometría |
| `extend_vitals_arm()` | Trivial | Aísla movimiento del servo MG996R ya existente |
| `follow_person(duration_s)` | **Alta** | La más costosa — última prioridad |
| `greet()` | Baja | Combinación: frase + expresión facial amigable + ligero movimiento del brazo de signos vitales (el robot no tiene brazo/cuello motorizado dedicado a saludar) |

**Comportamientos compuestos (combinan herramientas atómicas, no son herramientas nuevas):** `spin_and_greet` (turn_in_place + greet, útil para arranque de demo), mostrar compartimentos de medicamentos en pantalla al usar `list_medications`.

**Nota de diseño — traducción de lenguaje natural a `medication_id`:** `dispense_medication` recibe un `medication_id`, no el nombre hablado — la traducción de lenguaje natural ("la de la presión") al ID correcto la resuelve el LLM con el contexto de `list_medications` en su prompt. **Validación obligatoria:** el `medication_id` (y en general cualquier valor fijo proveniente de la base de datos — IDs de medicamento, de paciente, de waypoint, etc.) que el LLM incluya en una llamada a herramienta debe validarse contra la base de datos antes de ejecutar la acción, en vez de confiar en que el LLM lo generó correctamente — mismo principio del validador ético estructural, aplicado aquí como validación estructural de datos.

---

## Información faltante / pendiente de revisión

- **Diseño concreto del árbol raíz de py_trees** (ramas exactas, orden de prioridad detallado): marcado como pendiente explícito, a resolver en Fase 1.
- **Resolución final de la traducción NL → `medication_id`**: el principio está definido, falta el diseño concreto del prompt/contexto y de la validación.
- **Caso de dos usuarios detectados simultáneamente** (ver también `ROBOT_PERCEPCION.md`): no se define a cuál atiende el agente ni cómo se resuelve el conflicto de identidad.
- **Especificación exacta del validador ético estructural**: se define su propósito (nunca diagnosticar/prescribir) pero no las reglas/patrones concretos que debe rechazar, ni el mensaje de fallback cuando bloquea una respuesta.
- **Rangos de referencia de signos vitales** que disparan la reacción visual "fuera de rango" — no están enumerados (bpm, SpO2, temperatura).
- **Ubicación final del Módulo 5 y Capa 9**: se incluyeron aquí por no tener archivo dedicado en la separación solicitada — confirmar si esta ubicación es correcta o si merecen archivo propio.
- **Detalle de `save_note`**: no se especifica límite de longitud, ni cómo se recuperan las notas en conversación futura (más allá de la exclusión explícita de "recuperación proactiva entre sesiones").
