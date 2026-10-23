# Riesgo de formato — puntero al KB + regla operativa del skill

> **El conocimiento vive en el KB, no acá.** Desde el 2026-07-23 existe la base
> `media-formats`, construida con fuentes reales y provenance. Leé de ahí:
>
> | Para | Archivo |
> |---|---|
> | Doctrina y formatos objetivo | `~/dev/claude-kb/media-formats/preservation-doctrine.md` |
> | Códecs de video legacy y cómo identificarlos | `~/dev/claude-kb/media-formats/video-codecs.md` |
> | Formatos de imagen y operaciones sin pérdida | `~/dev/claude-kb/media-formats/image-formats.md` |
>
> Fuentes: Library of Congress, PRONOM, FADGI, FFmpeg, Mozilla mozjpeg + una medición
> `tier: proven` en esta máquina.

## Corrección importante (2026-07-23)

La versión anterior de este archivo estaba **escrita de memoria, sin fuentes**, y afirmaba
que Indeo "no abre en nada moderno". **Es falso.** Medido en esta máquina: `ffmpeg` 8.1.2
decodifica `indeo2/3/4/5`, `cinepak`, `svq1`, `svq3`, `msmpeg4v1/v2/v3`, `msrle`,
`msvideo1`, `rpza`, `mjpegb`, `dvvideo`, `wmv1/2/3` y `vc1`.

La distinción correcta, y la que hay que usar al reportar:

- **"No abre en el reproductor del sistema"** (QuickTime Player, Fotos, Vista Previa) →
  incomodidad. Es el caso de casi todos los códecs legacy.
- **"No se puede decodificar"** → pérdida real. Hoy no aplica a ninguno de los de arriba.

Confundirlas convierte un problema de comodidad en una urgencia falsa. **La urgencia real de
un archivo familiar es la degradación del CD físico, no la del códec.**

## Regla operativa de este skill (no delegable)

**El contenedor no decide la compatibilidad. El códec adentro sí.** Un `.avi` puede tener
MJPEG (abre bien) o Indeo (no abre por doble clic). Nunca clasifiques por extensión:

```bash
ffprobe -v error -select_streams v:0 \
  -show_entries stream=codec_name,codec_long_name,width,height \
  -show_entries format=format_name,duration -of json "<archivo>"
```

**Este juicio se queda en Claude, no se delega.** Medido el 2026-07-23: `qwen3.5-9b` tardó
168 s clasificando riesgo de formato y erró 2 de 4, incluyendo inventar que "Apple deprecó
QuickTime en 2017". Parece mecánico, pero exige conocimiento del mundo. Ver `/delegate`.

## Cómo reportar (no decidir por el usuario)

Para cada candidato:
1. **Qué es** — contenedor + códec real de `ffprobe`, no la extensión.
2. **Cuál de los dos problemas tiene** — no abre por doble clic, o no se decodifica.
3. **Qué se ganaría y qué se perdería** al convertir.
4. **Recomendación, sin ejecutarla** — este skill es read-only.

> **Nunca recomiendes re-comprimir un JPEG.** Es pérdida sin ganancia. Si hay que optimizar,
> `jpegtran` es sin pérdida (opera sobre coeficientes DCT); `cjpeg` re-codifica y degrada.
> Detalle y citas en `image-formats.md` del KB.
