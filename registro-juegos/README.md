# Torneo de Juegos

Son **dos archivos separados**, para que los jugadores solo vean el registro:

| Archivo | Quién lo usa | Qué tiene |
|---|---|---|
| `index.html` | **Jugadores** (este es el único que compartes) | Solo el formulario de registro. |
| `admin.html` | **Solo el organizador** (no lo compartas ni lo subas) | Inscritos, equipos de dominó, clasificación de ajedrez y llaves de dominó. |

## Registro (index.html)
Nombre y apellido, ficha (lista), cédula y juego (lista). Si el juego es **Dominó**, aparece además la **cédula del compañero**: los participantes arman sus parejas como quieran.
- La única validación es la **cédula**: no puede repetirse en ningún juego. La ficha se elige de una lista (`FICHAS` en `CONFIG`) y puede repetirse.

## Equipos de dominó (admin.html > Equipos)
Una pareja queda confirmada cuando **los dos se escriben mutuamente** (A pone la cédula de B y B pone la de A). Los que no coinciden aparecen como *Pendientes* con el motivo, y puedes **unirlos a mano**.

## Clasificación de ajedrez (admin.html > Ajedrez)
Sistema suizo: eliges el número de rondas, el programa empareja a los que van con puntos parecidos (sin repetir rivales mientras se pueda) y tú marcas cada resultado (1-0, ½, 0-1). Victoria 1 punto, tablas ½, descanso (si son impares) 1 punto. Empates se desempatan con Buchholz. Al terminar las rondas muestra al campeón.

## Llaves de dominó (admin.html > Llaves)
Eliminación directa con las parejas confirmadas. Toca una pareja para marcarla ganadora.

## Conectar con Google
1. Crea el Form con **5 preguntas de respuesta corta, en este orden**: *Nombre y apellido*, *Número de ficha*, *Número de cédula*, *Juego*, *Cédula del compañero (dominó)* (esta última no obligatoria).
2. Menú ⋮ > **Obtener enlace rellenado previamente**, llena cada campo con un texto de prueba y **Obtener enlace**. En la URL verás `entry.123456=...` para cada pregunta.
3. En `index.html`, bloque `CONFIG`: cambia `FORM_URL` (link del Form terminado en `/formResponse`) y los 5 `entry.XXXX`.
4. (Opcional, recomendado) Para bloquear cédulas repetidas desde cualquier celular: pega `Code.gs` en la hoja de respuestas (Extensiones > Apps Script), publícalo como aplicación web y pon su URL en `CHECK_URL`.
5. Para que `admin.html` vea a los inscritos: en la hoja de respuestas, Archivo > Compartir > **Publicar en la web** > CSV, y pon ese enlace en `SHEET_CSV_URL` dentro de `admin.html`.

## Seguridad: por qué los jugadores no pueden manipular los resultados
- Los jugadores solo reciben `index.html`: no contiene equipos, llaves ni clasificación.
- Equipos, llaves y resultados de ajedrez **se guardan solo en el navegador del organizador**, no en el Form ni en internet. Nadie más puede cambiarlos.
- **No subas `admin.html` a un sitio público.** Ábrelo desde tu celular o computador como archivo. Tiene el enlace de la hoja con las cédulas.
- Usa siempre el mismo dispositivo y navegador para el torneo; si borras los datos del navegador se pierden los resultados.
- Limitación: el Google Form es público por naturaleza (alguien podría enviarle datos por fuera de la página); por eso se revisa la cédula con `Code.gs`.
