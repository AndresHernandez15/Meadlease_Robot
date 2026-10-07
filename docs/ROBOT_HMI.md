# MEADLEASE — EXPRESIVIDAD / HMI

> **Paquete:** `robot_hmi` (Módulo 6)

## Funciones

- **Esencial:** comunicar el estado sin palabras, con una cara coherente con lo que el robot dice y hace.
- **Dashboard** de salud, medicación e historial, con tendencias de signos vitales.
- **Entrada:** trackpad + numpad MPR121 (ya montado; falta decidir para qué se usa).
- **Dictado por voz:** sin pantalla táctil ni teclado, escribir con el trackpad es incómodo, así que cualquier campo de formulario (medicamento, nombre de un waypoint…) se puede llenar hablando. Necesita internet.
- **Indicadores:** conectividad, batería y "esperando tu respuesta".
- **Sonidos de feedback** (p. ej. un beep al dejar de escuchar).
- **"Qué puedo hacer":** slideshow de capacidades cuando se le pregunta.
- **Bonus:** cerrar el dashboard solo, por privacidad.
- **Descartado:** botón de parada en pantalla (ADR-023) y "modo cuidador" con datos ampliados.
- **Nombre en la pantalla de reposo:** probablemente innecesario si va en la carcasa (pendiente en `PROYECTO_GENERAL.md`).

## Decisiones

| Qué | Decisión |
|---|---|
| Framework | NiceGUI en Chromium modo kiosco (ADR-022) |
| Cara | Canvas propio dentro de NiceGUI (springs, ondas de audio) |
| Sonidos | Web Audio API o una librería Python; no depende del framework |
| Datos | Lee y escribe la BD con la misma capa de acceso que el agente (`database/README.md`) |
| Mapa | Occupancy grid de Nav2 dibujado en canvas; con un clic se definen waypoints y la base (`ROBOT_MOVILIDAD.md`) |
| Mapeo y control remoto por QR | Ver `ROBOT_MOVILIDAD.md` |
| Dictado | El mismo STT del agente (Groq Whisper) en "modo dictado": escribe en el campo enfocado sin pasar por el LLM |
| WiFi | Desde el celular por QR (abajo). El teclado virtual `onboard` queda de respaldo. El dictado no sirve aquí porque no hay internet |
| Horarios de medicación | Que el usuario elija "todos los días", "algunos días" o "cada X horas" sin conocer el modelo de datos. El diseño visual se define al implementar |

### WiFi por QR (propuesta, sin implementar)

Si no hay una red conocida:

1. El Dell crea su propia red (`nmcli device wifi hotspot`, p. ej. `Koda-setup`).
2. La pantalla muestra dos QR: uno para conectar el celular a esa red (`WIFI:T:WPA;S:Koda-setup;P:…;;`) y otro con la URL de una página de NiceGUI (p. ej. `http://10.42.0.1:8080/wifi`).
3. La página lista las redes (`nmcli device wifi list`), recibe red y contraseña y ejecuta `nmcli device wifi connect`.
4. La tarjeta del Dell normalmente no puede ser punto de acceso y cliente a la vez: al enviar, se apaga la red propia y se intenta conectar; si falla, vuelve a crearla y muestra el error.

Es el patrón de *balena wifi-connect* y *comitup*. Primero hay que comprobar que la tarjeta WiFi del Dell soporte el modo hotspot.

## Pendientes

- Set inicial de estados del HMI y su relación con los eventos del agente y del árbol (crecerá durante el desarrollo).
- Diseño visual: colores por estado/urgencia, pantallas, tipografía.
- Para qué sirve el MPR121: ¿respaldo del dictado (ruido, privacidad, sin red) u otra cosa?
- Modo dictado: cómo se activa, cómo se corrigen errores y qué pasa sin conexión.
- WiFi por QR: implementación y prueba del hotspot.
- Contenido del slideshow de capacidades.
- Cierre automático del dashboard: tiempo y condición (bonus).
