# Expediente 2026-07-14_robustez_pipeline — Respuesta de auditoría de CÓDIGO (ronda 1)

**Auditor:** Gemini 3.1 Pro High (conversación nueva, con inicialización de identidad)
**Recibida:** 17-07-2026, pegada por el Director (pegado aplanado; texto literal, tabla reconstruida sin alterar redacción).
**Veredicto global:** APROBADO
**Validación anti-bluff:** ver ANEXO — VÁLIDA (citas y aritmética re-ejecutadas por el Arquitecto; 2 observaciones menores no bloqueantes).

---

# Reporte de Auditoría Adversarial

## 1. Verificación de Claims (C1..C6)

| Claim | Evidencia (Archivo:Línea) | Traza (Ejecución Simbólica) | Veredicto |
|---|---|---|---|
| C1 — Guard fiel y pre-gasto | `artifacts/api-server/src/lib/audioGuard.ts:4-7` · `artifacts/api-server/src/routes/actas.ts:250-258` | Llamada POST. `esAudioMudo(8106, 31939, 300)` se evalúa antes de `uploadToGemini()`. `(8106 / (31939 / 1000)) = 253.79 < 300` -> true. `res.status(422)` sin invocar Gemini. | CONFIRMADO |
| C2 — Centinelas intactos | `artifacts/api-server/src/routes/actas.ts:47-48` · `artifacts/api-server/src/routes/actas.ts:71-72` | Prompt incluye textualmente el Q3 (título, participantes [], AL MENOS UN fragmento) y la sintaxis de SINTESIS_PROMPT ([SIN CONTENIDO AUDIBLE]). | CONFIRMADO |
| C3 — looksEmpty cierra OBS-1 | `artifacts/api-server/src/routes/actas.ts:281-286` | Arreglo silenceKeywords incluye "no se detectó". Condiciones verifican `titulo === "Reunión sin contenido audible"` o resumen contiene la keyword. | CONFIRMADO |
| C4 — thinkingBudget quirúrgico | `artifacts/api-server/src/routes/actas.ts:193-200` | Configuración `{ thinkingBudget: 4096 }` pasada solo a `generarSintesisEnBackground`. (CTX-B confirma que acta queda sin config). | CONFIRMADO |
| C5 — Timeout proporcional | `artifacts/api-server/src/lib/audioGuard.ts:10-12` · `artifacts/api-server/src/routes/actas.ts:111-114` | Para un audio corto, `calcularMaxWaitMs` devuelve 40000. `maxAttempts = 40000/2000 = 20`. Preserva los mismos ~40s del comportamiento previo. | CONFIRMADO |
| C6 — Alcance cerrado | Diff global provisto en prompt | Los únicos archivos tocados son home.tsx, audioGuard.ts y actas.ts. El guard UI condicional depende solo de `processAudio.isPending`. | CONFIRMADO |

## 2. Preguntas de Control (Q1..Q4)

**Q1: Traza de esAudioMudo** Condición (`artifacts/api-server/src/lib/audioGuard.ts:5-6`): `if (msDuration < 5000) return false; return audioSizeBytes / (msDuration / 1000) < minBps;`

- (i) Caso E2E (8106, 31939): 31939 < 5000 (false). 8106 / (31939 / 1000) = 253.79.... 253.79 < 300 (true). Resultado: Rechazado.
- (ii) Caso frontera dictamen (1725000, 3600000): 3600000 < 5000 (false). 1725000 / (3600000 / 1000) = 479.16.... 479.16 < 300 (false). Resultado: Pasa.
- (iii) Exactamente 300.0 B/s: 300.0 < 300 (false). Resultado: Pasa. El operador < es el correcto frente a <= porque asegura que el umbral de 300.0 constituya el límite mínimo de aceptación, rechazando cualquier valor estrictamente menor.

**Q2: Traza de waitForFileActive**

- Con msDuration = 55958: `maxWaitMs = Math.min(Math.max(40000, 40000 + 55958 / 10), 600000) = 45595.8` · `maxAttempts = Math.ceil(45595.8 / 2000) = 23` · Error al agotar (CTX-A): `Error("Timeout: el archivo tardó demasiado en procesarse")` (HTTP 500).
- Con msDuration = 7200000 (2h): `maxWaitMs = Math.min(Math.max(40000, 40000 + 720000), 600000) = 600000` · `maxAttempts = Math.ceil(600000 / 2000) = 300` · Error al agotar (CTX-A): `Error("Timeout: el archivo tardó demasiado en procesarse")` (HTTP 500).
- ¿Queda alguna ruta colgada? No, porque `calcularMaxWaitMs` trunca mediante `Math.min(..., 600_000)` fijando un techo duro de 10 minutos (~300 iteraciones).

**Q3: Flujo frontend en caso muteado (30s)**

1. El usuario inicia el POST; React Query setea `isPending = true`.
2. El elemento `<p data-testid="text-espera">` es renderizado en el DOM (`artifacts/acta-express/src/pages/home.tsx:205`).
3. El backend evalúa la guardia (422) en <300ms.
4. La mutación frontend entra a `onError` (CTX-F), lanzando el toast destructivo y resolviendo el estado, lo cual setea `isPending = false`.
5. El elemento `data-testid="text-espera"` se desmonta instantáneamente al actualizar el estado de React.
6. ¿Existe instante donde el usuario vea el mensaje de espera y el toast a la vez? Visualmente no de forma persistente. El desmontaje del mensaje está atado a la resolución del estado isPending, el cual finaliza al momento de procesar el error, dejando solo el toast de error. No es un bug.

**Q4: Ruido blanco (400 B/s por 10 min)**

1. Pasa esAudioMudo porque 400 < 300 es false.
2. Llamada 1 (Acta) procesa el audio. Las instrucciones del prompt obligan a devolver: `titulo: "Reunión sin contenido audible"`, resumen iniciando con "No se detectó contenido audible.", `participantes: []` (`artifacts/api-server/src/routes/actas.ts:47-48`).
3. Evaluación looksEmpty (`artifacts/api-server/src/routes/actas.ts:284`): `titulo === "Reunión sin contenido audible"` es verdadero, volviendo a todo looksEmpty verdadero.
4. Efecto: Solo un `req.log.warn` en consola (CTX-C).
5. Persistencia Acta: Se guarda correctamente en Firestore y retorna 201 al cliente con un toast silente (CTX-C).
6. Llamada 2 (Síntesis) corre en background. Por instrucción del prompt, genera un texto que contiene exactamente la línea [SIN CONTENIDO AUDIBLE] en la sección ===TRANSCRIPCION===, dejando el resto de secciones vacías (`artifacts/api-server/src/routes/actas.ts:71-72`).
7. Persistencia Síntesis: CTX-E degrada las secciones sin contenido a strings o listas vacías, truncando si es necesario, y guardando el documento en la colección `sintesis/{actaId}`.
8. Veredicto: El comportamiento observado cumple rigurosamente con el diseño dictaminado. No hay errores de ejecución ni pérdida de datos por falsos positivos.

## 3. Refutación de Trampas Anti-Aprobación Automática (T1..T5)

- **T1:** Las transmisiones Opus DTX con un hablante normal superan cómodamente los 300 B/s en promedio temporal, dado que los fragmentos activos (>2000 B/s) levantan fácilmente el ratio ponderado, tal como se justifica matemáticamente con un ratio de silencio (~250) y voz normal (2000-4000). El umbral 300 deja margen adecuado.
- **T2:** El abuso de msDuration por parte del cliente es irrelevante para la estabilidad general del sistema. Si el cliente envía 4999 en vez de un valor real (bypass del guard), sólo gasta sus propios límites de cuota de Firebase y se expone al procesamiento inútil. Si manda 10^9, choca con el clamp de 600000 en el backend (`artifacts/api-server/src/lib/audioGuard.ts:11`). Afecta a sí mismo.
- **T3:** En `artifacts/api-server/src/routes/actas.ts:282`, la keyword es "no se detectó". El resumen generado por mandato (`artifacts/api-server/src/routes/actas.ts:47`) incluye la frase "No se detectó contenido audible.". El bloque evalúa `resumen.toLowerCase().includes(kw)` (`artifacts/api-server/src/routes/actas.ts:285`), por lo cual "no se detectó" matchea exitosamente con "no se detectó contenido audible.". El match de título `titulo === "Reunión sin contenido audible"` evalúa carácter a carácter. Mecanismo sincronizado, cero desajustes residuales.
- **T4:** La cláusula "Sin embargo, si detectas AL MENOS UN fragmento de conversación humana, omite esta regla, ignora los silencios, redacta el acta y extrae el contenido normalmente..." (`artifacts/api-server/src/routes/actas.ts:47`) blinda a Gemini contra el abandono temprano. La E2E adjunta prueba que un audio mixto no activa el centinela por culpa del silencio.
- **T5:** La configuración `{ thinkingBudget: 4096 }` se inyecta en `generarSintesisEnBackground` (`artifacts/api-server/src/routes/actas.ts:200`) que es asíncrona y puede demorar. Su cuota permite planificar la síntesis larga de un límite de 65536. Adicionalmente, el CTX-B muestra textualmente que en `callGemini(...)` el thinkingConfig NO fue inyectado, protegiendo así el response HTTP sincrónico.

## 4. Opiniones Fundadas (D1..D4)

- **D1 (Footgun operativo env):** En JavaScript, un parse numérico como Number("0") u omisiones falsy evaluarán al uso de la rama derecha del ||. Si alguien desea desactivar el guard desde variables de entorno con 0, activará el fallback de 300, requiriendo ingresar un valor como 0.001 para superarlo. Este comportamiento "Fail-Safe", aunque poco intuitivo, es óptimo para la resiliencia en un despliegue donde un tipográfico no deba desconectar el guard por accidente. No amerita refactor, pero debe documentarse operativamente.
- **D2 (Overhead de fetch no descontado):** Convertir el wall-clock estricto en "cantidad máxima de attempts" (maxAttempts) es preferible, ya que abstrae la latencia de red. Previene agotar el ciclo prematuramente debido a congestión de la propia red durante el polling y otorga a la File API una cuota justa de verificaciones reales. El impacto extra de tiempo absoluto es asumible.
- **D3 (Falso match en resumen largo):** Un monólogo con 1 participante que diga "...no se detectó el error..." activará la vía legacy keyword de looksEmpty. Sin embargo, las consecuencias documentadas (CTX-C) indican que el flujo no se interrumpe y los datos se persisten en su totalidad (status 201), sólo generando un WARN del servidor y un Toast silente en la UX. Dado que el título no matcheará al centinela exacto, es una regresión muy menor (UI toast errático) sobre un fallback que ya era imperfecto, aceptable a favor de priorizar la persistencia.
- **D4 (Síntesis con basura estructural):** Guardar un documento con secciones vacías o una única línea centinela es correcto desde el diseño del pipeline, pues provee observabilidad (Auditoría de Transacciones), asegurando que un fallo de transcripción no parezca una síntesis no lanzada o fallida por crash. Mantiene consistencia entre colecciones de Firestore.

## 5. Veredicto Global

**APROBADO**

---
---

# ANEXO — Validación anti-bluff del Arquitecto (17-07-2026)

**Checklist del contrato:** tabla C1..C6 con verdictos (6 CONFIRMADO) ✅ · Q1..Q4 respondidas con trazas y valores concretos ✅ · T1..T5 refutadas con evidencia ✅ · D1..D4 opinadas ✅ · veredicto global único ✅ · citas archivo:línea presentes en todas las verificaciones ✅.

**Citas verificadas con grep sobre el código real:**
- `audioGuard.ts:4-7` (esAudioMudo) y `:10-12` (calcularMaxWaitMs) ✅ exactas.
- `actas.ts:250-258` guard en handler ✅ (minBps en 250, 422 en 256).
- Centinelas: acta en `actas.ts:48`, síntesis en `:72` — dentro de los rangos citados (47-48 / 71-72) ✅.
- `looksEmpty`: titulo 281, keywords 282, `titulo ===` 284, `includes` en **286** (el Auditor citó 285 — desfase de ±1 línea, sin efecto sustantivo) ✅.
- `thinkingConfig` en `actas.ts:200`, única aparición en el archivo ✅. `text-espera` en `home.tsx:205-206` ✅.

**Aritmética re-ejecutada (node, no de memoria):** 8106/31,939s = **253,80** → true ✅ · 1.725.000/3.600s = **479,17** → false ✅ · 300,0 exacto → false (pasa) ✅ · `calc(55958)` = **45.595,8** → ceil = **23** intentos ✅ · `calc(7.200.000)` = **600.000** → **300** intentos ✅ · `"No se detectó contenido audible.".toLowerCase().includes("no se detectó")` = **true** ✅ (T3, el punto exacto de OBS-1, esta vez verificado correctamente por el Auditor) · semántica D1 confirmada: `Number("0")||300 = 300`, `Number("abc")||300 = 300`, `Number("0.001")||300 = 0.001` ✅.

**Observaciones del Arquitecto (no bloqueantes, no alteran el veredicto):**
- **OBS-A (sobre T2):** "sólo gasta sus propios límites de cuota de Firebase... afecta a sí mismo" es impreciso: la cuota de Gemini API es del PROYECTO (API key compartida), no del usuario. Sin embargo, el bypass de `msDuration` solo devuelve al comportamiento pre-guard (sin protección alguna), no lo empeora — no es bug de la tanda. Mitigación futura candidata a backlog: validar `msDuration` server-side contra la duración real del contenedor webm.
- **OBS-B:** desfase ±1 en la cita de `includes` (285 vs 286), irrelevante.

**Veredicto de la validación: RESPUESTA VÁLIDA — APROBADO aceptado.** D1 y D3 coinciden con las dudas declaradas del Arquitecto y quedan resueltas como "documentar, no refactorizar". Condición de F7 (lado Auditor) CUMPLIDA; falta el GATE G2 del Director.

━━ AVISO DE TRASPASO ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CICLO      : 2026-07-14_robustez_pipeline
FASE       : F7 — Cierre (GATE G2)
TURNO DE   : Director
ENTREGAR   : Decisión de gate: autorizar commit+push de la tanda
ADJUNTOS   : Ninguno
DESTINO    : Sesión del Arquitecto (esta misma)
ACCIÓN     : Conceder o denegar G2 (commit en ActaExpressWeb rama
             linux + cierre de expediente y bitácora en NexoExpress)
VUELVE A   : Arquitecto, que ejecuta el cierre F7 completo
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
