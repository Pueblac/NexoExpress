# Metodología Triple-IA v2.6 (Enfoque Pedagógico, Asesor del Director y Paradas de Observación) — Ecosistema Express

> **ESTADO: VIGENTE v2.6 — adoptada el 09-08-2026 por orden del Director.**
> Metodología única y predominante del ecosistema Express: no existen
> fallbacks ni metodologías alternativas. Todo cambio no trivial del
> ecosistema recorre este ciclo y solo este ciclo.
>
> **Linaje:** la v2 (adoptada 09-07-2026; revisión de diseño de Gemini
> **APROBADO CON CAMBIOS** r1, expediente
> `auditorias/2026-07-08_metodologia_v2/`) probó el ciclo F0–F7 en siete
> ciclos completos. La v2.5 (06-08-2026) conservó esa maquinaria y optimizó
> la asignación de modelos por complejidad y el gasto de tokens. La **v2.6
> conserva íntegras ambas** (fases, artefactos, AVISO, gates, anti-bluff,
> matriz de complejidad, estrategia de tokens) y añade cuatro cosas que
> atacan un mismo problema: **que el Director pueda decidir de verdad en los
> gates, sin tener que leer el código.**
>
> **Qué añade la v2.6:**
> 1. El **Asesor Estratégico del Director** (§1.1): un traductor pedagógico
>    y copiloto del Director en los gates.
> 2. La **Regla de Glosa Pedagógica Inline** (§4.3): todo término técnico
>    complejo en specs e informes lleva su analogía en lenguaje ordinario, y
>    toda decisión que se pide al Director se reduce al eje
>    **reversibilidad × impacto de negocio**.
> 3. Las **Paradas de Observación con Evidencia Comprobable** (§3.1): en
>    proyectos con UI, datos o indicadores, F0 predeclara qué va a poder
>    **ver y tocar** el Director, y cuándo.
> 4. El **Protocolo de Recalibración Dinámica de Evidencia**
>    (F3′ / Mini-Gate G0′, §3.2): qué hacer cuando en pleno F4/F5 se
>    descubre que el prototipo o el indicador estaban mal especificados,
>    sin que eso degenere en deriva de alcance.
>
> **Por qué:** el ciclo v2.5 demostró que produce código sólido, pero
> también que un Director que no lee `executor.py` línea a línea acaba
> aprobando por confianza en vez de por criterio. Un gate humano que se
> concede sin entender lo que se concede es un trámite, no un control.
>
> **Sustitución de modelo vigente desde el 10-08-2026** (mecanismo del §2,
> "Indisponibilidad de un modelo" — no es una versión nueva de la
> metodología): Anthropic cambió las condiciones de acceso a **Fable 5**,
> así que el Arquitecto Macro pasa a **Opus 5**. El Director no se limitó a
> un reemplazo 1:1 y escaló también los roles de mayor juicio del ciclo;
> detalle completo y justificación en §10, punto 7.

---

## 1. Los Roles (por modelo y parámetros)

| Rol | Quién | Configuración | Fases | Responsabilidad |
|---|---|---|---|---|
| **Director / Auditor Técnico** | Pueblac (humano) | — | Gates G0, G0′, G1, G2 | Define la visión y prioridades, autoriza los gates, **rota los artefactos entre modelos** (Modo M), arbitra conflictos y da la aprobación FINAL. Nada se commitea sin su visto bueno. |
| **Asesor Estratégico del Director** | **Gemini 3.6 Flash** (en Antigravity) | Conversación propia, separada de la del Auditor | **Gates G0, G0′, G1, G2** (a demanda del Director) | Traductor pedagógico y copiloto. Explica al Director qué está aprobando, en lenguaje ordinario, y le devuelve la decisión reducida al eje **reversibilidad × impacto**. **No decide, no vota, no produce artefactos del expediente.** Ver §1.1. |
| **Arquitecto Macro / Estratega** | Claude **Opus 5** | `effort: low` o `medium` | **F0 y F1** | Planificación macro, descomposición en micro-tareas con DoD, diseño conceptual, clasificación de complejidad (§2) y **predeclaración de las Paradas de Observación** (§3.1). Entregables **breves de alta inteligencia**: decide mucho, escribe poco. Custodia de expedientes y del checklist. |
| **Especificador y Diseñador Técnico** | Claude **Opus 5** (Alta) o Claude **Sonnet 5** (Media/Baja) | `effort: high` | **F3; F5 en Alta** | Redacción del **Paquete de Especificación** (`spec_mtNN.md`): contratos, schemas aplicados, extractos verificados, **glosa pedagógica inline** (§4.3). En complejidad **Alta**, el mismo rol (Opus) ejecuta además la verificación F5 — juicio semántico sobre el código real. |
| **Ingeniero** | Claude **Sonnet 5** | Estándar | **F4, toda complejidad** | Implementación FIEL a la spec. Desde el 10-08 es un rol único, sin split por complejidad (antes Sonnet/Haiku según §2) — ver §10.7. |
| **Sintetizador y Anti-Bluff Interno** | Claude **Haiku 4.5** | Estándar | **F5 (Media/Baja) y preparación de F6** | Re-ejecución determinista del DoD sobre el código real, parseo del `git diff` literal, verificación formal de citas y **empaquetado del prompt de auditoría** para Gemini. No emite juicios de diseño: ante ambigüedad, ESCALA (§2.1). |
| **Auditor Externo Adversarial** | **Gemini 3.1 Pro High** o **Gemini Flash** | Conversación NUEVA (contexto cero) | **F2 y F6** | Auditoría adversarial del DISEÑO antes del código y del CÓDIGO después, bajo contrato de citas, trazas y trampas. **Pro High** para arquitectura, seguridad, core y SIEMPRE la Ronda 1 de F6; **Flash** solo rondas 2+ o complejidad Baja (§2). |
| **Innovador** | Skill `innovador` | — | fuera de ciclo | Detecta mejoras fuera del plan. Propone, nunca implementa. |
| **Depurador de Agentes** | Skill `depurador_agentes` (la invoca el Director) | — | a demanda | Detecta bucles de error/alucinación en **cualquiera de las IAs del ciclo** y prescribe la intervención. |

### 1.1 Asesor Estratégico del Director (nuevo en v2.6)

**Problema que resuelve.** El Director aprueba gates sobre artefactos
escritos por y para máquinas. Cuando el artefacto es una spec de seguridad
de 16 KB, la opción realista deja de ser "aprobar o rechazar con criterio" y
pasa a ser "aprobar por confianza". Eso convierte el gate en un trámite.

**Qué hace.** A petición del Director, y **solo en los gates**, el Asesor:

1. Explica en lenguaje ordinario qué se está aprobando y qué cambia si se
   aprueba.
2. Traduce los términos técnicos con analogías, sin exigir del Director
   vocabulario previo.
3. Reduce la decisión al eje **reversibilidad × impacto de negocio**
   (§4.3): *¿cuánto cuesta deshacer esto?* y *¿a quién afecta si sale mal?*
4. Señala qué preguntas convendría hacerle al Arquitecto **antes** de
   conceder el gate.

**Qué NO hace, y esto es vinculante:**

- **No decide ni vota.** Su salida es una explicación, no un veredicto. La
  decisión del gate se registra siempre con la razón **del Director**, en
  sus palabras, nunca con "según el Asesor".
- **No produce artefactos del expediente.** Nada de lo que escriba entra en
  `auditorias/` como evidencia. Si el Director quiere conservar una
  explicación, la pega en la bitácora, no en el expediente del ciclo.
- **No sustituye la lectura del AVISO** (§5). El AVISO es el mínimo
  irreductible que el Director lee siempre.
- **Nunca comparte conversación con el Auditor.** Ambos son Gemini; si el
  Asesor y el Auditor conviven en un hilo, la auditoría adversarial queda
  contaminada por el encuadre del asesor. **Conversaciones separadas,
  siempre.**
- **No participa en el anti-bluff** ni en ninguna verificación. No es un
  nodo del triángulo (abajo).

**Riesgo asumido y declarado:** un asesor complaciente puede capturar el
gate de facto — si el Director decide con lo que el Asesor le cuenta, quien
manda es el Asesor. Neutralización: (a) la glosa pedagógica es
**responsabilidad del rol que produce el artefacto** (§4.3), no del Asesor,
de modo que el Director tiene siempre una explicación de origen distinto
con la que contrastar; (b) la decisión se registra con la razón del
Director; (c) el Asesor no ve nunca las respuestas del Auditor antes que el
Director.

### Triángulo de verificación (regla de oro)

**Ninguna IA verifica su propio trabajo con autoridad final.**

- El **Verificador de F5** (Opus 5 `effort: high` en Alta; el Sintetizador
  Haiku en Media/Baja) verifica al Ingeniero re-ejecutando el DoD sobre el
  código real. El **Sintetizador** verifica además formalmente al Auditor.
- El **Auditor** (Gemini) valida al Arquitecto (F2) y al
  Ingeniero/Especificador (F6).
- El **Ingeniero** no valida a nadie, pero su Informe declara dudas propias
  que dirigen la auditoría.
- El **Arquitecto** (Opus) arbitra las escaladas técnicas (§2.1) y las
  refutaciones de BUGs: un BUG solo se refuta con evidencia archivo:línea
  producida por Opus — el Arquitecto en F0/F1 o el mismo Opus en su rol de
  Verificador de F5-Alta. El Ingeniero (Sonnet) no puede refutar hallazgos
  sobre código que él mismo escribió (sigue siendo la regla de oro).
- El **Director** arbitra todo conflicto y es el único que aprueba adopción
  de diseño y commits.
- El **Asesor** (§1.1) **no forma parte del triángulo**: no verifica a
  nadie ni es verificado. Es un intérprete al servicio del Director.

Límite conocido y su neutralización: el nodo que redacta el prompt de
auditoría podría filtrar lo que ve el Auditor. Neutralización ESTRUCTURAL:
el `git diff` literal del Informe viaja íntegro y sin filtrar dentro del
prompt de F6 — el empaquetador no elige qué archivos ve el Auditor, que
rechaza como INVÁLIDO todo prompt sin diff estructurado. Complementos:
artefactos archivados literales y spot-checks del Director.

Trade-off heredado, parcialmente resuelto por la sustitución del 10-08
(§10.7): en **Alta**, Especificador/Verificador (Opus) e Ingeniero (Sonnet)
son ahora modelos distintos — el trade-off que v2.5 declaró y aceptó
**desaparece para esa franja**. En **Media/Baja** persiste: el Especificador
y el Ingeniero siguen siendo el mismo modelo (Sonnet 5) en **sesiones
separadas con contexto cero**. El aislamiento sigue siendo de contexto, no
de pesos; lo compensan el DoD determinista de F5 y la auditoría externa
cross-vendor de F6.

---

## 2. Matriz de asignación por complejidad de la micro-tarea

La complejidad la **clasifica el Arquitecto en F0** y la **ratifica el
Director en G0**, antes de F3. Queda anotada en el checklist (`[Alta]` /
`[Media]` / `[Baja]`). En caso de duda entre dos niveles, se asigna el
superior.

| Complejidad | Ejemplos | Spec (F3) | Impl (F4) | Verif (F5) | Audit (F2/F6) |
|---|---|---|---|---|---|
| **Alta** | Core, algoritmos RAG, schema Firestore, pipeline de IA | **Opus 5** (`effort: high`) | **Sonnet 5** | **Opus 5** (`effort: high`) | **Gemini 3.1 Pro High** |
| **Media** | UI features, handlers de API, integraciones | Sonnet 5 (`effort: high`) | **Sonnet 5** | Haiku 4.5 | F2: **Flash** · F6 r1: **Gemini 3.1 Pro High** · F6 r2+: **Flash** |
| **Baja / Trivial** | CSS, fixes simples, docs, types | Sonnet 5 (`effort: high`) | **Sonnet 5** | Haiku 4.5 | **Gemini Flash** |

Notas de aplicación:

- **Rondas de F6:** la Ronda 1 usa SIEMPRE **Gemini 3.1 Pro High**, incluso
  en Media — la primera mirada adversarial al código no se abarata.
  **Flash** solo para rondas 2+ o complejidad Baja.
- **F0/F1 (Opus) aplican a toda meta**; la ronda de diseño F1→F2 es
  obligatoria en Alta y Media. En **Baja**, el Director puede autorizar en
  G0 colapsar F1/F2 — la MT pasa de G0 directo a F3; F5 y F6 siguen siendo
  obligatorias.
- **Cambio trivial atómico** (typo, una línea de doc, texto de UI): el
  Director puede autorizar la **vía rápida** — ejecución directa sin ciclo
  completo, con anotación en el checklist
  `[vía rápida v2.6 autorizada por el Director]` y aprobación antes de
  commit. Es la única excepción al ciclo.
- **Indisponibilidad de un modelo:** el Director decide la sustitución
  dentro de la tabla de roles. Si Gemini no está disponible, NO hay cierre
  de ciclo: la sesión corta en el artefacto pendiente. Se anota en bitácora.
  (Precedente: la sustitución de Fable por Opus del 10-08-2026, §10.7.)
- **Indisponibilidad del Asesor:** no bloquea nada. El gate se concede igual
  con el AVISO y la glosa pedagógica del propio artefacto (§4.3), que es lo
  que garantiza que el Director pueda decidir aunque el Asesor no esté.

### 2.1 Regla de escalada

Ningún rol resuelve en silencio algo que excede su capacidad o su mandato.
La cadena es **Haiku → Sonnet → Opus → Director**, siempre mediante
artefacto, nunca por decisión inline — con una excepción: **Sonnet nunca
resuelve ni refuta una ambigüedad o un BUG sobre una micro-tarea que él
mismo implementó como Ingeniero.** Ahí la cadena salta directo a Opus,
porque desde el 10-08 Sonnet es exclusivamente el Ingeniero, y el Ingeniero
no verifica su propio trabajo con autoridad final (regla de oro, arriba).

- **F5 en complejidad Alta la ejecuta Opus 5 (`effort: high`), no Haiku ni
  Sonnet:** el juicio semántico sobre el código real no se delega al
  Sintetizador, y el Ingeniero no verifica lo que implementó. Haiku
  mantiene F5 en Media y Baja, y conserva en TODA complejidad el
  empaquetado determinista de F6.
- El **Sintetizador** que encuentra una discrepancia no determinista la
  escala a Opus; jamás la aprueba ni la refuta solo.
- El **Ingeniero** (F4, toda complejidad, siempre Sonnet desde el 10-08)
  que encuentra que la tarea era más compleja de lo clasificado DETIENE y
  devuelve la MT para reclasificar (reabre G0 de esa MT), no improvisa.
- Una **refutación de BUG** exige evidencia archivo:línea de Opus — el
  Arquitecto o el Verificador de F5-Alta — nunca de Sonnet, que en su
  calidad de Ingeniero no puede refutar hallazgos sobre código que él mismo
  escribió.
- **Nuevo en v2.6:** cualquier rol que detecte que la **evidencia
  observable** predeclarada en F0 (§3.1) ya no se sostiene, DETIENE y abre
  una **Solicitud de Recalibración** (§3.2). No la sustituye por otra
  evidencia por su cuenta.

---

## 3. El Ciclo v2.6 (obligatorio para todo cambio no trivial)

Cada fase termina con **un artefacto de traspaso** archivado y un **AVISO**
explícito (§5). Sin AVISO, la fase no está cerrada.

```
F0. PLAN         Arquitecto (Opus, effort low/medium; + roadmap_manager)
                 descompone la meta en micro-tareas con DoD, CLASIFICA la
                 complejidad de cada una (§2) y PREDECLARA la Parada de
                 Observación de la meta (§3.1) → checklist en
                 estado_actual.md.
                 ── GATE G0: Director aprueba plan, prioridades,
                    clasificación de complejidad y la evidencia
                    observable que se le promete. ──
F1. DISEÑO       Arquitecto (Opus) produce el diseño conceptual +
                 prompt de revisión de DISEÑO → expediente.
                 AVISO → Director → Auditor.
                 (En Baja, F1/F2 pueden colapsar por autorización de G0.)
F2. VEREDICTO    Auditor (Gemini Pro High / Flash según §2) responde en
                 conversación nueva. Director archiva la respuesta literal.
                 Anti-bluff: verificación formal por el Sintetizador;
                 disputas semánticas escalan a Opus (§2.1).
                 "APROBADO CON CAMBIOS" = incorporar los cambios.
                 "RECHAZADO" = rediseñar (volver a F1, ronda nueva).
                 ── GATE G1: Director adopta el veredicto. ──
F3. SPEC         Especificador (Opus 5 en Alta / Sonnet 5 en Media-Baja,
                 effort high) redacta el Paquete de Especificación de cada
                 micro-tarea (autocontenido, §4.1) CON glosa pedagógica
                 inline (§4.3) → expediente.
                 AVISO → Director → Ingeniero.
F4. IMPLEMENTAR  Ingeniero (Sonnet 5, toda complejidad desde el 10-08)
                 implementa FIEL a la spec, corre TODAS las verificaciones
                 del DoD (+ prueba A/B cuando proteja un fix) y entrega
                 Informe de Implementación con salida literal + dudas
                 propias + glosa.
                 Si la evidencia observable predeclarada no se sostiene →
                 Solicitud de Recalibración (§3.2), no improvisación.
                 AVISO → Director → Verificador.
F5. VERIFICAR    Verificador según §2 — Alta: Opus 5 (effort high), que
                 preserva el juicio SEMÁNTICO; Media/Baja: Sintetizador
                 (Haiku 4.5). Verifica SOBRE EL CÓDIGO REAL: EJECUTA los
                 comandos del DoD. Leer el informe NO es verificar.
                 Contrasta salida real vs informe, parsea el git diff
                 literal y confirma fidelidad a la spec. Discrepancia no
                 determinista en Media/Baja → ESCALADA (§2.1).
                 Evidencia observable insostenible → Recalibración (§3.2).
                 Desviación o DoD no reproducible → devolver a F4 con nota
                 de rechazo (cuenta para la regla anti-bucle).
                 ── PARADA DE OBSERVACIÓN: el Director ve y toca lo
                    predeclarado en F0, antes de gastar la auditoría. ──
F6. AUDITORÍA    Sintetizador (Haiku 4.5) empaqueta el prompt de auditoría
                 de CÓDIGO (CLAIM → EVIDENCIA archivo:línea → TRAZA →
                 VERDICTO) según la skill auditor_externo, e incrusta
                 ÍNTEGRO y SIN FILTRAR el git diff del Informe. El Auditor
                 rechaza como "INVÁLIDO: posible orquestación adversarial"
                 todo prompt sin diff estructurado.
                 AVISO → Director → Auditor. RONDA 1: SIEMPRE Gemini 3.1
                 Pro High. Flash solo rondas 2+ o Baja.
                 Respuesta → anti-bluff (formal: Haiku; refutaciones:
                 Opus, §2.1). BUG confirmado → F4 (fix) → ronda NUEVA.
F7. CIERRE       Con APROBADO del Auditor Y aprobación del Director:
                 ── GATE G2: Director autoriza commit + push. ──
                 Mensaje referenciando el ciclo; bitácora y estado
                 actualizados (documentador_sesion).
```

**Gates humanos (G0, G0′, G1, G2):** son del Director en ambos modos de
operación (§6) y no se automatizan jamás. Los pasos que dependen del
Director son cortes de sesión válidos: el artefacto + AVISO quedan listos y
la sesión puede cerrarse sin trabajo a medias. En cualquiera de ellos el
Director puede convocar al **Asesor** (§1.1).

### 3.1 Paradas de Observación con Evidencia Comprobable (nuevo en v2.6)

**El problema.** Un ciclo puede recorrer F0→F6 entero, con DoD verde y
auditoría aprobada, y dejar al Director sin haber visto nunca **nada**. El
código correcto no es lo mismo que el producto correcto, y solo el Director
sabe si lo segundo se cumplió.

**La regla.** Para toda meta que toque **UI, datos o indicadores**, la F0
debe **predeclarar** el resultado físico observable por el Director:

1. **Qué va a ver o tocar** — un prototipo navegable, una pantalla real, un
   documento generado, una consulta con su salida, un número en un panel.
   Descrito en una frase, sin jerga.
2. **Cuándo** — en qué punto del ciclo estará disponible. Por defecto **al
   cerrar F5**, antes de gastar la auditoría de F6: no tiene sentido pagar
   una auditoría de código sobre algo que el Director va a pedir cambiar.
3. **Cómo se comprueba** — los pasos exactos que el Director dará para
   verlo (URL, comando, dónde hacer clic). Si el Director no puede
   ejecutarlo solo, no es una Parada de Observación válida.
4. **Qué haría falta para declararla fallida** — el criterio de rechazo,
   escrito antes de construir nada. Sin esto, cualquier resultado se
   racionaliza como éxito.

Se registra en el checklist de `estado_actual.md` junto a la micro-tarea, y
se aprueba en **G0** como parte del plan: el Director aprueba también **qué
se le promete enseñar**.

**Metas exentas:** infraestructura pura sin efecto observable (por ejemplo,
el núcleo de ejecución de un orquestador). La exención **se declara
explícitamente en F0 y la ratifica el Director en G0** — no se asume por
omisión. Una meta sin Parada de Observación y sin exención declarada **no
pasa G0**.

**Límite conocido y heredado:** cuando la evidencia observable exige
hardware o presencia humana (un micrófono, un dispositivo Android), la
Parada **es bloqueante** y no se puede automatizar. El ciclo se detiene ahí
hasta que el Director la ejecute. Es un corte de sesión válido, no un fallo.

### 3.2 Protocolo de Recalibración Dinámica de Evidencia — F3′ / Mini-Gate G0′ (nuevo en v2.6)

**El problema.** A veces se descubre en pleno F4 o F5 que el prototipo
predeclarado no demuestra lo que se creía, o que el indicador elegido mide
otra cosa. Las dos salidas espontáneas son malas: seguir con una evidencia
que no prueba nada (teatro), o cambiarla sobre la marcha (deriva de alcance
sin control).

**La regla.** Quien lo detecte —Ingeniero, Verificador o Arquitecto—
**DETIENE** y emite una **Solicitud de Recalibración**
(`solicitud_recalibracion_mtNN.md` en el expediente), con cuatro campos y
nada más:

1. **Qué se predeclaró en F0** — cita literal.
2. **Por qué no se sostiene** — con evidencia ejecutada, no con opinión.
   La misma exigencia que el resto del ciclo: se demuestra, no se afirma.
3. **Qué se propone en su lugar** — una alternativa única y concreta, con
   sus pasos de comprobación. Nada de "podríamos hacer A o B".
4. **Impacto**, en el eje del §4.3: cuánto cambia el alcance, si es
   reversible, y a qué afecta en el producto.

**Mini-Gate G0′.** El Director aprueba, rechaza o modifica la
recalibración. Es un gate **humano y bloqueante** como los demás, pero de
alcance reducido: solo decide sobre la evidencia observable, **no reabre el
diseño ni la spec**. Su resolución se anota en el checklist junto a la MT.

Reglas de aplicación:

- **Solo la evidencia, nunca el alcance.** Si al recalibrar aparece que
  también hay que cambiar el contrato o el diseño, eso **no** es G0′: es
  F3′ (spec nueva) o vuelta a F1, según corresponda. Recalibrar la
  evidencia no es la puerta trasera para ampliar el trabajo.
- **Anti-bucle:** dos recalibraciones sobre la misma micro-tarea → STOP y
  reporte al Director. Si la evidencia hay que redefinirla dos veces, el
  problema está en F0, no en la evidencia.
- **Trazabilidad:** la solicitud y su resolución quedan en el expediente
  aunque se rechacen. Una recalibración rechazada es información valiosa
  sobre la calidad de la predeclaración.

---

## 4. Artefactos de traspaso

Todos viven en `auditorias/{YYYY-MM-DD}_{tema}/` (expediente = memoria
jurídica del ecosistema). Nomenclatura por rondas
(`prompt_{fase}_rondaN.md` / `respuesta_{fase}_rondaN.md`).

| Fase | Artefacto | Archivo | Productor → Consumidor |
|---|---|---|---|
| F0 | Checklist de micro-tareas con DoD + complejidad **+ Parada de Observación** | `docs/estado_actual.md` | Arquitecto → Director |
| F1 | Diseño + prompt de revisión de diseño | `prompt_diseno_rondaN.md` | Arquitecto → Auditor |
| F2 | Veredicto + validación anti-bluff | `respuesta_diseno_rondaN.md` (+ anexo) | Auditor → Sintetizador/Arquitecto |
| F3 | **Paquete de Especificación** | `spec_mtNN.md` | Especificador → Ingeniero |
| F4 | **Informe de Implementación** | `informe_mtNN.md` | Ingeniero → Verificador |
| F5 | Verificación F5 | anexo en `informe_mtNN.md` | Verificador → expediente |
| F6 | Prompt/respuesta de auditoría de código | `prompt_auditoria_rondaN.md` / `respuesta_auditoria_rondaN.md` | Sintetizador ↔ Auditor |
| F7 | Evidencia de cierre | `evidencia_mtNN.md` | Arquitecto → Director |
| **cualquiera** | **Solicitud de Recalibración (§3.2)** | `solicitud_recalibracion_mtNN.md` | quien la detecta → Director (G0′) |

### 4.1 Paquete de Especificación (`spec_mtNN.md`) — contrato Especificador → Ingeniero

**Autocontenido:** el Ingeniero arranca en contexto nuevo y no puede
depender de nada que no esté en la spec o en el repo. Secciones
obligatorias:

1. **Objetivo** (1–3 líneas), micro-tarea del checklist a la que responde y
   **complejidad asignada** (determina el modelo Ingeniero, §2).
2. **Contexto mínimo verificado**: rutas exactas, extractos literales del
   código actual, decisiones del diseño aprobado que aplican.
3. **Contrato**: firmas, campos, tipos, rutas de API/colecciones. Cambios de
   datos citan `schemas/firestore_schema.md` ya actualizado (el schema se
   toca en F1/F3, nunca lo decide el Ingeniero).
4. **Restricciones**: qué NO tocar, límites (anti-bucle, presupuesto de
   tokens, "sin dependencias nuevas").
5. **DoD ejecutable**: comandos/observaciones EXACTOS que demuestran que
   está terminada (estado final observable, jamás "corrió sin errores").
   Incluye la prueba A/B si protege un fix, y **la Parada de Observación
   que le corresponda** (§3.1).
6. **Protocolo de dudas**: "si algo es ambiguo, DETENTE y devuelve la duda
   en el Informe; implementar sobre un supuesto no declarado invalida la
   entrega." Una duda reabre **F3′**: el Director NO media con respuestas
   puntuales fuera de artefactos.
7. **Glosa pedagógica inline** (§4.3) — obligatoria, distribuida por el
   documento, no como apéndice.
8. **AVISO de traspaso** (§5).

### 4.2 Informe de Implementación (`informe_mtNN.md`) — contrato Ingeniero → Verificador

1. **Qué se hizo**: archivos tocados/creados con resumen por archivo.
2. **Diff literal**: bloque con el output ÍNTEGRO de `git diff` +
   `git status`, sin edición manual. Viaja TAL CUAL al prompt de F6. Sin
   diff, el informe es INVÁLIDO.
3. **Evidencia literal**: salida REAL de cada comando del DoD (copiada, no
   resumida). Sin evidencia literal, el informe es INVÁLIDO.
4. **Desviaciones**: cualquier diferencia respecto a la spec, con razón.
   Desviación no declarada detectada en F5 = entrega rechazada.
5. **Dudas del Ingeniero**: puntos de menor certeza (alimentan F6).
6. **Estado commiteable**: confirmación de que todo queda verde.
7. **Glosa pedagógica inline** (§4.3) — al menos en el resumen y en las
   dudas, que es lo que el Director lee.
8. **AVISO de traspaso** (§5).

### 4.3 Regla de Glosa Pedagógica Inline (nueva en v2.6)

**Todo término técnico complejo que aparezca en una spec o en un informe
lleva su analogía en lenguaje ordinario, en el sitio donde aparece.**

Cómo se aplica:

- **Inline, no en glosario.** La analogía va entre paréntesis o en la frase
  siguiente, donde el término se usa. Un glosario al final no se lee.
- **Una vez por documento.** Se glosa la primera aparición; repetirlo en
  cada línea es ruido.
- **Analogía, no definición.** "Fail-closed (como un torniquete que se
  bloquea si se va la luz, en vez de quedarse abierto)" enseña; "fail-closed
  significa que ante el fallo se deniega" no añade nada para quien no sabe
  qué es.
- **La escribe quien produce el artefacto** — Especificador en F3, Ingeniero
  en F4, Arquitecto en F0/F1. **No** el Asesor: así el Director tiene
  siempre dos fuentes independientes con las que contrastar (§1.1).

**Reducción de la decisión al eje reversibilidad × impacto.** Todo punto en
que un artefacto pida una decisión al Director debe presentarla en estos dos
términos, y solo en estos dos:

| | **Impacto bajo** | **Impacto alto** |
|---|---|---|
| **Reversible** | decide quien lo esté haciendo; se informa al Director | el Director decide; error asumible |
| **Irreversible** | el Director decide, con la alternativa descrita | **el Director decide con el expediente delante**; es donde conviene convocar al Asesor (§1.1) |

- **Reversibilidad:** ¿cuánto cuesta deshacerlo? (un commit revertido, una
  migración de datos, una decisión de arquitectura que arrastra tres MTs).
- **Impacto de negocio:** ¿a quién afecta si sale mal? (a nadie hasta el
  próximo ciclo, a un usuario en una sesión, a todas las actas guardadas).

Prohibido pedir al Director una decisión formulada en términos puramente
técnicos ("¿usamos allowlist o denylist?") sin traducirla a este eje
("¿preferimos que ante un error el sistema bloquee y moleste, o que deje
pasar y quizá borre trabajo? Lo primero es reversible; lo segundo no").

---

## 5. AVISO de traspaso (obligatorio al final de TODO artefacto)

Bloque estándar, literal, al final de cada artefacto. Diseñado para que el
Director pueda rotar la información **sin leer el artefacto completo**:

```
━━ AVISO DE TRASPASO ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CICLO      : {expediente, p. ej. 2026-08-09_metodologia_v26}
FASE       : {F0..F7} — {nombre}
TURNO DE   : {Director | Arquitecto | Especificador | Ingeniero |
              Verificador | Sintetizador | Auditor}
MODELO     : {Opus 5 | Sonnet 5 | Haiku 4.5 |
              Gemini 3.1 Pro High | Gemini Flash} — según §2
ENTREGAR   : {ruta(s) exacta(s) del artefacto a transportar}
ADJUNTOS   : {lista exacta de archivos del repo / git diff que
              viajan CON el artefacto, o "Ninguno"}
DESTINO    : {dónde pegarlo/adjuntarlo}
ACCIÓN     : {qué debe hacer quien recibe, en 1 línea}
OBSERVABLE : {qué podrá ver o tocar el Director tras esta fase, o
              "Ninguno en esta fase" — §3.1}
VUELVE A   : {rol que recibe el resultado} con {qué archivo se
              archiva y con qué nombre}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Reglas del AVISO:
- **Un artefacto sin AVISO no cierra fase.**
- **`ADJUNTOS` es exhaustivo**: lo listado es obligatorio transportarlo; lo
  no listado no se adjunta.
- **`MODELO` es vinculante**: indica qué modelo y configuración abrir para
  la fase siguiente, según §2.
- **`OBSERVABLE` es nuevo en v2.6**: dice al Director si esta fase le deja
  algo que ver. Evita que llegue a G2 sin haber tocado nada.
- Cada rol **verifica que el artefacto recibido le corresponde** (campo
  `TURNO DE`) y rechaza los ajenos con una línea, sin ejecutarlos. Este
  rechazo solo opera si la sesión fue inicializada con su rol (§6).
- En Modo M el `DESTINO` es una instrucción de operación para el Director;
  en Modo A es la llamada que hace el orquestador.

---

## 6. Modos de operación

### Modo M — Manual (DEFAULT)

El Director transporta cada artefacto entre las IAs:
- **Arquitecto**: sesión de Claude Code con Opus 5, `effort: low/medium`.
- **Especificador**: sesión de Claude Opus 5 en Alta / Sonnet 5 en
  Media-Baja (`effort: high`) — conversación nueva por meta.
- **Ingeniero**: sesión nueva de Sonnet 5 (toda complejidad desde el
  10-08); recibe SOLO el Paquete de Especificación (+ repo). Práctica
  consolidada: **rotación asistida** — el Arquitecto lanza al Ingeniero
  como subagente con contexto limpio y la spec archivada.
- **Verificador / Sintetizador**: sesión o subagente según §2.
- **Auditor**: conversación NUEVA de Gemini por ronda, sin herencia de hilo.
- **Asesor** (§1.1): conversación propia en Antigravity, **separada de la
  del Auditor**, convocada por el Director en los gates.

**Inicialización de identidad (obligatoria):** toda sesión nueva de
Especificador, Ingeniero, Verificador, Sintetizador o Auditor arranca con un
prompt de rol de una línea ANTES del primer artefacto:

> "Rol: {Especificador | Ingeniero | Verificador | Sintetizador | Auditor}
> del ciclo {expediente}, metodología v2.6 del ecosistema Express. Confirma
> recepción sin accionar; acepta únicamente artefactos cuyo campo TURNO DE
> diga {rol}."

Sin esta inicialización, la regla de rechazo de artefactos ajenos (§5) no
tiene base para operar. **Desde el 10-08 esta disciplina pesa más que
antes**: en complejidad Alta, Opus ocupa Arquitecto, Especificador y
Verificador — la inicialización de identidad es lo único que garantiza que
cada una de esas sesiones arranque realmente en frío (§10.7).

**Working tree limpio:** F4 arranca sobre la rama base sin cambios sin
commitear de otras micro-tareas. Una MT en vuelo a la vez por componente.

Costo asumido: toil humano de rotación (mitigado por la rotación asistida).
Beneficio: el Director ve pasar todos los artefactos y cada IA queda
aislada de verdad.

### Modo A — Automatizado (variante propuesta, NO habilitada; requiere ciclo propio)

El Arquitecto orquesta desde Claude Code: lanza Especificador, Ingeniero y
Verificador como subagentes y llama al Auditor vía API. El humano interviene
únicamente en los gates.

**Salvaguardas mínimas si algún día se habilita** (condición necesaria, no
suficiente):
1. Todo prompt enviado y toda respuesta recibida se archivan **literales**
   en el expediente ANTES de que el orquestador los procese.
2. El Director hace spot-check de al menos 1 traspaso por ciclo.
3. Los gates G0/G0′/G1/G2 siguen siendo humanos y bloqueantes.
4. La regla anti-bucle aplica al orquestador: 2 rondas sin converger → STOP.
5. **Nuevo en v2.6:** las Paradas de Observación (§3.1) son **bloqueantes
   también en Modo A**. Un ciclo autónomo no puede saltárselas: se detiene y
   espera al Director.

Pendiente de: gobernanza del tier de Gemini (privacidad) + ciclo de diseño
propio. La infraestructura del orquestador vive en el repositorio
**NexoOrchestrator** desde el 09-08-2026.

---

## 7. Estrategia de optimización de tokens

Gastar la inteligencia donde rinde y ahorrarla donde no. Dos palancas:

### 7.1 Prompt Caching (obligatorio para contexto base)

Los archivos de contexto base que viajan repetidamente
(`ECOSISTEMA_VISION.md`, `schemas/firestore_schema.md`, esta metodología, el
diseño aprobado del ciclo) se tratan como **bloques cacheables**:

- **Vía API / subagentes / Modo A:** marcar los bloques repetitivos con
  `cache_control: {"type": "ephemeral"}`. El contexto base va PRIMERO y el
  contenido volátil DESPUÉS — un solo byte cambiado invalida la caché de
  todo lo que le sigue.
- **En sesiones de Claude Code / chat:** la caché es automática, pero la
  disciplina es la misma: contexto estable al inicio, artefactos volátiles
  referenciados por ruta, nunca re-pegados.
- Regla práctica: si un bloque va a viajar ≥2 veces, es candidato a caché;
  si se incrusta dos veces a mano, es un defecto de operación.

### 7.2 Calibración del parámetro `effort`

Se calibra **por la irreversibilidad de la decisión, no por el largo del
documento**:

| Configuración | Cuándo | Por qué |
|---|---|---|
| Opus `effort: low` | F0 rutinario, clasificación de complejidad, arbitrajes simples | La inteligencia base basta; pagar razonamiento extra es sobre-gasto. |
| Opus `effort: medium` | F1 con decisiones de arquitectura o schema nuevos | Decisión irreversible y cara de corregir aguas abajo. |
| Opus `effort: high` | F3 y F5 en **Alta**, refutaciones de BUG (§2.1) | La spec y la verificación de Alta son el punto de mayor apalancamiento del ciclo; el precedente de MT-D2 (seis rondas, retractación firmada) confirma que aquí no se abarata. |
| Sonnet `effort: high` | F3 en **Media/Baja** | La spec sigue siendo el contrato del que depende F4–F6, aunque la complejidad no justifique escalar a Opus. |
| Sonnet estándar | F4, toda complejidad | Implementar contra una spec buena no exige razonamiento máximo. |
| Haiku (`thinking: enabled` si aplica) | F5 Media/Baja, empaquetado F6 | Trabajo determinista y mecánico. |

Anti-patrones de gasto (prohibidos): **Opus implementando** (F4 es
exclusivo de Sonnet, toda complejidad); **Opus redactando specs o
verificando F5 en Media/Baja** (ahí basta Sonnet/Haiku — reservar Opus para
Alta es lo que hace sostenible la escalada del 10-08); Sonnet `effort: high`
para typos o CSS; re-pegar contexto ya cacheado; rondas 2+ con Pro High
cuando Flash basta (la Ronda 1 de F6 es SIEMPRE Pro High salvo en Baja —
abaratarla no es optimización, es hueco de auditoría).

**Nota v2.6 sobre el coste de la glosa (§4.3):** añadir analogías encarece
las specs de forma marginal y **no** justifica bajar el `effort` de F3. Una
spec entendible que el Director puede cuestionar previene ciclos enteros;
esa es la comparación correcta, no los tokens de unos paréntesis.

---

## 8. Reglas no negociables

- **Micro-tareas**: ≤30–45 min, UN entregable verificable, DoD escrito
  ANTES, sistema commiteable al terminar, checklist en `estado_actual.md`,
  tandas ≤5 para auditoría, 1–3 micro-ciclos por sesión.
- **Evidencia**: estado final observable con salida literal (jamás "corrió
  sin errores"), prueba A/B para todo test que proteja un fix, dudas
  declaradas, schema centralizado primero.
- **Anti-bluff** a toda respuesta del Auditor (skill `auditor_externo`):
  citas verificadas con grep/ejecución; sin citas = INVÁLIDA; BUG confirmado
  = ronda nueva; BUG refutado solo con evidencia archivo:línea de Opus
  (§2.1) — nunca del Ingeniero sobre su propio código.
- **Anti-bucle**: 2 intentos del mismo fix fallando → STOP y reporte. Dos
  recalibraciones sobre la misma MT (§3.2) → STOP. Sospecha de bucle o
  alucinación en cualquiera de las IAs → `depurador_agentes`.
- **Nada se commitea sin aprobación explícita del Director** (gate G2).
- **Fidelidad a la spec**: el Ingeniero no redefine contrato, alcance ni
  DoD. Toda desviación se declara; una desviación no declarada invalida la
  entrega.
- **Duda = pregunta**: ambigüedad en la spec se devuelve como duda, nunca se
  resuelve con un supuesto silencioso. Una duda reabre F3′.
- **Verificación F5 obligatoria y al 100%** (sin muestreo): los comandos del
  DoD se EJECUTAN sobre el código real antes de generar el prompt de
  auditoría. Leer el informe no es verificar. Al Auditor llegan claims + el
  git diff ÍNTEGRO + código fuente, jamás prosa del implementador.
- **Diff sin filtrar**: el bloque `git diff` literal del Informe se incrusta
  completo en el prompt de F6.
- **AVISO de traspaso obligatorio** (§5), con `ADJUNTOS` exhaustivo,
  `MODELO` vinculante y `OBSERVABLE` declarado.
- **Inicialización de identidad** en toda sesión nueva de rol (§6) — desde
  el 10-08, requisito reforzado cuando Opus enlaza varios roles del mismo
  ciclo.
- **Working tree limpio antes de F4** y una MT en vuelo por componente.
- **Escalada por artefacto, nunca inline** (§2.1).
- **Parada de Observación declarada o exención ratificada** (§3.1): una meta
  con UI, datos o indicadores que llega a G0 sin evidencia observable
  predeclarada **no pasa el gate**.
- **Recalibración por artefacto** (§3.2): cambiar la evidencia observable
  exige Solicitud de Recalibración y Mini-Gate G0′. Cambiarla sobre la
  marcha es deriva de alcance y invalida la entrega.
- **Glosa pedagógica inline** (§4.3) en specs e informes, y toda decisión
  pedida al Director formulada en el eje reversibilidad × impacto.
- **El Asesor no decide** (§1.1): no vota, no produce artefactos del
  expediente, no comparte conversación con el Auditor, y toda resolución de
  gate se registra con la razón del Director.

---

## 9. Mapa de skills en el ciclo v2.6

| Momento | Skill | Nota v2.6 |
|---|---|---|
| F0 (descomponer/priorizar/clasificar) | `roadmap_manager` | añade la clasificación de complejidad (§2) **y la Parada de Observación (§3.1)** al checklist |
| F1, F2, F6 (prompts + anti-bluff) | `auditor_externo` | F1 la ejecuta el Arquitecto; el empaquetado F6 lo ejecuta el Sintetizador; anti-bluff formal Haiku, refutaciones Opus. **El Asesor no interviene aquí.** |
| Gates G0/G0′/G1/G2 | — (Asesor, §1.1) | conversación aparte en Antigravity; explica, no decide |
| Cierre de sesión | `documentador_sesion` | registra la resolución de las Paradas de Observación y de las recalibraciones |
| Fuera de plan | `innovador` | sin cambio |
| IA en bucle | `depurador_agentes` | cubre a TODAS las IAs del ciclo |
| Cambios de datos | `arquitecto_firebase` | el schema se toca en F1/F3, nunca en F4 |
| Paridad Web/Android | `auditor_paridad` | sin cambio |

---

## 10. Adopción

1. ✅ **v2 adoptada el 09-07-2026** (auditada por Gemini: APROBADO CON
   CAMBIOS r1; expediente `auditorias/2026-07-08_metodologia_v2/`) y probada
   en **siete ciclos completos**.
2. ✅ **v2.5 Optimizada adoptada el 06-08-2026**: reasignación de roles por
   modelo/parámetros (§1), matriz de complejidad (§2), estrategia de tokens
   (§7) y eliminación de toda metodología heredada.
3. ✅ **Ajustes del Director al conceder G2 (06-08-2026):** (a) F5 de
   complejidad Alta la ejecuta Sonnet 5 `effort: high`; (b) la Ronda 1 de F6
   usa SIEMPRE Gemini 3.1 Pro High.
4. ✅ **v2.6 adoptada el 09-08-2026** por orden directa del Director:
   Asesor Estratégico (§1.1), Glosa Pedagógica Inline (§4.3), Paradas de
   Observación (§3.1) y Protocolo de Recalibración Dinámica (§3.2). La
   maquinaria de v2/v2.5 se conserva íntegra.
5. **Evidencia empírica que motivó la v2.6** — el ciclo
   `2026-08-06_docker_orchestrator` (MT-D2, núcleo de ejecución del
   orquestador; expediente hoy en el repositorio **NexoOrchestrator**)
   recorrió **seis rondas de corrección y seis de verificación** más una
   auditoría externa que devolvió RECHAZADO. Encontró defectos reales cada
   vez, lo que valida el ciclo. Pero también dejó dos lecciones que la v2.6
   recoge:
   - **Ningún defecto serio lo encontró quien escribió el código**, y varios
     fueron fallos de diseño del propio Arquitecto — incluida una
     **retractación firmada** sobre un vector declarado cerrado sin estarlo.
     El valor está en la separación de roles, no en la habilidad de un nodo.
   - El Director aprobó gates sobre artefactos que no podía verificar por sí
     mismo, y una micro-tarea de infraestructura pura no le dejó **nada que
     ver** en seis rondas. De ahí §1.1, §3.1 y §4.3.
6. **Primer ciclo bajo v2.6:** el próximo G0 de la fila del Director. Retro
   en bitácora al cierre: si la Parada de Observación se predeclaró bien, si
   la glosa hizo que el Director cuestionara algo que antes habría aprobado
   sin más, y si el Asesor aportó criterio o solo comodidad.
7. **Sustitución de modelo — Fable 5 fuera del roster (10-08-2026).**
   Anthropic cambió las condiciones de acceso a Fable 5; deja de ser la
   opción por defecto del Arquitecto. Invocando el mecanismo YA PREVISTO en
   §2 ("Indisponibilidad de un modelo: el Director decide la sustitución
   dentro de la tabla de roles") — **no** una versión nueva de la
   metodología, solo la tabla de §1/§2 actualizada:
   - **Arquitecto Macro (F0/F1):** Opus 5, mismo `effort: low/medium`.
     Sustitución directa en el mismo nicho.
   - **Especificador + Verificador Semántico F5-Alta:** Opus 5,
     `effort: high` — escala junto con el Arquitecto, no solo lo reemplaza.
     Motivo: el precedente de MT-D2 (seis rondas de defectos, una auditoría
     RECHAZADA, una retractación firmada) es la evidencia más fuerte que
     tiene el ecosistema de que el juicio semántico en Alta es donde menos
     conviene ahorrar.
   - **Especificador — Media/Baja:** sin cambio, sigue en Sonnet 5
     `effort: high`. Escalar aquí habría sido el mismo anti-patrón de
     sobre-gasto que §7.2 ya prohibía para Fable.
   - **Ingeniero (F4):** se retira el split con Haiku 4.5; **Sonnet 5
     ejecuta F4 en toda complejidad.** Simplifica la matriz y le da a
     Sonnet una función única y clara.
   - **Sintetizador (F5 Media/Baja + empaquetado F6):** sin cambio, Haiku
     4.5 — es trabajo determinista, no hay irreversibilidad que justifique
     escalarlo.
   - **Auditor y Asesor:** sin cambio — son Gemini, ajenos al cambio de
     disponibilidad de Claude.

   **Efecto colateral en la regla de oro:** con Sonnet reducido a Ingeniero
   puro, la refutación de BUGs y la resolución de ambigüedades semánticas
   dejan de poder pasar por Sonnet — el Ingeniero no verifica ni refuta su
   propio trabajo. Esa autoridad se concentra en Opus (§2.1, Triángulo de
   verificación). Como contrapartida, en Alta el trade-off que v2.5 había
   declarado y aceptado (Especificador e Ingeniero comparten modelo)
   **desaparece**: son ahora Opus y Sonnet, modelos distintos.

   **Riesgo nuevo y declarado:** en Alta, Opus ocupa Arquitecto,
   Especificador y Verificador — tres de los cuatro nodos internos del
   ciclo. La separación que protege esa complejidad pasa a depender casi
   por completo de (a) que cada sesión de Opus arranque realmente en frío,
   con la inicialización de identidad de §6 sin excepción, y (b) la
   auditoría cross-vendor de Gemini en F6, cuya Ronda 1 sigue siendo
   SIEMPRE Pro High en Alta — ese requisito pasa de ser buena disciplina a
   ser el principal cortafuegos del triángulo en esta franja.

   **Provisional:** esta sustitución queda vigente hasta que el Director la
   revierta o Fable 5 vuelva a estar disponible en condiciones aceptables.
   No requiere un nuevo ciclo de diseño para revertirse — basta con otra
   entrada en este punto.
