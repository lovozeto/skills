# Prompts canónicos de subtareas delegadas

Prompts afinados con `prompt-master` para modelos **locales chicos** (Apple `fm`,
`gemma-4-e4b`, `qwen3.5-9b`). No los reescribas a ojo: están endurecidos contra un fallo
medido.

> **Fallo medido (2026-07-23):** con un prompt no optimizado, `gemma-4-e4b` respondió
> *pidiendo aclaraciones* en vez de devolver JSON. Por eso el lock de salida va en las
> primeras líneas y la estructura es plana — los modelos abiertos chicos pierden coherencia
> con instrucciones anidadas.

---

## 1. Extracción de pistas de fecha desde nombres

**Cuándo:** para los `date_hint_candidates` de `summary.json` (archivos sin fecha EXIF).
**Ruteo:** según `~/dev/claude-kb/delegation.md` (extraer campos de un texto → local).
**Sustituciones antes de enviar:** `{{CURRENT_YEAR}}` y `{{BATCH_JSON}}`.

```text
You extract dates from photo file names and folder names. You output JSON only.

NEVER ask questions. NEVER explain. NEVER add text before or after the JSON. NEVER emit
reasoning tags. Output the JSON array and nothing else.

Output exactly this shape, one object per input item, in the same order:
[{"file":"<file>","date_hint_iso":"YYYY"|"YYYY-MM"|"YYYY-MM-DD"|null,"confidence":"high"|"medium"|"low","source":"filename"|"folder"|"none"}]

Rules:
- Read BOTH the file name and the folder name. Use whichever suggests a date.
- Year only -> "2004". Year and month -> "2001-09". Full date -> "2003-07-14".
- A 2-digit year like 99 or '99 means 1999. 00 to 09 mean 2000 to 2009.
- Valid years are 1990 to {{CURRENT_YEAR}}. Outside that range, treat it as no hint.
- If the text suggests NO date: date_hint_iso null, confidence "low", source "none".
  NEVER guess a date that is not written in the text.
- source is "filename" if the hint came from the file name, "folder" if from the folder.
- confidence: "high" for an explicit full date or year+month, "medium" for a bare year,
  "low" when absent or uncertain.

Examples:

Input: [{"file":"IMG_20030714.JPG","folder":"CD1"}]
Output: [{"file":"IMG_20030714.JPG","date_hint_iso":"2003-07-14","confidence":"high","source":"filename"}]

Input: [{"file":"P1010023.JPG","folder":"Vacaciones Cartagena 2004"}]
Output: [{"file":"P1010023.JPG","date_hint_iso":"2004","confidence":"medium","source":"folder"}]

Input: [{"file":"foto12.jpg","folder":"Navidad 99"}]
Output: [{"file":"foto12.jpg","date_hint_iso":"1999","confidence":"medium","source":"folder"}]

Input: [{"file":"DSC00123.JPG","folder":"CD backup"}]
Output: [{"file":"DSC00123.JPG","date_hint_iso":null,"confidence":"low","source":"none"}]

Input: [{"file":"escaneo5.jpg","folder":"fotos mama sept 2001"}]
Output: [{"file":"escaneo5.jpg","date_hint_iso":"2001-09","confidence":"high","source":"folder"}]

Now process this input. Output only the JSON array.

Input: {{BATCH_JSON}}
```

### QA de esta salida (obligatorio antes de usarla)

1. Parsea como JSON y es un array del **mismo largo y orden** que el lote enviado.
2. Cada `date_hint_iso` es `null` o matchea `^\d{4}(-\d{2}(-\d{2})?)?$`.
3. Cada año está entre `1990` y el año actual.
4. `confidence` ∈ {high, medium, low}; `source` ∈ {filename, folder, none}.
5. Cuando `date_hint_iso` es `null`, `source` **debe** ser `none`.
6. **Spot-check de 3–5 casos** contra el nombre real: ¿la fecha está de verdad en el texto?
   Este paso es el que atrapa fechas inventadas — los otros solo validan la forma.

Si algo falla, re-hacer **un tier más arriba** (ver `delegation.md`). Nunca uses una salida
que no pasó.

### Lotes

Mandá de a **~40 items** por llamada. Más largo degrada la adherencia al formato en modelos
chicos; más corto desperdicia el overhead de coordinación.
