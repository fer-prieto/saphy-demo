# Studio Saphy — demo del sitio

Demo estática del sitio de **Studio Saphy** (estudio de arquitectura, Cusco, Perú).
Sin dependencias, sin build, sin servidor: HTML + CSS + JS plano y archivos WebP.

## Ver en local

```bash
cd ~/freelance/saphy/demo
python3 -m http.server 8000
# abrir http://127.0.0.1:8000
```

También funciona abriendo `index.html` con doble clic, porque los datos de los proyectos
están horneados en `js/data.js` (no se usa `fetch`).

## Estructura

```
index.html          portada: hero, grilla de proyectos, estudio, contacto
proyecto.html       ficha: ?p=<slug>
css/main.css        todos los estilos
js/main.js          filtro de la grilla y render de la ficha
js/data.js          GENERADO — no editar a mano
data/projects.json  fuente de verdad de los proyectos
assets/img/         renders en WebP, dos anchos (640 y 1280)
tools/build_images.py   regenera js/data.js y los WebP desde el PDF
```

## Proyectos

10 proyectos en 4 categorías, extraídos de `~/freelance/saphy/docs/saphy.pdf`:

| slug | nombre | categoría |
|---|---|---|
| `ccoricancha` | Vivienda Ccoricancha | Vivienda |
| `willka-wasi` | Willka Wasi | Vivienda |
| `casa-pacha` | Casa Pacha | Vivienda |
| `kimsa` | Kimsa | Vivienda |
| `cabana-antara` | Cabañas Antara | Vivienda |
| `airbnb-la-florida` | Airbnb La Florida | Interiorismo |
| `residencias-alpinas` | Residencias Alpinas | Paisajismo |
| `parque-urbano` | Parque Urbano | Parques & Condominios |
| `centro-deportes-aventura` | Centro de Deportes de Aventura | Parques & Condominios |
| `club-campestre-aronna` | Club Campestre Aronna | Parques & Condominios |

## Reemplazar o agregar un render

1. Exportar el render a JPG o PNG, idealmente ~1280 px de ancho.
2. Guardarlo en `assets/img/<slug>/`.
3. Agregar la entrada en `data/projects.json`:

```json
{ "src": "assets/img/kimsa/kimsa-04-1280.webp", "src640": "assets/img/kimsa/kimsa-04-640.webp",
  "w": 1280, "h": 720 }
```

4. Regenerar `js/data.js`:

```bash
python3 -c "import json;d=json.load(open('data/projects.json'));open('js/data.js','w').write('window.PROJECTS = '+json.dumps(d,ensure_ascii=False,indent=2)+';\n')"
```

## Regenerar todo desde el PDF

```bash
python3 tools/build_images.py
```

Extrae las imágenes de cada página del portafolio, las convierte a WebP (640 y 1280) y
reescribe `data/projects.json` y `js/data.js`.

> **Nota técnica:** los renders del PDF son JPEG en CMYK de Adobe, con los canales
> invertidos. Extraerlos con `pdfimages -all` y convertirlos directo produce colores en
> negativo (violeta). Por eso el script usa `pdfimages -png`, que hace la conversión
> CMYK→RGB correctamente. No cambiar a `-all` ni a JPG.

## Desplegar

Se despliega **solo esta carpeta** (`demo/`), nunca `~/freelance/saphy/`: ahí está el
portafolio del cliente (`docs/saphy.pdf`, 16 MB) y no debe quedar público.

Todas las rutas son relativas, así que el sitio funciona igual en la raíz de un dominio
que en un subdirectorio (`usuario.github.io/repo/`).

### GitHub Pages

```bash
cd ~/freelance/saphy/demo
git init -b main
git add .
git commit -m "Demo del sitio de Studio Saphy"
git remote add origin git@github.com:<usuario>/saphy-web.git
git push -u origin main
```

Luego, en el repositorio: **Settings → Pages → Source: Deploy from a branch →
Branch: `main` / `(root)` → Save**. Queda en `https://<usuario>.github.io/saphy-web/`
en uno o dos minutos.

Requiere repositorio **público** (Pages gratuito no sirve con repos privados).

### Vercel

Con el repositorio ya en GitHub: entrar a vercel.com → **Add New → Project** → importar
el repo → Framework Preset **Other**, sin build command y sin output directory →
**Deploy**. Queda en `https://<proyecto>.vercel.app`.

El CLI (`npx vercel --prod`) también sirve, pero en esta máquina no hay Node instalado.

### Dominio propio

En ambos casos se agrega desde el panel del proveedor (Vercel: Settings → Domains;
GitHub Pages: Settings → Pages → Custom domain). El HTTPS es automático.

## Pendiente del cliente

Estas erratas están en el portafolio original. El sitio ya las corrige; conviene que el
estudio lo sepa:

| Original | Corregido |
|---|---|
| "a tráves de la arquitectura" | "a través" |
| "innovación aquitectónica" | "arquitectónica" |
| "la estructura minimaza" | "minimiza" |
| "los huespedes" | "huéspedes" |
| "inspiradas en las construcción inca" | "las construcciones incas" |

Además:

- El correo del portafolio era `arq.studiosapy@gmail.com` (sin la **h** de Saphy). El
  sitio usa `gerencia@studiosaphy.com` por indicación del cliente.
- La descripción de **Vivienda Ccoricancha** termina cortada en el portafolio original
  ("…donde las ideas florecen, las"). Falta el final del texto.
- **Parque Urbano** no tiene descripción en el portafolio; se usó su propio título como
  texto provisional.

## Fuera de alcance en esta demo

Visualización 3D interactiva, panel de administración, dominio, correos. La demo usa los
renders del portafolio; no se produce material nuevo.
