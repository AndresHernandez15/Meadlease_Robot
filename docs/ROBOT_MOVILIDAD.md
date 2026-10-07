# MEADLEASE — MOVILIDAD Y NAVEGACIÓN

> **Paquete:** `robot_bringup` (Módulo 3)

## Funciones

| Función | Alcance | En la demo |
|---|---|---|
| Ir de A a B | Esencial, con waypoints con nombre | En vivo, lo de mayor impacto visual |
| Buscar al usuario | Ver abajo | En video; la interrupción por voz puede ir en vivo |
| Acercarse a la persona | Velocidad y distancia cómodas (acercamiento validado en el sistema anterior, por reimplementar) | En vivo |
| Seguir a la persona (follow-me) | Bonus; es lo más costoso de toda la lista | Solo si se construye |
| Volver a la base | Esencial. Va a un punto "home" donde una persona lo conecta al cargador (`HARDWARE_FIRMWARE.md`) | En background |
| Parada de emergencia | Hardware + reflejo del árbol (`ROBOT_COGNICION.md`) | Puede mostrarse en vivo |
| No moverse mientras dispensa | Esencial | Implícito |
| Compensar pendientes | Con el MPU6050 se ajusta la potencia al subir o bajar (dónde vive: ver pendientes) | Implícito |
| Luces traseras de giro y freno | 2 placas WS2812 en el ESP32 Movilidad (quién las comanda: ver pendientes) | Siempre visibles |
| Mapa tipo Roomba en el HMI | Ver el mapa y definir waypoints y la base con un clic (`ROBOT_HMI.md`) | Configuración |
| Mapeo | Manual: se mueve el robot mientras RTAB-Map mapea y se guarda desde el HMI (ADR-026) | Antes de la demo |
| Control remoto por QR | Página de NiceGUI que se abre desde el celular en la misma red. Sirve para manejarlo al mapear | Herramienta, no demo |

**Búsqueda del usuario:** recorre los waypoints del más cercano al más lejano mientras percepción mira en background. Si ve a alguien, se acerca y lo reconoce: si es el usuario, atiende la tarea; si no, sigue. Si se acaban los waypoints, avisa por Telegram y vuelve a la base. Si durante la búsqueda el usuario lo llama ("¡aquí estoy!"), deja el recorrido y lo busca ahí mismo, para que se sienta atento y no en piloto automático.

## Decisiones

| Qué | Decisión | ADR |
|---|---|---|
| SLAM | RTAB-Map 0.21.9+ con el Kinect (RGB-D) | 010, 034 |
| Navegación | Nav2 como action server externo | 011 |
| Waypoints | Nav2 Waypoint Follower + YAML nombre→pose | 011 |
| Cinemática | Diferencial: 2 motores traseros + rueda loca delantera (`HARDWARE_FIRMWARE.md`) | — |

## Pendientes

- **Compensación por pendiente:** ¿en el PID del ESP32 Movilidad (sin tocar el protocolo) o en ROS 2 (habría que enviar la inclinación por la trama)?
- **Luces de giro y freno:** ¿el ESP32 las deduce de las velocidades que recibe o las comanda ROS 2/Nav2?
- **Dimensiones y peso del chasis**, necesarios para configurar el controlador diferencial de Nav2.
- **La rueda loca se atasca en las juntas del piso:** problema mecánico sin solución todavía.
- **Espacio de la demo:** tamaño, distribución y cantidad de waypoints (afecta los tiempos del guion, Fase 5).
- **Parámetros de Nav2:** velocidades máximas, tolerancias, costmap (Fase 1/3).
- **Follow-me**, si se construye: falta especificarlo.
