# Plan de Caniles Públicos de Puerto Varas

Propuesta base para implementar tres caniles públicos de una hectárea en los sectores centro, sur y
norte de la comuna de Puerto Varas, partiendo con un canil piloto. Presenta: Lukas Matías Muñoz
Miranda — Gestión y Logística LM SpA.

## Documentos

| Archivo | Contenido |
|---|---|
| [`pdf/01-Plan-de-Caniles-Publicos-Puerto-Varas.pdf`](pdf/01-Plan-de-Caniles-Publicos-Puerto-Varas.pdf) | Plan completo: 20 secciones en cinco partes más cuatro anexos. |
| [`pdf/02-Presupuesto-Canil-Piloto-Puerto-Varas.pdf`](pdf/02-Presupuesto-Canil-Piloto-Puerto-Varas.pdf) | Presupuesto: desglose por partida e ítem, explicación de cada cantidad, tiempos de ejecución, flujo de caja mensual, ahorros, operación anual, proyección de los tres caniles, evaluación económica y metas. |

Cifras principales del canil piloto: **$124.413.925 a financiar** (1.735 UTM, dentro del tope PMU de
2.500 UTM), **$26.845.853 de aporte valorizado** del municipio, el liceo técnico y CONAF, y
**$23.478.732 anuales** de operación a financiar.

## Estructura del repositorio

```
src/
  plan.html          Documento 1, escrito a mano
  presupuesto.html   Documento 2, generado desde build/datos.py (no editar a mano)
  estilos.css        Hoja de estilos de impresión A4
  fuentes.css        Tipografías Source Serif 4 y Source Sans 3 incrustadas
  fuentes/           Archivos .woff2
build/
  datos.py                  Partidas, ítems, precios, calendario de pagos
  generar_presupuesto.py    Calcula totales y escribe src/presupuesto.html
  construir.py              Renderiza los PDF y arma el índice con folios reales
  render.js                 Render HTML a PDF con Chromium (Playwright)
  vista.py                  Exporta páginas a PNG para revisar la maqueta
pdf/                        Documentos finales
```

## Cómo regenerar los PDF

```bash
python3 build/generar_presupuesto.py     # recalcula el presupuesto
python3 build/construir.py               # genera los dos PDF
python3 build/construir.py plan          # solo el plan
python3 build/vista.py pdf/01-...pdf 4   # exporta la página 4 a PNG
```

Requiere Python 3 con `pypdf`, Node con `playwright` y Chromium disponible.

El generador comprueba que `cantidad × precio unitario` coincida con cada subtotal y avisa en consola
si hay diferencias mayores a $100. Todos los totales, porcentajes y el flujo de caja se calculan desde
`build/datos.py`: no hay cifras escritas a mano en las tablas del presupuesto.

## Cómo se arma el índice

`construir.py` renderiza el cuerpo una primera vez, lee con `pypdf` unas marcas invisibles incrustadas
en cada título (`@@clave@@`, en blanco y a 1 pt), anota en qué página cayó cada sección, completa el
índice y vuelve a renderizar. Después une la portada —renderizada aparte y sin pie de página— con el
cuerpo.

## Pendientes del proyecto

1. Cotizar los ítems marcados como **referenciales**, partiendo por tótem SOS, luminarias de grado
   público, cerraduras, cañerías, honorarios profesionales, retroexcavadora y camión.
2. Confirmar la profundidad real del pozo con el estudio hidrogeológico.
3. Encargar el cálculo estructural de la torre del estanque (11 toneladas).
4. Elegir los tres terrenos fiscales y definir el sector del canil piloto.
5. Definir los 20 mensajes de la cerca (propuesta: concurso en colegios de la comuna).
6. Definición jurídica sobre perros potencialmente peligrosos y ordenanza municipal del canil.
7. Levantar la línea base local y fijar las metas definitivas y la meta de uso que habilita la réplica.
8. Postulación al Fondo Concursable de Tenencia Responsable a través de una organización sin fines de
   lucro inscrita, para financiar los entrenadores del sector de perros complicados.
