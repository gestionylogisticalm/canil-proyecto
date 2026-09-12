#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convierte los once renders 3D del anexo D en imágenes fotorrealistas.

Cada render de src/img/ se envía como referencia de composición junto al
prompt que le corresponde en docs/prompts-imagenes-fotorrealistas.md, de modo
que la imagen resultante conserve las proporciones reales del proyecto —la
hectárea, el baño de 16 m², el amarre de 12 × 3 m, la torre de 4 m— en vez de
inventarlas. El resultado se guarda como foto-<nombre>.png junto al render.

La clave se toma de la variable de entorno GEMINI_API_KEY. No se escribe en
ningún archivo del repositorio.

Uso:  python3 build/generar_fotos.py [nombre-del-render ...]
      python3 build/generar_fotos.py --modelos     (lista los modelos de imagen)
"""

import base64
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(RAIZ, "src", "img")
PROMPTS = os.path.join(RAIZ, "docs", "prompts-imagenes-fotorrealistas.md")
BASE = "https://generativelanguage.googleapis.com/v1beta"

# Preferencia de modelos, de mejor a peor para esta tarea. El primero que la
# cuenta tenga disponible y sepa devolver imágenes es el que se usa.
PREFERIDOS = [
    "gemini-3-pro-image",
    "gemini-2.5-flash-image",
    "gemini-2.0-flash-preview-image-generation",
    "gemini-2.0-flash-exp-image-generation",
]

INSTRUCCION = (
    "Convert this 3D render into a photorealistic photograph. Keep exactly the "
    "same composition, camera angle, and position of every element: the fence "
    "lines, the buildings, the water tower, the paths and the proportions of "
    "the site must not change. Only the realism of materials, lighting, "
    "vegetation and atmosphere should improve.\n\n"
)

ESTILO = (
    "\n\nPhotorealistic architectural photography, shot on a full-frame camera, "
    "24mm lens for wide views and 50mm for detail views, f/8, natural daylight, "
    "soft overcast light typical of southern Chile, subtle haze in the distance, "
    "realistic materials with visible wear, high dynamic range, no HDR halos, "
    "sharp focus throughout, 16:9 aspect ratio.\n\n"
    "Avoid: cartoon or illustration look, video game graphics, low poly geometry, "
    "plastic materials, oversaturated colours, fisheye distortion, warped fences, "
    "floating objects, distorted animals with extra limbs, garbled text, "
    "watermarks, deformed faces, tropical vegetation, palm trees, desert."
)


def clave():
    k = os.environ.get("GEMINI_API_KEY", "").strip()
    if not k:
        sys.exit("Falta GEMINI_API_KEY en el entorno.")
    return k


def pedir(url, cuerpo=None, intentos=4):
    """GET o POST contra la API, reintentando ante errores temporales."""
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    for n in range(intentos):
        req = urllib.request.Request(url, data=datos, method="POST" if datos else "GET")
        req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            detalle = e.read().decode("utf-8", "replace")[:400]
            if e.code in (429, 500, 502, 503, 504) and n < intentos - 1:
                espera = 2 ** (n + 1)
                print("     %d, reintento en %d s" % (e.code, espera))
                time.sleep(espera)
                continue
            raise SystemExit("HTTP %d\n%s" % (e.code, detalle))
        except urllib.error.URLError as e:
            if n < intentos - 1:
                time.sleep(2 ** (n + 1))
                continue
            raise SystemExit("Sin conexión con la API: %s" % e)


def modelos_de_imagen(k):
    r = pedir("%s/models?key=%s&pageSize=200" % (BASE, k))
    disponibles = []
    for m in r.get("models", []):
        nombre = m["name"].split("/")[-1]
        metodos = m.get("supportedGenerationMethods", [])
        if "generateContent" in metodos and "image" in nombre:
            disponibles.append(nombre)
    return disponibles


def elegir_modelo(k):
    disponibles = modelos_de_imagen(k)
    if not disponibles:
        sys.exit("La cuenta no tiene ningún modelo de generación de imágenes.")
    for p in PREFERIDOS:
        for d in disponibles:
            if d.startswith(p):
                return d, disponibles
    return disponibles[0], disponibles


def leer_prompts():
    t = io.open(PROMPTS, encoding="utf-8").read()
    b = re.findall(r"^## \d+ · (.+?)\n\nArchivo de referencia: `(.+?)`\n\n```\n(.*?)\n```",
                   t, re.S | re.M)
    if len(b) != 11:
        sys.exit("Se esperaban 11 prompts y se encontraron %d." % len(b))
    return [(titulo, archivo, re.sub(r"\s+", " ", prompt).strip())
            for titulo, archivo, prompt in b]


def generar(k, modelo, archivo, prompt):
    ruta = os.path.join(IMG, archivo)
    if not os.path.exists(ruta):
        sys.exit("No existe el render de referencia: %s" % ruta)
    referencia = base64.b64encode(open(ruta, "rb").read()).decode()
    cuerpo = {
        "contents": [{
            "role": "user",
            "parts": [
                {"inline_data": {"mime_type": "image/png", "data": referencia}},
                {"text": INSTRUCCION + prompt + ESTILO},
            ],
        }],
        "generationConfig": {"responseModalities": ["IMAGE"]},
    }
    r = pedir("%s/models/%s:generateContent?key=%s" % (BASE, modelo, k), cuerpo)

    candidatos = r.get("candidates") or []
    if not candidatos:
        motivo = json.dumps(r.get("promptFeedback", r))[:300]
        return None, "la API no devolvió candidatos: %s" % motivo
    for parte in candidatos[0].get("content", {}).get("parts", []):
        datos = parte.get("inlineData") or parte.get("inline_data")
        if datos and datos.get("data"):
            salida = os.path.join(IMG, "foto-" + archivo)
            open(salida, "wb").write(base64.b64decode(datos["data"]))
            return salida, None
    razon = candidatos[0].get("finishReason", "sin imagen en la respuesta")
    return None, str(razon)


def main():
    k = clave()
    args = [a for a in sys.argv[1:] if not a.startswith("--")]

    if "--modelos" in sys.argv:
        modelo, disponibles = elegir_modelo(k)
        print("Modelos de imagen disponibles en la cuenta:")
        for d in disponibles:
            print("  %s %s" % ("→" if d == modelo else " ", d))
        return

    modelo, _ = elegir_modelo(k)
    print("Modelo: %s\n" % modelo)

    trabajos = leer_prompts()
    if args:
        trabajos = [t for t in trabajos if any(a in t[1] for a in args)]
        if not trabajos:
            sys.exit("Ningún render coincide con: %s" % ", ".join(args))

    hechas, fallidas = [], []
    for n, (titulo, archivo, prompt) in enumerate(trabajos, 1):
        print("  %2d/%d  %s" % (n, len(trabajos), titulo))
        t0 = time.time()
        salida, error = generar(k, modelo, archivo, prompt)
        if salida:
            kb = os.path.getsize(salida) // 1024
            print("        %s · %d KB · %.1f s"
                  % (os.path.basename(salida), kb, time.time() - t0))
            hechas.append(os.path.basename(salida))
        else:
            print("        sin imagen: %s" % error)
            fallidas.append((titulo, error))

    print("\n%d de %d generadas." % (len(hechas), len(trabajos)))
    for titulo, error in fallidas:
        print("  falló · %s · %s" % (titulo, error))


if __name__ == "__main__":
    main()
