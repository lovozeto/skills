---
name: vqa
description: Visual QA. Audita pantallas y componentes en múltiples breakpoints (375, 768, 1280 px) y en modo claro/oscuro, detectando desalineaciones, fuentes incorrectas y regresiones visuales.
---

# vqa — Auditoría Visual (Visual QA)

Usa esta skill cuando el usuario pida comprobar la apariencia visual de una pantalla o componente en el navegador antes de darlo por aprobado.

## Puntos de Verificación Visual

1. **Breakpoints Responsive:** Comprobar la visualización a:
   - **Móvil (375 px):** Sin desbordamientos horizontales, lectura cómoda, botones fáciles de tocar con el pulgar.
   - **Tablet (768 px):** Transición limpia entre layouts verticales y de varias columnas.
   - **Desktop (1280+ px):** Contenido contenido adecuadamente, márgenes equilibrados.
2. **Modo Claro vs. Modo Oscuro:**
   - Contraste legible en ambos modos (AA: 4.5:1 texto normal).
   - Sin cajas blancas o textos oscuros "fantasma" que hayan quedado fijos en modo oscuro.
3. **Tipografía y Jerarquía:**
   - Familias tipográficas correctas cargadas (sin fuentes genéricas del sistema que se filtren).
   - Jerarquía visual sólida: títulos claros, sin palabras huérfanas en encabezados.
4. **Espaciado y Alineación:**
   - Elementos alineados a la rejilla, padding interno coherente, sin elementos comprimidos o desproporcionados.
5. **Vibe y Acabado:**
   - Detectar si la interfaz se siente genérica/plana o si refleja fielmente el diseño de marca del proyecto.

## Formato de Salida

```
INFORME VQA — [Pantalla o Componente]
Breakpoints evaluados: 375px | 768px | 1280px
Modos evaluados: Claro | Oscuro

REGRESIONES / DETALLES VISUALES ENCONTRADOS:
1. [TIPOGRAFÍA | ESPACIADO | COLOR/CONTRASTE | MODO OSCURO | ALINEACIÓN]
   - Vista afectada: [375px | 768px | 1280px | Modo Oscuro]
   - Detalle visual: [Descripción del defecto visual observado]
   - Corrección sugerida: [Ajuste de CSS / Tokens necesario]

ELEMENTOS VISUALES CORRECTOS:
- [Aspectos que lucen alineados y con buen acabado]
```
