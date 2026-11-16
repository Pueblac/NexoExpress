# Encargo del asistente, por tipo de actividad — plantilla del modo «asistentes» (kit v1.5)

Nueva en v1.3.2. **El monitor** (un subagente de Claude) compone con esta plantilla el encargo del asistente a partir
de la fila del plan de actividades y lo guarda **dentro del workspace** (`<modo_autonomo.dir_encargos>/<ciclo>_<id>_asistente.txt`:
agy no lee fuera de él). `lanzar_agy.py` le dice al asistente: «tu arranque completo está en <ese archivo>; léelo íntegro
y cúmplelo, incluida la ADENDA final». La capa del asistente (`agy_roles.md`, secciones `asistente` y `asist_<tipo>`) ya
lleva lo técnico del motor, incluido **«agrupa en un mismo turno las acciones independientes»**; el encargo solo
dice **qué** hacer. Un encargo se compone de tres partes en este orden: la CABECERA, el bloque de la actividad y la ADENDA.

Los `<…>` se sustituyen con lo de la fila del plan, **literal**: el monitor no mejora, no amplía y no reinterpreta la
fila. Si la fila es ambigua, no lanza: devuelve ESCALAR con la duda.

## Cabecera (todo encargo)

````text
ENCARGO DE ASISTENTE — <ciclo>_<id> · actividad <tipo>
Eres el asistente de esta actividad. Lo que produzcas orienta: un monitor volverá a medir una muestra contra las
fuentes y, si no coincide, te rechazará. Haz exactamente lo pedido; si algo es ambiguo, escribe DUDA: al inicio de
tu salida y termina.
Agrupa en un mismo turno las acciones independientes (varias lecturas, varias comprobaciones).
Si un comando no corre, se deniega o no existe: NO improvises otro (ni variante, ni `--help`, ni otra ruta). Anótalo
como NO EJECUTADO en tu salida, con el comando y la línea que recibiste, y sigue con lo demás que este encargo pide.
Tu carpeta de salida: <asistentes/<ciclo>_<id>/>. Escribes solo ahí.
Fuentes que puedes leer: <rutas y repositorios del plan>. Nada más.
````

## Bloque A-lectura

````text
TAREA (A-lectura)
Entrada: <lista de tramos o temas: ruta y rango, o el archivo de temas>.
Haz: por cada pedido, copia LITERALES las líneas del tramo (máximo 40 por tramo) y su puntero ruta:línea-línea. Si
hay herramienta de tramos entre tus comandos, córrela primero con todos los temas juntos.
Salida: <archivo.md> con una sección por pedido: el puntero, y debajo las líneas literales en un bloque de código.
Resumen: <ninguno | 1 a 3 frases por tramo, cada una con su puntero>.
Criterio de aceptación: <el de la fila del plan>.
````

## Bloque A-prototipo

````text
TAREA (A-prototipo)
Entrada: <commit o copia base; archivos a cambiar; el cambio pedido, descrito sin ambigüedad>.
Haz: con la herramienta segura, <copiar|clonar> la base en una copia llamada <nombre>; escribe cada archivo cambiado
completo en tu carpeta de salida y ponlo en la copia con `poner`; corre con `correr` los tests: <lista>.
Salida: <archivos> (en tu carpeta) y <informe.md> con: el diff literal (`diff` contra la base), el `sello` de cada
archivo cambiado y la salida literal de cada test con su comando delante, sin reformatear.
No toques el repositorio ni decidas diseño: si el cambio pedido no se puede hacer como está, escribe DUDA:.
Criterio de aceptación: <el de la fila del plan>.
````

## Bloque A-medición

````text
TAREA (A-medición)
Entrada: <la lista exacta de comandos de la herramienta segura, uno por línea>.
Haz: corre cada comando tal cual, con la herramienta segura, y pega su salida literal con el comando delante.
Salida: <tabla.md> con la tabla que se describe aquí: <columnas y filas esperadas>, y debajo las salidas literales.
Si un comando corre y falla, anótalo como FALLA (con su exit); si la herramienta dice que no existe, NO EXISTE; si
no corrió (se denegó, se rechazó o no dio salida), NO EJECUTADO. No pruebes variantes ni pidas su `--help`.
Criterio de aceptación: <el de la fila del plan>.
````

## Bloque A-borrador

````text
TAREA (A-borrador)
Entrada: <hechos y fuentes: la salida aceptada de la actividad <id anterior> y las rutas que se citan>.
Haz: redacta <tabla | anexo | aplicador> con SOLO esos hechos. Cada dato lleva su puntero ruta:línea; el que no tenga
fuente va marcado [sin fuente]. No añadas cifras ni hechos.
Salida: <borrador.md>.
Criterio de aceptación: <el de la fila del plan>.
````

## Bloque A-revisión

````text
TAREA (A-revisión)
Entrada: el borrador <ruta> y las fuentes <rutas>.
Haz: por cada afirmación o cifra del borrador, busca su fuente y anota si coincide. No corrijas el borrador ni juzgues
su diseño.
Salida: <revision.md> con la tabla: afirmación o cifra | fuente ruta:línea | coincide (sí, no, no comprobable).
Criterio de aceptación: <el de la fila del plan>.
````

## Bloque A-navegación

Nuevo en v1.5. El monitor abre el Chrome del kit antes de lanzar (`abrir_navegador.py abrir`) y lo cierra después.

````text
TAREA (A-navegación)
Entrada: <URL de partida y, si hace falta, el camino dentro del sitio: qué enlace, pestaña, filtro o página>.
Haz: con tu subagente browser abre cada URL, navega lo indicado y extrae, LITERAL, lo pedido: <textos, tablas o
cifras, con el elemento o selector de cada uno>. Solo lees y navegas: no envías formularios que cambien algo, no
escribes credenciales ni datos personales. Si una página pide iniciar sesión, un segundo factor o un captcha, escribe
MANUAL: <URL> pide <qué> al inicio de tu salida y termina.
Salida: <archivo.md> con una sección por URL: el título, la URL final y lo extraído, cada dato con su elemento o
selector.<; y la captura <nombre.png>, solo si se pide>.
Criterio de aceptación: <el de la fila del plan; p. ej. «el monitor vuelve a abrir 2 URL y compara título y 3 datos»>.
````

## ADENDA (todo encargo, al final)

````text
ADENDA — tu respuesta final
La ruta de tu salida, un resumen de máximo 10 líneas y tus dudas o STOP. No narres lo que hiciste. Si corriste
comandos, la salida literal está en tu archivo, no en la respuesta. Lo que no mediste tú va rotulado «no verificado».
Si llegas al tope de llamadas, escribe STOP: tope de llamadas al inicio de tu salida con lo que falta.
Lo que quedó NO EJECUTADO va listado en tu respuesta, con su comando.
````
