# MEADLEASE — ROADMAP DE IMPLEMENTACIÓN

## FASE 0 — Cimientos

- [x] Crear repo en GitHub + estructura de carpetas (manual, paso a paso) — ver árbol completo en `PROYECTO_GENERAL.md`
- [ ] `venv --system-site-packages` + `uv` en el Asus (desarrollo) y en el Dell (pruebas de hardware real)
- [ ] Esquema SQLite creado a mano (`usuarios.db` + tabla de notas)
- [ ] `.gitignore` para `build/`, `install/`, `log/`, y `.env`
- [ ] `.env` (credenciales reales) + `.env.example` (plantilla) — Groq, Azure, Telegram, Cerebras
- [ ] Convención de idioma aplicada (código en inglés, contenido de usuario en español)

**Salida esperada:** primer nodo ROS2 real corriendo desde cualquiera de las dos máquinas (Asus o Dell).

---

## FASE 1 — Todo lo que NO depende del robot físico ensamblado (arranca de inmediato, en paralelo al ensamblaje)

- [ ] **Percepción** con cámara Dell real: detección de presencia (MediaPipe Pose), reconocimiento facial (SCRFD+ArcFace+ONNX) — validar aquí calidad/FOV real de la cámara
- [ ] **Voz** con micrófono real: los 4 benchmarks pendientes (wake word, VAD, TTS, STT offline) + pipeline completo integrado
- [ ] **Agente (Pydantic AI):** loop de conversación con Groq + fallback 3+3, herramientas implementadas como **stubs** primero, validador ético estructural
- [ ] **Behavior Tree (py_trees):** árbol raíz con jerarquía de prioridad, acciones como stubs al inicio
- [ ] **HMI (NiceGUI):** estados + dashboard + mapa (datos de prueba) + control remoto QR — conectado a estados simulados primero, ROS2 real después
- [ ] **Base de datos:** CRUD real contra el esquema, datos de prueba
- [ ] **Telegram:** notificación real, probada de una vez (pieza más autocontenida)
- [ ] **Simulación en Asus (Gazebo):** Nav2 + RTAB-Map contra robot simulado, valida lógica de navegación/búsqueda sin esperar ensamblaje físico
- [ ] **Regla transversal:** cada herramienta/acción se prueba aislada antes de conectarla al sistema completo

**Salida esperada:** sistema completo funcionando "en el aire" (conversando, mostrando cara, decidiendo), listo para conectar a hardware real.

---

## FASE 2 — Protocolo de comunicación (en paralelo a Fase 1, coordinado con Sergio y Linda)

- [ ] Especificación completa de la trama binaria+CRC8 (velocidad, sensores, dispensación, signos vitales, parada de emergencia)
- [ ] Entrega de especificación + plantilla base en C (Arduino/PlatformIO) a Sergio y Linda
- [ ] Andrés implementa el lado STM32 (puente) y valida contra la especificación

**Salida esperada:** protocolo cerrado en papel, firmwares de Sergio/Linda avanzando en paralelo sin bloquear ni bloquearse con la Fase 1.

---

## FASE 3 — Integración progresiva (dependiente de hitos de hardware, en el orden en que vayan llegando)

- [ ] **PCB de movilidad lista (Sergio)** → `navigate_to`/`find_user` reales, UART Movilidad end-to-end, `esp32_bridge_node` real
- [ ] **Pastillero con ajustes terminados (Linda)** → `dispense_medication` real, UART Médica end-to-end
- [ ] **Carcasa completamente armada (post-procesado)** → montaje definitivo Dell/Kinect/cámara/parlante, validación de cableado, **re-validar benchmarks de voz dentro de la carcasa cerrada** (la acústica cambia respecto al Dell suelto en escritorio)

**Salida esperada:** robot físico completo respondiendo a todas las herramientas del agente con hardware real, no stubs.

---

## FASE 4 — Validación de sistema completo

- [ ] UART STM32↔ambos ESP32 bajo carga real (movimiento + dispensación simultáneos si aplica)
- [ ] Mapeo real del espacio de la demo (modo manual/asistido)
- [ ] Flujo completo del Módulo 3 (búsqueda del usuario) de punta a punta con robot real
- [ ] Pruebas de estabilidad: batería, temperatura, comportamiento ante fallos de red (con y sin hotspot)

---

## FASE 5 — Preparación específica de la demo

- [ ] Guion de los 15 minutos (movimiento en vivo, dispensación pedida en el momento, consulta real a BD, momento proactivo del agente)
- [ ] Grabación de clip(s) de video para autonomía no demostrable en vivo
- [ ] Ensayo en condiciones similares al auditorio (hotspot, ruido ambiente)
- [ ] Ensayos repetidos hasta que se sienta natural, no ensayado

---

## FASE 6 — Documentación y cierre

- [ ] División del documento maestro en archivos modulares definitivos (este proceso, en curso)
- [ ] Actualización de `DECISIONES_TECNICAS.md` (formato ADR) con las decisiones de esta reformulación
- [ ] Registro de resultados finales de los 4 benchmarks con números reales

---

## Información faltante / pendiente de revisión

- **Fechas concretas por fase:** el documento maestro deja explícito que es "sin fechas — orden lógico por dependencias". Falta desglosar el rango 6-ago-2026 → 1-nov-2026 en hitos semanales/quincenales por fase.
- **Criterios de "hecho" (Definition of Done) por fase:** no están definidos más allá de la "salida esperada" general de cada fase.
- **Dependencias cruzadas explícitas** entre tareas de Fase 1 (ej. ¿el HMI puede avanzar sin que el agente tenga tools reales? ¿la simulación Gazebo bloquea algo de Fase 3?) — hoy están listadas como paralelas pero sin diagrama de dependencias.
- **Responsable por tarea dentro de cada fase** (más allá de lo ya asignado a Sergio/Linda en Fase 2 y 3) — varias tareas de Fase 0/1/4/5/6 no tienen dueño explícito distinto de "Andrés" por defecto.
