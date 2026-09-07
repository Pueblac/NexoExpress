# Prompt de revisión de DISEÑO — Ronda 1 (Tanda 1) — reemisión bajo metodología v3.0

**Ciclo:** `2026-08-11_traspaso_y_trazabilidad` · **Fase:** F2 · **Revisión del paquete:** r3 (06-09-2026)
**Emisor:** Arquitecto Macro (Claude Fable 5.1 High) · **Destinatario:** Auditor Externo Adversarial (Gemini 3.1 Pro High)
**Alcance:** Tanda 1 (Rutas de traspaso + trazabilidad). **La Fase Pre-F0 (tanda 2) NO entra
en esta ronda** y no debe auditarse aquí.
**Sustituye a:** `prompt_diseno_ronda1.md` (11-08, v2.6), que **nunca llegó al Auditor** y se
conserva en el expediente como registro; su desfase está cotejado en `desfase_v3_para_f1r3.md`.
**Diseño auditado:** `diseno_f1.md` §0–§8 (r2, aprobado en G0) **+ §9** (r3, actualización a v3.0;
donde §9 contradice a §0–§8, prevalece §9). Todo lo que necesitas está copiado abajo: **no tienes
disco** y no debes suponer nada que no esté en este documento.

---

# Rol y regla de oro

Eres auditor adversarial del ecosistema Express. El Arquitecto (otra IA, de otro proveedor)
afirma haber diseñado un mecanismo de traspaso de artefactos entre agentes y un control de
trazabilidad de sesión que reducen el trabajo mecánico del coordinador humano **sin debilitar el
aislamiento entre roles**. **Tu hipótesis de trabajo es que está mal o incompleto hasta que
demuestre lo contrario.** No eres un asistente conversacional: no agradezcas, no resumas, no
elogies. Cada afirmación sin cita textual del material de abajo (sección y línea) se considera
inventada.

# Formato obligatorio de CADA verificación

CLAIM → EVIDENCIA (cita textual del contexto de abajo) → TRAZA (ejecución simbólica paso a paso,
con roles y modelos concretos) → VERDICTO (CONFIRMADO / BUG / NO VERIFICABLE CON LO ADJUNTO). Lo
que no esté escrito abajo es NO VERIFICABLE: prohibido rellenarlo con suposiciones sobre cómo
"suele" funcionar un ciclo de este tipo.

# Material adjunto

**Ninguno — revisión de DISEÑO.** Todo el contexto verificado va abajo. Las citas
`archivo:línea` fueron comprobadas con `grep -n` sobre el disco el 06-09-2026; si una cita no
cuadra con lo que se transcribe, decláralo como hallazgo.

---

## CONTEXTO 1 — El ciclo vigente (v3.0, adoptada el 06-09-2026) y su regla de oro

Metodología Triple-IA **v3.0** (`docs/METODOLOGIA_TRIPLE_IA.md`, §10.8, adoptada 06-09-2026 por
orden del Director). Fases: F0 plan → G0 → F1 diseño → F2 auditoría de diseño → G1 → F3 spec →
F4 implementación → F5 verificación → F6 auditoría de código → F7 cierre. G0/G0′/G1/G2 son gates
humanos del Director y no se automatizan.

**Regla de oro** (`docs/METODOLOGIA_TRIPLE_IA.md:92`): *"Ninguna IA verifica su propio trabajo
con autoridad final."* Triángulo: el Verificador (F5) verifica al Ingeniero; el Auditor externo
(tú, Gemini) valida al Arquitecto en F2 y al Ingeniero/Especificador en F6; el Arquitecto arbitra
escaladas.

**Roster v3.0 — fijo, 1 modelo y 1 esfuerzo por rol, sin bifurcación por complejidad**
(`docs/METODOLOGIA_TRIPLE_IA.md:38-42` y `:135-141`):
Arquitecto = **Claude Fable 5.1** `high` (`:38`) · Especificador = **Claude Opus 5** `high`
(`:39`) · Ingeniero = **Claude Sonnet 5** `high` (`:40`) · Verificador = **Claude Opus 5**
`high`, *"Sesión NUEVA en frío obligatoria por Ruta B"* (`:41`) · Auditor = **Gemini 3.1 Pro**
`high` en F2 **y** F6, toda complejidad (`:42`, `:136`) · Asesor del Director = **Gemini 3.8
Flash** `high`, conversación separada del Auditor (`:37`). **El Sintetizador (Haiku 4.5) no
figura en el roster** (`:32-45`, `:133-141`).

**Riesgo declarado por la metodología, en su forma v3.0:** Opus 5 ocupa **dos** de los cuatro
nodos internos — Especificador (F3) y Verificador (F5) — mientras el Arquitecto es otro modelo.
La separación Especificador/Verificador depende de que la sesión del Verificador arranque de
verdad en frío, y la v3.0 lo fija estructuralmente: *"Sesión NUEVA en frío obligatoria por Ruta B.
NUNCA Ruta A"* (`:501`; también `coordinador.json:88-89`: *"NUNCA ruta A, sin excepción: en la
ruta interna el emisor escribe el prompt del receptor, y decidir qué se verifica es la mitad de
verificar"*).

**Modo de operación vigente (§6 v3.0, `:462-503`).** *"En v3.0 se elimina la redacción o copia
manual de prompts de arranque en frío. Todo arranque se genera de forma mecánica y determinista
mediante el script central"* `scripts/emitir_arranque.py` (`:466`), que lee `coordinador.json`
y `.claude/settings.json`, resuelve **rutas absolutas**, aborta con `exit 1` si un rol exige
`--insumo` y falta o no existe (`:482`), y *"escribe el bloque listo para el portapapeles en
`bloques/bloque_<rol>.txt` (ignorado por git)"* (`:483`). El insumo viaja como ruta, no como
contenido (`scripts/emitir_arranque.py:95-108`: *"El insumo viaja como RUTA ABSOLUTA, no volcado
dentro del prompt"*). El Director sigue siendo *"el custodio de los gates y transporta los
bloques emitidos"* (`:497`). Sobre Ruta A y B dice, literal:
- `:500` — *"Ingeniero (Claude Sonnet 5 High): Ejecuta la implementación. Admite **Ruta A**
  (subagente asistido lanzado por el Especificador) o **Ruta B** (sesión nueva abierta por el
  Director)."*
- `:501` — *"Verificador (Claude Opus 5 High): Sesión NUEVA en frío obligatoria por **Ruta B**.
  NUNCA Ruta A."*
- `:502` — *"Auditor (Gemini 3.1 Pro High): Conversación NUEVA en Gemini, cross-vendor, sin
  herencia de contexto."*
- `coordinador.json:142` — *"Arquitecto/Especificador -> Ingeniero admite Ruta A (subagente
  asistido). El Verificador y el Auditor NUNCA admiten Ruta A."*
- `coordinador.json:125` — *"Los arranques se emiten mecánicamente con scripts/emitir_arranque.py
  y los autoriza el Director."* Y `docs/PROMPT_ARRANQUE_SESION.md:42` encarga al **Arquitecto**
  emitir los arranques de Especificador, Ingeniero, Verificador y Auditor con ese script.
- El término *"rotación asistida"* de la v2.6 **ya no existe** en el documento (`grep` sin
  resultados).

**Guardrails mecánicos v3.0 (`:485-493`):** sello `[ROL · MODELO · turno N]` en toda respuesta;
negaciones por artefacto y ruta física; nombrar la regla violada antes de corregir; evidencia
literal no reformateada (`comando | tee archivo`); hook git `commit-msg` anti-huellas.

**Roster histórico del Arquitecto, necesario para el cotejo fechado (E1):** Fable 5 hasta la
sustitución del 10-08-2026 (`:673-719`, §10.7: *"Sustitución de modelo — Fable 5 fuera del roster
(10-08-2026)"*, Arquitecto → Opus 5); Opus 5 del 10-08 al 05-09; **Fable 5.1** desde el 06-09
(`:721-733`, §10.8). Los identificadores reales en transcript son distintos: `claude-fable-5`
(julio-agosto) y `claude-fable-5-1` (desde 06-09) — medido, ver M-8.

**Deuda interna de la v3.0, ya adjudicada al Director (no la audites como hallazgo):** las
tablas fijan Verificador = Opus 5 sin bifurcación (`:41`, `:139`), pero el cuerpo conserva texto
v2.6 que asigna F5 en Media/Baja al *"Sintetizador (Haiku 4.5)"* (`:94-96`, `:162-167`,
`:221-223`); el empaquetado de F6 sigue atribuido al Sintetizador (`:233`); la plantilla del
AVISO enumera *"Sintetizador"* y no lista a Fable 5.1 ni a Gemini 3.8 Flash (`:444-447`); la
tabla de artefactos dice que F5 es *"anexo en informe_mtNN.md"* (`:347`). Quién empaqueta F6 y
quién hace el anti-bluff formal es una corrección de documentación del Director.

## CONTEXTO 2 — Qué se propone (Tanda 1), revisión r3

**Ruta A — traspaso interno por subagente.** El agente emisor lanza al receptor como sesión hija
sin herencia de conversación. **Estado tras la v3.0:** *admitida* para la arista
Arquitecto/Especificador → Ingeniero (`:500`, `coordinador.json:71` y `:142`), pero **sin
mecanismo** (el emisor CLI sólo produce bloques `COPIAR`, es decir, Ruta B) y **sin instrumento**
que la audite a posteriori (el script de trazabilidad es F4). El diseño r2 la dejaba fuera de la
tanda (D1); el r3 la acepta como la deja la v3.0 y **le impone condiciones de uso** que no
dependen del script (`diseno_f1.md` §9.1):

1. *"El encargo se archiva en el expediente ANTES de lanzar el subagente, y el prompt de
   lanzamiento transporta rutas, no contenido."* Neutralización del encuadre del emisor: *"Si el
   emisor quiere filtrar, tiene que alterar un archivo archivado del expediente — y eso deja
   huella en git diff"* (`diseno_f1.md` §3.3).
2. **E4:** *"Toda entrega por Ruta A de una orden larga que llegue sin dudas y sin desviaciones se
   marca para spot-check del Director. No se rechaza; se mira"* (§3.4-bis).
3. **Frontera estructural, ampliada en r3:** *"Ruta A NUNCA cruza una arista de verificación del
   triángulo. Un emisor puede lanzar como subagente a quien CONSUME su salida; jamás a quien LA
   JUZGA"* (§3.4) — **y no sustituye un gate humano**: *"el receptor sólo se lanza cuando el
   artefacto que consume ya está archivado y el gate previo (G1) concedido"* (§9.1.3). Aplicado:
   el Arquitecto puede lanzar al Ingeniero **sólo** con la spec de F3 ya en el expediente, nunca
   desde F1 saltándose G1 y F3.
4. El archivo del **primer mensaje de usuario de cada subagente**, extraído del transcript
   (§3.5), queda **diferido a MT-T3**. Hasta entonces la Ruta A es *"admitida, no instrumentada"*,
   y el anexo lo dice con esas palabras.

**Aplicación de la frontera a los roles v3.0** (`diseno_f1.md` §3.4 corregida por §9.5):
Ingeniero **SÍ** (lanzado por Arquitecto o Especificador, con la condición 3) · Verificador
**NUNCA** (concuerda con `:501`) · Auditor **NUNCA** · Asesor **NUNCA** · Especificador **NO por
defecto** (la regla no lo prohíbe: consume el diseño; pero entre F1 y F3 está **G1**, y la
condición 3 impide cruzar un gate; además en r2 la razón era "mismo modelo en Alta", que en v3.0
ya no aplica: Arquitecto = Fable 5.1, Especificador = Opus 5) · **Empaquetador de F6: rol sin
asignar en v3.0**; sea quien sea, *"jamás lo lanza el Ingeniero y el git diff viaja íntegro"*.

**Ruta B — bloque `COPIAR`.** Bajo la v3.0, **el emisor CLI es la Ruta B mecanizada**: el bloque
lo genera `emitir_arranque.py` desde una plantilla fija por rol (`docs/prompts_arranque/*.md`),
el Director abre la sesión nueva y pega `bloques/bloque_<rol>.txt` sin editar. Variantes:
**B-código** (receptor con disco: Especificador, Ingeniero, Verificador) y **B-chat** (receptor
sin disco: Auditor, Asesor). Regla de operación r3 para B-chat (`diseno_f1.md` §9.6): como el
insumo va como **ruta absoluta** (`emitir_arranque.py:95-108`) y Gemini no puede leerla, el
Director envía **dos mensajes**: (1) el bloque emitido — identidad del rol —, (2) el **contenido
íntegro** del archivo insumo. Es el *"flujo de una sola escritura"* de `auditorias/README.md`
(07-07-2026) con el centinela añadido.

**Salvaguarda central: plantilla del Verificador — una sola, y fija.** Existían dos: la de
cinco huecos validada en PO-1 (`plantilla_copiar.md` §1, r2) y la del CLI
(`docs/prompts_arranque/verificador.md`, v3.0). El r3 **se queda con la del CLI** (porque `:466`
manda emisión mecánica) y **le porta** lo que PO-1 demostró (`diseno_f1.md` §9.4):

1. **Punto 0 fail-closed de directorio:** *"Comprueba que tu directorio de trabajo es el
   repositorio NexoExpress (debe existir docs/METODOLOGIA_TRIPLE_IA.md). Si no existe, DETENTE,
   responde exactamente "DETENIDO: directorio de trabajo incorrecto" y no escribas ningún
   archivo."* Las rutas absolutas del CLI **no** lo sustituyen: una sesión abierta fuera del repo
   escribiría igualmente en la ruta absoluta.
2. **Centinela y nombre fijo:** el Verificador escribe `verificacion_mtNN.md` en el expediente y
   termina con `— CIERRE {CICLO} / {MT} / AAAA-MM-DD`; sin centinela, el emisor rechaza el
   archivo y DETIENE (anti-lectura-rancia).
3. **Prosa prohibida en el bloque emitido:** para el Verificador, `{{TAREA}}` es literalmente
   `Verificar MT-NN del ciclo {CICLO}` y `{{INSUMO}}` es la ruta del informe (que cita la spec).
   *"Cualquier otra frase en `bloques/bloque_verificador.txt` lo hace INVÁLIDO y el Director lo
   devuelve sin pegarlo."* El bloque **no reproduce el DoD**: el Verificador lo lee de la spec.

La plantilla del CLI dice, literal (`docs/prompts_arranque/verificador.md:39-40`): *"**Tú
decides qué se verifica.** Nadie te entrega la lista cerrada: los criterios de aceptación de la
orden son el **mínimo**, no el techo."* El r3 **adopta** esa filosofía sobre el *"el DoD que debes
ejecutar es el de esa spec, y ninguno otro"* de r2: el bloque no puede *quitar* comprobaciones,
el Verificador puede *añadir*. Extractos literales de la plantilla vigente: `:73` `{{INSUMO}}`
bajo *"# La entrega que verificas"*; `:77` `{{TAREA}}` bajo *"# Tarea"*; `:81` *"En
{{DIR_ARTEFACTO}}, registrando la salida literal de cada comprobación que ejecutaste"*; `:3`
*"NUNCA por Ruta A, sin excepción"*.

**Riesgo residual declarado (no cerrado):** `{{TAREA}}` es texto libre en el código
(`emitir_arranque.py:159-160`) y quien lo teclea es el Arquitecto
(`docs/PROMPT_ARRANQUE_SESION.md:42`); la prohibición de prosa se hace cumplir **a ojo** por el
Director comparando `bloques/bloque_verificador.txt` con la plantilla. Un validador en el emisor
es candidato a una tanda posterior.

**Dos reglas de operación (sin cambio):** (a) fail-closed de directorio de trabajo — el
ecosistema es bi-máquina (Windows ↔ Linux); (b) centinela anti-lectura-rancia.

## CONTEXTO 3 — Trazabilidad de sesión

Script `scripts/analizar_sesion_ia.py`, **sólo lectura, sólo stdlib**, sobre los transcripts
JSONL del cliente (`~/.claude/projects/{slug}/`). Extrae por turno: identificador **real** del
modelo (`message.model`), `effort`, tokens, y la tabla de subagentes (`{sessionId}/subagents/`).

**Qué afirma y qué no** (escrito en el diseño, §5.2): *"detecta contradicciones, no conformidad.
No prueba que la sesión arrancara en frío; no prueba el rol; no detecta filtrado de artefactos.
Es un detector de humo, no un extintor."*

**Contrato del script (r3):** `--rol` coteja **cada turno** contra el roster **vigente en la
fecha local de ese turno** (tabla de vigencias abajo) y marca la desviación; un `--rol` fuera del
roster (p. ej. `coordinador`) → `exit 1` · `--esfuerzo` obligatorio, `exit 1` si falta ·
precedencia del esfuerzo **medido → settings → declarado**, rotulando siempre el origen · **lista
blanca fail-closed** de campos permitidos (modelo, effort, tokens, timestamps, agentType,
description, cwd, gitBranch, version), `content` jamás se lee · `exit ≠ 0` ante formato
desconocido, **jamás ceros** · el bloque `TRAZABILIDAD` **se genera el mismo día del cierre** de
la sesión (por M-7).

**Tabla de vigencias del Arquitecto (E1 r3, `diseno_f1.md` §9.2):**

| Ventana | Fechas (locales, -03:00) | Modelos legítimos |
|---|---|---|
| V1 | hasta 2026-08-06 | `claude-fable-5` |
| Transición | 2026-08-07 → 2026-08-09 | `claude-fable-5`, `claude-opus-5` |
| V2 | 2026-08-10 → 2026-09-05 | `claude-opus-5` |
| V3 | desde 2026-09-06 | `claude-fable-5-1` |

Justificación de la transición: la sustitución formal es del 10-08 (§10.7), pero la última sesión
medida de Fable 5 cerró el 06-08 (`caf731aa`) y la primera de Opus abrió el 07-08 (`a0b9d1eb`).
Sin la transición, el script marcaría 125/154 turnos (81%) de `a0b9d1eb` en vez de los 79 (51%)
de Sonnet que son la anomalía real (M-9). **La declara el Director** (duda D5).

**Integración con el emisor CLI (B3, `diseno_f1.md` §9.3):** ninguna en código. El emisor corre
al **inicio** de un rol y escribe en `bloques/` (tránsito, ignorado por git); el analizador corre
al **cierre** y su salida va al AVISO de un artefacto en `auditorias/` (expediente, commiteado).
MT-T5 se integra **por contrato**: el rol que cierra ejecuta `analizar_sesion_ia.py --last --rol
{rol} --esfuerzo {…}` y pega la salida literal en el campo `TRAZABILIDAD` de su AVISO. No se
edita el emisor ni `coordinador.json`.

**Restricción dura: el repositorio NexoExpress es PÚBLICO** (`gh repo view` → `"visibility":
"PUBLIC"`). El expediente se commitea y se publica. Decisiones no negociables (§5.3): lista
blanca fail-closed · `content` jamás se lee · prueba de canario en el DoD · fail-closed ante
formato desconocido, jamás ceros. Orden estructural: **MT-T3 (filtro) cierra antes de que
ninguna salida se commitee (MT-T5)**.

**Salida:** campo **`TRAZABILIDAD` propio** del AVISO, separado de `OBSERVABLE` (que sigue siendo
sólo lo que el Director puede abrir y tocar), con `CICLO` / `FASE` / `MT`. MT-T5 actualiza además
las enumeraciones `TURNO DE` / `MODELO` de la plantilla del AVISO (`:444-447`) al roster v3.0.

## CONTEXTO 4 — Evidencia empírica (medida, no supuesta)

**M-1.** De 7 sesiones medidas el 11-08, **3 ejecutaron dos modelos distintos en el mismo hilo**.
Caso `a0b9d1eb`: 75 turnos de `claude-opus-5` **y 79 de `claude-sonnet-5`**, en una sesión
declarada de Arquitecto — 51% de los turnos fuera de roster, invisible con la disciplina actual.

**M-2.** El campo `effort` está registrado como `high` en el 100% de las sesiones que lo
registran, **incluidas sesiones de F0/F1**, para las que §7.2 prescribe `low`/`medium`. En 3
sesiones (11-08) el campo era `null`.

**M-3.** `effortLevel` **no existe** en ningún `settings.json` (proyecto, usuario, ni el del
coordinador hermano).

**M-4. El roster depende de la fecha.** La sesión `caf731aa` (23-07 → 06-08) marcaba 97% de
desviación por `claude-fable-5` **y sin embargo era correcta**: Fable era el Arquitecto legítimo
hasta el 10-08. Registrado el 11-08 (`prueba_traspaso.md` F-1); **esa sesión ya no está en disco
(M-7)**. Caso vivo equivalente: `970c3ab4` (11-08, 133 turnos `claude-opus-5`) es correcta en V2 y
un cotejo contra el roster de hoy (Fable 5.1) la marcaría al 100%.

**M-5.** `isSidechain` es `false` en el 100% de las líneas; los turnos de subagente viven en
`{sessionId}/subagents/`. Un script que contara subagentes por ese campo reportaría **cero**
pareciendo correcto.

**M-6. Parada de Observación PO-1 ya ejecutada (11-08-2026), con dos corridas A/B:**
- **A/B-1** (sesión nueva dentro del repo): escribió el archivo pedido con los 10 campos correctos
  y el centinela. **No incluyó** un campo `TRAZABILIDAD` que sí aparece en otros artefactos del
  mismo expediente — prueba de que no arrastró contexto.
- **A/B-2** (sesión nueva **fuera** del repo, `cwd: /home/pueblac` verificado en el transcript):
  respondió literal `DETENIDO: directorio de trabajo incorrecto`, y las herramientas usadas fueron
  **`Bash` ×1 y nada más** — cero escrituras. No se creó ningún árbol paralelo.
- **Incidente intermedio:** dos intentos previos de A/B-2 corrieron en realidad dentro del repo
  (el entorno restauró el workspace). Los dos receptores informaron "directorio verificado" **y
  decían la verdad**; lo que resolvió la ambigüedad fue el campo `cwd` del transcript, no los
  autoinformes.

**M-7. El cliente rota los transcripts (medido 06-09-2026, `medicion_base_transcripts.md` §6).**
Cinco de las siete sesiones de la medición base **ya no existen** en `~/.claude/projects/`
(`01175772`, `0403aebe`, `6a1327bc`, `caf731aa`, `f50ba75a`: AUSENTE), y con ellas los 27
subagentes de M-5/H-4: *"(ninguna sesion en disco tiene directorio subagents/)"*. 26 días
después de la medición. Sólo quedan `a0b9d1eb`, `970c3ab4`, `b26bb166`, `7a918db5` (agosto) y las
dos de hoy.

**M-8. Fable 5.1 responde con identificador propio.** Sesión `def5412c` (Arquitecto bajo v3.0,
la que emite este paquete): `modelos={'claude-fable-5-1': 33}`, `effort={'high': 33}`, ventana
local `2026-09-06T21:12 → 21:18`, cliente `2.1.263`. Distinto de `claude-fable-5`.

**M-9. `a0b9d1eb` cruza la frontera del 10-08.** Por fecha local:
`turnos_por_ventana_roster={('V1(<=2026-08-09)', 'claude-opus-5'): 46, ('V2(2026-08-10..2026-09-05)',
'claude-opus-5'): 29, ('V2(2026-08-10..2026-09-05)', 'claude-sonnet-5'): 79}` (salida literal en
`medicion_base_transcripts.md` §6). Y `7479044c` (06-09, sesión del **Coordinador**, no del
Arquitecto): `modelos={'claude-opus-5': 69}`.

---

# Claims a verificar

**C1.** La frontera *"Ruta A nunca cruza una arista de verificación del triángulo, ni sustituye un
gate humano"* es **suficiente** para impedir la auto-verificación y el salto de gates, y es
superior a una lista de excepciones por rol porque sobrevive a los cambios de roster. Evidencia
nueva: el roster cambió **dos veces** (10-08 y 06-09) y la regla no tuvo que reescribirse; la
tabla de aplicación sí (desapareció el Sintetizador).

**C2.** Quedarse con la plantilla del CLI, portándole punto 0, centinela y prohibición de prosa
en `{{TAREA}}`, cierra el vector de encuadre del emisor sobre el Verificador **al menos tanto**
como la plantilla de cinco huecos de r2, y la filosofía *"mínimo, no techo"* (`verificador.md:39-40`)
lo mejora: el bloque no puede quitar comprobaciones y el Verificador puede añadir.

**C3.** Las dos reglas de operación (fail-closed de directorio + centinela) cierran los dos fallos
de operación identificados, **y siguen siendo necesarias con rutas absolutas**. Traza C3 sobre
M-6, que es una ejecución real, no un supuesto.

**C4.** La lista blanca fail-closed es **suficiente** para garantizar que ninguna salida
commiteada al repositorio **público** contenga contenido de conversación del Director.

**C5.** El cotejo fechado **por turno** con tres ventanas y transición declarada mantiene la
detección de M-1 sin producir falsas desviaciones sobre el histórico ni sobre el futuro. Ejecuta
simbólicamente los cuatro casos y muestra el veredicto literal para `a0b9d1eb`, `970c3ab4`,
`def5412c` y `7479044c` con `--rol arquitecto`.

**C6.** *"Ruta A admitida por v3.0 pero no instrumentada"* con las condiciones 1–3 de CONTEXTO 2
**no deja un hueco abierto** entre hoy y MT-T3: la salvaguarda de archivo previo al lanzamiento
(huella en `git diff`) no depende del script, y lo que sí depende (archivo del primer mensaje
del subagente) sólo añade detección a posteriori.

**C7.** Separar emisor (inicio, `bloques/`, no versionado) y analizador (cierre, `auditorias/`,
versionado) **sin acoplamiento de código** es el corte correcto, y no crea dos mecanismos
paralelos para el mismo dato.

# Dudas declaradas por el Arquitecto

**D1.** Que el campo del transcript se llame `effort` **no prueba** que sea la palanca que §7.2
nombra. Se rotula como "medido del transcript" sin afirmar equivalencia. ¿Es honesto ese rótulo o
induce a error igualmente?

**D2.** La prohibición de prosa en `{{TAREA}}` del Verificador se hace cumplir **a ojo** por el
Director (el emisor acepta cualquier texto, `emitir_arranque.py:159-160`). ¿Basta el control
visual sobre `bloques/bloque_verificador.txt`, o el diseño debe exigir ya un validador en el
emisor aunque eso amplíe la tanda?

**D3.** El script depende de `~/.claude/projects/`, ruta interna del cliente, no documentada,
sujeta a cambio de versión **y, ahora medido, a rotación** (M-7). ¿Es aceptable que un control
del ciclo dependa de un formato que nadie garantiza ni conserva? Mitigación: degradar a
`TRAZABILIDAD: no disponible` sin bloquear el ciclo, y generar el bloque el mismo día del cierre.

**D4.** PO-1 demostró que "abre una sesión nueva fuera del repo" **no es una instrucción
uniformemente ejecutable** en el entorno del Director (sin CLI en el terminal integrado; el
editor restauró el workspace). ¿Puede una directriz que promete fricción cero depender de un
gesto de interfaz que varía entre entornos?

**D5.** La ventana de **transición** (07-08 → 09-08, ambos modelos legítimos) evita marcar 46
turnos de Opus que ocurrieron cuando el roster escrito aún decía Fable. ¿Es una descripción
honesta de lo que pasó o una excepción que, generalizada, vaciaría el cotejo de sentido? Da una
recomendación única.

# Deuda YA ADJUDICADA — no son hallazgos nuevos

Presentar cualquiera de estos como descubrimiento es relleno y consume el presupuesto de la
respuesta:

1. El script **no** prueba arranque en frío, **no** prueba el rol y **no** detecta filtrado.
   Declarado en el diseño.
2. Ruta A **reduce** la visibilidad del Director sobre los traspasos. Por eso lleva condiciones y
   se declara "no instrumentada" hasta MT-T3.
3. La **Fase Pre-F0** (un rol nuevo para Gemini antes de F0) está **fuera de esta tanda** y tiene
   su propia ronda de diseño. No la audites aquí.
4. El coste en dinero no se calcula: los precios no están en el transcript.
5. Los gates G0/G0′/G1/G2 siguen siendo humanos y bloqueantes. No se automatiza ninguno.
6. La v3.0 se contradice sobre quién ejecuta F5 en Media/Baja, quién empaqueta F6 y quién hace el
   anti-bluff formal (CONTEXTO 1, último párrafo). Es documentación del Director, no de este diseño.
7. La rotación de transcripts (M-7) es una propiedad del cliente, no un defecto del diseño; lo que
   se audita es cómo el diseño la absorbe (D3).

**Regla dura sobre vectores mitigados.** El encuadre del emisor en Ruta A está **MITIGADO, NO
CERRADO**. Ataque residual descrito y asumido: el emisor puede (a) alterar el artefacto archivado
antes de lanzar —deja huella en `git diff`—, o (b) haber escrito un DoD débil en la spec, que
ninguna plantilla de bloque corrige. La prosa en `{{TAREA}}` del Verificador está **MITIGADA** por
control visual, no cerrada. Si demuestras que el diseño presenta como cerrado algo que sólo está
mitigado, tienes razón en rechazar el paquete.

# Preguntas de control (respóndelas TODAS; son parte del entregable)

**Q1.** Copia textualmente el **punto 0** que r3 porta a la plantilla del Verificador. Después
traza qué ocurre si el Arquitecto, al emitir, escribe en `{{TAREA}}`: *"Verificar MT-T3 del ciclo
2026-08-11_traspaso_y_trazabilidad; comprueba sobre todo que el filtro pasa"*: ¿qué regla del
diseño lo detecta, en qué momento, quién lo detecta y con qué compara? Da una **recomendación
única** sobre si esa detección es suficiente — no un "depende".

**Q2.** El diseño enumera **cuatro** decisiones derivadas de que el repositorio sea público.
Cítalas. Después indica **cuál de las cuatro cae primero** si una versión nueva del cliente añade
un campo no previsto al transcript, y por qué. Añade: ¿cambia la respuesta el hecho de que el
cliente **borre** sesiones (M-7)?

**Q3.** La condición 3 (*"no sustituye un gate humano"*) deja al Especificador fuera de Ruta A
porque entre F1 y F3 está G1. Pero `coordinador.json:142` admite **Arquitecto → Ingeniero**.
Traza el caso: el Arquitecto lanza al Ingeniero como subagente con la spec de F3 ya archivada y G1
concedido. ¿Cruza alguna arista de verificación o algún gate? Da una **recomendación única**:
mantener la admisión de `coordinador.json:142`, o restringirla a Especificador → Ingeniero como
dice `:500`.

**Q4.** Usando M-1, M-8 y M-9 y la tabla de vigencias, escribe la **línea literal de veredicto**
que el script debería emitir para `--rol arquitecto` sobre `a0b9d1eb` (07-08 → 11-08), `970c3ab4`
(11-08), `def5412c` (06-09) y `7479044c` (06-09). Deben justificarse por la fecha y el
identificador de modelo, no por el porcentaje. Después: qué debe emitir `7479044c --rol
coordinador`.

# Anti-aprobación-automática

Si tu veredicto global es APROBADO o APROBADO CON OBSERVACIONES, debes ADEMÁS demostrar **con
evidencia** por qué cada una de estas trampas NO aplica. "Parece bien" no es demostración.

**T1.** El mismo Opus 5 escribe la spec (F3) y, en sesión nueva, verifica (F5). La plantilla fija
impide sesgar el bloque, y *"mínimo, no techo"* deja al Verificador añadir comprobaciones — **pero
el DoD mínimo lo escribió el Especificador en la spec.** ¿Cierra el diseño ese vector, lo mitiga,
o sólo lo mueve del bloque a la spec? Distingue cerrado de mitigado.

**T2.** El centinela es `— CIERRE {CICLO} / {MT} / {FECHA}`. Se produce una recalibración (F3′)
que rehace **la misma MT, el mismo día, en el mismo ciclo**. El emisor vuelve, lee
`verificacion_mtNN.md` y encuentra un centinela **idéntico** al que espera. ¿Distingue la segunda
corrida de la primera?

**T3.** La lista blanca incluye `description` del subagente, que es **texto libre escrito por el
emisor**. Un emisor podría volcar ahí contenido sensible, y saldría publicado en un repositorio
público pasando el filtro. ¿Lo cierra el diseño?

**T4.** `--esfuerzo` es obligatorio y su valor se rotula como "declarado" cuando no hay medida.
Nada impide declarar `high` sin haberlo usado. ¿Aporta el campo algo más que una apariencia de
control?

**T5.** `coordinador.json:125` dice que los arranques *"los autoriza el Director"*, y
`PROMPT_ARRANQUE_SESION.md:42` dice que **los emite el Arquitecto**. En r2 el Director comparaba
dos textos fijos; en r3 compara `bloques/bloque_verificador.txt` contra una plantilla que tiene
dos huecos legítimos. ¿"Autorizar" es aquí un control real o un sello? ¿Qué tendría que existir
para que lo fuera, y lo exige el diseño?

# Entregable final

1. Tabla C1..C7 con verdictos. 2. Respuestas Q1..Q4 completas. 3. Las cinco trampas T, si
apruebas. 4. Opinión fundada sobre D1..D5. 5. Veredicto global (APROBADO / APROBADO CON
OBSERVACIONES / RECHAZADO).

Una respuesta sin citas del contexto o sin las trazas obligatorias es **INVÁLIDA** y será devuelta
sin discusión.

**Formato de entrega:** responde con **UN ÚNICO documento markdown completo**, listo para archivar
sin edición. No lo trocees ni lo comentes fuera del documento. Empieza con tu sello
`[AUDITOR · Gemini 3.1 Pro High · turno N]`. El Director lo guardará literal en
`auditorias/2026-08-11_traspaso_y_trazabilidad/respuesta_diseno_ronda1.md`. Termina el documento
con la línea:

```
— CIERRE 2026-08-11_traspaso_y_trazabilidad / F2-r1 / AAAA-MM-DD
```

---

━━ AVISO DE TRASPASO ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CICLO      : 2026-08-11_traspaso_y_trazabilidad
FASE       : F2 — Auditoría de DISEÑO, ronda 1 (Tanda 1), paquete r3 bajo v3.0
TURNO DE   : Auditor
MODELO     : Gemini 3.1 Pro High — fijo por §2 v3.0 (`:136`), sin desviación que ratificar
ENTREGAR   : auditorias/2026-08-11_traspaso_y_trazabilidad/prompt_diseno_ronda1_v3.md
ADJUNTOS   : Ninguno — revisión de diseño, el contexto viaja dentro del prompt
DESTINO    : conversación NUEVA de Gemini, sin herencia de ningún hilo y NUNCA
             el hilo del Asesor (§1.1). Pasos exactos del Director:
             1. (antes de nada, recomendado) copia de seguridad de los transcripts
                fuera del repo — preserva a0b9d1eb para PO-2 aunque el cliente
                la rote (M-7):
                cp -r ~/.claude/projects/-home-pueblac-AndroidStudioProjects-NexoExpress ~/.claude/respaldo_nexo_2026-09-06
             2. Ratificar (o cambiar) las dos decisiones de diseno_f1.md §9.1 y
                §9.2. Si cambia alguna, el Arquitecto reemite este paquete; si
                no, sigue.
             3. Reemitir el bloque del Auditor (el que hay en bloques/ apunta al
                paquete desfasado):
                python3 scripts/emitir_arranque.py auditor "Auditar F2 ronda 1: diseño de traspaso y trazabilidad (tanda 1), paquete r3 bajo v3.0" --insumo auditorias/2026-08-11_traspaso_y_trazabilidad/prompt_diseno_ronda1_v3.md
             4. En Gemini, conversación nueva. Mensaje 1: el contenido de
                bloques/bloque_auditor.txt (Ctrl+A, Ctrl+C). Esperar el sello
                [AUDITOR · Gemini 3.1 Pro High · turno 1] sin acción.
             5. Mensaje 2: el contenido ÍNTEGRO de este archivo (Gemini no lee
                rutas del disco).
ACCIÓN     : auditar el diseño de la Tanda 1 y devolver un único documento
OBSERVABLE : Ninguno en esta fase — PO-1 ya se cobró (M-6); PO-2 llega con MT-T3
TRAZABILIDAD: sesión def5412c · claude-fable-5-1 × 33 turnos · effort high
             [medido del transcript, lectura ad-hoc — el script es F4]
             · fase F2 (emisión) · cotejo roster V3 (Arquitecto): OK
VUELVE A   : Director, que guarda la respuesta literal como
             respuesta_diseno_ronda1.md y convoca el anti-bluff. Quién lo hace
             es deuda de la v3.0 (CONTEXTO 1); propuesta del Arquitecto:
             el Verificador (Opus 5, sesión nueva), no el Arquitecto sobre su
             propio diseño. Decide el Director antes de G1.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
