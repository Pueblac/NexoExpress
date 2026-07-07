# Expediente 2026-07-07_transcripcion_sintesis — Prompt de auditoría de CÓDIGO (ronda 1)

**Ciclo:** Auditoría de código (paso 4 de METODOLOGIA_DUAL_IA.md), posterior al diseño aprobado en `respuesta_diseno_ronda1.md`.

## Instrucciones de operación para el Director

1. Conversación **NUEVA** en Gemini 3.1 Pro High.
2. **Adjuntar EXACTAMENTE estos 4 archivos** (nada más):
   - `ActaExpressWeb/artifacts/api-server/src/routes/actas.ts`
   - `ActaExpressWeb/artifacts/api-server/src/lib/firebaseAdmin.ts`
   - `NexoExpress/auditorias/2026-07-07_transcripcion_sintesis/firestore_rules_desplegadas.rules`
   - `NexoExpress/auditorias/2026-07-07_transcripcion_sintesis/evidencia_mt02.md`
3. Pegar como primer mensaje lo que está entre `=== PROMPT ===`.
4. Guardar la respuesta completa TAL CUAL como `respuesta_auditoria_ronda1.md` en esta carpeta y avisar al Ingeniero (no hace falta pegarla en el chat).
5. Si llega sin citas archivo:línea o sin trazas: *"Auditoría INVÁLIDA según el contrato: faltan citas/trazas. Reenvíala completa."*

---

=== PROMPT ===

# Rol y regla de oro
Eres auditor adversarial de código del ecosistema Express. El implementador (otra IA) afirma haber implementado la generación de transcripción y análisis profundo en background conforme a un diseño que TÚ aprobaste con cambios (dos llamadas a Gemini: acta síncrona + síntesis asíncrona; flag `generarSintesis` default false; purga de campos pesados; truncado a 800k chars). **Tu hipótesis de trabajo es que la implementación está mal o traiciona el diseño hasta que se demuestre lo contrario.** No agradezcas, no resumas, no elogies. Cada afirmación sin cita textual del material adjunto (archivo y nº de línea) se considera inventada.

# Formato obligatorio de CADA verificación
CLAIM → EVIDENCIA (cita textual, archivo:línea) → TRAZA (ejecución simbólica paso a paso con valores concretos) → VERDICTO (CONFIRMADO / BUG / NO VERIFICABLE CON LO ADJUNTO). Lo no adjuntado es NO VERIFICABLE — prohibido rellenarlo con suposiciones.

# Material adjunto
1. `actas.ts` — ruta del endpoint POST /actas/process y helpers de Gemini/síntesis.
2. `firebaseAdmin.ts` — capa REST de Firestore (incluye el fix de `firestoreSet`).
3. `firestore_rules_desplegadas.rules` — reglas de seguridad HOY desplegadas en el proyecto `actaexpress`.
4. `evidencia_mt02.md` — evidencia literal del E2E ejecutado (respuesta 201 real + documento `sintesis/` real leído de Firestore).

# Claims a verificar
- **C1 — Fidelidad al diseño: dos llamadas.** La llamada síncrona del acta usa `ACTA_PROMPT` con `maxOutputTokens: 4096` y `responseMimeType: "application/json"` (sin cambios funcionales sobre el flujo original), y el `201` se envía ANTES de disparar la síntesis. La llamada de síntesis usa `SINTESIS_PROMPT` con `maxOutputTokens: 65536` y `responseMimeType: "text/plain"`, reutiliza el MISMO `fileUri` ya subido, y escribe exclusivamente `sintesis/{id}`.
- **C2 — No bloqueo y no caída.** `generarSintesisEnBackground` se invoca sin `await` y con `.catch` que loggea; un fallo en la síntesis no puede ni retrasar el `201` ni tumbar el proceso Node ni dejar promesa sin manejar.
- **C3 — Purga anti-derrame.** `actas/{id}` no puede contener `transcripcion`, `analisis_profundo`, `preguntas_sin_resolver` ni `temas_clave` aunque Gemini los devolviera espontáneamente en el JSON del acta. Traza el spread completo de `docData`.
- **C4 — Flag de costo.** Con `generarSintesis` ausente, `false`, o cualquier valor no-`true` (p. ej. `"true"` string, `1`), NO se dispara la llamada 2. Solo `true` booleano la dispara.
- **C5 — Parser de secciones.** `parseSintesisText` mapea los 4 delimitadores a los 4 campos del schema; con secciones vacías o ausentes degrada a `""`/`[]` sin lanzar; las listas se derivan de líneas con prefijo "- ".
- **C6 — Truncado.** Transcripción > 800.000 chars se corta y recibe el sufijo literal de truncamiento antes de `firestoreSet`.
- **C7 — Fix de `firestoreSet`.** El `updateMask.fieldPaths` ahora va repetido por campo (antes: unido por comas → 400 INVALID_ARGUMENT, reproducido en `evidencia_mt02.md` §Hallazgos). Verifica que la URL resultante es válida para la API REST de Firestore.
- **C8 — Ejecución simbólica completa (obligatoria).** Traza: `POST /actas/process` con `{mimeType:"audio/wav", msDuration: 29300, generarSintesis: true}`, Gemini devolviendo un acta válida y un texto de síntesis con las 4 secciones → estado final de `actas/{id}` y `sintesis/{id}` campo por campo, y compáralo contra el documento real de `evidencia_mt02.md`.

# Dudas declaradas por el implementador
- **D1 (la que más me preocupa):** el truncado C6 opera en CARACTERES (`.slice(0, 800000)`), pero el límite de Firestore es en BYTES (1.048.576). Con contenido mayoritariamente multibyte (CJK, emojis, cirílico) 800k chars pueden superar 1.6 MB y el `firestoreSet` fallaría igual (capturado por el catch, síntesis perdida en silencio). Para reuniones en español el margen medido es ~166 KB. ¿Es un BUG que exige truncado por bytes (`Buffer.byteLength`) o una observación aceptable para esta fase?
- **D2:** si la transcripción hablada contuviera literalmente un delimitador (alguien dicta "===TEMAS_CLAVE==="), el parser cortaría la transcripción en ese punto. Lo considero improbable y sin impacto de seguridad, pero no imposible.
- **D3:** el `idToken` del request se pasa a la tarea background; vigencia ~1h. Para el audio máximo actual (~150 MB) ¿hay escenario realista donde la llamada 2 exceda la vigencia?
- **D4:** no hay test unitario A/B del parser (`parseSintesisText`); la protección actual es solo el E2E. ¿Bloqueante o deuda aceptable documentada?
- **D5:** la heurística de audio silencioso (`looksEmpty`) quedó intacta pero esta ronda no la probó con audio mudo; si dispara, la síntesis igualmente se genera cuando el flag es true (posible costo inútil en audio vacío).

# Preguntas de control (respóndelas TODAS; son parte del entregable)
- **Q1:** Copia textualmente el bloque de purga de campos de `actas.ts` (las 5 líneas de `actaLimpia`) con sus números de línea.
- **Q2:** ¿Qué devuelve exactamente `parseSintesisText("texto sin ningún delimitador")`? Traza el valor de cada uno de los 4 campos.
- **Q3:** En `firebaseAdmin.ts`, escribe la URL COMPLETA (con query string) que genera `firestoreSet("sintesis", "abc", {actaId:..., ownerId:...}, token)` tras el fix.
- **Q4:** Según `firestore_rules_desplegadas.rules`, ¿puede el usuario A leer `sintesis/{id}` de un acta del usuario B? Cita la regla exacta y traza la evaluación.

# Anti-aprobación-automática
Si tu veredicto global es APROBADO o APROBADO CON OBSERVACIONES, debes ADEMÁS demostrar por qué cada trampa NO aplica, con evidencia:
- **T1:** Dos POST concurrentes del mismo usuario con `generarSintesis: true` → ¿pueden las tareas background pisarse los documentos entre sí o escribir la síntesis con el `actaId` cruzado?
- **T2:** Gemini responde la llamada 2 con texto que incluye los delimitadores DESORDENADOS o duplicados → ¿el parser lanza, mezcla secciones, o degrada de forma segura?
- **T3:** `firestoreAdd` del acta tiene éxito pero la llamada 2 falla (red, 429 del tier gratuito de Gemini) → ¿queda algún registro de que la síntesis se perdió, o muere en silencio otra vez (la trampa que ya se materializó una vez con las reglas)?
- **T4:** Un cliente malicioso envía `generarSintesis: true` en un loop para inflar el gasto de tokens de salida del servidor → ¿existe alguna protección (rate limit, créditos) o queda como riesgo aceptado y documentado?
- **T5:** El JSON del acta llega con `transcripcion` incluida espontáneamente por el modelo pese al prompt → traza que aún así `actas/{id}` queda limpio.

# Entregable final
1. Tabla C1..C8 con verdictos. 2. Respuestas Q1..Q4. 3. Refutación T1..T5 si apruebas. 4. Opinión fundada sobre D1..D5 (en D1 exige postura: BUG u observación). 5. Veredicto global (APROBADO / APROBADO CON OBSERVACIONES / RECHAZADO).

**Formato de entrega:** redacta TODA tu respuesta como un único documento markdown listo para archivar tal cual (será guardado como `respuesta_auditoria_ronda1.md` sin edición). Una auditoría sin citas archivo:línea o sin las trazas obligatorias es INVÁLIDA y será devuelta.

=== FIN PROMPT ===
