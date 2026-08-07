# MEADLEASE — PERCEPCIÓN

> **Corresponde a:** `robot_perception` (Juan)
> **Frecuencia de cambio:** Media.
> Extraído de `MEADLEASE_REFORMULACION.md` (v1) — Capa 3 y Módulo 1. Pendiente de revisión manual — ver sección final.

*(Nota: `robot_perception` como paquete separado no es solo prolijidad — es la frontera de trabajo de Juan, quien solo necesita tocar esa carpeta sin fricción de coordinación con el resto del equipo.)*

---

## Objetivos funcionales (Módulo 1)

| Función | Alcance | Demo |
|---|---|---|
| Detección de presencia | Cámara Dell integrada (no Kinect, ahorro energético) — a validar calidad de cámara en Fase 1 | Background, siempre activa |
| Identificación de usuario | Acotada exclusivamente a gatear la dispensación de medicamentos. **Debe soportar 2 usuarios o más registrados simultáneamente** (ej. varios adultos mayores en el mismo hogar) — cada uno con su propio embedding facial, su propio esquema de medicación y su propio historial | Momento en vivo específico (usuario no reconocido → no dispensa; usuario reconocido → se identifica cuál es antes de dispensar) |
| Mapeo y localización propia | Esencial | Soporte de navegación |
| Detección de obstáculos/personas en movimiento | Esencial | Soporte de navegación |
| Escucha ambiental continua | **Eliminada** | — |
| Estado interno de "atención" | Explorable, no bloqueante | Bonus |
| Kinect V2 | Reservado exclusivamente a SLAM/navegación — se activa solo cuando el robot necesita moverse, no constante | — |

## Decisiones técnicas (Capa 3)

| Función | Decisión | Justificación |
|---|---|---|
| Detección de presencia | **MediaPipe Pose** (sin cambio) | Sigue siendo la mejor opción CPU-only en 2026, ya validado funcionando |
| Reconocimiento facial | **SCRFD (detección) + ArcFace (embeddings) vía ONNX Runtime**, similitud coseno | Reemplaza LBPH. Resuelve de raíz el bug de pipeline multi-usuario incompleto (agregar usuario = agregar embedding, sin reentrenar) — soporta los 2+ usuarios registrados requeridos (Módulo 1). Menos fotos necesarias (3-5 vs 200), menor sensibilidad a iluminación. Comparte runtime ONNX con VAD/wake word (ver `ROBOT_VOZ.md`) |
| Cámara | Cámara Dell integrada, exclusiva para percepción visual | Kinect reservado a SLAM. Ya validada informalmente en el sistema anterior (funcionó correctamente) — no es un riesgo que preocupe de momento, pero se re-confirma en Fase 1. **Plan B si no fuera suficiente:** usar el Kinect también para percepción visual, o en última instancia una webcam externa |

---

## Información faltante / pendiente de revisión

- **Caso de dos o más usuarios en el mismo cuadro simultáneamente:** no se especifica cómo el sistema decide a cuál atender/dispensar primero.
- **Umbral concreto de similitud coseno** para aceptar/rechazar una coincidencia de ArcFace (falsos positivos vs. falsos negativos).
- **Resolución/FPS de la cámara Dell** y su FOV real — el documento marca esto como "a validar en Fase 1", aún sin números.
- **Detalle del "estado interno de atención"** mencionado como explorable/bonus — sin especificación de qué señales lo componen ni cómo se expone al resto del sistema (HMI/agente).
- **Proceso de alta/registro de un nuevo usuario** (cuántas fotos, flujo de UI, quién lo ejecuta) — no descrito, solo se menciona que "agregar usuario = agregar embedding, sin reentrenar".
