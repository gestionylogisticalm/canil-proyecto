# Plan de Caniles Públicos de Puerto Varas

Propuesta base para implementar tres caniles públicos de una hectárea en los sectores centro, sur y
norte de la comuna de Puerto Varas, partiendo con un canil piloto. Presenta: Lukas Matías Muñoz
Miranda — Gestión y Logística LM SpA.

## Documentos

| Archivo | Contenido |
|---|---|
| [`pdf/01-Plan-de-Caniles-Publicos-Puerto-Varas.pdf`](pdf/01-Plan-de-Caniles-Publicos-Puerto-Varas.pdf) | Plan completo: 20 secciones en cinco partes más cuatro anexos. |
| [`pdf/02-Presupuesto-Canil-Piloto-Puerto-Varas.pdf`](pdf/02-Presupuesto-Canil-Piloto-Puerto-Varas.pdf) | Presupuesto: desglose por partida e ítem, explicación de cada cantidad, tiempos de ejecución, flujo de caja mensual, ahorros, operación anual, proyección de los tres caniles, evaluación económica y metas. |

Cifras principales del canil piloto: **$136.465.828 a financiar** (1.903 UTM, dentro del tope PMU de
2.500 UTM), **$26.845.853 de aporte valorizado** del municipio, el liceo técnico y CONAF, y
**$24.714.355 anuales** de operación a financiar. Los precios se revisaron uno a uno contra precios
publicados de proveedores chilenos en septiembre de 2026; el detalle de los ajustes está en el
capítulo 12 del presupuesto.

## Estructura del repositorio

```
src/
  plan.html          Documento 1, escrito a mano
  presupuesto.html   Documento 2, generado desde build/datos.py (no editar a mano)
  estilos.css        Hoja de estilos de impresión A4, con la paleta del Gobierno de Chile
  fuentes.css        Tipografías Source Serif 4 y Source Sans 3 incrustadas
  fuentes/           Archivos .woff2
  img/               Las seis imágenes 3D, en PNG (original) y JPEG (para el PDF)
build/
  datos.py                  Partidas, ítems, precios, calendario de pagos
  generar_presupuesto.py    Calcula totales y escribe src/presupuesto.html
  verificar.py              Recalcula y compara todas las cifras con los valores decididos
  construir.py              Renderiza los PDF y arma el índice con folios reales
  render.js                 Render HTML a PDF con Chromium (Playwright)
  vista.py                  Exporta páginas a PNG para revisar la maqueta
  optimizar_imagenes.py     Convierte los renders a JPEG para el documento
  3d/escena.html            Modelo 3D del canil en Three.js, con las medidas del plan
  3d/render3d.js            Renderiza las seis vistas
pdf/                        Documentos finales
```

## Paleta

Los documentos usan los colores institucionales del Gobierno de Chile: azul PANTONE 293 C
(`#0f69b4`, RGB 15/105/180) como color principal y rojo PANTONE 185 C (`#eb3c46`, RGB 235/60/70)
solo como acento en los recuadros de advertencia.

## Imágenes 3D

Las seis vistas del anexo D salen de un modelo tridimensional construido con las medidas reales del
plan: terreno de 100 × 100 m, cercos de 1,8 y 1,2 m, baño de 16 m², amarre de 12 × 3 m, torre de agua
de 4 m. Se modelan tres situaciones de terreno —un cuarto de bosque, solo pradera, mitad y mitad— y
cada una se renderiza desde dos ángulos.

```bash
node build/3d/render3d.js          # genera src/img/*.png (necesita NODE_PATH con playwright)
python3 build/optimizar_imagenes.py # convierte a JPEG para el PDF
```

## Cómo regenerar los PDF

```bash
python3 build/generar_presupuesto.py     # recalcula el presupuesto
python3 build/verificar.py               # comprueba todas las cifras
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

1. Cotizar formalmente los ítems que siguen marcados como **referenciales**, partiendo por el tótem
   SOS, las cañerías y fittings, el proyecto sanitario y el proyecto eléctrico. Los precios de
   topografía, baño químico, cerraduras, luminarias solares, prevencionista, retroexcavadora y camión
   ya fueron contrastados con precios publicados de mercado.
2. Confirmar la profundidad real del pozo con el estudio hidrogeológico.
3. Encargar el cálculo estructural de la torre del estanque (11 toneladas).
4. Elegir los tres terrenos fiscales y definir el sector del canil piloto. El protocolo está en la
   sección 8 del plan: oficio a la Seremi de Bienes Nacionales de Los Lagos, capa de propiedad fiscal
   del Geoportal del ministerio, cruce con el catastro municipal y filtro por Plan Regulador.
5. Definir los 20 mensajes de la cerca (propuesta: concurso en colegios de la comuna).
6. Definición jurídica sobre perros potencialmente peligrosos y ordenanza municipal del canil.
7. Levantar la línea base local y fijar las metas definitivas y la meta de uso que habilita la réplica.
8. Postulación al Fondo Concursable de Tenencia Responsable a través de una organización sin fines de
   lucro inscrita, para financiar los entrenadores del sector de perros complicados.
