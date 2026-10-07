# MEADLEASE — PERCEPCIÓN

> **Paquete:** `robot_perception` (Juan) — Módulo 1

## Funciones

| Función | Alcance | En la demo |
|---|---|---|
| Detección de presencia | Con la cámara Dell (su calidad se valida en Fase 1) | En background, siempre activa |
| Identificación del usuario | Solo para autorizar la dispensación. Debe soportar 2 o más usuarios, cada uno con su embedding, sus horarios y su historial. Si hay varias personas en cuadro, se reportan todas; a quién atender lo decide cognición | En vivo: un desconocido no recibe medicamento; un usuario reconocido sí |
| Soporte a la navegación | Mapeo, localización y obstáculos los resuelven RTAB-Map/Nav2 con el Kinect y los ultrasonidos (`ROBOT_MOVILIDAD.md`) | — |
| Estado de "atención" | Explorable, no bloqueante | Bonus |
| Escucha ambiental continua | Eliminada | — |

## Decisiones

| Qué | Decisión |
|---|---|
| Presencia | MediaPipe Pose (igual que antes; ya validado sin GPU) |
| Reconocimiento facial | SCRFD + ArcFace en ONNX Runtime, similitud coseno (ADR-009) |
| Cámara | La cámara Dell es la única que mira personas; el Kinect no (ADR-034). Funcionó en el sistema anterior y se reconfirma en Fase 1. Plan B: usar también el Kinect o una webcam externa |

## Pendientes

- Umbral de similitud coseno para aceptar una cara (balance entre falsos positivos y negativos).
- Resolución, FPS y campo de visión reales de la cámara Dell.
- Qué es exactamente el "estado de atención" y cómo se comunica al HMI y al agente (bonus).
- Registro de un usuario nuevo: cuántas fotos, flujo en el HMI y quién lo hace. Ya se sabe que primero se crean los datos y después la cara (`database/README.md`).
