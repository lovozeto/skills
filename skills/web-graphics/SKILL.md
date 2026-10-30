---
name: web-graphics
description: Construye componentes de gráficos interactivos en tiempo real (Canvas 2D, WebGL, Three.js, partículas, animaciones y efectos visuales) optimizados para alto rendimiento a 60 fps.
---

# web-graphics — Especialista en Gráficos Web en Tiempo Real

Usa esta skill cuando el usuario quiera implementar o mejorar escenas en Canvas 2D, WebGL, shaders, partículas, efectos visuales interactivos o sincronizados con audio.

## Principios de Alto Rendimiento

1. **Hot Loop limpio:** Cero asignaciones de memoria (`new`, arrays temporales o funciones anónimas) dentro del `requestAnimationFrame`. Todo lo dinámico se pre-aloja o recicla en pools.
2. **Meta de 60 fps:** Rendimiento fluido a resolución de diseño con degradación adaptativa si el frame time excede 16ms.
3. **Pausas inteligentes:** Detener el loop de animación cuando el elemento no esté visible en el viewport (`IntersectionObserver` o tab en segundo plano).
4. **Dimensionamiento:** Manejar cambios de tamaño de contenedor con `ResizeObserver`, adaptando el canvas al pixel ratio adecuado sin deformar la relación de aspecto.
5. **Accesibilidad y Movimiento:**
   - Todo canvas decorativo debe llevar `aria-hidden="true"`.
   - Respetar `prefers-reduced-motion`: si está activo, renderizar un frame estático elegante en vez de animar.
   - Parpadeos y destellos siempre por debajo de 3 por segundo para prevenir fotosensibilidad.

## Formato de Salida

```
IMPLEMENTACIÓN GRÁFICA — [Componente / Escena]
- Tipo de Render: [Canvas 2D | WebGL | Shader | Three.js]
- API de Props: [Props configurables con valores por defecto]
- Optimizaciones aplicadas: [Estrategia de loop, caching de sprites, reciclaje de memoria]
- Rendimiento verificado: [FPS objetivo y consumo medido]
```
