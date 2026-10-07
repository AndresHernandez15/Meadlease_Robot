# MEADLEASE — COGNICIÓN Y AGENCIA

> **Paquete:** `robot_cognition`. Cubre el Módulo 2 (cognición), el Módulo 5 (salud) y las integraciones externas.

## Módulo 2 — Cognición

- **Dos capas:** un Behavior Tree siempre activo y sin LLM (reactivo) y un agente LLM que decide metas y toma la iniciativa (deliberativo). El agente propone, el árbol ejecuta y puede interrumpir (ADR-015).
- **Metas propias:** a partir de los horarios de medicación y mediciones de la BD.
- **Iniciativa moderada**, con 3 disparadores: (1) dosis próxima o vencida, (2) signo vital fuera de rango, (3) el usuario vuelve a aparecer tras una ausencia (saludo o comentario).
- **Personalidad:** calmada y profesional, como un cuidador, con algo de humor y curiosidad propia (hace preguntas). Ni payaso ni frío.
- **Memoria:** la de la sesión (turnos recientes) + datos importantes en la BD (mediciones, dispensaciones, notas con `save_note`). No recuerda conversaciones de sesiones anteriores (ADR-027).
- **Prioridades fijas en el árbol:** emergencia > tarea médica en curso > conversación > reposo. El LLM no arbitra.
- **Urgencia visible:** el tono y el color del HMI cambian según la prioridad del evento.
- **Límites éticos:** un validador de Pydantic AI revisa cada respuesta del agente: nunca diagnostica ni receta, solo recomienda y deriva a una persona. No depende solo del prompt.

## Módulo 5 — Salud

**Dispensación:** programada o a pedido, siempre tras verificar la identidad (Módulo 1), con confirmación real de entrega y registro de cada intento. Solo se manejan los fallos realistas de la demo (usuario no reconocido, la pastilla no cae).

**Signos vitales:** a pedido o programados, con historial y tendencias para el cuidador. Si un valor sale de rango cambia el tono/color, sin interpretación médica.

**Emergencias:** se activan con el botón NC, el sensor TTP223 (`HARDWARE_FIRMWARE.md`) o un comando de voz offline ("detente", "ayuda", "emergencia"). Cualquiera de ellas **solo detiene el robot** y lo deja esperando una reanudación explícita: no notifica a nadie ni hace nada más. La detección autónoma de anomalías queda fuera de alcance.

**Parada ≠ aviso al cuidador:** son mecanismos independientes. La parada solo detiene. `notify_emergency_contact` solo envía un Telegram (p. ej. si no encuentra al usuario con una dosis pendiente, o si el usuario lo pide) y nunca detiene el robot.

## Decisiones técnicas

| Qué | Decisión | ADR |
|---|---|---|
| Agente | Pydantic AI | 012 |
| LLM | Groq: `gpt-oss-120b` → `gpt-oss-20b` → `qwen3.8-27b`, con 2 keys | 013 |
| Behavior Tree | py_trees + py_trees_ros | 014 |
| Agente ↔ árbol | El agente propone (tool calls), el árbol dispone | 015 |
| Escalación a humano | Bot de Telegram (validado en el sistema anterior, por reimplementar) | — |

Los `gpt-oss` usan internamente el formato "Harmony" de OpenAI, pero Groq hace la traducción: se envían los roles normales (`system`/`user`/`assistant`) y no hay que implementar nada.

## Herramientas del agente

Solo son herramientas las acciones que el LLM decide invocar. Los reflejos de seguridad (parada, obstáculos) viven en el árbol y nunca pasan por el agente.

> Las firmas son tentativas: los parámetros exactos se fijan al implementar cada tool.

### Funcionales

| Herramienta | Qué hace |
|---|---|
| `navigate_to(location)` | Va a un waypoint con nombre (Nav2) |
| `find_user()` | Busca al usuario recorriendo waypoints (`ROBOT_MOVILIDAD.md`) |
| `return_to_base()` | Vuelve al punto de carga manual |
| `dispense_medication(medication_id)` | Verifica identidad, dispensa y devuelve el resultado |
| `list_medications()` | Lista los medicamentos cargados |
| `measure_vitals(kind)` | Mide bpm, SpO₂, temperatura o todo |
| `get_last_vitals(usuario_id)` | Última medición guardada |
| `get_next_dose(usuario_id)` | Próxima dosis y cuánto falta (calculado en código, no por el LLM) |
| `get_dose_history(usuario_id, limit)` | Historial de dispensaciones |
| `save_note(usuario_id, text)` | Agrega una nota con fecha ("durmió mal") a la bitácora |
| `update_user_context(usuario_id, text)` | Reescribe el perfil de gustos del usuario. El LLM recibe el perfil actual y devuelve la versión final; la tool solo la guarda |
| `notify_emergency_contact(reason)` | Envía un Telegram al cuidador. No detiene el robot |

### Demostrativas (opcionales)

| Herramienta | Esfuerzo | Nota |
|---|---|---|
| `approach_person()` | Bajo | Acercamiento validado en el sistema anterior, por reimplementar |
| `turn_in_place(degrees, direction)` | Muy bajo | Giro sobre su eje con odometría |
| `extend_vitals_arm()` | Trivial | Mueve solo el servo del brazo |
| `follow_person(duration_s)` | Alto | La más costosa; última prioridad |
| `greet()` | Bajo | Frase + cara amigable + un leve movimiento del brazo de signos vitales |
| `describe_surroundings(question)` | Exploratoria | Responder "¿qué ves?" con una foto y un modelo de visión (candidato: Qwen VL en Groq). Sin decidir, depende de un benchmark de calidad y latencia. Si pasa, falta definir si la descripción vuelve al LLM principal (mantiene la personalidad y el validador) o si Qwen VL responde directo |

Comportamientos compuestos (no son tools nuevas): `spin_and_greet` (giro + saludo para arrancar la demo) y mostrar los compartimentos en pantalla al usar `list_medications`. Si se construye la localización de voz (ADR-033), `turn_in_place` sirve para girar hacia quien habla.

### Reglas de implementación

- **Origen de los IDs:** en la descripción de cada parámetro que sea un ID de la BD, decir de dónde sale (p. ej. "`medication_id`: un id devuelto por `list_medications`"), para que el LLM no lo invente a partir de la conversación.
- **Validar antes de actuar:** todo ID que proponga el LLM (medicamento, usuario, waypoint) se comprueba contra la BD antes de ejecutar. Así se traduce "la de la presión" a un `medication_id` sin confiar ciegamente en el modelo.

## Pendientes

- **Reanudar tras una parada:** el botón NC devuelve la corriente al girarlo, el TTP223 reanuda con una segunda pulsación y está previsto el comando de voz "reanudar". Falta decidir qué vía libera la parada en el árbol según el origen: ¿basta con girar el botón NC o hay que confirmar? ¿"reanudar" por voz puede liberar una parada hecha con el TTP223?
- **Árbol raíz de py_trees:** ramas y orden exacto de prioridades (Fase 1).
- **Traducción de lenguaje natural a `medication_id`:** falta el diseño concreto del prompt y la validación.
- **Dos o más usuarios a la vez:** percepción reporta a todos (`ROBOT_PERCEPCION.md`); falta decidir a quién atiende el agente, por ejemplo para dispensar.
- **Validador ético:** reglas concretas y mensaje de respuesta cuando bloquea algo.
- **Rangos de referencia** de bpm, SpO₂ y temperatura para marcar "fuera de rango".
- **`save_note` y `update_user_context`:** límite de longitud y cómo se pasa el perfil actual al LLM.
- **`describe_surroundings`:** benchmark de Qwen VL.
