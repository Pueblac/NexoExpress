# Diseño conceptual F1 — Directriz de Traspaso (Rutas A y B) + Trazabilidad de Sesión

**Ciclo:** `2026-08-11_traspaso_y_trazabilidad`
**Productor:** r1/r2 Arquitecto Macro — Claude Opus 5 (v2.6) · r3 Arquitecto Macro — Claude Fable 5.1 High (v3.0)
**Revisión:** **r3 — 06-09-2026, actualización a la metodología v3.0 (ver §9; r2 del 11-08 conservada íntegra en §0–§8).**
**Evidencia de apoyo:** `medicion_base_transcripts.md` · `prueba_traspaso.md`
**Fuente de referencia:** ya **no es la versión simulada del encargo**, sino
los documentos reales del proyecto hermano, leídos el 11-08:
`Coordinador_Indicadores_ImasD/docs/directriz_traspaso_entre_agentes.md` y
`.../directriz_cierre_trazabilidad.md` (ambos vigentes desde el 10-08-2026).

---

## 0. Estado del gate y qué cambió en r2

**G0 concedido por el Director el 11-08-2026**, sujeto a las cuatro
enmiendas que el propio Arquitecto detectó al contrastar su diseño con las
directrices reales del hermano, más una pieza nueva de arquitectura.

Cambios de r1 → r2:

| # | Cambio | Origen |
|---|---|---|
| E1 | El script cotea `--rol` contra el roster **vigente en la fecha de la sesión** y marca la desviación | Directriz hermana §3.3(1) + hallazgo F-1 de `prueba_traspaso.md` |
| E2 | `--esfuerzo` obligatorio: **exit 1** si falta | Directriz hermana, cierre §3 |
| E3 | Precedencia del esfuerzo: **medido → settings → declarado**, rotulando el origen | Divergencia empírica F-3: aquí el campo `effort` SÍ existe |
| E4 | Ruta A incorpora el riesgo *"entrega interna sin dudas = sospecha"* | Directriz hermana §3.3(4) — no estaba en r1 |
| E5 | **`TRAZABILIDAD` es campo propio del AVISO**, no sub-bloque de `OBSERVABLE` | Decisión del Director sobre D-e |
| E6 | Nueva **Fase Pre-F0** (Guionista de Negocio) — ver §8 | Orden del Director |

**Anomalía de procedimiento, que sigue vigente.** La metodología ordena
**F0 → G0 → F1 → F2**, y este diseño se redactó junto al plan. Con G0 ya
concedido la anomalía queda saldada para las Rutas A/B y la trazabilidad.
**No queda saldada para §8 (Pre-F0)**, que es material nuevo: modifica la
secuencia de fases del ciclo y por tanto exige su propia ronda F1→F2 antes
de adoptarse. Sigue sin emitirse `prompt_diseno_ronda1.md`.

---

## 1. El problema, en una frase

El Director es hoy el **bus de datos** del ciclo: abre las sesiones, pega el
contexto, rutea cada artefacto y archiva cada respuesta. Y de todo ese
tráfico **no queda registro de quién lo resolvió realmente** — sólo de quién
se suponía que debía resolverlo.

Son dos problemas distintos y conviene no confundirlos, porque **una mejora
no arregla la otra**:

| | Problema | Síntoma |
|---|---|---|
| **P1 — Toil** | El traspaso consume atención humana en tareas mecánicas | El Director inicializa, pega, rutea, archiva. Cuatro operaciones por fase. |
| **P2 — Opacidad** | No hay registro empírico del modelo ni del esfuerzo | El campo `MODELO` del AVISO (§5) es una *intención*, no un *hecho* |

**P2 está confirmado empíricamente, no supuesto.** Tres de siete sesiones de
este proyecto ejecutaron dos modelos distintos en el mismo hilo, y el
`effort` registrado es `high` en el 100% de las sesiones que lo registran,
incluidas las de F0/F1 donde §7.2 prescribe `low`/`medium`. Hallazgos H-1 y
H-2 de `medicion_base_transcripts.md`.

---

## 2. Hallazgo que reencuadra todo el análisis: esto no es nuevo, es a medias

Antes de evaluar "adoptar Ruta A y Ruta B", conviene ver que **el ecosistema
ya usa las dos, sin nombre y sin frontera escrita**:

- **Ruta A ya existe.** §6 de la metodología: *"Práctica consolidada:
  rotación asistida — el Arquitecto lanza al Ingeniero como subagente con
  contexto limpio y la spec archivada"*. Se ha usado en al menos cuatro
  ciclos (27 subagentes registrados en tres sesiones, H-4).
- **Ruta B ya existe.** `auditorias/README.md`, desde el 07-07-2026:
  *"Flujo de una sola escritura: cada prompt instruye a Gemini para que
  entregue su respuesta como un único documento markdown listo para
  archivar. El Director lo guarda tal cual (...) y avisa al Sintetizador
  (sin pegarlo en el chat); este lo lee del disco."* Eso **es** Ruta B: un
  bloque autónomo, respuesta escrita a una ruta conocida, y el emisor la lee
  del disco al volver.

**Consecuencia para el juicio del Director:** la pregunta de G0 no es
"¿incorporamos dos mecanismos nuevos y arriesgados?" sino **"¿ponemos por
escrito la frontera de dos mecanismos que ya usamos sin ella?"**. Un
mecanismo en uso sin regla escrita es más peligroso que el mismo mecanismo
con regla escrita. Eso baja el riesgo percibido y, sobre todo, cambia dónde
está el riesgo: no en adoptarlas, sino en **dónde se les pone el freno**.

---

## 3. Ruta A — traspaso interno por subagente

### 3.1 Qué es

El emisor lanza al receptor como **subagente** (una sesión hija que arranca
sin memoria de la conversación del padre — analogía: un becario nuevo al que
le das una carpeta y nada más) en vez de devolverle el artefacto al Director
para que lo rote a mano.

### 3.2 Viabilidad: alta, y ya demostrada

27 subagentes lanzados en tres sesiones, con `description`, alias de modelo
pedido y modelo real por turno registrados (H-4). En `caf731aa`, 15
subagentes pedidos como `sonnet` produjeron 509 turnos de `claude-sonnet-5`
— coherencia confirmada. No hay que construir nada: hay que **acotarlo**.

### 3.3 El riesgo real, y no es el que parece

El riesgo obvio —"el subagente no arranca del todo limpio"— es menor: el
subagente sí arranca sin el historial del padre.

El riesgo serio es otro: **el emisor escribe el prompt del receptor**. Quien
redacta el encargo elige qué ve el que lo recibe. Es exactamente el límite
que §1 ya declaró para el prompt de auditoría (*"el nodo que redacta el
prompt de auditoría podría filtrar lo que ve el Auditor"*), y allí se
neutralizó de forma **estructural**: el `git diff` literal viaja íntegro y
el Auditor rechaza como INVÁLIDO todo prompt sin diff.

Ruta A necesita la neutralización equivalente:

> **El prompt de lanzamiento no transporta contenido: transporta rutas.**
> El subagente lee el artefacto del disco. Si el emisor quiere filtrar,
> tiene que alterar un archivo archivado del expediente — y eso deja huella
> en `git diff`.

### 3.4 La frontera de exclusión (el punto que el Director debe fijar en G0)

La orden pedía atención especial a mantener al Verificador aislado. Mi
dictamen es que **la exclusión del Verificador no basta**, porque la razón
por la que se le excluye aplica a más nodos. La regla correcta es
estructural, no una lista de excepciones:

> **Ruta A NUNCA cruza una arista de verificación del triángulo (§1).**
> Un emisor puede lanzar como subagente a quien **consume** su salida;
> jamás a quien **la juzga**.

Aplicada a los roles del ciclo:

| Receptor | ¿Ruta A? | Por qué |
|---|---|---|
| **Ingeniero (F4)** | **SÍ** — lanzado por Arquitecto o Especificador | No verifica a nadie (§1). Práctica ya consolidada. |
| **Sintetizador — empaquetado F6** | **SÍ**, lanzado por el **Arquitecto**; **NO** por el Ingeniero | Empaquetar es determinista, pero quien escribió el código no elige el empaquetador de su propia auditoría. |
| **Verificador F5 (Opus en Alta / Haiku en Media-Baja)** | **NUNCA** | Verifica al Ingeniero, y en Alta el Especificador es el mismo modelo. Un Verificador lanzado por el verificado es auto-verificación con un rodeo. |
| **Auditor externo (Gemini)** | **NUNCA** | Es cross-vendor y adversarial por diseño. Además, técnicamente no cabe: no vive en Claude Code. |
| **Asesor (Gemini)** | **NUNCA** | Es del Director, no del ciclo (§1.1). |
| **Especificador (F3)** | **NO por defecto** | Consume el diseño del Arquitecto, así que la regla no lo prohíbe; pero en **Alta** Arquitecto y Especificador son el mismo modelo, y encadenarlos internamente borra el único corte de contexto que los separa. Se deja fuera hasta tener datos. |

**Por qué esta regla y no una lista:** una lista de excepciones envejece mal
—cambia el roster de modelos y hay que reescribirla, como pasó el 10-08 con
Fable—. Una regla anclada al triángulo sobrevive a los cambios de modelo,
porque el triángulo no cambia.

### 3.4-bis El riesgo propio de la Ruta A (E4)

La directriz hermana (§3.3.4) señala un vector que este diseño **no tenía**
en r1, y que es el más fino de los dos documentos:

> *"Una sesión subordinada tiende a decidir para poder terminar. Si una
> entrega interna llega sin dudas y sin desviaciones en una orden larga, eso
> es motivo de sospecha, no de satisfacción."*

Es una inversión del instinto normal: en Ruta A, **la ausencia de fricción
es un síntoma, no un logro**. Un subagente sabe que su trabajo termina
cuando entrega, y "duda = pregunta" (§8) compite con esa presión. Un
Ingeniero humano que no entiende algo interrumpe; un subagente tiende a
resolverlo por su cuenta para poder cerrar.

Se incorpora como regla de lectura, no como control automático — no hay
forma mecánica de distinguir una orden bien especificada de una duda tapada:

> **Toda entrega por Ruta A de una orden larga que llegue sin dudas y sin
> desviaciones se marca para spot-check del Director.** No se rechaza; se
> mira.

Nótese la coherencia con el ecosistema: los ciclos que más defectos
encontraron son los que más dudas declararon (MT-D2: seis rondas, §10.5).
Una entrega impoluta a la primera nunca ha sido la norma aquí.

### 3.5 Lo que Ruta A le cuesta al Director, y que no debe ocultarse

§6 justifica el toil del Modo M con un beneficio concreto: *"el Director ve
pasar todos los artefactos"*. Ruta A **le quita eso**. Y hay que decirlo
claro: **Ruta A es Modo A restringido a las aristas no-verificadoras** — y
el Modo A está declarado NO habilitado y "requiere ciclo propio" (§6).

No propongo saltarse esa condición. Propongo lo contrario: que Ruta A
herede desde el primer día las salvaguardas que §6 exige al Modo A —
artefacto archivado **antes** del lanzamiento, spot-check de al menos un
traspaso por ciclo, gates humanos intactos, anti-bucle vigente— más una
específica: **el primer mensaje de usuario de cada subagente se archiva en
el expediente**, extraído del transcript. Así el Director puede comprobar,
después y sin estar presente, con qué encargo exacto arrancó el receptor.

**Y por eso Ruta A va la última** (MT fuera de esta tanda): es la única de
las tres mejoras que **reduce** la visibilidad del Director, y no debe
entrar antes de que exista el mecanismo que se la devuelve.

---

## 4. Ruta B — el bloque `COPIAR`

### 4.1 Qué es

El emisor termina su artefacto con un bloque literal que el Director
**copia y pega sin leer ni editar** en una sesión nueva. El bloque lleva
dentro todo lo que el receptor necesita: su rol, el ciclo, las rutas que
debe leer del disco, la tarea, y **dónde escribir la respuesta**. El
Director hace dos gestos: abrir sesión con el modelo indicado, y pegar.

Es la única de las tres mejoras que ataca P1 (toil) **sin** tocar P2, y la
única que **no reduce** el control del Director: sigue siendo él quien abre
la sesión, así que el aislamiento del receptor es real, no prometido.

### 4.2 Por qué es el vehículo correcto **precisamente para el Verificador**

Aquí está el punto más importante del diseño, y es contraintuitivo:

- Por **Ruta A**, un Verificador lanzado por el Arquitecto/Especificador
  (mismo modelo en Alta) es auto-verificación disfrazada. **Prohibido.**
- Por **Ruta B**, la sesión del Verificador **la abre el Director**. El
  emisor no la lanza, no hereda contexto de él y no puede tocarla. El
  aislamiento es estructural.

Ruta B no es un atajo que debilita el aislamiento del Verificador: **es lo
que lo hace barato de mantener**. Hoy el aislamiento cuesta cuatro
operaciones manuales, y lo que cuesta caro se acaba saltando.

### 4.3 El riesgo residual, y su neutralización

Queda una rendija: **el bloque lo escribe el emisor**. Un bloque de
verificación redactado como *"comprueba que el DoD pasa"* induce un
resultado; *"ejecuta los comandos del DoD y reporta la salida literal"* no.

Neutralización — **plantilla fija con huecos, prosa prohibida**:

> El bloque `COPIAR` del **Verificador** es una plantilla literal e
> invariable. Lo único que cambia entre ciclos son cinco huecos: expediente,
> micro-tarea, ruta de la spec, ruta del informe, ruta de salida.
> **El emisor no escribe ni una frase libre dentro.** Un bloque de
> verificación con prosa añadida es **INVÁLIDO** y el Director lo devuelve
> sin ejecutarlo.

Esto es verificable de un vistazo, que es la propiedad que lo hace útil: el
Director no tiene que juzgar si el encargo está sesgado, sólo si el bloque
es idéntico al de siempre. **Es un control que él puede ejercer sin ser
técnico** — el mismo criterio de las Paradas de Observación (§3.1).

Corolario: el bloque **no reproduce el DoD**. El Verificador lo lee de la
spec archivada. Si el DoD se copiara dentro del bloque, ahí es donde
entraría el filtrado.

### 4.4 Dos variantes, porque los receptores no son iguales

| | **B-código** | **B-chat** |
|---|---|---|
| Receptor | Sesión de Claude Code sobre el repo | Gemini en el navegador (Auditor, Asesor) |
| Escribe la respuesta | **El propio receptor**, en la ruta indicada | El **Director** pega la respuesta literal en la ruta indicada |
| Estado | Nuevo | **Ya en uso desde el 07-07** (`auditorias/README.md`) |

La orden del Director describía B-código. B-chat existe y funciona; la
directriz debe recogerlo para no dejar al Auditor fuera de la norma.

### 4.5 Dos fallos de operación que hay que cerrar en el diseño, no en el uso

1. **El ecosistema es bi-máquina** (Windows trabajo ↔ Linux casa, §
   bitácora 28-07). Un bloque con rutas absolutas revienta al cambiar de
   máquina, o peor: escribe en un sitio equivocado. **Regla:** rutas
   relativas al repo, y **primera instrucción del bloque = comprobar que el
   directorio de trabajo es el repo correcto y DETENERSE si no lo es**
   (*fail-closed*: como un torniquete que se bloquea si se va la luz, en vez
   de quedarse abierto).
2. **Lectura rancia.** El emisor vuelve, lee la ruta de salida y encuentra
   un archivo... del ciclo anterior. Y cierra la fase creyendo que se
   ejecutó. **Regla:** el receptor cierra su archivo con una línea centinela
   fija que incluye ciclo, micro-tarea y fecha; **sin centinela, el emisor
   rechaza el archivo y DETIENE**. Determinista y barato.

---

## 5. Trazabilidad — `scripts/analizar_sesion_ia.py`

### 5.1 Viabilidad: confirmada hoy, con datos

Todo lo que la directriz pide existe en el transcript y está medido en
`medicion_base_transcripts.md`: modelo real por turno (`message.model`),
`effort` por turno, tokens de entrada/salida/caché, y la tabla completa de
subagentes con rol declarado y modelo real.

### 5.2 Qué debe y qué NO debe afirmar

Este es el punto donde un script de trazabilidad se convierte en su propio
enemigo. Lo que puede afirmar:

> *"La orden MT-Tx se cerró con 154 turnos: 75 de `claude-opus-5` y 79 de
> `claude-sonnet-5`, `effort: high`, 368k tokens de salida. El AVISO
> declaraba Opus 5. **DISCREPANCIA.**"*

Lo que **no** puede afirmar, y debe quedar escrito en la propia directriz
para que nadie lo lea de más:

- No prueba que la sesión arrancara **en frío** — registra el modelo, no el
  contexto. La inicialización de identidad (§6) sigue sin verificación
  mecánica, y ése era precisamente el riesgo declarado en §10.7.
- No prueba el **rol**: `description` es lo que el emisor dijo que era.
- No detecta **filtrado** de artefactos.

En el eje de §4.3: **detecta contradicciones, no conformidad.** Un detector
de humo, no un extintor. Si el Director lo interpreta como garantía de
cumplimiento, la directriz habrá empeorado el ciclo en vez de mejorarlo:
tendría un control que no controla y la sensación de que sí.

### 5.2-bis Contrato del script tras las enmiendas (E1, E2, E3)

El script deja de ser un informe y pasa a ser un **control**. Tres cambios:

**E1 — `--rol` cotea contra el roster, con la fecha en cuenta.** El script
compara el modelo medido contra el que el roster asigna a ese rol y **marca
la desviación**. Con un matiz que sólo apareció al renderizar el bloque
sobre datos reales (`prueba_traspaso.md`, F-1): **el roster depende de la
fecha**. La sesión `caf731aa` marca 97% de desviación por `claude-fable-5`
y sin embargo era correcta — es del 23-07 al 06-08, y la sustitución de
Fable por Opus es del 10-08 (§10.7). Un cotejo contra el roster de hoy
llenaría de falsas alarmas todo el histórico y quemaría la credibilidad del
mecanismo en su estreno. **El roster va con tabla de vigencias por fecha.**

**E2 — `--esfuerzo` obligatorio, exit 1 si falta.** Tomado literal de la
directriz hermana: *"un cierre sin esfuerzo declarado está incompleto por
diseño"*. Ojo a la distinción con D4: **E2 impide cerrar sin declarar el
esfuerzo; D4 dice que si el script entero falla, el ciclo no se detiene.**
Son cosas distintas y ambas se sostienen.

**E3 — Precedencia del esfuerzo: medido → settings → declarado.** Y aquí
este ecosistema **diverge del hermano por evidencia, no por criterio**:

| | `Coordinador_Indicadores_ImasD` | NexoExpress |
|---|---|---|
| `effort` en el transcript | barrido con **cero apariciones** | **existe** por turno: `high` en 4 sesiones, `null` en 3 |
| `effortLevel` en settings | fuente usada | **no existe** (verificado: ni proyecto, ni usuario, ni el propio hermano) |
| Resultado | esfuerzo *declarado* | esfuerzo **medido** donde lo haya |

La regla es por tanto de precedencia, no de fuente fija, y **el origen se
rotula siempre**: `[medido del transcript]`, `[settings]` o `[declarado]`.
Una cifra declarada presentada como medida es peor que no tenerla — ése es
el criterio del hermano y se conserva íntegro.

**Cautela que no se elimina:** que el campo se llame `effort` no prueba que
sea la palanca que §7.2 nombra. Se rotula como *medido del transcript* y
nada más. Afirmar "esta sesión corrió con el `effort` de §7.2" sería una
inferencia no probada — exactamente el tipo de salto que el anti-bluff caza.

### 5.3 Riesgo dominante: el repositorio es PÚBLICO

`Pueblac/NexoExpress` es **PUBLIC** (verificado con `gh repo view`). El
transcript contiene todo lo tecleado, incluidas rutas de credenciales y
prosa del Director; el expediente se commitea y se publica.

Decisiones de diseño que se derivan, no negociables:

1. **Lista blanca fail-closed.** Se enumeran los campos permitidos —modelo,
   effort, tokens, timestamps, agentType, description, cwd, gitBranch,
   version— y **todo lo demás se descarta**, incluido cualquier campo futuro
   que aparezca con una versión nueva del cliente. Una lista negra fallaría
   abierta el día que cambie el formato.
2. **`content` jamás se lee.** No se filtra: no se toca.
3. **Prueba de canario en el DoD**: se toma una cadena literal conocida de
   la conversación y se comprueba que **no aparece** en la salida. Un filtro
   sin prueba adversarial es una intención.
4. **Fail-closed ante formato desconocido**: si el JSONL no encaja con el
   esquema esperado, el script sale con error visible. **Jamás imprime
   ceros** — un cero que en realidad es "no pude leerlo" es un dato falso
   con apariencia de dato bueno, que es lo peor que puede producir un
   artefacto de trazabilidad.

Y el orden de las micro-tareas se vuelve estructural: **el filtro (MT-T3)
cierra antes de que ninguna salida se commitee (MT-T5)**. Publicar es
irreversible: un commit se revierte, pero lo que estuvo en un repo público
se da por difundido.

### 5.4 Trampa técnica ya identificada

`isSidechain` es `false` en el 100% de las líneas (H-5). Los turnos de
subagente viven en `{sessionId}/subagents/`, no en el JSONL del padre. Un
script que contara subagentes por `isSidechain` reportaría **cero** y
parecería funcionar. Queda escrito **antes** de implementar, para que el
DoD lo cace.

### 5.5 Acoplamiento externo, declarado

Los transcripts viven en `~/.claude/projects/{slug}/`, una ruta interna del
cliente que puede cambiar sin avisar. Mitigación: ruta parametrizable con
`Path.home()` por defecto (funciona en Linux y Windows) y fallo ruidoso si
no existe. **Este script no se convierte en dependencia de ninguna fase del
ciclo**: si un día deja de funcionar, el AVISO registra `TRAZABILIDAD: no
disponible` y el ciclo sigue. Un ciclo que se bloquea porque falla su propio
instrumento de medida es un ciclo peor que el que no medía.

---

## 6. Decisiones — resueltas en G0 (11-08-2026)

| # | Decisión | Eje | Resolución del Director |
|---|---|---|---|
| **D1** | ¿Entra la **Ruta A** en esta tanda? | Reversible × impacto **alto** | **NO en esta tanda** (recomendación adoptada). Su frontera se escribe ahora en MT-T4; se habilita cuando exista el instrumento que devuelve visibilidad. Coherente con la propia directriz hermana, cuyo §4 hace depender la Ruta A del cierre con trazabilidad. |
| **D2** | ¿**v2.7** o **anexo local**? | Reversible × bajo | **Se parte en dos.** Traspaso + trazabilidad → **anexo local** `docs/DIRECTRIZ_TRASPASO.md` (tanda 1). **Pre-F0 → v2.7**, porque altera la secuencia de fases del §3 y eso no cabe en un anexo. Ver §8.4. |
| **D3** | ¿La salida del script se **commitea** al expediente público? | **Irreversible** × alto | **Sí, sólo el bloque agregado y sólo tras la prueba de canario de MT-T3.** Nunca el transcript crudo. |
| **D4** | ¿La trazabilidad **bloquea** el cierre? | Reversible × medio | **No bloqueante** como mecanismo (si el script falla, `no disponible` y el ciclo sigue). Compatible con E2, que sí exige declarar el esfuerzo cuando el script corre. |
| **D-e** | ¿`TRAZABILIDAD` dentro de `OBSERVABLE` o campo propio? | Reversible × bajo | **Campo propio** (E5). El hermano lo mete dentro de `OBSERVABLE` y en la misma frase argumenta que *"son dos cosas distintas y mezclarlas vaciaría el campo de sentido"*; el Director lleva ese argumento a su conclusión. `OBSERVABLE` sigue siendo sólo lo que él puede abrir y tocar (§3.1). |

---

## 7. Alcance explícito

**Tanda 1 — dentro:** plantillas del bloque `COPIAR` (Verificador fija ·
B-código · B-chat) probadas en un caso inofensivo · script de trazabilidad
de sólo lectura con cotejo de roster fechado y filtro fail-closed · anexo
`docs/DIRECTRIZ_TRASPASO.md` con la frontera de exclusión de Ruta A escrita
· campo propio `TRAZABILIDAD` en el AVISO.

**Tanda 2 — dentro:** definición formal de la **Fase Pre-F0** y su adopción
como **v2.7**, con su propia ronda F1→F2 (§8).

**Fuera (y por qué):** habilitar Ruta A (D1) · Modo A completo (§6, ciclo
propio) · cualquier automatización de gates (§3, no se automatizan jamás) ·
cálculo de coste en dinero (los precios no están en el transcript; inferirlos
sería inventarlos) · tocar código de producto (este ciclo no entra en
ActaExpressWeb) · que Opus escriba el script (F4 es de Sonnet, §7.2).

---

## 8. Fase Pre-F0 — el Guionista de Negocio (E6, orden del Director)

### 8.1 La fase, formalmente

```
Pre-F0. GUION   Guionista de Negocio (Gemini 3.1 Pro High, conversación
                NUEVA) recibe los requerimientos crudos del Director y emite
                un guion/roadmap de PRODUCTO: qué debe hacer el sistema,
                para quién, con qué prioridad y qué queda fuera.
                Transporte: Ruta B-chat. Archivo: guion_negocio.md en el
                expediente, literal y sin editar.
                NO contiene arquitectura, contratos, schemas ni micro-tareas.
                ── No hay gate. El guion es INSUMO de F0, no un acuerdo. ──
F0. PLAN        Arquitecto (Opus) lee el guion y produce el plan. Está
                OBLIGADO a reformular el requerimiento con sus palabras y a
                declarar qué del guion acepta, qué rechaza y por qué.
                ── GATE G0: el Director aprueba el PLAN, no el guion. ──
```

**Exención:** Pre-F0 sólo aplica a metas que arrancan de requerimiento
crudo. Un bugfix, un cambio de metodología o una MT de infraestructura no
tienen guion que escribir, y forzarlo sería ceremonia. **La exención se
declara, no se omite en silencio** — mismo criterio que §3.1.

### 8.2 El cortafuegos: qué protege de verdad, y qué no

El argumento del Director es correcto **en su capa**: si el diseño técnico
lo escribe Opus, Gemini en F2/F6 no audita sus propias decisiones técnicas y
la regla de oro (§1) se mantiene. Confirmo esa parte.

Pero el cortafuegos **no es total**, y el diseño tiene que decirlo antes de
adoptarse:

> **F2 audita un diseño que desciende del encuadre del propio Auditor.**
> Gemini no auditará "esta funcionalidad no debería existir" ni "el
> requerimiento está mal planteado", porque el planteamiento lo puso él.
> La auditoría adversarial deja de cubrir **la capa de requerimiento**.

Es un vector real y de la misma familia que el que §1 ya declara para el
prompt de auditoría. Neutralizaciones, en orden de fuerza:

1. **El guion NO viaja a F2 ni a F6.** El prompt de auditoría lleva el
   diseño y el `git diff`, nunca el guion. Si el guion viajara, el Auditor
   reconocería su propio encuadre y quedaría anclado a él.
2. **F0 debe poder rechazar el guion, y dejar constancia.** Si el Arquitecto
   no puede descartar partes, el que decide es el Guionista. Por eso la
   reformulación con acepto/rechazo es obligatoria, no cortesía.
3. **Conversación nueva y separada.** Ya hay dos Gemini que no pueden
   compartir hilo (Auditor y Asesor, §1.1). Con el Guionista son **tres
   vértices**, y la regla de separación se vuelve más fácil de romper por
   descuido. Va escrita como prohibición explícita, no como buena práctica.
4. **El guion no tiene autoridad de gate.** G0 aprueba el plan de Opus.
5. **Residuo declarado:** los errores de requerimiento introducidos por el
   guion **quedan fuera del alcance de la auditoría adversarial**. El único
   control que los alcanza es el Director en G0 y la **Parada de Observación
   (§3.1)** — que existe precisamente para eso: para que el Director vea el
   producto, no el código. Es la compensación, y conviene verla como tal:
   **Pre-F0 sube la carga que soporta §3.1.**

### 8.3 La premisa de ahorro: no está probada, y ahora es medible

La justificación dada es que el consumo de Opus en F0/F1 es el mayor cuello
de botella. **Con los datos de hoy no puedo confirmarlo ni negarlo**, y
conviene decirlo antes de que la fase se adopte sobre una cifra que nadie
midió:

- El coste medido existe (`caf731aa`: 906.955 tokens de salida;
  `a0b9d1eb`: 368.178), pero **no está desglosado por fase**: una sesión
  abarca días y varias fases (hallazgo F-2 de `prueba_traspaso.md`).
- En este ecosistema, el requerimiento de producto **lo trae el Director**,
  no lo inventa Opus — `estado_actual.md` está lleno de "dirección de
  producto del Director". Lo que consume F0/F1 aquí parece ser **leer el
  repo y redactar artefactos**, no elicitar qué debe hacer el producto. Si
  es así, Pre-F0 sustituye algo que Opus apenas hace, y el ahorro sería
  marginal.
- Un guion externo puede incluso **encarecer** F0: Opus tendría que leerlo,
  contrastarlo con el repo y justificar sus rechazos — trabajo que hoy no
  hace.

**Esto no es una objeción a la fase, es una condición sobre su
justificación.** Pre-F0 puede valer la pena por otra razón, más sólida que
el ahorro: **obliga a que exista un requerimiento escrito y completo antes
de que nadie diseñe nada**, que es una carencia real del ciclo actual.

Y la buena noticia es que la tanda 1 construye justo el instrumento que
zanja la discusión. Por eso el bloque `TRAZABILIDAD` declara `CICLO`, `FASE`
y `MT`: en dos o tres ciclos se podrá responder con cifras **cuánto cuesta
F0/F1 de verdad**, en vez de discutirlo. La hipótesis queda escrita como
falsable, que es la exigencia que este ecosistema aplica a todo lo demás.

### 8.4 Por qué Pre-F0 es v2.7 y no un anexo, y por qué va en tanda 2

- **Es v2.7**: añade una fase al ciclo del §3 y un rol al §1. Un anexo local
  puede añadir reglas de operación; no puede cambiar la secuencia de fases
  sin que el documento principal mienta.
- **Va en tanda 2**: (a) la regla de tandas ≤5 para auditoría (§8) ya está
  cubierta por MT-T1..T5; (b) acoplar un cambio de fases con un cambio de
  transporte hace que un `RECHAZADO` en F2 arrastre a los dos; (c) su
  premisa se mide con el instrumento de la tanda 1.
- **Aviso sobre su F2**: la ronda de diseño de Pre-F0 pedirá a **Gemini que
  audite una propuesta que le concede a Gemini un rol nuevo**. El conflicto
  es leve pero real. Se neutraliza preguntándolo de frente en el prompt y
  aplicando el anti-bluff con lupa a cualquier veredicto que amplíe su
  propio papel.

---

## 9. Revisión r3 (06-09-2026) — actualización a la metodología v3.0

**Por qué existe esta sección.** El Director adoptó la **v3.0** el 06-09
(`docs/METODOLOGIA_TRIPLE_IA.md` §10.8) con el paquete de F2 ya escrito bajo
v2.6 y sin enviar. El Coordinador cotejó el desfase (`desfase_v3_para_f1r3.md`:
7 desfases de hecho A1–A7, 3 de fondo B1–B3, una deuda interna C). Esta sección
resuelve B1–B3, añade tres desfases de fondo que el cotejo no alcanzó a revisar
(§9.4–§9.6, ámbito declarado en su §E) y deja al Director las decisiones que
son suyas. §0–§8 **no se reescriben**: siguen siendo el diseño aprobado en G0;
donde §9 contradice a §0–§8, **prevalece §9**.

**Verificación previa de las citas del cotejo.** Las citas de §6 del cotejo
(`:462`, `:466`, `:495-503`) son exactas. Las de la tabla de roles van **una
línea por encima** de lo real: Arquitecto=Fable 5.1 está en `:38` (no `:39`),
Especificador en `:39`, Verificador en `:41`, y «Admite Ruta A» / «NUNCA Ruta A»
en `:500` / `:501`. El fondo del cotejo no cambia; el paquete de F2 cita las
líneas correctas (regla del Auditor: cita no verificable = afirmación inventada).

### 9.1 B1 — Ruta A: de «NO entra en esta tanda» a «admitida por v3.0, no instrumentada»

**Hecho.** La v3.0 dice que el Ingeniero «admite **Ruta A** (subagente asistido
lanzado por el Especificador) o Ruta B» (`docs/METODOLOGIA_TRIPLE_IA.md:500`) y
`coordinador.json:71` fija `"ruta_traspaso": "A"` para el Ingeniero;
`coordinador.json:142` amplía: «Arquitecto/Especificador -> Ingeniero admite
Ruta A». D1 (G0, 11-08) decía lo contrario. La orden posterior del mismo
Director prevalece: **Ruta A está admitida** para la arista
Arquitecto/Especificador → Ingeniero. Pero la v3.0 la admite **sin ninguna de
las salvaguardas de §3.5** (encargo archivado antes del lanzamiento, spot-check,
archivo del primer mensaje del subagente) y sin el instrumento que la audita a
posteriori (MT-T2/T3, aún F4). Mecánicamente, además, el emisor CLI sólo
produce bloques `COPIAR` (`bloques/bloque_ingeniero.txt`, Ruta B): la Ruta A de
la v3.0 es hoy una **declaración sin mecanismo**.

**Decisión r3.** MT-T4 escribe la frontera **como la v3.0 la deja** (admitida en
esa única arista) y le añade las **condiciones de uso** que no dependen del
script y que por tanto valen desde hoy:

1. **El encargo se archiva en el expediente ANTES de lanzar** el subagente, y
   el prompt de lanzamiento **transporta rutas, no contenido** (§3.3). Es la
   salvaguarda que deja huella en `git diff` y no necesita instrumento.
2. **E4:** entrega interna larga sin dudas ni desviaciones → spot-check
   obligatorio del Director (§3.4-bis).
3. **Nunca cruza una arista de verificación** (regla estructural de §3.4) **ni
   sustituye un gate humano**: el receptor sólo se lanza cuando el artefacto que
   consume ya está archivado y el gate previo (G1) concedido. Esta segunda
   cláusula es nueva en r3 y responde a `coordinador.json:142`: el Arquitecto
   puede lanzar al Ingeniero **sólo** con la spec de F3 ya en el expediente,
   nunca desde F1 saltándose G1 y F3.
4. **El archivo del primer mensaje del subagente** (extraído del transcript,
   §3.5) queda como condición **diferida a MT-T3**: hasta entonces la Ruta A
   está «admitida, no instrumentada», y así lo dice el anexo.

*Eje:* reversible (una regla del anexo) × impacto medio (visibilidad del
Director sobre los traspasos). **Recomendación:** mantener la v3.0 tal cual y
exigir las condiciones 1–3 desde el primer uso. La alternativa —congelar Ruta A
hasta MT-T5, como decía D1— es igual de reversible; la elige el Director en G1.

### 9.2 B2 — E1 con tres ventanas, transición declarada y cotejo por turno

**Hecho.** La v3.0 devuelve al Arquitecto a Fable, ahora **5.1**, cuyo
identificador real es **`claude-fable-5-1`** (H-7, distinto de `claude-fable-5`).
Y `a0b9d1eb` cruza la frontera del 10-08 con 46 turnos de Opus en la ventana en
que el roster escrito aún decía Fable (H-8).

**Decisión r3 — tabla de vigencias del Arquitecto** (el resto de roles se
tabula con el mismo criterio; sólo se cotejan roles del roster, un `--rol` fuera
del roster —«coordinador», «director»— es `exit 1`):

| Ventana | Fechas (locales) | Modelos legítimos | Fuente |
|---|---|---|---|
| V1 | hasta 2026-08-06 | `claude-fable-5` | v2/v2.5 (§10.2), última sesión medida `caf731aa` (F-1) |
| **Transición** | 2026-08-07 → 2026-08-09 | `claude-fable-5`, `claude-opus-5` | Fable dejó de estar disponible antes de formalizarse la sustitución (§10.7); primera sesión Opus `a0b9d1eb` abre el 07-08 |
| V2 | 2026-08-10 → 2026-09-05 | `claude-opus-5` | §10.7 |
| V3 | desde 2026-09-06 | `claude-fable-5-1` | §10.8, medido en `def5412c` |

**Cotejo por turno, no por sesión:** cada turno `assistant` se coteja contra la
ventana de **su propia fecha local**. Una sesión que cruza una frontera no se
adjudica entera a ninguna ventana. Veredictos literales que el DoD de MT-T2
fija **antes** de escribir el script:

- `a0b9d1eb --rol arquitecto` → **DESVIACIÓN**: `claude-sonnet-5` × 79 (51%)
  fuera de roster en V2. Los 46 turnos de Opus de la transición **no** se
  marcan.
- `970c3ab4 --rol arquitecto` → **OK** (133 turnos `claude-opus-5`, V2), pese a
  que el roster de hoy diga Fable 5.1. Sustituye a `caf731aa` como prueba de que
  el cotejo va fechado (H-9).
- `def5412c --rol arquitecto` → **OK** (V3, `claude-fable-5-1`).
- `7479044c --rol arquitecto` → **DESVIACIÓN** (69 turnos `claude-opus-5` el
  06-09, V3 exige `claude-fable-5-1`). Es una sesión del Coordinador, no del
  Arquitecto: `--rol coordinador` → `exit 1`, rol fuera del roster.

*Eje:* reversible (una fila de la tabla) × impacto bajo. **Punto que decide el
Director:** si la transición 07-08 → 09-08 se declara (recomendado: es lo que
ocurrió, y evitar falsas alarmas fue el motivo de E1) o si esos 46 turnos se
marcan como desviación. El paquete de F2 lo somete al Auditor como duda D5.

### 9.3 B3 — El bloque `TRAZABILIDAD` y el emisor CLI: dos mecanismos, dos momentos, sin acoplamiento

`scripts/emitir_arranque.py` corre al **inicio** de un rol y escribe en
`bloques/` (tránsito, ignorado por git — `.gitignore`); el bloque
`TRAZABILIDAD` se produce al **cierre** de una sesión y va al AVISO de un
artefacto en `auditorias/` (expediente, commiteado). No hay solapamiento de
función ni de archivo. **Decisión r3:** MT-T5 **no toca** el emisor ni
`coordinador.json` («No edite los scripts», `coordinador.json` línea 2) y se
integra **por contrato**: el rol que cierra un artefacto ejecuta
`analizar_sesion_ia.py --last --rol {rol} --esfuerzo {…}` y pega la salida
literal en el campo `TRAZABILIDAD` de su AVISO. Regla añadida por H-6: **se
genera el mismo día del cierre**, porque el cliente rota los transcripts. La
puerta `antes_de_emitir` del emisor (`emitir_arranque.py:119-127`) queda
documentada como punto de integración futuro, no usado en esta tanda.

### 9.4 Desfase nuevo — dos plantillas del Verificador; se queda una

**Hecho.** MT-T1 validó en PO-1 la plantilla fija de cinco huecos (§4.3,
`plantilla_copiar.md` §1). La v3.0 trae **otra**: `docs/prompts_arranque/verificador.md`,
emitida por CLI, con `{{TAREA}}` en texto libre (`:77`), `{{INSUMO}}` de una sola
ruta (`:73`), salida a un directorio y no a un archivo (`:81`), **sin** punto 0
fail-closed ni centinela, y con una filosofía distinta: «Tú decides qué se
verifica (…) los criterios de aceptación de la orden son el mínimo, no el
techo» (`:39-40`) frente al «el DoD que debes ejecutar es el de esa spec, y
ninguno otro» de r2.

**Decisión r3 — una sola plantilla: la del CLI**, porque la v3.0 manda que todo
arranque se emita mecánicamente (`docs/METODOLOGIA_TRIPLE_IA.md:466`). MT-T4
le **porta** lo que PO-1 demostró y ella no tiene:

1. **Punto 0 fail-closed de directorio** («DETENIDO: directorio de trabajo
   incorrecto»). Las rutas absolutas del CLI no lo sustituyen: una sesión
   abierta fuera del repo escribiría igualmente en la ruta absoluta.
2. **Centinela de cierre** `— CIERRE {CICLO} / {MT} / AAAA-MM-DD` y **nombre de
   archivo fijo** `verificacion_mtNN.md` en el expediente (la tabla de §4 de la
   metodología, `:347`, aún dice «anexo en informe_mtNN.md» — texto v2.6).
3. **Prosa prohibida en el bloque emitido:** para el Verificador, `{{TAREA}}` es
   literalmente `Verificar MT-NN del ciclo {CICLO}` y `{{INSUMO}}` es la ruta
   del informe (que cita la spec). Cualquier otra frase en
   `bloques/bloque_verificador.txt` lo hace **INVÁLIDO** y el Director lo devuelve
   sin pegarlo — el mismo control de un vistazo que r2 le daba.

Se **adopta la filosofía de la v3.0** («mínimo, no techo»): el bloque no puede
*quitar* comprobaciones del DoD, pero el Verificador puede *añadir*. Es
estrictamente mejor contra la trampa T1 (DoD débil en la spec) y no reabre el
vector de encuadre, porque el bloque sigue sin reproducir el DoD.
`plantilla_copiar.md` §1 pasa a ser **registro histórico de PO-1**, no plantilla
vigente. *Riesgo residual declarado:* `{{TAREA}}` sigue siendo texto libre en el
código (`emitir_arranque.py:159-160`) y quien lo teclea es el Arquitecto
(`docs/PROMPT_ARRANQUE_SESION.md:42`); la prohibición se hace cumplir **a ojo**
por el Director. Un validador en el emisor es candidato a una tanda posterior,
no a esta (regla de tandas ≤5).

### 9.5 Desfase nuevo — el Sintetizador desaparece; el empaquetado de F6 y el anti-bluff quedan sin dueño

La tabla de §3.4 daba al Sintetizador (Haiku) el empaquetado de F6 lanzado por
el Arquitecto. En v3.0 el Sintetizador **no figura** en §1 ni §2
(`:32-45`, `:133-141`) aunque el cuerpo lo siga nombrando (`:94-96`, `:162-167`,
`:221-223`, `:233`, `:444-445`). **Decisión r3:** la fila desaparece de la
frontera; en su lugar el anexo dice: «el empaquetador de F6 es un rol **sin
asignar** en v3.0; sea quien sea, **jamás lo lanza el Ingeniero** y el `git
diff` viaja íntegro». Quién empaqueta F6 y quién hace el anti-bluff formal de
las respuestas del Auditor es **deuda de documentación del Director** (cotejo
§C ampliado). Propuesta no vinculante para el anti-bluff de esta F2: el
**Verificador** (Opus 5, sesión nueva) — es el rol que juzga y no escribió el
diseño; el Arquitecto refutando hallazgos sobre su propio diseño roza la regla
de oro.

### 9.6 Desfase nuevo — Ruta B-chat bajo el emisor CLI

`resolver_insumo` mete el insumo como **ruta absoluta**
(`scripts/emitir_arranque.py:95-108`). Gemini no tiene disco: un
`bloque_auditor.txt` con una ruta es, para el Auditor, un bloque sin paquete.
**Regla de operación r3 (va a MT-T4, variante B-chat):** mensaje 1 = el bloque
emitido (identidad); mensaje 2 = el **contenido íntegro** del archivo insumo,
pegado por el Director. El `bloque_auditor.txt` que hay hoy en `bloques/`
(emitido 20:58, insumo `prompt_diseno_ronda1.md`) apunta al paquete
**desfasado** y debe reemitirse con el nuevo.

### 9.7 Lo que H-6 (rotación de transcripts) cambia en el plan

- **MT-T2 DoD (a)** se rebasa: reproducir literalmente las sesiones que **siguen
  en disco** (`a0b9d1eb`, `970c3ab4` ya cerrada con 133 turnos, `b26bb166`,
  `7a918db5`; cifras congeladas en `medicion_base_transcripts.md` §6) y el
  Verificador anota **cuáles existían** al ejecutar F5.
- **MT-T2 DoD (d)** (trampa H-5) se prueba con un **fixture sintético** de
  metadatos bajo `scripts/tests/fixtures/` — sin contenido real, porque el repo
  es público y porque ya no queda ningún subagente real.
- **MT-T5 / PO-3:** el bloque se genera al cierre, el mismo día.
- **Copia de seguridad recomendada al Director**, fuera del repo y nunca al
  expediente: `cp -r ~/.claude/projects/-home-pueblac-AndroidStudioProjects-NexoExpress ~/.claude/respaldo_nexo_2026-09-06` — preserva `a0b9d1eb` para PO-2
  aunque el cliente la rote antes de F4/F5. Reversible, impacto nulo.

### 9.8 Qué NO cambia en r3

El triángulo y la regla de oro (`:92`); §1.1 Asesor y su separación del Auditor;
§2 matriz y §2.1 escalada; §3.1 Paradas y §3.2 recalibración; §7.2 calibración
de `effort`; MT-T1 y PO-1 (cerradas); la evidencia de
`medicion_base_transcripts.md` §2 como registro; la decisión D3 (sólo el bloque
agregado se commitea) y D4 (no bloqueante — reforzada por H-6); D-e/E5 (campo
propio); la lista blanca fail-closed; la tanda 2 (Pre-F0) sigue fuera. La
«desviación de matriz» de F2 (Flash vs Pro) **desaparece**: la v3.0 fija Pro
High para F2 en toda complejidad (`:136`).

---

━━ AVISO DE TRASPASO ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CICLO      : 2026-08-11_traspaso_y_trazabilidad
FASE       : F1 — Diseño conceptual r3 (actualizado a v3.0; r2 congelada en §0–§8)
TURNO DE   : Arquitecto
MODELO     : Claude Fable 5.1 High
ENTREGAR   : auditorias/2026-08-11_traspaso_y_trazabilidad/diseno_f1.md
ADJUNTOS   : auditorias/2026-08-11_traspaso_y_trazabilidad/medicion_base_transcripts.md (§6 nuevo)
             auditorias/2026-08-11_traspaso_y_trazabilidad/prueba_traspaso.md
             auditorias/2026-08-11_traspaso_y_trazabilidad/desfase_v3_para_f1r3.md
DESTINO    : expediente del ciclo → prompt_diseno_ronda1_v3.md (F2, tanda 1)
ACCIÓN     : el Director lee §9.1 y §9.2 (las dos decisiones que son suyas) y
             sigue los pasos del AVISO de prompt_diseno_ronda1_v3.md
OBSERVABLE : Ninguno en esta fase. PO-1 ya se cobró; PO-2 llega con MT-T3
TRAZABILIDAD: sesión def5412c · claude-fable-5-1 × 33 turnos · effort high
             [medido del transcript, lectura ad-hoc — el script es F4]
             · fase F1 r3 · cotejo roster V3: OK
VUELVE A   : Director, para G1 sobre el veredicto de F2
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
