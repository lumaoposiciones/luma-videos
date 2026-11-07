# Cómo se prepara cada vídeo de LuMa Oposiciones

Cuenta: maestro de Primaria con plaza y ex-tribunal de oposición en la Comunitat Valenciana.
Público: opositores a Maestro de Primaria (C. Valenciana). Tono: cercano, directo, de "te lo cuento desde el otro lado de la mesa".

## Calendario
Publicaciones en TikTok + Instagram (Reel): lunes, miércoles y viernes a las 20:00 y domingos a las 11:00 (Europe/Madrid).
La tarea se ejecuta la víspera y deja la publicación de Instagram PROGRAMADA en Metricool con publicación automática (desde el 07/11/2026, por decisión del usuario; ya no hace falta que la apruebe). Avisa al usuario de lo que se ha programado por si quiere cambiar algo antes de la hora.
TikTok (desde el 05/11/2026): NO se crea nada en Metricool para TikTok. El PC del usuario sube solo el vídeo de `videos/` a la bandeja de TikTok como borrador (tarea de Windows "LuMa TikTok borradores", entre las 17:00 y las 23:00 de la víspera) y el usuario lo publica desde la app con el texto de `guiones/<slug>.txt`. Por eso el nombre del vídeo DEBE empezar por la fecha de publicación (`AAAA-MM-DD-...mp4`).

## Pasos de cada ejecución
0. **Antes de nada, comprueba Metricool** (marca 7793390, getScheduledPosts) para la fecha de publicación que toca: si ya hay un post (borrador o programado) ese día, NO crees otro; limítate a avisar al usuario para que lo revise y termina.
1. `git pull`. Mira `temas.md`: coge el primer tema sin marcar. Calcula la fecha de publicación (el siguiente lunes/miércoles/viernes/domingo) y el slug `AAAA-MM-DD-tema-corto`.
2. Escribe `guiones/<slug>.json` (formato en `tools/make_video.py`; ejemplo: `guiones/2026-11-04-dua.json`):
   - 5-7 escenas; la primera con `recuadro` = gancho en MAYÚSCULAS con pregunta; la última con `recuadro` = "LA CLAVE PARA EL TRIBUNAL" y la voz terminando en "¡Sígueme!".
   - Voz total ≤ 400 caracteres (el script corta en 450). Frases cortas.
   - `portada`: 1-3 líneas cortas (≤ 16 caracteres por línea idealmente), el tema en 2-4 palabras.
   - Contenido correcto y prudente: nada de cifras, artículos o fechas de normativa de los que no estés seguro. Mejor un consejo práctico que un dato dudoso.
3. Fotos: para cada escena busca con `python3 tools/buscar_fotos.py "<búsqueda en inglés>" /tmp/fN.jpg`, MIRA la hoja y elige fotos realistas que encajen (aula, mesa de estudio, materiales, docente…). Evita: fotos recortadas sobre fondo liso, Navidad u otras fiestas fuera de temporada, adultos en contextos no educativos, contenido raro. Pon el id en `foto_id`.
4. `python3 tools/make_video.py guiones/<slug>.json` y MIRA `/tmp/luma_<slug>/control.jpg`. Si una foto no encaja o un texto se sale, corrige y vuelve a ejecutar (la voz se reutiliza si no cambia el texto).
5. Escribe la descripción en `guiones/<slug>.txt` con el estilo de `guiones/2026-11-04-dua.txt`: título con 2 emojis, problema común, 3-5 puntos con emoji + número, "🔑 El truco de 10: …", "📌 Guarda este post para …", y estos hashtags (cambia el 3.º por uno del tema):
   `#oposicionesvalencia #oposicionesmaestros #<tema> #lumaoposiciones #tribunaldeoposiciones #opofamily #oposiciones2026 #programaciondidactica`
6. Marca el tema en `temas.md` como `- [x] AAAA-MM-DD · tema`. Si quedan menos de 4 temas, añade 8 nuevos al final (variados: programación, SdA, evaluación, DUA/inclusión, exposición oral, supuesto práctico, organización del estudio).
7. `git add -A && git commit && git push`. Comprueba que `https://raw.githubusercontent.com/lumaoposiciones/luma-videos/main/videos/<slug>.mp4` responde 200.
8. Metricool (marca 7793390): createScheduledPost con `draft: false` y `autoPublish: true` (publicación automática; decisión del usuario del 07/11/2026), providers **solo instagram** (TikTok NO va por Metricool), media = enlace raw del vídeo, `videoThumbnailUrl` = enlace raw de `portadas/<slug>.jpg`, text = descripción, `instagramData: {type: "REEL", showReelOnFeed: true, isAiGenerated: true}`.
