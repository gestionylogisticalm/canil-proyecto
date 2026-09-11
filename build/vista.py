#!/usr/bin/env python3
"""Exporta páginas de un PDF a PNG para revisar la maqueta.

Uso:  python3 build/vista.py pdf/archivo.pdf 1 2 3
"""
import os
import sys

import pymupdf

SALIDA = "/tmp/claude-0/-home-user-canil-proyecto/ede1c3be-e18b-55cb-94ec-84a4e0aa3225/scratchpad/vista"

if __name__ == "__main__":
    ruta = sys.argv[1]
    paginas = [int(p) for p in sys.argv[2:]] or [1]
    os.makedirs(SALIDA, exist_ok=True)
    doc = pymupdf.open(ruta)
    for n in paginas:
        pag = doc[n - 1]
        pix = pag.get_pixmap(dpi=105)
        destino = os.path.join(SALIDA, "p%03d.png" % n)
        pix.save(destino)
        print(destino)
