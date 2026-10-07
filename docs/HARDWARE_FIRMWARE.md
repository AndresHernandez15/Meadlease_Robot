# MEADLEASE — HARDWARE Y FIRMWARE

> **Cubre:** `firmware/` (STM32 y ESP32) y el Módulo 7 — Backbone físico.

## Objetivos (Módulo 7)

- Comunicación en tiempo real entre el cerebro (agente + árbol) y los actuadores, sin latencia perceptible.
- Si falla algo no crítico (HMI, conversación), la seguridad y el movimiento siguen funcionando.
- Batería suficiente para la demo, con aviso de batería baja (ver "Monitoreo de energía").
- Autodiagnóstico básico de sensores.

## Estado de construcción (octubre 2026)

| Frente | Estado |
|---|---|
| Impresión 3D | ✅ Completa, incluidas cabeza, cuello, brazo de signos vitales y compuertas |
| Post-procesado | ✅ Masillado, pintado y con el acabado final |
| Cableado | Parcial (Sergio): base lista; faltan torso y cabeza (Dell, Kinect, STM32, ESP32 Médica). Se accede por las compuertas |
| Dispensador | ✅ Funcional, ventosa de TPU incluida. Linda está cambiando el tornillo sin fin impreso por uno metálico |
| PCB auxiliar de movilidad | ✅ Falsos contactos de los ultrasonidos resueltos |
| PCB Médica | ✅ PCB propia con todos sus periféricos |
| Firmware ESP32 Médica | Firmware de prueba funcional (Linda); falta integrarlo con el protocolo UART (Fase 2) |
| Firmware ESP32 Movilidad | PID de velocidad probado (Sergio); falta integrarlo con el protocolo UART (Fase 2) |
| Dell Inspiron | Fuera de la carcasa, en el escritorio, con su pantalla. Ubuntu 24.04 + ROS 2 Jazzy instalados. Todas las pruebas (también las del HMI) se hacen así hasta el montaje final |
| STM32F411 | micro-ROS validado con el PC por USB; falta el UART con los ESP32 |

## Inventario

### Computación y entrada

| Componente | Detalle | Ubicación | Estado |
|---|---|---|---|
| Dell Inspiron 3421 | Placa sin carcasa: i3-3227U, 12 GB DDR3, sin GPU. Único computador del robot | Cabeza (atrás) | ✅ |
| Pantalla Samsung | Panel LED de 14–15" reusado, conectado por LVDS/eDP a la placa del Dell. Salida del HMI | Cabeza (frente, ~110 cm) | ✅ |
| Trackpad Samsung | Original, conector ZIF interno compatible con el Dell (no USB). Entrada del HMI | Pecho izq. (~95 cm) | ✅ |
| Numpad MPR121 | Teclado capacitivo, I2C al STM32. Uso por definir (`ROBOT_HMI.md`) | Parte superior del pecho, junto al trackpad | Montado, sin probar |
| Cámara Dell | Integrada en la placa. Presencia y reconocimiento facial | Cabeza | ✅ |
| STM32F411 Blackpill | Puente único de comunicaciones con micro-ROS (ADR-005) | Pecho (bajo la cabeza) | ✅ micro-ROS validado |
| ESP32-S3 Movilidad | Motores BLDC, encoders, ultrasonidos, PID, energía (INA3221 + divisor), IMU, relé de la COB y WS2812. Va sobre una placa de expansión | Base | ✅ PID probado |
| Placa de expansión ESP32-S3 | Base del ESP32 Movilidad; por aquí se conectan motores, encoders, relé, WS2812 y MPU6050 | Base | ✅ |
| PCB auxiliar de movilidad | Los 5 ultrasonidos, el INA3221 y el divisor de batería. Va unida a la placa de expansión con un bus de cables (es la "PCB de movilidad" del resto de los documentos) | Base | ✅ |
| ESP32-S3 Médica | Dispensador, signos vitales y sensores médicos, con PCB propia | Torso | ✅ Firmware de prueba |
| ESP32-CAM | Verifica la pastilla. La ESP32 Médica le pregunta por UART si es la esperada y responde sí/no (lógica de Linda) | Torso, mirando la salida | ✅ Funciona aislada |
| Parlante HK-5002 | 3 W, por USB al Dell (vía hub). Salida de voz | Por confirmar | ✅ |

### USB del Dell

El Dell tiene solo 2 puertos:

| Puerto | Conectado a |
|---|---|
| USB 3.0 | Kinect V2 (solo datos; se alimenta del riel de 12V) |
| USB 2.0 | Hub → parlante, STM32 y 2 puertos libres para mouse y teclado de desarrollo |

Por verificar: si el hub es pasivo, todo lo que cuelga de él comparte los ~500 mA del puerto USB 2.0.

### Visión, mapeo y audio

| Sensor | Función | Alimentación | Ubicación |
|---|---|---|---|
| Kinect V2 | SLAM RGB-D + micrófono del robot (ADR-034). Audio: ALSA "Xbox NUI Sensor", S32_LE, 4 canales, 16 kHz, por USB 2.0. ✅ Audio probado en el Asus; falta en el Dell y dentro de la carcasa | 12V | Pecho (~88 cm) |
| Cámara Dell | Presencia + reconocimiento facial | Del Dell | Cabeza |
| ESP32-CAM | Verificación de la pastilla | 5V | Torso |

### Obstáculos

5 ultrasonidos **JSN-SR04T** (5V, 0.2–4.5 m): 2 frontales (bordes, 0°), 2 laterales (esquinas delanteras, 90°) y 1 trasero (centro, 180°). Van a 10 cm del suelo en carcasas impresas con ángulo fijo y protección contra golpes. ✅ Montados y funcionando.

### Sensores biomédicos y del dispensador

| Sensor | Modelo | Qué hace | Alim. | Conexión |
|---|---|---|---|---|
| Pulso + SpO₂ | MAX30102 | BPM y SpO₂ | 3.3V | I2C → ESP32 Médica |
| Temperatura | MLX90614 | Temperatura corporal | 3.3V | I2C → ESP32 Médica |
| IR pastilla | FC-51 | Detecta que la pastilla cayó a la salida (activo bajo) | 5V | GPIO, pull-up 10kΩ |
| Presión de manguera | MPS20N0040D + HX711 (un módulo) | Confirma que la bomba está succionando la pastilla | 3.3V | CLK+DATA |
| Final de carrera | HOME del carrusel | Posición inicial del carrusel | — | ESP32 Médica |

**Brazo de signos vitales:** servo MG996R de 180° en el eje del brazo, PWM estándar, 5V. Es el que mueve `extend_vitals_arm()`. ✅ Disponible.

### IMU

**MPU6050** (acelerómetro + giroscopio) para apoyar la odometría y compensar pendientes. 3.3V desde la placa de expansión (~4 mA), I2C al ESP32 Movilidad en el mismo bus que el INA3221 (direcciones distintas). 🚧 En desarrollo; su integración está por definir (`ROBOT_MOVILIDAD.md`).

### Locomoción

| Componente | Detalle | Consumo | Estado |
|---|---|---|---|
| Motores BLDC ×2 | Hoverboard 6.5", 24V, encoders Hall | Vacío 640 mA (15.4 W) · crucero ~250 mA (6 W c/u) · pico ~2 A (48 W c/u) | ✅ Montados, PID listo |
| Drivers ZS-X11H ×2 | PWM, con disipador | Pérdidas ~10% (1.5 W crucero, 10 W pico) | ✅ Probados |
| Rueda loca | Delantera | — | ✅ |

**Tracción diferencial:** 2 motores traseros + rueda loca delantera. La odometría sale de los encoders Hall de los drivers ("Speed Pulse Out" → GPIO del ESP32 Movilidad).

### Dispensación

| Componente | Detalle | Estado |
|---|---|---|
| Steppers 28BYJ-48 ×2 + ULN2003 ×2 | Uno para el carrusel, otro para subir y bajar el brazo | ✅ |
| Bomba de vacío ZT370-K3.7A | Nominal 3.7V @ 440 mA; funciona bien a 5V | ✅ |
| Driver de la bomba | TIP122 desde el riel de 5V. Su caída (~1 V, por medir) deja la bomba cerca de su tensión nominal, sin regulador extra | ✅ Falta verificar diodo de flyback y corriente real |
| Ventosa + manguera | Ventosa de TPU en la punta del brazo, manguera flexible a la bomba | ✅ |

### Luces

| Componente | Detalle | Control | Estado |
|---|---|---|---|
| Tira COB inferior | Decorativa, 2 m × 7 W/m = 14 W (2.8 A a 5V) | Relé desde el ESP32 Movilidad (solo on/off) | ✅ ⚠️ No cabe en el riel de 5V (ver "Presupuesto de potencia") |
| Relé de 1 canal | Bobina ~70 mA (estimado) | GPIO del ESP32 Movilidad | ✅ |
| WS2812 traseras ×2 | 2 placas de 8 LEDs para giro y freno; hasta 0.96 A a brillo máximo | ESP32 Movilidad (una línea por placa o en cadena, por confirmar) | ✅ |

### Parada de emergencia

Dos dispositivos con interrupción directa al STM32, fuera de la trama UART (ADR-007):

| Dispositivo | Qué hace | Pin |
|---|---|---|
| Botón NC tipo hongo | Corta la alimentación de los motores por hardware y avisa al STM32 (vía divisor de voltaje). Queda enclavado hasta que se gira. Está en la parte trasera baja: se alcanza agachándose o con el pie | PA0 |
| Sensor capacitivo TTP223 | Activa la parada; una segunda pulsación reanuda. Está en la parte superior de la cabeza, accesible desde cualquier lado | PA1 |

Qué hace el robot ante una parada y cómo se reanuda: `ROBOT_COGNICION.md`. **Pendiente:** cómo el STM32 avisa de la emergencia a los ESP32 y a ROS 2.

## Energía

Batería 7S4P con BMS → interruptor → fusible principal → 29V → tres reguladores (19.7V, 12V, 5V).

| Componente | Detalle |
|---|---|
| Batería 7S4P | Celdas 18650 mixtas validadas: 25.9V nominal (29.4V llena, 21V mínimo), ~8 Ah, ~207 Wh |
| BMS | HXYP-C47-MA18, 7S con balanceo, 20 A, conector de balance de 8 pines |
| Cargador | SJT-65E, 29.4V @ 2A. Su conector AC de 110V está empotrado en el torso trasero, bajo la compuerta: se carga sin abrir el robot |
| Interruptor | Balancín junto a la batería, apaga todo el robot. Capacidad por confirmar (peor caso ~8.8 A) |

**"Volver a la base"** significa ir hasta un punto donde una persona conecta el cargador. No hay dock automático: se descartó por alcance.

### Monitoreo de energía

En el ESP32 Movilidad:

- **INA3221** (en la PCB auxiliar, I2C): corriente y tensión de los 3 rieles (19.7V, 12V, 5V).
- **Divisor de voltaje** (en la PCB auxiliar, ADC): tensión de la batería.

**Pendiente:** el mensaje que lleva estas lecturas al resto del sistema, y los valores del divisor y del shunt del INA3221.

### Reguladores y fusibles

| Riel | Regulador | Máx | Carga | Margen | Fusible | Alimenta |
|---|---|---|---|---|---|---|
| 19.7V | XL4016 #1 | 9 A | 2.3 A | 74% | 3 A rápido | Dell (llegan ~19.5V tras la caída en el cable del cuello) |
| 12V ± 0.1 | XL4016 #2 | 9 A | 2.5 A pico | 72% | 3 A rápido | Kinect |
| 5V ± 0.05 | XL4015 | 5 A | 3.83 A sin COB · **6.63 A con COB** ⚠️ | 23% · **−33%** | 5 A rápido (saltaría con la COB) | MCUs, sensores, steppers, bomba, relé, WS2812 |

**Fusible principal:** 15 A lento, entre el BMS y la distribución de 29V. Tiene que ser lento porque el arranque de los motores pide 7.8 A y uno rápido de 10 A saltaría. Al estar por debajo de los 20 A del BMS, ante un corto actúa primero el fusible y protege el cableado.

### Presupuesto de potencia

| Riel | Carga | Corriente |
|---|---|---|
| 19.7V | Dell con pantalla | 2.3 A |
| 12V | Kinect (encendido casi siempre por ser el micrófono) | 2.5 A pico |
| 5V | Lógica (MCUs, sensores, steppers, bomba) | 2.8 A pico |
| 5V | WS2812 (16 LEDs a brillo máximo) | 0.96 A |
| 5V | Relé | 0.07 A |
| 5V | Tira COB | 2.8 A |
| 3.3V | MPU6050 | ~0.004 A |
| USB | Parlante, STM32 | Desde el hub, no de los rieles |

**Problema del riel de 5V:** con la COB llega a 6.63 A en un regulador y un fusible de 5 A. Acortarla no alcanza: con 1 m sigue en 5.2 A. Opciones (sin decidir):

| Opción | Resultado | Contras |
|---|---|---|
| A. Segundo XL4015 solo para la COB | Lógica 3.83/5 A · COB 2.8/5 A | Más espacio, un regulador más |
| B. Cambiar el XL4015 por un XL4016 (9 A) | 6.63/9 A (margen 26%) | Hay que subir el fusible de 5V y revisar disipación |
| C. Atenuar la COB al 50% con TIP122 en PWM | 5.23 A: no alcanza con el XL4015; con B queda en 5.23/9 A | El TIP122 reemplazaría al relé y daría control de brillo |

**Peor caso de batería** (todo a pico, reguladores al ~90%): Dell 45 W + Kinect 30 W + 5V 33 W + motores 96 W ≈ 204 W → ~227 W / 25.9V ≈ **8.8 A**. Dentro del fusible de 15 A y del BMS de 20 A.

## Comunicación PC ↔ microcontroladores

| Qué | Decisión |
|---|---|
| Arquitectura | PC ↔ STM32 (micro-ROS por USB) ↔ ESP32 por UART (ADR-005) |
| Enlace UART | 2 líneas dedicadas, trama binaria con CRC8, watchdog de velocidad (ADR-006, ADR-028) |
| Parada de emergencia | Fuera de la trama (ver arriba) |
| ESP32-CAM | Cuelga de la ESP32 Médica, no del STM32; el STM32 solo recibe el resultado final |
| MPR121 | I2C directo al STM32 |
| Firmware ESP32 | PlatformIO + ESP-IDF (ADR-008), hecho por Sergio y Linda sobre la especificación y la plantilla de Andrés |
| Firmware STM32 | STM32CubeIDE, hecho por Andrés |

### Borrador de trama UART (no vinculante)

> ⚠️ Propuesta inicial. Se cierra con Sergio y Linda al implementar cada firmware y puede cambiar cualquier campo. Lo único fijo está en ADR-028.

**Framing:** `[0xAA] [MSG_TYPE] [LEN] [PAYLOAD] [CRC8] [0x55]`. Propuesta: CRC8 Maxim/Dallas (polinomio 0x31) sobre `MSG_TYPE+LEN+PAYLOAD`, little-endian, 115200 baudios.

**Link Movilidad**

| Tipo | Nombre | Dirección | Frec. | Payload |
|---|---|---|---|---|
| `0x01` | CMD_VELOCITY | STM32→ESP32 | 20 Hz | `VL int16`, `VR int16` (mm/s) |
| `0x81` | TELEMETRY | ESP32→STM32 | 50 Hz | `RPM_izq`, `RPM_der` (int16) · 5 distancias uint16 en mm (frontal izq/der, lateral izq/der, trasera; `0xFFFF` = sin lectura) · `flags_fallo` uint8 (un bit por ultrasonido) · `voltage` uint16 (mV) · `current` uint16 (mA) |

**Link Médica**

| Tipo | Nombre | Dirección | Payload |
|---|---|---|---|
| `0x02` | CMD_DISPENSE | STM32→ESP32 | `slot_id` uint8 |
| `0x03` | CMD_MEASURE_VITALS | STM32→ESP32 | `kind` uint8 (0=bpm, 1=spo2, 2=temp, 3=todas) |
| `0x04` | CMD_VITALS_ARM | STM32→ESP32 | `posición` uint8 (0=retraer, 1=extender) |
| `0x82` | RESP_DISPENSE | ESP32→STM32 | `slot_id` · `resultado` (0=éxito, 1=no cae, 2=pastilla incorrecta, 3=fallo de succión) · `pastilla_verificada` (bool) |
| `0x83` | RESP_VITALS | ESP32→STM32 | `bpm` uint8 · `spo2` uint8 · `temp` int16 ×10 (368 = 36.8°C) |

**Problemas a resolver al cerrarla:**

1. **Ultrasonidos a 50 Hz no es posible:** hay que dispararlos en secuencia para que no se interfieran (~5–10 Hz el ciclo completo). Conviene separar distancias y RPM en mensajes con frecuencias distintas.
2. **RPM entera es poca resolución:** cada unidad son ~8.6 mm/s en una rueda de 6.5", demasiado gruesa para la odometría de Nav2. Mejor ticks acumulados o RPM ×10/×100.
3. **`RESP_DISPENSE` es redundante:** "pastilla incorrecta" y `pastilla_verificada` dicen lo mismo.
4. **`RESP_VITALS` no tiene código de error** (dedo no detectado, timeout).
5. **`CMD_VITALS_ARM` no tiene confirmación.**
6. **Faltan mensajes:** emergencia, energía (3 rieles + batería), IMU (si la pendiente se compensa en ROS 2) y luces.
