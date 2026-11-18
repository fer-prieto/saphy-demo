#!/usr/bin/env python3
"""A1 — Extrae los renders del portafolio PDF y construye data/projects.json.

Los JPEG del PDF son CMYK de Adobe (canales invertidos): si se extraen con
`pdfimages -all` y se convierten directo, los colores salen en negativo. Por eso
se extrae a PNG (poppler hace la conversión CMYK->RGB correctamente).

Uso:  python3 build_images.py
Salida:  ~/freelance/saphy/demo/assets/img/<slug>/*.webp
         ~/freelance/saphy/demo/data/projects.json
         ~/freelance/saphy/demo/js/data.js
"""
import json
import os
import re
import shutil
import subprocess
import sys

PDF = os.path.expanduser("~/freelance/saphy/docs/saphy.pdf")
DEMO = os.path.expanduser("~/freelance/saphy/demo")
WORK = "/tmp/a1/work"

# Erratas del portafolio original corregidas en el sitio (ver README).
CORRECCIONES = {
    "tráves": "través",
    "aquitectónica": "arquitectónica",
    "minimaza": "minimiza",
    "huespedes": "huéspedes",
    "las construcción inca": "las construcciones incas",
}

# slug, nombre, categoría, páginas del PDF que lo contienen
PROJECTS = [
    ("ccoricancha",              "Vivienda Ccoricancha",           "Vivienda",              [5]),
    ("willka-wasi",              "Willka Wasi",                    "Vivienda",              [6]),
    ("casa-pacha",               "Casa Pacha",                     "Vivienda",              [7]),
    ("kimsa",                    "Kimsa",                          "Vivienda",              [8]),
    ("cabana-antara",            "Cabañas Antara",                 "Vivienda",              [9]),
    ("airbnb-la-florida",        "Airbnb La Florida",              "Interiorismo",          [11]),
    ("residencias-alpinas",      "Residencias Alpinas",            "Paisajismo",            [13, 14]),
    ("parque-urbano",            "Parque Urbano",                  "Parques & Condominios", [16]),
    ("centro-deportes-aventura", "Centro de Deportes de Aventura", "Parques & Condominios", [17, 18]),
    ("club-campestre-aronna",    "Club Campestre Aronna",          "Parques & Condominios", [19]),
]

MAX_BYTES = 256_000  # 250 KB


def ffprobe_dims(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height,pix_fmt", "-of", "csv=p=0", path],
        capture_output=True, text=True, check=True).stdout.strip().splitlines()[0]
    w, h, pix = out.split(",")[:3]
    return int(w), int(h), pix


def extraer_pagina(pagina, destino):
    """Extrae las imágenes de una página como PNG RGB. Devuelve [(ruta, w, h)]."""
    if os.path.isdir(destino):
        shutil.rmtree(destino)
    os.makedirs(destino, exist_ok=True)
    subprocess.run(["pdfimages", "-png", "-f", str(pagina), "-l", str(pagina),
                    PDF, os.path.join(destino, "p")], check=True)
    imgs = []
    for nombre in sorted(os.listdir(destino)):
        ruta = os.path.join(destino, nombre)
        w, h, pix = ffprobe_dims(ruta)
        if pix != "rgb24":      # máscaras alfa y duplicados grises: fuera
            os.remove(ruta)
            continue
        if w < 300 or h < 200:  # miniaturas del sumario / recortes
            os.remove(ruta)
            continue
        imgs.append((ruta, w, h))
    return imgs


def convertir(src, slug, k, ancho):
    out = os.path.join(DEMO, "assets/img", slug, f"{slug}-{k:02d}-{ancho}.webp")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    base = 78 if ancho > 640 else 76
    for q in (base, base - 8, base - 16, base - 24):
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src,
                        "-vf", f"scale='min({ancho},iw)':-2",
                        "-c:v", "libwebp", "-quality", str(q),
                        "-compression_level", "6", out], check=True)
        if os.path.getsize(out) <= MAX_BYTES:
            break
    return os.path.getsize(out)


def es_titulo(linea):
    s = linea.strip()
    if not s or s.isdigit():
        return True
    letras = [c for c in s if c.isalpha()]
    return bool(letras) and all(c.isupper() for c in letras)


def descripcion(paginas):
    partes, titulos = [], []
    for p in paginas:
        txt = subprocess.run(["pdftotext", "-f", str(p), "-l", str(p), PDF, "-"],
                             capture_output=True, text=True, check=True).stdout
        cuerpo = []
        for linea in txt.splitlines():
            if not linea.strip():
                continue
            if es_titulo(linea):
                if not linea.strip().isdigit():
                    titulos.append(linea.strip())
            else:
                cuerpo.append(linea.strip())
        if cuerpo:
            partes.append(" ".join(cuerpo))
    texto = re.sub(r"\s+", " ", " ".join(partes)).strip()
    if not texto:
        vistos, unicos = set(), []
        for t in titulos:
            if t not in vistos:
                vistos.add(t)
                unicos.append(t)
        texto = " ".join(unicos).capitalize().rstrip(".") + "."
    texto = re.sub(r"\s+", " ", texto)
    for mal, bien in CORRECCIONES.items():
        texto = texto.replace(mal, bien)
    return texto


def main():
    if not os.path.exists(PDF):
        sys.exit(f"No existe el PDF: {PDF}")
    os.makedirs(WORK, exist_ok=True)
    data, total, n = [], 0, 0

    # Portada del sitio = imagen de la página 2 (apertura del portafolio)
    print("hero")
    hero = extraer_pagina(2, os.path.join(WORK, "p2"))
    if not hero:
        sys.exit("No se encontró imagen de portada en la página 2")
    src, w, h = max(hero, key=lambda t: t[1] * t[2])
    for ancho in (1600, 800):
        total += convertir(src, "hero", 1, ancho)
        n += 1
    print(f"  hero {w}x{h}")

    for slug, nombre, categoria, paginas in PROJECTS:
        imgs = []
        for p in paginas:
            imgs += extraer_pagina(p, os.path.join(WORK, f"p{p}"))
        if not imgs:
            sys.exit(f"Sin imágenes para {slug} (páginas {paginas})")

        entradas = []
        for k, (ruta, w, h) in enumerate(imgs, 1):
            for ancho in (1280, 640):
                total += convertir(ruta, slug, k, ancho)
                n += 1
            pw, ph, _ = ffprobe_dims(os.path.join(
                DEMO, f"assets/img/{slug}/{slug}-{k:02d}-1280.webp"))
            entradas.append({
                "src": f"assets/img/{slug}/{slug}-{k:02d}-1280.webp",
                "src640": f"assets/img/{slug}/{slug}-{k:02d}-640.webp",
                "w": pw, "h": ph,
            })

        # Portada de la tarjeta: la imagen apaisada más grande; si no hay, la mayor.
        apaisadas = [i for i in entradas if i["w"] / i["h"] >= 1.15]
        portada = max(apaisadas or entradas, key=lambda i: i["w"] * i["h"])

        data.append({
            "slug": slug,
            "nombre": nombre,
            "categoria": categoria,
            "descripcion": descripcion(paginas),
            "portada": portada["src"],
            "portada640": portada["src640"],
            "portada_w": portada["w"],
            "portada_h": portada["h"],
            "imagenes": entradas,
        })
        print(f"{slug:26s} {len(entradas):2d} imgs  portada {portada['w']}x{portada['h']}")

    os.makedirs(f"{DEMO}/data", exist_ok=True)
    with open(f"{DEMO}/data/projects.json", "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    os.makedirs(f"{DEMO}/js", exist_ok=True)
    with open(f"{DEMO}/js/data.js", "w") as f:
        f.write("window.PROJECTS = ")
        f.write(json.dumps(data, ensure_ascii=False, indent=2))
        f.write(";\n")

    print(f"\n{len(data)} proyectos, {n} webp, {total / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main()
