# Expediente 2026-07-08_metodologia_v2 — Prompt de revisión de DISEÑO (ronda 1)

**Ciclo:** Diseño (F1 — este ciclo corre aún bajo la v1, paso 1 de METODOLOGIA_DUAL_IA.md)
**Meta:** [NexoExpress] Adoptar la Metodología v2 (Triple-IA): Fable 5 Arquitecto / Claude Sonnet Ingeniero / Gemini 3.1 Pro High Auditor.
**Objeto revisado:** `docs/METODOLOGIA_TRIPLE_IA.md` (borrador, condensado fielmente en el contexto de abajo).
**Preparado por:** Arquitecto (Claude Fable 5) — sesión 08-07-2026

## Instrucciones de operación para el Director

1. Conversación **NUEVA** en Gemini 3.1 Pro High.
2. **Sin adjuntos** — todo el contexto verificado va dentro del prompt.
3. Pegar como primer mensaje únicamente lo que está entre las marcas `=== PROMPT ===`.
4. Si la respuesta llega sin veredicto por claim o sin responder TODAS las Q, responder solo: *"Auditoría INVÁLIDA según el contrato: faltan verdictos/respuestas Q. Reenvíala completa."*
5. Guardar la respuesta tal cual como `respuesta_diseno_ronda1.md` en este expediente y avisar al Arquitecto para validación anti-bluff antes de adoptar nada.

---

=== PROMPT ===

# Rol y regla de oro
Eres auditor adversarial de diseño del ecosistema Express. El diseñador (otra IA) propone una **metodología de trabajo v2** con tres IAs en roles rotativos. Nota de transparencia: en esa metodología TÚ ocuparías el rol de Auditor Externo; eso no te da ni te quita autoridad — audita el diseño con la misma hostilidad que cualquier otro, incluidas las partes que definen tu propio rol. **Tu hipótesis de trabajo es que el diseño está mal o incompleto hasta que se demuestre lo contrario.** No eres un asistente conversacional: no agradezcas, no resumas, no elogies. Cada afirmación tuya debe apoyarse en el contexto citado abajo (referéncialo por sección); lo que no esté en este prompt es NO VERIFICABLE — prohibido rellenarlo con suposiciones.

# Formato obligatorio de CADA verificación
CLAIM → EVIDENCIA (cita del contexto de este prompt) → TRAZA (razonamiento paso a paso con un escenario concreto) → VERDICTO (SÓLIDO / DÉBIL / RECHAZADO).

# Material adjunto
Ninguno — revisión de diseño. Contexto verificado a continuación.

# Contexto verificado

**CTX-1 — Metodología v1 vigente (probada en un ciclo completo real, expediente 2026-07-07).** Dos IAs: Claude (Fable 5) como Ingeniero (diseña, implementa, verifica, genera prompts de auditoría y valida anti-bluff las respuestas) y Gemini como Auditor adversarial (revisa diseño antes, audita código después, citas archivo:línea + trazas obligatorias). El humano (Director) transporta los prompts, arbitra y aprueba commits. Reglas: diseño primero; micro-tareas de ≤30–45 min con UN entregable y DoD escrito antes; evidencia = estado final observable con salida literal; prueba A/B para tests que protegen fixes; anti-bluff a toda respuesta del auditor (citas verificadas con grep/ejecución; sin citas = INVÁLIDA); regla anti-bucle (2 fixes fallidos = STOP); expedientes en `auditorias/{fecha}_{tema}/`; nada se commitea sin aprobación del Director. Resultado real del primer ciclo: cazó 3 defectos que ninguna IA vio sola.

**CTX-2 — Cambio central propuesto (v2).** El rol de Ingeniero v1 se divide: **Arquitecto** (Fable 5: plan macro, descomposición, diseño, especificación, verificación del trabajo del Ingeniero re-ejecutando el DoD, prompts de auditoría, anti-bluff, custodia de gates) e **Ingeniero** (Claude Sonnet: implementa micro-tareas exactamente según especificación, corre el DoD, entrega informe con salida literal y dudas; no diseña, no amplía alcance, no se autovalida). Gemini sigue de Auditor. Regla de oro extendida: ninguna IA verifica su propio trabajo con autoridad final; el Arquitecto valida a Ingeniero y Auditor; el Auditor valida diseño y código; el Ingeniero no valida a nadie pero declara dudas; el Director arbitra.

**CTX-3 — Ciclo v2 por fases.** F0 PLAN (Arquitecto descompone en micro-tareas con DoD; GATE G0: Director aprueba) → F1 DISEÑO (Arquitecto: diseño + prompt de revisión) → F2 VEREDICTO (Auditor responde; Arquitecto anti-bluff; GATE G1: Director adopta el veredicto) → F3 SPEC (Arquitecto: Paquete de Especificación por micro-tarea) → F4 IMPLEMENTAR (Ingeniero: código + Informe de Implementación) → F5 VERIFICAR (Arquitecto re-ejecuta el DoD sobre el código real; desviación → devuelve a F4) → F6 AUDITORÍA (Arquitecto genera prompt de auditoría de código con las dudas del Ingeniero y las propias; Auditor responde; anti-bluff; BUG → F4 y ronda nueva) → F7 CIERRE (GATE G2: Director autoriza commit; bitácora y estado). Los 3 gates son humanos y no se automatizan en ningún modo. Cambios triviales: sin ciclo completo, pero con aprobación del Director antes de commit.

**CTX-4 — Artefactos de traspaso.** Todos archivados en el expediente. (a) **Paquete de Especificación** (`spec_mtNN.md`, Arquitecto→Ingeniero), autocontenido: objetivo; contexto mínimo verificado con extractos literales; contrato (firmas/campos/rutas — cambios de datos citan el schema ya actualizado en F1/F3, el Ingeniero nunca decide schema); restricciones (qué NO tocar); DoD ejecutable con comandos exactos; protocolo de dudas ("ambigüedad → DETENTE y devuelve la duda; implementar sobre supuesto no declarado invalida la entrega"). (b) **Informe de Implementación** (`informe_mtNN.md`, Ingeniero→Arquitecto): archivos tocados; evidencia literal de cada comando del DoD (sin ella el informe es INVÁLIDO); desviaciones declaradas (no declarada y detectada en F5 = entrega rechazada); dudas del Ingeniero; confirmación de estado commiteable. (c) Prompts/respuestas de diseño y auditoría, nomenclatura v1 por rondas.

**CTX-5 — AVISO de traspaso.** Bloque estándar obligatorio al final de TODO artefacto, con campos: CICLO, FASE, TURNO DE, ENTREGAR (rutas exactas), DESTINO (dónde pegarlo), ACCIÓN (1 línea), VUELVE A (rol + nombre de archivo con que se archiva el resultado). Reglas: artefacto sin AVISO no cierra fase; cada rol verifica que el artefacto recibido le corresponde (campo TURNO DE) y rechaza artefactos ajenos sin ejecutarlos. Diseñado para que el Director rote información sin leer el artefacto completo.

**CTX-6 — Modos de operación.** **Modo M (manual, DEFAULT y único modo del piloto):** el Director transporta cada artefacto; Ingeniero en sesión Sonnet separada (conversación nueva por micro-tarea, recibe solo la spec + repo); Auditor en conversación Gemini nueva por ronda. **Modo A (automatizado, NO habilitado):** el Arquitecto orquesta — Ingeniero como subagente Sonnet con contexto limpio, Auditor vía API de Gemini; humano solo en gates. El propio diseño declara los riesgos de Modo A: el Arquitecto (nodo con más poder de filtrado: escribe spec, verifica implementación y redacta el prompt de auditoría) controlaría además qué ve el Auditor; degeneración a modo chat del auditor solo detectable post-hoc. Salvaguardas mínimas declaradas si se habilitara: archivado literal de todo prompt/respuesta ANTES de procesarse, spot-check del Director ≥1 traspaso por ciclo, gates humanos bloqueantes, anti-bucle del orquestador (2 rondas sin converger = STOP). Prerrequisitos declarados: gobernanza del tier de la API de Gemini (pendiente: privacidad, hoy tier gratuito) y costos. Decisión del borrador: Modo A pospuesto, requiere ciclo de diseño propio.

**CTX-7 — Excepciones.** Micro-tarea trivial-técnica: el Director puede autorizar colapso Arquitecto=Ingeniero (degrada a v1 para esa MT, anotado en checklist). Sonnet indisponible → degrada a v1 con anotación. Gemini indisponible → NO hay cierre de ciclo. La v1 se conserva como fallback; tras adoptar v2, una micro-tarea posterior (MT-02) elimina referencias huérfanas al ciclo v1 en documentos operativos (prompt de arranque de sesión, skills `auditor_externo` y `roadmap_manager`, README).

**CTX-8 — Adopción y piloto.** La v2 solo entra en vigor con tu APROBADO (o APROBADO CON CAMBIOS incorporados) + aprobación del Director. Piloto: MT-04 de ActaExpressWeb (frontend envía flag `generarSintesis: true`; UX decidida por el Director), en Modo M, con retro en bitácora (incluida la pregunta de si el overhead de escribir specs obliga a recalibrar el tamaño de micro-tarea).

# Claims a verificar

- **C1 — El triángulo preserva la regla de oro.** Con la división de CTX-2, ningún actor valida su propio trabajo con autoridad final, y cada producción (diseño, código, veredicto) tiene al menos un verificador distinto de su autor. La concentración residual de poder en el Arquitecto queda mitigada por: adjuntos = código fuente real (nunca prosa del implementador), archivado literal de artefactos, spot-checks del Director.
- **C2 — La spec autocontenida es un traspaso suficiente.** Un Ingeniero (Sonnet) en conversación nueva, con SOLO el Paquete de Especificación de CTX-4a + acceso al repo, puede implementar la micro-tarea sin heredar contexto de sesión, y el protocolo de dudas evita que la ambigüedad se resuelva con supuestos silenciosos.
- **C3 — El AVISO elimina la ambigüedad de turno.** Con CTX-5, en cualquier corte de sesión el Director sabe exactamente qué transportar, a dónde y qué esperar de vuelta, sin leer artefactos completos; y el enrutamiento erróneo (artefacto al rol equivocado) es detectado por el receptor.
- **C4 — Doble verificación de la implementación.** F5 (Arquitecto re-ejecuta el DoD sobre código real) + F6 (tu auditoría adversarial) hacen que un bluff del Ingeniero (evidencia inventada o test falso-positivo) sea detectado antes del commit, manteniendo además la prueba A/B de la v1.
- **C5 — Posponer Modo A es la decisión correcta.** Dado CTX-6 (riesgo de filtrado por el orquestador + gobernanza del tier de Gemini pendiente), pilotar la v2 exclusivamente en Modo M y exigir ciclo de diseño propio para Modo A es la secuencia correcta, no un exceso de cautela.
- **C6 — La transición v1→v2 no deja estados ambiguos.** Con CTX-7/CTX-8 (v1 vigente hasta APROBADO + aprobación del Director; MT-02 de limpieza de referencias; excepciones de degradación explícitas), en ningún momento hay dos metodologías simultáneamente "vigentes" ni una sesión futura puede ejecutar el ciclo equivocado por documentos desactualizados.

# Dudas declaradas por el diseñador

- **D1:** El Arquitecto escribe la spec, verifica la implementación Y redacta el prompt de auditoría. Aunque los adjuntos sean código real, el Arquitecto decide QUÉ claims y QUÉ archivos te llegan. ¿Es mitigación suficiente el archivado literal + spot-checks, o el diseño necesita un mecanismo estructural adicional (p. ej. que el prompt de auditoría liste obligatoriamente TODOS los archivos tocados según `git diff`, no una selección del Arquitecto)?
- **D2:** Costo/latencia: tres modelos + dos verificaciones (F5 y F6) por micro-tarea de ≤30–45 min. ¿La v2 es rentable para TODA micro-tarea no trivial, o conviene un umbral explícito (p. ej. tandas de ≤5 MTs comparten una sola pasada F5+F6, como ya permite la v1 con las tandas de auditoría)?
- **D3:** El overhead de redactar specs autocontenidas (CTX-4a) puede superar los 30–45 min de la propia micro-tarea. ¿Recalibrar el tamaño de micro-tarea en v2, o aceptar que la spec es parte del presupuesto de F3 y no de la MT?
- **D4:** En Modo M el Ingeniero (Sonnet) trabaja "con acceso al repo". Si el repo local ya contiene trabajo a medias de otra MT de la misma tanda, la premisa "conversación nueva = aislamiento" se debilita (el aislamiento de contexto no es aislamiento de working tree). ¿Debe la v2 exigir 1 MT en vuelo a la vez (serialización estricta) o basta la regla v1 de "sistema commiteable entre micro-tareas"?

# Preguntas de control (respóndelas TODAS con recomendación ÚNICA y justificada; "depende" no es respuesta)

- **Q1:** ¿F5 (re-ejecución del DoD por el Arquitecto) debe ser obligatoria en el 100% de las micro-tareas, o muestreada? UNA recomendación, justificada con el modelo de amenaza concreto (qué clase de defecto se escaparía en cada opción y con qué probabilidad de llegar a F7).
- **Q2:** Enumera los campos del AVISO de CTX-5 y dictamina: ¿falta o sobra algún campo para que un Director con prisa rote SIN leer el artefacto? Si falta, di CUÁL exactamente y su formato.
- **Q3:** ¿Qué debe pasar cuando el Ingeniero devuelve una duda en mitad de F4 (protocolo de CTX-4a): vuelve el turno al Arquitecto con ronda nueva de spec (F3'), o el Director media con una respuesta puntual sin regenerar la spec? UNA recomendación, considerando trazabilidad del expediente y la regla anti-bucle.
- **Q4:** Traza simbólica completa: ejecuta el piloto (MT-04: el frontend de ActaExpressWeb debe enviar `generarSintesis: true` con un toggle cuya UX decide el Director) bajo la v2 en Modo M, fase por fase (F0→F7), nombrando cada artefacto con su nombre de archivo exacto según CTX-4 y cada AVISO (quién → quién). Señala el punto EXACTO del ciclo donde estallaría si el Paquete de Especificación omitiera el DoD ejecutable, y quién lo detectaría primero según el diseño.

# Anti-aprobación-automática
Si tu veredicto global es APROBADO o APROBADO CON CAMBIOS, debes ADEMÁS demostrar por qué cada una de estas trampas NO aplica (o qué cambio del diseño la neutraliza), con evidencia del contexto:

- **T1 — Spec ambigua + Ingeniero obediente.** La spec de una MT omite un caso borde; Sonnet, instruido a ser fiel, implementa literal y el hueco pasa F5 (el DoD tampoco lo cubría, fue escrito por el mismo Arquitecto que la spec). Autor de spec y autor de DoD son el MISMO nodo: ¿dónde rompe el diseño esta correlación de errores?
- **T2 — Prosa en vez de código.** Bajo presión de tiempo, el Arquitecto redacta el prompt de auditoría F6 resumiendo el informe del Ingeniero en vez de adjuntar los archivos fuente. ¿Qué elemento del diseño lo IMPIDE estructuralmente (no solo lo desaconseja) y cómo lo detectarías tú como Auditor desde tu lado?
- **T3 — Colusión del orquestador (Modo A).** Si mañana se habilita Modo A sin ciclo propio: el Arquitecto compone tu prompt, recibe tu respuesta y redacta el anti-bluff — los tres flujos en un solo nodo sin testigo humano por traspaso. ¿Las salvaguardas de CTX-6 son suficientes o el diseño debe declarar Modo A incompatible con auditoría adversarial mientras no exista archivado fuera del alcance del orquestador?
- **T4 — Enrutamiento cruzado.** El Director pega la spec de MT-05 en la sesión del Auditor y el prompt de auditoría en la de Sonnet. Según CTX-5, cada rol rechaza artefactos ajenos — pero ¿con qué información distingue Sonnet un artefacto "suyo" si ambos son markdown del mismo expediente? Dictamina si el campo TURNO DE basta o si falta un encabezado de destinatario por artefacto.
- **T5 — Deriva documental v1/v2.** La v2 se aprueba, pero MT-02 (limpieza de referencias) se pospone dos sesiones. El prompt de arranque de la siguiente sesión aún dice "Eres el Ingeniero" y referencia METODOLOGIA_DUAL_IA.md. ¿Qué elemento del diseño impide que esa sesión ejecute v1 por inercia, o es un hueco real que exige hacer MT-02 bloqueante ANTES del piloto?

# Entregable final
1. Tabla C1..C6 con verdictos (SÓLIDO / DÉBIL / RECHAZADO + cambio requerido si aplica).
2. Respuestas Q1..Q4 (recomendación única cada una; Q4 con la traza completa).
3. Refutación de T1..T5 si apruebas.
4. Opinión fundada sobre D1..D4.
5. Veredicto global: APROBADO / APROBADO CON CAMBIOS (listar los cambios EXACTOS) / RECHAZADO (razón + contra-diseño mínimo).

Entrega TODA tu respuesta como UN único documento markdown listo para archivar tal cual (sin texto fuera del documento). Una revisión sin verdicto por claim, sin las Q respondidas o sin la traza de Q4 es INVÁLIDA y será devuelta.

=== FIN PROMPT ===
