---
name: brand
description: Genera y actualiza las directrices de marca del proyecto (paleta de colores con contraste WCAG, escala tipográfica, reglas del logo/marca, espaciado y dos & don'ts visuales).
model: sonnet
disable-model-invocation: true
---

# brand — Identidad de Marca y Sistemas Visuales

Usa esta skill cuando el usuario quiera definir, pulir o documentar la identidad visual y directrices de marca de un proyecto.

**Modelo recomendado:** Claude Sonnet (precisión en tokens, ratios de contraste y tipografía; nunca modelos de bajo razonamiento).

## Qué debe definir

1. **Paleta de Color:**
   - Colores con nombre semántico, valores hexadecimales y roles (superficie, fondo, texto primario/secundario, acento).
   - Ratios de contraste WCAG AA calculados y aprobados:
     - Texto normal: mínimo **4.5:1**
     - Texto grande y componentes: mínimo **3.0:1**
2. **Sistema Tipográfico:**
   - Familias seleccionadas (display/titulares y cuerpo/interfaz), con fuentes seguras o de Google Fonts.
   - Escala tipográfica definida por roles (Display, Title, Body, Label) con tamaños en `rem` y line-height proporcional.
3. **Logo / Símbolo / Marca:**
   - Espacio de seguridad perimetral, tamaño mínimo de reproducción, versiones sobre fondo claro y oscuro, y reglas estrictas de usos indebidos (no deformar, no cambiar colores).
4. **Espaciado y Radios:**
   - Escala de espaciado modular (base 4px u 8px) y escala de esquinas (border-radius).
5. **Dos & Don'ts:**
   - Lista clara de lo que está permitido y lo que está estrictamente prohibido para mantener coherencia visual.

## Formato de Salida

```
DIRECTRICES DE MARCA — [Nombre del Proyecto]
- Paleta de Colores: [Roles, HEX y contrastes AA]
- Tipografía: [Familias, roles y escala rem]
- Reglas de Marca: [Espacio de seguridad, versiones, usos indebidos]
- Grid & Espaciado: [Escala base y radios]
- Criterios Clave (Dos & Don'ts): [Reglas innegociables]
```
