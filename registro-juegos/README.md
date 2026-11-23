# Torneo de Juegos

Página móvil (modo claro y oscuro) con 4 pantallas, todas en `index.html`:

| Pantalla | Para quién | Qué hace |
|---|---|---|
| **Registro** | Participantes | Tres botones (Ajedrez, Dominó, Bingo) abren la lista de participantes de cada juego. Abajo, el formulario: nombre y apellido, ficha, documento y una lista para elegir el juego. |
| **Participantes** | Todos | Lista de inscritos de un juego, con pestañas para cambiar de juego y buscador. No muestra el documento. |
| **Equipos** | Organizador | Lista de jugadores de Dominó y de las parejas sorteadas. |
| **Sorteo** | Organizador | Mezcla a los jugadores al azar y arma las parejas (el dominó se inscribe de forma individual). |
| **Llaves** | Organizador | Cuadro de eliminación directa. Toca una pareja para marcarla ganadora y avanza sola. |

## 1. Conectar el registro con tu Google Form
1. Crea el Form con 4 preguntas de respuesta corta, en este orden: *Nombre y apellido*, *Número de ficha*, *Número de documento*, *Juego*.
2. Menú ⋮ > **Obtener enlace rellenado previamente**, llena cada campo con un texto de prueba y pulsa **Obtener enlace**. En la URL verás `entry.123456=...` para cada pregunta.
3. En `index.html`, bloque `CONFIG`: cambia `FORM_URL` (el link del Form terminado en `/formResponse`) y los 4 `entry.XXXX`.

## 2. Un solo juego por persona
- La página bloquea repetidos por documento o ficha en el mismo dispositivo.
- Para bloquearlos desde cualquier dispositivo, pega `Code.gs` en la hoja de respuestas (Extensiones > Apps Script), publícalo como aplicación web y pon su URL en `CHECK_URL`.

## 3. Que Participantes y Equipos lean todos los inscritos
En la hoja de respuestas del Form: Archivo > Compartir > **Publicar en la web** > hoja de respuestas > formato **CSV**. Pon ese enlace en `SHEET_CSV_URL`. Columnas esperadas: A fecha, B nombre, C ficha, D documento, E juego. Sin esto, Participantes solo muestra a quienes se inscribieron desde ese mismo dispositivo, y en Equipos los jugadores se agregan a mano con **+ Jugador**.

## Importante
- El sorteo y los resultados se guardan **solo en el navegador del organizador** (no se comparten entre dispositivos). Haz el sorteo en un solo dispositivo.
- Las pantallas Equipos, Sorteo y Llaves no tienen contraseña: cualquiera que abra el enlace puede verlas y hacer su propio sorteo local. Si el enlace es público, comparte solo `#registro` con los participantes.
