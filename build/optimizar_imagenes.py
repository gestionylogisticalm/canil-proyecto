#!/usr/bin/env python3
"""Convierte los PNG del render 3D a JPEG optimizados para el PDF.

Los PNG de 2000 px pesan cerca de 1,5 MB cada uno; en JPEG de 1600 px quedan
en torno a 250 kB sin pérdida visible a tamaño de página.

Uso:  python3 build/optimizar_imagenes.py
"""

import glob
import os

import pymupdf

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIGEN = os.path.join(RAIZ, "src", "img")
ANCHO = 1600
CALIDAD = 86

if __name__ == "__main__":
    total = 0
    for png in sorted(glob.glob(os.path.join(ORIGEN, "*.png"))):
        pix = pymupdf.Pixmap(png)
        escala = ANCHO / pix.width
        doc = pymupdf.open()
        pagina = doc.new_page(width=pix.width * escala, height=pix.height * escala)
        pagina.insert_image(pagina.rect, filename=png)
        nuevo = pagina.get_pixmap(dpi=72)
        destino = png[:-4] + ".jpg"
        nuevo.save(destino, output="jpg", jpg_quality=CALIDAD)
        doc.close()
        total += os.path.getsize(destino)
        print("  %s  %.0f kB" % (os.path.basename(destino), os.path.getsize(destino) / 1024))
    print("  total %.1f MB" % (total / 1e6))
