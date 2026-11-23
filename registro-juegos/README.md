# Inscripción a Juegos

Página de una sola pantalla: eliges **Ajedrez, Dominó o Bingo**, escribes nombre y apellido, ficha y documento, y pulsas **Participar**. Los datos llegan a tu Google Form.

## Conectar con tu Google Form
1. Crea el Form con 4 preguntas de respuesta corta: *Nombre y apellido*, *Número de ficha*, *Número de documento*, *Juego*.
2. Menú ⋮ > **Obtener enlace rellenado previamente**, llena cada campo con un texto de prueba y pulsa **Obtener enlace**. En la URL verás `entry.123456=...` para cada pregunta.
3. En `index.html`, bloque `CONFIG`: cambia `FORM_URL` (el link del Form, pero terminado en `/formResponse`) y los 4 `entry.XXXX`.

## Un solo juego por persona
- La página bloquea repetidos por documento o ficha en el mismo dispositivo.
- Para bloquearlos de verdad (desde cualquier dispositivo), pega `Code.gs` en la hoja de respuestas, implícalo como aplicación web y pon su URL en `CHECK_URL`.
