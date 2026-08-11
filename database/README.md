# MEADLEASE — BASE DE DATOS

> Motor: SQLite. Esquema creado a mano (DB Browser for SQLite), no generado automáticamente — ver principio de "tareas de configuración de una sola vez" en `docs/PROYECTO_GENERAL.md`.
> Este archivo documenta el razonamiento de cada tabla en formato ADR: por qué existe cada columna, no solo qué contiene. Las decisiones de más alto nivel (terminología `usuarios`, diseño de `horarios_medicacion`) están además registradas como ADR-030 y ADR-031 en `docs/DECISIONES_TECNICAS.md`.

---

## Tabla `usuarios`

```sql
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    edad INTEGER,
    genero TEXT,
    chat_id_telegram TEXT,
    carpeta_embeddings TEXT,
    contexto_relevante TEXT,
    fecha_registro TEXT DEFAULT CURRENT_TIMESTAMP,
    activo INTEGER DEFAULT 1
);
```

- **Estado:** Aceptada
- **Por qué `usuarios` y no `pacientes`:** Koda es un robot doméstico de acompañamiento, no un dispositivo médico clínico — "pacientes" implica un contexto clínico que el proyecto explícitamente no busca cumplir (ver ADR-030 en `docs/DECISIONES_TECNICAS.md`).
- **`carpeta_embeddings` (no los embeddings faciales en la BD):** los embeddings faciales se guardan como archivos en una carpeta separada por usuario (Opción B), dominio del módulo de percepción (Juan) — la BD solo guarda la **ruta** a esa carpeta, no los vectores/imágenes en sí. Evita mezclar datos biométricos binarios con el resto del esquema relacional y mantiene la frontera de trabajo de Juan intacta (ver `docs/ROBOT_PERCEPCION.md`).
- **Orden de creación `id` → carpeta:** el registro en `usuarios` se crea primero (obteniendo el `id` autoincremental), y la carpeta de embeddings se nombra después usando ese mismo `id` — evita tener que inventar o coordinar un identificador externo antes de que la fila exista.
- **`contexto_relevante` vs. tabla `notas` (distinción de propósito):**
  - `contexto_relevante` (columna única, se sobrescribe): perfil de personalidad/gustos del usuario (comida favorita, equipo de fútbol, etc.) — no es un historial cronológico, es el "estado actual" de lo que el agente sabe sobre quién es el usuario. Alimentado por la tool `update_user_context(usuario_id, text)`.
  - Tabla `notas` (histórico, se acumula): bitácora situacional/médica puntual ("durmió mal", "se golpeó la cabeza", "vomitó 2 veces"), timestamped, historial completo. Alimentado por la tool `save_note(usuario_id, text)`.
  - Ambas son tools separadas del agente (ver `docs/ROBOT_COGNICION.md`) precisamente porque resuelven necesidades distintas: una es memoria de identidad, la otra es registro de eventos.
- **`chat_id_telegram`:** por usuario, ya que `notify_emergency_contact` puede necesitar notificar al cuidador asociado a un usuario específico en un hogar con 2+ usuarios registrados.
- **`activo`:** soft-delete — un usuario dado de baja no se borra (conserva historial de dispensaciones/signos vitales), simplemente deja de aparecer en flujos activos (reconocimiento facial, próximas dosis).

---

## Tabla `medicamentos`

```sql
CREATE TABLE medicamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    slot_id INTEGER NOT NULL UNIQUE,
    cantidad_actual INTEGER NOT NULL DEFAULT 0,
    cantidad_maxima INTEGER NOT NULL,
    descripcion TEXT,
    activo INTEGER DEFAULT 1
);
-- slot_id: rango válido (actualmente 1-6, según capacidad del carrusel de Linda)
-- validado en código, NO como CHECK en SQL, porque el número de slots puede cambiar
-- con el diseño mecánico
```

- **Estado:** Aceptada
- **Catálogo ligado al inventario físico, no al usuario:** `medicamentos` representa lo que está físicamente cargado en el carrusel (un `slot_id` = un compartimento físico), no una relación por usuario. La relación real usuario↔medicamento (quién toma qué, cuándo) vive en `horarios_medicacion`, una relación N-a-N genuina.
- **`slot_id` compartido entre usuarios:** si dos usuarios registrados toman el mismo medicamento, apunta al mismo `slot_id`/fila en `medicamentos` — no se duplica el medicamento por usuario, evitando inconsistencias de inventario (dos filas para la misma pastilla física).
- **`slot_id` validado en código, no `CHECK` en SQL:** el número de slots del carrusel (actualmente 1-6) es una decisión de diseño mecánico que puede cambiar; un `CHECK` fijo en el esquema requeriría migración si cambia la capacidad física, mientras que la validación en código es un cambio de una constante.
- **`cantidad_maxima` (solo para UI):** alimenta la barra de nivel del compartimento en el HMI (ver `docs/ROBOT_HMI.md`) — no tiene lógica de negocio adicional (no bloquea dispensación, no genera alertas por sí sola). Se recalcula al alza si una recarga real supera el valor guardado (ej. el usuario cargó más pastillas de las que el sistema tenía registradas como máximo), sin ninguna otra regla.
- **`descripcion` (opcional y manual):** texto libre, capturado manualmente al registrar el medicamento. **Explícitamente no se genera automáticamente vía consulta web** — hacerlo introduciría lenguaje clínico no curado en la base de datos, que luego el agente podría repetir en conversación y comprometer al validador ético estructural (nunca diagnostica/prescribe, ver `docs/ROBOT_COGNICION.md`).

---

## Tabla `horarios_medicacion`

```sql
CREATE TABLE horarios_medicacion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
    medicamento_id INTEGER NOT NULL REFERENCES medicamentos(id),
    tipo_horario TEXT NOT NULL, -- 'diario' | 'dias_semana' | 'intervalo'
    hora TEXT,                  -- HH:MM, usado en 'diario' y 'dias_semana'
    dias_semana TEXT,           -- CSV ("1,3,5"), solo modo 'dias_semana', L=1..D=7
    intervalo_horas INTEGER,    -- solo modo 'intervalo'
    hora_inicio TEXT,           -- solo modo 'intervalo'
    activo INTEGER DEFAULT 1
);
```

- **Estado:** Aceptada (ver también ADR-031 en `docs/DECISIONES_TECNICAS.md`)
- **Relación N-a-N real usuario↔medicamento:** esta tabla, no `medicamentos`, es donde vive la asociación real de quién toma qué y cuándo — permite que el mismo medicamento tenga horarios distintos para usuarios distintos, y que un usuario tenga varios medicamentos con distintos patrones.
- **3 modos de horario, una sola tabla con columna discriminadora `tipo_horario`:**
  1. **`diario`** — misma hora todos los días. Usa `hora`. UX en HMI: casilla "todos los días".
  2. **`dias_semana`** — días específicos de la semana, misma hora. Usa `hora` + `dias_semana` (CSV, L=1..D=7). UX en HMI: selector de días tipo L-M-M-J-V-S-D.
  3. **`intervalo`** — cada X horas desde una hora de inicio. Usa `intervalo_horas` + `hora_inicio`. UX en HMI: modo "cada X horas desde...".
  - Alternativa de una tabla separada por modo descartada — ver justificación en ADR-031 (complica el cálculo de "próxima dosis" y duplica la relación N-a-N en 3 tablas).
- **Columnas nulas según el modo:** es intencional que `hora`, `dias_semana`, `intervalo_horas`, `hora_inicio` sean todas opcionales — cada fila solo llena las columnas relevantes a su `tipo_horario`, el resto queda `NULL`. La validez de la combinación (ej. que `intervalo` tenga `intervalo_horas` no nulo) se valida en código, mismo principio que `slot_id` en `medicamentos`.
- **Un patrón vigente a la vez:** un usuario+medicamento tiene un solo horario activo (`activo = 1`) en un momento dado — cambiar el patrón de horario significa desactivar el anterior y crear uno nuevo, no editar campos sueltos de una fila compartida entre modos.
- **Cálculo de "próxima dosis":** resuelto en código (tool `get_next_dose`, ver `docs/ROBOT_COGNICION.md`) según el valor de `tipo_horario` — nunca delegado al LLM, para evitar alucinaciones temporales.

---

## Información faltante / pendiente de revisión

- **Tablas `signos_vitales` y `registros_dispensacion`:** aún no detalladas en este documento — el esquema completo mencionado en `docs/PROYECTO_GENERAL.md` incluye 5 tablas + notas; falta documentar aquí las columnas de estas dos y de la tabla `notas`.
- **Umbral/formato exacto de `dias_semana`:** se define como CSV de enteros 1-7, pero no hay validación documentada de duplicados o valores fuera de rango (ej. `"1,1,9"`).
- **Política de `activo = 0` en `horarios_medicacion`:** no se especifica si se conserva indefinidamente como historial o si hay algún proceso de limpieza.
