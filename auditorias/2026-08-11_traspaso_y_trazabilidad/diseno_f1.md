# Diseño conceptual F1 — Directriz de Traspaso (Rutas A y B) + Trazabilidad de Sesión

**Ciclo:** `2026-08-11_traspaso_y_trazabilidad`
**Productor:** Arquitecto Macro — Claude Opus 5, metodología v2.6
**Revisión:** **r2 — 11-08-2026, tras G0 concedido con enmiendas.**
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

━━ AVISO DE TRASPASO ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CICLO      : 2026-08-11_traspaso_y_trazabilidad
FASE       : F1 — Diseño conceptual r2 (CONGELADO tras G0 con enmiendas)
TURNO DE   : Arquitecto
MODELO     : Opus 5
ENTREGAR   : auditorias/2026-08-11_traspaso_y_trazabilidad/diseno_f1.md
ADJUNTOS   : auditorias/2026-08-11_traspaso_y_trazabilidad/medicion_base_transcripts.md
             auditorias/2026-08-11_traspaso_y_trazabilidad/prueba_traspaso.md
DESTINO    : expediente del ciclo → prompt_diseno_ronda1.md (F2, tanda 1)
ACCIÓN     : Arquitecto genera el prompt de revisión de DISEÑO de la tanda 1
             para Gemini 3.1 Pro High, conversación nueva. La tanda 2
             (Pre-F0 → v2.7, §8) lleva su propia ronda F1→F2, separada
OBSERVABLE : Ninguno en esta fase. Primera evidencia tocable: PO-1, con el
             bloque ya escrito en prueba_traspaso.md §1.2
TRAZABILIDAD: sesión 970c3ab4 · claude-opus-5 · effort high [medido del
             transcript] · fase F1 · bloque por lectura ad-hoc, no por
             scripts/analizar_sesion_ia.py (aún no existe — es F4)
VUELVE A   : Director, para G1 sobre el veredicto de F2
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
