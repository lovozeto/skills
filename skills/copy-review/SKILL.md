---
name: copy-review
description: Audita y redacta microcopy, mensajes de error, etiquetas de botones y textos de interfaz en el tono de voz adecuado, sin rodeos ni patrones de culpa.
disable-model-invocation: true
---

# copy-review — Redacción y Microcopy de Interfaz

Usa esta skill cuando el usuario pida revisar o redactar textos, copys, mensajes de error, onboarding o etiquetas de una interfaz.

## Principios de Redacción

1. **Claridad sobre ingenio:** Las etiquetas de botones y enlaces deben describir exactamente la acción que va a ocurrir (ej. "Descargar reporte PDF" en lugar de "Continuar").
2. **Mensajes de error útiles:** Todo error debe explicar en lenguaje humano qué pasó y qué puede hacer el usuario para solucionarlo (nada de "Error 0x823" o "Ocurrió un error inesperado" a secas).
3. **Cero manipulación emocional:** Sin confirmshaming ("No gracias, no me gusta ahorrar dinero"), sin falsa urgencia ni cuentas regresivas artificiales.
4. **Economía de palabras:** Frases cortas y contundentes. Si una palabra no aporta significado, se elimina.
5. **Consistencia de tono:** En español colombiano natural, profesional pero cercano, sin formalismos arcaicos ni jerga incomprensible.

## Formato de Salida

```
REVISIÓN DE COPY — [Pantalla o Componente]
TEXTOS PROPUESTOS:
- [Elemento]: "[Texto sugerido]"
  - Por qué: [Razón de usabilidad o tono]

TEXTOS EXISTENTES CORREGIDOS:
- Antes: "[Texto original]"
- Después: "[Texto pulido]"
  - Motivo del cambio: [Ambigüedad, tono, longitud]
```
