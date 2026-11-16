# Plan de actividades — plantilla del modo «asistentes» (kit v1.5)

Nueva en v1.3.2; **desde v1.4 la escriben todos los roles de `supervision.asistentes.roles`** (por defecto el
Arquitecto, el Ingeniero y el Verificador, en Claude) cuando `supervision.modo = "asistentes"`
(`MOTOR_EXTERNO.md` §10). Va en la carpeta del rol (`<escribe_en>/<ID>_plan_actividades.md`), **antes** de su
artefacto: la orden, la entrega o el veredicto. Divide el trabajo mecánico del rol en ACTIVIDADES SECUENCIALES;
cada una la ejecuta un asistente Gemini (agy) y la vigila un monitor de Claude. El rol conserva para sí **las
decisiones, el juicio y la redacción final de su artefacto**; no lee las salidas largas: lee el veredicto corto de
cada actividad.

**Usarlo no es opcional (v1.4).** Mientras el uso de los asistentes quedó a criterio del rol, los asistentes se
ignoraron hasta que el Director midió que no se usaban. Por eso el plan lleva la tabla **«Cobertura»**: cada tipo
del catálogo, con las actividades que lo cubren o con `Sin asistente: <motivo concreto>`. El Agente C lo mide al
cerrar el ciclo con `scripts/medir_asistentes.py <ciclo>`, que lee este plan, los registros de agy y los
veredictos en disco, e investiga cada tipo sin actividad y sin motivo.

Se copia al directorio de plantillas del proyecto (`proyecto.dir_plantillas`) y se rellena por orden; los
marcadores `<…>` se sustituyen. Es un artefacto del rol que lo escribe: ningún asistente ni monitor lo edita.

## Catálogo base de actividades

| Tipo | Qué es | Herramienta | Asistente (por defecto) | Monitor (por defecto) |
|---|---|---|---|---|
| `A-lectura` | resumen o extracto con punteros `archivo:línea` de los tramos que el Arquitecto necesita | tramos y `git` de lectura | `gemini-3.8-flash-low` | Haiku |
| `A-prototipo` | cambio de código en una COPIA, con los tests corridos | herramienta segura (`copiar`, `clonar`, `poner`, `correr`, `diff`, `sello`) | `gemini-3.8-flash-high` | Sonnet |
| `A-medición` | corridas y tablas | herramienta segura (`correr`, `diff`, `sello`, `mutar`) | `gemini-3.8-flash-low` | Haiku |
| `A-borrador` | tablas, anexos, primer aplicador | lectura | `gemini-3.8-flash-medium` | Sonnet |
| `A-revisión` | cotejo de un borrador contra sus fuentes | lectura y `diff` | `gemini-3.8-flash-medium` | Sonnet |
| `A-navegación` *(v1.5)* | leer y navegar sitios web: páginas, tablas y cifras que solo están en un navegador (tableros, JupyterHub, GitLab, portales) | subagente `browser` de agy sobre el Chrome del kit; no actúa sobre el sitio | `gemini-3.8-flash-medium` | Haiku |

Qué suele delegar cada rol (orientación; la tabla «Cobertura» dice lo que de verdad hizo):

| Rol | Tipos que suelen aplicar | Lo que nunca delega |
|---|---|---|
| Arquitecto | los cinco, y `A-navegación` cuando el encuadre depende de lo que muestra un sitio | las decisiones (DA-n), el diseño, la redacción final y la firma de la orden |
| Ingeniero | `A-medición` (correr las pruebas en una copia, sellos y finales de línea, huella de la carpeta real), `A-revisión` (cotejar la evidencia con los criterios de la orden), `A-lectura` (tramos de la orden), `A-navegación` (ver el resultado publicado de un cambio) | aplicar el cambio en el repositorio, la entrega y sus dudas |
| Verificador | `A-medición` (todas las pruebas en una copia, sellos, alcance del diff, huella), `A-revisión` (que cada salida de la entrega lleve su comando, cotejo contra las fuentes), `A-lectura`, `A-navegación` (que el tablero o la página publicada muestre lo que dice la entrega) | qué se verifica, las sondas que diseña, el juicio, cada defecto y el veredicto |

Un tipo que no aplica al rol se marca igual en «Cobertura», con el motivo (`Sin asistente: el prototipo es del
Arquitecto`). Un motivo vale si se puede comprobar: «la herramienta segura no corre este script», «CUOTA en el
lanzamiento <registro>», «no hay pruebas que correr en este carril». «No hacía falta» o «era más rápido hacerlo yo»
no valen: son la razón por la que el modo se ignoraba.

Son los valores del ejemplo de `coordinador.json` (`supervision.asistentes.actividades`); el plan solo los
cambia con una razón escrita en la fila. `gemini-4-argon-high` va **solo** si el plan lo justifica por escrito
(sección «Justificación Argon»): su bolsa es chica y semanal. La bolsa «Claude and GPT» de agy no se usa para
trabajo de rutina: un asistente corre siempre en un modelo gemini-*.

## Reglas del plan

1. **Secuencial.** Cada actividad dice de cuál depende; no se lanza hasta que la anterior tiene veredicto
   ACEPTADO. Las que no dependen entre sí pueden ir una tras otra sin esperar; no en paralelo (el lanzador
   serializa los lanzamientos de la máquina).
2. **Entrada, salida y criterio, cerrados.** La entrada nombra rutas, tramos o comandos exactos. La salida es
   una ruta bajo `asistentes/<ciclo>_<id>/`. El criterio de aceptación es **verificable**: el comando exacto que
   el monitor vuelve a correr, o la muestra que vuelve a leer (cuántos elementos y de dónde). «Que esté bien»
   no es un criterio.
3. **Lo que produce un asistente orienta; no es un hecho** hasta que el monitor, o tú, lo vuelve a medir. Lo no
   verificado se rotula `no verificado` y no entra a la orden como cifra.
4. **El monitor devuelve un veredicto corto, no la salida.** Máximo 2 reintentos del asistente con una nota
   concreta; después, ESCALAR a ti. En CUOTA (exit 4 del lanzador) el monitor NO cambia de modelo: devuelve
   «CUOTA» y esa actividad la haces con un auxiliar de Claude de tu sección «Tus auxiliares».
5. **Te reservas** lo que tu rol no delega (tabla de arriba): decisiones, juicio, redacción final y firma.
6. **Cobertura completa.** Cada tipo del catálogo tiene su fila: las actividades que lo cubren, o
   `Sin asistente: <motivo>` con al menos 15 caracteres que se puedan comprobar. Si cambias de idea a mitad
   de turno (una actividad que no lanzaste), corrige la fila antes de terminar.
7. **Monitores con tope.** Cada monitor recibe en su encargo el tope de llamadas de `auxiliar`
   (`modo_autonomo.topes_llamadas`, 20 por defecto).
8. **Ids con el prefijo del rol** (`arq1`, `ing1`, `ver1`…): en un mismo ciclo, dos roles no pueden compartir la
   carpeta `asistentes/<ciclo>_<id>/`. `medir_asistentes.py` marca un id repetido entre roles.

## Plantilla

````text
# Plan de actividades — <ID del artefacto> · ciclo <ciclo>
Rol: [<ROL · MODELO · turno N>] · Fecha: <fecha> · Entrada: <encuadre, orden o entrega>

## Actividades
| Id | Tipo | Depende de | Entrada (rutas, tramos, comandos) | Salida (bajo asistentes/<ciclo>_<id>/) | Criterio de aceptación VERIFICABLE | Asistente | Monitor |
|---|---|---|---|---|---|---|---|
| <arq1> | A-lectura | — | <tramos o rutas exactas> | <archivo.md> | <p. ej. «los 6 tramos pedidos, ≤ 40 líneas cada uno; el monitor relee 3 punteros»> | gemini-3.8-flash-low | haiku |
| <arq2> | A-borrador | <arq1> | <salida de arq1 + fuentes> | <borrador.md> | <p. ej. «cada cifra con puntero; el monitor vuelve a medir 5»> | gemini-3.8-flash-medium | sonnet |

## Argon
Justificación Argon: <una sola línea, solo si alguna fila usa gemini-4-argon-high: por qué el trabajo lo merece y
qué se pierde con flash. Escribe «no aplica» si ninguna lo usa. Sin esta línea con al menos 15 caracteres de
texto, el lanzador se niega a lanzar Argon a un asistente.>

## Cobertura (una fila por tipo del catálogo; la lee scripts/medir_asistentes.py)
| Tipo | Actividades | Sin asistente (motivo) |
|---|---|---|
| A-lectura | <arq1> | — |
| A-prototipo | — | Sin asistente: <motivo concreto y comprobable> |
| A-medicion | <ids o —> | <— o Sin asistente: motivo> |
| A-borrador | <ids o —> | <— o Sin asistente: motivo> |
| A-revision | <ids o —> | <— o Sin asistente: motivo> |
| A-navegacion | <ids o —> | <— o Sin asistente: motivo, p. ej. «el ciclo no consulta ningún sitio web»> |

## Lo que me reservo (no se delega)
<decisiones, juicio, redacción final y firma de mi artefacto>

## Veredictos recibidos (una línea por actividad; la llena el rol)
| Id | Veredicto | Reintentos | Registro | Lo no verificado |
|---|---|---|---|---|
````

La línea «Justificación Argon: <texto>» se comprueba: para lanzar un asistente en Argon, el monitor pasa
`--plan <este archivo>` al lanzador y este exige una línea que empiece por `Justificación Argon:` seguida de al
menos 15 caracteres de texto, en esa misma línea.

## Formato del veredicto corto

Lo escribe el monitor (en `asistentes/<ciclo>_<id>/VEREDICTO.md`) y lo devuelve **tal cual** al rol que lo lanzó, en
12 líneas como máximo; el rol no lee nada más de esa actividad salvo los punteros que el veredicto cita. La primera
línea la lee `scripts/medir_asistentes.py`: no cambies su forma.

````text
VEREDICTO <ciclo>_<id> (<tipo>): ACEPTADO | RECHAZADO | ESCALAR | CUOTA
Motivo: <una o dos líneas; si no es ACEPTADO, qué falló exactamente>
Muestra: <qué se volvió a medir: n de N elementos, con qué comando o lectura>
Salida: <ruta de la salida del asistente>
Registro: <ruta del .ndjson del último lanzamiento> · lanzamientos: <n> · reintentos: <0-2>
Punteros: <hasta 5 ruta:línea que el Arquitecto puede abrir si quiere comprobar>
No verificado: <lo que quedó sin medir, rotulado; «nada» solo si se midió todo>
````

- **ACEPTADO**: la muestra coincidió con las fuentes y se cumplió el criterio. No es una garantía del resto
  (por eso `No verificado`).
- **RECHAZADO**: no se acepta y no se reintenta (p. ej. un resultado ya producido que se entrega a verificar, o un
  motivo que una nota no arregla). Dice el motivo.
- **ESCALAR**: dos reintentos agotados sin que la muestra coincida. Pasa al rol que lanzó al monitor.
- **CUOTA**: el lanzador salió con 4. El monitor no cambia de modelo ni activa créditos de pago.
