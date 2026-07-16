# Expediente 2026-07-14_robustez_pipeline — Prompt de revisión de DISEÑO (ronda 1)

**Ciclo:** F1 Diseño (METODOLOGIA_TRIPLE_IA.md) · **Meta:** [ActaExpressWeb] Robustez del pipeline (hallazgos H1+H2+H5 del piloto MT-04): audio defectuoso o reunión larga NUNCA producen acta confabulada, síntesis truncada ni fallo por timeout.
**Plan aprobado en G0 (13-07-2026):** MT-R1 guard anti-audio-mudo · MT-R2 prompts anti-alucinación · MT-R3 thinkingBudget · MT-R4 timeout proporcional · MT-R5 UX de expectativa.
**Preparado por:** Arquitecto (Claude Fable 5)

## Instrucciones de operación para el Director

1. Conversación **NUEVA** en Gemini 3.1 Pro High.
2. **Inicialización de identidad** — primer mensaje: *"Rol: Auditor del ciclo 2026-07-14_robustez_pipeline, metodología v2 del ecosistema Express. Confirma recepción sin accionar; acepta únicamente artefactos cuyo TURNO DE diga Auditor."*
3. **Sin adjuntos** — contexto verificado dentro del prompt.
4. Segundo mensaje: solo el bloque entre `=== PROMPT ===`.
5. Respuesta incompleta → frase de devolución estándar.
6. Guardar la respuesta tal cual como `respuesta_diseno_ronda1.md` y avisar al Arquitecto.

---

=== PROMPT ===

# Rol y regla de oro
Eres auditor adversarial de diseño del ecosistema Express. El Arquitecto (otra IA) propone 5 cambios de robustez al pipeline de actas que un Ingeniero (tercera IA) implementará según spec. **Tu hipótesis de trabajo es que el diseño está mal o incompleto hasta que se demuestre lo contrario.** No agradezcas, no resumas, no elogies. Apoya cada afirmación en el contexto citado abajo; lo que no esté en este prompt es NO VERIFICABLE — prohibido rellenarlo con suposiciones.

# Formato obligatorio de CADA verificación
CLAIM → EVIDENCIA (cita del contexto) → TRAZA (razonamiento con valores concretos) → VERDICTO (SÓLIDO / DÉBIL / RECHAZADO).

# Material adjunto
Ninguno — revisión de diseño. Contexto verificado a continuación.

# Contexto verificado (extraído del código real y de logs de producción local, 13-07-2026)

**Sistema:** ActaExpressWeb. Backend Express/TS (`artifacts/api-server/src/routes/actas.ts`): POST `/actas/process` recibe audio base64 → sube a la File API de Gemini → espera estado ACTIVE → llamada 1 síncrona (acta JSON, 4096 tokens) → 201 → si `generarSintesis: true`, llamada 2 en background (texto plano, 65536 tokens) → `sintesis/{actaId}`.

**CTX-1 — Datos EMPÍRICOS de los logs del piloto (11→13-07):**
- Audio SILENCIOSO real (mic apagado): 10.5 KB / 42.5 s ≈ **253 B/s**; segundo caso 8.9 KB / 36.2 s ≈ **246 B/s** (WebM/Opus con DTX comprime silencio a casi nada).
- Audio con VOZ real (guion leído): transcripción fiel; voz en Opus produce típicamente ≥ 2.000-4.000 B/s.
- Sobre audio silencioso, Gemini se comportó de forma INTERMITENTE: a veces confesó ("Reunión sin contenido audible", transcripción "Participante 1: Silencio."), a veces CONFABULÓ actas de negocios completas con acuerdos inventados (2 casos reales documentados, distintos entre sí sobre el mismo audio).
- Llamada de síntesis: `thoughtsTokenCount` osciló entre despreciable (latencia ~10 s) y **62.912 de 65.536 tokens** (97% del presupuesto en razonamiento interno, latencia ~4 min, `finishReason: STOP` rozando el techo). En gemini-2.5-flash `maxOutputTokens` INCLUYE los thoughts → una transcripción larga + thoughts descontrolados = MAX_TOKENS (y el diseño vigente, correctamente, no reintenta).

**CTX-2 — Zona del guard (actas.ts:236-249, literal):**
```ts
const audioSizeBytes = Math.round((audioBase64.length * 3) / 4);
const audioSizeKB = (audioSizeBytes / 1024).toFixed(1);
const audioSizeMB = (audioSizeBytes / (1024 * 1024)).toFixed(2);
req.log.info({ mimeType, msDuration, audioSizeKB, audioSizeMB, uid: req.uid }, "processAudio: received audio");
try {
  const uploadedFile = await uploadToGemini(audioBase64, mimeType);
  ...
  const activeFile = await waitForFileActive(uploadedFile.name);
```
El handler ya calcula `audioSizeBytes` y tiene `msDuration` ANTES de subir nada. Errores del try se responden `500 {error: msg}`; el frontend los muestra en un toast destructivo con `err.message` ("Error al procesar").

**CTX-3 — Espera de archivo (actas.ts:108-117, literal):**
```ts
async function waitForFileActive(fileName: string): Promise<GeminiFile> {
  for (let i = 0; i < 20; i++) {
    const res = await fetch(`${GEMINI_BASE}/v1beta/${fileName}?key=${GEMINI_API_KEY}`);
    const file = await res.json() as GeminiFile;
    if (file.state === "ACTIVE") return file;
    if (file.state === "FAILED") throw new Error("El archivo de audio falló al procesarse");
    await new Promise((r) => setTimeout(r, 2000));
  }
  throw new Error("Timeout: el archivo tardó demasiado en procesarse");
}
```
**Techo fijo: 20×2 s = 40 s**, independiente de la duración del audio. Dato real: audio de 42 s quedó ACTIVE en <1 s. Sin datos empíricos para audios de 30-60 min. `express.json({ limit: "200mb" })` verificado en app.ts:30 (el body de ~1-2 h de audio cabe).

**CTX-4 — Prompt del ACTA (actas.ts:19-46, extracto de reglas):** pide JSON con titulo/fecha/duracionMinutos/participantes/resumen/puntosImportantes/acuerdos/pendientes; "Responde en el idioma en que se realizó la reunión"; reglas: "Si no identificas nombres usa Participante 1...", "Si no hubo acuerdos explícitos devuelve []". **NO contiene NINGUNA instrucción sobre audio inaudible** — ante silencio, el modelo queda libre de inventar (CTX-1). Heurística downstream (actas.ts:263-268): `looksEmpty = participantes.length <= 1 && silenceKeywords.some(kw => resumen.toLowerCase().includes(kw))` con keywords `["no se pudo","no audible","no hay audio","sin contenido","silencio"]` — bypasseada si el modelo confabula un resumen plausible.

**CTX-5 — Prompt de SÍNTESIS (actas.ts:51-69):** texto plano con 4 secciones delimitadas (===TRANSCRIPCION===, ===ANALISIS_PROFUNDO===, ===PREGUNTAS_SIN_RESOLVER===, ===TEMAS_CLAVE===); transcripción literal con hablantes. Tampoco tiene instrucción de inaudibilidad. Config actual de la llamada (actas.ts:191-195): `{ temperature: 0.2, maxOutputTokens: 65536, responseMimeType: "text/plain" }` — SIN `thinkingConfig`. La API v1beta de gemini-2.5-flash acepta `generationConfig.thinkingConfig.thinkingBudget` (0 = desactiva razonamiento extendido).

**CTX-6 — Frontend (home.tsx):** durante `processAudio.isPending` el botón muestra spinner y el estado dice "Procesando con IA..."; los errores del POST se muestran con toast destructivo `err.message`. Restricción de fase: sin cambios de schema Firestore, reglas ni `openapi.yaml`.

# Diseño propuesto (claims a verificar)

- **C1 — Guard de audio mudo (MT-R1).** En el handler, ANTES de `uploadToGemini`: si `msDuration >= 5000` y `bytesPerSec = audioSizeBytes/(msDuration/1000) < MIN_AUDIO_BPS` (env, **default 500 B/s**), responder **422** `{ error: "No se detectó señal de audio en la grabación (micrófono apagado o en silencio). Revisa tu micrófono e inténtalo de nuevo." }` y loggear warn con los números. Justificación del umbral: silencio real medido ≈ 250 B/s; voz ≥ ~2.000 B/s (CTX-1) — 500 es 2× el silencio y 4× bajo la voz. El frontend ya muestra `err.message` (CTX-2) sin cambios. Cero tokens gastados en audio muerto.
- **C2 — Centinelas anti-confabulación (MT-R2).** Añadir a AMBOS prompts una regla de audibilidad con salida DETERMINISTA: ACTA → si no hay voz inteligible, devolver exactamente `titulo: "Reunión sin contenido audible"`, `resumen` comenzando con "No se detectó contenido audible", `participantes: []` y arrays vacíos; SÍNTESIS → sección TRANSCRIPCION con únicamente `[SIN CONTENIDO AUDIBLE]`. Más la prohibición general en ambos: *"Transcribe/describe ÚNICAMENTE lo que se oye. PROHIBIDO inventar o inferir contenido que no esté en el audio; ante duda, declara la ausencia."* La heurística `looksEmpty` se conserva y se le suma el match exacto del título centinela (dos capas). No se toca la regla de idioma.
- **C3 — thinkingBudget acotado SOLO en la síntesis (MT-R3).** `thinkingConfig: { thinkingBudget: 0 }` en la llamada 2. La llamada 1 (acta) NO se toca en este ciclo (thoughts medidos ~790, aporta estructuración; un cambio a la vez). Meta: liberar el presupuesto de 65.536 tokens para el texto y acotar la latencia del peor caso (~4 min → segundos).
- **C4 — Timeout proporcional (MT-R4).** `waitForFileActive(fileName, msDuration)`: `maxWaitMs = clamp(40_000, 40_000 + msDuration/10, 600_000)` (1 h de audio → ~400 s de espera máx; techo absoluto 10 min), poll cada 2 s como hoy, mismo mensaje de error. Firma nueva retrocompatible en el único call-site.
- **C5 — UX de expectativa (MT-R5, frontend).** Cuando `isPending`: bajo "Procesando con IA...", texto secundario permanente *"Esto puede tardar unos minutos — no cierres esta pestaña."* (muted, sin layout shift). Nada más cambia.
- **C6 — Alcance cerrado.** Solo `routes/actas.ts` y `home.tsx`. Sin schema, reglas, `openapi.yaml` (ningún campo nuevo de API), sin dependencias. El límite de body (200mb) ya cubre audios largos — verificado, no se toca.

# Dudas declaradas por el Arquitecto

- **D1:** el umbral 500 B/s sale de solo 2 muestras de silencio y el conocimiento general de Opus. ¿Es el valor correcto o recomiendas otro (con qué margen) dado que un falso positivo BLOQUEA al usuario?
- **D2:** elegí **rechazo 422** sobre "aviso y procesar igual". Argumento: no gastar tokens ni crear actas basura; el mensaje guía al usuario. Contra-argumento: un falso positivo impide grabar del todo. ¿Confirmas el rechazo o propones estrategia mixta concreta?
- **D3:** `thinkingBudget: 0` es óptimo para TRANSCRIPCION (mecánica), pero la sección ANALISIS_PROFUNDO sí requiere razonamiento (en el piloto detectó un lapsus del hablante y matices). ¿0 absoluto o un budget bajo fijo (p. ej. 2048-4096) que proteja el análisis sin devorar el presupuesto?
- **D4:** la fórmula de C4 (`+ msDuration/10`, techo 10 min) es conjetura sin datos de la File API para audios de 30-60 min. ¿Criterio mejor con el contexto disponible?

# Preguntas de control (respóndelas TODAS con recomendación ÚNICA y justificada; "depende" no es respuesta)

- **Q1:** Umbral de MIN_AUDIO_BPS: da UN valor (o UNA fórmula) con su justificación numérica frente a los datos de CTX-1, explicitando el trade-off falso-positivo vs token gastado.
- **Q2:** thinkingBudget de la síntesis: ¿0 o un valor bajo concreto? UNA recomendación razonando sobre las 4 secciones del output (CTX-5) y el riesgo MAX_TOKENS de CTX-1.
- **Q3:** Redacta el texto EXACTO (listo para pegar) de la regla de audibilidad del ACTA_PROMPT, de modo que: (a) no dispare en reuniones reales con tramos inaudibles parciales, (b) sea consistente con la heurística `looksEmpty` de CTX-4, y (c) no interfiera con la regla de idioma.
- **Q4:** Traza simbólica completa: reunión REAL de 60 minutos con voz normal (~130.000 chars de transcripción esperada) bajo el diseño completo C1-C5. Indica: resultado del guard (números), timeout aplicado (fórmula), tokens estimados de la síntesis con tu recomendación de Q2, estado final de `actas/{id}` y `sintesis/{id}` (incluido el truncado a 800.000 bytes si aplica), y señala el RIESGO RESIDUAL más grande que queda vivo tras este ciclo.

# Anti-aprobación-automática
Si tu veredicto global es APROBADO o APROBADO CON CAMBIOS, demuestra ADEMÁS por qué cada trampa NO aplica (o qué cambio la neutraliza), con evidencia del contexto:

- **T1 — Falso positivo del guard.** Hablante muy suave/lejano produce ~600-900 B/s reales: con C1 queda BLOQUEADO sin poder grabar nada. ¿El diseño lo mitiga de verdad (umbral, mensaje, env override) o condena un caso de uso legítimo?
- **T2 — Doble mecanismo inconsistente.** El centinela de C2 y la heurística `looksEmpty` de CTX-4 pueden divergir (p. ej. el modelo devuelve el centinela pero con 1 participante fantasma, o un resumen centinela con wording distinto). ¿Las dos capas se reconcilian o pueden contradecirse dejando pasar una confabulación?
- **T3 — Costo de calidad del thinking.** Con tu recomendación de Q2, ¿la diarización de hablantes y el ANALISIS_PROFUNDO del caso real del piloto (detección de lapsus, matices) se conservan? Demuestra por qué no se degrada — o qué se acepta perder.
- **T4 — Reunión de 2+ horas.** Con el techo de 10 min de C4 y `maxOutputTokens` 65.536 compartido con thoughts: ¿dónde revienta primero el pipeline (timeout, MAX_TOKENS, truncado 800 KB, request HTTP colgado) y el diseño lo degrada con gracia o pierde el acta?
- **T5 — Mensaje de espera fuera de lugar.** El texto de C5 depende de `isPending` del mutation de procesar: ¿puede aparecer durante otras operaciones (borrar acta, listar) o quedarse pegado tras un error? Demuestra el ciclo de vida.

# Entregable final
1. Tabla C1..C6 con verdictos (SÓLIDO / DÉBIL / RECHAZADO + cambio requerido si aplica).
2. Respuestas Q1..Q4 (Q3 con el texto exacto; Q4 con la traza completa).
3. Refutación de T1..T5 si apruebas.
4. Opinión fundada sobre D1..D4.
5. Veredicto global: APROBADO / APROBADO CON CAMBIOS (cambios EXACTOS) / RECHAZADO (razón + contra-diseño mínimo).

Entrega TODA tu respuesta como UN único documento markdown listo para archivar tal cual. Sin verdicto por claim, sin las Q respondidas o sin la traza de Q4 es INVÁLIDA y será devuelta.

=== FIN PROMPT ===

---

━━ AVISO DE TRASPASO ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CICLO      : 2026-07-14_robustez_pipeline
FASE       : F1 — Diseño
TURNO DE   : Director
ENTREGAR   : auditorias/2026-07-14_robustez_pipeline/prompt_diseno_ronda1.md
             (solo el bloque entre === PROMPT ===)
ADJUNTOS   : Ninguno (revisión de diseño; contexto dentro del prompt)
DESTINO    : Conversación NUEVA de Gemini 3.1 Pro High — inicialización
             de identidad primero (instrucción 2), luego el prompt
ACCIÓN     : Obtener la revisión adversarial del diseño de robustez
VUELVE A   : Arquitecto, archivando la respuesta literal como
             respuesta_diseno_ronda1.md → anti-bluff → gate G1 → F3
             (specs para el Ingeniero)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
