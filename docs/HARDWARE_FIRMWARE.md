# MEADLEASE — HARDWARE Y FIRMWARE

> **Corresponde a:** `firmware/`
> **Frecuencia de cambio:** Alta mientras se arma el robot.
> Extraído de `MEADLEASE_REFORMULACION.md` (v1) — Capa 0, Capa 2, Módulo 7 y estado físico de construcción. Pendiente de revisión manual — ver sección final.

---

## Estado del hardware (última actualización: reformulación de agosto 2026)

| Elemento | Estado |
|---|---|
| Impresión 3D | ~90% — cuerpo completo impreso incluyendo cabeza y cuello. Falta: compuertas de mantenimiento y brazo de signos vitales |
| Post-procesado | Iniciado (todo el equipo), ~1 semana estimada una vez impresas las piezas faltantes |
| Cableado | En curso (Sergio), en paralelo al post-procesado — objetivo: robot completamente cableado antes de pegar/masillar la carcasa de forma definitiva, dejando solo las compuertas de mantenimiento como punto de acceso |
| Dispensador (pastillero) | **100% funcional**, ajustes menores en curso (Linda) — cambio de tornillo sin fin impreso en 3D por uno metálico, para mejorar tolerancias y suavidad |
| PCB de movilidad | En curso (Sergio) — resolviendo falsos contactos en sensores ultrasónicos JSN-SR04T |
| Dell Inspiron (placa) | **Desmontable** — actualmente fuera de la carcasa, en el escritorio de Andrés, con acceso total a cámara/micrófono/puertos. Ubuntu 24.04 + ROS2 Jazzy ya instalados limpios. La pantalla del Dell también está desmontada y en el mismo escritorio — todas las pruebas de desarrollo (incluido el HMI) se realizan con esa misma pantalla, de forma consistente hasta el ensamblaje final |
| PCB Médica / firmware ESP32 Médica | Pendiente, en coordinación con especificación de protocolo (Fase 2 del roadmap) |

## Capa 0 — Hardware físico (🔒 fijo, sin cambios)

- Dell Inspiron 3421 (i3-3227U, 12GB RAM DDR3, sin GPU)
- STM32F411 Blackpill
- ESP32 S3 ×2 (Movilidad, Médica)
- Kinect V2
- Cámara Dell integrada
- Motores BLDC + ZS-X11H
- Steppers 28BYJ-48
- Servo MG996R
- Bomba ZT370

## Capa 2 — Comunicación PC ↔ Microcontroladores

| Decisión | Valor | Justificación |
|---|---|---|
| Arquitectura | **STM32 como puente único** (PC↔STM32↔ESP32s vía UART) | Se evaluó micro-ROS también en ESP32 (WiFi directo a PC, viable técnicamente — existe componente oficial micro-ROS para ESP-IDF) — descartado: movimiento/parada de emergencia son capa reactiva, no pueden depender de WiFi (riesgo real en demo con auditorio congestionado) |
| micro-ROS | Se mantiene en STM32F411 (USB-CDC), ya validado físicamente | Confirmado soporte oficial para Jazzy |
| Protocolo UART STM32↔ESP32 | **Trama binaria fija + CRC8** (reemplaza texto plano `"VL:...,VR:...\n"`) | Más eficiente de parsear, detecta corrupción, sigue siendo depurable (logs de valores ya decodificados). Especificación completa a definir en Fase 2, coordinada con Sergio (ESP32 Movilidad) y Linda (ESP32 Médica) |
| Botón físico de emergencia | Conectado como **interrupción directa al STM32** (no pasa por la trama UART normal) — el STM32, al recibir la interrupción, actualiza inmediatamente un valor/estado que se propaga a ROS2 (ej. tópico o campo de estado de alta prioridad) para que el PC (agente/BT/HMI) se entere del cambio de estado sin depender del ciclo normal de la trama | Garantiza que la parada de emergencia no compita en latencia/prioridad con el resto de los datos del protocolo binario |
| Firmware ESP32 | **PlatformIO + framework Arduino** | Balance velocidad de desarrollo/estructura de proyecto vs. ESP-IDF puro. Implementado por Sergio/Linda sobre especificación y plantilla base entregada por Andrés |
| Firmware STM32 | STM32CubeIDE, sin cambios | Ya validado, estándar correcto para el chip. Implementado por Andrés |

## Módulo 7 — Backbone físico / Comunicaciones (objetivos funcionales)

- Comunicación en tiempo real entre cerebro (agente+BT) y actuadores, sin latencia perceptible.
- Resiliencia básica: si un módulo no crítico falla (HMI, conversación), el robot mantiene funciones esenciales de seguridad y movimiento.
- Autonomía energética suficiente para la duración de la demo, con aviso proactivo de batería baja.
- Auto-diagnóstico básico de sensores.

## Estructura de firmware en el repo

```
firmware/
├── stm32_backbone/          ← Andrés (STM32CubeIDE)
├── esp32_movilidad/         ← Sergio (PlatformIO, sobre spec+plantilla)
└── esp32_medica/            ← Linda (PlatformIO, sobre spec+plantilla)
```

---

## Información faltante / pendiente de revisión

- **Especificación completa de la trama binaria + CRC8:** marcada como pendiente explícita en el documento maestro (a definir en Fase 2) — campos exactos, tamaños, orden de bytes, manejo de errores/reintentos.
- **Batería y sistema de carga:** no hay especificación de tipo/capacidad de batería, autonomía estimada en horas, ni diseño del mecanismo físico de acople a la base de carga.
- **Cinemática/tracción del robot:** se listan motores BLDC+ZS-X11H y steppers 28BYJ-48 pero no el tipo de tracción (diferencial u otro) ni dimensiones/peso del chasis — dato necesario para configurar el plugin de Nav2 (ver `ROBOT_MOVILIDAD.md`).
- **Estado y especificación de la PCB Médica:** listada como "pendiente" sin más detalle.
- **Planos eléctricos / diagrama de conexión completo** entre STM32, ambos ESP32, sensores y actuadores.
- **Detalle del auto-diagnóstico básico de sensores** mencionado en Módulo 7 — no se especifica qué sensores cubre ni cómo se reporta al resto del sistema.
