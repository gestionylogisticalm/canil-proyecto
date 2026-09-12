#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera src/presupuesto.html a partir de build/datos.py.

Todos los subtotales, totales, porcentajes y el flujo de caja se calculan aquí:
el documento no contiene ninguna cifra escrita a mano que no provenga de estos
cálculos, salvo los textos explicativos.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datos import (  # noqa: E402
    COMPRA, CONAF, CUADRILLA, LICEO, MUNI,
    ETAPAS_MES, MESES_MARCHA_BLANCA, OPERACION, PAGOS_ITEM, PAGOS_PARTIDA,
    PARAMETROS, PARTIDAS, SEMANAS_PARTIDA, VERIFICADO,
)

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESTINO = os.path.join(RAIZ, "src", "presupuesto.html")

UTM = 71721
TOPE_UTM = 2500
TOPE_PMU = TOPE_UTM * UTM
GG = 0.08
IMPREVISTOS = 0.10
IPC = 0.035

HABITANTES = 52942
PERROS_COMUNA_BAJO = 20053
PERROS_COMUNA_ALTO = 23797
PERROS_PROMEDIO = 21925
PERROS_SECTOR = 7308
VISITAS_SEMANA = 731
VISITAS_DIA = 104
VISITAS_MES = 3132
VISITAS_ANO = 38108
VISITAS_ANO3 = 45729


# --------------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------------

def pesos(n):
    return "$" + format(int(round(n)), ",d").replace(",", ".")


def miles(n):
    """Monto en miles de pesos, para la tabla de flujo de caja."""
    if not n:
        return "—"
    return format(int(round(n / 1000)), ",d").replace(",", ".")


def numero(n, dec=0):
    if dec:
        return format(round(n, dec), ",.%df" % dec).replace(",", "·").replace(".", ",").replace("·", ".")
    return format(int(round(n)), ",d").replace(",", ".")


def cantidad(c):
    if isinstance(c, float) and c != int(c):
        return str(c).replace(".", ",")
    return numero(c)


def esc(t):
    return t


# --------------------------------------------------------------------------
# Cálculos
# --------------------------------------------------------------------------

def calcular():
    resumen = []
    avisos = []
    for p in PARTIDAS:
        val = fin = 0
        for cod, desc, cant, un, pu, tot, origen, tipo, fuente in p["items"]:
            esperado = cant * pu
            if abs(esperado - tot) > 100:
                avisos.append("%s: cantidad × precio = %s pero el total es %s" % (cod, pesos(esperado), pesos(tot)))
            val += tot
            if origen == COMPRA:
                fin += tot
        resumen.append({
            "codigo": p["codigo"],
            "nombre": p["nombre"],
            "valorizado": val,
            "financiar": fin,
            "aporte": val - fin,
        })

    directo_val = sum(r["valorizado"] for r in resumen)
    directo_fin = sum(r["financiar"] for r in resumen)
    aporte = directo_val - directo_fin
    gg = round(directo_fin * GG)
    imp = round((directo_fin + gg) * IMPREVISTOS)
    total_fin = directo_fin + gg + imp
    total_val = directo_val + gg + imp

    op = operacion(directo_fin, total_fin)
    op_val = sum(o[5] for o in op)
    op_fin = sum(o[5] for o in op if o[6] == COMPRA)

    return {
        "operacion": op,
        "resumen": resumen,
        "avisos": avisos,
        "directo_val": directo_val,
        "directo_fin": directo_fin,
        "aporte": aporte,
        "gg": gg,
        "imp": imp,
        "total_fin": total_fin,
        "total_val": total_val,
        "utm": total_fin / UTM,
        "op_val": op_val,
        "op_fin": op_fin,
        "op_aporte": op_val - op_fin,
    }


def suma(*codigos):
    """Suma los subtotales de los ítems indicados, por código."""
    buscados = set(codigos)
    return sum(i[5] for p in PARTIDAS for i in p["items"] if i[0] in buscados)


def operacion(directo_fin, total_fin):
    """La reposición, la provisión de recambio de equipos y el seguro son
    porcentajes de la inversión: se recalculan para que sigan cuadrando cuando
    cambia un precio."""
    partida_f = sum(i[5] for p in PARTIDAS if p["codigo"] == "F" for i in p["items"])
    formulas = {
        "O.11": round(directo_fin * 0.02),
        "O.12": round(partida_f * 0.10),
        "O.15": round(total_fin * 0.005),
    }
    lista = []
    for cod, desc, cant, un, pu, tot, origen, nota in OPERACION:
        if cod in formulas:
            tot = pu = formulas[cod]
        lista.append((cod, desc, cant, un, pu, tot, origen, nota))
    return lista


def flujo(datos):
    """Gasto mensual a financiar y aporte valorizado, por partida y por mes."""
    meses = list(range(1, 14))
    fin = {p["codigo"]: {m: 0.0 for m in meses} for p in PARTIDAS}
    apo = {p["codigo"]: {m: 0.0 for m in meses} for p in PARTIDAS}

    for p in PARTIDAS:
        cod_p = p["codigo"]
        for cod, desc, cant, un, pu, tot, origen, tipo, fuente in p["items"]:
            plan = PAGOS_ITEM.get(cod) or PAGOS_PARTIDA[cod_p]
            destino = fin if origen == COMPRA else apo
            for mes, frac in plan:
                destino[cod_p][mes] += tot * frac

    total_fin_mes = {m: sum(fin[c][m] for c in fin) for m in meses}
    total_apo_mes = {m: sum(apo[c][m] for c in apo) for m in meses}

    base = sum(total_fin_mes.values())
    gg_mes = {m: datos["gg"] * total_fin_mes[m] / base for m in meses}
    imp_mes = {m: datos["imp"] * total_fin_mes[m] / base for m in meses}
    total_mes = {m: total_fin_mes[m] + gg_mes[m] + imp_mes[m] for m in meses}

    acumulado = {}
    acc = 0.0
    for m in meses:
        acc += total_mes[m]
        acumulado[m] = acc

    return {
        "meses": meses,
        "fin": fin,
        "apo": apo,
        "total_fin_mes": total_fin_mes,
        "total_apo_mes": total_apo_mes,
        "gg_mes": gg_mes,
        "imp_mes": imp_mes,
        "total_mes": total_mes,
        "acumulado": acumulado,
    }


# --------------------------------------------------------------------------
# Construcción del HTML
# --------------------------------------------------------------------------

def tabla_items(p):
    filas = []
    for cod, desc, cant, un, pu, tot, origen, tipo, fuente in p["items"]:
        clase = "" if origen == COMPRA else ' class="aporte"'
        filas.append(
            "<tr%s><td>%s</td><td>%s</td><td class=\"num\">%s</td><td>%s</td>"
            "<td class=\"num\">%s</td><td class=\"num\">%s</td><td>%s</td><td>%s</td></tr>"
            % (clase, cod, esc(desc), cantidad(cant), un, pesos(pu), pesos(tot), origen, tipo)
        )
    val = sum(i[5] for i in p["items"])
    fin = sum(i[5] for i in p["items"] if i[6] == COMPRA)
    filas.append(
        '<tr class="subtotal"><td colspan="5">Subtotal valorizado · partida %s</td>'
        '<td class="num">%s</td><td colspan="2">A financiar %s · aporte %s</td></tr>'
        % (p["codigo"], pesos(val), pesos(fin), pesos(val - fin))
    )
    return (
        '<div class="tabla-envoltura"><table class="compacta presupuesto">'
        '<thead><tr><th>Código</th><th>Ítem</th><th class="num">Cant.</th><th>Unidad</th>'
        '<th class="num">Precio unitario</th><th class="num">Subtotal</th><th>Origen</th>'
        '<th>Tipo</th></tr></thead><tbody>%s</tbody></table></div>' % "".join(filas)
    )


def tabla_fuentes(p):
    filas = []
    for cod, desc, cant, un, pu, tot, origen, tipo, fuente in p["items"]:
        filas.append("<tr><td>%s</td><td>%s</td></tr>" % (cod, esc(fuente)))
    return (
        '<div class="tabla-envoltura"><table class="compacta">'
        '<thead><tr><th style="width:10%%">Código</th><th>Origen del precio</th></tr></thead>'
        "<tbody>%s</tbody></table></div>" % "".join(filas)
    )


def seccion_partida(p, indice):
    val = sum(i[5] for i in p["items"])
    fin = sum(i[5] for i in p["items"] if i[6] == COMPRA)
    verificados = sum(1 for i in p["items"] if i[7] == VERIFICADO)
    semanas, detalle = SEMANAS_PARTIDA[p["codigo"]]

    explic = "".join("<p>%s</p>" % e for e in p["explicacion"])
    return """
<section class="seccion">
  <h2><span class="numero">Partida %(cod)s<span class="marcador">@@p%(codl)s@@</span></span>%(nombre)s</h2>
  <p class="entradilla">%(resumen)s</p>

  <div class="cifras cuatro">
    <div class="cifra"><span class="dato">%(val)s</span><span class="glosa">Costo valorizado de la partida</span></div>
    <div class="cifra"><span class="dato">%(fin)s</span><span class="glosa">A financiar con el fondo</span></div>
    <div class="cifra"><span class="dato">%(apo)s</span><span class="glosa">Aporte valorizado</span></div>
    <div class="cifra"><span class="dato">%(semanas)s</span><span class="glosa">%(detalle)s</span></div>
  </div>

  <h3>Qué incluye y cómo se calculó</h3>
  %(explic)s

  <h3>Detalle de ítems</h3>
  %(tabla)s
  <p class="nota-tabla">%(verif)d de %(nitems)d ítems tienen precio verificado contra un valor
    publicado en 2025 o 2026; el resto son referenciales y deben cotizarse antes de ejecutar. Las filas
    con fondo azul son aportes valorizados: no se pagan con el fondo.</p>

  <h3>Origen de cada precio</h3>
  %(fuentes)s
</section>""" % {
        "cod": p["codigo"],
        "codl": p["codigo"].lower(),
        "nombre": p["nombre"],
        "resumen": p["resumen"],
        "val": pesos(val),
        "fin": pesos(fin),
        "apo": pesos(val - fin),
        "semanas": semanas,
        "detalle": detalle,
        "explic": explic,
        "tabla": tabla_items(p),
        "fuentes": tabla_fuentes(p),
        "verif": verificados,
        "nitems": len(p["items"]),
    }


def construir():
    d = calcular()
    f = flujo(d)

    for a in d["avisos"]:
        print("  aviso: " + a)

    # ---------------- portada e índice ----------------
    partes = []
    partes.append("""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Presupuesto del Canil Piloto de Puerto Varas</title>
<link rel="stylesheet" href="estilos.css">
<style>
  table.presupuesto { font-size: 7.9pt; }
  table.presupuesto td { padding: 3pt 4pt; }
  tbody tr.aporte td { background: #e3eef8 !important; }
  table.flujo { font-size: 7.2pt; }
  table.flujo td, table.flujo th { padding: 2.6pt 2pt; }
  table.flujo td.et { text-align: left; }
</style>
</head>
<body>

<div class="portada">
  <div class="decoracion"></div>
  <div class="decoracion dos"></div>
  <div class="banda-superior">
    <div class="escudo">Comuna de Puerto Varas · Región de Los Lagos</div>
  </div>
  <div class="cuerpo">
    <div class="documento">Propuesta base de proyecto · Documento 2 de 2</div>
    <h1>Presupuesto del canil piloto</h1>
    <div class="linea"></div>
    <p class="bajada">Desglose por partida e ítem, explicación de cada cantidad, tiempos de ejecución,
      flujo mensual de gastos, operación anual, proyección de los tres caniles y verificación del tope
      PMU.</p>
  </div>
  <div class="pie">
    <div class="datos">
      <strong>Presenta:</strong> Lukas Matías Muñoz Miranda<br>
      Gestión y Logística LM SpA · Vecino de Puerto Varas<br>
      Septiembre de 2026
    </div>
    <div class="sello">
      Valores en pesos chilenos con IVA incluido, a septiembre de 2026. Los ítems marcados como
      referenciales deben cotizarse antes de ejecutar.
    </div>
  </div>
</div>
<!--FIN-PORTADA-->

<section class="seccion indice">
  <h2>Índice</h2>

  <div class="grupo">Marco del presupuesto</div>
  <ol>
    <li><span class="num">1</span><span class="txt">Cómo leer este presupuesto</span><span class="puntos"></span><span class="pag" data-ref="c1">—</span></li>
    <li><span class="num">2</span><span class="txt">Supuestos y parámetros de cálculo</span><span class="puntos"></span><span class="pag" data-ref="c2">—</span></li>
    <li><span class="num">3</span><span class="txt">Resumen general del canil piloto</span><span class="puntos"></span><span class="pag" data-ref="c3">—</span></li>
  </ol>

  <div class="grupo">Desglose por partida</div>
  <ol>""")

    for p in PARTIDAS:
        partes.append(
            '<li><span class="num">%s</span><span class="txt">%s</span>'
            '<span class="puntos"></span><span class="pag" data-ref="p%s">—</span></li>'
            % (p["codigo"], p["nombre"], p["codigo"].lower())
        )

    partes.append("""</ol>

  <div class="grupo">Programación del gasto</div>
  <ol>
    <li><span class="num">4</span><span class="txt">Tiempos de ejecución por partida</span><span class="puntos"></span><span class="pag" data-ref="c4">—</span></li>
    <li><span class="num">5</span><span class="txt">Flujo de caja mensual</span><span class="puntos"></span><span class="pag" data-ref="c5">—</span></li>
  </ol>

  <div class="grupo">Resultados</div>
  <ol>
    <li><span class="num">6</span><span class="txt">Qué gastos se ahorran y cuáles no</span><span class="puntos"></span><span class="pag" data-ref="c6">—</span></li>
    <li><span class="num">7</span><span class="txt">Operación anual</span><span class="puntos"></span><span class="pag" data-ref="c7">—</span></li>
    <li><span class="num">8</span><span class="txt">Proyección de los tres caniles y tope PMU</span><span class="puntos"></span><span class="pag" data-ref="c8">—</span></li>
    <li><span class="num">9</span><span class="txt">Evaluación económica</span><span class="puntos"></span><span class="pag" data-ref="c9">—</span></li>
    <li><span class="num">10</span><span class="txt">Metas proyectadas</span><span class="puntos"></span><span class="pag" data-ref="c10">—</span></li>
    <li><span class="num">11</span><span class="txt">Ahorros adicionales identificados</span><span class="puntos"></span><span class="pag" data-ref="c11">—</span></li>
  </ol>

  <div class="grupo">Cierre</div>
  <ol>
    <li><span class="num">12</span><span class="txt">Fuentes de precios y advertencias</span><span class="puntos"></span><span class="pag" data-ref="c12">—</span></li>
  </ol>
</section>
""")

    # ---------------- 1. Cómo leer ----------------
    n_items = sum(len(p["items"]) for p in PARTIDAS)
    n_verif = sum(1 for p in PARTIDAS for i in p["items"] if i[7] == VERIFICADO)
    partes.append("""
<section class="seccion">
  <h2><span class="numero">Capítulo 1<span class="marcador">@@c1@@</span></span>Cómo leer este presupuesto</h2>

  <p class="entradilla">Este documento acompaña al plan y contiene el cálculo completo de lo que cuesta
    construir y operar un canil de una hectárea en Puerto Varas. Está ordenado para que cualquier
    profesional municipal pueda revisarlo ítem por ítem y reemplazar lo que corresponda.</p>

  <h3>Qué significa cada columna</h3>
  <div class="tabla-envoltura">
  <table>
    <thead><tr><th style="width:18%%">Columna</th><th>Qué contiene</th></tr></thead>
    <tbody>
      <tr><td><strong>Código</strong></td><td>Identificador del ítem dentro de su partida, por ejemplo C.9. Se usa igual en el flujo de caja y en el cronograma.</td></tr>
      <tr><td><strong>Cantidad y unidad</strong></td><td>La medida con que se compra o se contrata: rollos, unidades, metros, metros cuadrados, metros cúbicos, meses o global (gl) cuando es un encargo completo.</td></tr>
      <tr><td><strong>Precio unitario</strong></td><td>Precio con IVA incluido. En los equipos importados incorpora tipo de cambio y factor de internación.</td></tr>
      <tr><td><strong>Subtotal</strong></td><td>Cantidad por precio unitario. En los ítems calculados desde UF, euros o dólares, el subtotal se obtiene de la cifra sin redondear, por lo que puede diferir en algunos pesos del producto de las columnas anteriores.</td></tr>
      <tr><td><strong>Origen</strong></td><td><em>Compra/contrato</em> es lo que se paga con el fondo. <em>Aporte municipal</em>, <em>Cuadrilla municipal</em>, <em>Liceo técnico</em> y <em>CONAF</em> son aportes valorizados: tienen valor de mercado, se contabilizan, pero no se desembolsan.</td></tr>
      <tr><td><strong>Tipo</strong></td><td><em>Verificado</em>: precio publicado en 2025 o 2026, con la fuente indicada. <em>Referencial</em>: estimación fundada que debe cotizarse antes de ejecutar.</td></tr>
    </tbody>
  </table>
  </div>

  <h3>Tres cifras distintas, que no hay que confundir</h3>
  <ul class="marcas">
    <li><strong>Costo valorizado:</strong> lo que vale todo el proyecto, incluidos los aportes. Es la
      cifra que muestra el tamaño real de la obra.</li>
    <li><strong>Costo a financiar:</strong> lo que efectivamente hay que pagar con el fondo. Es la
      cifra que hay que conseguir.</li>
    <li><strong>Aporte valorizado:</strong> la diferencia entre ambas. Es lo que ponen el municipio, el
      liceo técnico y CONAF en trabajo y materiales.</li>
  </ul>

  <h3>Estado de los precios</h3>
  <p>De los %(nitems)d ítems de inversión, <strong>%(nverif)d tienen precio verificado</strong> contra
    un valor publicado y el resto son referenciales. Ningún presupuesto de esta etapa puede tener el
    100%% de precios cotizados: lo que corresponde es que la mesa técnica del proyecto reemplace los
    referenciales por cotizaciones formales antes de licitar, empezando por los de mayor monto —tótem
    SOS, luminarias de grado público, cerraduras, cañerías, honorarios profesionales, retroexcavadora y
    camión—.</p>

  <div class="destacado">
    <div class="titulo">Cómo se compra lo que aquí se presupuesta</div>
    <p>El orden de revisión al momento de ejecutar es: primero la <strong>Plataforma de Economía
      Circular</strong> de Mercado Público, donde los servicios públicos ceden gratuitamente bienes
      dados de baja —de ahí sale el contenedor bodega y pueden salir basureros y mobiliario—; después
      <strong>Convenio Marco</strong>, que permite comprar con precios ya licitados y sin proceso
      adicional; y solo lo que no esté disponible por esas vías se licita o se cotiza en el mercado
      local. Ese mismo orden es el que permite verificar en la ejecución que los precios de este
      presupuesto se cumplan.</p>
  </div>


</section>""" % {"nitems": n_items, "nverif": n_verif})

    # ---------------- 2. Supuestos ----------------
    filas_par = "".join(
        "<tr><td><strong>%s</strong></td><td>%s</td><td>%s</td></tr>" % p for p in PARAMETROS
    )
    partes.append("""
<section class="seccion">
  <h2><span class="numero">Capítulo 2<span class="marcador">@@c2@@</span></span>Supuestos y parámetros de cálculo</h2>

  <p class="entradilla">Todos los valores del presupuesto dependen de estos parámetros. Si cambia
    alguno —el valor de la UTM, la profundidad del pozo, el plazo de obra— cambia el resultado, y por eso
    están declarados por separado.</p>

  <div class="tabla-envoltura">
  <table>
    <thead><tr><th style="width:26%%">Parámetro</th><th style="width:26%%">Valor</th><th>Detalle</th></tr></thead>
    <tbody>%(filas)s</tbody>
  </table>
  </div>

  <h3>Los tres supuestos que más pesan</h3>
  <ol>
    <li><strong>Profundidad del pozo.</strong> Se presupuestaron 40 metros. Cada 10 metros adicionales
      suman $2.300.000 al costo directo, más gastos generales e imprevistos. El estudio hidrogeológico
      de la partida A existe justamente para acotar esta incertidumbre antes de ejecutar.</li>
    <li><strong>Costo del baño público.</strong> Se calculó a 30 UF/m² sobre 16 m², dentro de un rango
      de mercado de 22 a 42 UF/m². En el extremo inferior del rango el baño costaría unos $14,4
      millones y en el superior unos $27,5 millones.</li>
    <li><strong>Plazo de obra.</strong> Cuatro meses. Cada mes adicional suma %(mes_obra)s en mano de
      obra y arriendos a financiar, porque el equipo permanente se mantiene.</li>
  </ol>
</section>""" % {
        "filas": filas_par,
        "mes_obra": pesos((suma("I.1") + suma("I.2") + suma("I.6") + suma("B.2")) / 4),
    })

    # ---------------- 3. Resumen general ----------------
    filas_res = ""
    for r in d["resumen"]:
        filas_res += (
            '<tr><td class="cen"><strong>%s</strong></td><td>%s</td><td class="num">%s</td>'
            '<td class="num">%s</td><td class="num">%s</td><td class="num">%s%%</td></tr>'
            % (r["codigo"], r["nombre"], pesos(r["valorizado"]), pesos(r["financiar"]),
               pesos(r["aporte"]), numero(100.0 * r["financiar"] / d["directo_fin"], 1))
        )
    partes.append("""
<section class="seccion">
  <h2><span class="numero">Capítulo 3<span class="marcador">@@c3@@</span></span>Resumen general del canil piloto</h2>

  <div class="cifras cuatro">
    <div class="cifra"><span class="dato">%(total_fin)s</span><span class="glosa">Total a financiar, equivalente a %(utm)s UTM</span></div>
    <div class="cifra"><span class="dato">%(aporte)s</span><span class="glosa">Aporte valorizado del municipio, el liceo y CONAF</span></div>
    <div class="cifra"><span class="dato">%(total_val)s</span><span class="glosa">Valor total del proyecto, incluidos aportes</span></div>
    <div class="cifra"><span class="dato">%(margen)s</span><span class="glosa">Margen disponible bajo el tope PMU</span></div>
  </div>

  <h3>Costo directo por partida</h3>
  <div class="tabla-envoltura">
  <table>
    <thead><tr><th class="cen" style="width:7%%">Partida</th><th>Nombre</th><th class="num">Valorizado</th>
      <th class="num">A financiar</th><th class="num">Aporte</th><th class="num">%% del gasto</th></tr></thead>
    <tbody>
      %(filas)s
      <tr class="total"><td class="cen">—</td><td>Costo directo total</td><td class="num">%(directo_val)s</td>
        <td class="num">%(directo_fin)s</td><td class="num">%(aporte)s</td><td class="num">100,0%%</td></tr>
    </tbody>
  </table>
  </div>

  <h3>Del costo directo al total del proyecto</h3>
  <div class="tabla-envoltura">
  <table>
    <thead><tr><th>Concepto</th><th class="num" style="width:22%%">Monto</th><th style="width:34%%">Cómo se calcula</th></tr></thead>
    <tbody>
      <tr><td>Costo directo valorizado</td><td class="num">%(directo_val)s</td><td>Suma de las nueve partidas.</td></tr>
      <tr><td>Aportes valorizados</td><td class="num">−%(aporte)s</td><td>Municipio, cuadrilla municipal, liceo técnico y CONAF.</td></tr>
      <tr><td>Costo directo a financiar</td><td class="num">%(directo_fin)s</td><td>Lo que se paga con el fondo.</td></tr>
      <tr><td>Gastos generales (8%%)</td><td class="num">%(gg)s</td><td>Sobre el costo directo a financiar.</td></tr>
      <tr><td>Imprevistos (10%%)</td><td class="num">%(imp)s</td><td>Sobre costo directo más gastos generales.</td></tr>
      <tr class="total"><td>Total a financiar</td><td class="num">%(total_fin)s</td><td>%(utm)s UTM</td></tr>
      <tr><td>Tope PMU por proyecto</td><td class="num">%(tope)s</td><td>2.500 UTM de septiembre de 2026.</td></tr>
      <tr><td>Margen bajo el tope</td><td class="num">%(margen)s</td><td>%(margen_utm)s UTM disponibles.</td></tr>
      <tr><td>Valor total del proyecto</td><td class="num">%(total_val)s</td><td>Incluye los aportes valorizados, que son el %(pct_aporte)s%% del total.</td></tr>
    </tbody>
  </table>
  </div>

  <div class="destacado">
    <div class="titulo">Las cuatro partidas que concentran el gasto</div>
    <p>La zona de acceso, el agua, la mano de obra y la energía y seguridad concentran la mayor parte
      de lo que hay que pagar. Dentro de ellas, tres ítems explican por sí solos una parte importante
      del presupuesto: el baño público, la perforación del pozo y el tótem SOS. Son también los tres
      ítems donde una buena cotización produce el mayor ahorro.</p>
  </div>
</section>""" % {
        "filas": filas_res,
        "directo_val": pesos(d["directo_val"]),
        "directo_fin": pesos(d["directo_fin"]),
        "aporte": pesos(d["aporte"]),
        "gg": pesos(d["gg"]),
        "imp": pesos(d["imp"]),
        "total_fin": pesos(d["total_fin"]),
        "total_val": pesos(d["total_val"]),
        "utm": numero(d["utm"]),
        "tope": pesos(TOPE_PMU),
        "margen": pesos(TOPE_PMU - d["total_fin"]),
        "margen_utm": numero(TOPE_UTM - d["utm"]),
        "pct_aporte": numero(100.0 * d["aporte"] / d["total_val"], 1),
    })

    # ---------------- Partidas ----------------
    for i, p in enumerate(PARTIDAS):
        partes.append(seccion_partida(p, i))

    # ---------------- 4. Tiempos de ejecución ----------------
    filas_t = ""
    for p in PARTIDAS:
        semanas, detalle = SEMANAS_PARTIDA[p["codigo"]]
        fin = sum(i[5] for i in p["items"] if i[6] == COMPRA)
        filas_t += (
            '<tr><td class="cen"><strong>%s</strong></td><td>%s</td><td>%s</td><td>%s</td>'
            '<td class="num">%s</td></tr>'
            % (p["codigo"], p["nombre"], semanas, detalle, pesos(fin))
        )
    partes.append("""
<section class="seccion">
  <h2><span class="numero">Capítulo 4<span class="marcador">@@c4@@</span></span>Tiempos de ejecución por partida</h2>

  <p class="entradilla">La obra dura 16 semanas, repartidas en cuatro meses, con frentes de trabajo
    traslapados. Antes de eso hay nueve meses de estudios, trámites y fabricación en el liceo técnico.</p>

  <div class="tabla-envoltura">
  <table>
    <thead><tr><th class="cen" style="width:7%%">Partida</th><th style="width:22%%">Nombre</th>
      <th style="width:15%%">Cuándo</th><th>Detalle</th><th class="num">A financiar</th></tr></thead>
    <tbody>%s</tbody>
  </table>
  </div>

  <h3>Las 16 semanas de obra</h3>
  <div class="tabla-envoltura">
  <table>
    <thead><tr><th style="width:14%%">Semanas</th><th style="width:28%%">Frente de trabajo</th><th>Partidas involucradas</th></tr></thead>
    <tbody>
      <tr><td><strong>1 a 2</strong></td><td>Instalación de faena y trazado</td><td>B completa, más el aserrado de la madera municipal que alimenta las partidas C, D, E y G.</td></tr>
      <tr><td><strong>3 a 8</strong></td><td>Cerco y esclusas</td><td>C completa.</td></tr>
      <tr><td><strong>4 a 10</strong></td><td>Baño, amarre, torre y pozo</td><td>D, y los ítems E.1 a E.9 de pozo, torre y estanques.</td></tr>
      <tr><td><strong>8 a 12</strong></td><td>Agua, energía y cámaras</td><td>E.10 a E.26 y F completa.</td></tr>
      <tr><td><strong>10 a 14</strong></td><td>Mobiliario, juegos y paisajismo</td><td>G y H.</td></tr>
      <tr><td><strong>15 a 16</strong></td><td>Pruebas y recepción</td><td>Pruebas de riego y refresco, horarios y cerraduras, cámaras y parlantes con la central municipal, y análisis del agua (A.10).</td></tr>
    </tbody>
  </table>
  <p class="nota-tabla">La partida I —mano de obra y servicios— acompaña todas las semanas: el equipo
    permanente son un jefe de obra, tres carpinteros, cuatro jornales municipales y un prevencionista en
    media jornada, con el gasfíter y el electricista incorporados durante mes y medio cada uno.</p>
  </div>

  <div class="destacado">
    <div class="titulo">Por qué la obra va en primavera y verano</div>
    <p>Todo lo que se hace en el canil depende del suelo seco: plantar 280 postes, enterrar 400 metros
      de barrera, abrir zanjas, compactar 125 m³ de grava y perforar el pozo. Ejecutar en los meses
      lluviosos significa pagar el mismo equipo por más semanas y arriesgar terminaciones de madera mal
      selladas. El cronograma total del plan está armado para que las 16 semanas de obra caigan en esa
      ventana.</p>
  </div>
</section>""" % filas_t)

    # ---------------- 5. Flujo de caja ----------------
    meses = f["meses"]
    enc = "".join('<th class="num">%d</th>' % m for m in meses)
    filas_fl = ""
    for p in PARTIDAS:
        c = p["codigo"]
        if sum(f["fin"][c].values()) == 0:
            continue
        celdas = "".join('<td class="num">%s</td>' % miles(f["fin"][c][m]) for m in meses)
        filas_fl += '<tr><td class="et"><strong>%s</strong> · %s</td>%s<td class="num">%s</td></tr>' % (
            c, p["nombre"], celdas, miles(sum(f["fin"][c].values()))
        )
    filas_fl += '<tr class="subtotal"><td class="et">Costo directo a financiar</td>%s<td class="num">%s</td></tr>' % (
        "".join('<td class="num">%s</td>' % miles(f["total_fin_mes"][m]) for m in meses),
        miles(sum(f["total_fin_mes"].values())),
    )
    filas_fl += '<tr><td class="et">Gastos generales (8%%)</td>%s<td class="num">%s</td></tr>' % (
        "".join('<td class="num">%s</td>' % miles(f["gg_mes"][m]) for m in meses), miles(d["gg"]))
    filas_fl += '<tr><td class="et">Imprevistos (10%%)</td>%s<td class="num">%s</td></tr>' % (
        "".join('<td class="num">%s</td>' % miles(f["imp_mes"][m]) for m in meses), miles(d["imp"]))
    filas_fl += '<tr class="total"><td class="et">Gasto del mes</td>%s<td class="num">%s</td></tr>' % (
        "".join('<td class="num">%s</td>' % miles(f["total_mes"][m]) for m in meses), miles(d["total_fin"]))
    filas_fl += '<tr><td class="et">Acumulado</td>%s<td class="num">%s</td></tr>' % (
        "".join('<td class="num">%s</td>' % miles(f["acumulado"][m]) for m in meses), miles(d["total_fin"]))
    filas_fl += '<tr><td class="et">Aporte valorizado del mes</td>%s<td class="num">%s</td></tr>' % (
        "".join('<td class="num">%s</td>' % miles(f["total_apo_mes"][m]) for m in meses),
        miles(sum(f["total_apo_mes"].values())))

    etapas = ""
    for m in meses:
        etapas += "<tr><td class=\"cen\"><strong>%d</strong></td><td>%s</td><td class=\"num\">%s</td><td class=\"num\">%s</td></tr>" % (
            m, ETAPAS_MES[m], pesos(f["total_mes"][m]), pesos(f["acumulado"][m]))

    op_mensual = d["op_fin"] / 12.0
    mb = ""
    for m in MESES_MARCHA_BLANCA:
        mb += '<td class="num">%s</td>' % miles(op_mensual)

    partes.append("""
<section class="seccion">
  <h2><span class="numero">Capítulo 5<span class="marcador">@@c5@@</span></span>Flujo de caja mensual</h2>

  <p class="entradilla">En qué mes se paga cada partida, desde el inicio del trabajo hasta la marcha
    blanca. Los meses 1 a 3 son de mesas técnicas y línea base; los meses 4 a 9, de estudios y trámites;
    los meses 10 a 13, de obra; desde el mes 14 empieza la operación.</p>

  <div class="tabla-envoltura">
  <table class="flujo">
    <caption>Gasto mensual a financiar, en miles de pesos</caption>
    <thead><tr><th class="et" style="width:20%%">Partida</th>%(enc)s<th class="num">Total</th></tr></thead>
    <tbody>%(filas)s</tbody>
  </table>
  <p class="nota-tabla">Cifras en miles de pesos. Los gastos generales y los imprevistos se prorratean
    en proporción al gasto directo de cada mes. El aporte valorizado no es desembolso: se muestra para
    dejar constancia de cuándo se produce el trabajo del municipio, del liceo y de CONAF.</p>
  </div>

  <h3>Resumen mes a mes</h3>
  <div class="tabla-envoltura">
  <table>
    <thead><tr><th class="cen" style="width:8%%">Mes</th><th>Etapa</th><th class="num">Gasto del mes</th><th class="num">Acumulado</th></tr></thead>
    <tbody>%(etapas)s</tbody>
  </table>
  </div>

  <h3>Desde el mes 14: marcha blanca</h3>
  <div class="tabla-envoltura">
  <table class="flujo">
    <thead><tr><th class="et" style="width:28%%">Concepto</th><th class="num">14</th><th class="num">15</th>
      <th class="num">16</th><th class="num">17</th><th class="num">18</th><th class="num">19</th></tr></thead>
    <tbody>
      <tr><td class="et">Operación mensual a financiar</td>%(mb)s</tr>
    </tbody>
  </table>
  <p class="nota-tabla">Cifras en miles de pesos. La operación mensual a financiar es %(opm)s e incluye
    los dos auxiliares de aseo, insumos, datos, control de roedores, reposición y provisiones. El
    detalle está en el capítulo 7.</p>
  </div>

  <div class="destacado">
    <div class="titulo">Lo que muestra el flujo</div>
    <p>El gasto es bajo y parejo durante los primeros nueve meses —estudios y trámites— y se concentra
      casi por completo en los cuatro meses de obra. Eso es relevante para la programación presupuestaria
      municipal: entre la ejecución y el primer desembolso grande hay margen, y el peso del proyecto
      cae en un solo ejercicio de obra.</p>
  </div>
</section>""" % {"enc": enc, "filas": filas_fl, "etapas": etapas, "mb": mb, "opm": pesos(op_mensual)})

    # ---------------- 6. Ahorros ----------------
    aporte_por_origen = {}
    for p in PARTIDAS:
        for cod, desc, cant, un, pu, tot, origen, tipo, fuente in p["items"]:
            if origen != COMPRA:
                aporte_por_origen[origen] = aporte_por_origen.get(origen, 0) + tot
    filas_ap = "".join(
        '<tr><td>%s</td><td class="num">%s</td><td class="num">%s%%</td></tr>'
        % (o, pesos(v), numero(100.0 * v / d["aporte"], 1))
        for o, v in sorted(aporte_por_origen.items(), key=lambda x: -x[1])
    )
    herramientas = sum(i[5] for p in PARTIDAS if p["codigo"] == "B"
                       for i in p["items"] if i[0] in ("B.4", "B.5", "B.6", "B.7", "B.8", "B.9", "B.10", "B.11"))

    partes.append("""
<section class="seccion">
  <h2><span class="numero">Capítulo 6<span class="marcador">@@c6@@</span></span>Qué gastos se ahorran y cuáles no</h2>

  <p class="entradilla">El proyecto ahorra %(aporte)s en aportes valorizados, es decir el %(pct)s%% del
    valor total. Aquí está el detalle de dónde viene ese ahorro y, sobre todo, de lo que no se puede
    ahorrar.</p>

  <h3>De dónde viene el aporte</h3>
  <div class="tabla-envoltura">
  <table>
    <thead><tr><th>Origen del aporte</th><th class="num">Monto valorizado</th><th class="num">%% del aporte</th></tr></thead>
    <tbody>%(filas)s
      <tr class="total"><td>Total aportado</td><td class="num">%(aporte)s</td><td class="num">100,0%%</td></tr>
    </tbody>
  </table>
  </div>

  <h3>Lo que se ahorra, con monto</h3>
  <div class="tabla-envoltura">
  <table class="compacta">
    <thead><tr><th style="width:30%%">Concepto</th><th class="num" style="width:16%%">Monto</th><th>Por qué</th></tr></thead>
    <tbody>
      <tr><td>Terreno</td><td class="num">Sin costo</td><td>Es fiscal y se obtiene por concesión de uso gratuito: no se compra ni se arrienda.</td></tr>
      <tr><td>Mano de obra de cuatro jornales</td><td class="num">%(cuadrilla)s</td><td>Cuadrilla municipal existente destinada a la obra.</td></tr>
      <tr><td>Madera de postes, listones, paneles, torre, pérgolas, amarre, juegos y techos</td><td class="num">%(muni)s</td><td>Árboles que el municipio retira por temporal, riesgo o poda, aserrados en terreno, más compost municipal y el contenedor bodega.</td></tr>
      <tr><td>Bancas, tótems, tablas grabadas, bebederos, arcos y letreros</td><td class="num">%(liceo)s</td><td>Fabricación del liceo técnico contra un aporte de insumos de $1.500.000.</td></tr>
      <tr><td>Arbustos nativos, plantación y asesoría</td><td class="num">%(conaf)s</td><td>Convenio de arborización comunitaria con CONAF.</td></tr>
      <tr><td>Herramientas y equipos de faena</td><td class="num">%(herr)s</td><td>Se compran una vez y se reutilizan en los caniles 2 y 3: el ahorro se produce en las etapas siguientes.</td></tr>
      <tr><td>Cuentas de luz y de agua</td><td class="num">Permanente</td><td>Energía solar y pozo propio: el recinto no tiene empalme eléctrico ni conexión a la red de agua potable.</td></tr>
      <tr><td>Vigilancia, veterinario y retiro de residuos</td><td class="num">Servicios existentes</td><td>Central municipal de cámaras, veterinario municipal y recorrido de aseo ya operativos.</td></tr>
    </tbody>
  </table>
  </div>

  <h3>Lo que no se ahorra</h3>
  <p>Hay una parte del proyecto que hay que pagar sí o sí, y conviene que quede dicho con claridad para
    que nadie espere que el canil se construya solo con aportes:</p>
  <div class="tabla-envoltura">
  <table class="compacta">
    <thead><tr><th style="width:34%%">Concepto</th><th class="num" style="width:18%%">Monto a financiar</th><th>Observación</th></tr></thead>
    <tbody>
      <tr><td>Baño público y su sistema sanitario</td><td class="num">%(bano)s</td><td>Es el ítem más caro del proyecto y no tiene reemplazo por aporte.</td></tr>
      <tr><td>Pozo, bomba solar y derechos de agua</td><td class="num">%(pozo)s</td><td>Incluye perforación, desarrollo, bomba, paneles y el trámite ante la DGA.</td></tr>
      <tr><td>Estudios, proyectos y trámites</td><td class="num">%(estudios)s</td><td>Exigidos por normativa; solo el diseño puede reducirse con profesionales municipales.</td></tr>
      <tr><td>Malla, alambre y ferretería del cerco</td><td class="num">%(ferreteria)s</td><td>No hay forma de producirlos localmente.</td></tr>
      <tr><td>Sistema solar, cámaras, cerraduras y tótem SOS</td><td class="num">%(energia)s</td><td>Es lo que permite operar sin personal en terreno.</td></tr>
      <tr><td>Mano de obra especializada y servicios</td><td class="num">%(mano)s</td><td>Jefe de obra, carpinteros, gasfíter, electricista, prevencionista, maquinaria y camión.</td></tr>
      <tr><td>Operación anual</td><td class="num">%(op)s</td><td>Auxiliares de aseo, insumos, datos, análisis de agua, seguro y reposición. Se repite todos los años.</td></tr>
    </tbody>
  </table>
  </div>
</section>""" % {
        "aporte": pesos(d["aporte"]),
        "pct": numero(100.0 * d["aporte"] / d["total_val"], 1),
        "filas": filas_ap,
        "cuadrilla": pesos(aporte_por_origen.get(CUADRILLA, 0)),
        "muni": pesos(aporte_por_origen.get(MUNI, 0)),
        "liceo": pesos(aporte_por_origen.get(LICEO, 0)),
        "conaf": pesos(aporte_por_origen.get(CONAF, 0)),
        "herr": pesos(herramientas),
        "bano": pesos(suma("D.1", "D.2", "D.3", "D.4", "D.5", "D.6", "D.7")),
        "pozo": pesos(suma("E.4", "E.5", "E.6", "E.7", "E.8", "E.9", "A.6", "A.7")),
        "estudios": pesos(suma("A.1", "A.2", "A.3", "A.4", "A.5", "A.9", "A.10")),
        "ferreteria": pesos(suma("C.1", "C.2", "C.3", "C.4", "C.9", "C.11", "C.12", "C.13", "C.14", "C.15", "C.17")),
        "energia": pesos(suma("F.1", "F.2", "F.3", "F.4", "F.5", "F.6", "F.7", "F.8", "F.9", "F.11", "F.12")),
        "mano": pesos(suma("I.1", "I.2", "I.4", "I.5", "I.6", "I.7", "I.8")),
        "op": pesos(d["op_fin"]) + " al año",
    })

    # ---------------- 7. Operación anual ----------------
    filas_op = ""
    for cod, desc, cant, un, pu, tot, origen, nota in d["operacion"]:
        clase = "" if origen == COMPRA else ' class="aporte"'
        filas_op += (
            "<tr%s><td>%s</td><td>%s</td><td class=\"num\">%s</td><td>%s</td>"
            "<td class=\"num\">%s</td><td class=\"num\">%s</td><td>%s</td></tr>"
            % (clase, cod, desc, cantidad(cant), un, pesos(pu), pesos(tot), origen)
        )
    notas_op = "".join("<tr><td>%s</td><td>%s</td></tr>" % (o[0], o[7]) for o in d["operacion"])
    costo_visita = d["op_fin"] / VISITAS_ANO
    costo_visita3 = d["op_fin"] / VISITAS_ANO3

    partes.append("""
<section class="seccion">
  <h2><span class="numero">Capítulo 7<span class="marcador">@@c7@@</span></span>Operación anual</h2>

  <p class="entradilla">Lo que cuesta mantener el canil funcionando durante un año completo, con
    personal de aseo, insumos, servicios y provisiones de reposición.</p>

  <div class="cifras cuatro">
    <div class="cifra"><span class="dato">%(fin)s</span><span class="glosa">Operación anual a financiar</span></div>
    <div class="cifra"><span class="dato">%(mes)s</span><span class="glosa">Costo mensual a financiar</span></div>
    <div class="cifra"><span class="dato">%(apo)s</span><span class="glosa">Aporte municipal anual valorizado</span></div>
    <div class="cifra"><span class="dato">%(visita)s</span><span class="glosa">Costo de operación por visita, año 1</span></div>
  </div>

  <div class="tabla-envoltura">
  <table class="compacta presupuesto">
    <thead><tr><th>Código</th><th>Ítem</th><th class="num">Cant.</th><th>Unidad</th>
      <th class="num">Precio unitario</th><th class="num">Subtotal</th><th>Origen</th></tr></thead>
    <tbody>%(filas)s
      <tr class="total"><td colspan="5">Total operación anual valorizada</td><td class="num">%(val)s</td>
        <td>A financiar %(fin)s</td></tr>
    </tbody>
  </table>
  </div>

  <h3>Por qué cada ítem</h3>
  <div class="tabla-envoltura">
  <table class="compacta">
    <thead><tr><th style="width:10%%">Código</th><th>Justificación</th></tr></thead>
    <tbody>%(notas)s</tbody>
  </table>
  </div>

  <h3>Costo por visita</h3>
  <p>Con 38.108 visitas proyectadas el primer año, el costo de operación por visita es de
    <strong>%(visita)s</strong>. Al tercer año, con 45.729 visitas, baja a <strong>%(visita3)s</strong>
    sin aumentar el gasto: la operación es prácticamente fija y el costo unitario mejora con el uso. Es
    la razón por la que la difusión del recinto no es un gasto accesorio, sino parte de la eficiencia
    del proyecto.</p>

  <div class="destacado">
    <div class="titulo">El %(pct_aseo)s%% de la operación es aseo</div>
    <p>Los dos auxiliares de aseo son %(aseo)s de los %(fin)s anuales a financiar. Todo lo demás
      —insumos, datos, control de roedores, análisis de agua, seguro y provisiones de reposición— suma
      menos de un tercio. Cualquier mejora de eficiencia en la operación pasa por cómo se organizan esos
      turnos, no por recortar insumos.</p>
  </div>
</section>""" % {
        "filas": filas_op,
        "notas": notas_op,
        "val": pesos(d["op_val"]),
        "fin": pesos(d["op_fin"]),
        "apo": pesos(d["op_aporte"]),
        "mes": pesos(d["op_fin"] / 12.0),
        "visita": pesos(costo_visita),
        "visita3": pesos(costo_visita3),
        "aseo": pesos(16170000),
        "pct_aseo": numero(100.0 * 16170000 / d["op_fin"]),
    })

    # ---------------- 8. Proyección 3 caniles ----------------
    descuento = herramientas
    contenedor = 2500000
    directo_fin_2 = (d["directo_fin"] - descuento) * (1 + IPC)
    gg2 = directo_fin_2 * GG
    imp2 = (directo_fin_2 + gg2) * IMPREVISTOS
    total_2 = directo_fin_2 + gg2 + imp2
    aporte_2 = (d["aporte"] - contenedor) * (1 + IPC)
    total_3 = d["total_fin"] + 2 * total_2
    aporte_3 = d["aporte"] + 2 * aporte_2
    utm_2 = total_2 / UTM

    partes.append("""
<section class="seccion">
  <h2><span class="numero">Capítulo 8<span class="marcador">@@c8@@</span></span>Proyección de los tres caniles y tope PMU</h2>

  <p class="entradilla">Cada canil se formula y se ejecuta por separado. Los caniles 2 y 3 descuentan
    las herramientas y el contenedor bodega, que ya se compraron para el piloto, e incorporan un reajuste
    de 3,5%% por inflación.</p>

  <div class="tabla-envoltura">
  <table>
    <thead><tr><th>Canil</th><th class="num">A financiar</th><th class="num">Aporte valorizado</th>
      <th class="num">Total valorizado</th><th class="num">UTM</th><th class="cen">¿Bajo el tope?</th></tr></thead>
    <tbody>
      <tr><td>Canil 1 · piloto (etapa 1)</td><td class="num">%(t1)s</td><td class="num">%(a1)s</td>
        <td class="num">%(v1)s</td><td class="num">%(u1)s</td><td class="cen">Sí</td></tr>
      <tr><td>Canil 2 (etapa 2)</td><td class="num">%(t2)s</td><td class="num">%(a2)s</td>
        <td class="num">%(v2)s</td><td class="num">%(u2)s</td><td class="cen">Sí</td></tr>
      <tr><td>Canil 3 (etapa 2)</td><td class="num">%(t2)s</td><td class="num">%(a2)s</td>
        <td class="num">%(v2)s</td><td class="num">%(u2)s</td><td class="cen">Sí</td></tr>
      <tr class="total"><td>Total de los tres caniles</td><td class="num">%(t3)s</td><td class="num">%(a3)s</td>
        <td class="num">%(v3)s</td><td class="num">%(u3)s</td><td class="cen">—</td></tr>
    </tbody>
  </table>
  <p class="nota-tabla">El tope del PMU es de 2.500 UTM <strong>por proyecto</strong>, equivalentes a
    %(tope)s. Cada canil queda holgadamente bajo ese límite; la suma de los tres no compite con el tope
    porque se formulan como proyectos independientes y se ejecutan en momentos distintos.</p>
  </div>

  <h3>Cómo se construyen las cifras de los caniles 2 y 3</h3>
  <div class="tabla-envoltura">
  <table>
    <thead><tr><th>Concepto</th><th class="num" style="width:22%%">Monto</th><th style="width:34%%">Explicación</th></tr></thead>
    <tbody>
      <tr><td>Costo directo a financiar del piloto</td><td class="num">%(df1)s</td><td>Base de cálculo.</td></tr>
      <tr><td>Herramientas y equipos que no se repiten</td><td class="num">−%(herr)s</td><td>Ítems B.4 a B.11, comprados una sola vez.</td></tr>
      <tr><td>Reajuste por inflación (3,5%%)</td><td class="num">+%(reaj)s</td><td>IPC de 12 meses aplicado al costo directo.</td></tr>
      <tr><td>Costo directo a financiar</td><td class="num">%(df2)s</td><td></td></tr>
      <tr><td>Gastos generales e imprevistos</td><td class="num">%(ggimp)s</td><td>Mismos porcentajes que en el piloto.</td></tr>
      <tr class="total"><td>Total por canil replicado</td><td class="num">%(t2)s</td><td>%(u2)s UTM</td></tr>
    </tbody>
  </table>
  </div>

  <h3>Operación de los tres caniles</h3>
  <div class="tabla-envoltura">
  <table>
    <thead><tr><th>Concepto</th><th class="num">Un canil</th><th class="num">Tres caniles</th></tr></thead>
    <tbody>
      <tr><td>Operación anual a financiar</td><td class="num">%(op1)s</td><td class="num">%(op3)s</td></tr>
      <tr><td>Aporte municipal anual valorizado</td><td class="num">%(opa1)s</td><td class="num">%(opa3)s</td></tr>
      <tr><td>Visitas anuales proyectadas</td><td class="num">%(vis1)s</td><td class="num">%(vis3)s</td></tr>
      <tr><td>Costo de operación por visita</td><td class="num">%(cv)s</td><td class="num">%(cv)s</td></tr>
    </tbody>
  </table>
  <p class="nota-tabla">La proyección de tres caniles supone, de forma conservadora, que cada recinto se
    opera por separado y con su propio personal. El capítulo 11 muestra cuánto baja este costo si la
    operación se organiza en red.</p>
  </div>
</section>""" % {
        "t1": pesos(d["total_fin"]), "a1": pesos(d["aporte"]), "v1": pesos(d["total_val"]), "u1": numero(d["utm"]),
        "t2": pesos(total_2), "a2": pesos(aporte_2), "v2": pesos(total_2 + aporte_2), "u2": numero(utm_2),
        "t3": pesos(total_3), "a3": pesos(aporte_3), "v3": pesos(total_3 + aporte_3),
        "u3": numero(total_3 / UTM),
        "tope": pesos(TOPE_PMU),
        "df1": pesos(d["directo_fin"]),
        "herr": pesos(descuento),
        "reaj": pesos((d["directo_fin"] - descuento) * IPC),
        "df2": pesos(directo_fin_2),
        "ggimp": pesos(gg2 + imp2),
        "op1": pesos(d["op_fin"]), "op3": pesos(d["op_fin"] * 3),
        "opa1": pesos(d["op_aporte"]), "opa3": pesos(d["op_aporte"] * 3),
        "vis1": numero(VISITAS_ANO), "vis3": numero(VISITAS_ANO * 3),
        "cv": pesos(costo_visita),
    })

    # ---------------- 9. Evaluación económica ----------------
    visitas_10 = VISITAS_ANO + 9 * VISITAS_ANO3
    inv_por_visita = d["total_fin"] / visitas_10
    partes.append("""
<section class="seccion">
  <h2><span class="numero">Capítulo 9<span class="marcador">@@c9@@</span></span>Evaluación económica</h2>

  <p class="entradilla">Qué se obtiene por lo que se invierte. Este capítulo existe porque un
    presupuesto no se aprueba solo por estar bien sumado: hay que poder comparar el gasto con el
    beneficio.</p>

  <h3>Indicadores de inversión</h3>
  <div class="tabla-envoltura">
  <table>
    <thead><tr><th>Indicador</th><th class="num" style="width:20%%">Valor</th><th style="width:38%%">Cómo se calcula</th></tr></thead>
    <tbody>
      <tr><td>Inversión a financiar por habitante de la comuna</td><td class="num">%(porhab)s</td><td>%(total)s ÷ %(hab)s habitantes (Censo 2024).</td></tr>
      <tr><td>Inversión valorizada por perro del sector</td><td class="num">%(porperro)s</td><td>%(totalval)s ÷ %(perros)s perros estimados en el sector del canil.</td></tr>
      <tr><td>Inversión por visita, amortizada a 10 años</td><td class="num">%(porvisita)s</td><td>%(total)s ÷ %(vis10)s visitas proyectadas en 10 años.</td></tr>
      <tr><td>Costo total por visita el año 1 (operación más inversión amortizada)</td><td class="num">%(totvisita)s</td><td>%(cv)s de operación más %(porvisita)s de inversión.</td></tr>
      <tr><td>Aporte valorizado sobre el total del proyecto</td><td class="num">%(pctap)s%%</td><td>%(aporte)s de %(totalval)s.</td></tr>
      <tr><td>Retorno referencial de la inversión en parques</td><td class="num">%(retorno)s</td><td>Criterio del Trust for Public Land: al menos US$3 por cada US$1 invertido, aplicado al valor total del proyecto.</td></tr>
    </tbody>
  </table>
  <p class="nota-tabla">El retorno de 3 a 1 es un criterio internacional de referencia para inversión en
    parques, no una estimación hecha para este proyecto: se incluye como orden de magnitud y no como
    resultado calculado.</p>
  </div>

  <h3>Beneficios que el presupuesto no monetiza</h3>
  <p>Hay efectos esperados que este documento <strong>no</strong> convierte en pesos, porque no existe
    una cifra oficial local que lo permita y sería un error presentarlos como ahorro garantizado. Se
    dejan enunciados para que la mesa técnica decida si los valoriza con datos propios:</p>
  <ul class="marcas">
    <li><strong>Atenciones de salud por mordeduras evitadas.</strong> La comuna tiene una base estimada
      de 175 atenciones al año. Cada atención tiene un costo para la red asistencial que no está
      publicado a nivel comunal.</li>
    <li><strong>Ataques de perros a ganado y fauna.</strong> La Región de Los Lagos encabeza las
      denuncias del SAG. El daño por animal atacado es cuantificable por el propio sector ganadero.</li>
    <li><strong>Aseo de playas, costanera y plazas.</strong> Concentrar las fecas en un recinto con
      bolsas y basureros reduce carga de trabajo en el resto del espacio público.</li>
    <li><strong>Turismo.</strong> El 42%% de los viajeros declara que poder llevar su mascota influye en
      la elección del destino, en una comuna que alcanzó 81,3%% de ocupación en enero.</li>
    <li><strong>Salud de las personas.</strong> Más actividad física al aire libre en una comuna cuya
      población de 60 años y más creció 45,9%% desde 2017.</li>
  </ul>

  <h3>El costo de no hacer nada</h3>
  <p>La alternativa actual no es gratuita: es el uso intensivo de playas, costanera y plazas por perros
    sueltos, con los conflictos, reclamos y trabajo de aseo que eso implica, y sin ningún lugar donde
    hacer entrenamiento, operativos de chip o cursos de obediencia. Ese costo hoy se paga distribuido en
    varias direcciones municipales y no aparece en ninguna línea presupuestaria.</p>

  <div class="destacado">
    <div class="titulo">Comparación con el tope del fondo</div>
    <p>El proyecto usa %(pcttope)s%% del tope disponible del PMU y deja %(margen)s de margen. Ese margen
      es el espacio real que tiene la mesa técnica para absorber cotizaciones más altas —especialmente en
      el pozo, el baño y el tótem SOS— sin salirse del marco de financiamiento.</p>
  </div>
</section>""" % {
        "porhab": pesos(d["total_fin"] / HABITANTES),
        "total": pesos(d["total_fin"]),
        "hab": numero(HABITANTES),
        "porperro": pesos(d["total_val"] / PERROS_SECTOR),
        "totalval": pesos(d["total_val"]),
        "perros": numero(PERROS_SECTOR),
        "porvisita": pesos(inv_por_visita),
        "vis10": numero(visitas_10),
        "totvisita": pesos(costo_visita + inv_por_visita),
        "cv": pesos(costo_visita),
        "pctap": numero(100.0 * d["aporte"] / d["total_val"], 1),
        "aporte": pesos(d["aporte"]),
        "retorno": pesos(d["total_val"] * 3),
        "pcttope": numero(100.0 * d["total_fin"] / TOPE_PMU, 1),
        "margen": pesos(TOPE_PMU - d["total_fin"]),
    })

    # ---------------- 10. Metas ----------------
    partes.append("""
<section class="seccion">
  <h2><span class="numero">Capítulo 10<span class="marcador">@@c10@@</span></span>Metas proyectadas</h2>

  <p class="entradilla">Las metas del canil piloto y la base de cálculo con que se construyeron. Son
    metas propuestas: la línea base local se levanta en la etapa 1 y las metas definitivas las fija la
    mesa técnica antes de abrir.</p>

  <h3>Base de cálculo</h3>
  <div class="tabla-envoltura">
  <table class="compacta">
    <thead><tr><th style="width:46%%">Dato</th><th class="num">Valor</th><th>Origen</th></tr></thead>
    <tbody>
      <tr><td>Perros estimados en la comuna (rango)</td><td class="num">%(pb)s a %(pa)s</td><td>Cálculo propio sobre población comunal y tasas nacionales</td></tr>
      <tr><td>Promedio usado</td><td class="num">%(pp)s</td><td>Punto medio del rango</td></tr>
      <tr><td>Perros del sector del canil piloto</td><td class="num">%(ps)s</td><td>Un tercio de la comuna</td></tr>
      <tr><td>Uso proyectado</td><td class="num">10%% por semana</td><td>Supuesto de demanda</td></tr>
      <tr><td>Visitas semanales</td><td class="num">%(vs)s</td><td>10%% de los perros del sector</td></tr>
      <tr><td>Visitas diarias</td><td class="num">%(vd)s</td><td>Visitas semanales ÷ 7</td></tr>
      <tr><td>Visitas mensuales</td><td class="num">%(vm)s</td><td>Visitas diarias × 30</td></tr>
      <tr><td>Visitas anuales</td><td class="num">%(va)s</td><td>Visitas diarias × 365</td></tr>
      <tr><td>Mordeduras base en la comuna</td><td class="num">175 al año</td><td>60.986 atenciones nacionales (2023) llevadas a la población comunal</td></tr>
      <tr><td>Nuevas inscripciones base</td><td class="num">1.066 al año</td><td>Registro Nacional de Mascotas llevado a la población comunal</td></tr>
    </tbody>
  </table>
  </div>

  <h3>Metas e indicadores</h3>
  <div class="tabla-envoltura">
  <table>
    <thead><tr><th>Indicador</th><th>Línea base</th><th class="cen">Meta año 1</th><th class="cen">Meta año 3</th><th>Medición</th></tr></thead>
    <tbody>
      <tr><td>Visitas diarias</td><td>0</td><td class="cen">104</td><td class="cen">125</td><td>Contador automático</td></tr>
      <tr><td>Visitas anuales</td><td>0</td><td class="cen">38.108</td><td class="cen">45.729</td><td>Contador automático</td></tr>
      <tr><td>Reclamos por perros en playas, costanera y plazas</td><td>Por levantar</td><td class="cen">−15%%</td><td class="cen">−30%%</td><td>OIRS y Seguridad Pública</td></tr>
      <tr><td>Fecas en recorridos de muestra</td><td>Por levantar</td><td class="cen">−20%%</td><td class="cen">−35%%</td><td>5 recorridos fijos mensuales</td></tr>
      <tr><td>Nuevas inscripciones en la comuna</td><td>1.066</td><td class="cen">1.279</td><td class="cen">1.439</td><td>Registro Nacional de Mascotas</td></tr>
      <tr><td>Chips y antirrábicas en operativos</td><td>0</td><td class="cen">200</td><td class="cen">250</td><td>Veterinario municipal, 4 operativos</td></tr>
      <tr><td>Mordeduras atendidas en la comuna</td><td>175</td><td class="cen">166</td><td class="cen">157</td><td>Seremi de Salud</td></tr>
      <tr><td>Denuncias SAG en la comuna</td><td>Por levantar</td><td class="cen">−10%%</td><td class="cen">−20%%</td><td>SAG Los Lagos</td></tr>
      <tr><td>Satisfacción de personas usuarias (1 a 5)</td><td>—</td><td class="cen">4,0</td><td class="cen">4,3</td><td>Encuesta por QR</td></tr>
      <tr><td>Costo de operación por visita</td><td>—</td><td class="cen">%(cv)s</td><td class="cen">%(cv3)s</td><td>Operación anual ÷ visitas</td></tr>
    </tbody>
  </table>
  </div>


</section>""" % {
        "pb": numero(PERROS_COMUNA_BAJO), "pa": numero(PERROS_COMUNA_ALTO),
        "pp": numero(PERROS_PROMEDIO), "ps": numero(PERROS_SECTOR),
        "vs": numero(VISITAS_SEMANA), "vd": numero(VISITAS_DIA),
        "vm": numero(VISITAS_MES), "va": numero(VISITAS_ANO),
        "cv": pesos(costo_visita), "cv3": pesos(costo_visita3),
    })

    # ---------------- 11. Ahorros adicionales ----------------
    ahorro_grava = 3594544
    ahorro_diseno = 6000000
    factor_gg = (1 + GG) * (1 + IMPREVISTOS)
    ahorro_piloto = (ahorro_grava + ahorro_diseno) * factor_gg
    ahorro_tipo = 4500000 * (1 + IPC) * factor_gg
    aseo_red = 2 * 12 * 673750
    op3_red = d["op_fin"] * 3 - aseo_red
    visitas3 = VISITAS_ANO * 3

    partes.append("""
<section class="seccion">
  <h2><span class="numero">Capítulo 11<span class="marcador">@@c11@@</span></span>Ahorros adicionales identificados</h2>

  <p class="entradilla">El presupuesto base es deliberadamente conservador: no descuenta nada que no
    esté confirmado. Estos son los ahorros que existen y que, al confirmarse, bajan el monto del proyecto
    o el costo de operación.</p>

  <h3>En la inversión del piloto</h3>
  <div class="tabla-envoltura">
  <table>
    <thead><tr><th style="width:30%%">Ahorro</th><th class="num" style="width:18%%">Efecto</th><th>Condición para que se concrete</th></tr></thead>
    <tbody>
      <tr><td>Grava del propio terreno o de pozo de áridos municipal</td><td class="num">−%(grava)s</td><td>Que la Dirección de Obras confirme material utilizable en el terreno o excedentes de otras obras, con la calidad necesaria para senderos y bases.</td></tr>
      <tr><td>Diseño con profesionales municipales</td><td class="num">−%(diseno)s</td><td>Que Secplan y la Dirección de Obras asuman el diseño de arquitectura y especialidades en vez de contratarlo.</td></tr>
      <tr class="total"><td>Efecto conjunto sobre el total del proyecto</td><td class="num">−%(piloto)s</td><td>El total bajaría de %(base)s a %(nuevo)s, es decir %(nutm)s UTM.</td></tr>
    </tbody>
  </table>
  <p class="nota-tabla">El efecto incluye el arrastre de gastos generales e imprevistos, porque ambos se
    calculan como porcentaje del costo directo.</p>
  </div>

  <h3>En los caniles 2 y 3: el proyecto tipo</h3>
  <p>El expediente técnico del piloto —planos, especificaciones, detalles constructivos y presupuesto—
    queda como proyecto tipo de la municipalidad. Los caniles del sur y del norte no necesitan un diseño
    nuevo, sino la adecuación del existente al terreno que corresponda. Si el diseño de la partida A.2
    baja de $6.000.000 a $1.500.000 en cada réplica, el ahorro es de <strong>%(tipo)s por canil</strong>,
    es decir %(tipo2)s en las dos etapas siguientes.</p>

  <h3>En la operación, cuando existan los tres caniles</h3>
  <div class="tabla-envoltura">
  <table>
    <thead><tr><th>Escenario de operación de los tres caniles</th><th class="num">Costo anual a financiar</th><th class="num">Costo por visita</th></tr></thead>
    <tbody>
      <tr><td>Tres recintos operados por separado, con dos auxiliares cada uno</td><td class="num">%(op3)s</td><td class="num">%(cv)s</td></tr>
      <tr><td>Operación en red: cuatro auxiliares en rutas que cubren los tres recintos</td><td class="num">%(op3red)s</td><td class="num">%(cvred)s</td></tr>
      <tr class="total"><td>Diferencia anual</td><td class="num">−%(dif)s</td><td class="num">−%(difcv)s</td></tr>
    </tbody>
  </table>
  <p class="nota-tabla">El escenario en red supone rutas de aseo que cubren más de un recinto por turno,
    una sola cuadrilla mensual de mantención para los tres caniles, compras de insumos consolidadas y un
    único contrato de datos. Requiere que los tres recintos ya estén construidos y que la Dirección de
    Aseo y Ornato valide los tiempos de traslado entre sectores.</p>
  </div>

  <h3>La palanca más grande: los puntos de luz</h3>
  <p>Las treinta luminarias solares suman %(luminarias)s, el %(pctlum)s%% del costo directo a
    financiar, después de corregir su precio a valor de mercado. El recinto cierra a las 21:00 y los
    sectores libres no necesitan iluminación: la luz hace falta en la zona de acceso, en las esclusas,
    en el sendero accesible y en el sendero a los sectores de entrenamiento.
    <strong>Reducir de 30 a 16 puntos de luz ahorra %(ahorrolum)s</strong> de costo directo, sin
    afectar la seguridad dentro del horario de funcionamiento. Es una decisión de diseño que
    corresponde tomar con la Dirección de Obras y con Seguridad Pública; el presupuesto base mantiene
    los treinta puntos.</p>

  <h3>Otras vías de reducción</h3>
  <ul class="marcas">
    <li><strong>Plataforma de Economía Circular:</strong> además del contenedor bodega, pueden obtenerse
      sin costo basureros, mobiliario y equipamiento dados de baja por otros servicios públicos. Cada
      ítem que salga por esta vía se descuenta del presupuesto.</li>
    <li><strong>Convenio Marco:</strong> comprar con precios ya licitados evita sobreprecios en los
      ítems referenciales y acorta los plazos de adquisición.</li>
    <li><strong>Aportes privados en especies</strong> de empresas del rubro mascotas y del turismo local
      —bolsas compostables, insumos de operativos, reposición de piezas—, bajo convenio anual revocable,
      sin publicidad dentro de los sectores y sin que ningún aporte condicione el reglamento ni el uso
      del canil. Es una vía a evaluar con Asesoría Jurídica: el proyecto no depende de ella.</li>
    <li><strong>Fondo Concursable de Tenencia Responsable:</strong> financia los entrenadores y cursos
      del sector de perros complicados a través de una organización sin fines de lucro inscrita en el
      registro correspondiente, de modo que ese costo no recae en el presupuesto municipal de
      operación.</li>
  </ul>
</section>""" % {
        "grava": pesos(ahorro_grava), "diseno": pesos(ahorro_diseno),
        "piloto": pesos(ahorro_piloto), "base": pesos(d["total_fin"]),
        "nuevo": pesos(d["total_fin"] - ahorro_piloto),
        "nutm": numero((d["total_fin"] - ahorro_piloto) / UTM),
        "tipo": pesos(ahorro_tipo), "tipo2": pesos(ahorro_tipo * 2),
        "op3": pesos(d["op_fin"] * 3), "op3red": pesos(op3_red),
        "cv": pesos(d["op_fin"] * 3 / visitas3), "cvred": pesos(op3_red / visitas3),
        "dif": pesos(aseo_red), "difcv": pesos(aseo_red / visitas3),
        "luminarias": pesos(suma("F.9")),
        "pctlum": numero(100.0 * suma("F.9") / d["directo_fin"], 1),
        "ahorrolum": pesos(14 * 389990),
    })

    # ---------------- 12. Fuentes ----------------
    partes.append("""
<section class="seccion">
  <h2><span class="numero">Capítulo 12<span class="marcador">@@c12@@</span></span>Fuentes de precios y advertencias</h2>

  <p class="entradilla">De dónde salió cada precio verificado y qué hay que hacer antes de ejecutar.</p>

  <h3>Fuentes de precios</h3>
  <div class="tabla-envoltura">
  <table class="compacta">
    <thead><tr><th style="width:28%">Fuente</th><th>Ítems</th></tr></thead>
    <tbody>
      <tr><td>Sodimac.cl</td><td>Mallas Inchalam 5014, polines y pino, anclajes IDAF, estanques y fosas Amerplast, aceite impregnante de 20 L, referencia de luminarias solares de consumo.</td></tr>
      <tr><td>Easy.cl</td><td>Alambre galvanizado 2,11 mm en rollo de 25 kg.</td></tr>
      <tr><td>Falabella.cl</td><td>Aserradero portátil para motosierra.</td></tr>
      <tr><td>Full Áridos / CMGC</td><td>Grava y compost por metro cúbico.</td></tr>
      <tr><td>Cruzat Ingeniería, 2026</td><td>Perforación de pozo por metro.</td></tr>
      <tr><td>Club del Agua, 2026</td><td>Estudio hidrogeológico.</td></tr>
      <tr><td>Obramat (España)</td><td>Bomba solar sumergible de 1,1 kW con controlador.</td></tr>
      <tr><td>Sungold Power</td><td>Paneles solares de 550 W.</td></tr>
      <tr><td>Autosolar (España)</td><td>Kit solar aislado con batería de 5 kWh.</td></tr>
      <tr><td>MediaWorld (Italia)</td><td>Cámara Ezviz EB3 con panel solar.</td></tr>
      <tr><td>Estrella de Iquique</td><td>Referencia de tótems de emergencia: $345 millones por 23 unidades.</td></tr>
      <tr><td>hacecuentas.com, con base CChC y Minvu</td><td>Costo de construcción por metro cuadrado, 2026.</td></tr>
      <tr><td>Chiletrabajos y Mega</td><td>Sueldos de carpintero, gásfiter y eléctrico en construcción.</td></tr>
      <tr><td>Carey</td><td>Ingreso mínimo mensual 2026.</td></tr>
      <tr><td>Buk y Banco Central</td><td>Valor de la UF.</td></tr>
      <tr><td>Servicio de Impuestos Internos</td><td>Valor de la UTM.</td></tr>
      <tr><td>Infobae y Banco Central vía finclaro</td><td>Tipos de cambio de euro y dólar.</td></tr>
      <tr><td>Seremi de Salud</td><td>Arancel de autorización sanitaria.</td></tr>
      <tr><td>Natura Energy</td><td>Luminaria solar integrada de 40 W IP65 para alumbrado público.</td></tr>
      <tr><td>Scanavini</td><td>Cerradura electromagnética para puerta de abatir.</td></tr>
      <tr><td>Jurmaq, 2026</td><td>Arriendo de retroexcavadora con operador, por hora.</td></tr>
      <tr><td>2x3.cl, 2026</td><td>Arriendo mensual de baño químico con lavamanos.</td></tr>
      <tr><td>Computrabajo, 2026</td><td>Sueldo promedio de prevencionista de riesgos.</td></tr>
      <tr><td>Colegio de Arquitectos</td><td>Arancel referencial de honorarios de proyecto.</td></tr>
    </tbody>
  </table>
  </div>

  <h3>Ajustes por revisión de mercado</h3>
  <p>Los precios referenciales de la primera versión de este presupuesto se contrastaron uno a uno
    contra precios publicados de proveedores chilenos en 2026. Siete ítems cambiaron, en los dos
    sentidos: cuatro estaban por sobre el mercado y tres por debajo. El más importante es el de las
    luminarias solares: el valor anterior correspondía a productos de consumo que no resisten uso
    público intensivo, y una luminaria integrada de grado público cuesta seis veces más.</p>
  <div class="tabla-envoltura">
  <table class="compacta">
    <thead><tr><th style="width:24%">Ítem</th><th class="num">Antes</th><th class="num">Corregido</th>
      <th class="num">Efecto</th><th style="width:30%">Fuente del precio</th></tr></thead>
    <tbody>
      <tr><td>A.1 Levantamiento topográfico</td><td class="num">$1.500.000</td><td class="num">$800.000</td>
        <td class="num">−$700.000</td><td>Rango de mercado de $150.000 a $800.000</td></tr>
      <tr><td>B.2 Baño químico, 4 meses</td><td class="num">$120.000/mes</td><td class="num">$119.000/mes</td>
        <td class="num">−$4.000</td><td>2x3.cl: $100.000 + IVA con lavamanos</td></tr>
      <tr><td>F.8 Cerraduras, 5 unidades</td><td class="num">$180.000</td><td class="num">$175.000</td>
        <td class="num">−$25.000</td><td>Scanavini: $155.530 más temporizador</td></tr>
      <tr><td>F.9 Luminarias solares, 30 unidades</td><td class="num">$65.000</td><td class="num">$389.990</td>
        <td class="num">+$9.749.700</td><td>Natura Energy: integrada 40 W IP65</td></tr>
      <tr><td>I.6 Prevencionista, 4 meses</td><td class="num">$400.000/mes</td><td class="num">$566.000/mes</td>
        <td class="num">+$664.000</td><td>Computrabajo 2026: promedio $905.427</td></tr>
      <tr><td>I.7 Retroexcavadora, 24 horas</td><td class="num">$45.000/hora</td><td class="num">$35.000/hora</td>
        <td class="num">−$240.000</td><td>Jurmaq 2026: $25.000 a $35.000 con operador</td></tr>
      <tr><td>I.8 Camión con chofer, 10 días</td><td class="num">$180.000/día</td><td class="num">$250.000/día</td>
        <td class="num">+$700.000</td><td>Tolva de 15 m³ con chofer y combustible</td></tr>
      <tr class="total"><td>Efecto neto en el costo directo</td><td class="num">—</td><td class="num">—</td>
        <td class="num">+$10.144.700</td><td>+$12.051.903 con gastos generales e imprevistos</td></tr>
    </tbody>
  </table>
  <p class="nota-tabla">Corregir al alza donde el mercado es más caro es lo que evita que la obra se
    detenga a mitad de camino por un presupuesto insuficiente. Con estos ajustes el proyecto sigue
    holgadamente bajo el tope de 2.500 UTM del PMU.</p>
  </div>

  <h3>Qué hacer antes de ejecutar</h3>
  <ol>
    <li><strong>Cotizar los ítems referenciales</strong>, partiendo por los de mayor monto: tótem SOS,
      luminarias de grado público, cerraduras electromagnéticas, cañerías y fittings, honorarios
      profesionales, retroexcavadora y camión.</li>
    <li><strong>Confirmar la profundidad real del pozo</strong> con el estudio hidrogeológico. Es la
      variable que más mueve el total.</li>
    <li><strong>Encargar el cálculo estructural de la torre de agua</strong>, que sostiene once
      toneladas.</li>
    <li><strong>Cotizar el baño llave en mano</strong> con constructoras locales y comparar con el valor
      de 30 UF/m² usado aquí.</li>
    <li><strong>Revisar la Plataforma de Economía Circular</strong> y el Convenio Marco antes de
      licitar, y descontar del presupuesto todo lo que se obtenga por esas vías.</li>
    <li><strong>Actualizar UF, UTM y tipos de cambio</strong> a la fecha de ejecución.</li>
  </ol>

  <h3>Alcance de este presupuesto</h3>
  <p>Este presupuesto es una propuesta base. Las cantidades provienen de un diseño preliminar que aún
      no tiene topografía ni terreno definido, por lo que pueden variar: la superficie de cerco depende
      de la forma del terreno, el volumen de grava depende de las pendientes y la profundidad del pozo
      depende de la napa. Los precios tienen fecha —septiembre de 2026— y los equipos importados
      dependen del tipo de cambio. Nada de lo que aquí se propone reemplaza el trabajo de los
      profesionales municipales: el objetivo es que tengan un punto de partida completo y verificable
      sobre el cual corregir.</p>
</section>

</body>
</html>
""")

    html = "\n".join(partes)
    with open(DESTINO, "w", encoding="utf-8") as fh:
        fh.write(html)

    print("  presupuesto.html generado")
    print("  costo directo valorizado: %s" % pesos(d["directo_val"]))
    print("  costo directo a financiar: %s" % pesos(d["directo_fin"]))
    print("  total a financiar: %s (%s UTM)" % (pesos(d["total_fin"]), numero(d["utm"])))
    print("  total valorizado: %s" % pesos(d["total_val"]))
    print("  operación anual a financiar: %s" % pesos(d["op_fin"]))
    print("  suma del flujo: %s" % pesos(sum(f["total_mes"].values())))


if __name__ == "__main__":
    construir()
