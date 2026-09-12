#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Datos del presupuesto del canil piloto de Puerto Varas.

Todos los montos están en pesos chilenos con IVA incluido, a septiembre de 2026.
Cada ítem lleva:
  cod, desc, cant, unidad, pu (precio unitario), total, origen, tipo, fuente
`total` se guarda explícito porque varios precios provienen de conversiones
(UF, euros, dólares) y el redondeo del precio unitario no siempre reproduce
exactamente el total; el generador verifica que la diferencia sea menor a $10.

origen: "Compra/contrato" es lo que se financia con el fondo; el resto son
aportes valorizados (municipio, cuadrilla municipal, liceo técnico, CONAF).
"""

COMPRA = "Compra/contrato"
MUNI = "Aporte municipal"
CUADRILLA = "Cuadrilla municipal"
LICEO = "Liceo técnico"
CONAF = "CONAF"

VERIFICADO = "Verificado"
REFERENCIAL = "Referencial"

# --------------------------------------------------------------------------
# Parámetros generales
# --------------------------------------------------------------------------

PARAMETROS = [
    ("UF", "$40.885,63", "Valor al 9 de septiembre de 2026"),
    ("UTM", "$71.721", "Valor de septiembre de 2026 (SII)"),
    ("IVA", "19%", "Todos los montos se presentan con IVA incluido"),
    ("Ingreso mínimo mensual", "$539.000", "Vigente en 2026"),
    ("Euro", "$1.048", "Tipo de cambio usado para equipos importados"),
    ("Dólar", "$922", "Tipo de cambio usado para equipos importados"),
    ("Factor de importación", "1,25", "Flete, seguro e internación sobre el precio de origen"),
    ("Factor de flete de áridos", "1,35", "Sobrecosto de traslado de áridos a Puerto Varas"),
    ("Factor de costo empleador", "1,25", "Cotizaciones y cargas sobre el sueldo líquido"),
    ("Gastos generales", "8%", "Sobre el costo directo a financiar"),
    ("Imprevistos", "10%", "Sobre costo directo más gastos generales"),
    ("Superficie del baño", "16 m² a 30 UF/m²", "Terminación media; rango de mercado 22 a 42 UF/m²"),
    ("Profundidad del pozo", "40 m a $230.000/m", "Más 15% por desarrollo y prueba de bombeo"),
    ("Plazo de obra", "4 meses", "16 semanas con frentes de trabajo traslapados"),
    ("Tope PMU", "2.500 UTM = $179.302.500", "Máximo por proyecto del Programa de Mejoramiento Urbano"),
    ("IPC 12 meses", "3,5%", "Reajuste aplicado a los caniles 2 y 3"),
    ("Población de Chile", "18.480.432", "Base para llevar cifras nacionales a la comuna"),
    ("Uso proyectado", "10% de los perros del sector por semana", "Supuesto de demanda del canil piloto"),
    ("Uso de bolsas", "20% de las visitas", "Supuesto de consumo de bolsas compostables"),
    ("Costo de la bolsa compostable", "$40", "Precio unitario supuesto"),
]

# --------------------------------------------------------------------------
# Partidas de inversión
# --------------------------------------------------------------------------

PARTIDAS = [
    {
        "codigo": "A",
        "nombre": "Estudios y trámites",
        "resumen": "Todo lo que hay que estudiar, diseñar y tramitar antes de que llegue "
                   "la primera cuadrilla al terreno.",
        "explicacion": [
            "Esta partida financia el expediente técnico completo del canil: el levantamiento del "
            "terreno, el diseño, los proyectos de especialidad que exige la normativa y los trámites "
            "ante los servicios públicos. Se ejecuta entre los meses 3 y 9, antes de la obra.",
            "Las cantidades son globales porque se trata de servicios profesionales contratados por "
            "encargo completo y no por unidad de medida. El monto de la autorización sanitaria es el "
            "único arancel con valor publicado: se usó el tope del rango de la Seremi de Salud "
            "($56.200 a $905.900) para no subestimar. El estudio hidrogeológico también se calculó "
            "en el máximo de su rango de mercado ($150.000 a $400.000).",
            "El permiso de edificación se valoriza como aporte municipal porque es una gestión "
            "interna de la Dirección de Obras. El diseño de arquitectura y especialidades es el ítem "
            "más grande de la partida y es también el que más puede bajar: si Secplan y la Dirección "
            "de Obras asumen el diseño con profesionales municipales, se ahorran hasta $6.000.000.",
        ],
        "items": [
            ("A.1", "Levantamiento topográfico y planos del terreno (≈1,1 ha)", 1, "gl", 800000, 800000, COMPRA, VERIFICADO, "Mercado chileno 2026: $150.000 a más de $800.000 según superficie, vegetación y pendiente; se usa el tope del rango por tratarse de 1,1 ha con bosque"),
            ("A.2", "Diseño de arquitectura y especialidades, incluido cálculo estructural de la torre y paisajismo", 1, "gl", 6000000, 6000000, COMPRA, VERIFICADO, "5,7% del costo directo a financiar. El arancel referencial del Colegio de Arquitectos asigna entre 6% y 11% a trabajos preparatorios y proyecto en arquitectura paisajista, de modo que el valor queda bajo el rango. Puede reducirse con profesionales municipales"),
            ("A.3", "Proyecto sanitario firmado por proyectista inscrito", 1, "gl", 1200000, 1200000, COMPRA, REFERENCIAL, "Cotizar"),
            ("A.4", "Autorización sanitaria Seremi de Salud", 1, "gl", 905900, 905900, COMPRA, VERIFICADO, "Arancel Seremi: $56.200 a $905.900 según trámite; se usa el máximo"),
            ("A.5", "Proyecto eléctrico fotovoltaico", 1, "gl", 800000, 800000, COMPRA, REFERENCIAL, "Cotizar con instalador autorizado SEC"),
            ("A.6", "Estudio hidrogeológico previo al pozo", 1, "gl", 400000, 400000, COMPRA, VERIFICADO, "Club del Agua 2026: $150.000 a $400.000; se usa el máximo"),
            ("A.7", "Derechos de agua DGA: publicaciones, radio, visita e inscripción en el Conservador", 1, "gl", 1000000, 1000000, COMPRA, REFERENCIAL, "Costos de publicación e inscripción a cargo del solicitante; cotizar"),
            ("A.8", "Permiso de edificación DOM", 1, "gl", 300000, 300000, MUNI, REFERENCIAL, "Gestión interna municipal"),
            ("A.9", "Participación ciudadana: talleres y difusión en los tres sectores", 1, "gl", 600000, 600000, COMPRA, REFERENCIAL, "Materiales, arriendo de local y difusión"),
            ("A.10", "Análisis de laboratorio del agua del pozo (línea base)", 1, "gl", 150000, 150000, COMPRA, REFERENCIAL, "Laboratorio acreditado; cotizar"),
        ],
    },
    {
        "codigo": "B",
        "nombre": "Instalación de faena y herramientas",
        "resumen": "La obra se monta una vez y sirve para los tres caniles.",
        "explicacion": [
            "Incluye la instalación de faena —bodega, baño químico, cierre provisorio y letrero de "
            "obra— y todas las herramientas y equipos necesarios para trabajar la madera en terreno, "
            "plantar postes y compactar áridos.",
            "La particularidad de esta partida es que <strong>no se repite</strong>: las herramientas "
            "y equipos de los ítems B.4 a B.11 se compran una sola vez y se reutilizan en los caniles "
            "2 y 3, lo que descuenta $4.750.290 del costo directo de cada canil siguiente. El "
            "contenedor bodega se solicita sin costo a la Plataforma de Economía Circular de Mercado "
            "Público, donde los servicios públicos ceden bienes dados de baja; por eso se valoriza "
            "como aporte y no como compra.",
            "El aserradero portátil para motosierra es la pieza clave del enfoque de materiales: "
            "permite convertir en terreno los árboles que el municipio retira en postes, tablas y "
            "listones, sin pagar aserradero externo ni flete de ida y vuelta.",
            "El equipo de protección personal se calcula para 12 personas, que es el tamaño máximo "
            "del equipo en obra considerando profesionales, carpinteros, jornales y especialistas.",
        ],
        "items": [
            ("B.1", "Contenedor bodega", 1, "u", 2500000, 2500000, MUNI, REFERENCIAL, "Solicitar vía Plataforma de Economía Circular (Mercado Público)"),
            ("B.2", "Baño químico para trabajadores", 4, "mes", 119000, 476000, COMPRA, VERIFICADO, "2x3.cl 2026: baño estándar $90.000 + IVA y con lavamanos $100.000 + IVA al mes, con una limpieza semanal"),
            ("B.3", "Cierre provisorio y letrero de obra", 1, "gl", 400000, 400000, COMPRA, REFERENCIAL, "Letrero según formato del fondo"),
            ("B.4", "Generador 5 kVA", 1, "u", 600000, 600000, COMPRA, REFERENCIAL, "Cotizar"),
            ("B.5", "Motosierra profesional", 2, "u", 450000, 900000, COMPRA, REFERENCIAL, "Cotizar"),
            ("B.6", "Aserradero portátil para motosierra 36\"", 1, "u", 90290, 90290, COMPRA, VERIFICADO, "Falabella.cl, 2026"),
            ("B.7", "Ahoyadora a motor", 1, "u", 250000, 250000, COMPRA, REFERENCIAL, "Cotizar"),
            ("B.8", "Placa compactadora (arriendo)", 1, "mes", 350000, 350000, COMPRA, REFERENCIAL, "Cotizar"),
            ("B.9", "Herramientas eléctricas: 2 sierras circulares y 4 taladros", 1, "gl", 900000, 900000, COMPRA, REFERENCIAL, "Cotizar"),
            ("B.10", "Herramientas de mano: carretillas, palas, chuzos, escaleras, niveles y tensor", 1, "gl", 700000, 700000, COMPRA, REFERENCIAL, "Cotizar"),
            ("B.11", "Equipo de protección personal", 12, "persona", 80000, 960000, COMPRA, REFERENCIAL, "Casco, guantes, lentes, zapatos de seguridad y protección auditiva"),
        ],
    },
    {
        "codigo": "C",
        "nombre": "Cerco, esclusas y puertas",
        "resumen": "El perímetro, las divisiones internas, las siete puertas de esclusa y las tablas "
                   "con mensajes.",
        "explicacion": [
            "El cerco es lo que define el canil: unos 575 metros lineales de cerco de 1,8 m en los "
            "sectores de perros grandes, de entrenamiento y en la división entre grandes y pequeños; "
            "unos 125 metros de 1,2 m en el perímetro del sector de pequeños; y unos 70 metros de "
            "cerco móvil interior para rotar el pasto en invierno.",
            "Las cantidades de malla se calcularon por rollos comerciales completos, que es como se "
            "compra: 25 rollos de 2,0 × 25 m para el cerco alto —incluidos los 20 cm que quedan "
            "enterrados—, 9 rollos de 1,5 × 25 m para el cerco bajo y el cerco móvil, y 9 rollos de "
            "1,0 × 25 m que se cortan en franjas para armar la barrera enterrada en L de unos 400 "
            "metros de perímetro. Los postes van cada 2,5 metros aproximadamente: 230 de 2,7 m para "
            "los cercos altos y 50 de 2,0 m para el bajo.",
            "Los postes, el listón superior y los paneles opacos se valorizan al precio de mercado de "
            "la madera equivalente, pero <strong>no se compran</strong>: salen de los árboles que el "
            "municipio retira por temporal, riesgo o poda, aserrados en terreno. Por eso figuran como "
            "aporte municipal. Se agregan anclajes galvanizados para el 30% de los postes, que es la "
            "proporción estimada en que no habrá madera de especie durable disponible.",
            "Las tablas grabadas con los 20 mensajes de la cerca las fabrica el liceo técnico; lo "
            "único que se compra es la pintura para rellenar las letras en bajo relieve.",
        ],
        "items": [
            ("C.1", "Malla galvanizada 5014, 2,0 × 25 m (cerco de 1,8 m más 20 cm enterrados)", 25, "rollo", 97210, 2430250, COMPRA, VERIFICADO, "Sodimac.cl, Inchalam 2,0 × 25 m 5014; ≈575 m lineales más traslapes"),
            ("C.2", "Malla galvanizada 5014, 1,5 × 25 m (cerco de 1,2 m y cerco móvil)", 9, "rollo", 73090, 657810, COMPRA, VERIFICADO, "Sodimac.cl, Inchalam 1,50 × 25 m 5014; ≈125 m más 70 m de cerco móvil"),
            ("C.3", "Malla galvanizada 5014, 1,0 × 25 m, cortada en franjas para la barrera enterrada en L", 9, "rollo", 48970, 440730, COMPRA, VERIFICADO, "Sodimac.cl, Inchalam 1 × 25 m 5014; ≈400 m perimetrales"),
            ("C.4", "Alambre galvanizado 2,11 mm, rollo de 25 kg (tres líneas tensoras)", 3, "rollo", 85990, 257970, COMPRA, VERIFICADO, "Easy.cl, rollo 25 kg 2,11 mm"),
            ("C.5", "Postes de madera de 2,7 m (árboles municipales)", 230, "u", 4990, 1147700, MUNI, VERIFICADO, "Valor de referencia: polín 7,5–10 cm de 2,44 m, Sodimac.cl $4.990"),
            ("C.6", "Postes de madera de 2,0 m (árboles municipales)", 50, "u", 4990, 249500, MUNI, VERIFICADO, "Valor de referencia Sodimac.cl"),
            ("C.7", "Postes removibles del cerco móvil", 28, "u", 4990, 139720, MUNI, VERIFICADO, "Valor de referencia Sodimac.cl"),
            ("C.8", "Listón superior 2×4 (≈650 m, soporte de las tablas grabadas)", 204, "pieza 3,2 m", 6057, 1235628, MUNI, VERIFICADO, "Valor de referencia: pino 2×4 de 3,2 m, Sodimac.cl $6.057"),
            ("C.9", "Anclaje galvanizado de base de poste (30% de los postes)", 84, "u", 18490, 1553160, COMPRA, VERIFICADO, "Sodimac.cl, base de anclaje para pilar IDAF; donde no haya madera durable"),
            ("C.10", "Paneles opacos entre sectores de entrenamiento y sectores libres", 250, "m²", 8000, 2000000, MUNI, REFERENCIAL, "Madera municipal aserrada; valor referencial"),
            ("C.11", "Bisagras reforzadas para puertas de esclusa", 21, "u", 8000, 168000, COMPRA, REFERENCIAL, "Cotizar"),
            ("C.12", "Cierres automáticos de resorte", 7, "u", 25000, 175000, COMPRA, REFERENCIAL, "Cotizar"),
            ("C.13", "Pestillos", 7, "u", 10000, 70000, COMPRA, REFERENCIAL, "Cotizar"),
            ("C.14", "Portón de mantención: herrajes y candado", 1, "gl", 120000, 120000, COMPRA, REFERENCIAL, "Cotizar"),
            ("C.15", "Tornillería galvanizada, grapas, tensores y abrazaderas", 1, "gl", 600000, 600000, COMPRA, REFERENCIAL, "Cotizar"),
            ("C.16", "Tablas grabadas de doble cara: madera y mano de obra del liceo", 20, "u", 15000, 300000, LICEO, REFERENCIAL, "Valor referencial del aporte"),
            ("C.17", "Pintura exterior para relleno de letras en bajo relieve", 1, "gl", 150000, 150000, COMPRA, REFERENCIAL, "Cotizar"),
        ],
    },
    {
        "codigo": "D",
        "nombre": "Zona de acceso",
        "resumen": "Baño público, zona de amarre techada, estacionamiento y senderos.",
        "explicacion": [
            "El baño público es el ítem más caro de todo el proyecto y es también el que hace que el "
            "canil funcione de verdad: sin baño, la gente no se queda. Son 16 m² con dos recintos "
            "universales, pensados para entrar con el perro, con inodoro, lavamanos, grifería "
            "temporizada, jabón, portarrollos, toallas, barras de apoyo, gancho para la correa y "
            "basurero.",
            "El costo se calculó con el estándar de terminación media de 30 UF/m², dentro de un rango "
            "de mercado de 22 a 42 UF/m² para construcción en 2026, e incluye artefactos básicos. Es "
            "un precio verificado contra referencias de costo por metro cuadrado, no una cotización: "
            "corresponde cotizarlo llave en mano con constructoras locales.",
            "El sistema sanitario es fosa séptica horizontal de 3.500 litros con kit completo "
            "—desgrasador, cámara de inspección, distribuidor, 25 m de dren y geotextil—, ambos con "
            "precio publicado. Si el terreno elegido tiene alcantarillado cercano, esta solución se "
            "reemplaza por el empalme correspondiente.",
            "La grava es el único árido que se compra: 125 m³ para el estacionamiento de unos 375 m² "
            "con 15 cm de espesor, los senderos de unos 250 m² con 10 cm, las bases de bebederos y "
            "pozas, y las zanjas de infiltración. El precio unitario incluye un factor de flete de "
            "1,35 sobre el valor de referencia por metro cúbico. Si el propio terreno tiene material "
            "utilizable, esta partida puede bajar hasta $3.594.544.",
        ],
        "items": [
            ("D.1", "Baño público de dos recintos universales, estructura de madera, llave en mano", 16, "m²", 1226569, 19625102, COMPRA, VERIFICADO, "30 UF/m² de terminación media (rango 22–42 UF/m², 2026); incluye artefactos básicos"),
            ("D.2", "Grifería temporizada antivandálica", 2, "u", 90000, 180000, COMPRA, REFERENCIAL, "Cotizar"),
            ("D.3", "Barras de apoyo de accesibilidad", 4, "u", 35000, 140000, COMPRA, REFERENCIAL, "Cotizar"),
            ("D.4", "Dispensadores, portarrollos, ganchos para correa y basureros", 1, "gl", 150000, 150000, COMPRA, REFERENCIAL, "Cotizar"),
            ("D.5", "Fosa séptica horizontal 3.500 L", 1, "u", 669990, 669990, COMPRA, VERIFICADO, "Sodimac.cl, Amerplast 3.500 L"),
            ("D.6", "Kit de fosa: desgrasador, cámara de inspección, distribuidor, 25 m de dren y geotextil", 1, "u", 319990, 319990, COMPRA, VERIFICADO, "Sodimac.cl, kit completo Amerplast"),
            ("D.7", "Filtro y clorador para el agua del lavamanos", 1, "gl", 250000, 250000, COMPRA, REFERENCIAL, "Cotizar"),
            ("D.8", "Zona de amarre techada 12 × 3 m: techumbre zincalum y canaleta", 1, "gl", 450000, 450000, COMPRA, REFERENCIAL, "Cotizar"),
            ("D.9", "Zona de amarre techada: estructura de madera", 1, "gl", 300000, 300000, MUNI, REFERENCIAL, "Madera municipal; valor referencial"),
            ("D.10", "Argollas galvanizadas de amarre", 5, "u", 6000, 30000, COMPRA, REFERENCIAL, "Cotizar"),
            ("D.11", "Grava 1½\": estacionamiento, senderos, sendero accesible, bases de agua y zanjas", 125, "m³", 28756, 3594544, COMPRA, VERIFICADO, "Full Áridos 2026: $17.900 + IVA por m³ (camión de 13 m³) × factor de flete. Puede reducirse con material del terreno"),
        ],
    },
    {
        "codigo": "E",
        "nombre": "Agua y sistemas de refresco",
        "resumen": "Pozo con bomba solar, torre y estanques, captación de lluvia, redes y los cinco "
                   "sistemas de refresco.",
        "explicacion": [
            "El agua del canil sale de un pozo propio y se acumula en dos estanques de 5.500 litros "
            "sobre una torre de madera de unos 4 metros, desde donde se distribuye por gravedad. El "
            "agua lluvia de los techos del baño, el amarre y las pérgolas complementa el llenado y "
            "reduce el bombeo.",
            "La perforación se presupuestó en 40 metros a $230.000 por metro, con un precio de "
            "mercado verificado, más un 15% por desarrollo del pozo y prueba de bombeo. "
            "<strong>Esta es la variable que más mueve el total</strong>: cada 10 metros adicionales "
            "de profundidad significan $2,3 millones más. Por eso el estudio hidrogeológico de la "
            "partida A se hace antes y no después.",
            "La bomba es solar sumergible de 1,1 kW con cuatro paneles propios de 550 W, "
            "independientes del sistema solar central, dimensionados para la demanda de verano. Ambos "
            "precios se calcularon desde catálogos internacionales con tipo de cambio, IVA y factor de "
            "importación de 1,25.",
            "Los cinco sistemas de refresco —bebedero de canoa, poza para chapotear, pérgola con "
            "aspersores, arco rociador y canaleta tipo riachuelo— se instalan en los sectores de "
            "perros grandes y de pequeños. Los dos sectores de entrenamiento llevan solo bebedero de "
            "flujo continuo, que es el criterio de seguridad explicado en el plan. La estructura de "
            "madera de la torre, las pérgolas y las canaletas es aporte municipal; los bebederos y "
            "los arcos rociadores los fabrica el liceo técnico. Lo que se compra son estanques, "
            "bomba, paneles, cañerías, válvulas, láminas impermeables y boquillas.",
            "Las seis zanjas de infiltración con grava, tubo perforado y geotextil son las que evitan "
            "que el rebalse del sistema de refresco genere barro: es un detalle menor en costo y "
            "decisivo en el funcionamiento diario del recinto.",
        ],
        "items": [
            ("E.1", "Estanque vertical 5.500 L (dos unidades: 11.000 L)", 2, "u", 649990, 1299980, COMPRA, VERIFICADO, "Sodimac.cl, Amerplast Estándar 5.500 L"),
            ("E.2", "Torre de madera de ≈4 m: estructura", 1, "gl", 1500000, 1500000, MUNI, REFERENCIAL, "Madera municipal; requiere cálculo estructural (11 t de agua)"),
            ("E.3", "Torre: pernos, placas y herrajes estructurales", 1, "gl", 400000, 400000, COMPRA, REFERENCIAL, "Cotizar"),
            ("E.4", "Perforación de pozo de 6\" entubado", 40, "m", 230000, 9200000, COMPRA, VERIFICADO, "Cruzat Ingeniería 2026; profundidad por confirmar con el estudio hidrogeológico"),
            ("E.5", "Desarrollo del pozo y prueba de bombeo (15% de la perforación)", 1, "gl", 1380000, 1380000, COMPRA, REFERENCIAL, "Supuesto de 15% sobre el valor de la perforación"),
            ("E.6", "Bomba solar sumergible 1,1 kW con controlador", 1, "u", 547548, 547548, COMPRA, VERIFICADO, "Obramat (España) €351,24 sin IVA × tipo de cambio × IVA × factor de importación"),
            ("E.7", "Paneles solares de 550 W para la bomba (independientes del sistema central)", 4, "u", 212853, 851412, COMPRA, VERIFICADO, "Sungold Power: pallet de 32 paneles de 550 W a US$6.210 (≈US$194 c/u) × tipo de cambio × IVA"),
            ("E.8", "Estructura de paneles, protecciones y cable de bomba", 1, "gl", 350000, 350000, COMPRA, REFERENCIAL, "Cotizar"),
            ("E.9", "Caseta de protección del pozo: herrajes", 1, "gl", 150000, 150000, COMPRA, REFERENCIAL, "Madera municipal más herrajes"),
            ("E.10", "Captación de lluvia: ≈40 m de canaleta, 4 bajadas y filtro de primeras aguas", 1, "gl", 400000, 400000, COMPRA, REFERENCIAL, "Cotizar"),
            ("E.11", "Bomba de presión pequeña para aspersores y arcos", 1, "u", 180000, 180000, COMPRA, REFERENCIAL, "Cotizar"),
            ("E.12", "Cañería enterrada ≈300 m y fittings", 1, "gl", 1200000, 1200000, COMPRA, REFERENCIAL, "Cotizar"),
            ("E.13", "Llaves de paso", 10, "u", 12000, 120000, COMPRA, REFERENCIAL, "Cotizar"),
            ("E.14", "Electroválvulas 24 V", 14, "u", 35000, 490000, COMPRA, REFERENCIAL, "Cotizar"),
            ("E.15", "Programador de riego multizona", 1, "u", 180000, 180000, COMPRA, REFERENCIAL, "Cotizar"),
            ("E.16", "Grifos reductores de caudal para bebederos", 5, "u", 15000, 75000, COMPRA, REFERENCIAL, "Cotizar"),
            ("E.17", "Bebederos de flujo continuo en madera", 5, "u", 80000, 400000, LICEO, REFERENCIAL, "Fabricación del liceo técnico; valor referencial"),
            ("E.18", "Lámina impermeable para dos pozas y dos canaletas (≈34 m²)", 34, "m²", 12000, 408000, COMPRA, REFERENCIAL, "Cotizar geomembrana o EPDM"),
            ("E.19", "Válvulas de vaciado de pozas", 2, "u", 25000, 50000, COMPRA, REFERENCIAL, "Cotizar"),
            ("E.20", "Pérgolas de 4 × 4 m en madera", 2, "u", 400000, 800000, MUNI, REFERENCIAL, "Madera municipal; valor referencial"),
            ("E.21", "Aspersores de gota gruesa", 8, "u", 8000, 64000, COMPRA, REFERENCIAL, "Cotizar"),
            ("E.22", "Arcos rociadores en madera", 2, "u", 150000, 300000, LICEO, REFERENCIAL, "Fabricación del liceo técnico; valor referencial"),
            ("E.23", "Boquillas para arcos", 12, "u", 5000, 60000, COMPRA, REFERENCIAL, "Cotizar"),
            ("E.24", "Canaletas tipo riachuelo de 10 m en madera", 2, "u", 200000, 400000, MUNI, REFERENCIAL, "Madera municipal; valor referencial"),
            ("E.25", "Tubo dren perforado para zanjas", 30, "m", 3500, 105000, COMPRA, REFERENCIAL, "Cotizar"),
            ("E.26", "Geotextil para zanjas", 40, "m²", 1500, 60000, COMPRA, REFERENCIAL, "Cotizar"),
        ],
    },
    {
        "codigo": "F",
        "nombre": "Energía, seguridad y automatización",
        "resumen": "El sistema que permite operar de 6:00 a 21:00 sin personal en terreno.",
        "explicacion": [
            "Esta partida es la que reemplaza a un portero. El sistema solar central de unos 2 kWp "
            "con batería de litio de 5 kWh alimenta cámaras, parlantes, cerraduras temporizadas, "
            "router y contadores; está dimensionado para invierno, que es la condición crítica en "
            "Puerto Varas, y admite respaldo de red eléctrica si el terreno tiene conexión cercana.",
            "Las siete cámaras cubren acceso y estacionamiento, esclusa común, dos posiciones en el "
            "sector de perros grandes, el sector de pequeños y cada sector de entrenamiento. Son de "
            "visión nocturna y audio bidireccional, graban por movimiento y las de los sectores "
            "alejados llevan panel solar propio, lo que evita tender cable por todo el recinto.",
            "Las cinco cerraduras corresponden a las tres esclusas y a las dos puertas del baño. Están "
            "programadas para abrir a las 6:00 y bloquear el ingreso a las 21:00, con salida siempre "
            "libre desde el interior.",
            "Las 30 luminarias LED solares con sensor de movimiento se presupuestaron a $65.000 por "
            "unidad y no al precio de los productos de consumo, que parten en $16.990: esos equipos no "
            "resisten uso público intensivo ni el clima de la zona. Es un precio referencial que debe "
            "cotizarse en grado público.",
            "El tótem SOS es el ítem referencial más sensible de la partida. Como referencia de "
            "mercado, Iquique aprobó $345 millones por 23 tótems con cámara e internet, unos $15 "
            "millones cada uno; el tótem de este proyecto es mucho más simple —tres botones, sin "
            "cámara propia— y se presupuestó en $3.500.000. Es una cifra que debe confirmarse con "
            "cotización antes de ejecutar.",
        ],
        "items": [
            ("F.1", "Sistema solar central: ≈2 kWp de paneles, batería de litio de 5 kWh, inversor/cargador de 5,5 kW y cables", 1, "gl", 2796402, 2796402, COMPRA, VERIFICADO, "Autosolar (España), kit aislada 5.500 W más batería de 5 kWh: €1.793,83 sin IVA × tipo de cambio × IVA × factor de importación"),
            ("F.2", "Gabinete, protecciones y puesta a tierra", 1, "gl", 450000, 450000, COMPRA, REFERENCIAL, "Cotizar con instalador autorizado SEC"),
            ("F.3", "Router 4G exterior con antena", 1, "u", 250000, 250000, COMPRA, REFERENCIAL, "Cotizar"),
            ("F.4", "Puntos de acceso wifi exterior", 2, "u", 150000, 300000, COMPRA, REFERENCIAL, "Cotizar"),
            ("F.5", "Cámara exterior 2K con panel solar, visión nocturna y audio bidireccional", 7, "u", 91687, 641808, COMPRA, VERIFICADO, "Ezviz EB3 más panel solar: €69,99 con IVA (MediaWorld Italia, 2026) × tipo de cambio × factor de importación"),
            ("F.6", "Tarjetas microSD para grabación", 7, "u", 25000, 175000, COMPRA, REFERENCIAL, "Cotizar"),
            ("F.7", "Parlantes exteriores con amplificador para el aviso de cierre", 2, "u", 120000, 240000, COMPRA, REFERENCIAL, "Cotizar"),
            ("F.8", "Cerraduras electromagnéticas exteriores con temporizador y apertura interior libre", 5, "u", 175000, 875000, COMPRA, VERIFICADO, "Scanavini 2026: cerradura electromagnética para puerta de abatir $155.530, más temporizador de relé"),
            ("F.9", "Luminarias solares integradas 40 W todo en uno, IP65, con sensor de movimiento", 30, "u", 389990, 11699700, COMPRA, VERIFICADO, "Natura Energy 2026: luminaria solar integrada 40 W $389.990; los modelos de 60 W van de $390.000 a $509.990. Los productos de consumo desde $16.990 no resisten uso público intensivo"),
            ("F.10", "Postes de madera para luminarias", 30, "u", 4990, 149700, MUNI, VERIFICADO, "Valor de referencia Sodimac.cl"),
            ("F.11", "Tótem SOS solar con tres botones y conexión celular", 1, "u", 3500000, 3500000, COMPRA, REFERENCIAL, "Referencia: Iquique aprobó $345 millones por 23 tótems con cámara e internet (≈$15 millones c/u); este modelo es más simple"),
            ("F.12", "Contadores automáticos de visitas", 3, "u", 120000, 360000, COMPRA, REFERENCIAL, "Cotizar"),
        ],
    },
    {
        "codigo": "G",
        "nombre": "Mobiliario, juegos y señalética",
        "resumen": "Bancas, juegos de troncos, tótems de bolsas y todos los letreros.",
        "explicacion": [
            "Son 12 bancas: 5 en el sector de perros grandes, 3 en el de pequeños, 2 en el acceso y 1 "
            "en cada sector de entrenamiento. No hay mesas, por decisión de diseño: la comida es la "
            "principal fuente de conflictos entre perros sueltos. Tres bancas llevan techo pequeño "
            "—en pequeños y en cada sector de entrenamiento—; en grandes las bancas van bajo los "
            "árboles existentes.",
            "Los juegos son de troncos y no de plástico, y se valorizan como aporte municipal porque "
            "se hacen con los troncos que el municipio retira: saltos, tocones escalonados, vigas de "
            "equilibrio y rampas sobre lomas naturales en el sector de grandes, y versiones bajas en "
            "el de pequeños. Lo único que se compra son los herrajes y fijaciones.",
            "Bancas, tótems de bolsas y letreros los fabrica el liceo técnico con el diseño que "
            "entrega el municipio, siguiendo el modelo de convenio con establecimientos técnicos. Lo "
            "que se compra es lo que el taller no puede producir: herrajes, dispensadores, basureros, "
            "rotulado y las señales de ruta, que deben cumplir norma de Tránsito.",
            "El aceite impregnante para madera se calculó en 40 litros —dos envases de 20 L con "
            "precio publicado— para la primera aplicación completa de toda la madera expuesta.",
        ],
        "items": [
            ("G.1", "Bancas de madera: material y mano de obra del liceo", 12, "u", 60000, 720000, LICEO, REFERENCIAL, "Fabricación del liceo técnico; valor referencial"),
            ("G.2", "Herrajes para bancas", 12, "u", 15000, 180000, COMPRA, REFERENCIAL, "Cotizar"),
            ("G.3", "Techos pequeños sobre bancas: estructura de madera", 3, "u", 150000, 450000, MUNI, REFERENCIAL, "Madera municipal"),
            ("G.4", "Techos pequeños sobre bancas: techumbre", 3, "u", 80000, 240000, COMPRA, REFERENCIAL, "Cotizar"),
            ("G.5", "Juegos de troncos del sector de grandes: saltos, tocones, vigas y rampas", 1, "gl", 600000, 600000, MUNI, REFERENCIAL, "Troncos municipales"),
            ("G.6", "Juegos de troncos del sector de pequeños", 1, "gl", 250000, 250000, MUNI, REFERENCIAL, "Troncos municipales"),
            ("G.7", "Herrajes y fijaciones de juegos", 1, "gl", 210000, 210000, COMPRA, REFERENCIAL, "Cotizar"),
            ("G.8", "Tótems de bolsas en madera", 5, "u", 40000, 200000, LICEO, REFERENCIAL, "Fabricación del liceo técnico; valor referencial"),
            ("G.9", "Dispensadores de bolsas de a una", 5, "u", 15000, 75000, COMPRA, REFERENCIAL, "Cotizar"),
            ("G.10", "Basureros con tapa", 5, "u", 60000, 300000, COMPRA, REFERENCIAL, "Cotizar o solicitar vía Plataforma de Economía Circular"),
            ("G.11", "Contenedor mayor de residuos", 1, "u", 150000, 150000, COMPRA, REFERENCIAL, "Cotizar"),
            ("G.12", "Letreros de madera: 3 de reglas, 2 de ocupado/libre, 1 de videovigilancia y 1 de entrada", 7, "u", 30000, 210000, LICEO, REFERENCIAL, "Fabricación del liceo técnico; valor referencial"),
            ("G.13", "Rotulado de letreros", 7, "u", 20000, 140000, COMPRA, REFERENCIAL, "Cotizar"),
            ("G.14", "Señales de ruta desde playas y costanera", 4, "u", 80000, 320000, COMPRA, REFERENCIAL, "Según norma de Tránsito; cotizar"),
            ("G.15", "Aceite impregnante exterior para madera, envase de 20 L", 2, "u", 68990, 137980, COMPRA, VERIFICADO, "Sodimac.cl, pack de 20 litros $68.990"),
        ],
    },
    {
        "codigo": "H",
        "nombre": "Paisajismo",
        "resumen": "Refuerzo de las franjas de separación con especies nativas.",
        "explicacion": [
            "El terreno se usa tal como está, así que el paisajismo se limita a reforzar lo que ya "
            "existe: unos 300 arbustos nativos en las franjas de separación entre sectores y en la "
            "barrera visual de los sectores de entrenamiento, compost municipal para la plantación y "
            "semilla de pasto para resembrar las zonas que se pisen durante la obra.",
            "Los arbustos se solicitan a CONAF dentro del convenio de arborización comunitaria, que "
            "en la Región de Los Lagos ya tiene precedente: junto al Servicio de Salud Osorno, CONAF "
            "aportó especies nativas, cercado, obra y asesoría por $24 millones. Por eso figuran como "
            "aporte y no como compra.",
            "Lo único que se compra en esta partida son 10 kg de semilla de pasto: $80.000 sobre un "
            "valor valorizado de $1.193.605.",
        ],
        "items": [
            ("H.1", "Arbustos nativos para franjas y barreras visuales", 300, "u", 3000, 900000, CONAF, REFERENCIAL, "Programa de Arborización de CONAF; valor referencial"),
            ("H.2", "Compost", 5, "m³", 42721, 213605, MUNI, VERIFICADO, "Valor de referencia Full Áridos 2026: $35.900 + IVA por m³"),
            ("H.3", "Semilla de pasto para resiembra", 10, "kg", 8000, 80000, COMPRA, REFERENCIAL, "Cotizar"),
        ],
    },
    {
        "codigo": "I",
        "nombre": "Mano de obra y servicios",
        "resumen": "El equipo que construye el canil, durante cuatro meses de obra.",
        "explicacion": [
            "La obra dura cuatro meses con frentes traslapados. El equipo permanente es un jefe de "
            "obra o maestro carpintero, tres carpinteros y cuatro jornales; se suman un gasfíter y un "
            "electricista autorizado durante un mes y medio cada uno, y un prevencionista de riesgos "
            "en media jornada durante toda la obra.",
            "Los sueldos se calcularon a partir de valores de mercado publicados para la construcción "
            "y se multiplicaron por un factor de costo empleador de 1,25, que incorpora cotizaciones y "
            "cargas: es el costo real para quien contrata, no el líquido que recibe el trabajador. Los "
            "cuatro jornales se valorizaron al ingreso mínimo de 2026 con el mismo factor.",
            "Los cuatro jornales son <strong>cuadrilla municipal</strong>: personal que ya existe y "
            "que se destina a la obra, por lo que sus $10.780.000 son aporte valorizado y no gasto a "
            "financiar. Ese es el aporte individual más grande del proyecto.",
            "Los servicios externos son retroexcavadora con operador —24 horas para fosa, zanjas y "
            "apoyo al pozo—, camión con chofer —10 días para troncos, grava y materiales— y la "
            "empresa de perforación, cuyo costo está en la partida E.",
            "El aporte al liceo técnico ($1.500.000) financia los insumos de taller con los que los "
            "estudiantes fabrican bancas, juegos, tablas, tótems, bebederos, arcos y letreros. Es un "
            "monto a convenir: contra él, el liceo entrega piezas valorizadas en $2.130.000 y los "
            "estudiantes obtienen práctica real en un encargo municipal.",
        ],
        "items": [
            ("I.1", "Jefe de obra / maestro carpintero", 4, "mes", 1185000, 4740000, COMPRA, VERIFICADO, "Sueldo de carpintero $948.000 (Chiletrabajos vía Mega, 2025) × factor de costo empleador"),
            ("I.2", "Carpinteros (3)", 12, "mes-persona", 813412, 9760950, COMPRA, VERIFICADO, "Sueldo promedio de carpintero $650.730 (Chiletrabajos, julio de 2026) × factor de costo empleador"),
            ("I.3", "Jornales (4): cuadrilla municipal", 16, "mes-persona", 673750, 10780000, CUADRILLA, VERIFICADO, "Ingreso mínimo 2026 × factor de costo empleador; personal municipal existente"),
            ("I.4", "Gasfíter", 1.5, "mes", 1025820, 1538730, COMPRA, VERIFICADO, "Maestro gásfiter $820.656 (Chiletrabajos vía Mega, 2025) × factor"),
            ("I.5", "Electricista autorizado SEC", 1.5, "mes", 1013320, 1519980, COMPRA, VERIFICADO, "Maestro eléctrico $810.656 (Chiletrabajos vía Mega, 2025) × factor"),
            ("I.6", "Prevencionista de riesgos (media jornada)", 4, "mes", 566000, 2264000, COMPRA, VERIFICADO, "Computrabajo 2026: sueldo promedio de prevencionista de riesgos $905.427; media jornada × factor de costo empleador"),
            ("I.7", "Retroexcavadora con operador: fosa, zanjas y apoyo al pozo", 24, "hora", 35000, 840000, COMPRA, VERIFICADO, "Jurmaq 2026: arriendo con operador $25.000 a $35.000 por hora; se usa el tope del rango por el traslado a Puerto Varas"),
            ("I.8", "Camión con chofer: troncos, grava y materiales", 10, "día", 250000, 2500000, COMPRA, VERIFICADO, "Mercado 2026: camión tolva de 15 m³ con chofer entre $200.000 y $250.000 por día; se usa el tope por incluir combustible"),
            ("I.9", "Aporte al liceo técnico para insumos de taller", 1, "gl", 1500000, 1500000, COMPRA, REFERENCIAL, "Monto a convenir"),
            ("I.10", "Plantación y asesoría de CONAF", 1, "gl", 800000, 800000, CONAF, REFERENCIAL, "Convenio de arborización; valor referencial"),
        ],
    },
]

# --------------------------------------------------------------------------
# Operación anual (un canil)
# --------------------------------------------------------------------------

OPERACION = [
    ("O.1", "Auxiliares de aseo (2), turnos que cubren 7 días", 24, "mes-persona", 673750, 16170000, COMPRA,
     "Ingreso mínimo 2026 × factor de costo empleador. Es el 69% de la operación a financiar."),
    ("O.2", "Mantención mensual por cuadrilla municipal", 12, "mes", 300000, 3600000, CUADRILLA,
     "Una visita mensual: cercos, juegos, madera, paneles, estanque y zanjas."),
    ("O.3", "Plan de datos 4G del router", 12, "mes", 25000, 300000, COMPRA,
     "Una sola conexión por canil, que sirve a cámaras, cerraduras y contadores."),
    ("O.4", "SIM del tótem SOS", 12, "mes", 8000, 96000, COMPRA,
     "Línea independiente, para que el tótem funcione aunque falle el router."),
    ("O.5", "Bolsas compostables", 7622, "u", 40, 304860, COMPRA,
     "20% de las 38.108 visitas proyectadas, a $40 la bolsa."),
    ("O.6", "Insumos de baño: papel, jabón, toallas, desinfectante y bolsas", 12, "mes", 120000, 1440000, COMPRA,
     "Consumo de dos recintos con uso diario."),
    ("O.7", "Retiro de residuos por el servicio municipal existente", 12, "mes", 100000, 1200000, MUNI,
     "Se suma el canil al recorrido municipal ya existente."),
    ("O.8", "Vaciado de fosa séptica con camión limpiafosas", 1, "vez", 150000, 150000, COMPRA,
     "Una vez al año; la frecuencia real se ajusta según uso."),
    ("O.9", "Análisis anual del agua", 1, "vez", 150000, 150000, COMPRA,
     "Laboratorio acreditado, además del análisis de línea base."),
    ("O.10", "Control de roedores", 12, "mes", 40000, 480000, COMPRA,
     "Medida sanitaria permanente por leptospirosis."),
    ("O.11", "Reposición de materiales: barniz, malla, madera y boquillas", 1, "gl", 2094511, 2094511, COMPRA,
     "2% del costo directo financiado. Cubre el desgaste normal del primer año."),
    ("O.12", "Provisión para reposición de baterías y equipos", 1, "gl", 1171291, 1171291, COMPRA,
     "10% anual del valor del sistema solar y de las cámaras, para no llegar sin fondos al recambio."),
    ("O.13", "Operativos de chip y vacuna antirrábica del veterinario municipal", 4, "operativo", 250000, 1000000, MUNI,
     "Cuatro al año, con el veterinario municipal que ya está en funciones."),
    ("O.14", "Aporte al liceo técnico para reposición de piezas de madera", 1, "gl", 500000, 500000, COMPRA,
     "Mantiene vivo el convenio y resuelve el recambio de piezas en contacto con agua."),
    ("O.15", "Seguro del recinto", 1, "gl", 622070, 622070, COMPRA,
     "0,5% de la inversión financiada."),
]

# --------------------------------------------------------------------------
# Calendario de pagos: código de partida o de ítem -> [(mes, fracción)]
# Meses 1 a 9: estudios y trámites. Meses 10 a 13: obra. Mes 14 en adelante:
# marcha blanca.
# --------------------------------------------------------------------------

PAGOS_ITEM = {
    "A.1": [(4, 1.0)],
    "A.2": [(5, 1 / 3), (6, 1 / 3), (7, 1 / 3)],
    "A.3": [(6, 1.0)],
    "A.4": [(8, 1.0)],
    "A.5": [(6, 1.0)],
    "A.6": [(4, 1.0)],
    "A.7": [(5, 0.25), (6, 0.25), (7, 0.25), (8, 0.25)],
    "A.8": [(8, 1.0)],
    "A.9": [(2, 0.5), (3, 0.5)],
    "A.10": [(12, 1.0)],
    "B.2": [(10, 0.25), (11, 0.25), (12, 0.25), (13, 0.25)],
    "C.16": [(7, 1.0)],
    "E.4": [(10, 0.5), (11, 0.5)],
    "E.5": [(11, 1.0)],
    "E.17": [(7, 1.0)],
    "E.22": [(7, 1.0)],
    "G.1": [(7, 1.0)],
    "G.8": [(7, 1.0)],
    "G.12": [(7, 1.0)],
    "I.1": [(10, 0.25), (11, 0.25), (12, 0.25), (13, 0.25)],
    "I.2": [(10, 0.25), (11, 0.25), (12, 0.25), (13, 0.25)],
    "I.3": [(10, 0.25), (11, 0.25), (12, 0.25), (13, 0.25)],
    "I.4": [(11, 0.5), (12, 0.5)],
    "I.5": [(11, 0.5), (12, 0.5)],
    "I.6": [(10, 0.25), (11, 0.25), (12, 0.25), (13, 0.25)],
    "I.7": [(10, 0.6), (11, 0.4)],
    "I.8": [(10, 0.25), (11, 0.25), (12, 0.25), (13, 0.25)],
    "I.9": [(6, 1.0)],
    "I.10": [(13, 1.0)],
}

PAGOS_PARTIDA = {
    "A": [(6, 1.0)],
    "B": [(10, 1.0)],
    "C": [(10, 0.4), (11, 0.6)],
    "D": [(10, 0.2), (11, 0.4), (12, 0.4)],
    "E": [(10, 0.25), (11, 0.4), (12, 0.35)],
    "F": [(11, 0.4), (12, 0.6)],
    "G": [(12, 0.4), (13, 0.6)],
    "H": [(13, 1.0)],
    "I": [(10, 0.25), (11, 0.25), (12, 0.25), (13, 0.25)],
}

ETAPAS_MES = {
    1: "Mesas técnicas y línea base",
    2: "Mesas técnicas y línea base",
    3: "Mesas técnicas y línea base",
    4: "Estudios y trámites",
    5: "Estudios y trámites",
    6: "Estudios y trámites",
    7: "Estudios y trámites",
    8: "Estudios y trámites",
    9: "Financiamiento y convenios",
    10: "Obra: faena, cerco y pozo",
    11: "Obra: cerco, baño, torre y redes",
    12: "Obra: agua, energía y seguridad",
    13: "Obra: mobiliario, paisajismo y pruebas",
}

MESES_MARCHA_BLANCA = [14, 15, 16, 17, 18, 19]

# Tiempos de ejecución de cada partida dentro de las 16 semanas de obra
SEMANAS_PARTIDA = {
    "A": ("Meses 3 a 9", "Antes de la obra: estudios, proyectos y trámites."),
    "B": ("Semanas 1 a 2", "Instalación de faena; el baño químico se mantiene las 16 semanas."),
    "C": ("Semanas 3 a 8", "Postes, malla, barrera enterrada, esclusas y portón."),
    "D": ("Semanas 4 a 10", "Baño, amarre, estacionamiento y senderos."),
    "E": ("Semanas 4 a 12", "Pozo y torre primero; redes y sistemas de refresco después."),
    "F": ("Semanas 8 a 12", "Sistema solar, cámaras, cerraduras, luminarias y tótem SOS."),
    "G": ("Semanas 10 a 14", "Instalación de piezas fabricadas por el liceo durante los meses 3 a 9."),
    "H": ("Semanas 10 a 14", "Plantación con CONAF, compost y resiembra."),
    "I": ("Semanas 1 a 16", "Equipo permanente durante toda la obra."),
}
