# MEADLEASE — MOVILIDAD Y NAVEGACIÓN

> **Corresponde a:** `robot_bringup`

---

## Objetivos funcionales (Módulo 3)

| Función | Alcance | Demo |
|---|---|---|
| Navegación autónoma A→B | Esencial, con waypoints con nombre (vía Nav2 Waypoint Follower) | En vivo — mayor impacto visual |
| Búsqueda activa del usuario | Recorrido de waypoints ordenados por cercanía, apoyada en percepción continua (`ROBOT_PERCEPCION.md`) — sin lógica de detección propia duplicada. Flujo: navega a siguiente waypoint no visitado → percepción detecta persona (en background) → si detecta, se acerca y reconoce → si es el usuario, atiende tarea; si no, continúa → si se acaban waypoints sin encontrarlo, notifica (Telegram) y regresa a base. **Interrumpible por voz:** si durante la búsqueda el usuario llama al robot (ej. "¡Aquí estoy!"), el agente lo reconoce, detiene el recorrido a waypoints y dispara la búsqueda de persona en la posición actual en lugar de continuar al siguiente waypoint — refuerza el objetivo de que el robot se sienta atento/vivo, no en piloto automático ciego | Video (mejor que en vivo por tiempo), con el momento de interrupción por voz como posible instante en vivo |
| Aproximación social | Velocidad/distancia cómodas — reutiliza comportamiento APPROACHING | En vivo, parte natural del movimiento |
| Seguimiento (follow-me) | **Opcional/bonus** — construir solo si el tiempo alcanza, es la función más costosa de toda la lista (tracking continuo + control de velocidad en lazo cerrado) | Demo si se construye |
| Regreso a base/carga | Esencial para operación, bajo perfil en demo | Background |
| Parada de emergencia | No negociable — resuelta en hardware + reflejo de capa reactiva (ver `ROBOT_COGNICION.md` Módulo 5C) | Podría mostrarse en vivo |
| Bloqueo de movimiento durante dispensación | Esencial | Implícito |
| Mapa interactivo tipo Roomba en HMI | Mostrar occupancy grid de Nav2, clic para definir waypoints y estación de carga (ver `ROBOT_HMI.md`) | Construcción/config, no necesariamente demo en vivo |
| Modo de mapeo | **Manual/asistido** (mover el robot mientras RTAB-Map mapea, guardar desde HMI) — exploración autónoma de frontera **descartada** por complejidad/riesgo desproporcionado para el alcance de prototipo | Config previa a la demo |
| Control remoto vía QR | Página adicional del mismo servidor NiceGUI (`/control`), QR codifica la URL, mismo WiFi que comparte el celular durante la demo. Útil para mover el robot manualmente durante mapeo | Herramienta de operación, no de demo en vivo |

## Decisiones técnicas (Capa 4 — SLAM y Navegación)

| Función | Decisión | Justificación |
|---|---|---|
| SLAM | **RTAB-Map**, actualizar a 0.21.9+ | Confirmado con paper académico 2026 sobre Jazzy — alternativas (SLAM Toolbox, Cartographer, GMapping) son LiDAR-first, no aptas para RGB-D sin conversión con costo de CPU. Versión 0.21.9 corrige bug real de sincronización `message_filters` |
| Navegación | **Nav2**, sin alternativa real mejor | Nav2 usa `BehaviorTree.CPP` internamente, pero es irrelevante para nuestra decisión de framework de BT propio — se le llama como action server externo, su árbol interno es una caja negra |
| Waypoints con nombre | **Nav2 Waypoint Follower + YAML** nombre→pose | Resuelto con herramienta nativa, no requiere código propio |

---

## Información faltante / pendiente de revisión

- **Dimensiones y peso del chasis** — la cinemática ya está definida (tracción diferencial, 2 motores traseros + rueda loca delantera, ver `HARDWARE_FIRMWARE.md`); falta el dato físico de dimensiones/peso para completar la configuración del plugin de controlador diferencial de Nav2.
- **Layout y cantidad de waypoints** para el espacio real de la demo — no definidos aún.
- **Dimensiones del espacio de prueba/demo** (relevante para tiempos de navegación en el guion de la Fase 5 del roadmap).
- **Parámetros concretos de Nav2** (velocidades máximas, radios de tolerancia, perfil del costmap) — no especificados, quedan para configuración durante Fase 1/3.
- **Definición operativa de "seguimiento (follow-me)"** si se llega a construir: no hay especificación técnica más allá de "tracking continuo + control de velocidad en lazo cerrado".
