// Apps Script (opcional): evita que una misma persona se inscriba en 2 juegos.
// En la hoja de respuestas del Form: Extensiones > Apps Script > pegar > Implementar como Aplicación web
// (Ejecutar como: yo · Acceso: cualquiera). Copia la URL en CONFIG.CHECK_URL del index.html.
// Orden de columnas de la hoja: A=Marca de tiempo, B=Nombre, C=Ficha, D=Documento, E=Juego
function doGet(e) {
  const rows = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0].getDataRange().getValues().slice(1);
  const doc = String(e.parameter.documento || ""), ficha = String(e.parameter.ficha || "");
  const hit = rows.find(r => String(r[3]) === doc || String(r[2]) === ficha);
  return ContentService.createTextOutput(JSON.stringify({ existe: !!hit, juego: hit ? hit[4] : "" }))
    .setMimeType(ContentService.MimeType.JSON);
}
