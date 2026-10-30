---
name: ux-review
description: Evalúa flujos de usuario, jerarquía de información, ergonomía móvil (tap targets >= 44px), claridad de interacción y prevención de patrones oscuros.
disable-model-invocation: true
---

# ux-review — Auditoría de Experiencia de Usuario

Usa esta skill cuando el usuario pida revisar la UX de una pantalla, flujo, componente o interfaz.

## Criterios de Evaluación

1. **Integridad del flujo:** Sin callejones sin salida; un usuario que entra por primera vez puede completar la tarea clave sin ayuda.
2. **Jerarquía visual:** Lo esencial se encuentra en menos de 5 segundos en un móvil (375px).
3. **Ergonomía móvil:** Áreas táctiles mínimas de 44×44 px con espaciado adecuado. Sin scroll horizontal indeseado. Modales o bottom sheets que no tapen el teclado.
4. **Claridad de interacción:** Validación inline en inputs, errores accionables y recuperables, botones que describen exactamente lo que va a ocurrir.
5. **Carga cognitiva y confianza:** Cada sección tiene un único propósito claro. Sin patrones oscuros (urgencia falsa, confirmshaming, consentimiento premarcado, costos ocultos).
6. **Estados del sistema:** Contempla estados de carga (loading), vacío (empty), error, éxito y parciales para pasos asíncronos.
7. **Accesibilidad (A11Y):** Orden lógico de foco, nombres para controles con solo iconos, nada transmitido únicamente por color.

## Formato de Salida

```
AUDITORÍA UX — [Pantalla o Flujo]
HALLAZGOS:
1. [FLUJO | JERARQUÍA | INTERACCIÓN | MÓVIL | COGNITIVO | A11Y] Severidad: [Alta | Media | Baja]
   - Problema: [Descripción precisa]
   - Ubicación: [Archivo o componente]
   - Recomendación: [Solución concreta]

PUNTOS APROBADOS:
- [Aspectos que pasaron la revisión con éxito]
```
