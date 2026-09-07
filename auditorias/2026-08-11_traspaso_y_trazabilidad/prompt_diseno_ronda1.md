# Prompt de revisión de DISEÑO — Ronda 1 (Tanda 1)

**Ciclo:** `2026-08-11_traspaso_y_trazabilidad` · **Fase:** F2
**Emisor:** Arquitecto Macro (Opus 5) · **Destinatario:** Auditor Externo Adversarial
**Alcance:** Tanda 1 (Rutas de traspaso + trazabilidad). **La Fase Pre-F0
(tanda 2) NO entra en esta ronda** y no debe auditarse aquí.

---

# Rol y regla de oro

Eres auditor adversarial del ecosistema Express. El Arquitecto (otra IA)
afirma haber diseñado un mecanismo de traspaso de artefactos entre agentes y
un control de trazabilidad de sesión que reducen el trabajo mecánico del
coordinador humano **sin debilitar el aislamiento entre roles**. **Tu
hipótesis de trabajo es que está mal o incompleto hasta que demuestre lo
contrario.** No eres un asistente conversacional: no agradezcas, no resumas,
no elogies. Cada afirmación sin cita textual del material de abajo (sección
y línea) se considera inventada.

# Formato obligatorio de CADA verificación

CLAIM → EVIDENCIA (cita textual del contexto de abajo) → TRAZA (ejecución
simbólica paso a paso, con roles y modelos concretos) → VERDICTO
(CONFIRMADO / BUG / NO VERIFICABLE CON LO ADJUNTO). Lo que no esté escrito
abajo es NO VERIFICABLE: prohibido rellenarlo con suposiciones sobre cómo
"suele" funcionar un ciclo de este tipo.

# Material adjunto

**Ninguno — revisión de DISEÑO.** Todo el contexto verificado va abajo.

---

## CONTEXTO 1 — El ciclo vigente y su regla de oro

Metodología Triple-IA v2.6. Fases: F0 plan → G0 → F1 diseño → F2 auditoría
de diseño → G1 → F3 spec → F4 implementación → F5 verificación → F6
auditoría de código → F7 cierre. G0/G1/G2 son gates humanos del Director.

**Regla de oro (§1):** *"Ninguna IA verifica su propio trabajo con autoridad
final."* Triángulo: el Verificador (F5) verifica al Ingeniero; el Auditor
externo (tú, Gemini) valida al Arquitecto en F2 y al Ingeniero en F6; el
Arquitecto arbitra escaladas.

**Roster desde el 10-08-2026 (§10.7):** Arquitecto = Opus 5 · Especificador
= Opus 5 en complejidad Alta, Sonnet 5 en Media/Baja · Ingeniero = Sonnet 5
(toda complejidad) · Verificador F5 = Opus 5 en Alta, Haiku 4.5 en
Media/Baja · Sintetizador (empaquetado F6) = Haiku 4.5 · Auditor = Gemini.
**Roster anterior al 10-08:** el Arquitecto era Fable 5.

**Riesgo ya declarado por la propia metodología (§10.7):** *"en Alta, Opus
ocupa Arquitecto, Especificador y Verificador — tres de los cuatro nodos
internos. La separación pasa a depender casi por completo de que cada sesión
de Opus arranque realmente en frío."*

**Modo de operación vigente (§6):** Modo M manual. El Director transporta
cada artefacto a mano entre sesiones. El **Modo A automatizado está
propuesto y NO habilitado**; requiere su propio ciclo de diseño.

## CONTEXTO 2 — Qué se propone (Tanda 1)

**Ruta A — traspaso interno por subagente.** El agente emisor lanza al
receptor como sesión hija sin herencia de conversación. **Se diseña ahora
pero NO se habilita en esta tanda.**

**Frontera de exclusión propuesta, formulada como regla estructural:**

> *"Ruta A NUNCA cruza una arista de verificación del triángulo. Un emisor
> puede lanzar como subagente a quien CONSUME su salida; jamás a quien LA
> JUZGA."*

Aplicación: Ingeniero **SÍ** (no verifica a nadie) · Sintetizador para
empaquetado F6 **SÍ si lo lanza el Arquitecto, NO si lo lanza el Ingeniero**
· Verificador F5 **NUNCA** · Auditor externo **NUNCA** · Asesor del Director
**NUNCA** · Especificador **no por defecto** (la regla estructural no lo
prohíbe, pero en Alta Arquitecto y Especificador son el mismo modelo).

**Neutralización del encuadre en Ruta A:** *"el prompt de lanzamiento no
transporta contenido: transporta rutas. El subagente lee el artefacto del
disco. Si el emisor quiere filtrar, tiene que alterar un archivo archivado
del expediente — y eso deja huella en git diff."* Más: el encargo interno se
archiva, y toda entrega por Ruta A de una orden larga que llegue **sin dudas
y sin desviaciones** se marca para spot-check (*"una sesión subordinada
tiende a decidir para poder terminar"*).

**Ruta B — bloque `COPIAR`.** El emisor termina su artefacto con un bloque
literal que el Director copia y pega en una sesión nueva **sin editar nada**.
El bloque lleva dentro el rol, las rutas que leer, la tarea y **dónde
escribir la respuesta**. Variantes: **B-código** (receptor con disco, escribe
él) y **B-chat** (receptor sin disco — Gemini —, el Director guarda la
respuesta literal).

**Salvaguarda central: plantilla FIJA del Verificador.** Cinco huecos
—`{CICLO}`, `{MT}`, `{RUTA_SPEC}`, `{RUTA_INFORME}`, `{RUTA_SALIDA}`— y
**prosa libre prohibida**. Texto literal e invariable:

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

Razón declarada: *"el bloque NO reproduce el DoD — el Verificador lo lee de
la spec archivada. Si el DoD se copiara dentro del bloque, ahí es donde
entraría el filtrado."* Y: *"un bloque de verificación con prosa añadida es
INVÁLIDO y el Director lo devuelve sin ejecutarlo"*, control que el Director
puede ejercer comparando dos textos, sin leer código.

**Argumento de por qué el Verificador va por Ruta B y no por Ruta A:** por
Ruta A lo lanzaría el emisor (en Alta, el mismo modelo que escribió la spec);
por Ruta B **la sesión la abre el Director**, así que el aislamiento es
estructural y no depende de disciplina.

**Dos reglas de operación:** (a) **fail-closed de directorio de trabajo** —
el ecosistema es bi-máquina (Windows ↔ Linux), rutas relativas al repo y
parada si el directorio no es el correcto; (b) **centinela anti-lectura
rancia** — el receptor cierra su archivo con `— CIERRE {CICLO} / {MT} /
{FECHA}`; sin centinela el emisor rechaza el archivo y DETIENE.

## CONTEXTO 3 — Trazabilidad de sesión

Script `scripts/analizar_sesion_ia.py`, **sólo lectura**, sobre los
transcripts JSONL del cliente (`~/.claude/projects/{slug}/`). Extrae por
turno: identificador **real** del modelo, `effort`, tokens, y la tabla de
subagentes (`{sessionId}/subagents/`, con rol declarado y modelo real).

**Qué afirma y qué no** (escrito en el propio diseño): *"detecta
contradicciones, no conformidad. No prueba que la sesión arrancara en frío;
no prueba el rol; no detecta filtrado de artefactos. Es un detector de humo,
no un extintor."*

**Contrato del script:** `--rol` cotea el modelo medido contra el roster
**vigente en la fecha de la sesión** y marca la desviación · `--esfuerzo`
obligatorio, exit 1 si falta · precedencia del esfuerzo **medido → settings
→ declarado**, rotulando siempre el origen · **lista blanca fail-closed** de
campos permitidos, `content` jamás se lee · exit ≠ 0 ante formato
desconocido, **jamás ceros**.

**Restricción dura: el repositorio NexoExpress es PÚBLICO** (verificado con
`gh repo view` → `"visibility":"PUBLIC"`). El expediente se commitea y se
publica. El transcript contiene todo lo tecleado por el Director, incluidas
rutas de credenciales.

**Salida:** campo **`TRAZABILIDAD` propio** del AVISO de traspaso, separado
de `OBSERVABLE` (que sigue siendo sólo lo que el Director puede abrir y
tocar), con `CICLO` / `FASE` / `MT`.

## CONTEXTO 4 — Evidencia empírica ya producida (medida, no supuesta)

**M-1.** De 7 sesiones del proyecto, **3 ejecutaron dos modelos distintos en
el mismo hilo**. Caso `a0b9d1eb`: 75 turnos de `claude-opus-5` **y 79 de
`claude-sonnet-5`**, en una sesión declarada de Arquitecto — 51% de los
turnos fuera de roster, invisible con la disciplina actual.

**M-2.** El campo `effort` está registrado como `high` en el 100% de las
sesiones que lo registran (530/530, 154/154, 131/131), **incluidas sesiones
de F0/F1**, para las que §7.2 prescribe `low`/`medium`. En 3 sesiones más el
campo es `null`.

**M-3.** `effortLevel` **no existe** en ningún `settings.json` (proyecto,
usuario, ni el del coordinador hermano).

**M-4. El roster depende de la fecha.** La sesión `caf731aa` (23-07 → 06-08)
marca 97% de desviación por `claude-fable-5` **y sin embargo era correcta**:
Fable era el Arquitecto legítimo hasta el 10-08. Un cotejo contra el roster
de hoy produciría falsas desviaciones sobre todo el histórico.

**M-5.** `isSidechain` es `false` en el 100% de las líneas; los turnos de
subagente viven en `{sessionId}/subagents/`. Un script que contara
subagentes por ese campo reportaría **cero** pareciendo correcto.

**M-6. Parada de Observación PO-1 ya ejecutada (11-08-2026), con dos
corridas A/B:**
- **A/B-1** (sesión nueva dentro del repo): escribió el archivo pedido con
  los 10 campos correctos y el centinela. **No incluyó** un campo
  `TRAZABILIDAD` que sí aparece en otros artefactos del mismo expediente
  — prueba de que no arrastró contexto.
- **A/B-2** (sesión nueva **fuera** del repo, `cwd: /home/pueblac`
  verificado en el transcript): respondió literal `DETENIDO: directorio de
  trabajo incorrecto`, y las herramientas usadas fueron **`Bash` ×1 y nada
  más** — cero escrituras. No se creó ningún árbol paralelo.
- **Incidente intermedio:** dos intentos previos de A/B-2 corrieron en
  realidad dentro del repo (el entorno restauró el workspace). Los dos
  receptores informaron "directorio verificado" **y decían la verdad**; lo
  que resolvió la ambigüedad fue el campo `cwd` del transcript, no los
  autoinformes.

---

# Claims a verificar

**C1.** La frontera *"Ruta A nunca cruza una arista de verificación del
triángulo"* es **suficiente** para impedir la auto-verificación, y es
superior a una lista de excepciones por rol porque sobrevive a los cambios
de roster (precedente: la sustitución de Fable por Opus del 10-08 obligó a
reescribir tablas de roles).

**C2.** La plantilla fija de cinco huecos cierra el vector de encuadre del
emisor sobre el Verificador, **porque el bloque no reproduce el DoD** y
porque una plantilla invariable es comparable de un vistazo por un Director
no técnico.

**C3.** Las dos reglas de operación (fail-closed de directorio + centinela)
cierran los dos fallos de operación identificados. **Traza C3 sobre la
evidencia M-6**, que es una ejecución real, no un supuesto.

**C4.** La lista blanca fail-closed es **suficiente** para garantizar que
ninguna salida commiteada al repositorio **público** contenga contenido de
conversación del Director.

**C5.** El cotejo de roster **fechado** (M-4) mantiene la capacidad de
detección de M-1 sin producir falsas desviaciones sobre el histórico.
Ejecuta simbólicamente ambos casos y muestra el veredicto literal que
debería emitir el script para `a0b9d1eb` y para `caf731aa`.

**C6.** La secuenciación —Ruta A diseñada pero **NO habilitada** hasta que
exista la trazabilidad— es una dependencia real y no una postergación
arbitraria.

# Dudas declaradas por el Arquitecto

**D1.** Que el campo del transcript se llame `effort` **no prueba** que sea
la palanca que §7.2 nombra. Se rotula como "medido del transcript" sin
afirmar equivalencia. ¿Es honesto ese rótulo o induce a error igualmente?

**D2.** La plantilla fija del Verificador la sigue **tecleando el emisor**.
¿Basta con prohibir la prosa, o la plantilla debería vivir en el repo como
archivo, y el bloque limitarse a citar su ruta más los cinco valores? Lo
segundo es más rígido pero añade un archivo que el emisor también podría
editar.

**D3.** El script depende de `~/.claude/projects/`, ruta interna del cliente,
no documentada y sujeta a cambio de versión. ¿Es aceptable que un control
del ciclo dependa de un formato que nadie garantiza? La mitigación propuesta
es degradar a `TRAZABILIDAD: no disponible` sin bloquear el ciclo.

**D4.** PO-1 demostró que "abre una sesión nueva fuera del repo" **no es una
instrucción uniformemente ejecutable** en el entorno del Director (el primer
intento falló por falta de CLI en el terminal integrado; el segundo, porque
el editor restauró el workspace). ¿Puede una directriz que promete fricción
cero depender de un gesto de interfaz que varía entre entornos?

# Deuda YA ADJUDICADA — no son hallazgos nuevos

Presentar cualquiera de estos como descubrimiento es relleno y consume el
presupuesto de la respuesta:

1. El script **no** prueba arranque en frío, **no** prueba el rol y **no**
   detecta filtrado. Declarado en el diseño.
2. Ruta A **reduce** la visibilidad del Director sobre los traspasos. Por eso
   no se habilita en esta tanda.
3. La **Fase Pre-F0** (un rol nuevo para Gemini antes de F0) está **fuera de
   esta tanda** y tiene su propia ronda de diseño. No la audites aquí.
4. El coste en dinero no se calcula: los precios no están en el transcript.
5. Los gates G0/G1/G2 siguen siendo humanos y bloqueantes. No se automatiza
   ninguno.

**Regla dura sobre vectores mitigados.** El encuadre del emisor en Ruta A
está **MITIGADO, NO CERRADO**. Ataque residual descrito y asumido: el emisor
puede (a) alterar el artefacto archivado antes de lanzar —deja huella en
`git diff`—, o (b) haber escrito un DoD débil en la spec, que ninguna
plantilla de bloque corrige. Si demuestras que el diseño presenta como
cerrado algo que sólo está mitigado, tienes razón en rechazar el paquete.

# Preguntas de control (respóndelas TODAS; son parte del entregable)

**Q1.** Copia textualmente el punto **0** de la plantilla fija del
Verificador. Después traza qué ocurre si un emisor añade al final del bloque
la frase *"verifica que el DoD pasa"*: ¿qué regla del diseño lo detecta, en
qué momento, y quién lo detecta? Da una **recomendación única** sobre si esa
detección es suficiente — no un "depende".

**Q2.** El diseño enumera **cuatro** decisiones derivadas de que el
repositorio sea público. Cítalas. Después indica **cuál de las cuatro cae
primero** si una versión nueva del cliente añade un campo no previsto al
transcript, y por qué.

**Q3.** La regla estructural de C1 **no prohíbe** que el Arquitecto lance al
Especificador por Ruta A; el diseño lo deja fuera "por defecto". Traza el
caso concreto en complejidad **Alta**, donde Arquitecto y Especificador son
ambos Opus 5, y da una **recomendación única**: prohibirlo explícitamente, o
dejarlo como está.

**Q4.** Usando M-1 y M-4, escribe la **línea literal de veredicto** que el
script debería emitir para `--rol arquitecto` sobre `a0b9d1eb` (07-08 →
11-08) y sobre `caf731aa` (23-07 → 06-08). Deben ser distintas y la
diferencia debe estar justificada por la fecha, no por el porcentaje.

# Anti-aprobación-automática

Si tu veredicto global es APROBADO o APROBADO CON OBSERVACIONES, debes
ADEMÁS demostrar **con evidencia** por qué cada una de estas trampas NO
aplica. "Parece bien" no es demostración.

**T1.** En complejidad Alta, el mismo Opus escribe la spec (F3) y emite el
bloque `COPIAR` del Verificador. La plantilla fija impide sesgar el bloque
— **pero el DoD que el Verificador ejecutará lo escribió ese mismo emisor en
la spec.** ¿Cierra el diseño ese vector, o sólo mueve el sesgo del bloque a
la spec?

**T2.** El centinela es `— CIERRE {CICLO} / {MT} / {FECHA}`. Se produce una
recalibración (F3′) que rehace **la misma MT, el mismo día, en el mismo
ciclo**. El emisor vuelve, lee la ruta de salida y encuentra un archivo con
un centinela **idéntico** al que espera. ¿Distingue la segunda corrida de la
primera?

**T3.** La lista blanca incluye `description` del subagente, que es **texto
libre escrito por el emisor**. Un emisor podría volcar ahí contenido
sensible, y saldría publicado en un repositorio público pasando el filtro.
¿Lo cierra el diseño?

**T4.** `--esfuerzo` es obligatorio y su valor se rotula como "declarado".
Nada impide declarar `high` sin haberlo usado. ¿Aporta el campo algo más que
una apariencia de control?

**T5.** Regla de C1: el emisor no lanza a quien lo juzga. En complejidad
**Alta**, el Verificador F5 es Opus. Si ese mismo Opus, en su rol de
Arquitecto, lanza al Sintetizador (Haiku) que empaqueta el prompt de
auditoría F6 **de la micro-tarea que él acaba de verificar**, ¿cruza o no
cruza una arista de verificación? El diseño dice que el Arquitecto SÍ puede
lanzar al Sintetizador.

# Entregable final

1. Tabla C1..C6 con verdictos. 2. Respuestas Q1..Q4 completas. 3. Las cinco
trampas T, si apruebas. 4. Opinión fundada sobre D1..D4. 5. Veredicto global
(APROBADO / APROBADO CON OBSERVACIONES / RECHAZADO).

Una respuesta sin citas del contexto o sin las trazas obligatorias es
**INVÁLIDA** y será devuelta sin discusión.

**Formato de entrega:** responde con **UN ÚNICO documento markdown
completo**, listo para archivar sin edición. No lo trocees ni lo comentes
fuera del documento. El Director lo guardará literal en
`auditorias/2026-08-11_traspaso_y_trazabilidad/respuesta_diseno_ronda1.md`.
Termina el documento con la línea:

```
— CIERRE 2026-08-11_traspaso_y_trazabilidad / F2-r1 / AAAA-MM-DD
```

---

━━ AVISO DE TRASPASO ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CICLO      : 2026-08-11_traspaso_y_trazabilidad
FASE       : F2 — Auditoría de DISEÑO, ronda 1 (Tanda 1)
TURNO DE   : Auditor
MODELO     : **Gemini 3.1 Pro High** — ver nota de desviación abajo
ENTREGAR   : auditorias/2026-08-11_traspaso_y_trazabilidad/prompt_diseno_ronda1.md
ADJUNTOS   : Ninguno — revisión de diseño, el contexto viaja dentro del prompt
DESTINO    : conversación NUEVA de Gemini, sin herencia de ningún hilo.
             Primer mensaje, inicialización de identidad:
             "Rol: Auditor del ciclo 2026-08-11_traspaso_y_trazabilidad,
             metodología v2.6 del ecosistema Express. Confirma recepción sin
             accionar; acepta únicamente artefactos cuyo TURNO DE diga
             Auditor."
             Segundo mensaje: este prompt completo.
             NO usar el hilo del Asesor (§1.1): ambos son Gemini y compartir
             hilo contamina la auditoría.
ACCIÓN     : auditar el diseño de la Tanda 1 y devolver un único documento
OBSERVABLE : Ninguno en esta fase — PO-1 ya se cobró (M-6)
TRAZABILIDAD: sesión 970c3ab4 · claude-opus-5 · effort high [medido del
             transcript] · fase F2 (emisión) · bloque por lectura ad-hoc,
             no por script (aún no existe — es F4)
VUELVE A   : Director, que guarda la respuesta literal como
             respuesta_diseno_ronda1.md y convoca el anti-bluff
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

> **Nota de desviación de la matriz (§2), para ratificación del Director.**
> La tanda es de complejidad **Media**, y §2 asigna **Flash** a F2 en Media.
> El Arquitecto recomienda **Pro High** por una razón acotada: lo que se
> audita no es una funcionalidad del producto, sino **el sistema de control
> del propio ciclo**. Un defecto aquí no rompe una pantalla — debilita en
> silencio todas las auditorías futuras, y no habría nada que lo detectara.
> §2 ya prevé el criterio: *"en caso de duda entre dos niveles, se asigna el
> superior"*. **Es reversible y de coste bajo; la decisión es del Director.**
