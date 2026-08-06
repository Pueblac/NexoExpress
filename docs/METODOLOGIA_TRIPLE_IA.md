# Metodología Triple-IA v2.5 (Optimizada) — Ecosistema Express

> **ESTADO: VIGENTE v2.5 Optimizada — adoptada el 06-08-2026 con aprobación
> del Director.** Metodología única y predominante del ecosistema Express:
> no existen fallbacks ni metodologías alternativas. Todo cambio no trivial
> del ecosistema recorre este ciclo y solo este ciclo.
>
> **Linaje:** la v2 (adoptada 09-07-2026; revisión de diseño de Gemini
> **APROBADO CON CAMBIOS** r1, expediente
> `auditorias/2026-07-08_metodologia_v2/`, con los 5 cambios obligatorios y
> Q1/Q3/D4 incorporados) probó el ciclo F0–F7 en siete ciclos completos.
> La v2.5 conserva íntegra esa maquinaria (fases, artefactos, AVISO, gates,
> anti-bluff) y **optimiza la asignación de modelos por complejidad y el
> gasto de tokens**. La metodología heredada anterior a la v2 fue eliminada
> del repositorio el 06-08-2026; sus expedientes históricos en `auditorias/`
> y las bitácoras conservan su valor como memoria jurídica, pero ningún
> documento operativo la referencia ya como flujo ejecutable.

---

## 1. Los Roles (por modelo y parámetros)

| Rol | Quién | Configuración | Fases | Responsabilidad |
|---|---|---|---|---|
| **Director / Auditor Técnico** | Pueblac (humano) | — | Gates G0, G1, G2 | Define la visión y prioridades, autoriza los gates, **rota los artefactos entre modelos** (Modo M), arbitra conflictos y da la aprobación FINAL. Nada se commitea sin su visto bueno. |
| **Arquitecto Macro / Estratega** | Claude **Fable 5** | `effort: low` o `medium` | **F0 y F1** | Planificación macro, descomposición estratégica en micro-tareas con DoD, diseño conceptual de arquitectura y schemas, clasificación de complejidad de cada MT (§2). Entregables **breves de alta inteligencia**: decide mucho, escribe poco. Custodia de expedientes y del checklist. |
| **Especificador y Diseñador Técnico** | Claude **Sonnet 5** | `effort: high` | **F3; F5 en Alta** | Redacción del **Paquete de Especificación** detallado (`spec_mtNN.md`): contratos de API, schemas aplicados, extractos de código contextuales verificados. La spec es la entrega primaria del diseño — aquí SÍ se gasta detalle. En complejidad **Alta** ejecuta además la verificación F5 (juicio semántico sobre el código real, §2.1). |
| **Ingeniero Adaptativo** | Claude **Sonnet 5** o Claude **Haiku 4.5** | Sonnet: estándar. Haiku: `thinking: enabled` si aplica | **F4** | Implementación FIEL a la spec. Criterio de selección: **Sonnet 5** para tareas complejas o refactorizaciones pesadas; **Haiku 4.5** para micro-tareas, UI fixes, typos, scripts simples o tests unitarios. La selección la fija la matriz de complejidad (§2) en G0. |
| **Sintetizador y Anti-Bluff Interno** | Claude **Haiku 4.5** | Estándar | **F5 (Media/Baja) y preparación de F6** | Re-ejecución determinista de las verificaciones del DoD sobre el código real (en Media/Baja; la F5 de Alta es de Sonnet, §2.1), parseo del `git diff` literal, verificación formal de citas (anti-bluff mecánico) y **empaquetado del prompt estructurado de auditoría** para Gemini (en TODA complejidad). No emite juicios de diseño: ante ambigüedad, ESCALA (§2.1). |
| **Auditor Externo Adversarial** | **Gemini 3.1 Pro High** o **Gemini Flash** | Conversación NUEVA (contexto cero) | **F2 y F6** | Auditoría adversarial del DISEÑO antes del código y del CÓDIGO después, bajo contrato de citas obligatorias, trazas y trampas. **Gemini 3.1 Pro High** para arquitectura, seguridad, core y SIEMPRE la Ronda 1 de F6; **Gemini Flash** solo para rondas 2+ (verificación de fixes) o complejidad Baja (§2). |
| **Innovador** | Skill `innovador` | — | fuera de ciclo | Detecta mejoras fuera del plan. Propone, nunca implementa. |
| **Depurador de Agentes** | Skill `depurador_agentes` (la invoca el Director) | — | a demanda | Detecta bucles de error/alucinación en **cualquiera de las IAs del ciclo** y prescribe la intervención. |

### Triángulo de verificación (regla de oro)

**Ninguna IA verifica su propio trabajo con autoridad final.**

- El **Verificador de F5** (Sonnet 5 `effort: high` en Alta; el
  Sintetizador Haiku en Media/Baja) verifica al Ingeniero re-ejecutando el
  DoD sobre el código real. El **Sintetizador** verifica además
  formalmente al Auditor (citas y salidas literales, anti-bluff mecánico).
- El **Auditor** (Gemini) valida al Arquitecto (revisión adversarial del
  diseño en F2) y al Ingeniero/Especificador (auditoría adversarial del
  código en F6).
- El **Ingeniero** no valida a nadie, pero su Informe declara dudas propias
  que dirigen la auditoría.
- El **Arquitecto** (Fable) arbitra las escaladas técnicas (§2.1) y las
  refutaciones de BUGs alegados: un BUG solo se refuta con evidencia
  archivo:línea producida por Fable o Sonnet `effort: high`, nunca por el
  Sintetizador en solitario.
- El **Director** arbitra todo conflicto y es el único que aprueba adopción
  de diseño y commits.

Límite conocido y su neutralización (heredados de la auditoría de la v2 y
aún vigentes): el nodo que redacta el prompt de auditoría podría filtrar lo
que ve el Auditor. Neutralización ESTRUCTURAL: el `git diff` literal del
Informe de Implementación viaja íntegro y sin filtrar dentro del prompt de
F6 — el empaquetador no elige qué archivos ve el Auditor, que rechaza como
INVÁLIDO todo prompt sin diff estructurado. En v2.5 el riesgo baja además
porque el empaquetador (Haiku, F6) y el diseñador (Fable, F1) son roles
separados. Complementos: artefactos archivados literales en el expediente y
spot-checks del Director.

Trade-off aceptado en v2.5 (declarado): en complejidad Alta/Media el
Especificador y el Ingeniero son el mismo modelo (Sonnet 5) en **sesiones
separadas con contexto cero**. El aislamiento es de contexto, no de pesos;
lo compensan el DoD determinista de F5 (Haiku) y la auditoría externa
cross-vendor de F6 (Gemini).

---

## 2. Matriz de asignación por complejidad de la micro-tarea

La complejidad de cada micro-tarea la **clasifica el Arquitecto en F0** y la
**ratifica el Director en G0**, antes de F3. Queda anotada en el checklist
(`[Alta]` / `[Media]` / `[Baja]`). En caso de duda entre dos niveles, se
asigna el superior.

| Complejidad | Ejemplos | Spec (F3) | Impl (F4) | Verif (F5) | Audit (F2/F6) |
|---|---|---|---|---|---|
| **Alta** | Core, algoritmos RAG, schema Firestore, pipeline de IA | Sonnet 5 (`effort: high`) | **Sonnet 5** | **Sonnet 5** (`effort: high`) | **Gemini 3.1 Pro High** |
| **Media** | UI features, handlers de API, integraciones | Sonnet 5 (`effort: high`) | **Sonnet 5** | Haiku 4.5 | F2: **Flash** · F6 r1: **Gemini 3.1 Pro High** · F6 r2+: **Flash** |
| **Baja / Trivial** | CSS, fixes simples, docs, types | Sonnet 5 (`effort: high`) | **Haiku 4.5** | Haiku 4.5 | **Gemini Flash** |

Notas de aplicación:

- **Rondas de F6:** la Ronda 1 de auditoría de código usa SIEMPRE
  **Gemini 3.1 Pro High**, incluso en complejidad Media — la primera
  mirada adversarial al código no se abarata. **Gemini Flash** queda
  autorizado únicamente para rondas 2+ (verificación de fixes) o para
  complejidad Baja.
- **F0/F1 (Fable) aplican a toda meta**; la ronda de diseño F1→F2 es
  obligatoria en Alta y Media. En **Baja**, el Director puede autorizar en
  G0 colapsar F1/F2 (sin ronda de diseño externa) — la MT pasa de G0
  directo a F3; F5 y F6 siguen siendo obligatorias.
- **Cambio trivial atómico** (typo, una línea de doc, texto de UI): el
  Director puede autorizar la **vía rápida v2.5** — ejecución directa en la
  sesión activa sin ciclo completo, con anotación en el checklist
  `[vía rápida v2.5 autorizada por el Director]` y aprobación del Director
  antes de commit. Es la única excepción al ciclo y es parte de la v2.5,
  no una metodología distinta.
- **Indisponibilidad de un modelo:** el Director decide la sustitución
  dentro de la tabla de roles (p. ej. Sonnet cae → Fable `effort: medium`
  especifica; Haiku cae → Sonnet verifica). Si Gemini no está disponible,
  NO hay cierre de ciclo: la sesión corta en el artefacto pendiente. La
  sustitución se anota en la bitácora.

### 2.1 Regla de escalada (nueva en v2.5)

Ningún rol resuelve en silencio algo que excede su capacidad o su mandato.
La cadena de escalada es **Haiku → Sonnet (`effort: high`) → Fable →
Director**, siempre mediante artefacto (nota en el informe o anexo en el
expediente), nunca por decisión inline:

- **F5 en complejidad Alta la ejecuta Sonnet 5 (`effort: high`), no
  Haiku:** el juicio semántico sobre el código real (fidelidad al diseño
  aprobado, efectos que el DoD no evidencia — precedente: el bug de diseño
  contra Radix cazado en el F5 del ciclo basurero) no se delega al
  Sintetizador. Haiku 4.5 mantiene F5 en Media y Baja, y conserva en TODA
  complejidad el empaquetado determinista de F6 (parseo del diff,
  ensamblado del prompt).
- El **Sintetizador** (F5 Media/Baja) que encuentra una discrepancia no determinista
  (el DoD pasa pero el comportamiento no coincide con la spec, o una cita
  del Auditor es formalmente correcta pero semánticamente dudosa) la escala
  a Sonnet/Fable; jamás la aprueba ni la refuta solo.
- El **Ingeniero Haiku** (F4 en Baja) que encuentra que la tarea era más
  compleja de lo clasificado DETIENE y devuelve la MT para reclasificar
  (reabre G0 de esa MT), no improvisa.
- Una **refutación de BUG** alegado por el Auditor exige evidencia
  archivo:línea de Fable o Sonnet `effort: high` (precedente: BUG 3 del
  ciclo selector, refutado con `useMicLevel.ts:32`).

---

## 3. El Ciclo v2.5 (obligatorio para todo cambio no trivial)

Cada fase termina con **un artefacto de traspaso** archivado y un **AVISO**
explícito (formato en §5) que dice a quién le toca y con qué. Sin AVISO, la
fase no está cerrada.

```
F0. PLAN         Arquitecto (Fable, effort low/medium; + roadmap_manager)
                 descompone la meta en micro-tareas con DoD y CLASIFICA la
                 complejidad de cada una (§2) → checklist en
                 estado_actual.md.
                 ── GATE G0: Director aprueba plan, prioridades y
                    clasificación de complejidad. ──
F1. DISEÑO       Arquitecto (Fable) produce el diseño conceptual —
                 arquitectura, schemas, decisiones estratégicas; breve y
                 denso — + prompt de revisión de DISEÑO → expediente.
                 AVISO → Director → Auditor.
                 (En Baja, F1/F2 pueden colapsar por autorización de G0.)
F2. VEREDICTO    Auditor (Gemini Pro High / Flash según §2) responde en
                 conversación nueva. Director archiva la respuesta literal.
                 Anti-bluff: verificación formal por el Sintetizador;
                 disputas semánticas escalan a Fable (§2.1).
                 "APROBADO CON CAMBIOS" = incorporar los cambios.
                 "RECHAZADO" = rediseñar (volver a F1, ronda nueva).
                 ── GATE G1: Director adopta el veredicto. ──
F3. SPEC         Especificador (Sonnet 5, effort high) redacta el Paquete
                 de Especificación de cada micro-tarea (autocontenido, §4)
                 a partir del diseño aprobado → expediente.
                 AVISO → Director → Ingeniero.
F4. IMPLEMENTAR  Ingeniero (Sonnet 5 o Haiku 4.5 según §2) implementa FIEL
                 a la spec, corre TODAS las verificaciones del DoD (+ prueba
                 A/B cuando proteja un fix) y entrega Informe de
                 Implementación con salida literal + dudas propias.
                 AVISO → Director → Sintetizador.
F5. VERIFICAR    Verificador según §2 — en Alta: Sonnet 5 (effort high),
                 que preserva el juicio SEMÁNTICO sobre el código real;
                 en Media/Baja: Sintetizador (Haiku 4.5). Verifica SOBRE
                 EL CÓDIGO REAL: EJECUTA los comandos del DoD (si el
                 entorno no permite ejecución, el Director o un CI los
                 corre y entrega stdout/stderr literal). Leer el informe
                 NO es verificar. Contrasta salida real vs informe
                 (anti-bluff interno), parsea el git diff literal y
                 confirma fidelidad a la spec (formal en Media/Baja;
                 también semántica en Alta). Discrepancia no determinista
                 en Media/Baja → ESCALADA (§2.1).
                 Desviación o DoD no reproducible → devolver a F4 con nota
                 de rechazo (cuenta para la regla anti-bucle).
F6. AUDITORÍA    Sintetizador (Haiku 4.5) empaqueta el prompt de auditoría
                 de CÓDIGO (CLAIM → EVIDENCIA archivo:línea → TRAZA →
                 VERDICTO) según la skill auditor_externo: claims del
                 diseño aprobado, dudas del Ingeniero y del ciclo, trampas,
                 e incrusta ÍNTEGRO y SIN FILTRAR el git diff del Informe
                 de Implementación. El Auditor rechaza como "INVÁLIDO:
                 posible orquestación adversarial" todo prompt sin diff
                 estructurado.
                 AVISO → Director → Auditor. RONDA 1: SIEMPRE Gemini 3.1
                 Pro High (incluso en Media; Baja puede usar Flash desde
                 r1). Flash solo en rondas 2+ de verificación de fixes.
                 Respuesta → anti-bluff (formal: Haiku; refutaciones:
                 Fable/Sonnet, §2.1). BUG confirmado → F4 (fix) → ronda
                 NUEVA.
F7. CIERRE       Con APROBADO del Auditor Y aprobación del Director:
                 ── GATE G2: Director autoriza commit + push. ──
                 Mensaje referenciando el ciclo; bitácora y estado
                 actualizados (documentador_sesion).
```

**Gates humanos (G0, G1, G2):** son del Director en ambos modos de operación
(§6) y no se automatizan jamás. Los pasos que dependen del Director son
cortes de sesión válidos: el artefacto + AVISO quedan listos y la sesión
puede cerrarse sin trabajo a medias.

---

## 4. Artefactos de traspaso

Todos viven en `auditorias/{YYYY-MM-DD}_{tema}/` (expediente = memoria
jurídica del ecosistema). Nomenclatura por rondas
(`prompt_{fase}_rondaN.md` / `respuesta_{fase}_rondaN.md`).

| Fase | Artefacto | Archivo | Productor → Consumidor |
|---|---|---|---|
| F0 | Checklist de micro-tareas con DoD + complejidad | `docs/estado_actual.md` | Arquitecto → Director |
| F1 | Diseño + prompt de revisión de diseño | `prompt_diseno_rondaN.md` | Arquitecto → Auditor |
| F2 | Veredicto + validación anti-bluff | `respuesta_diseno_rondaN.md` (+ anexo de validación) | Auditor → Sintetizador/Arquitecto |
| F3 | **Paquete de Especificación** | `spec_mtNN.md` | Especificador → Ingeniero |
| F4 | **Informe de Implementación** | `informe_mtNN.md` | Ingeniero → Sintetizador |
| F5 | Verificación F5 | anexo en `informe_mtNN.md` | Verificador (Sonnet en Alta / Haiku en Media-Baja) → expediente |
| F6 | Prompt/respuesta de auditoría de código | `prompt_auditoria_rondaN.md` / `respuesta_auditoria_rondaN.md` | Sintetizador ↔ Auditor |
| F7 | Evidencia de cierre | `evidencia_mtNN.md` | Arquitecto → Director |

### 4.1 Paquete de Especificación (`spec_mtNN.md`) — contrato Especificador → Ingeniero

**Autocontenido:** el Ingeniero arranca en conversación/contexto nuevo y no
puede depender de nada que no esté en la spec o en el repo. Secciones
obligatorias:

1. **Objetivo** (1–3 líneas), micro-tarea del checklist a la que responde y
   **complejidad asignada** (determina el modelo Ingeniero, §2).
2. **Contexto mínimo verificado**: rutas exactas, extractos literales del
   código actual relevante, decisiones del diseño aprobado que aplican
   (citando el dictamen del expediente).
3. **Contrato**: firmas, campos, tipos, rutas de API/colecciones — lo que el
   código DEBE exponer. Cambios de datos citan `schemas/firestore_schema.md`
   ya actualizado (regla de schema centralizado: el schema se toca en
   F1/F3, nunca lo decide el Ingeniero).
4. **Restricciones**: qué NO tocar, límites (p. ej. anti-bucle, presupuesto
   de tokens, "sin dependencias nuevas").
5. **DoD ejecutable**: comandos/observaciones EXACTOS que demuestran que
   está terminada (estado final observable, jamás "corrió sin errores").
   Incluye la prueba A/B si la micro-tarea protege un fix.
6. **Protocolo de dudas**: "si algo es ambiguo, DETENTE y devuelve la duda
   en el Informe; implementar sobre un supuesto no declarado invalida la
   entrega." Una duda devuelta **reabre F3 (ronda nueva de spec, F3')**:
   el Director NO media con respuestas puntuales fuera de artefactos —
   inyectaría decisiones de diseño invisibles para F5/F6.
7. **AVISO de traspaso** (§5).

### 4.2 Informe de Implementación (`informe_mtNN.md`) — contrato Ingeniero → Sintetizador

1. **Qué se hizo**: archivos tocados/creados con resumen por archivo.
2. **Diff literal**: bloque con el output ÍNTEGRO de `git diff` +
   `git status`, sin edición manual. Este bloque viaja TAL CUAL al prompt
   de auditoría de F6 — nadie elige qué archivos ve el Auditor. Sin diff,
   el informe es INVÁLIDO.
3. **Evidencia literal**: salida REAL de cada comando del DoD (copiada, no
   resumida). Sin evidencia literal, el informe es INVÁLIDO.
4. **Desviaciones**: cualquier diferencia respecto a la spec, con razón.
   Desviación no declarada detectada en F5 = entrega rechazada.
5. **Dudas del Ingeniero**: puntos de menor certeza (alimentan el prompt de
   auditoría de F6).
6. **Estado commiteable**: confirmación de que todo queda verde, nada a
   medias.
7. **AVISO de traspaso** (§5).

---

## 5. AVISO de traspaso (obligatorio al final de TODO artefacto)

Bloque estándar, literal, al final de cada artefacto. Diseñado para que el
Director pueda rotar la información **sin leer el artefacto completo**:

```
━━ AVISO DE TRASPASO ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CICLO      : {expediente, p. ej. 2026-08-06_metodologia_v25}
FASE       : {F0..F7} — {nombre}
TURNO DE   : {Director | Arquitecto | Especificador | Ingeniero |
              Sintetizador | Auditor}
MODELO     : {Fable 5 | Sonnet 5 (effort high) | Haiku 4.5 |
              Gemini 3.1 Pro High | Gemini Flash} — según §2
ENTREGAR   : {ruta(s) exacta(s) del artefacto a transportar}
ADJUNTOS   : {lista exacta de archivos del repo / git diff que
              viajan CON el artefacto, o "Ninguno"}
DESTINO    : {dónde pegarlo/adjuntarlo: chat nuevo de Gemini /
              sesión del modelo indicado}
ACCIÓN     : {qué debe hacer quien recibe, en 1 línea}
VUELVE A   : {rol que recibe el resultado} con {qué archivo se
              archiva y con qué nombre}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Reglas del AVISO:
- **Un artefacto sin AVISO no cierra fase.**
- **`ADJUNTOS` es exhaustivo**: lo listado es obligatorio transportarlo; lo
  no listado no se adjunta. Es lo único que el Director necesita leer para
  rotar sin abrir el artefacto.
- **`MODELO` es vinculante** (nuevo en v2.5): indica al Director qué modelo
  y configuración abrir para la fase siguiente, según la matriz §2.
- Cada rol **verifica que el artefacto recibido le corresponde** (campo
  `TURNO DE`). Si un rol recibe un artefacto ajeno (p. ej. el Ingeniero
  recibe un prompt de auditoría), lo rechaza con una línea y sin ejecutarlo.
  Este rechazo solo puede operar si la sesión fue inicializada con su rol
  (ver Inicialización de identidad, §6).
- En Modo M el `DESTINO` es una instrucción de operación para el Director;
  en Modo A es la llamada que hace el orquestador.

---

## 6. Modos de operación

### Modo M — Manual (DEFAULT)

El Director transporta cada artefacto entre las IAs:
- **Arquitecto**: sesión de Claude Code con Fable 5 (este repo),
  `effort: low/medium`.
- **Especificador**: sesión de Claude Sonnet 5 (`effort: high`) —
  conversación nueva por meta, recibe el diseño aprobado + repo.
- **Ingeniero**: sesión nueva del modelo que fije la matriz §2 (Sonnet 5 o
  Haiku 4.5) por micro-tarea; recibe SOLO el Paquete de Especificación
  (+ repo). Práctica consolidada: **rotación asistida** — el Arquitecto
  lanza al Ingeniero como subagente con contexto limpio y la spec
  archivada, manteniendo el aislamiento de contexto sin toil de copiado.
- **Sintetizador**: sesión/subagente Haiku 4.5 por verificación.
- **Auditor**: conversación NUEVA de Gemini por ronda (Pro High o Flash
  según §2), sin herencia de hilo.

**Inicialización de identidad (obligatoria):** toda sesión nueva de
Especificador, Ingeniero, Sintetizador o Auditor arranca con un prompt de
rol de una línea ANTES del primer artefacto, p. ej.:

> "Rol: {Especificador | Ingeniero | Sintetizador | Auditor} del ciclo
> {expediente}, metodología v2.5 del ecosistema Express. Confirma recepción
> sin accionar; acepta únicamente artefactos cuyo campo TURNO DE diga
> {rol}."

Sin esta inicialización, la regla de rechazo de artefactos ajenos (§5) no
tiene base para operar: un modelo en contexto cero no sabe qué rol funge.

**Working tree limpio:** F4 arranca sobre la rama base sin cambios sin
commitear de otras micro-tareas — la conversación nueva aísla el contexto,
no el sistema de archivos. Una MT en vuelo a la vez por componente
(serialización estricta).

Costo asumido: toil humano de rotación (mitigado por la rotación asistida).
Beneficio: el Director ve pasar todos los artefactos (supervisión total) y
cada IA queda aislada de verdad.

### Modo A — Automatizado (variante propuesta, NO habilitada; requiere ciclo propio)

El Arquitecto orquesta desde Claude Code: lanza Especificador, Ingeniero y
Sintetizador como subagentes (contexto limpio, reciben solo su artefacto) y
llama al Auditor **vía API de Gemini**. El humano interviene únicamente en
los gates G0, G1 y G2.

**Salvaguardas mínimas si algún día se habilita** (condición necesaria, no
suficiente — exige su propio ciclo de diseño):
1. Todo prompt enviado y toda respuesta recibida se archivan **literales**
   en el expediente ANTES de que el orquestador los procese.
2. El Director hace spot-check de al menos 1 traspaso por ciclo.
3. Los gates G0/G1/G2 siguen siendo humanos y bloqueantes.
4. La regla anti-bucle aplica al orquestador: 2 rondas automatizadas sin
   converger → STOP y reporte al Director.

Pendiente de: gobernanza del tier de Gemini (privacidad; hoy tier gratuito
en `gen-lang-client-0046942155`) + ciclo de diseño propio.

---

## 7. Estrategia de optimización de tokens (nueva en v2.5)

La v2.5 existe para gastar la inteligencia donde rinde y ahorrarla donde no.
Dos palancas:

### 7.1 Prompt Caching (obligatorio para contexto base)

Los archivos de contexto base que viajan repetidamente entre fases y
sesiones (`ECOSISTEMA_VISION.md`, `schemas/firestore_schema.md`, esta
metodología, el diseño aprobado del ciclo) se tratan como **bloques
cacheables**:

- **Vía API / subagentes / Modo A:** marcar los bloques repetitivos con
  `cache_control: {"type": "ephemeral"}` al final del bloque estable del
  prompt. El contexto base va PRIMERO y el contenido volátil (artefacto de
  la fase, pregunta concreta) va DESPUÉS — un solo byte cambiado invalida
  la caché de todo lo que le sigue.
- **En sesiones de Claude Code / chat:** la caché es automática, pero la
  disciplina es la misma: contexto estable al inicio de la sesión, de una
  vez y sin re-pegarlo después; los artefactos volátiles se referencian
  por ruta del repo, no incrustados de nuevo.
- Regla práctica: si un bloque va a viajar ≥2 veces en el ciclo, es
  candidato a caché; si se incrusta dos veces a mano, es un defecto de
  operación.

### 7.2 Calibración del parámetro `effort`

`effort` controla cuánto razonamiento interno gasta el modelo antes de
responder. Se calibra **por la irreversibilidad de la decisión, no por el
largo del documento**:

| Configuración | Cuándo | Por qué |
|---|---|---|
| Fable `effort: low` | F0 rutinario, clasificación de complejidad, arbitrajes simples | La inteligencia base de Fable basta; pagar razonamiento extra es sobre-gasto. |
| Fable `effort: medium` | F1 con decisiones de arquitectura o schema nuevas | Decisión irreversible y cara de corregir aguas abajo. |
| Sonnet `effort: high` | F3 (siempre), F5 en Alta y refutaciones de BUG (§2.1) | La spec es el contrato del que depende todo F4–F6; la F5 de Alta exige juicio semántico; un supuesto malo aquí cuesta un ciclo entero. |
| Sonnet estándar | F4 complejo | Implementar contra una spec buena no exige razonamiento máximo. |
| Haiku (`thinking: enabled` si aplica) | F4 Baja, F5 Media/Baja, empaquetado F6 | Trabajo determinista y mecánico; thinking solo si la tarea tiene pasos encadenados. |

Anti-patrones de gasto (prohibidos): Fable redactando specs detalladas o
implementando (eso es de Sonnet/Haiku); Sonnet `effort: high` para typos o
CSS; re-pegar contexto ya cacheado; rondas 2+ de verificación de fixes con
Pro High cuando Flash basta (ojo: la Ronda 1 de F6 es SIEMPRE Pro High
salvo en Baja — abaratarla no es optimización, es hueco de auditoría).

---

## 8. Reglas no negociables

- **Micro-tareas**: ≤30–45 min, UN entregable verificable, DoD escrito
  ANTES, sistema commiteable al terminar, checklist en `estado_actual.md`,
  tandas ≤5 para auditoría, 1–3 micro-ciclos por sesión.
- **Evidencia**: estado final observable con salida literal (jamás "corrió
  sin errores"), prueba A/B para todo test que proteja un fix, dudas
  declaradas, schema centralizado primero (`schemas/firestore_schema.md`
  se actualiza en F1/F3, nunca lo decide el Ingeniero).
- **Anti-bluff** a toda respuesta del Auditor (checklist de la skill
  `auditor_externo`): citas verificadas con grep/ejecución; sin citas =
  INVÁLIDA con frase de devolución; BUG confirmado = ronda nueva; BUG
  refutado solo con evidencia archivo:línea de Fable/Sonnet (§2.1).
- **Anti-bucle**: 2 intentos del mismo fix fallando → STOP y reporte.
  Sospecha de bucle/alucinación en cualquiera de las IAs → el Director
  invoca `depurador_agentes`.
- **Nada se commitea sin aprobación explícita del Director** (gate G2).
- **Fidelidad a la spec**: el Ingeniero no redefine contrato, alcance ni
  DoD. Toda desviación se declara en el Informe; una desviación no
  declarada invalida la entrega.
- **Duda = pregunta**: ambigüedad en la spec se devuelve como duda, nunca
  se resuelve con un supuesto silencioso. Una duda reabre F3'.
- **Verificación F5 obligatoria y al 100%** (sin muestreo): los comandos
  del DoD se EJECUTAN sobre el código real antes de generar el prompt de
  auditoría. Leer el informe no es verificar. El informe del Ingeniero
  nunca se reenvía al Auditor como evidencia — al Auditor llegan claims +
  el git diff ÍNTEGRO + código fuente, jamás prosa del implementador.
- **Diff sin filtrar**: el bloque `git diff` literal del Informe de
  Implementación se incrusta completo en el prompt de auditoría de F6. El
  Auditor rechaza como INVÁLIDO todo prompt de auditoría de código sin
  diff estructurado.
- **AVISO de traspaso obligatorio** al cierre de todo artefacto (§5), con
  campos `ADJUNTOS` exhaustivo y `MODELO` vinculante.
- **Inicialización de identidad** en toda sesión nueva de rol (§6) —
  prerrequisito del rechazo de artefactos ajenos.
- **Working tree limpio antes de F4** y una MT en vuelo por componente (§6).
- **Escalada por artefacto, nunca inline** (§2.1): ningún rol resuelve en
  silencio lo que excede su capacidad o mandato.

---

## 9. Mapa de skills en el ciclo v2.5

| Momento | Skill | Nota v2.5 |
|---|---|---|
| F0 (descomponer/priorizar/clasificar) | `roadmap_manager` | añade la clasificación de complejidad (§2) al checklist |
| F1, F2, F6 (prompts + anti-bluff) | `auditor_externo` | F1 la ejecuta el Arquitecto; el empaquetado F6 lo ejecuta el Sintetizador con la misma plantilla; anti-bluff formal Haiku, refutaciones Fable/Sonnet |
| Cierre de sesión | `documentador_sesion` | sin cambio |
| Fuera de plan | `innovador` | sin cambio |
| IA en bucle | `depurador_agentes` | cubre a TODAS las IAs del ciclo (ya lo hace por diseño) |
| Cambios de datos | `arquitecto_firebase` | el schema se toca en F1/F3, nunca en F4 |
| Paridad Web/Android | `auditor_paridad` | sin cambio |

---

## 10. Adopción

1. ✅ **v2 adoptada el 09-07-2026** (auditada por Gemini: APROBADO CON
   CAMBIOS r1, 5 cambios incorporados; expediente
   `auditorias/2026-07-08_metodologia_v2/`) y probada en **siete ciclos
   completos** (MT-04 piloto → selector de micrófono, cierre 04-08-2026).
2. ✅ **v2.5 Optimizada adoptada el 06-08-2026** por orden directa del
   Director: reasignación de roles por modelo/parámetros (§1), matriz de
   complejidad (§2), estrategia de tokens (§7) y **eliminación de toda
   metodología heredada** — la limpieza documental se ejecutó el mismo día
   (metodología heredada borrada del repo; prompt de arranque, skills,
   README y estado actualizados; cero referencias operativas huérfanas).
3. ✅ **Ajustes del Director al conceder G2 (06-08-2026):** (a) F5 de
   complejidad Alta la ejecuta Sonnet 5 `effort: high` — el precedente del
   bug de diseño contra Radix (F5 del ciclo basurero) motivó no delegar el
   juicio semántico a Haiku; (b) la Ronda 1 de F6 usa SIEMPRE Gemini 3.1
   Pro High, Flash solo rondas 2+ o Baja.
4. **Primer ciclo bajo v2.5:** el próximo G0 de la fila del Director
   (acta persistente → página de Configuración → billing/Vertex). Retro en
   bitácora al cierre: si la matriz de complejidad clasificó bien, si F5
   con Haiku en Media/Baja sostiene el nivel, y si el ahorro de tokens es
   medible.
