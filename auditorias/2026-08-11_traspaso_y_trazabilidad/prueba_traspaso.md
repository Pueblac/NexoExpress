# Prueba del traspaso — bloques `COPIAR` y registro de trazabilidad real

**Ciclo:** `2026-08-11_traspaso_y_trazabilidad` · **Fase:** F1 (evidencia de diseño)
**Productor:** Arquitecto Macro — Claude Opus 5
**Pedido por el Director:** *"una prueba observable o un bloque de ejemplo
concreto"* de cómo se ve un bloque `COPIAR` de fricción cero y cómo luce el
registro de trazabilidad demostrando un salto de modelo.

> **Límite de esta pieza, declarado.** Los bloques de §1 son **plantillas de
> diseño**, y su prueba real es MT-T1 (la ejecutas tú). El registro de §2 se
> generó con una lectura ad-hoc del transcript, **no** con
> `scripts/analizar_sesion_ia.py`, que **todavía no existe**: escribirlo es
> F4 y le corresponde al Ingeniero (Sonnet). §7.2 prohíbe "Opus
> implementando", y esa regla no se salta ni para lucir una demo. Lo que
> sigue demuestra que **el dato existe y el formato funciona**, no que el
> script esté hecho.

---

## 1. Los bloques `COPIAR` (Ruta B)

### 1.1 Plantilla FIJA del Verificador — cinco huecos, prosa prohibida

Ésta es la salvaguarda central del diseño. El emisor **sólo rellena
`{CICLO}`, `{MT}`, `{RUTA_SPEC}`, `{RUTA_INFORME}` y `{RUTA_SALIDA}`**. Todo
lo demás es literal e invariable. Un bloque de verificación con una sola
frase añadida es **INVÁLIDO** y lo devuelves sin ejecutarlo.

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

**Por qué así.** El bloque **no reproduce el DoD** — el Verificador lo lee de
la spec archivada. Si el DoD se copiara aquí dentro, éste sería exactamente
el sitio por donde el emisor podría recortar lo que se verifica. Y como la
plantilla es siempre idéntica, tu control es comparar dos textos, no juzgar
si un encargo está sesgado: **es un control que puedes ejercer sin leer
código**.

### 1.2 Instancia rellena e inofensiva — el DoD de MT-T1

Esto es lo que pegarás en una sesión nueva para la Parada de Observación
**PO-1**. No toca producto, no borra nada, sólo lee y escribe un archivo
nuevo dentro del expediente:

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

**Las dos corridas del DoD:**

| | Dónde pegas el bloque | Qué debe pasar |
|---|---|---|
| **A/B-1** | Sesión nueva **abierta en el repo** | Aparece `prueba_copiar_ok.md` con los **10** campos y la línea centinela |
| **A/B-2** | Sesión nueva **abierta fuera del repo** | Responde `DETENIDO: directorio de trabajo incorrecto` y **no escribe nada** |

La corrida A/B-2 es la que importa: prueba que el bloque falla **cerrado**
(como un torniquete que se bloquea si se va la luz, en vez de quedarse
abierto). Sin esa corrida, sólo habríamos probado el camino feliz.

### 1.3 Variante B-chat — receptor que no puede escribir en disco

Gemini en el navegador (Auditor, Asesor, y el Guionista de Pre-F0) no tiene
acceso al disco. La hoja de ruta se dirige entonces **a ti**, y el bloque lo
dice dentro:

```
Rol: Auditor Externo Adversarial del ciclo {CICLO}, metodología v2.6 del
ecosistema Express. Conversación NUEVA, sin herencia de ningún hilo previo.

[…contrato de auditoría, claims, trazas y el git diff íntegro…]

FORMATO DE ENTREGA: responde con UN ÚNICO documento markdown completo,
listo para archivar sin edición. No lo trocees ni lo comentes fuera del
documento.
DESTINO: el Director lo guardará literal en
{RUTA_SALIDA}. Termina el documento con la línea:
   — CIERRE {CICLO} / {RONDA} / AAAA-MM-DD
```

Esto **no es nuevo**: es el "flujo de una sola escritura" que
`auditorias/README.md` describe desde el 07-07-2026. La directriz sólo le
añade el centinela y el nombre.

### 1.4 Regla anti-lectura-rancia

El emisor vuelve, lee `{RUTA_SALIDA}` y encuentra… el archivo del ciclo
anterior. Y cierra la fase creyendo que se ejecutó. Por eso el centinela:
**sin la línea de cierre con el ciclo y la MT correctos, el emisor rechaza
el archivo y DETIENE.** Determinista y barato.

---

## 2. El registro de trazabilidad — con datos reales

Formato propuesto para el campo `TRAZABILIDAD` del AVISO. **Todo lo que
sigue salió de transcripts reales de este proyecto**, hoy 11-08-2026:

```
┌─ TRAZABILIDAD DE SESIÓN ─ a0b9d1eb ─ rol declarado: arquitecto
│ MODELOS (medido)   : claude-sonnet-5 × 79 turnos, claude-opus-5 × 75 turnos
│ ⚠ DESVIACIÓN       : roster 'arquitecto' = ['claude-opus-5']; respondieron además ['claude-sonnet-5'] (51% de los turnos)
│ ESFUERZO (medido)  : {'high': 154}
│ TOKENS             : salida 368,178 · entrada+caché 24,991,058
│ SUBAGENTES         : 0
│ VENTANA            : 2026-08-07T11:17:42.183Z → 2026-08-11T10:43:48.015Z
│ RAMA / CLIENTE     : ['main'] / ['2.1.223']
└──────────────────────────────────────────────────────────────────

┌─ TRAZABILIDAD DE SESIÓN ─ caf731aa ─ rol declarado: arquitecto
│ MODELOS (medido)   : claude-fable-5 × 512 turnos, claude-opus-5 × 18 turnos
│ ⚠ DESVIACIÓN       : roster 'arquitecto' = ['claude-opus-5']; respondieron además ['claude-fable-5'] (97% de los turnos)
│ ESFUERZO (medido)  : {'high': 530}
│ TOKENS             : salida 906,955 · entrada+caché 161,974,718
│ SUBAGENTES         : 16 — modelos reales {'claude-sonnet-5': 509, 'claude-opus-5': 26}
│ VENTANA            : 2026-07-23T11:36:12.060Z → 2026-08-06T11:04:43.259Z
│ RAMA / CLIENTE     : ['main'] / ['2.1.218', '2.1.220', '2.1.223']
└──────────────────────────────────────────────────────────────────

┌─ TRAZABILIDAD DE SESIÓN ─ f50ba75a ─ rol declarado: ingeniero
│ MODELOS (medido)   : claude-sonnet-5 × 30 turnos
│ COTEJO ROSTER      : OK — coincide con ['claude-sonnet-5']
│ ESFUERZO           : no registrado en transcript → cae a settings/declarado
│ TOKENS             : salida 23,501 · entrada+caché 1,295,199
│ SUBAGENTES         : 0
│ VENTANA            : 2026-07-11T16:00:23.711Z → 2026-07-11T16:06:30.826Z
│ RAMA / CLIENTE     : ['main'] / ['2.1.204']
└──────────────────────────────────────────────────────────────────
```

### 2.1 El salto de modelo que pedías, en una sesión real

**`a0b9d1eb` es la prueba.** Una sesión declarada de Arquitecto en la que
**el 51% de los turnos los respondió Sonnet 5**, no Opus. No es una
hipótesis ni un ejemplo inventado: es una de tus sesiones de este mes, en
`main`. Con la disciplina actual eso es invisible — el AVISO habría dicho
`MODELO: Opus 5` y nadie habría tenido con qué desmentirlo.

Y `f50ba75a` demuestra el otro lado: un cotejo **OK** limpio, con el
esfuerzo rotulado honestamente como **no registrado** en vez de rellenado.

### 2.2 Tres hallazgos que sólo aparecen al renderizar el bloque

**F-1. El roster depende de la fecha.** `caf731aa` marca 97% de desviación
por `claude-fable-5`… y sin embargo **era correcta**: esa sesión es del
23-07 al 06-08, cuando Fable 5 era el Arquitecto legítimo. La sustitución
por Opus es del **10-08** (§10.7). Un cotejo contra el roster de hoy produce
**falsas desviaciones sobre todo el histórico**. → El `--rol` debe cotejar
contra el **roster vigente en la fecha de la sesión**, con la tabla de
vigencias en el propio script. Sin esto, la primera corrida sobre el archivo
histórico llenaría el expediente de alarmas falsas y el mecanismo perdería
credibilidad en su estreno.

**F-2. Una sesión no es una orden.** `a0b9d1eb` abarca del **07-08 al
11-08**: cuatro días y varias fases. Atribuir sus tokens a una micro-tarea
sería inventar. → El bloque `TRAZABILIDAD` debe declarar `CICLO`, `FASE` y
`MT`, y el script aceptar una ventana temporal. Es también lo que hará
respondible, dentro de unos ciclos, la pregunta de cuánto cuesta F0/F1 —
justo la premisa de la fase Pre-F0 (`diseno_f1.md` §8).

**F-3. El `effort` sí está aquí, y esto diverge del proyecto hermano.** La
directriz de `Coordinador_Indicadores_ImasD` declara un barrido con **cero
apariciones** de `effort` y lo trata como *declarado*, leyéndolo de
`settings.json`. En NexoExpress el campo **existe** por turno (`high` en 4
sesiones, `null` en 3), y `effortLevel` **no está en ningún settings** — ni
en el de este proyecto, ni en el del usuario, ni en el del hermano
(verificado hoy). De ahí la cadena de precedencia enmendada:
**medido → settings → declarado, rotulando siempre el origen.**

*Cautela que no se elimina:* que el campo se llame `effort` no prueba que
sea la misma palanca que §7.2 nombra. Se rotula como **medido del
transcript** y nada más; interpretarlo como "el `effort` de §7.2" es una
inferencia que aún no está probada.

---

━━ AVISO DE TRASPASO ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CICLO      : 2026-08-11_traspaso_y_trazabilidad
FASE       : F1 — Diseño (prueba de traspaso solicitada por el Director)
TURNO DE   : Arquitecto
MODELO     : Opus 5
ENTREGAR   : auditorias/2026-08-11_traspaso_y_trazabilidad/prueba_traspaso.md
ADJUNTOS   : Ninguno
DESTINO    : expediente del ciclo
ACCIÓN     : el Director lee §2.1 (el salto de modelo real) y conserva §1.2
             para ejecutarlo en PO-1
OBSERVABLE : el bloque de §1.2 es ya ejecutable — es la Parada PO-1
TRAZABILIDAD: sesión 970c3ab4 · claude-opus-5 · effort high [medido del
             transcript] · bloque generado por lectura ad-hoc, NO por
             scripts/analizar_sesion_ia.py (aún no existe — es F4)
VUELVE A   : Arquitecto, que incorpora F-1/F-2/F-3 al DoD de MT-T2 y MT-T3
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
