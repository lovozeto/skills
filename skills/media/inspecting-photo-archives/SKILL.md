---
name: inspecting-photo-archives
description: Inspecciona carpetas de fotos y videos viejos (importados de CDs, DVDs o discos externos) y produce un reporte de metadata para poder importarlos con criterio. Reporta fecha de captura, cámara, zona horaria, fechas perdidas en la copia y formatos en riesgo. Es de solo lectura, nunca modifica los archivos. Usar cuando el usuario mencione fotos de CDs, fotos viejas o escaneadas, metadata o EXIF, fotos sin fecha o desordenadas, revisar o auditar una carpeta de fotos antes de importarla, o pregunte qué cámara/fecha tiene una foto. También para "check my old photos", "EXIF report", "photos have no date".
---

# Inspeccionar archivos de fotos viejas

Produce un reporte que permita importar fotos viejas **con criterio**: qué hay, qué
metadata tiene, qué se perdió al copiarlas del CD, y qué formatos conviene mirar.

> **Regla dura: este skill es de SOLO LECTURA.** Nunca modificar, mover, renombrar ni
> convertir un archivo del archivo original. Si el usuario pide convertir, decir que
> eso es otro skill (`optimizing-legacy-media`) y que primero hay que aprobar este
> reporte. Los originales son irreemplazables.

Copiá esta checklist y marcá a medida que avanzás:

```
- [ ] Paso 0: preflight de dependencias
- [ ] Paso 1: escanear metadata (read-only)
- [ ] Paso 2: resumir a formato compacto
- [ ] Paso 3: juzgar formatos en riesgo (con ffprobe)
- [ ] Paso 4: inferir fechas desde nombres (delegado + QA)
- [ ] Paso 5: preguntar fechas estimadas al usuario
- [ ] Paso 6: emitir reporte JSON + markdown
```

## Paso 0 — Preflight de dependencias

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/check_deps.sh"
```

Sale con código 3 y un `install_command` si falta algo. Si falta:

1. Decile al usuario **qué** falta y **para qué** sirve (`exiftool` = leer metadata de
   fotos y video; `ffmpeg`/`ffprobe` = identificar el códec real adentro de un video).
2. **Pedí confirmación explícita antes de instalar** — instalar cambia su sistema.
3. Con el OK: `brew install <lo que falte>`.

**Sin el OK, los dos no degradan igual:**

| Falta | Consecuencia |
|---|---|
| `exiftool` | **Bloqueante.** `scan_archive.sh` sale con código 2 — no hay escaneo posible. Decilo y frená; no hay modo reducido. |
| `ffprobe` | **Degradable.** Todo corre salvo el Paso 3: los videos quedan **sin clasificar** (el contenedor no alcanza). Seguí y marcá en el reporte qué videos quedaron sin verificar. |

Estas dependencias son de **capa skill**, no de host: se declaran acá y las chequea
`check_deps.sh`. **No van a `INSTALL.md`.**

## Paso 1 — Escanear (read-only)

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/scan_archive.sh" "<carpeta>" "<salida>/raw-scan.json"
```

`<salida>` = `~/Documents/photo-archive-reports/<scope>/<YYYY-MM-DD>/`, donde `<scope>`
es el nombre de la carpeta o del CD. Cada corrida crea su carpeta con fecha; las
anteriores se conservan.

**No leas `raw-scan.json` entero en la conversación** — el escaneo de un CD entero
puede ser de megabytes. Para eso está el paso 2.

## Paso 2 — Resumir

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/summarize_scan.py" \
  "<salida>/raw-scan.json" "<salida>/summary.json"
```

Leé `summary.json`. Trae, por carpeta: cantidad, rango de años, cámaras, formatos, y
el conteo de estos flags con ejemplos:

| Flag | Qué significa |
|---|---|
| `no_capture_date` | Sin `DateTimeOriginal` ni `CreateDate` — no se sabe cuándo se tomó |
| `impossible_date` | Año < 1990 o futuro — pila de la cámara muerta, reloj reseteado |
| `placeholder_time` | Fecha real pero hora `00:00:00` — la cámara grabó el día, no el reloj. **El día sirve, la hora no** |
| `identical_timestamps` | Toda la carpeta comparte un timestamp — no se puede saber el orden interno |
| `filedate_mismatch` | La fecha EXIF y la del archivo difieren > 1 año — **la fecha se perdió al copiar del CD** |
| `tz_missing` | Sin offset de zona horaria (lo normal en cámaras viejas) |
| `tz_not_bogota` | Offset presente pero ≠ `-05:00` — foto de viaje, o cámara nunca reconfigurada |
| `legacy_container` | `.avi`, `.wmv`, `.mpg`, `.bmp`… — candidato a revisar, **no** a convertir todavía |

Para consultar registros puntuales sin cargar todo, usá `jq` sobre el raw:

```bash
jq '.[] | select(.FileName=="IMG_0042.JPG")' "<salida>/raw-scan.json"
```

## Paso 3 — Juzgar formatos en riesgo

**Leé `reference/format-risk.md` antes de clasificar nada.** Contiene el criterio y la
razón por la que este juicio no se delega.

> **El conocimiento vive en el KB.** La base **`media-formats`** se construyó el 2026-07-23
> con fuentes reales (Library of Congress, PRONOM, FADGI, FFmpeg, Mozilla mozjpeg) más una
> medición `tier: proven` en esta máquina. `reference/format-risk.md` quedó como **puntero +
> regla operativa**; el conocimiento de formatos se lee de:
> `~/dev/claude-kb/media-formats/video-codecs.md` (códecs y cómo identificarlos),
> `image-formats.md` (imagen y operaciones sin pérdida) y `preservation-doctrine.md`
> (doctrina y formatos objetivo). Todo `tier: advisory` salvo lo marcado `proven`.
>
> **Corrección que cambia el reporte:** la versión anterior decía que Indeo "no abre en nada
> moderno" — **falso**. `ffmpeg` decodifica todos los códecs legacy medidos. Distinguí
> siempre **"no abre por doble clic"** (incomodidad) de **"no se puede decodificar"**
> (pérdida real). Hoy casi todo cae en el primer caso, y **la urgencia real es el CD físico,
> no el códec**.

Regla central: **el contenedor no decide la compatibilidad, el códec adentro sí.** Para
cada entrada de `videos_to_probe` en el summary, corré `ffprobe` (comando exacto en la
referencia) y recién ahí clasificá alto/medio/bajo con la razón concreta.

Nunca recomiendes re-comprimir un JPEG: es pérdida sin ganancia.

## Paso 4 — Inferir fechas desde nombres (subtarea delegable)

Para los `date_hint_candidates` del summary (archivos sin fecha de captura), el nombre
del archivo y de la carpeta suelen tener la pista (`Cartagena 2004`, `IMG_20030714`,
`Navidad 99`). Extraer campos de texto sucio es **voluminoso y simple en razonamiento**:
es delegable hacia un modelo local.

- El mapa tarea→wrapper→modelo es **`~/dev/claude-kb/delegation.md`** (runtime: skill
  `/delegate`). No hardcodees IDs de modelos acá; se eligen según `hardware.md`.
- **Usá el prompt canónico de [reference/delegable-prompts.md](reference/delegable-prompts.md)**
  — está afinado con `prompt-master` y endurecido contra un fallo medido (un modelo chico
  respondió pidiendo aclaraciones en vez de JSON). No lo reescribas a ojo. Sustituí
  `{{CURRENT_YEAR}}` y `{{BATCH_JSON}}`, en lotes de ~40 items.
- **Fallback:** si el wrapper sale con código ≠ 0, hacelo vos. Nunca falles la tarea por eso.

> **QA de lo delegado (obligatorio):** toda salida que venga de un modelo delegado hacia
> abajo se verifica antes de usarse. Los 6 chequeos exactos están en
> [reference/delegable-prompts.md](reference/delegable-prompts.md) — incluido el
> **spot-check de 3–5 casos**, que es el único que atrapa fechas inventadas (los demás solo
> validan la forma). Si no pasa, se re-hace un tier más arriba. No asumas que otro ya revisó.

Toda fecha inferida entra al reporte marcada como **inferida**, nunca como dato duro.

## Paso 5 — Preguntar fechas estimadas

Donde no haya ni EXIF ni pista utilizable, preguntá al usuario **por carpeta** (no por
archivo) una fecha estimada, mostrándole el contexto que ya tenés: nombre de la carpeta,
cantidad de fotos, cámaras detectadas, rango de años de las vecinas. Ofrecé "no sé" como
opción válida — una carpeta sin fecha es un resultado legítimo.

## Paso 6 — Emitir el reporte

Escribí en `<salida>/`:

- **`report.json`** — estructurado, para que lo consuma otro paso o skill.
- **`report.md`** — legible, para decidir. Por carpeta: qué hay, rango de fechas, cámaras,
  qué está mal, formatos a mirar, y **qué acción sugerida** (sin ejecutarla).

Cerrá con un resumen de una frase: cuántos archivos, cuántos sin fecha confiable, cuántos
formatos en riesgo, y cuál es el siguiente paso concreto.

## Alcance

Este skill **inspecciona y reporta**. No convierte, no renombra, no mueve, no importa.
Si aparece otra tarea, decilo y frená — no amplíes por iniciativa propia.

**Si disparás un subagente** (p. ej. para escanear un árbol muy grande en contexto aislado):
lleva **un solo alcance**, corre en su propio contexto y devuelve **resultado o
`FUERA DE ALCANCE`**. Nunca amplía por iniciativa propia. Un alcance por subagente: si
aparece una segunda tarea, abrí otro. Eso es lo que hace barata la QA del que lo llamó.

## Estado de verificación

| Nivel | Estado |
|---|---|
| **0 — estructural** (`quick_validate`) | ✅ pasa (`Skill is valid!`) |
| **1 — disparo** (eval de `description`) | ✅ **12/13** con `haiku` — ver `evals/results-2026-07-23.md` |
| **Funcional end-to-end** | ⏳ **pendiente** — nunca corrió sobre un archivo real |

Medido el 2026-07-23: **negativos 5/5** (incluido el vecino cercano "convertí este AVI a MP4",
que es `optimizing-legacy-media`), positivos 7/8. El único fallo se re-corrió y resultó
**varianza de muestreo, no un hueco**: la cadena idéntica disparó 2 de 3 veces. La
`description` no se cambió.

**`run_eval.py` de `skill-creator` NO sirve para medir este skill:** crea un command temporal
que compite con el skill real ya instalado globalmente y reporta 0 en todo. El método que sí
funciona está documentado en `evals/results-2026-07-23.md`.
