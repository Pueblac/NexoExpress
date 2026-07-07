# Expediente 2026-07-07_transcripcion_sintesis — Prompt de revisión de DISEÑO

**Ciclo:** Diseño (paso 1 de METODOLOGIA_DUAL_IA.md)
**Meta:** [ActaExpressWeb] Enriquecer el prompt de Gemini del endpoint `/actas/process` para obtener transcripción completa + análisis profundo y poblar `sintesis/` con contenido real.
**Preparado por:** Ingeniero (Claude Fable 5) — sesión 07-07-2026

## Instrucciones de operación para el Director

1. Conversación **NUEVA** en Gemini 3.1 Pro High.
2. **Sin adjuntos** — todo el contexto verificado va dentro del prompt.
3. Pegar como primer mensaje únicamente lo que está entre las marcas `=== PROMPT ===`.
4. Si la respuesta llega sin veredicto por claim o sin responder TODAS las Q, responder solo: *"Auditoría INVÁLIDA según el contrato: faltan verdictos/respuestas Q. Reenvíala completa."*
5. Pegar la respuesta literal al Ingeniero para validación anti-bluff antes de implementar nada.

---

=== PROMPT ===

# Rol y regla de oro
Eres auditor adversarial de diseño del ecosistema Express. El implementador (otra IA) propone un diseño para que el endpoint de generación de actas también produzca transcripción completa y análisis profundo. **Tu hipótesis de trabajo es que el diseño está mal o incompleto hasta que se demuestre lo contrario.** No eres un asistente conversacional: no agradezcas, no resumas, no elogies. Cada afirmación tuya debe apoyarse en el contexto citado abajo (referéncialo por sección/línea); lo que no esté en este prompt es NO VERIFICABLE — prohibido rellenarlo con suposiciones.

# Formato obligatorio de CADA verificación
CLAIM → EVIDENCIA (cita del contexto de este prompt) → TRAZA (razonamiento paso a paso con valores concretos) → VERDICTO (SÓLIDO / DÉBIL / RECHAZADO).

# Material adjunto
Ninguno — revisión de diseño. Contexto verificado a continuación.

# Contexto verificado (extraído literalmente del código real el 07-07-2026)

**Sistema:** ActaExpressWeb. Backend Express/TypeScript (`artifacts/api-server/src/routes/actas.ts`). El endpoint `POST /actas/process` recibe audio en base64, lo sube a la File API de Gemini, llama a `gemini-2.5-flash` con `generateContent` y guarda el resultado en Firestore.

**CTX-1 — Prompt actual (`ACTA_PROMPT`, actas.ts:18-45).** Pide ÚNICAMENTE un JSON con: `titulo`, `fecha`, `duracionMinutos`, `participantes[]`, `resumen`, `puntosImportantes[]`, `acuerdos[]`, `pendientes[]` (objetos `{tarea, responsable, fecha}`). Termina con: "No incluyas texto ni explicaciones fuera del JSON". NO pide transcripción ni análisis.

**CTX-2 — Llamada a Gemini (actas.ts:92-112), literal:**
```ts
async function callGemini(fileUri: string, mimeType: string): Promise<Record<string, unknown>> {
  const res = await fetch(
    `${GEMINI_BASE}/v1beta/models/${MODEL}:generateContent?key=${GEMINI_API_KEY}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        contents: [{ parts: [{ text: ACTA_PROMPT }, { fileData: { mimeType, fileUri } }] }],
        generationConfig: { temperature: 0.2, maxOutputTokens: 4096, responseMimeType: "application/json" },
      }),
    }
  );
  if (!res.ok) { /* lanza Error con err.error.message */ }
  const data = await res.json() as { candidates?: Array<{ content?: { parts?: Array<{ text?: string }> } }> };
  const text = data.candidates?.[0]?.content?.parts?.[0]?.text;
  if (!text) throw new Error("Gemini devolvió una respuesta vacía");
  return JSON.parse(text) as Record<string, unknown>;
}
```
Nota verificada: **no se inspecciona `finishReason`** en ninguna parte del archivo.

**CTX-3 — Escritura del acta (actas.ts:177-186), literal:**
```ts
const docData: Record<string, unknown> = {
  ...actaData,
  ownerId: req.uid!,
  duracionMinutos,
  plataforma: "web",
  audioStoragePath: null,
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
};
const id = await firestoreAdd("actas", docData, req.idToken!);
```
Es decir: **todo campo extra que Gemini devuelva se derrama en `actas/{id}` vía spread**.

**CTX-4 — Escritura de síntesis (actas.ts:189-212).** Ya existe un bloque try/catch "no crítico" que escribe `sintesis/{id}` con: `actaId`, `ownerId`, `transcripcion` (lee `actaData.transcripcion`, hoy siempre `""`), `analisis_profundo` (hoy `""`), `preguntas_sin_resolver` (hoy `[]`), `temas_clave` (fallback a `puntosImportantes`), `contexto_previo: ""`, `createdAt`. Si `firestoreSet` falla, solo se emite `req.log.warn` y el flujo continúa (el usuario no lo ve).

**CTX-5 — Heurística de audio silencioso (actas.ts:148-153), literal:**
```ts
const silenceKeywords = ["no se pudo", "no audible", "no hay audio", "sin contenido", "silencio"];
const looksEmpty =
  participantes.length <= 1 &&
  silenceKeywords.some((kw) => resumen.toLowerCase().includes(kw));
```

**CTX-6 — Contrato de datos (`schemas/firestore_schema.md`, colección `sintesis/{actaId}`).** Campos documentados: `actaId`, `ownerId`, `transcripcion` ("texto completo hablado"), `analisis_profundo`, `preguntas_sin_resolver[]`, `temas_clave[]`, `contexto_previo`, `createdAt`. Razón de separación documentada: "Documentos grandes. No inflar la colección `actas/` que se lee frecuentemente." Android aún no escribe `sintesis/` (pendiente, regla "Web primero"). Límite duro de Firestore: 1 MiB por documento.

# Diseño propuesto (claims a verificar)

- **C1 — Una sola llamada.** Se enriquece `ACTA_PROMPT` para que el MISMO `generateContent` devuelva el JSON actual + 4 campos nuevos: `transcripcion` (transcripción completa, con hablantes cuando sean identificables), `analisis_profundo`, `preguntas_sin_resolver[]`, `temas_clave[]`. Se descarta una segunda llamada solo-transcripción porque duplicaría el costo de procesar el mismo audio y la latencia percibida.
- **C2 — Presupuesto de salida.** `maxOutputTokens` sube de 4096 a 65536 (máximo de salida de gemini-2.5-flash). `temperature: 0.2` y `responseMimeType: "application/json"` se mantienen.
- **C3 — Guardia anti-truncamiento con degradación elegante.** `callGemini` pasa a inspeccionar `finishReason`. Si `finishReason === "MAX_TOKENS"` o `JSON.parse` lanza, se hace UN reintento con el `ACTA_PROMPT` original (sin síntesis) para garantizar que el usuario nunca pierda el acta; la síntesis queda vacía y se registra warn. Sin segundo reintento (regla anti-bucle).
- **C4 — Separación estricta acta/síntesis.** Antes de construir `docData`, los 4 campos de síntesis se EXTRAEN de `actaData` (destructuring) de modo que `actas/{id}` no los contenga jamás. Es corrección obligada del spread de CTX-3.
- **C5 — Sin cambio de schema.** Los 4 campos ya están documentados en `sintesis/` (CTX-6). `contexto_previo` sigue siendo `""` (Fase 3). No se toca `firestore_schema.md`.
- **C6 — Guardia de tamaño Firestore.** `transcripcion` se trunca a 800.000 caracteres antes de `firestoreSet`, añadiendo el sufijo `"\n[TRANSCRIPCIÓN TRUNCADA POR LÍMITE DE ALMACENAMIENTO]"`, para no chocar con el límite de 1 MiB por documento.

# Dudas declaradas por el implementador
- **D1:** ¿Es fiable `responseMimeType: "application/json"` cuando un solo campo string pesa cientos de KB? Sospecho posibilidad de truncamiento u degradación de calidad del JSON en salidas muy largas incluso por debajo de 65536 tokens.
- **D2:** Hoy no se inspecciona `finishReason` (CTX-2): sospecho que ya existen truncamientos silenciosos en producción con 4096 tokens y reuniones largas — el diseño C3 lo corrige, pero ¿debería además loggearse `usageMetadata` para dimensionar el problema?
- **D3:** Costo: pedir la transcripción completa multiplica los tokens de salida de CADA acta. No hay hoy descuento de `remainingCredits` por tokens. ¿Es un riesgo aceptable en esta fase o el diseño debe incluir un interruptor (flag por request o por usuario)?
- **D4:** Con el prompt enriquecido, ¿la heurística de silencio (CTX-5) sigue disparando igual, o el modelo tenderá a redactar el `resumen` distinto y hay que adaptar las keywords?

# Preguntas de control (respóndelas TODAS con recomendación ÚNICA y justificada; "depende" no es respuesta)
- **Q1:** ¿Una llamada (C1) o dos llamadas separadas (acta corta + transcripción aparte)? Da UNA recomendación y su justificación con números aproximados de costo/latencia/riesgo de truncamiento.
- **Q2:** ¿El reintento de C3 es la degradación correcta, o recomiendas otra estrategia concreta (p. ej. pedir transcripción como ÚLTIMO campo del JSON, o partir en dos llamadas solo cuando `msDuration` supere un umbral)? UNA estrategia final.
- **Q3:** ¿Qué debe devolver el `201` del endpoint: el acta sola (como hoy), o acta + síntesis completa? Considera que el frontend actual no consume la síntesis y que la transcripción puede pesar cientos de KB por respuesta HTTP.
- **Q4:** Traza el escenario completo con valores concretos: reunión de 90 minutos, transcripción estimada de ~110.000 caracteres. Indica el estado final esperado de `actas/{id}` y `sintesis/{id}` campo por campo bajo el diseño propuesto, y en qué punto exacto fallaría si `maxOutputTokens` siguiera en 4096.

# Anti-aprobación-automática
Si tu veredicto global es APROBADO o APROBADO CON CAMBIOS, debes ADEMÁS demostrar por qué cada una de estas trampas NO aplica (o qué cambio del diseño la neutraliza), con evidencia del contexto:
- **T1:** Reunión de 2+ horas cuya transcripción excede el presupuesto de salida → JSON truncado → sin C3, `JSON.parse` lanza y el usuario pierde el acta COMPLETA (regresión del flujo principal por una feature secundaria).
- **T2:** El spread de CTX-3 derrama `transcripcion` y `analisis_profundo` dentro de `actas/{id}`, violando la razón de separación de CTX-6 e inflando la colección de lectura frecuente.
- **T3:** Documento `sintesis/` > 1 MiB → `firestoreSet` falla → por el catch "no crítico" de CTX-4 la feature muere en silencio y nadie lo detecta.
- **T4:** Al crecer y complejizarse el prompt, el modelo devuelve claves renombradas (`transcripción` con tilde, `transcript`) o texto fuera del JSON → los typeof/Array.isArray de CTX-4 degradan a `""`/`[]` en silencio → síntesis vacía sin error visible.
- **T5:** Paridad Android: Android aún no escribe `sintesis/` (CTX-6). El diseño debe apoyarse SOLO en campos ya documentados del schema para que Android pueda replicarlo sin renegociar el contrato.

# Entregable final
1. Tabla C1..C6 con verdictos (SÓLIDO / DÉBIL / RECHAZADO + cambio requerido si aplica).
2. Respuestas Q1..Q4 (recomendación única cada una).
3. Refutación de T1..T5 si apruebas.
4. Opinión fundada sobre D1..D4.
5. Veredicto global: APROBADO / APROBADO CON CAMBIOS (listar los cambios EXACTOS) / RECHAZADO (razón + contra-diseño mínimo).

Una revisión sin verdicto por claim, sin las Q respondidas o sin la traza de Q4 es INVÁLIDA y será devuelta.

=== FIN PROMPT ===
