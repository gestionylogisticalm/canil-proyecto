#!/usr/bin/env node
/**
 * Render de HTML a PDF con Chromium (Playwright).
 *
 * Uso:  node build/render.js '<json de configuración>'
 *
 * Configuración:
 *   { "entrada": "ruta.html", "salida": "ruta.pdf",
 *     "pie": true|false, "titulo": "texto del pie", "margenInferior": "14mm" }
 */

const path = require('path');
const { chromium } = require('playwright');

async function main() {
  const cfg = JSON.parse(process.argv[2]);
  const entrada = path.resolve(cfg.entrada);
  const salida = path.resolve(cfg.salida);

  const navegador = await chromium.launch();
  const pagina = await navegador.newPage();
  await pagina.goto('file://' + entrada, { waitUntil: 'networkidle' });
  await pagina.evaluate(() => document.fonts.ready);

  const pie = `
    <div style="width:100%; font-family:'Source Sans 3', Arial, sans-serif; font-size:7.5pt;
                color:#5a636b; padding:0 17mm; margin-top:-2mm;
                display:flex; justify-content:space-between; align-items:center;">
      <span style="letter-spacing:0.04em;">${cfg.titulo || ''}</span>
      <span style="font-weight:600; color:#1f4d35;"><span class="pageNumber"></span></span>
    </div>`;

  await pagina.pdf({
    path: salida,
    format: 'A4',
    printBackground: true,
    displayHeaderFooter: !!cfg.pie,
    headerTemplate: '<span></span>',
    footerTemplate: cfg.pie ? pie : '<span></span>',
    margin: cfg.pie
      ? { top: '14mm', right: '0mm', bottom: cfg.margenInferior || '16mm', left: '0mm' }
      : { top: '0mm', right: '0mm', bottom: '0mm', left: '0mm' },
  });

  await navegador.close();
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
