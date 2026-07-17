# Expediente 2026-07-14_robustez_pipeline — Prompt de auditoría de CÓDIGO (ronda 1)

**Ciclo:** F6 Auditoría (METODOLOGIA_TRIPLE_IA.md v2) · **Tanda:** MT-R1..MT-R5 (robustez del pipeline: H1+H2+H5)
**Preparado por:** Arquitecto (Claude Fable 5) — 17-07-2026. Implementación del Ingeniero (Claude Sonnet, rotación asistida: 5 subagentes secuenciales, cero desviaciones, cero dudas); F5 COMPLETA (DoD re-ejecutado por el Arquitecto + E2E real con el Director el 17-07).

## Instrucciones de operación para el Director

1. Conversación **NUEVA** en Gemini 3.1 Pro High.
2. **Inicialización de identidad** — primer mensaje: *"Rol: Auditor del ciclo 2026-07-14_robustez_pipeline (auditoría de código, ronda 1), metodología v2 del ecosistema Express. Confirma recepción sin accionar; acepta únicamente artefactos cuyo TURNO DE diga Auditor."*
3. Sin adjuntos aparte — el **git diff ÍNTEGRO** va dentro de este prompt (regla v2, dictamen metodología cambio 1).
4. Pegar como segundo mensaje solo el bloque entre `=== PROMPT ===`.
5. Respuesta sin citas archivo:línea o sin trazas → *"Auditoría INVÁLIDA según el contrato: faltan citas/trazas. Reenvíala completa."*
6. Guardar la respuesta tal cual como `respuesta_auditoria_ronda1.md` y avisar al Arquitecto (anti-bluff antes de aceptar nada).

---

=== PROMPT ===

# Rol y regla de oro
Eres auditor adversarial de CÓDIGO del ecosistema Express. Un Ingeniero (IA) implementó, según especificaciones derivadas del diseño que TÚ aprobaste con cambios en ronda 1 (umbral 300 B/s, thinkingBudget 4096, texto de centinela Q3), una tanda de 5 micro-tareas de robustez en ActaExpressWeb. **Tu hipótesis de trabajo es que el código está mal o incompleto hasta que se demuestre lo contrario.** No agradezcas, no resumas, no elogies. Cada afirmación tuya requiere cita textual del material de este prompt (archivo y nº de línea del diff o del contexto); lo no incluido es NO VERIFICABLE — prohibido suponerlo.

# Formato obligatorio de CADA verificación
CLAIM → EVIDENCIA (cita textual, archivo:línea) → TRAZA (ejecución simbólica con valores concretos) → VERDICTO (CONFIRMADO / BUG / NO VERIFICABLE CON LO ADJUNTO).

# Contexto del ciclo (verificado por el Arquitecto sobre el código real)

Las 5 micro-tareas y su mandato de diseño (tu dictamen r1):

- **MT-R1 — Guard 422 de audio casi mudo:** módulo nuevo `audioGuard.ts` con `esAudioMudo` (umbral **300 B/s** — TU cambio 1 —, env-configurable vía `MIN_AUDIO_BPS`, piso de 5s sin evaluar) llamado en el handler ANTES de subir nada a Gemini; rechazo 422 con mensaje amigable y log de diagnóstico.
- **MT-R2 — Centinelas anti-confabulación:** TU texto Q3 literal inyectado en `ACTA_PROMPT`; adaptación para `SINTESIS_PROMPT` (línea `[SIN CONTENIDO AUDIBLE]` en TRANSCRIPCION, demás secciones vacías); heurística `looksEmpty` reconciliada con doble vía: match EXACTO del título centinela **O** (≤1 participante + keyword), añadiendo `"no se detectó"` a `silenceKeywords` (cierra OBS-1 del anti-bluff: las keywords viejas NO matcheaban el resumen centinela "No se detectó contenido audible.").
- **MT-R3 — `thinkingConfig: { thinkingBudget: 4096 }`** — TU cambio 2 — SOLO en la llamada de síntesis; la llamada del acta queda intacta.
- **MT-R4 — Timeout proporcional de File API:** `calcularMaxWaitMs = clamp(40_000, 40_000 + msDuration/10, 600_000)`; `waitForFileActive(fileName, msDuration)` deriva sus intentos del presupuesto (`ceil(maxWaitMs/2000)`, polling cada 2s).
- **MT-R5 — UX de expectativa:** texto "Esto puede tardar unos minutos — no cierres esta pestaña." bajo el estado, renderizado SOLO con `processAudio.isPending` (`data-testid="text-espera"`).

Contexto de código NO incluido en el diff (extractos literales del working tree, verificados):

- **CTX-A (`actas.ts:111-123`, resultado tras MT-R4):** `waitForFileActive` — si el archivo llega a `FAILED` lanza `Error("El archivo de audio falló al procesarse")`; si se agotan los intentos lanza `Error("Timeout: el archivo tardó demasiado en procesarse")`. Ambos caen al `catch` del handler → `res.status(500)`.
- **CTX-B (`actas.ts:267-271`):** la llamada del ACTA es `callGemini(activeFile.uri, mimeType, ACTA_PROMPT, { temperature: 0.2, maxOutputTokens: 4096, responseMimeType: "application/json" })` — **sin** `thinkingConfig` (verificado por grep: `thinkingConfig` aparece UNA sola vez en el archivo, en la config de síntesis).
- **CTX-C (`actas.ts:288-301`):** cuando `looksEmpty` es true el handler SOLO emite `req.log.warn(...)`; el flujo continúa: el acta (centinela o no) SE PERSISTE en `actas/` y se responde 201. El frontend (lógica preexistente del ciclo MT-04, fuera de este diff) detecta el resultado silencioso en `onSuccess` y muestra un toast distinto. `looksEmpty` NO bloquea nada.
- **CTX-D (`actas.ts:310-342`):** antes de persistir se purgan de `actas/` los campos de síntesis (`actaLimpia`); tras el 201, si `generarSintesis === true`, corre `generarSintesisEnBackground(...).catch(...)` — nunca bloquea ni tumba el flujo principal.
- **CTX-E (`actas.ts:160-186`):** `parseSintesisText` trocea por delimitadores `===SECCION===`; secciones ausentes/vacías → string vacío / listas vacías. La síntesis se guarda en `sintesis/{actaId}` (colección separada, límite 800 KB con truncado).
- **CTX-F (`home.tsx`, preexistente):** el error 422 llega por `onError` de la mutación → toast destructivo con el mensaje del server; `isPending` pasa a false al resolverse o rechazarse la mutación (react-query), desmontando cualquier render condicionado a él.
- **CTX-G (handler, preexistente):** `audioSizeBytes` se calcula EN EL SERVER desde el base64 recibido; `msDuration` viene del CLIENTE en el body (`AudioInput.msDuration`), sin validación de rango más allá del schema zod (`zod.number()`).

**E2E ya ejecutado (F5 parte 2, Director + Arquitecto, 17-07 — evidencia literal en el expediente):**
- Mic MUTEADO 31,9s → log `audio casi mudo rechazado (guard MT-R1)` con `audioSizeBytes: 8106, bytesPerSec: 254, minBps: 300` → **422 en 292 ms, cero llamadas a Gemini**, toast correcto, sin acta.
- Grabación real 56s (guión como ground truth, toggle ON) → acta FIEL (tareas/responsables/fechas exactos, cero invenciones), síntesis guardada (`transcripcionChars: 1111`), y `sintesis: respuesta de Gemini recibida` con **`thoughtsTokenCount: 1145` ≤ 4096** (baseline pre-fix: 62.912), `finishReason: "STOP"` en ambas llamadas. Mensaje de espera visible durante el procesamiento y desmontado al terminar.

**Hallazgos H3/H4 (captura/detector de mic en cliente), H6 (resiliencia IndexedDB) y el timeout HTTP de reverse-proxy en despliegue (Q4-r1):** defectos/riesgos PREEXISTENTES documentados con ciclos propios — **NO son objeto de esta auditoría**; no los re-reportes salvo que esta tanda los EMPEORE.

# Material adjunto — git diff ÍNTEGRO del working tree (sin filtrar, regla v2)

`git status --short`: ` M artifacts/acta-express/src/pages/home.tsx` · ` A artifacts/api-server/src/lib/audioGuard.ts` · ` M artifacts/api-server/src/routes/actas.ts` — nada más cambia en el repo.

```diff
diff --git a/artifacts/acta-express/src/pages/home.tsx b/artifacts/acta-express/src/pages/home.tsx
index 741c2ba..158bdb3 100644
--- a/artifacts/acta-express/src/pages/home.tsx
+++ b/artifacts/acta-express/src/pages/home.tsx
@@ -202,7 +202,12 @@ export default function Home() {
               {isRecording && <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />}
               <p className="font-medium">{getStatusMessage()}</p>
             </div>
-            
+            {processAudio.isPending && (
+              <p className="text-xs text-muted-foreground" data-testid="text-espera">
+                Esto puede tardar unos minutos — no cierres esta pestaña.
+              </p>
+            )}
+
             <AnimatePresence>
               {captureMode && isRecording && (
                 <motion.div 
diff --git a/artifacts/api-server/src/lib/audioGuard.ts b/artifacts/api-server/src/lib/audioGuard.ts
new file mode 100644
index 0000000..b2542e1
--- /dev/null
+++ b/artifacts/api-server/src/lib/audioGuard.ts
@@ -0,0 +1,12 @@
+export const MIN_AUDIO_BPS_DEFAULT = 300;
+
+/** Audio casi mudo: bitrate efectivo bajo el umbral. Grabaciones <5s no se evalúan. */
+export function esAudioMudo(audioSizeBytes: number, msDuration: number, minBps: number = MIN_AUDIO_BPS_DEFAULT): boolean {
+  if (msDuration < 5000) return false;
+  return audioSizeBytes / (msDuration / 1000) < minBps;
+}
+
+/** Espera máxima para que la File API active el archivo, proporcional a la duración del audio. */
+export function calcularMaxWaitMs(msDuration: number): number {
+  return Math.min(Math.max(40_000, 40_000 + msDuration / 10), 600_000);
+}
diff --git a/artifacts/api-server/src/routes/actas.ts b/artifacts/api-server/src/routes/actas.ts
index 3e5dff7..415f5ad 100644
--- a/artifacts/api-server/src/routes/actas.ts
+++ b/artifacts/api-server/src/routes/actas.ts
@@ -8,6 +8,7 @@ import {
 } from "../lib/firebaseAdmin.js";
 import { requireAuth, type AuthRequest } from "../middlewares/requireAuth.js";
 import { truncarPorBytes } from "../lib/truncate.js";
+import { esAudioMudo, MIN_AUDIO_BPS_DEFAULT, calcularMaxWaitMs } from "../lib/audioGuard.js";
 import type { Response } from "express";
 
 const router = Router();
@@ -43,7 +44,8 @@ Reglas:
 - Si no identificas nombres usa "Participante 1", "Participante 2", etc.
 - Si no hubo acuerdos explícitos devuelve "acuerdos": []
 - Si no hay tareas pendientes devuelve "pendientes": []
-- No incluyas texto ni explicaciones fuera del JSON`;
+- No incluyas texto ni explicaciones fuera del JSON
+- Si y solo si a lo largo de TODA la grabación no logras detectar ninguna voz humana inteligible (es decir, el audio es únicamente silencio continuo o ruidos de fondo de principio a fin), DEBES generar la salida con título exacto "Reunión sin contenido audible", iniciar el resumen obligatoriamente con la frase "No se detectó contenido audible.", y fijar participantes como un arreglo vacío []. Esta regla tiene prioridad absoluta. Sin embargo, si detectas AL MENOS UN fragmento de conversación humana, omite esta regla, ignora los silencios, redacta el acta y extrae el contenido normalmente en el idioma en que se realizó la reunión. PROHIBIDO inventar o inferir contenido que no esté en el audio; ante duda, declara la ausencia.`;
 
 // Llamada 2 (background): texto plano con delimitadores — NO JSON, porque un
 // string de cientos de KB dentro de JSON rompe el parseo por errores de escape
@@ -66,7 +68,8 @@ Un tema por línea, cada línea empieza con "- ".
 
 Reglas:
 - No escribas NADA fuera de las cuatro secciones.
-- Los delimitadores deben aparecer EXACTAMENTE como se muestran, cada uno en su propia línea.`;
+- Los delimitadores deben aparecer EXACTAMENTE como se muestran, cada uno en su propia línea.
+- Si y solo si a lo largo de TODA la grabación no logras detectar ninguna voz humana inteligible, escribe en la sección ===TRANSCRIPCION=== únicamente la línea [SIN CONTENIDO AUDIBLE] y deja las demás secciones vacías. Esta regla tiene prioridad absoluta. Si detectas AL MENOS UN fragmento de conversación humana, omite esta regla e ignora los silencios. PROHIBIDO inventar o inferir contenido que no esté en el audio; ante duda, declara la ausencia.`;
 
 const SINTESIS_MAX_BYTES = 800_000; // en BYTES UTF-8 (límite Firestore: 1 MiB/doc); deja margen para el resto de campos
 const SINTESIS_TRUNC_SUFFIX = "\n[TRANSCRIPCIÓN TRUNCADA POR LÍMITE DE ALMACENAMIENTO]";
@@ -105,8 +108,10 @@ async function uploadToGemini(audioBase64: string, mimeType: string): Promise<Ge
   return data.file;
 }
 
-async function waitForFileActive(fileName: string): Promise<GeminiFile> {
-  for (let i = 0; i < 20; i++) {
+async function waitForFileActive(fileName: string, msDuration: number): Promise<GeminiFile> {
+  const maxWaitMs = calcularMaxWaitMs(msDuration);
+  const maxAttempts = Math.ceil(maxWaitMs / 2000);
+  for (let i = 0; i < maxAttempts; i++) {
     const res = await fetch(`${GEMINI_BASE}/v1beta/${fileName}?key=${GEMINI_API_KEY}`);
     const file = await res.json() as GeminiFile;
     if (file.state === "ACTIVE") return file;
@@ -192,6 +197,7 @@ async function generarSintesisEnBackground(
     temperature: 0.2,
     maxOutputTokens: 65536,
     responseMimeType: "text/plain",
+    thinkingConfig: { thinkingBudget: 4096 },
   });
   log.info(
     { actaId, finishReason: result.finishReason, usageMetadata: result.usageMetadata },
@@ -241,11 +247,21 @@ router.post("/actas/process", requireAuth, async (req: AuthRequest, res: Respons
     "processAudio: received audio"
   );
 
+  const minBps = Number(process.env.MIN_AUDIO_BPS) || MIN_AUDIO_BPS_DEFAULT;
+  if (esAudioMudo(audioSizeBytes, msDuration, minBps)) {
+    req.log.warn(
+      { audioSizeBytes, msDuration, bytesPerSec: Math.round(audioSizeBytes / (msDuration / 1000)), minBps },
+      "processAudio: audio casi mudo rechazado (guard MT-R1)"
+    );
+    res.status(422).json({ error: "No se detectó señal de audio en la grabación (micrófono apagado o en silencio). Revisa tu micrófono e inténtalo de nuevo." });
+    return;
+  }
+
   try {
     const uploadedFile = await uploadToGemini(audioBase64, mimeType);
     req.log.info({ fileName: uploadedFile.name }, "processAudio: uploaded to Gemini");
 
-    const activeFile = await waitForFileActive(uploadedFile.name);
+    const activeFile = await waitForFileActive(uploadedFile.name, msDuration);
     req.log.info({ fileUri: activeFile.uri }, "processAudio: file active in Gemini");
 
     const actaResult = await callGemini(activeFile.uri, mimeType, ACTA_PROMPT, {
@@ -262,10 +278,12 @@ router.post("/actas/process", requireAuth, async (req: AuthRequest, res: Respons
     // Detect likely empty/silent audio based on Gemini output
     const participantes = Array.isArray(actaData.participantes) ? actaData.participantes : [];
     const resumen = typeof actaData.resumen === "string" ? actaData.resumen : "";
-    const silenceKeywords = ["no se pudo", "no audible", "no hay audio", "sin contenido", "silencio"];
+    const titulo = typeof actaData.titulo === "string" ? actaData.titulo : "";
+    const silenceKeywords = ["no se pudo", "no audible", "no hay audio", "sin contenido", "silencio", "no se detectó"];
     const looksEmpty =
-      participantes.length <= 1 &&
-      silenceKeywords.some((kw) => resumen.toLowerCase().includes(kw));
+      titulo === "Reunión sin contenido audible" ||
+      (participantes.length <= 1 &&
+        silenceKeywords.some((kw) => resumen.toLowerCase().includes(kw)));
 
     if (looksEmpty) {
       req.log.warn(
```

# Claims a verificar

- **C1 — Guard fiel al dictamen y realmente pre-gasto.** `esAudioMudo` implementa exactamente umbral 300 B/s (default), piso `msDuration < 5000`, comparación estricta `<`; el handler lo evalúa ANTES de `uploadToGemini` y retorna 422 sin ninguna llamada a Gemini ni escritura en Firestore. `MIN_AUDIO_BPS` de entorno lo sobreescribe.
- **C2 — Centinelas = texto Q3 sin mutaciones.** El bloque añadido a `ACTA_PROMPT` es TU texto Q3 carácter a carácter (título exacto, frase inicial del resumen, `participantes: []`, cláusula "AL MENOS UN fragmento", prohibición de inventar); la variante de `SINTESIS_PROMPT` preserva la misma semántica adaptada a secciones (`[SIN CONTENIDO AUDIBLE]`).
- **C3 — `looksEmpty` reconciliada cierra OBS-1.** Con la salida centinela exacta del prompt, `looksEmpty` dispara SIEMPRE (por el título, sin depender de keywords); la vía de keywords se mantiene para salidas legacy/imperfectas e incorpora `"no se detectó"` que matchea el resumen centinela. Consecuencia de disparo: solo log WARN (CTX-C), sin cambio de flujo.
- **C4 — thinkingBudget quirúrgico.** `thinkingConfig: { thinkingBudget: 4096 }` existe ÚNICAMENTE en la config de `generarSintesisEnBackground` (síntesis, `maxOutputTokens: 65536`); la llamada del acta (CTX-B) queda byte a byte como estaba.
- **C5 — Timeout proporcional fiel a la fórmula.** `calcularMaxWaitMs` = `min(max(40_000, 40_000 + ms/10), 600_000)`; `waitForFileActive` deriva `maxAttempts = ceil(maxWaitMs/2000)` y conserva la semántica previa (poll 2s, `FAILED` lanza, agotamiento lanza — CTX-A). Para el caso previo (comportamiento viejo: 20 intentos = 40s), un audio corto produce los mismos ~40s (sin regresión).
- **C6 — Alcance cerrado.** El diff toca exactamente 3 archivos; nada en `openapi.yaml`, schemas, reglas Firestore, clientes generados ni `useAudioRecorder.ts`; sin dependencias nuevas; el mensaje de espera solo se renderiza con `isPending` y no altera lógica de estado.

# Dudas declaradas

*Del Ingeniero:* ninguna — los 5 informes se entregaron sin desviaciones ni dudas (verificado en F5 contra el código).

*Del Arquitecto:*
- **D1:** `Number(process.env.MIN_AUDIO_BPS) || MIN_AUDIO_BPS_DEFAULT` — con `MIN_AUDIO_BPS=0` (intención: desactivar el guard) el `||` cae al default 300 y el guard sigue activo; un valor no numérico → `NaN` → 300. ¿Es un footgun operativo que amerite cambio, o comportamiento seguro-por-defecto aceptable documentándolo?
- **D2:** `maxAttempts = ceil(maxWaitMs/2000)` cuenta solo los sleeps: la latencia de cada `fetch` no se descuenta, así que el tiempo real de pared puede exceder `maxWaitMs` (p. ej. fetch de 500ms → ~25% más). ¿Rompe la intención del diseño o es una aproximación aceptable del presupuesto?
- **D3:** la keyword nueva `"no se detectó"` con `participantes.length <= 1`: un monólogo legítimo (1 participante) cuyo resumen diga p. ej. "no se detectó el error en producción" activaría `looksEmpty`. Dado CTX-C (solo WARN + toast distinto en frontend, el acta SÍ se guarda), ¿el daño se limita a un falso aviso de UX o hay un efecto que no estoy viendo?
- **D4:** el centinela de síntesis deja `[SIN CONTENIDO AUDIBLE]` en TRANSCRIPCION y las demás secciones vacías; `parseSintesisText` (CTX-E) las degrada a strings/listas vacías y se persiste igualmente un doc en `sintesis/`. ¿Debe considerarse correcto (trazabilidad) o desperdicio (doc basura) según el diseño aprobado?

# Preguntas de control (respóndelas TODAS)

- **Q1:** Copia textualmente del diff la condición completa de `esAudioMudo` y traza con valores: (i) el caso E2E real `(8106, 31939)`; (ii) el caso frontera de TU dictamen `(1.725.000, 3.600.000)` = 479 B/s; (iii) exactamente 300,0 B/s. Indica para cada uno si pasa o se rechaza y por qué el operador (`<` vs `<=`) es el correcto respecto al dictamen.
- **Q2:** Traza `waitForFileActive` con `msDuration = 55.958` (E2E) y con `msDuration = 7.200.000` (2h): valores de `maxWaitMs`, `maxAttempts`, y qué error EXACTO y qué status HTTP recibe el cliente si el archivo nunca activa (usa CTX-A). ¿Queda alguna ruta donde el request se cuelgue sin límite?
- **Q3:** Traza el flujo completo del caso mic muteado 30s desde el POST hasta el DOM: guard → 422 → `onError` (CTX-F) → estado de `isPending` → ¿qué pasa con el elemento `data-testid="text-espera"` del diff en cada instante? ¿Existe algún instante en que el usuario vea el mensaje de espera Y el toast de error a la vez, y es eso un bug?
- **Q4:** Audio de ruido blanco a 400 B/s durante 10 min (pasa el guard): traza qué produce cada llamada según los prompts del diff (acta centinela / síntesis `[SIN CONTENIDO AUDIBLE]`), la evaluación de `looksEmpty` término a término, qué se persiste en `actas/` y (con toggle ON) en `sintesis/`, y qué ve el usuario. Dictamina si ese comportamiento es el del diseño aprobado.

# Anti-aprobación-automática
Si tu veredicto global es APROBADO o APROBADO CON OBSERVACIONES, demuestra ADEMÁS por qué cada trampa NO aplica, con evidencia del diff/CTX:

- **T1 — Falso positivo con voz real de bajo bitrate.** Codec Opus con DTX agresivo y un hablante lejano: ¿puede una grabación CON voz inteligible promediar < 300 B/s y perderse irremediablemente por el 422? Argumenta con los números del dictamen (silencio ≈ 250 B/s, voz ≥ 2.000-4.000 B/s) si el margen de 50 B/s es suficiente o si existe un perfil realista que caiga dentro.
- **T2 — `msDuration` es input del cliente (CTX-G).** Un cliente buggy/malicioso puede mandar `msDuration: 4999` con un audio de 1h (bypass total del guard) o `msDuration: 10^9` con audio normal (¿falso 422? ¿`maxWaitMs` clavado al techo de 600s?). Traza ambos abusos y dictamina el daño real y a quién afecta (¿solo a sí mismo, o al servicio?).
- **T3 — Doble mecanismo inconsistente, segunda ronda.** Ya fallaste una vez aquí (OBS-1: citaste una keyword inexistente). Verifica AHORA contra el diff, substring por substring, que el resumen centinela "No se detectó contenido audible." (en minúsculas) contiene la keyword `"no se detectó"` Y que el título centinela matchea `titulo === "Reunión sin contenido audible"` exactamente (mayúsculas, acentos). ¿Hay algún desajuste residual entre lo que el prompt ordena y lo que `looksEmpty` comprueba?
- **T4 — El centinela degrada actas normales.** La regla tiene "prioridad absoluta" dentro del prompt: ¿puede inducir a Gemini a declarar "sin contenido audible" en reuniones REALES con largos silencios (p. ej. 55 min de silencio + 5 de voz), perdiendo contenido legítimo? Cita la cláusula del diff que lo previene y contrasta con la evidencia E2E (acta fiel con guión real).
- **T5 — Presupuesto 4096 insuficiente o mal colocado.** ¿Puede `thinkingBudget: 4096` truncar la CALIDAD de la síntesis de una reunión de 1h (32.500 tokens de transcripción) o interactuar mal con `maxOutputTokens: 65536`? ¿Y confirmas con CTX-B que el acta NO quedó accidentalmente con thinking ilimitado siendo la llamada síncrona (la que bloquea el request HTTP)?

# Entregable final
1. Tabla C1..C6 con verdictos. 2. Respuestas Q1..Q4. 3. Refutación T1..T5 si apruebas. 4. Opinión fundada sobre D1..D4. 5. Veredicto global: APROBADO / APROBADO CON OBSERVACIONES / RECHAZADO (con los cambios EXACTOS si aplica).

Entrega TODA tu respuesta como UN único documento markdown listo para archivar tal cual. Sin citas archivo:línea o sin las trazas de Q1..Q4 es INVÁLIDA y será devuelta.

=== FIN PROMPT ===

---

━━ AVISO DE TRASPASO ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CICLO      : 2026-07-14_robustez_pipeline
FASE       : F6 — Auditoría de código (tanda MT-R1..R5)
TURNO DE   : Director
ENTREGAR   : auditorias/2026-07-14_robustez_pipeline/prompt_auditoria_ronda1.md
             (solo el bloque entre === PROMPT ===)
ADJUNTOS   : Ninguno aparte — el diff íntegro va DENTRO del prompt
DESTINO    : Conversación NUEVA de Gemini 3.1 Pro High — inicialización
             de identidad primero (instrucción 2), luego el prompt
ACCIÓN     : Obtener la auditoría adversarial del código
VUELVE A   : Arquitecto, archivando la respuesta literal como
             respuesta_auditoria_ronda1.md → anti-bluff → F7 (gate G2)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
