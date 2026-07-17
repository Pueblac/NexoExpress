# Expediente 2026-07-17_captura_confiable — Prompt de revisión de DISEÑO (ronda 1)

**Ciclo:** F1 Diseño (METODOLOGIA_TRIPLE_IA.md v2) · **Meta:** [ActaExpressWeb] Captura confiable (hallazgos H3+H4 del piloto): el usuario elige EXPLÍCITAMENTE el tipo de reunión (sin diálogos sorpresa ni degradación silenciosa de la fuente) y un micrófono muerto se detecta EN LOS PRIMEROS SEGUNDOS de la grabación, no al final.
**Plan aprobado en G0 (17-07-2026):** MT-C1 selector de tipo de reunión · MT-C2 `startRecording(modo)` sin fallback silencioso · MT-C3 hook de nivel de micrófono (AnalyserNode) · MT-C4 banner de mic muerto · MT-C5 estado de procesamiento prominente. Decisiones de producto del Director: default = presencial; el aviso H4 solo avisa, nunca corta; MT-C5 dentro de la tanda.
**Preparado por:** Arquitecto (Claude Fable 5)

## Instrucciones de operación para el Director

1. Conversación **NUEVA** en Gemini 3.1 Pro High.
2. **Inicialización de identidad** — primer mensaje: *"Rol: Auditor del ciclo 2026-07-17_captura_confiable, metodología v2 del ecosistema Express. Confirma recepción sin accionar; acepta únicamente artefactos cuyo TURNO DE diga Auditor."*
3. **Sin adjuntos** — contexto verificado dentro del prompt.
4. Segundo mensaje: solo el bloque entre `=== PROMPT ===`.
5. Respuesta incompleta → frase de devolución estándar.
6. Guardar la respuesta tal cual como `respuesta_diseno_ronda1.md` y avisar al Arquitecto.

---

=== PROMPT ===

# Rol y regla de oro
Eres auditor adversarial de diseño del ecosistema Express. El Arquitecto (otra IA) propone 5 cambios de captura de audio en el frontend de ActaExpressWeb que un Ingeniero (tercera IA) implementará según spec. **Tu hipótesis de trabajo es que el diseño está mal o incompleto hasta que se demuestre lo contrario.** No agradezcas, no resumas, no elogies. Apoya cada afirmación en el contexto citado abajo; lo que no esté en este prompt es NO VERIFICABLE — prohibido rellenarlo con suposiciones.

# Formato obligatorio de CADA verificación
CLAIM → EVIDENCIA (cita del contexto) → TRAZA (razonamiento con valores concretos) → VERDICTO (SÓLIDO / DÉBIL / RECHAZADO).

# Material adjunto
Ninguno — revisión de diseño. Contexto verificado a continuación.

# Contexto verificado (extraído del código real, 17-07-2026)

**Sistema:** ActaExpressWeb frontend React/TS. `useAudioRecorder.ts` (hook de grabación, 261 líneas) + `home.tsx` (página principal). Entorno primario del Director: Chrome sobre Linux. El backend tiene desde el ciclo anterior un guard 422 server-side que rechaza audio < 300 B/s (última defensa; silencio real medido: 254 B/s).

**CTX-1 — Arranque de grabación actual (`useAudioRecorder.ts:144-192`, literal condensado) — RAÍZ de H3:**
```ts
const startRecording = useCallback(async () => {
  ...
  // --- Try system audio first ---
  const displayResult = await getDisplayAudioStream();   // SIEMPRE abre el diálogo de compartir
  if (displayResult) {
    displayStreamRef.current = displayResult.stream;
    const { mixedStream, audioCtx, micStream } = await mixAudioStreams(displayResult.stream);
    ...
    mode = micStream ? "system+mic" : "system";
    // listener: si la pestaña deja de compartir, se detiene la grabación
  } else {
    // --- Fallback: microphone only ---  ← DEGRADACIÓN SILENCIOSA
    try {
      recordingStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      micStreamRef.current = recordingStream;
      mode = "microphone";
    } catch (err) { setError(msg); return; }
  }
  setCaptureMode(mode);
  const mediaRecorder = new MediaRecorder(recordingStream);
  ...
  mediaRecorder.start(1000);
  setIsRecording(true);
```
Comportamiento actual: TODA grabación abre primero el diálogo `getDisplayMedia` (elegir pestaña/pantalla). Si el usuario cancela, cae EN SILENCIO a solo-micrófono. El usuario nunca declara su intención; el hallazgo H3 documentó actas de reuniones virtuales grabadas sin audio de la pestaña (en Linux/Chrome la captura de audio solo funciona eligiendo "Pestaña" + "Compartir audio de la pestaña"; "Pantalla"/"Ventana" no entregan audio).

**CTX-2 — `getDisplayAudioStream` (`useAudioRecorder.ts:43-85`):** intento 1 audio-only (`video: false`), intento 2 video+audio (descarta el track de video). Devuelve `null` si el usuario cancela O si el stream llega sin tracks de audio. `mixAudioStreams` (`:92-117`): `AudioContext` + `createMediaStreamDestination`, conecta display y LUEGO intenta `getUserMedia({audio: {echoCancellation: true, noiseSuppression: true}})`; si el mic falla, sigue solo con display ("that's OK").

**CTX-3 — Cleanup y estado (`useAudioRecorder.ts:135-142, 203-213`):** `cleanupStreams` para todos los tracks y cierra el `AudioContext` en `onstop`. El hook expone `{isRecording, startRecording, stopRecording, audioBlob, audioBase64, duration, error, captureMode}`. `captureMode: "system+mic" | "system" | "microphone" | null` se muestra como badge durante la grabación (`home.tsx:212-228`).

**CTX-4 — Disparo del botón (`home.tsx:183`, literal):**
```tsx
onClick={isRecording ? stopRecording : startRecording}
```
NOTA del Arquitecto: React pasa el `MouseEvent` como primer argumento — cualquier cambio de firma de `startRecording` debe blindarse contra ese argumento posicional.

**CTX-5 — Patrón de persistencia por usuario ya auditado y aprobado (ciclo MT-04, `home.tsx:55-68`):** `useState` inicializado desde `localStorage.getItem("actaexpress:generarSintesis:${user.uid}")`, escritura en el handler de cambio, `ref` espejo para lecturas dentro de callbacks. `Home` solo monta con `user` resuelto (`ProtectedRoute`). Este patrón se REUTILIZA para el selector.

**CTX-6 — Envío al server (`home.tsx:121-137`):** efecto que dispara `processAudio.mutate` cuando `audioBase64 && !isRecording && duration > 0`, con guard `lastProcessedAudioRef` + `!isPending` (diseño r2 del ciclo MT-04 — NO tocar). El server responde 422 si el audio promedia < 300 B/s (mic muerto detectado AL FINAL: el Director graba 30 min en vano y recién entonces se entera — motivación de H4, re-pedida explícitamente por el Director en el E2E del 17-07).

**CTX-7 — Estado de procesamiento actual (`home.tsx:197-209`):** timer + "Procesando con IA..." (`getStatusMessage`) + texto pequeño `text-espera` "Esto puede tardar unos minutos — no cierres esta pestaña." (MT-R5, recién auditado APROBADO). Observación de UX del Director en el E2E: se ve pequeño; quiere jerarquía visual clara de "el sistema está pensando".

**CTX-8 — Datos empíricos del audio (logs del piloto + ciclo robustez):** mic muteado en el SO produce WebM/Opus de ~254 B/s (DTX comprime silencio a casi nada); voz real ≥ 2.000-4.000 B/s. El `AnalyserNode` de Web Audio lee muestras en tiempo real ANTES de la compresión Opus (PCM del stream), así que el detector H4 opera sobre amplitud cruda, no sobre bitrate.

# Diseño propuesto (a auditar)

**D-1 (MT-C1) — Selector de tipo de reunión.** Estado `modoReunion: "presencial" | "virtual"` en `home.tsx`, UI de 2 opciones (RadioGroup o segmented control) encima del botón de grabar: **"Reunión presencial — sonido ambiente"** (mic directo) y **"Reunión virtual"** (audio de pestaña + mic). Default: `"presencial"` (decisión G0). Persistencia por uid con el patrón CTX-5 (`actaexpress:modoReunion:${uid}`) + ref espejo. Deshabilitado con `isRecording || processAudio.isPending`.

**D-2 (MT-C2) — `startRecording(modo)` sin fallback silencioso.** Firma nueva `startRecording(modo: ModoReunion)`, invocada como `() => startRecording(modoReunionRef.current)` (blindaje CTX-4).
- `"presencial"`: `getUserMedia({audio: true})` DIRECTO — cero diálogo de compartir. Error → `setError` (camino existente).
- `"virtual"`: `getDisplayAudioStream()` como hoy; si devuelve `null` (cancelación o pestaña sin audio) → `setError` con mensaje accionable (texto exacto en Q3) y **la grabación NO arranca** (se elimina el fallback a mic de CTX-1). Si hay display pero `getUserMedia` del mic falla → se procede como `"system"` (el audio de la pestaña sigue siendo valioso) y el detector H4 avisará que el mic no aporta señal.
- `captureMode` pasa a reflejar SIEMPRE lo realmente capturado; el listener de "pestaña dejó de compartir" se conserva.

**D-3 (MT-C3) — Detector de mic muerto (H4).** El hook expone el stream del MICRÓFONO (no el mezclado) en un estado nuevo `micStream: MediaStream | null`. Hook nuevo `useMicLevel(micStream, isRecording)`:
- `AudioContext` propio + `AnalyserNode` (fftSize 2048) sobre un `MediaStreamSource` del mic crudo; muestreo cada ~200 ms con `getByteTimeDomainData` → RMS normalizado (desviación sobre el centro 128).
- `micSilent = true` cuando TODAS las muestras de una ventana deslizante de 3 s están bajo el umbral `RMS < 0.01`, evaluable solo a partir de t≥3 s de grabación (calibración anti-falso-arranque). Vuelve a `false` INMEDIATAMENTE con una sola muestra sobre el umbral.
- En modo virtual se analiza el mic crudo a propósito: el audio de la pestaña NO debe enmascarar un mic muerto.
- Cleanup: cerrar su `AudioContext` al parar la grabación o desmontar. Constantes exportadas (`MIC_RMS_THRESHOLD`, `MIC_SILENT_WINDOW_MS`); sin dependencias nuevas.

**D-4 (MT-C4) — Aviso H4.** En `home.tsx`: banner destructivo persistente `{isRecording && micSilent && (...)}` con `data-testid="banner-mic-muerto"`, texto "⚠️ No se detecta señal de tu micrófono — revisa que no esté silenciado en el sistema." Aparece ≤5 s tras iniciar con mic muerto (3 s de ventana + margen), desaparece solo al detectar señal. NUNCA detiene la grabación (decisión G0). Aplica en ambos modos.

**D-5 (MT-C5) — Estado de procesamiento prominente.** Sustituir el bloque CTX-7 durante `isPending` por una tarjeta destacada (borde + fondo `primary/10`, `Loader2` girando, "Procesando con IA..." en cuerpo grande y el mensaje de espera debajo, conservando `data-testid="text-espera"`). Sin cambios de lógica de estado ni del guard CTX-6.

**Alcance cerrado:** 2 archivos tocados + 1 hook nuevo (`useMicLevel.ts`). Cero cambios en backend, openapi, schema, reglas, clientes generados. El guard 422 del server queda como defensa en profundidad.

# Claims a verificar

- **C1 — El selector elimina H3 sin regresión.** Con default presencial persistido por uid, el flujo cotidiano del Director (probado E2E) queda idéntico pero SIN el diálogo sorpresa; la reunión virtual pasa a ser intención declarada. La eliminación del fallback silencioso convierte el peor caso de H3 (creer que grabaste la pestaña cuando solo grabaste el mic) en un error visible y accionable.
- **C2 — "Virtual sin mic → system + aviso H4" es la degradación correcta.** A diferencia del fallback eliminado, esta degradación es visible (badge "Solo altavoces" + banner H4) y conserva el valor principal (audio de la reunión remota).
- **C3 — El detector RMS es fiable para el caso real.** Un mic muteado a nivel de SO entrega PCM plano (RMS ≈ 0); voz o sonido ambiente cruza 0.01 con holgura. Ventana de 3 s + histéresis inmediata de salida evita tanto el falso positivo del arranque como el parpadeo entre frases.
- **C4 — Analizar el mic crudo (no el mix) es la decisión correcta en virtual.** Si se analizara el stream mezclado, el audio de la pestaña enmascararía un mic muerto y H4 jamás dispararía justo en el modo donde el Director lo sufrió.
- **C5 — El cambio de firma es seguro.** Con el wrapper `() => startRecording(modoReunionRef.current)` (CTX-4) y el ref espejo (CTX-5), no hay forma de que un `MouseEvent` o un estado stale entren como modo.
- **C6 — Alcance cerrado y defensa en profundidad.** Nada del backend cambia; si H4 falla (bug del detector, navegador raro), el guard 422 sigue atrapando el audio mudo al final, como hoy.

# Preguntas de control (respóndelas TODAS, recomendación ÚNICA y justificada; un "depende" es respuesta INVÁLIDA)

- **Q1 — Umbral y ventana del detector:** ¿`RMS < 0.01` (sobre muestras normalizadas de `getByteTimeDomainData`, centro 128) con ventana de 3 s es correcto para distinguir mic muteado-en-SO de una sala en silencio entre frases, considerando que `getUserMedia` del diseño hereda `echoCancellation/noiseSuppression: true` (CTX-2) que atenúan el ruido de fondo? Da EL número (umbral y ventana) que usarías y por qué; si cambias alguno, es cambio mandatado.
- **Q2 — Constraints del mic en presencial:** el Director definió "presencial — sonido ambiente" para salas con varias personas. ¿`getUserMedia({audio: true})` a secas (constraints por defecto del navegador, con procesamiento de voz activado) o `{echoCancellation: false, noiseSuppression: false, autoGainControl: true/false}` para no matar voces lejanas? Recomendación única con la config exacta y su trade-off (calidad de transcripción vs nivel de ruido para el detector Q1 — deben ser consistentes entre sí).
- **Q3 — Texto exacto del error de virtual cancelado/sin audio:** redacta el mensaje literal (≤ 2 frases) que el usuario ve cuando en modo virtual cancela el diálogo o elige una fuente sin audio. Debe ser accionable en Chrome/Linux (elegir "Pestaña" + activar "Compartir audio de la pestaña") y no culpar al usuario.
- **Q4 — Traza completa de defensa en profundidad:** usuario en presencial con mic muteado en el SO pulsa grabar y habla 30 s. Traza segundo a segundo qué ve (t=0 arranque, t≈3-5 s banner H4, t=30 s stop) y qué pasa si IGNORA el banner y detiene: ¿qué responde el server (CTX-6) y qué toast ve? Confirma que en ningún punto se pierde una grabación VÁLIDA ni se crea un acta confabulada, y señala el hueco más grande que quede.

# Anti-aprobación-automática
Si tu veredicto global es APROBADO o APROBADO CON CAMBIOS, demuestra ADEMÁS por qué cada trampa NO aplica (o mandata el cambio que la neutraliza):

- **T1 — AudioContext suspendido.** La política de autoplay de Chrome puede crear el `AudioContext` del analizador en estado `suspended`; un contexto suspendido entrega buffers planos (constante 128) → RMS = 0 → **falso positivo de H4 con un mic perfectamente vivo**. ¿El diseño lo previene? ¿Basta el gesto de usuario del click en grabar, o el hook DEBE llamar `audioCtx.resume()` y/o abortar la evaluación mientras `state !== "running"`?
- **T2 — Doble AudioContext sobre el mismo track.** En virtual ya existe el `AudioContext` del mixer (CTX-2) y el diseño añade OTRO en `useMicLevel` sobre el mismo `MediaStream` del mic. ¿Crear dos `MediaStreamSource` de dos contextos sobre un mismo track es seguro y sin efectos sobre el audio grabado, o hay que compartir un único contexto?
- **T3 — El silencio "legítimo" de una reunión virtual.** En virtual, el usuario puede escuchar 20 min sin hablar: su mic está VIVO pero calla (o el noiseSuppression aplana su respiración a ~0). El banner diría "no se detecta señal" durante toda la reunión — ¿aviso correcto (el mic realmente no aporta) o ruido de UX que enseña al usuario a ignorar el banner (y entonces H4 muere por fatiga de alarmas)? ¿El texto/estilo del banner debe diferenciar "mic sin señal" de "mic muerto" en virtual?
- **T4 — Regresión del guard de envío.** MT-C2 cambia cómo arranca la grabación y MT-C5 el render del procesamiento. ¿Alguna interacción con el efecto CTX-6 (`lastProcessedAudioRef`, `!isPending`, deps) que pudiera re-disparar un POST o bloquear la grabación siguiente (el bug B1 que este proyecto ya sufrió)?
- **T5 — Estado del selector vs realidad de permisos.** Usuario elige "virtual", Chrome recuerda que BLOQUEÓ el permiso de mic para el sitio: `getDisplayAudioStream` OK, mic falla → queda "system". El badge y H4 lo comunican, ¿pero el SELECTOR sigue diciendo "Reunión virtual" como si todo fuera normal? ¿Hace falta un estado de error/aviso adicional en el selector, o el badge+banner bastan? Justifica.

# Entregable final
1. Tabla C1..C6 con verdictos. 2. Respuestas Q1..Q4 (recomendación única). 3. Refutación/neutralización T1..T5. 4. Opinión fundada: D1 (¿default presencial correcto?), D2 (¿RadioGroup vs segmented control — alguna razón de accesibilidad?), D3 (¿el hook debe vivir separado o dentro de useAudioRecorder?), D4 (¿algo del diseño invade decisiones que deberían ser del Ingeniero?). 5. Veredicto global: APROBADO / APROBADO CON CAMBIOS (cambios EXACTOS enumerados) / RECHAZADO.

Entrega TODA tu respuesta como UN único documento markdown listo para archivar tal cual. Sin trazas con valores concretos en Q1/Q4 o sin refutación de trampas es INVÁLIDA y será devuelta.

=== FIN PROMPT ===

---

━━ AVISO DE TRASPASO ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CICLO      : 2026-07-17_captura_confiable
FASE       : F1 — Diseño (revisión externa)
TURNO DE   : Director
ENTREGAR   : auditorias/2026-07-17_captura_confiable/prompt_diseno_ronda1.md
             (solo el bloque entre === PROMPT ===)
ADJUNTOS   : Ninguno — contexto verificado dentro del prompt
DESTINO    : Conversación NUEVA de Gemini 3.1 Pro High — inicialización
             de identidad primero (instrucción 2), luego el prompt
ACCIÓN     : Obtener la revisión adversarial del diseño
VUELVE A   : Arquitecto, archivando la respuesta literal como
             respuesta_diseno_ronda1.md → anti-bluff → GATE G1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
