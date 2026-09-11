#!/usr/bin/env python3
"""
Construye los PDF del Plan de Caniles de Puerto Varas.

Pasos por documento:
  1. Separa la portada del cuerpo (marca <!--FIN-PORTADA-->).
  2. Renderiza el cuerpo una primera vez para leer en qué página cae cada
     sección (marcas invisibles @@clave@@) y completar el índice.
  3. Renderiza la portada (sin pie) y el cuerpo final (con pie y folio).
  4. Une ambos PDF en pdf/<salida>.pdf

Uso:  python3 build/construir.py [plan|presupuesto|todo]
"""

import json
import os
import re
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(RAIZ, "src")
SALIDA = os.path.join(RAIZ, "pdf")
TMP = os.path.join(RAIZ, "build", "tmp")

ENTORNO = dict(os.environ, NODE_PATH="/opt/node22/lib/node_modules")

DOCUMENTOS = {
    "plan": {
        "fuente": "plan.html",
        "salida": "01-Plan-de-Caniles-Publicos-Puerto-Varas.pdf",
        "pie": "Plan de Caniles Públicos · Municipalidad de Puerto Varas",
    },
    "presupuesto": {
        "fuente": "presupuesto.html",
        "salida": "02-Presupuesto-Canil-Piloto-Puerto-Varas.pdf",
        "pie": "Presupuesto Canil Piloto · Municipalidad de Puerto Varas",
    },
}


def render(entrada, salida, pie=None, titulo=""):
    cfg = {"entrada": entrada, "salida": salida, "pie": bool(pie), "titulo": titulo}
    subprocess.run(
        ["node", os.path.join(RAIZ, "build", "render.js"), json.dumps(cfg)],
        check=True,
        env=ENTORNO,
    )


def paginas_de_marcas(pdf_path):
    from pypdf import PdfReader

    mapa = {}
    lector = PdfReader(pdf_path)
    for i, pagina in enumerate(lector.pages, start=1):
        # el texto puede venir en mayúsculas y espaciado por el CSS del título
        texto = re.sub(r"\s+", "", (pagina.extract_text() or "")).lower()
        for clave in re.findall(r"@@([a-z0-9\-]+)@@", texto):
            mapa.setdefault(clave, i)
    return mapa


def completar_indice(html, mapa):
    def reemplazo(m):
        clave = m.group(1)
        return '<span class="pag" data-ref="%s">%s</span>' % (
            clave,
            mapa.get(clave, "—"),
        )

    return re.sub(r'<span class="pag" data-ref="([a-z0-9\-]+)">[^<]*</span>', reemplazo, html)


def construir(nombre):
    doc = DOCUMENTOS[nombre]
    os.makedirs(TMP, exist_ok=True)
    os.makedirs(SALIDA, exist_ok=True)

    ruta = os.path.join(SRC, doc["fuente"])
    with open(ruta, encoding="utf-8") as f:
        html = f.read()

    if "<!--FIN-PORTADA-->" not in html:
        raise SystemExit("Falta la marca <!--FIN-PORTADA--> en %s" % doc["fuente"])

    cabeza, _, resto = html.partition("<!--FIN-PORTADA-->")
    cierre = "</body></html>"
    encabezado = cabeza[: cabeza.index("<body")] + "<body>\n"

    portada_html = cabeza + cierre
    cuerpo_html = encabezado + resto

    p_portada = os.path.join(SRC, ".tmp-portada.html")
    p_cuerpo = os.path.join(SRC, ".tmp-cuerpo.html")
    pdf_portada = os.path.join(TMP, "portada.pdf")
    pdf_cuerpo = os.path.join(TMP, "cuerpo.pdf")

    try:
        # Pasada 1: ubicar las secciones para el índice
        with open(p_cuerpo, "w", encoding="utf-8") as f:
            f.write(cuerpo_html)
        render(p_cuerpo, pdf_cuerpo, pie=True, titulo=doc["pie"])
        mapa = paginas_de_marcas(pdf_cuerpo)
        print("  secciones ubicadas: %d" % len(mapa))

        # Pasada 2: índice completo
        cuerpo_html = completar_indice(cuerpo_html, mapa)
        with open(p_cuerpo, "w", encoding="utf-8") as f:
            f.write(cuerpo_html)
        render(p_cuerpo, pdf_cuerpo, pie=True, titulo=doc["pie"])

        with open(p_portada, "w", encoding="utf-8") as f:
            f.write(portada_html)
        render(p_portada, pdf_portada)

        from pypdf import PdfWriter, PdfReader

        escritor = PdfWriter()
        escritor.append(PdfReader(pdf_portada), pages=(0, 1))
        escritor.append(PdfReader(pdf_cuerpo))
        destino = os.path.join(SALIDA, doc["salida"])
        with open(destino, "wb") as f:
            escritor.write(f)

        total = len(PdfReader(destino).pages)
        print("  %s · %d páginas · %.1f MB" % (doc["salida"], total, os.path.getsize(destino) / 1e6))
    finally:
        for p in (p_portada, p_cuerpo):
            if os.path.exists(p):
                os.remove(p)


if __name__ == "__main__":
    objetivo = sys.argv[1] if len(sys.argv) > 1 else "todo"
    nombres = list(DOCUMENTOS) if objetivo == "todo" else [objetivo]
    for n in nombres:
        print("Construyendo %s…" % n)
        construir(n)
