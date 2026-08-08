# MEADLEASE — EXPRESIVIDAD / HMI

> **Corresponde a:** `robot_hmi`

---

## Objetivos funcionales (Módulo 6)

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
- Nombre del robot en pantalla de reposo: **probablemente innecesario** si el nombre se coloca en la carcasa física — pendiente de decisión de diseño físico (ver `PROYECTO_GENERAL.md`).
- Pantalla de "modo cuidador" con datos médicos ampliados: **descartada**, fuera de alcance/objetivos definidos.

## Decisiones técnicas (Capa 7)

| Componente | Decisión | Justificación |
|---|---|---|
| Framework | **NiceGUI** sobre Chromium Kiosk | Construido sobre FastAPI+WebSockets (misma base que el sistema anterior), pero toda la interfaz en Python puro — unifica lenguaje con agente/BT/nodos ROS2. Usado en producción para paneles de robots (Zauberzeug) |
| Alternativa evaluada y descartada | **Godot Engine** | Integración con ROS2 es experimental/comunidad, requiere compilar módulo C++ propio dentro del engine — mismo tipo de riesgo frágil que el driver del Kinect, no apto para deadline |
| Animación de cara | Componente canvas personalizado embebido dentro de NiceGUI (springs, ondas de audio) | NiceGUI permite insertar HTML/JS personalizado cuando hace falta |
| Efectos de sonido | Reproducción de audio estándar (Web Audio API o librería de audio Python), independiente del framework elegido | No es una limitación de NiceGUI — aclarado explícitamente |
| Mapa interactivo | Renderizado de `/map` (occupancy grid de Nav2) como imagen en canvas, clic define waypoints/estación de carga | Reutiliza Waypoint Follower de Nav2 (ver `ROBOT_MOVILIDAD.md`) |
| Modo de mapeo | Manual/asistido (no exploración autónoma) | Ver `ROBOT_MOVILIDAD.md` |
| Control remoto | Página adicional del mismo servidor NiceGUI, acceso vía QR (misma red WiFi que la demo) | Sin infraestructura nueva — consecuencia de decisiones ya tomadas |
| Configuración WiFi | Página en NiceGUI + teclado virtual del sistema (`onboard` o similar de Linux) | Evita reinventar teclado en pantalla |
| Botón de parada en HMI | **Descartado** | Sin pantalla táctil, impráctico — se mantiene solo el físico |

---

## Información faltante / pendiente de revisión

- **Enumeración de los estados del HMI:** no hay un número fijo predefinido de estados — se definen y se amplían según necesidad durante el desarrollo (evitar camisa de fuerza desde el diseño). Falta definir el set inicial y su relación con los eventos del agente/BT, con la expectativa de que crezca orgánicamente.
- **Diseño visual concreto** (paleta de colores por estado/urgencia, wireframes de las pantallas, tipografía) — no está especificado más allá de la descripción funcional.
- **Uso concreto del numpad MPR121:** explícitamente marcado como pendiente ("decisión pendiente es *para qué* se usa, no si se usa").
- **Especificación de la pantalla "slideshow" de capacidades:** no se detalla contenido ni cuántas diapositivas/tarjetas incluye.
- **Detalle del cierre automático de dashboard por privacidad:** temporizador, condición de activación — no especificado (marcado como bonus).
