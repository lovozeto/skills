---
name: qa
description: Ejecuta auditoría técnica estricta (build, TypeScript/compilación, resolución de imports, cobertura de estados de error/carga y validación de lógica). Reporta errores reales sin suposiciones.
---

# qa — Auditoría Técnica y Validación de Código

Usa esta skill cuando el usuario pida verificar la calidad técnica, correr pruebas o buscar errores antes de dar por terminada una tarea.

## Protocolo de Verificación (Secuencia Estricta)

1. **Compilación / Build:** Ejecuta el comando de construcción del proyecto (`npm run build`, `cargo check`, etc.). Si falla, detén la auditoría y reporta el error exacto.
2. **Chequeo de Tipos:** Ejecuta `npx tsc --noEmit` (en TypeScript) o el linter de tipos correspondiente.
3. **Resolución de Dependencias e Imports:** Verifica que no existan imports rotos, referencias circulares o módulos huérfanos.
4. **Cobertura de Estados Asíncronos:** Toda llamada asíncrona debe tener manejados explícitamente sus estados:
   - `loading` (indicador visual de carga)
   - `error` (mensaje de error legible y accionable)
   - `empty` (estado vacío si no hay datos)
   - `success`
5. **Reglas de Negocio / Lógica:** Comprueba que los cambios cumplan la lógica solicitada sin efectos colaterales en módulos adyacentes.
6. **Accesibilidad Técnica:** Controles con solo iconos deben tener `aria-label`, inputs con etiquetas asociadas, imágenes con `alt`.

## Formato de Salida

Si todo está limpio:
```
ZERO ERRORS — Build pasa limpio, tipos validados, estados cubiertos.
```

Si hay errores:
```
ERRORES ENCONTRADOS — [Severidad descendente]
1. [BUILD | TIPOS | IMPORTS | ESTADOS | LÓGICA | A11Y]
   - Archivo y Línea: [ruta:línea]
   - Error exacto: [Descripción del fallo]
   - Causa raíz: [Por qué ocurre]
```
