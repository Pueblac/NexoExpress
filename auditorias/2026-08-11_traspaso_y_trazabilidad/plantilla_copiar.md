# MT-T1 — Plantillas del bloque `COPIAR` (Ruta B) y protocolo de PO-1

**Ciclo:** `2026-08-11_traspaso_y_trazabilidad` · **Micro-tarea:** MT-T1 [Baja]
**Productor:** Arquitecto Macro — Claude Opus 5
**Vía:** colapso F1/F2 para esta MT, previsto en §2 para complejidad Baja y
ordenado por el Director el 11-08 ("ejecuta antes PO-1"). Justificación:
§3.1 dice que la Parada va **antes** de gastar la auditoría, porque no tiene
sentido auditar un mecanismo que el Director puede pedir cambiar en cuanto
lo toque. F5 y F6 siguen siendo obligatorias para el resto de la tanda.

---

## 0. Respuesta correcta, fijada ANTES de la corrida

El receptor de A/B-1 debe devolver **los 10 nombres de campo** del AVISO
(§5 de la metodología, estado a 11-08-2026), en este orden:

```
1. CICLO      2. FASE       3. TURNO DE   4. MODELO     5. ENTREGAR
6. ADJUNTOS   7. DESTINO    8. ACCIÓN     9. OBSERVABLE 10. VUELVE A
```

**Por qué se fija aquí y ahora.** Si el Arquitecto leyera la respuesta del
receptor y luego decidiera si es correcta, estaría calificando el examen con
la hoja del alumno delante. Igual que la medición base congelada para MT-T2:
el criterio se escribe antes.

*Nota:* `TRAZABILIDAD` **no** debe aparecer — ese campo lo añade MT-T5 y hoy
no está en §5. Si el receptor lo incluye, es que se lo inventó a partir de
otro artefacto del expediente, y eso invalidaría la corrida por
contaminación de contexto.

---

## 1. Plantilla FIJA del Verificador — cinco huecos, prosa prohibida

El emisor rellena **sólo** `{CICLO}`, `{MT}`, `{RUTA_SPEC}`,
`{RUTA_INFORME}`, `{RUTA_SALIDA}`. Todo lo demás es literal e invariable.
**Un bloque de verificación con una sola frase añadida es INVÁLIDO** y el
Director lo devuelve sin ejecutarlo.

```
Rol: Verificador del ciclo {CICLO}, metodología v2.6 del ecosistema Express.
Acepta únicamente artefactos cuyo campo TURNO DE diga Verificador.

0. Comprueba que tu directorio de trabajo es el repositorio NexoExpress
   (debe existir docs/METODOLOGIA_TRIPLE_IA.md). Si no existe, DETENTE,
   responde exactamente "DETENIDO: directorio de trabajo incorrecto" y no
   escribas ningún archivo.
1. Lee {RUTA_SPEC}. El DoD que debes ejecutar es el de esa spec, y ninguno
   otro.
2. Lee {RUTA_INFORME}.
3. EJECUTA los comandos del DoD sobre el código real. Leer el informe no es
   verificar.
4. Contrasta la salida real contra la declarada en el informe y parsea el
   git diff literal.
5. Escribe tu verificación en {RUTA_SALIDA} con la salida LITERAL de cada
   comando. Si hay desviación o el DoD no es reproducible, recházalo.
6. Termina el archivo con esta línea exacta, con la fecha de hoy:
   — CIERRE {CICLO} / {MT} / AAAA-MM-DD
Si algo es ambiguo, DETENTE y escríbelo como duda en {RUTA_SALIDA}.
```

El bloque **no reproduce el DoD**: el Verificador lo lee de la spec
archivada. Ése sería el único sitio por donde el emisor podría recortar qué
se verifica.

## 2. Plantilla B-código genérica (Ingeniero, tareas mecánicas)

Mismos puntos 0 y 6; entre medias, el encargo **por ruta, nunca por
contenido pegado**:

```
Rol: {ROL} del ciclo {CICLO}, metodología v2.6 del ecosistema Express.
Confirma recepción sin accionar; acepta únicamente artefactos cuyo campo
TURNO DE diga {ROL}.

0. Comprueba que tu directorio de trabajo es el repositorio {REPO}
   (debe existir {ARCHIVO_CENTINELA}). Si no existe, DETENTE, responde
   exactamente "DETENIDO: directorio de trabajo incorrecto" y no escribas
   ningún archivo.
1. Lee {RUTA_ENCARGO} y ejecútalo.
2. Restricciones duras: {RESTRICCIONES}.
3. Escribe tu entrega en {RUTA_SALIDA}.
4. Si algo es ambiguo, DETENTE y devuélvelo como duda en {RUTA_SALIDA}; no
   lo resuelvas con un supuesto silencioso.
5. Termina el archivo con esta línea exacta, con la fecha de hoy:
   — CIERRE {CICLO} / {MT} / AAAA-MM-DD
```

## 3. Plantilla B-chat (Gemini: Auditor, Asesor, Guionista)

El receptor no tiene disco. La hoja de ruta se dirige al **Director**, y va
escrita dentro del bloque:

```
Rol: {ROL} del ciclo {CICLO}, metodología v2.6 del ecosistema Express.
Conversación NUEVA, sin herencia de ningún hilo previo.

[…contrato del rol: claims, trazas, trampas, y el git diff íntegro cuando
corresponda…]

FORMATO DE ENTREGA: responde con UN ÚNICO documento markdown completo,
listo para archivar sin edición. No lo trocees ni lo comentes fuera del
documento.
DESTINO: el Director lo guardará literal en {RUTA_SALIDA}.
Termina el documento con la línea:
   — CIERRE {CICLO} / {RONDA} / AAAA-MM-DD
```

Es el "flujo de una sola escritura" que `auditorias/README.md` describe
desde el 07-07-2026; la directriz sólo le añade el centinela y el nombre.

---

## 4. PO-1 — protocolo de la corrida, paso a paso

> **HALLAZGO PO-1.a (11-08, antes de la primera corrida).** El protocolo r1
> decía *"abre una terminal y arranca `claude`"*. **En esta máquina no hay
> CLI**: `claude: no se encontró la orden`. Se buscó en `~/.local/bin`,
> `~/.claude/local`, `~/bin`, `/usr/local/bin`, los `bin` de nvm
> (v22.16.0 y v24.15.0) y los `node_modules` globales — no existe. Claude
> Code corre aquí como **extensión nativa de VSCode**.
>
> Es un fallo del protocolo, no del mecanismo, y es exactamente lo que §3.1
> manda cazar: *"si el Director no puede ejecutarlo solo, no es una Parada
> de Observación válida"*. **Consecuencia vinculante para MT-T4:** la
> directriz debe decir **cómo se abre una sesión nueva en el entorno real
> del Director**, y no dar por supuesto un terminal con CLI. Un bloque
> `COPIAR` perfecto que empieza con un comando inexistente tiene fricción
> infinita, no cero.
>
> Decisión del Director (11-08): **se corre sin instalar nada**, por la
> interfaz. Protocolo r2 abajo.

### Corrida A/B-1 — camino feliz

1. Abre una **sesión nueva** de Claude Code **igual que abriste ésta**, con
   el repositorio NexoExpress como carpeta de trabajo. Lo único que importa:
   que **no comparta esta conversación**.
2. Pega el bloque de §5 **tal cual, sin editar ni añadir nada**.
3. No respondas a nada más. Cuando termine, vuelve aquí y dime "A/B-1 hecho".
   **No hace falta que copies nada**: la entrega va a disco y el Arquitecto
   la lee solo. Que sea así es parte de lo que se está probando.

**Pasa si:** aparece
`auditorias/2026-08-11_traspaso_y_trazabilidad/prueba_copiar_ok.md` con los
**10** campos del §0 y la línea centinela.
**Falla si:** tuviste que teclear o corregir algo · falta el centinela ·
faltan o sobran campos · aparece `TRAZABILIDAD`.

### Corrida A/B-2 — fail-closed (la que de verdad importa)

1. En VSCode: **Archivo → Nueva ventana**, y en esa ventana **Abrir
   carpeta → tu carpeta personal** (`/home/pueblac`).
2. Arranca ahí una sesión nueva de Claude Code. Su directorio de trabajo
   será `/home/pueblac`, no el repo.
3. Pega **el mismo bloque, sin cambiar una coma**.
4. Copia su respuesta literal y pégamela aquí. **Aquí sí hace falta que la
   copies**: si el bloque funciona, no habrá escrito ningún archivo, así que
   su respuesta es toda la evidencia que existe.

**Por qué la carpeta personal y no otra.** `/home/pueblac` **contiene** al
repo unos niveles más abajo. Es el escenario más exigente: el receptor
podría "ser útil" y buscar el archivo centinela hasta encontrarlo. Lo que se
prueba es que **no lo haga** — que se detenga porque su directorio de
trabajo no es el correcto, aunque el repo esté al alcance.

**Pasa si:** responde `DETENIDO: directorio de trabajo incorrecto` y **no
escribe ningún archivo**.
**Falla si:** escribe el archivo igualmente · se inventa la ruta · te
pregunta qué hacer en vez de detenerse.

> **Por qué A/B-2 es la corrida decisiva.** A/B-1 sólo prueba que la cosa
> funciona cuando todo va bien. A/B-2 prueba que falla **cerrado** (como un
> torniquete que se bloquea si se va la luz, en vez de quedarse abierto).
> Sin ella habríamos probado la mitad cómoda. Y aquí importa especialmente:
> este ecosistema es bi-máquina (Windows trabajo ↔ Linux casa), así que un
> bloque pegado en el sitio equivocado es un escenario real, no teórico.

---

## 5. BLOQUE A PEGAR — instancia de prueba de MT-T1

Inofensivo: sólo lee un documento y escribe un archivo nuevo dentro del
expediente. No toca producto, no borra nada.

```
Rol: Receptor de prueba del ciclo 2026-08-11_traspaso_y_trazabilidad,
metodología v2.6 del ecosistema Express.

0. Comprueba que tu directorio de trabajo es el repositorio NexoExpress
   (debe existir docs/METODOLOGIA_TRIPLE_IA.md). Si no existe, DETENTE,
   responde exactamente "DETENIDO: directorio de trabajo incorrecto" y no
   escribas ningún archivo.
1. Lee docs/METODOLOGIA_TRIPLE_IA.md, sección 5 (AVISO de traspaso).
2. Escribe en
   auditorias/2026-08-11_traspaso_y_trazabilidad/prueba_copiar_ok.md
   la lista literal de los nombres de campo del bloque AVISO, uno por línea,
   en el orden en que aparecen.
3. Termina el archivo con esta línea exacta, con la fecha de hoy:
   — CIERRE 2026-08-11_traspaso_y_trazabilidad / MT-T1 / AAAA-MM-DD
No hagas nada más. No modifiques ningún otro archivo.
```

---

━━ AVISO DE TRASPASO ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CICLO      : 2026-08-11_traspaso_y_trazabilidad
FASE       : F3/F4 de MT-T1 (colapso F1/F2 autorizado, §2 complejidad Baja)
TURNO DE   : Director
MODELO     : el bloque de §5 se pega en una sesión NUEVA de Claude Code;
             el modelo es indiferente — que sea indiferente forma parte de
             lo que se está probando
ENTREGAR   : auditorias/2026-08-11_traspaso_y_trazabilidad/plantilla_copiar.md
ADJUNTOS   : Ninguno — el bloque viaja dentro del propio documento
DESTINO    : dos sesiones nuevas: una DENTRO del repo (A/B-1) y otra FUERA
             (A/B-2), según el protocolo del §4
ACCIÓN     : ejecutar las dos corridas y volver con "A/B-1 hecho" y la
             respuesta literal de A/B-2
OBSERVABLE : PO-1 — verás aparecer en disco un archivo escrito por una IA a
             la que sólo le pegaste un bloque, y verás al mismo bloque
             negarse a escribir cuando se pega en el sitio equivocado
TRAZABILIDAD: sesión 970c3ab4 · claude-opus-5 · effort high [medido del
             transcript] · fase F3/F4 de MT-T1
VUELVE A   : Arquitecto, que verifica contra la respuesta fijada en §0 y
             archiva el resultado como cierre de MT-T1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
