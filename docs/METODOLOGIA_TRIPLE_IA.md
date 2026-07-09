# Metodología Triple-IA (v2) — Ecosistema Express

> **ESTADO: VIGENTE — adoptada el 09-07-2026 con aprobación del Director.**
> Revisión de diseño de Gemini 3.1 Pro High: **APROBADO CON CAMBIOS**
> (ronda 1, 08-07-2026 — expediente `auditorias/2026-07-08_metodologia_v2/`,
> respuesta validada anti-bluff); los 5 cambios obligatorios del dictamen y
> las recomendaciones Q1/Q3/D4 están incorporados. Sustituye a
> `METODOLOGIA_DUAL_IA.md` (v1), que se conserva como histórico y fallback
> operativo (§7) si la v2 falla en el piloto.
>
> **Origen:** evolución de la v1 (ciclo dual Claude↔Gemini, probado completo
> en `auditorias/2026-07-07_transcripcion_sintesis/`). Cambio central: el rol
> de Ingeniero se divide en **Arquitecto** (Fable 5) e **Ingeniero** (Claude
> Sonnet), creando un triángulo de verificación con el Auditor (Gemini).

---

## 1. Los Roles

| Rol | Quién | Responsabilidad |
|---|---|---|
| **Director / Auditor Técnico** | Pueblac (humano) | Define objetivos y prioridades, decide en los gates, **rota los artefactos entre modelos** (Modo M), da la aprobación FINAL. Nada se commitea sin su visto bueno. |
| **Arquitecto** | Claude Code (**Fable 5**) | Planes macro y descomposición en micro-tareas; diseño técnico; redacción del **Paquete de Especificación** para el Ingeniero; verificación independiente del trabajo del Ingeniero (re-ejecuta el DoD); generación de prompts de auditoría; **validación anti-bluff** de toda respuesta externa; custodia de gates y expedientes. **No implementa** las micro-tareas especificadas (salvo excepción del §7). |
| **Ingeniero** | Claude **Sonnet** | Implementa micro-tareas **exactamente según el Paquete de Especificación**. Corre las verificaciones del DoD y entrega **Informe de Implementación** con salida literal. Si la spec es ambigua: pregunta, nunca supone (regla "duda = pregunta"). No diseña, no amplía alcance, no se autovalida con autoridad final. |
| **Auditor Externo** | Gemini 3.1 Pro High | Revisa el DISEÑO antes del código y audita el CÓDIGO después, bajo contrato adversarial (citas obligatorias, trazas, trampas). Siempre en conversación nueva. |
| **Innovador** | Skill `innovador` | Detecta mejoras fuera del plan. Propone, nunca implementa. |
| **Depurador de Agentes** | Skill `depurador_agentes` (la invoca el Director) | Detecta bucles de error/alucinación en **cualquiera de las tres IAs** y prescribe la intervención. |

### Triángulo de verificación (regla de oro, heredada y extendida)

**Ninguna IA verifica su propio trabajo con autoridad final.**

- El **Arquitecto** valida al Ingeniero (re-ejecuta el DoD sobre el código
  real, no sobre el informe) y valida al Auditor (anti-bluff).
- El **Auditor** valida al Arquitecto (revisión adversarial del diseño) y al
  Ingeniero (auditoría adversarial del código).
- El **Ingeniero** no valida a nadie, pero su Informe declara dudas propias
  que dirigen la auditoría (herencia OPCG).
- El **Director** arbitra todo conflicto y es el único que aprueba adopción
  de diseño y commits.

Límite conocido del triángulo: el Arquitecto redacta la spec, verifica la
implementación **y** redacta el prompt de auditoría — es el nodo con más
poder de filtrado (duda D1 del expediente, confirmada por el Auditor en
ronda 1). Neutralización ESTRUCTURAL (dictamen r1, cambio 1): el `git diff`
literal del Informe de Implementación viaja íntegro y sin filtrar al
prompt de auditoría — el Arquitecto no puede ocultar archivos modificados
al Auditor, que rechaza como INVÁLIDO todo prompt sin diff estructurado.
Complementos: artefactos archivados literales en el expediente y
spot-checks del Director.

---

## 2. El Ciclo v2 (obligatorio para todo cambio no trivial)

Cada fase termina con **un artefacto de traspaso** archivado y un **AVISO**
explícito (formato en §4) que dice a quién le toca y con qué. Sin AVISO, la
fase no está cerrada.

```
F0. PLAN         Arquitecto (+ roadmap_manager) descompone la meta en
                 micro-tareas con DoD → checklist en estado_actual.md.
                 ── GATE G0: Director aprueba el plan y prioridades. ──
F1. DISEÑO       Arquitecto produce el diseño técnico + prompt de revisión
                 de DISEÑO → expediente.  AVISO → Director → Auditor.
F2. VEREDICTO    Auditor responde (conversación nueva). Director archiva la
                 respuesta literal. Arquitecto ejecuta ANTI-BLUFF.
                 "APROBADO CON CAMBIOS" = incorporar los cambios.
                 "RECHAZADO" = rediseñar (volver a F1, ronda nueva).
                 ── GATE G1: Director adopta el veredicto. ──
F3. SPEC         Arquitecto redacta el Paquete de Especificación de cada
                 micro-tarea (autocontenido, ver §3) → expediente.
                 AVISO → Director → Ingeniero.
F4. IMPLEMENTAR  Ingeniero implementa FIEL a la spec, corre TODAS las
                 verificaciones del DoD (+ prueba A/B cuando proteja un
                 fix) y entrega Informe de Implementación con salida
                 literal + dudas propias.  AVISO → Director → Arquitecto.
F5. VERIFICAR    Arquitecto verifica el trabajo SOBRE EL CÓDIGO REAL:
                 EJECUTA los comandos del DoD (terminal de Claude Code;
                 si el entorno no permite ejecución, el Director o un
                 CI los corre y entrega stdout/stderr literal). Leer el
                 informe NO es verificar (dictamen r1, cambio 3).
                 Contrasta salida real vs informe (anti-bluff interno)
                 y confirma fidelidad al diseño aprobado. Desviación o
                 DoD no reproducible → devolver a F4 con nota de
                 rechazo (cuenta para la regla anti-bucle).
F6. AUDITORÍA    Arquitecto genera el prompt de auditoría de CÓDIGO
                 (CLAIM → EVIDENCIA archivo:línea → TRAZA → VERDICTO),
                 integrando las dudas del Ingeniero y las propias, e
                 incrustando ÍNTEGRO y SIN FILTRAR el git diff del
                 Informe de Implementación (dictamen r1, cambio 1). El
                 Auditor rechaza como "INVÁLIDO: posible orquestación
                 adversarial" todo prompt de auditoría sin diff
                 estructurado.
                 AVISO → Director → Auditor. Respuesta → ANTI-BLUFF del
                 Arquitecto. BUG confirmado → F4 (fix) → ronda NUEVA.
F7. CIERRE       Con APROBADO del Auditor Y aprobación del Director:
                 ── GATE G2: Director autoriza commit + push. ──
                 Mensaje referenciando el ciclo; bitácora y estado
                 actualizados (documentador_sesion).
```

**Gates humanos (G0, G1, G2):** son del Director en ambos modos de operación
(§5) y no se automatizan jamás. Los pasos que dependen del Director son
cortes de sesión válidos: el artefacto + AVISO quedan listos y la sesión
puede cerrarse sin trabajo a medias.

**Cambios triviales** (typo, texto de UI, doc): no requieren ciclo completo,
pero sí aprobación del Director antes de commit (herencia v1).

---

## 3. Artefactos de traspaso

Todos viven en `auditorias/{YYYY-MM-DD}_{tema}/` (expediente = memoria
jurídica del ecosistema). Nomenclatura por rondas heredada de v1
(`prompt_{fase}_rondaN.md` / `respuesta_{fase}_rondaN.md`).

| Fase | Artefacto | Archivo | Productor → Consumidor |
|---|---|---|---|
| F0 | Checklist de micro-tareas con DoD | `docs/estado_actual.md` | Arquitecto → Director |
| F1 | Prompt de revisión de diseño | `prompt_diseno_rondaN.md` | Arquitecto → Auditor |
| F2 | Veredicto + validación anti-bluff | `respuesta_diseno_rondaN.md` (+ anexo de validación) | Auditor → Arquitecto |
| F3 | **Paquete de Especificación** | `spec_mtNN.md` | Arquitecto → Ingeniero |
| F4 | **Informe de Implementación** | `informe_mtNN.md` | Ingeniero → Arquitecto |
| F5 | Verificación del Arquitecto | anexo en `informe_mtNN.md` | Arquitecto → expediente |
| F6 | Prompt/respuesta de auditoría de código | `prompt_auditoria_rondaN.md` / `respuesta_auditoria_rondaN.md` | Arquitecto ↔ Auditor |
| F7 | Evidencia de cierre | `evidencia_mtNN.md` | Arquitecto → Director |

### 3.1 Paquete de Especificación (`spec_mtNN.md`) — contrato Arquitecto → Ingeniero

**Autocontenido:** el Ingeniero arranca en conversación/contexto nuevo y no
puede depender de nada que no esté en la spec o en el repo. Secciones
obligatorias:

1. **Objetivo** (1–3 líneas) y micro-tarea del checklist a la que responde.
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
   inyectaría decisiones de diseño invisibles para F5/F6 (dictamen r1, Q3).
7. **AVISO de traspaso** (§4).

### 3.2 Informe de Implementación (`informe_mtNN.md`) — contrato Ingeniero → Arquitecto

1. **Qué se hizo**: archivos tocados/creados con resumen por archivo.
2. **Diff literal** (dictamen r1, cambio 1): bloque con el output ÍNTEGRO
   de `git diff` + `git status`, sin edición manual. Este bloque viaja TAL
   CUAL al prompt de auditoría de F6 — el Arquitecto no elige qué archivos
   ve el Auditor. Sin diff, el informe es INVÁLIDO.
3. **Evidencia literal**: salida REAL de cada comando del DoD (copiada, no
   resumida). Sin evidencia literal, el informe es INVÁLIDO.
4. **Desviaciones**: cualquier diferencia respecto a la spec, con razón.
   Desviación no declarada detectada en F5 = entrega rechazada.
5. **Dudas del Ingeniero**: puntos de menor certeza (alimentan el prompt de
   auditoría de F6).
6. **Estado commiteable**: confirmación de que todo queda verde, nada a
   medias.
7. **AVISO de traspaso** (§4).

---

## 4. AVISO de traspaso (obligatorio al final de TODO artefacto)

Bloque estándar, literal, al final de cada artefacto. Diseñado para que el
Director pueda rotar la información **sin leer el artefacto completo**:

```
━━ AVISO DE TRASPASO ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CICLO      : {expediente, p. ej. 2026-07-08_metodologia_v2}
FASE       : {F0..F7} — {nombre}
TURNO DE   : {Director | Arquitecto | Ingeniero | Auditor}
ENTREGAR   : {ruta(s) exacta(s) del artefacto a transportar}
ADJUNTOS   : {lista exacta de archivos del repo / git diff que
              viajan CON el artefacto, o "Ninguno"}
DESTINO    : {dónde pegarlo/adjuntarlo: chat nuevo de Gemini /
              sesión de Sonnet / sesión del Arquitecto}
ACCIÓN     : {qué debe hacer quien recibe, en 1 línea}
VUELVE A   : {rol que recibe el resultado} con {qué archivo se
              archiva y con qué nombre}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Reglas del AVISO:
- **Un artefacto sin AVISO no cierra fase.**
- **`ADJUNTOS` es exhaustivo** (dictamen r1, cambio 4): lo listado es
  obligatorio transportarlo; lo no listado no se adjunta. Es lo único que
  el Director necesita leer para rotar sin abrir el artefacto.
- Cada rol **verifica que el artefacto recibido le corresponde** (campo
  `TURNO DE`). Si un rol recibe un artefacto ajeno (p. ej. el Ingeniero
  recibe un prompt de auditoría), lo rechaza con una línea y sin ejecutarlo.
  Este rechazo solo puede operar si la sesión fue inicializada con su rol
  (ver Inicialización de identidad, §5).
- En Modo M el `DESTINO` es una instrucción de operación para el Director;
  en Modo A es la llamada que hace el orquestador.

---

## 5. Modos de operación

### Modo M — Manual (DEFAULT y único modo del piloto)

El Director transporta cada artefacto entre las tres IAs:
- **Arquitecto**: sesión de Claude Code con Fable 5 (este repo).
- **Ingeniero**: sesión de Claude (Sonnet) separada — conversación nueva por
  micro-tarea, recibe SOLO el Paquete de Especificación (+ repo).
- **Auditor**: conversación NUEVA de Gemini por ronda, sin herencia de hilo.

**Inicialización de identidad (obligatoria, dictamen r1, cambio 2):** toda
sesión nueva de Ingeniero o Auditor arranca con un prompt de rol de una
línea ANTES del primer artefacto, p. ej.:

> "Rol: Ingeniero del ciclo {expediente}, metodología v2 del ecosistema
> Express. Confirma recepción sin accionar; acepta únicamente artefactos
> cuyo campo TURNO DE diga Ingeniero."

Sin esta inicialización, la regla de rechazo de artefactos ajenos (§4) no
tiene base para operar: un modelo en contexto cero no sabe qué rol funge.

**Working tree limpio (dictamen r1, D4):** F4 arranca sobre la rama base
sin cambios sin commitear de otras micro-tareas — la conversación nueva
aísla el contexto, no el sistema de archivos. Una MT en vuelo a la vez por
componente (serialización estricta).

Costo asumido: toil humano de rotación. Beneficio: el Director ve pasar
todos los artefactos (supervisión total) y cada IA queda aislada de verdad.

### Modo A — Automatizado (variante propuesta, NO habilitada; requiere ciclo propio)

El Arquitecto orquesta desde Claude Code: lanza al Ingeniero como
**subagente Sonnet** (contexto limpio, recibe solo la spec) y llama al
Auditor **vía API de Gemini**. El humano interviene únicamente en los gates
G0, G1 y G2.

Evaluación del Arquitecto (para el veredicto del Auditor):

| Aspecto | Modo M | Modo A |
|---|---|---|
| Toil del Director | Alto (cada traspaso) | Solo gates |
| Aislamiento de contexto | Real (sesiones separadas) | Real para subagentes (contexto limpio), PERO el orquestador compone los prompts de todos |
| Riesgo de filtrado/colusión | Bajo (Director ve todo) | **Alto**: el nodo con más poder (Arquitecto) controla qué ve el Auditor |
| Detección de degeneración a modo chat del Auditor | Director la ve en vivo | Solo detectable post-hoc en la respuesta archivada |
| Prerrequisitos | Ninguno | API key de Gemini + **gobernanza del tier pendiente** (privacidad; hoy tier gratuito en `gen-lang-client-0046942155`), costos de API |

**Salvaguardas mínimas si algún día se habilita Modo A** (condición
necesaria, no suficiente — exige su propio ciclo de diseño):
1. Todo prompt enviado y toda respuesta recibida se archivan **literales**
   en el expediente ANTES de que el Arquitecto los procese.
2. El Director hace spot-check de al menos 1 traspaso por ciclo.
3. Los gates G0/G1/G2 siguen siendo humanos y bloqueantes.
4. La regla anti-bucle aplica al orquestador: 2 rondas automatizadas sin
   converger → STOP y reporte al Director.

**Decisión de este borrador:** el piloto de la v2 (MT-04) corre en **Modo M
exclusivamente**. Modo A queda documentado como propuesta evaluada y
pendiente de: gobernanza del tier de Gemini + ciclo de diseño propio.

---

## 6. Reglas no negociables (herencia v1 + nuevas)

Heredadas de v1 sin cambio (siguen aplicando tal cual):
- **Micro-tareas** (§3 de la v1): ≤30–45 min, UN entregable verificable,
  DoD escrito ANTES, sistema commiteable al terminar, checklist en
  `estado_actual.md`, tandas ≤5 para auditoría, 1–3 micro-ciclos por sesión.
- **Evidencia** (§4 de la v1): estado final observable, salida literal,
  prueba A/B para tests que protegen fixes, dudas declaradas, schema
  centralizado primero.
- **Anti-bluff** a toda respuesta del Auditor (checklist de la skill
  `auditor_externo`): citas verificadas con grep/ejecución, sin citas =
  INVÁLIDA con frase de devolución, BUG confirmado = ronda nueva.
- **Anti-bucle**: 2 intentos del mismo fix fallando → STOP y reporte.
  Sospecha de bucle/alucinación en cualquiera de las TRES IAs → el Director
  invoca `depurador_agentes`.
- **Nada se commitea sin aprobación explícita del Director.**

Nuevas en v2:
- **Fidelidad a la spec**: el Ingeniero no redefine contrato, alcance ni
  DoD. Toda desviación se declara en el Informe; una desviación no
  declarada invalida la entrega.
- **Duda = pregunta**: ambigüedad en la spec se devuelve como duda, nunca
  se resuelve con un supuesto silencioso.
- **Verificación del Arquitecto (F5) obligatoria y al 100%** (sin muestreo,
  dictamen r1, Q1): los comandos del DoD se EJECUTAN sobre el código real
  (terminal del Arquitecto; en su defecto, Director o CI entregan
  stdout/stderr literal) antes de generar el prompt de auditoría. Leer el
  informe no es verificar. El informe del Ingeniero nunca se reenvía al
  Auditor como evidencia — al Auditor llegan claims + el git diff ÍNTEGRO +
  código fuente, jamás prosa del implementador.
- **Diff sin filtrar** (dictamen r1, cambio 1): el bloque `git diff`
  literal del Informe de Implementación se incrusta completo en el prompt
  de auditoría de F6. El Auditor rechaza como INVÁLIDO todo prompt de
  auditoría de código sin diff estructurado.
- **AVISO de traspaso obligatorio** al cierre de todo artefacto (§4), con
  campo `ADJUNTOS` exhaustivo.
- **Inicialización de identidad** en toda sesión nueva de Ingeniero/Auditor
  (§5) — prerrequisito del rechazo de artefactos ajenos.
- **Working tree limpio antes de F4** y una MT en vuelo por componente
  (§5, dictamen r1, D4).

---

## 7. Excepciones y degradación a v1

- **Micro-tarea trivial-técnica** (p. ej. un rename guiado, un doc): el
  Director puede autorizar que el Arquitecto la implemente directamente
  (colapso Arquitecto=Ingeniero → el ciclo degrada a v1 para esa MT). Debe
  quedar anotado en el checklist: `[modo v1 autorizado por el Director]`.
- **Indisponibilidad de un modelo**: si Sonnet no está disponible, el ciclo
  degrada a v1 (Fable implementa) con anotación en la bitácora. Si Gemini
  no está disponible, NO hay cierre de ciclo: la sesión corta en el
  artefacto pendiente.
- La v1 (`METODOLOGIA_DUAL_IA.md`) se conserva como documento histórico y
  fallback; tras adoptarse la v2, MT-02 elimina referencias huérfanas en
  los documentos operativos (prompt de arranque, skills) para que ninguna
  sesión futura ejecute el ciclo equivocado por accidente.

---

## 8. Mapa de skills en el ciclo v2

| Momento | Skill | Nota v2 |
|---|---|---|
| F0 (descomponer/priorizar) | `roadmap_manager` | MT-02: actualizar referencia al ciclo |
| F1, F2, F6 (prompts + anti-bluff) | `auditor_externo` | MT-02: la ejecuta el **Arquitecto**; añadir F5 y artefactos spec/informe |
| Cierre de sesión | `documentador_sesion` | sin cambio |
| Fuera de plan | `innovador` | sin cambio |
| IA en bucle | `depurador_agentes` | cubre a las TRES IAs (ya lo hace por diseño) |
| Cambios de datos | `arquitecto_firebase` | el schema se toca en F1/F3, nunca en F4 |
| Paridad Web/Android | `auditor_paridad` | sin cambio |

---

## 9. Adopción

1. ✅ Revisión de diseño del Auditor completada: **APROBADO CON CAMBIOS**
   (ronda 1, 08-07-2026), respuesta validada anti-bluff y los 5 cambios
   incorporados a este documento (expediente
   `auditorias/2026-07-08_metodologia_v2/`).
2. Con la aprobación del Director → la v2 entra en vigor y se ejecuta
   INMEDIATAMENTE la limpieza documental MT-02 (actualizar
   `PROMPT_ARRANQUE_SESION.md`, skills `auditor_externo` y
   `roadmap_manager`, README regla 5; cero referencias huérfanas al ciclo
   v1 en documentos operativos).
3. **MT-02 es BLOQUEANTE** (dictamen r1, cambio 5): el piloto NO arranca
   su F0 hasta que la limpieza documental esté hecha — impide que una
   sesión ejecute v1 por inercia de documentos desactualizados.
4. **Piloto:** MT-04 de ActaExpressWeb (frontend envía
   `generarSintesis: true`; UX del toggle la decide el Director), en Modo M.
5. Retro del piloto en bitácora: qué fase costó más, si el tamaño de
   micro-tarea necesita recalibrarse (el dictamen r1/D3 sostiene que la
   spec es la entrega primaria de F1–F3, no overhead — verificarlo en la
   práctica), y si Modo A amerita su ciclo de diseño.
