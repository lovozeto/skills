---
name: kanban
description: Organiza y consulta ideas, tareas y progreso en el tablero Kanban del proyecto (GitHub Projects o KANBAN.md).
---

# kanban — Tablero Ágil de Tareas

Usa esta skill cuando el usuario quiera interactuar con su tablero de tareas (Ideas / Backlog, En Progreso, Hecho).

## Acciones rápidas

1. **Crear una idea o tarea:**
   - Si el proyecto usa GitHub Projects:
     `gh project item-create <project-number> --owner "@me" --title "<título>" --body "<descripción>"`
     (O con issue: `gh issue create --title "<título>" --body "<descripción>"`)
   - Si el proyecto usa un archivo local `KANBAN.md`:
     Añade la tarea bajo `### Ideas / Backlog`.

2. **Listar tareas activas:**
   - Si es GitHub Projects:
     `gh project item-list <project-number> --owner "@me"`
   - Si es `KANBAN.md`:
     Muestra un resumen compacto de las columnas.

3. **Mover tarea de columna:**
   - Pasa la tarea a **En Progreso** cuando se inicie, o a **Hecho** cuando finalice.

## Reglas de oro
- **Cero burocracia:** Nunca detengas el trabajo ni exijas tickets obligatorios para programar o responder. El tablero es solo una ayuda visual para el usuario.
- **Confirmación ágil:** Confirma en una sola línea (ej. *"✓ Tarea 'X' agregada al Backlog"*).
