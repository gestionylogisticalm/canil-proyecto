# Prompts para generar las imágenes fotorrealistas del canil

Documento de trabajo interno. **No forma parte del plan que se entrega a la municipalidad.**

Las once imágenes del anexo D son renders de un modelo 3D con las medidas reales del proyecto.
Sirven para discutir el diseño, pero no son fotorrealistas. Para llegar a fotorrealismo hay que
pasar cada vista por un generador de imágenes.

---

## Cómo usarlo

Hay dos caminos. El primero da mucho mejor resultado.

### 1. Con la imagen 3D como referencia (recomendado)

Sube el PNG del render junto con el prompt y pide que **respete la composición**. Así la imagen
fotorrealista conserva las proporciones reales del proyecto —la hectárea, el baño de 16 m², el
amarre de 12 × 3 m, la torre de 4 m— en vez de inventarlas.

En ChatGPT, Gemini o Copilot: adjuntar el PNG y escribir *«Convierte esta escena en una fotografía
realista, manteniendo exactamente la misma composición, ubicación de los elementos y ángulo de
cámara»*, seguido del prompt de la vista.

En Midjourney: subir la imagen, copiar su URL y anteponerla al prompt, con `--iw 1.5` para que pese
la referencia.

En herramientas con ControlNet o img2img: usar el render como imagen base con fuerza 0,55 a 0,7.

### 2. Solo con el texto

Pegar el prompt tal cual. La imagen sale realista pero la distribución será libre: sirve para
ilustrar, no para mostrar el diseño.

Los archivos PNG en resolución completa están en `src/img/`.

---

## Bloque de estilo común

Agregar al final de cada prompt:

```
Photorealistic architectural photography, shot on a full-frame camera, 24mm lens for wide views and
50mm for detail views, f/8, natural daylight, soft overcast light typical of southern Chile, subtle
haze in the distance, realistic materials with visible wear, high dynamic range, no HDR halos,
sharp focus throughout, 16:9.
```

## Negativo común

```
cartoon, illustration, 3D render look, video game graphics, low poly, plastic materials, oversaturated
colors, fisheye distortion, warped fences, floating objects, distorted animals, extra limbs, garbled
text, watermark, people with deformed faces, tropical vegetation, palm trees, desert.
```

## Anclajes que deben repetirse siempre

Para que la serie completa se vea como el mismo lugar:

- Ubicación: Puerto Varas, sur de Chile, Región de Los Lagos.
- Paisaje: pradera verde húmeda, bosque nativo templado de fondo, volcán Osorno nevado en el
  horizonte, lago Llanquihue al fondo en las vistas amplias.
- Materiales: madera nativa envejecida, tejuela oscura en los techos, grava volcánica gris oscuro,
  malla galvanizada sobre postes de madera rústicos.
- Nada de plástico de colores, nada de juegos infantiles, nada de mesas de picnic.

---

## 1 · Vista general, un cuarto de bosque

Archivo de referencia: `canil-cuarto-bosque-aerea.png`

```
Aerial three-quarter view, drone at about 100 meters, of a one-hectare fenced public dog park in the
countryside near Puerto Varas, southern Chile. The land is left in its natural state: open mown
meadow across three quarters and a dense stand of native temperate forest occupying the back-right
quarter. Rustic wooden posts with galvanized wire mesh divide the hectare into a large-dog area, a
smaller area for small dogs, and two separate training enclosures at the back. A gravel parking lot
with about ten cars sits outside the fence at the front, next to a small wooden restroom building
with a steep dark shingled roof, a covered wooden tie-up shelter, and a four-meter timber water tower
with two white tanks. Dogs of different breeds run in the meadow. Dark volcanic gravel paths.
Overcast morning light.
```

## 2 · Acceso, un cuarto de bosque

Archivo de referencia: `canil-cuarto-bosque-acceso.png`

```
Eye-level photograph from the gravel parking lot of a public dog park near Puerto Varas, southern
Chile. In the foreground, parked cars on compacted gravel. Behind them, a rustic fence of wooden
posts and galvanized mesh, and beyond it the access area: a small public restroom built in vertical
wood siding with a steep shingled gable roof, wide eaves, white window frames and a solar panel on
the north slope, in the German colonial style of the region; next to it a long covered wooden tie-up
shelter with steel rings. Further back, the open meadow of the dog park with dogs running, and the
snow-capped Osorno volcano on the horizon across the lake.
```

## 3 · Vista general, solo pradera

Archivo de referencia: `canil-pradera-aerea.png`

```
Aerial three-quarter view of a one-hectare fenced public dog park near Puerto Varas, southern Chile,
entirely open mown meadow with no forest inside the fence, only scattered mature native trees for
shade and hedgerows of native shrubs along the internal divisions. Rustic wooden post and wire mesh
fencing, gravel parking outside, wooden restroom and tie-up shelter at the access, timber water
tower. Rolling green farmland around it, native forest on the far edges.
```

## 4 · Acceso, solo pradera

Archivo de referencia: `canil-pradera-acceso.png`

```
Photograph from the gravel parking area of a public dog park in open green farmland near Puerto
Varas, southern Chile. A four-meter timber water tower with two white plastic tanks stands to the
left, a covered wooden tie-up shelter in the middle, and a small wooden public restroom with a steep
shingled roof to the right. Rustic wooden post and galvanized mesh fence in the foreground. Open
meadow with dogs behind the fence, distant native forest and the Osorno volcano on the horizon.
```

## 5 · Vista general, mitad bosque

Archivo de referencia: `canil-mitad-bosque-aerea.png`

```
Aerial three-quarter view of a one-hectare fenced public dog park near Puerto Varas, southern Chile,
where dense native temperate forest covers the entire back half of the enclosure and open mown meadow
the front half. The fence line weaves between existing tree trunks without being attached to them.
Two training enclosures at the back are partly inside the forest and screened by shrubs. Gravel
parking, wooden restroom and tie-up shelter at the front.
```

## 6 · Acceso, mitad bosque

Archivo de referencia: `canil-mitad-bosque-acceso.png`

```
Photograph from the parking area of a public dog park near Puerto Varas, southern Chile, with dense
native temperate rainforest rising immediately behind the fenced meadow. Rustic wooden and wire mesh
fence, small wooden restroom with steep shingled roof and solar panel, covered tie-up shelter, gravel
paths. Wet green grass, moss on the tree trunks, soft overcast light.
```

## 7 · Baño público

Archivo de referencia: `detalle-bano.png`

```
Photograph of a small public restroom building in a rural park near Puerto Varas, southern Chile.
Two doors for two universal accessible cubicles, vertical wood siding weathered to grey-brown, a low
stone plinth, a steep gable roof covered in dark wooden shingles with wide overhanging eaves and
exposed rafter tails, white painted window and door frames, a solar panel mounted flush on the rear
roof slope, and a rain gutter feeding a downpipe. Gravel path in front, mown grass around, wooden
post and wire mesh fence behind, native forest and a distant snow-capped volcano. 50mm lens, three
quarter view, natural overcast light.
```

## 8 · Zona de amarre

Archivo de referencia: `detalle-amarre.png`

```
Photograph of a twelve by three meter covered dog tie-up shelter in a rural park near Puerto Varas,
southern Chile: rustic round wooden posts supporting a simple gable roof of corrugated galvanized
sheet, a horizontal wooden beam with galvanized steel tie rings spaced every three meters, compacted
gravel floor. A golden labrador is tied at one of the rings, waiting calmly. A person walks past. In
the background, the wooden restroom building and the gravel parking lot. 35mm lens, natural light.
```

## 9 · Juegos de troncos

Archivo de referencia: `detalle-juegos.png`

```
Photograph of the large-dog area of a public dog park near Puerto Varas, southern Chile: agility
elements built entirely from natural logs and rough sawn timber — log jumps, stepped tree stumps, a
balance beam, a ramp built into a small grass mound — spread across a mown green meadow. Dogs of
different breeds running and sniffing, a person watching from a simple wooden bench. Dense native
temperate forest at the back with a sniffing trail entering it. No plastic playground equipment,
no bright colors. Late morning overcast light.
```

## 10 · Bebederos y juegos de agua

Archivo de referencia: `detalle-agua.png`

```
Photograph of the cooling area of a public dog park near Puerto Varas, southern Chile: a shallow
wooden-framed splash pool set on a bed of volcanic gravel, a wooden pergola fitted with large-droplet
sprinklers, a wooden spray arch that dogs run through, and a continuous-flow wooden drinking trough.
A wet dog shakes itself beside the pool. Mown grass worn thin around the water features. Native
forest behind, soft daylight, water droplets catching the light.
```

## 11 · Letrero de reglas

Archivo de referencia: `detalle-letrero.png`

```
Close-up photograph of a wooden rules sign at the entrance of a public dog park near Puerto Varas,
southern Chile. A thick plank board mounted on two rustic wooden posts, with a small protective
wooden roof on top. The text is carved into the wood in relief and filled with dark blue and brown
paint, in a classic serif typeface. Weathered timber with visible grain, small knots and varnish
sheen. Behind it, the fenced meadow of the dog park, dogs playing, and the distant volcano out of
focus. 50mm lens, shallow depth of field on the background, sharp focus on the board.
```

Para que el texto salga legible y correcto, casi ningún generador escribe bien en español. Conviene
generar el letrero **sin texto** —pidiendo «a blank carved wooden board»— y después montar encima el
texto real, que ya está en el anexo B del plan:

```
Perro inscrito con chip · Vacuna antirrábica vigente · Perro desparasitado · Sin hembras en celo ni
cachorros · Niños siempre con un adulto · Supervise a su perro · Recoja las fecas de su perro ·
Horario de 6:00 a 21:00 · Zona videovigilada · Máximo 4 perros por paseador
```

---

## Qué revisar antes de dar una imagen por buena

1. Que el cerco sea de **postes de madera con malla**, no de reja metálica ni de madera maciza.
2. Que el techo del baño tenga **pendiente fuerte y tejuela oscura**: es lo que lo hace de Puerto
   Varas y no de cualquier parte.
3. Que **no aparezcan juegos de plástico** ni mesas de picnic.
4. Que los perros tengan cuatro patas, una cola y proporciones normales.
5. Que el volcán y el bosque se vean del sur de Chile, no tropicales.
6. Que la escala sea creíble: el baño es de 16 m², no una casa.
