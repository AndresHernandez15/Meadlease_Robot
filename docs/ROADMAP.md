# MEADLEASE — ROADMAP DE IMPLEMENTACIÓN

Orden lógico por dependencias. Responsable por defecto: Andrés, salvo que se indique otro.

## FASE 0 — Cimientos

- [x] Crear repo en GitHub + estructura de carpetas (manual, paso a paso) — ver estructura planificada en `PROYECTO_GENERAL.md`
- [x] `venv --system-site-packages` + `uv` en el Asus (desarrollo) y en el Dell (pruebas de hardware real)
- [x] Esquema SQLite creado a mano (`meadlease.db` — 6 tablas incl. `notas`) + `schema.sql` exportado
- [x] `.gitignore` para `build/`, `install/`, `log/`, `.env`, bases de datos y datos personales
- [x] `.env` (credenciales reales) + `.env.example` (plantilla) — Groq, Azure, Telegram
- [x] Convención de idioma definida (código en inglés, contenido de usuario en español, identificadores de BD en español como excepción)

**Salida:** repo, entornos, base de datos y credenciales listos en ambas máquinas.

---

## FASE 1 — Todo lo que NO depende del robot físico ensamblado (en paralelo al montaje)

- [ ] Crear `ros2_ws` + primer nodo ROS2 corriendo en el Asus y en el Dell
- [ ] **Percepción** con cámara Dell real (Juan): detección de presencia (MediaPipe Pose), reconocimiento facial (SCRFD+ArcFace+ONNX) — validar aquí calidad/FOV real de la cámara
- [ ] **Voz** con micrófono real (array del Kinect): entrenar el wake word "Koda" (openWakeWord), los 4 benchmarks (`ROBOT_VOZ.md`) + pipeline completo integrado
- [ ] **(Opcional/bonus) Validar localización de fuente sonora** con el Kinect rotado a ángulos reales medidos y recalibrar la separación `D` del array — procedimiento en `scripts/benchmarks/README.md` (ADR-033)
- [x] **Benchmark de LLM (Groq):** completado en septiembre 2026 — cadena de fallback definida (`gpt-oss-120b` → `gpt-oss-20b` → `qwen3.8-27b`), ver ADR-013 y `scripts/benchmarks/llm/`
- [ ] **Agente (Pydantic AI):** loop de conversación con Groq + fallback 3+3, herramientas implementadas como **stubs** primero, validador ético estructural
- [ ] **Behavior Tree (py_trees):** árbol raíz con jerarquía de prioridad, acciones como stubs al inicio
- [ ] **Base de datos:** capa de acceso común (agente + HMI), CRUD real contra el esquema, datos de prueba (opcional: `database/seed.sql`)
- [ ] **HMI (NiceGUI):** estados + dashboard + mapa (datos de prueba) + control remoto QR + configuración WiFi vía QR/hotspot — conectado a estados simulados primero, ROS2 real después
- [ ] **Telegram:** reimplementar la notificación al cuidador (validada en el sistema anterior)
- [ ] **(Opcional) Benchmark de Qwen VL** para decidir `describe_surroundings` (`ROBOT_COGNICION.md`)
- [ ] **Modelos ONNX:** crear `scripts/fetch_models.py` + `models/README.md` al integrar SCRFD, ArcFace, openWakeWord, Vosk (ya previstos en `.gitignore`)
- [ ] **Simulación en Asus (Gazebo):** Nav2 + RTAB-Map contra robot simulado, valida lógica de navegación/búsqueda sin esperar el montaje físico
- [ ] **Regla transversal:** cada herramienta/acción se prueba aislada antes de conectarla al sistema completo

**Salida esperada:** sistema completo funcionando "en el aire" (conversando, mostrando cara, decidiendo), listo para conectar a hardware real.

---

## FASE 2 — Protocolo de comunicación y firmware (en paralelo a Fase 1, con Sergio y Linda)

- [x] Arquitectura del enlace UART: 2 líneas dedicadas, trama binaria + CRC8, watchdog (ADR-028)
- [ ] Cerrar los mensajes del link Movilidad con Sergio, partiendo del borrador en `HARDWARE_FIRMWARE.md` y resolviendo sus problemas conocidos
- [ ] Cerrar los mensajes del link Médica con Linda (misma base)
- [ ] Definir la propagación de la parada de emergencia (STM32 → ESP32 / ROS2)
- [ ] Definir la telemetría de energía (3 rieles del INA3221 + batería)
- [ ] Decidir dónde vive la compensación por pendiente (IMU) y quién comanda las luces traseras (`ROBOT_MOVILIDAD.md`)
- [ ] Resolver el riel de 5V con la tira COB (opciones A/B/C en `HARDWARE_FIRMWARE.md`, "Presupuesto de potencia")
- [ ] Entrega de especificación + plantilla base en C (PlatformIO + ESP-IDF) a Sergio y Linda
- [ ] Andrés implementa el lado STM32 (puente) y valida contra la especificación

**Salida esperada:** protocolo cerrado y firmwares de Sergio/Linda avanzando en paralelo sin bloquear ni bloquearse con la Fase 1.

---

## FASE 3 — Integración progresiva (en el orden en que vayan llegando los hitos de hardware)

- [ ] **Firmware Movilidad integrado (Sergio)** → `navigate_to`/`find_user` reales, UART Movilidad end-to-end, integración STM32 (micro-ROS) ↔ ROS2 real
- [ ] **Pastillero con ajustes terminados + firmware Médica integrado (Linda)** → `dispense_medication` real, UART Médica end-to-end
- [ ] **Cableado de torso y cabeza (Sergio) + montaje final** de Dell/Kinect/cámara/parlante dentro de la carcasa terminada → validación de cableado y **re-validación de los benchmarks de voz dentro de la carcasa cerrada** (la acústica cambia respecto al Dell suelto en escritorio); si aplica, repetir la validación de localización de fuente sonora (bonus)
- [ ] Integrar el numpad MPR121 (uso a definir, ver `ROBOT_HMI.md`)

**Salida esperada:** robot físico completo respondiendo a todas las herramientas del agente con hardware real, no stubs.

---

## FASE 4 — Validación de sistema completo

- [ ] UART STM32↔ambos ESP32 bajo carga real (movimiento + dispensación simultáneos si aplica)
- [ ] Mapeo real del espacio de la demo (modo manual/asistido)
- [ ] Flujo completo del Módulo 3 (búsqueda del usuario) de punta a punta con robot real
- [ ] Pruebas de estabilidad: batería (con el Kinect siempre encendido), temperatura, comportamiento ante fallos de red (con y sin hotspot)

---

## FASE 5 — Preparación específica de la demo

- [ ] Guion de los 15 minutos (movimiento en vivo, dispensación pedida en el momento, consulta real a BD, momento proactivo del agente)
- [ ] Grabación de clip(s) de video para autonomía no demostrable en vivo
- [ ] Ensayo en condiciones similares al auditorio (hotspot, ruido ambiente)
- [ ] Ensayos repetidos hasta que se sienta natural, no ensayado

---

## FASE 6 — Documentación y cierre

- [x] División del documento maestro en archivos modulares (documento maestro archivado en `docs/archivo/`)
- [x] Registro de decisiones en `DECISIONES_TECNICAS.md` (formato ADR)
- [ ] Análisis de precio de producción en masa: inventario de componentes (Excel, se subirá a `docs/`), posibles reemplazos más económicos y costo por unidad (resultado como documento aparte en `docs/`)
- [ ] Registro de resultados finales de los benchmarks de voz con números reales en `ROBOT_VOZ.md` (el benchmark de LLM ya está registrado en ADR-013)
