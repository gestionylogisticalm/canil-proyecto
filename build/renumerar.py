#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Elimina la sección de referentes del plan y renumera el documento.

- La sección 6 (Referentes) desaparece: su contenido quedó repartido en las
  secciones que corresponden.
- Las secciones 7 a 20 pasan a ser 6 a 19.
- La parte II (Respaldo) desaparece y la sección de cifras se integra a la
  parte I; las partes III, IV y V pasan a ser II, III y IV.

El renumerado se hace en dos fases, con marcas temporales, para que los
reemplazos no se pisen entre sí.
"""

import io
import re
import sys

RUTA = "src/plan.html"


def quitar_seccion(texto, marcador, clase="seccion"):
    """Elimina la <section> de la clase indicada que contiene el marcador."""
    pos = texto.index(marcador)
    apertura = '<section class="%s">' % clase
    ini = texto.rindex(apertura, 0, pos)
    fin = texto.index("</section>", pos) + len("</section>")
    return texto[:ini] + texto[fin:].lstrip("\n")


def main():
    with io.open(RUTA, encoding="utf-8") as f:
        s = f.read()

    # 1. Fuera la sección de referentes
    s = quitar_seccion(s, "@@s6@@")

    # 2. Fuera su entrada del índice
    s = re.sub(r'\s*<li><span class="num">6</span><span class="txt">Referentes</span>'
               r'<span class="puntos"></span><span class="pag" data-ref="s6">[^<]*</span></li>', "", s)

    # 3. La parte II desaparece y las cifras se integran a la parte I
    s = s.replace('''  <div class="grupo">Parte II · Respaldo</div>
  <ol>
    <li><span class="num">5</span><span class="txt">Cifras</span><span class="puntos"></span><span class="pag" data-ref="s5">—</span></li>
  </ol>

  <div class="grupo">Parte III · Propuesta</div>''',
                  '''  <div class="grupo">Parte II · Propuesta</div>''')
    s = s.replace('''    <li><span class="num">4</span><span class="txt">Carácter del documento y quién lo presenta</span><span class="puntos"></span><span class="pag" data-ref="s4">—</span></li>
  </ol>''',
                  '''    <li><span class="num">4</span><span class="txt">Carácter del documento y quién lo presenta</span><span class="puntos"></span><span class="pag" data-ref="s4">—</span></li>
    <li><span class="num">5</span><span class="txt">Cifras</span><span class="puntos"></span><span class="pag" data-ref="s5">—</span></li>
  </ol>''')
    s = s.replace('  <div class="grupo">Parte IV · Construcción</div>', '  <div class="grupo">Parte III · Construcción</div>')
    s = s.replace('  <div class="grupo">Parte V · Gestión</div>', '  <div class="grupo">Parte IV · Gestión</div>')

    # 4. Portadillas de parte
    s = quitar_seccion(s, '<div class="rotulo">Parte II</div>', clase="parte")
    s = s.replace('''      <li>Resumen ejecutivo</li>
      <li>Introducción</li>
      <li>Objetivos y metas</li>
      <li>Carácter del documento y quién lo presenta</li>''',
                  '''      <li>Resumen ejecutivo</li>
      <li>Introducción</li>
      <li>Objetivos y metas</li>
      <li>Carácter del documento y quién lo presenta</li>
      <li>Cifras</li>''')
    s = s.replace('<div class="rotulo">Parte III</div>', '<div class="rotulo">Parte II</div>')
    s = s.replace('<div class="rotulo">Parte IV</div>', '<div class="rotulo">Parte III</div>')
    s = s.replace('<div class="rotulo">Parte V</div>', '<div class="rotulo">Parte IV</div>')
    s = s.replace('<ol start="7">', '<ol start="6">')
    s = s.replace('<ol start="14">', '<ol start="13">')
    s = s.replace('<ol start="16">', '<ol start="15">')

    # 5. Renumerado de secciones 7..20 -> 6..19, en dos fases
    pares = [(n, n - 1) for n in range(7, 21)]
    patrones = [
        ('@@s%d@@', '@@T%d@@'),
        ('data-ref="s%d"', 'data-ref="T%d"'),
        ('<span class="numero">Sección %d<', '<span class="numero">SecciónT%d<'),
        ('<span class="num">%d</span>', '<span class="numT%d</span>'),
        ('sección %d', 'secciónT%d'),
    ]
    for viejo, nuevo in pares:
        for pv, pn in patrones:
            s = s.replace(pv % viejo, pn % nuevo)
    for viejo, nuevo in pares:
        for pv, pn in patrones:
            s = s.replace(pn % nuevo, pv % nuevo)

    with io.open(RUTA, "w", encoding="utf-8") as f:
        f.write(s)

    # 6. Comprobaciones
    secciones = re.findall(r'<span class="numero">Sección (\d+)<', s)
    indice = re.findall(r'<span class="num">(\d+)</span>', s)
    print("  secciones en el cuerpo: %s" % ", ".join(secciones))
    print("  números del índice:     %s" % ", ".join(indice))
    sueltas = re.findall(r'sección (\d+)', s)
    print("  referencias cruzadas:   %s" % ", ".join(sorted(set(sueltas), key=int)))
    if secciones != [str(i) for i in range(1, 20)]:
        print("  REVISAR: la numeración del cuerpo no es 1 a 19")
        sys.exit(1)
    if indice != [str(i) for i in range(1, 20)]:
        print("  REVISAR: la numeración del índice no es 1 a 19")
        sys.exit(1)
    print("  numeración correcta")


if __name__ == "__main__":
    main()
