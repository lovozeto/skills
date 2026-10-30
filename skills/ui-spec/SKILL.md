---
name: ui-spec
description: Especifica decisiones de interfaz de usuario (jerarquía, escalas tipográficas, paleta de color con contraste AA, espaciado, breakpoints responsive y estados de componentes).
---

# ui-spec — Especificación de Interfaz y Diseño

Usa esta skill cuando el usuario pida diseñar, especificar o pulir la UI de una pantalla, tarjeta o componente.

## Dimensiones a Especificar

1. **Jerarquía visual:** Qué elemento capta la atención primero, segundo y tercero.
2. **Tipografía:** Roles (display, title, body, label), familias tipográficas, tamaños (rem), peso y altura de línea (line-height) para breakpoints clave (375px móvil, 768px tablet, 1280px desktop).
3. **Color y Contraste:** Roles de superficie, texto y acento para modo claro y oscuro. Exige contraste WCAG AA:
   - Texto normal: mínimo **4.5:1**
   - Texto grande y componentes de UI: mínimo **3.0:1**
4. **Espaciado y Grid:** Escala de espaciado coherente (base 4px u 8px) y gaps para agrupar o separar visualmente.
5. **Comportamiento Responsive:** Cómo se reorganiza el layout entre 375px, 768px y 1280px.
6. **Objetivos Táctiles:** Mínimo 44×44 px con espacio entre ellos.
7. **Estados interactivos:** Default, hover, focus visible, active/pressed, disabled y loading.
8. **Check anti-genérico:** Evita que el componente parezca un template genérico de Bootstrap o Material crudo si el proyecto tiene identidad propia.

## Formato de Salida

```
ESPECIFICACIÓN UI — [Componente o Pantalla]
- Jerarquía: [Orden de lectura visual]
- Tipografía: [Escala por rol y tamaño]
- Color & Contraste: [Valores claro/oscuro + ratio comprobado]
- Espaciado: [Padding, margin, gaps]
- Responsive (375 / 768 / 1280): [Adaptación de layout]
- Estados: [Hover, foco, pulsado, deshabilitado]
- Anti-genérico: [Detalles que elevan la identidad visual]
```
