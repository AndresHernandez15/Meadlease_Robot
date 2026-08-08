# MEADLEASE — HARDWARE Y FIRMWARE

## Estado de construcción (última actualización: reformulación de agosto 2026)

| Frente | Estado |
|---|---|
| Impresión 3D | ~90% — cuerpo completo impreso incluyendo cabeza y cuello. Falta: compuertas de mantenimiento y brazo de signos vitales |
| Post-procesado | Iniciado (todo el equipo), ~1 semana estimada una vez impresas las piezas faltantes |
| Cableado | En curso (Sergio), en paralelo al post-procesado — objetivo: robot completamente cableado antes de pegar/masillar la carcasa de forma definitiva, dejando solo las compuertas de mantenimiento como punto de acceso |
| Dispensador (pastillero) | **100% funcional y probado**, incluida la ventosa de succión en TPU (ya fabricada). Ajuste menor en curso (Linda): cambio de tornillo sin fin impreso en 3D por uno metálico, para mejorar tolerancias y suavidad |
| PCB de movilidad | En curso (Sergio) — resolviendo falsos contactos en sensores ultrasónicos JSN-SR04T |
| PCB Médica / firmware ESP32 Médica | Pendiente, en coordinación con especificación de protocolo (Fase 2 del roadmap) |
| Dell Inspiron (placa) | **Desmontable** — actualmente fuera de la carcasa, en el escritorio de Andrés, con acceso total a cámara/micrófono/puertos. Ubuntu 24.04 + ROS2 Jazzy ya instalados limpios. La pantalla del Dell también está desmontada y en el mismo escritorio — todas las pruebas de desarrollo (incluido el HMI) se realizan con esa misma pantalla, de forma consistente hasta el ensamblaje final |
| STM32F411 (micro-ROS) | Validado con PC vía USB-CDC — pendiente conexión UART a ambos ESP32 |

*(El estado de cada componente individual — sensores, actuadores, MCUs — está junto a su ficha en el inventario de la Capa 0, para no repetir la información dos veces.)*

## Capa 0 — Hardware físico (🔒 fijo, sin cambios)

### Computación y procesamiento

| Componente | Especificación | Ubicación | Función | Estado |
|---|---|---|---|---|
| Dell Inspiron 3421 | Placa madre sin carcasa · i3-3227U · 12GB RAM DDR3, sin GPU | Cabeza (trasera) | Única computadora del sistema — corre Ubuntu 24.04 + ROS2 Jazzy | ✅ Funcional |
| Pantalla Samsung | Panel LED 14–15" reusado, vía cable LVDS/eDP interno a la placa Dell | Cabeza (frontal, ~110 cm) | Salida del HMI | ✅ Funcional |
| Trackpad Samsung | Trackpad original Samsung, conector ZIF interno compatible con la placa Dell (no USB) | Pecho (izquierda, ~95 cm) | Entrada táctil del HMI | ✅ Funcional |
| Cámara Dell | Integrada en la placa madre | Cabeza | Percepción visual (ver `ROBOT_PERCEPCION.md`) | ✅ Funcional |
| STM32F411 Blackpill | MCU auxiliar, micro-ROS, puente único de comunicaciones | Pecho (bajo cabeza) | Ver Capa 2 | ✅ micro-ROS validado con PC — pendiente UART a ESP32 |
| ESP32 S3 — Movilidad | Control motores BLDC, encoders Hall, ultrasonidos, PID de velocidad, monitoreo de energía | Base | Ver Capa 2 y "Sistema de energía" | ✅ Montado, PID probado |
| ESP32 S3 — Médica | Control del dispensador, signos vitales, sensores médicos | Torso | Ver Capa 2 | ✅ Funcional |
| ESP32-CAM | Verificación visual de la caída de la pastilla — funciona como un sensor "esclavo" del ESP32 Médica: éste le pregunta por UART si la pastilla detectada corresponde al medicamento esperado (X), y la ESP32-CAM responde sí/no. Lógica de comparación a cargo de Linda | Torso (vista al compartimento de salida) | Verificación de identidad de la pastilla dispensada | ✅ Funcional de forma aislada |

### Sensores de percepción — visión y mapeo

| Sensor | Modelo | Función | Alimentación | Ubicación |
|---|---|---|---|---|
| Kinect V2 | Microsoft Kinect V2 | SLAM RGB-D + detección de personas + array de micrófonos de 4 canales | 12V | Pecho (~88 cm) |
| Cámara Dell | Integrada en placa madre | Reconocimiento facial | Incluida en el Dell | Cabeza |
| ESP32-CAM | Módulo dedicado | Verificación visual de pastilla en el cajón de salida | 5V | Torso |

### Sensores de obstáculos

| Sensor | Cantidad | Posición | Alimentación | Rango | Estado |
|---|---|---|---|---|---|
| JSN-SR04T | 5 | 2 frontales (bordes, 0°) · 2 laterales (esquinas delanteras, 90°) · 1 trasero (centrado, 180°) | 5V | 0.2–4.5 m | Montaje y ángulos definidos — falsos contactos en resolución (PCB de movilidad, ver "Estado de construcción") |

Montaje a 10 cm del suelo, en carcasas impresas integradas a la carcasa base con ángulos fijos y protección contra golpes incluida en el diseño.

### Sensores biomédicos

| Sensor | Modelo | Medición | Alimentación | Comunicación |
|---|---|---|---|---|
| Pulso + SpO₂ | MAX30102 | BPM + SpO₂ | 3.3V | I2C → ESP32 Médica |
| Temperatura | MLX90614 | Temperatura corporal | 3.3V | I2C → ESP32 Médica |

**Brazo de signos vitales:** servo MG996R de 180° acoplado directamente al eje del brazo, extiende/retrae el brazo hacia el usuario mediante PWM estándar (ángulo 0°–180°), 5V. Corresponde a la herramienta `extend_vitals_arm()` (ver `ROBOT_COGNICION.md`). Estado: ✅ disponible.

### Sensores del sistema de dispensación

| Sensor | Modelo | Función | Alimentación | Comunicación |
|---|---|---|---|---|
| IR pastilla | FC-51 | Detecta la caída de la pastilla hacia el compartimento de salida (reflexivo, activo bajo) | 5V | GPIO digital → ESP32 Médica (pull-up 10kΩ) |
| Presión de manguera | MPS20N0040D | Verifica succión activa de la bomba — confirma captura de la pastilla | 3.3V | HX711 (CLK+DATA) → ESP32 Médica |
| Final de carrera | Sensor HOME del carrusel | Confirma posición inicial del carrusel | — | ESP32 Médica |

### Odometría

Encoders Hall integrados en los drivers ZS-X11H, salida "Speed Pulse Out" vía GPIO hacia el ESP32 S3 Movilidad — fuente de velocidad/RPM/odometría para Nav2 (ver `ROBOT_MOVILIDAD.md`).

### Actuadores — locomoción

| Componente | Especificación | Consumo medido | Estado |
|---|---|---|---|
| Motores BLDC ×2 | Hoverboard 6.5", 24V, encoders Hall integrados | 640 mA @ 24V vacío (15.4 W) · ~250 mA crucero (6W c/u) · ~2A pico (48W c/u) | ✅ Montados en chasis metálico, PID implementado |
| Drivers ZS-X11H ×2 | Control PWM, disipador integrado | Pérdidas ~10% (1.5W crucero, 10W pico) | ✅ Montados y probados |
| Rueda loca ×1 | Frontal, equilibrio | — | ✅ |

**Tracción: diferencial** — 2 motores traseros + 1 rueda loca delantera (triángulo de apoyo). Dato de cinemática usado para configurar el plugin de controlador diferencial de Nav2 (ver `ROBOT_MOVILIDAD.md`).

### Actuadores — dispensación

| Componente | Especificación | Estado |
|---|---|---|
| Steppers 28BYJ-48 ×2 | 1 para el carrusel + 1 para el brazo (sube/baja vertical) | ✅ Disponibles |
| Drivers ULN2003 ×2 | Control de los steppers | ✅ Disponibles |
| Bomba de vacío ZT370-K3.7A | Nominal 3.7V @ 440 mA | ✅ Disponible |
| Ventosa de succión | Impresión en TPU, acoplada al extremo del brazo, conecta con la manguera de vacío | ✅ Fabricada y probada |
| Manguera de vacío | Tipo acuario/destreza, flexible, conecta bomba → ventosa | ✅ Disponible |



### Batería principal

| Componente | Especificación |
|---|---|
| Pack 7S4P | 7 serie × 4 paralelo, celdas 18650 mixtas validadas, 25.9V nominal (29.4V cargado, 21V mínimo), ~8Ah, ~207.2 Wh |
| BMS | HXYP-C47-MA18 (7S, balance), 10A continuo, 15A pico, conector balance de 8 pines (7 celdas + común) |
| Cargador | SJT-65E, 29.4V @ 2A |

### Puerto de carga externo

Conector AC 110V del propio cargador SJT-65E, empotrado en la carcasa exterior (torso trasero, bajo la puerta de mantenimiento) — no requiere abrir el robot para cargar.

**Naturaleza del "regreso a base":** es un conector manual, no un dock de acople automático. `return_to_base()` (ver `ROBOT_COGNICION.md`/`ROBOT_MOVILIDAD.md`) navega al robot hasta un punto "home" donde un humano puede conectarlo manualmente al cargador — no realiza acople/carga autónoma. Una base de carga automática sería lo ideal, pero se descartó deliberadamente para este prototipo por simplicidad y para ajustarse al alcance funcional definido.

### Reguladores de voltaje

| Regulador | Entrada | Salida ajustada | Corriente máx | Carga real | Margen | Asignación |
|---|---|---|---|---|---|---|
| XL4016 #1 | 29V | 19.7V (compensa caída en cable del cuello) | 9A | 2.3A | 74% | Dell Inspiron |
| XL4016 #2 | 29V | 12.0V ± 0.1V | 9A | 2.5A pico | 72% | Kinect V2 |
| XL4015 | 29V | 5.0V ± 0.05V | 5A | 2.8A pico | 44% | Lógica (MCUs, sensores, steppers, bomba) |

### Fusibles

| Fusible | Valor | Tipo | Ubicación | Protege |
|---|---|---|---|---|
| Principal | 15A | Slow-blow ("T") | Entre BMS y distribución 29V | Pico de arranque de motores (7.8A) — un fast-blow de 10A saltaría en arranque normal |
| 19.5V | 3A | Fast-blow | Salida XL4016 #1 | Sobrecarga del Dell |
| 12V | 3A | Fast-blow | Salida XL4016 #2 | Sobrecarga del Kinect |
| 5V | 5A | Fast-blow | Salida XL4015 | Sobrecarga de lógica |

## Capa 2 — Comunicación PC ↔ Microcontroladores

| Decisión | Valor | Justificación |
|---|---|---|
| Arquitectura | **STM32 como puente único** (PC↔STM32↔ESP32s vía UART) | Se evaluó micro-ROS también en ESP32 (WiFi directo a PC, viable técnicamente — existe componente oficial micro-ROS para ESP-IDF) — descartado: movimiento/parada de emergencia son capa reactiva, no pueden depender de WiFi (riesgo real en demo con auditorio congestionado) |
| micro-ROS | Se mantiene en STM32F411 (USB-CDC), ya validado físicamente | Confirmado soporte oficial para Jazzy |
| Protocolo UART STM32↔ESP32 | **Trama binaria fija + CRC8**, especificación cerrada (ver ADR-028 en `DECISIONES_TECNICAS.md` y tablas de detalle abajo) | Más eficiente de parsear, detecta corrupción, sigue siendo depurable (logs de valores ya decodificados) |
| Botones físicos de emergencia (trasero + cabeza) | Conectados como **interrupción directa al STM32** (GPIO PA0 y PA1, no pasan por la trama UART normal), redundantes entre sí | Garantiza que la parada de emergencia no compita en latencia/prioridad con el resto de los datos del protocolo binario |
| ESP32-CAM | Cuelga como sensor esclavo del **ESP32 Médica** vía UART (no del STM32 directamente): la ESP32 Médica pregunta si la pastilla detectada corresponde al medicamento esperado, la ESP32-CAM responde sí/no. Lógica de comparación a cargo de Linda | Evita duplicar una segunda conexión UART directa al STM32 — el STM32 solo necesita el resultado ya consolidado que le entrega la ESP32 Médica |
| Numpad MPR121 | I2C directo al STM32F411 (no a un ESP32) | Consistente con que el STM32 es el puente central también para entrada de usuario física |
| Firmware ESP32 | **PlatformIO + framework Arduino** | Balance velocidad de desarrollo/estructura de proyecto vs. ESP-IDF puro. Implementado por Sergio/Linda sobre especificación y plantilla base entregada por Andrés |
| Firmware STM32 | STM32CubeIDE, sin cambios | Ya validado, estándar correcto para el chip. Implementado por Andrés |

### Especificación de la trama UART (detalle)

**Framing (idéntico en ambos links):**

`[START 0xAA] [MSG_TYPE 1B] [LEN 1B] [PAYLOAD 0-N bytes] [CRC8 1B] [END 0x55]`

- CRC8 Maxim/Dallas (polinomio 0x31), calculado sobre `MSG_TYPE + LEN + PAYLOAD`
- Little-endian en todos los campos multi-byte
- Baudrate: 115200
- Dos líneas UART físicas dedicadas (STM32↔Movilidad, STM32↔Médica) — sin bus compartido, sin byte de dirección

**Link Movilidad**

| MSG_TYPE | Nombre | Dirección | Frecuencia | Payload |
|---|---|---|---|---|
| `0x01` | CMD_VELOCITY | STM32→ESP32 | 20 Hz | `0-1: VL int16 (mm/s)` · `2-3: VR int16 (mm/s)` |
| `0x81` | TELEMETRY | ESP32→STM32 | 50 Hz | `0-1: RPM_izq int16` · `2-3: RPM_der int16` · `4-5: dist_frontal_izq uint16 (mm)` · `6-7: dist_frontal_der uint16 (mm)` · `8-9: dist_lateral_izq uint16 (mm)` · `10-11: dist_lateral_der uint16 (mm)` · `12-13: dist_trasero uint16 (mm)` · `14: flags_fallo uint8 (bitmask por ultrasonido)` · `15-16: voltage uint16 (mV)` · `17-18: current uint16 (mA)` |

`0xFFFF` en cualquier campo de distancia = sin eco/lectura no válida ese ciclo. `flags_fallo` reporta por bit qué ultrasonido específico no respondió — útil para diagnosticar los falsos contactos actuales de los JSN-SR04T.

RPM se calcula en el ESP32 Movilidad (no se envían ticks crudos), reutilizando el cálculo que ya hace para su lazo de control PID.

**Sensor de energía (INA3221 + divisor de voltaje):** lectura directa desde el ESP32 Movilidad, reportado dentro de `TELEMETRY` (campos `voltage`/`current`) — no tiene link ni trama propia.

**Watchdog:** si el ESP32 Movilidad no recibe `CMD_VELOCITY` en 500 ms, frena motores por su cuenta, independiente del botón físico de emergencia.

**Link Médica**

| MSG_TYPE | Nombre | Dirección | Payload |
|---|---|---|---|
| `0x02` | CMD_DISPENSE | STM32→ESP32 | `0: slot_id uint8` |
| `0x03` | CMD_MEASURE_VITALS | STM32→ESP32 | `0: kind uint8 (0=bpm, 1=spo2, 2=temp, 3=all)` |
| `0x04` | CMD_VITALS_ARM | STM32→ESP32 | `0: posición uint8 (0=retraer, 1=extender)` |
| `0x82` | RESP_DISPENSE | ESP32→STM32 | `0: slot_id uint8` · `1: resultado uint8 (0=éxito, 1=no_cae_pastilla, 2=pastilla_incorrecta, 3=fallo_succión)` · `2: pastilla_verificada uint8 (bool)` |
| `0x83` | RESP_VITALS | ESP32→STM32 | `0: bpm uint8` · `1: spo2 uint8 (%)` · `2-3: temp int16 (×10, ej. 368=36.8°C)` |

El resultado de verificación de la ESP32-CAM va consolidado dentro de `RESP_DISPENSE` (campo `pastilla_verificada`) — no requiere trama propia en este link, ya que se resuelve un nivel antes en la comunicación ESP32 Médica↔ESP32-CAM.

**Fuera de la trama binaria:** botones físicos de emergencia → interrupción directa GPIO PA0/PA1 del STM32, no pasan por ninguna trama definida arriba.

## Módulo 7 — Backbone físico / Comunicaciones (objetivos funcionales)

- Comunicación en tiempo real entre cerebro (agente+BT) y actuadores, sin latencia perceptible.
- Resiliencia básica: si un módulo no crítico falla (HMI, conversación), el robot mantiene funciones esenciales de seguridad y movimiento.
- Autonomía energética suficiente para la duración de la demo, con aviso proactivo de batería baja — respaldada por el divisor de voltaje + INA3221 descritos en "Monitoreo de energía".
- Auto-diagnóstico básico de sensores.

## Estructura de firmware en el repo

```
firmware/
├── stm32_backbone/          ← Andrés (STM32CubeIDE)
├── esp32_movilidad/         ← Sergio (PlatformIO, sobre spec+plantilla)
└── esp32_medica/            ← Linda (PlatformIO, sobre spec+plantilla; incluye la lógica de la ESP32-CAM como sub-target, dado que cuelga de este mismo firmware)
```

---

## Información faltante / pendiente de revisión

- **Manejo de errores/reintentos de la trama UART:** la especificación de campos/tamaños/orden de bytes ya está cerrada (ver sección "Especificación de la trama UART" arriba y ADR-028). Falta definir política de reintentos ante CRC inválido o timeout (¿el emisor reenvía automáticamente? ¿cuántos intentos antes de reportar fallo de link?).
- **Ubicación final de la tira LED ambiental:** pendiente de definir en CAD.
- **Estado y especificación de la PCB Médica:** sigue listada como "pendiente" sin más detalle.
- **Planos eléctricos / diagrama de conexión completo** entre STM32, ambos ESP32 S3, la ESP32-CAM, sensores y actuadores — esta documentación de hardware da los circuitos puntuales (bomba, divisor de voltaje, INA3221) pero no un diagrama unificado.
- **Nota de discrepancia de versión de SO:** el documento de hardware de la iteración pasada menciona Ubuntu 22.04 en el Dell; la decisión vigente del proyecto (`PROYECTO_GENERAL.md`) es Ubuntu 24.04 + ROS2 Jazzy, ya reinstalado limpio — se documenta aquí solo el inventario físico, la versión de SO vigente no cambia.
