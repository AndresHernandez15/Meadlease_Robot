# Meadlease_Robot

Robot asistente doméstico para acompañar y apoyar a personas mayores. Proyecto de grado de Ingeniería Mecatrónica, Biomédica y Sistemas — Universidad Tecnológica de Bolívar, 2026.

**Koda** es el nombre del robot; **Meadlease**, el del proyecto.

> En construcción. En agosto de 2026 el proyecto se reformuló desde cero: el sistema anterior se había construido módulo por módulo, sin pensar en cómo cada pieza afecta al resto.

## Qué hace

Koda no busca ser un chatbot con ruedas: inicia comportamiento por su cuenta, toma decisiones y actúa con propósito propio.

- Conversa en español, con memoria de turno y un validador ético que le impide diagnosticar o recetar.
- Dispensa medicamentos (programados o a pedido) tras reconocer la cara del usuario.
- Mide frecuencia cardíaca, SpO₂ y temperatura, y guarda el historial.
- Navega por la casa y busca al usuario cuando no lo ve.
- Se detiene por botón físico, sensor táctil o comando de voz offline, sin depender de la red.
- Avisa a un cuidador por Telegram cuando hace falta.

Es un prototipo de tesis: el alcance está pensado para funcionar de forma consistente en una sustentación en vivo de 15 minutos.

## Arquitectura

Dos capas:

- **Reactiva:** un Behavior Tree (`py_trees`) siempre activo y sin LLM. Emergencias, obstáculos y prioridades de movimiento tienen la última palabra.
- **Deliberativa:** un agente LLM (Pydantic AI + Groq) que interpreta lenguaje natural y propone intenciones vía tool calls. El agente propone, el árbol dispone.

Un Dell Inspiron sin GPU (Ubuntu 24.04 + ROS 2 Jazzy) es el único cerebro. Un STM32 (micro-ROS) hace de puente por UART hacia dos ESP32, así que movimiento y parada de emergencia nunca dependen del WiFi.

```
Percepción (cámara Dell)   Voz (micrófono Kinect)
          │                        │
          ▼                        ▼
   Behavior Tree (py_trees) ◄──── Agente LLM (Pydantic AI)
          │                 propone intenciones
          ▼
   STM32 (micro-ROS, puente UART) ── ESP32 Movilidad
                                  └── ESP32 Médica ── ESP32-CAM
```

## Estado

La arquitectura está definida y registrada en los ADR. Los detalles de integración (mensajes UART, tópicos ROS 2, firmas de tools) se cierran al implementar cada parte.

Robot físico: impreso, post-procesado y pintado con el acabado final; dispensador funcional; base cableada (faltan torso y cabeza). Avance por fases en el [roadmap](docs/ROADMAP.md).

## Documentación

| Documento | Contenido |
|---|---|
| [`PROYECTO_GENERAL.md`](docs/PROYECTO_GENERAL.md) | Contexto, equipo, principios, entorno, estructura del repo |
| [`DECISIONES_TECNICAS.md`](docs/DECISIONES_TECNICAS.md) | Decisiones (ADR) con alternativas y justificación |
| [`ROADMAP.md`](docs/ROADMAP.md) | Fases de implementación |
| [`ROBOT_PERCEPCION`](docs/ROBOT_PERCEPCION.md) · [`ROBOT_COGNICION`](docs/ROBOT_COGNICION.md) · [`ROBOT_MOVILIDAD`](docs/ROBOT_MOVILIDAD.md) · [`ROBOT_VOZ`](docs/ROBOT_VOZ.md) · [`ROBOT_HMI`](docs/ROBOT_HMI.md) | Un documento por módulo |
| [`HARDWARE_FIRMWARE.md`](docs/HARDWARE_FIRMWARE.md) | Inventario, energía, comunicación con microcontroladores |
| [`database/README.md`](database/README.md) | Esquema de la base de datos |
| [`scripts/benchmarks/README.md`](scripts/benchmarks/README.md) | Benchmarks y experimentos |
