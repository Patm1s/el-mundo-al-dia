# 🌍 El Mundo al Día

Periódico familiar estático en español, accesible desde el celular. Sin servidor, base de datos ni mantenimiento de infraestructura.

## Publicar gratis en GitHub Pages

1. Crea una cuenta en https://github.com y un repositorio **público** llamado `el-mundo-al-dia`.
2. Descomprime este ZIP y sube **todos los archivos y carpetas**, incluida `.github/workflows/daily.yml`, a la raíz del repositorio. Puedes usar **Add file → Upload files**; comprueba que la carpeta `.github` también se haya subido.
3. En el repositorio, abre **Settings → Pages → Build and deployment → Source: Deploy from a branch**. Selecciona `main` y `/(root)`, y guarda.
4. En unos minutos, la dirección será `https://TU-USUARIO.github.io/el-mundo-al-dia/` (sustituye TU-USUARIO). Puedes compartirla por WhatsApp.
5. Para activar la redacción automática, crea una clave de API en https://platform.openai.com/api-keys . La API tiene **facturación independiente de ChatGPT**; configura un límite de gasto.
6. En GitHub: **Settings → Secrets and variables → Actions → New repository secret**. Nombre exacto: `OPENAI_API_KEY`. Pega la clave **solo allí**, nunca en el código ni en el sitio público.
7. Abre **Actions → Actualizar noticias diariamente → Run workflow** para probar. La edición nueva aparecerá después del commit y la publicación de GitHub Pages.

## Qué hace

- Cada mañana intenta ejecutar la actualización a las **08:00, hora de Austria**, con ajuste de horario de verano/invierno.
- Recoge titulares recientes mediante Google News RSS por categoría y utiliza la API de OpenAI para seleccionar y redactar **resúmenes prudentes basados solo en titulares**.
- Conserva las ediciones anteriores y no reemplaza la última edición si falla la actualización.
- Los enlaces llevan a los resultados originales de Google News, que pueden redirigir a los medios de comunicación.
- Diseño responsive, letra grande y sección Perú.

## Limitaciones importantes

- **No es verificación periodística completa.** Los RSS no incluyen necesariamente los textos de los artículos; el modelo no puede comprobar por sí solo la exactitud de un titular ni verificar independientemente declaraciones. El sitio señala esta limitación. Para una publicación editorial realmente verificada hay que integrar fuentes de texto completo autorizadas, contrastar varias fuentes y/o revisión humana.
- Los feeds pueden fallar, cambiar o incluir duplicados. Las tareas programadas de GitHub Actions pueden retrasarse u omitirse. La página muestra la fecha real de la última edición publicada.
- No garantiza 7–10 noticias si no hay material suficiente. En ese caso puede publicar menos, o conservar la edición anterior.
- La publicación en un repositorio público deja visibles los textos de las ediciones. **Nunca** incluyas secretos en archivos del repositorio.
- La actualización consume tokens de la API de OpenAI (costo variable), aunque GitHub Pages suele ser gratuito para repositorios públicos dentro de sus límites de uso.
- El ejemplo inicial del 6/11/2026 está claramente marcado como **demostración** y no debe interpretarse como noticias reales.
- Si GitHub suspende el workflow por inactividad prolongada, reactívalo desde Actions.

## Archivos

- `index.html`: web completa.
- `data/manifest.json`: lista de ediciones.
- `data/YYYY-MM-DD.json`: noticias de cada día.
- `update.py`: descarga titulares y prepara la edición.
- `.github/workflows/daily.yml`: automatización diaria.

## Personalización

Cambia el nombre, colores o textos en `index.html`. Puedes configurar el modelo con la variable de entorno `OPENAI_MODEL` en el workflow. Para usar dominio propio, configúralo en GitHub Pages y en tu DNS.
