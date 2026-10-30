---
name: kb-curate
description: Extrae reglas atómicas y de alta fidelidad desde fuentes de documentación, URLs o artículos técnicos hacia la Base de Conocimiento (shared/claude-kb/).
model: sonnet
---

# kb-curate — Extracción y Curaduría de Conocimiento Atómico

Usa esta skill cuando el usuario proporcione una fuente técnica (URL, artículo, estándar de diseño o documentación) y quiera extraer sus principios clave hacia la base de conocimiento (`shared/claude-kb/`).

**Modelo obligatorio:** Claude Sonnet (fidelidad textual y rigor analítico; nunca usar Haiku u otros modelos ligeros para evitar alucinaciones en reglas técnicas).

## Aislamiento de Contexto y Calidad

Para evitar contaminar el chat principal con páginas web masivas de 50.000 tokens:
1. Lee la fuente en una pasada aislada.
2. Extrae **únicamente reglas atómicas** (cada regla debe ser una sola viñeta concisa de ~50 tokens).
3. Cada regla debe incluir su cita de procedencia exacta (Autor/Organización y URL).

## Estructura de las Reglas Atómicas

Cada regla extraída debe seguir este formato exacto:
```markdown
- `tema#sección` · [Regla clara y accionable en una o dos oraciones]. [Fuente: URL o Nombre]
```

Ejemplo:
```markdown
- `usability-heuristics#error-messages` · Usa un tono descriptivo que no culpe al usuario y evita el humor en situaciones de fallo. [NN/g: https://www.nngroup.com/articles/error-message-guidelines/]
```

## Proceso de Guardado

1. Identifica a qué base temática pertenece (ej. `ux/`, `ui/`, `accessibility/`, `web-patterns/`, `cpp/`, `swift/`).
2. Agrega o actualiza la sección correspondiente dentro de `${KB_ROOT:-~/dev/claude-kb}/<base>/<archivo>.md`.
3. Notifica al usuario en una sola línea de resumen con las reglas añadidas.
