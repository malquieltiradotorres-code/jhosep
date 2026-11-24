// Apps Script (opcional): evita que una misma cédula se registre dos veces (en el mismo juego o en otro).
// En la hoja de respuestas del Form: Extensiones > Apps Script > pegar > Implementar como Aplicación web
// (Ejecutar como: yo · Acceso: cualquiera). Copia la URL en CONFIG.CHECK_URL del index.html.
// Orden de columnas de la hoja: A=Marca de tiempo, B=Nombre, C=Ficha, D=Cédula, E=Juego
function doGet(e) {
  const solo = v => String(v || "").replace(/\D/g, "");
  const rows = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0].getDataRange().getValues().slice(1);
  const doc = solo(e.parameter.documento);
  const hit = doc && rows.find(r => solo(r[3]) === doc);
  return ContentService.createTextOutput(JSON.stringify({ existe: !!hit, juego: hit ? hit[4] : "" }))
    .setMimeType(ContentService.MimeType.JSON);
}
