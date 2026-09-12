#!/usr/bin/env node
/**
 * Renderiza las seis imágenes 3D del canil.
 *
 * Tres proporciones de bosque × dos ángulos de cámara:
 *   cuarto  · un cuarto de bosque y el resto pradera
 *   pradera · solo pradera
 *   mitad   · mitad bosque y mitad pradera
 *
 * Uso:  node build/3d/render3d.js
 */

const path = require('path');
const fs = require('fs');
const { chromium } = require('playwright');

const AQUI = __dirname;
const SALIDA = path.resolve(AQUI, '..', '..', 'src', 'img');
/* se renderiza al doble de resolución y la imagen final se reduce:
   el supermuestreo elimina los bordes dentados */
const ANCHO = 3000;
const ALTO = 1688;

const COMBINACIONES = [
  { conf: 'cuarto', vista: 'aerea', archivo: 'canil-cuarto-bosque-aerea.png' },
  { conf: 'cuarto', vista: 'acceso', archivo: 'canil-cuarto-bosque-acceso.png' },
  { conf: 'pradera', vista: 'aerea', archivo: 'canil-pradera-aerea.png' },
  { conf: 'pradera', vista: 'acceso', archivo: 'canil-pradera-acceso.png' },
  { conf: 'mitad', vista: 'aerea', archivo: 'canil-mitad-bosque-aerea.png' },
  { conf: 'mitad', vista: 'acceso', archivo: 'canil-mitad-bosque-acceso.png' },
  // vistas de detalle de los espacios del canil
  { conf: 'cuarto', vista: 'bano', archivo: 'detalle-bano.png' },
  { conf: 'cuarto', vista: 'amarre', archivo: 'detalle-amarre.png' },
  { conf: 'cuarto', vista: 'juegos', archivo: 'detalle-juegos.png' },
  { conf: 'cuarto', vista: 'agua', archivo: 'detalle-agua.png' },
  { conf: 'cuarto', vista: 'letrero', archivo: 'detalle-letrero.png' },
];

async function main() {
  fs.mkdirSync(SALIDA, { recursive: true });
  const navegador = await chromium.launch({
    args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'],
  });
  const pagina = await navegador.newPage({ viewport: { width: ANCHO, height: ALTO } });
  pagina.on('pageerror', (e) => console.error('  error en la escena:', e.message));

  for (const c of COMBINACIONES) {
    const url = 'file://' + path.join(AQUI, 'escena.html')
      + `?conf=${c.conf}&vista=${c.vista}&w=${ANCHO}&h=${ALTO}`;
    const t0 = Date.now();
    await pagina.goto(url, { waitUntil: 'load' });
    await pagina.waitForFunction('window.__listo === true', null, { timeout: 300000 });
    const lienzo = await pagina.$('canvas');
    await lienzo.screenshot({ path: path.join(SALIDA, c.archivo) });
    console.log(`  ${c.archivo}  (${((Date.now() - t0) / 1000).toFixed(1)} s)`);
  }

  await navegador.close();
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
