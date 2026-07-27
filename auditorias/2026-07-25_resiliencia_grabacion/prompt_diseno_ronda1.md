# Expediente 2026-07-25_resiliencia_grabacion — Prompt de revisión de DISEÑO, ronda 1

**Generado:** 25-07-2026 por el Arquitecto (Fable 5), tras G0 del Director (25-07: recuperación OFRECIDA con tarjeta, máx. 1 sesión huérfana, H6 confirmado como ciclo; Vertex pospuesto).
**TURNO DE:** Auditor (Gemini 3.1 Pro High).
**ADJUNTOS:** NINGUNO — revisión de diseño; el contexto verificado va dentro del MENSAJE 2.

---

## AVISO — Qué haces tú, paso a paso (Director)

1. Abre una conversación **NUEVA** de Gemini 3.1 Pro High (sin herencia de hilo).
2. Pega como primer mensaje el bloque **MENSAJE 1** y espera su confirmación.
3. Pega como segundo mensaje TODO el bloque **MENSAJE 2** (desde `# Rol y regla de oro` hasta el final).
4. Si responde sin el formato exigido (recomendación única por pregunta, trampas demostradas): *"Revisión INVÁLIDA según el contrato. Reenvíala completa."*
5. Guarda la respuesta TAL CUAL como `auditorias/2026-07-25_resiliencia_grabacion/respuesta_diseno_ronda1.md` y avísame; yo anexo la validación anti-bluff y de ahí sale el diseño para tu G1.

---

## MENSAJE 1 — Inicialización de identidad (pegar y esperar confirmación)

```
Rol: Auditor del ciclo 2026-07-25_resiliencia_grabacion, metodología v2 del
ecosistema Express. Confirma recepción sin accionar; acepta únicamente
artefactos cuyo campo TURNO DE diga Auditor.
```

---

## MENSAJE 2 — Prompt de revisión de diseño (pegar íntegro tras la confirmación)

# Rol y regla de oro

Eres auditor adversarial del ecosistema Express. El Arquitecto (otra IA) propone un DISEÑO para "Resiliencia de grabación" (hallazgo H6): que un crash o cierre de pestaña a mitad de una reunión larga no pierda el audio ya grabado. **Tu hipótesis de trabajo es que el diseño está mal o incompleto hasta que se demuestre lo contrario.** No eres un asistente conversacional: no agradezcas, no resumas, no elogies. Esto es una revisión de DISEÑO: no hay código nuevo que auditar; el contexto técnico verificado del código EXISTENTE va abajo y es la única base fáctica — lo que no esté ahí es NO VERIFICABLE, prohibido suponerlo.

# Formato obligatorio

Para cada CLAIM: ANÁLISIS (razonado contra el contexto, citando la línea del contexto que usas) → VERDICTO (SÓLIDO / DÉBIL con alternativa concreta / RECHAZADO con razón). Para cada PREGUNTA: una recomendación ÚNICA y justificada — un "depende" sin resolución se considera no-respuesta. Si tu veredicto global es APROBADO (con o sin cambios), demuestra por qué cada TRAMPA no aplica.

# Contexto técnico VERIFICADO del código existente (ActaExpressWeb, commit 35580f0, rama linux)

- App React+Vite; graba reuniones y genera actas vía backend con Gemini File API. Todo lo de abajo fue verificado por el Arquitecto con lectura y grep del código real:
- `useAudioRecorder.ts`: `MediaRecorder.start(1000)` produce chunks de 1 s (`:231`); `ondataavailable` los acumula SOLO EN MEMORIA en `chunksRef.current` (`:215-217`); `onstop` arma `new Blob(chunksRef.current, { type: mediaRecorder.mimeType || "audio/webm" })`, lo convierte a base64 y limpia streams (`:219-229`). Cerrar la pestaña pierde `chunksRef` — ESE es H6.
- `duration` ya es milisegundos: `Date.now() - startTimeRef.current` (`:236`).
- Dos modos de captura (ciclo anterior "captura confiable"): `presencial` (getUserMedia directo) y `virtual` (pestaña+mic mezclados vía Web Audio, `mixAudioStreams`). En virtual, si el usuario deja de compartir, el track `ended` para la grabación automáticamente (`:196-206`).
- `home.tsx`: un `useEffect` auto-procesa al terminar: cuando `audioBase64 && !isRecording && duration > 0` y no se procesó ya, llama `processAudio.mutate({ audioBase64, mimeType: "audio/webm", msDuration: duration, generarSintesis })` (`:141-155`). El server tiene un guard 422 que rechaza audio casi mudo (< 300 B/s) ANTES de gastar tokens.
- Sesión de usuario: Firebase Auth; `home.tsx` solo se monta con `user` resuelto (ProtectedRoute). Preferencias por-uid ya usan el patrón `actaexpress:<clave>:${user.uid}` en localStorage.
- Restricción de gobernanza: 100% frontend; sin cambios de schema Firestore, openapi ni server.

# Diseño propuesto (decisiones de producto YA fijadas por el Director en G0: recuperación OFRECIDA con tarjeta Recuperar/Descartar, máximo 1 sesión huérfana conservada — no cuestionar el QUÉ, auditar el CÓMO)

**D-A. Módulo nuevo `recordingVault.ts`** — wrapper de IndexedDB (DB `actaexpress-vault`): store `sessions` (key `sessionId` UUID; metadata: `uid`, `modo`, `mimeType` real del MediaRecorder, `startedAt`, `lastChunkAt`, `chunkCount`) y store `chunks` (key compuesta `[sessionId, seq]`, value Blob de 1 s). API: `createSession`, `appendChunk` (actualiza `lastChunkAt`+`chunkCount`), `listSessions(uid)`, `readChunks(sessionId)`, `deleteSession`, `purgeAllExcept(sessionId)`.

**D-B. Escritura al vuelo en `useAudioRecorder`** — en `startRecording`: `createSession` + purga de huérfanas previas dejando máx. 1 según política (ver Q2); en `ondataavailable`: además del push a memoria (intacto), `appendChunk` **fire-and-forget** con errores silenciados: un fallo de IndexedDB (no disponible, QuotaExceeded) desactiva el vault para esa sesión y la grabación continúa EXACTAMENTE como hoy. El flujo actual (memoria → blob → base64 → auto-proceso) no cambia.

**D-C. Ciclo de vida / borrado** — la sesión del vault se borra SOLO en: (a) `onSuccess` del procesamiento (acta creada), o (b) descarte explícito del usuario en la tarjeta. NO se borra en `onstop`: así un crash DURANTE el procesamiento tampoco pierde el audio. Costo aceptado: tras un 422 legítimo (audio mudo) la sesión queda huérfana y la tarjeta reaparecerá; el usuario la descarta.

**D-D. Detección de huérfanas con heartbeat** — una sesión es huérfana si `lastChunkAt < now − STALE_MS` (propuesto 10 000 ms; los chunks llegan cada ~1 s). Esto evita el falso positivo crítico de multi-pestaña: la pestaña B abierta en paralelo NO debe ofrecer "recuperar" la grabación VIVA de la pestaña A (que sigue latiendo). Al montar `home.tsx`: `listSessions(uid)` → filtrar huérfanas → conservar la más reciente, purgar el resto.

**D-E. Tarjeta de recuperación en `home.tsx`** — si hay huérfana: tarjeta "Se encontró una grabación interrumpida (~X min) — Recuperar / Descartar" (X = `chunkCount` segundos). Recuperar: `readChunks` ordenados por `seq` → `new Blob(chunks, { type: mimeType guardado })` → `blobToBase64` → `processAudio.mutate({ audioBase64, mimeType: "audio/webm", msDuration: chunkCount × 1000, generarSintesis: toggle vigente })` — entra al pipeline existente sin cambios de server. Descartar: `deleteSession`. La tarjeta no se muestra durante una grabación activa.

**Micro-tareas (aprobadas en G0):** MT-H6a vault · MT-H6b escritura al vuelo + heartbeat · MT-H6c tarjeta + recuperación · MT-H6d robustez (límite 1, purga, quota/IndexedDB ausente).

# Claims a verificar

- **C1:** La escritura fire-and-forget por chunk (1 Blob de ~10–20 KB/s a IndexedDB) no puede bloquear ni degradar la grabación; el peor caso (IndexedDB roto/lleno) degrada exactamente al comportamiento actual.
- **C2:** El borrado en `onSuccess` (y no en `onstop`) es el punto correcto: cubre crash durante grabación Y durante procesamiento, sin dejar basura en el caso feliz.
- **C3:** El heartbeat `lastChunkAt` con umbral 10 s distingue correctamente huérfana real vs grabación viva en otra pestaña, incluyendo el caso de pestaña de fondo con timers throttleados (los chunks de MediaRecorder NO dependen de setInterval de JS — `ondataavailable` los emite el propio recorder).
- **C4:** Un webm reconstruido concatenando los chunks de `dataavailable` en orden (header EBML en el chunk 1, clusters subsiguientes; posible último chunk parcial por el crash) es procesable por el pipeline actual (File API de Gemini + transcripción), con `mimeType: "audio/webm"`.
- **C5:** El diseño respeta las restricciones: 100% frontend, cero cambios de schema/openapi/server, y ningún camino nuevo de fallo en el flujo de grabación existente.

# Preguntas de diseño (recomendación ÚNICA y justificada cada una)

- **Q1:** ¿`msDuration = chunkCount × 1000` es una estimación aceptable para el guard 422 y el timeout proporcional del server, o propones otra fuente (p. ej. `lastChunkAt − startedAt`)? Una sola recomendación.
- **Q2:** ¿En qué momento purgar hasta el límite de 1 huérfana: al crear sesión nueva, al montar Home, o ambos? ¿Y qué hacer con huérfanas de OTRO uid en el mismo navegador (multi-cuenta): ofrecerlas nunca, borrarlas nunca, o borrarlas por antigüedad? Una sola política.
- **Q3:** Si el usuario pulsa "Recuperar" y el procesamiento falla (422 de audio mudo, error de red), ¿la sesión debe conservarse (tarjeta reaparece) o descartarse automáticamente? Recomendación única considerando el bucle tarjeta→422→tarjeta.
- **Q4:** ¿STALE_MS = 10 000 es el umbral correcto frente a: GC/pausas largas del navegador, `dataavailable` retrasado en máquinas lentas, y suspensión del portátil con la grabación "viva"? Si propones otro valor o mecanismo complementario (p. ej. marca `closedAt` al `onstop`), UNO solo.

# Anti-aprobación-automática

Si tu veredicto global es APROBADO (con o sin cambios), demuestra por qué cada trampa NO aplica (con el mecanismo del diseño que la neutraliza):

- **T1:** Crash del navegador DURANTE el procesamiento (post-stop, pre-acta): ¿el audio sobrevive y es recuperable al reabrir?
- **T2:** Dos pestañas de ActaExpress abiertas, la A grabando: ¿puede la B ofrecer recuperar (o peor, purgar) la sesión viva de A? ¿Y si A Y B graban a la vez?
- **T3:** Reunión de 2 h en virtual (~70–140 MB de webm): ¿QuotaExceeded a mitad de grabación corta la reunión, pierde lo ya persistido, o solo desactiva el vault? ¿Qué ve el usuario?
- **T4:** El usuario recupera una grabación, el acta se crea con éxito, y ADEMÁS tenía el auto-proceso del `useEffect` armado por una grabación normal reciente: ¿puede dispararse un procesamiento doble (dos actas del mismo audio)?
- **T5:** Suspensión del portátil (lid close) durante una grabación y reapertura 1 h después en la MISMA pestaña: ¿el heartbeat marca la sesión como huérfana mientras `isRecording` sigue true? ¿Qué debe pasar?

# Entregable final

UN ÚNICO documento markdown listo para archivar: 1. Tabla C1..C5 con verdictos. 2. Respuestas Q1..Q4 (recomendación única cada una). 3. Demostración T1..T5 si apruebas. 4. Lista numerada de CAMBIOS obligatorios si tu veredicto es APROBADO CON CAMBIOS. 5. Veredicto global (APROBADO / APROBADO CON CAMBIOS / RECHAZADO). Recuerda: "APROBADO CON CAMBIOS" significa que se implementará CON tus cambios — no son sugerencias.
