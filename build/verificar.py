#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificación independiente del presupuesto.

Recalcula desde build/datos.py todas las cifras del documento 2 y las compara
con los valores decididos del proyecto. Además revisa que cada ítem cuadre con
cantidad × precio unitario y que el flujo de caja sume el total.

Uso:  python3 build/verificar.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datos import COMPRA, OPERACION, PARTIDAS  # noqa: E402

GG = 0.08
IMPREVISTOS = 0.10
IPC = 0.035
VISITAS_ANO = 38108
VISITAS_ANO3 = 45729

# Cifras del proyecto después de la revisión de precios de mercado y del
# retiro del convenio con CONAF. Si cambia un precio en datos.py, estos valores deben
# actualizarse conscientemente: para eso está esta verificación.
ESPERADO = {
    "costo directo valorizado": 140016079,
    "costo directo a financiar": 114870226,
    "aporte valorizado": 25145853,
    "gastos generales": 9189618,
    "imprevistos": 12405984,
    "total a financiar": 136465828,
    "total valorizado": 161611681,
    "operación anual valorizada": 30514355,
    "operación anual a financiar": 24714355,
    "canil 2 y 3, a financiar": 135401271,
    "canil 2 y 3, aporte": 23438458,
    "tres caniles, a financiar": 407268370,
    "tres caniles, aportes": 72022769,
}

problemas = []
avisos = []


def revisar(nombre, calculado, esperado, tolerancia=2):
    estado = "ok" if abs(calculado - esperado) <= tolerancia else "REVISAR"
    if estado != "ok":
        problemas.append("%s: calculado %s, esperado %s" % (nombre, calculado, esperado))
    print("  %-34s %14s   esperado %14s   %s"
          % (nombre, "{:,}".format(int(round(calculado))).replace(",", "."),
             "{:,}".format(esperado).replace(",", "."), estado))


print("\n1. Coherencia de cada ítem (cantidad × precio unitario = subtotal)")
descuadres = 0
for p in PARTIDAS:
    for cod, desc, cant, un, pu, tot, origen, tipo, fuente in p["items"]:
        dif = abs(cant * pu - tot)
        if dif > 100:
            descuadres += 1
            problemas.append("%s descuadra en $%d" % (cod, dif))
        elif dif > 0:
            avisos.append("%s: diferencia de $%d por redondeo del precio unitario" % (cod, round(dif)))
for cod, desc, cant, un, pu, tot, origen, nota in OPERACION:
    dif = abs(cant * pu - tot)
    if dif > 100:
        descuadres += 1
        problemas.append("%s descuadra en $%d" % (cod, dif))
    elif dif > 0:
        avisos.append("%s: diferencia de $%d por redondeo" % (cod, round(dif)))
n_items = sum(len(p["items"]) for p in PARTIDAS) + len(OPERACION)
print("  %d ítems revisados · %d descuadres · %d diferencias menores de redondeo"
      % (n_items, descuadres, len(avisos)))
for a in avisos:
    print("     · " + a)

print("\n2. Totales de inversión")
directo_val = sum(i[5] for p in PARTIDAS for i in p["items"])
directo_fin = sum(i[5] for p in PARTIDAS for i in p["items"] if i[6] == COMPRA)
aporte = directo_val - directo_fin
gg = round(directo_fin * GG)
imp = round((directo_fin + gg) * IMPREVISTOS)
total_fin = directo_fin + gg + imp
total_val = directo_val + gg + imp

revisar("costo directo valorizado", directo_val, ESPERADO["costo directo valorizado"])
revisar("costo directo a financiar", directo_fin, ESPERADO["costo directo a financiar"])
revisar("aporte valorizado", aporte, ESPERADO["aporte valorizado"])
revisar("gastos generales (8%)", gg, ESPERADO["gastos generales"])
revisar("imprevistos (10%)", imp, ESPERADO["imprevistos"])
revisar("total a financiar", total_fin, ESPERADO["total a financiar"])
revisar("total valorizado", total_val, ESPERADO["total valorizado"])

print("\n4. Operación anual")
from generar_presupuesto import operacion  # noqa: E402
op = operacion(directo_fin, total_fin)
op_val = sum(o[5] for o in op)
op_fin = sum(o[5] for o in op if o[6] == COMPRA)
revisar("operación anual valorizada", op_val, ESPERADO["operación anual valorizada"])
revisar("operación anual a financiar", op_fin, ESPERADO["operación anual a financiar"])
print("  %-34s %14s" % ("mensual a financiar", "{:,}".format(int(op_fin / 12)).replace(",", ".")))
print("  %-34s %14s" % ("costo por visita, año 1", "$" + str(int(round(op_fin / VISITAS_ANO)))))
print("  %-34s %14s" % ("costo por visita, año 3", "$" + str(int(round(op_fin / VISITAS_ANO3)))))

print("\n5. Caniles 2 y 3")
herramientas = sum(i[5] for p in PARTIDAS if p["codigo"] == "B"
                   for i in p["items"] if i[0] in ("B.4", "B.5", "B.6", "B.7", "B.8", "B.9", "B.10", "B.11"))
contenedor = 2500000
df2 = (directo_fin - herramientas) * (1 + IPC)
gg2 = df2 * GG
imp2 = (df2 + gg2) * IMPREVISTOS
total2 = df2 + gg2 + imp2
aporte2 = (aporte - contenedor) * (1 + IPC)
revisar("canil 2 y 3, a financiar", total2, ESPERADO["canil 2 y 3, a financiar"])
revisar("canil 2 y 3, aporte", aporte2, ESPERADO["canil 2 y 3, aporte"])
revisar("tres caniles, a financiar", total_fin + 2 * total2, ESPERADO["tres caniles, a financiar"])
revisar("tres caniles, aportes", aporte + 2 * aporte2, ESPERADO["tres caniles, aportes"])

print("\n6. Flujo de caja")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generar_presupuesto import calcular, flujo  # noqa: E402
d = calcular()
f = flujo(d)
suma = sum(f["total_mes"].values())
revisar("suma del flujo mensual", suma, ESPERADO["total a financiar"])
sin_gasto = [m for m in f["meses"] if f["total_mes"][m] == 0]
print("  meses sin desembolso: %s" % (", ".join(str(m) for m in sin_gasto) or "ninguno"))

print("\n7. Participación de cada partida en el gasto")
for p in PARTIDAS:
    fin = sum(i[5] for i in p["items"] if i[6] == COMPRA)
    print("  %s · %-38s %12s  %5.1f%%"
          % (p["codigo"], p["nombre"][:38],
             "{:,}".format(fin).replace(",", "."), 100 * fin / directo_fin))

print("\n8. Cotejo con las cifras citadas en el documento 1 (plan)")
plan = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "src", "plan.html"), encoding="utf-8").read()


def moneda(n):
    return "$" + format(int(round(n)), ",d").replace(",", ".")


citas = {
    "costo directo valorizado": moneda(directo_val),
    "costo directo a financiar": moneda(directo_fin),
    "gastos generales": moneda(gg),
    "imprevistos": moneda(imp),
    "total a financiar": moneda(total_fin),
    "total valorizado": moneda(total_val),
    "aporte valorizado": moneda(aporte),
    "canil 2 y 3": moneda(total2),
    "tres caniles": moneda(total_fin + 2 * total2),
    "operación mensual": moneda(op_fin / 12),
}
for nombre, texto in citas.items():
    presente = texto in plan
    print("  %-28s %16s   %s" % (nombre, texto, "citada" if presente else "NO APARECE"))
    if not presente:
        problemas.append("el plan no cita %s (%s)" % (nombre, texto))

viejas = ["$141.716.079", "$26.845.853", "$163.311.681", "$25.197.958", "$77.241.769",
          "$124.413.925", "$104.725.526", "$131.571.379", "$151.259.778", "$23.478.732",
          "$1.956.561", "$122.927.550", "$370.269.025", "$8.378.042", "$11.310.357"]
quedan = [v for v in viejas if v in plan]
print("  cifras de la versión anterior que quedaron en el plan: %s" % (", ".join(quedan) or "ninguna"))
if quedan:
    problemas.append("quedan cifras antiguas en el plan: " + ", ".join(quedan))

print("\n" + ("Sin problemas: todas las cifras cuadran." if not problemas
              else "PROBLEMAS DETECTADOS:\n  - " + "\n  - ".join(problemas)))
sys.exit(1 if problemas else 0)
