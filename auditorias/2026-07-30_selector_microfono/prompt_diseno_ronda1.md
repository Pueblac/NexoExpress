# Expediente 2026-07-30_selector_microfono — Prompt de revisión de DISEÑO, ronda 1

**Generado:** 30-07-2026 por el Arquitecto (Fable 5), tras G0 del Director (30-07: hot-swap SIN cortar la grabación; la elección PERSISTE como default futuro por uid; CTA SOLO en el banner H4 — el default sigue siendo automático).
**TURNO DE:** Auditor (Gemini 3.1 Pro High).
**ADJUNTOS:** NINGUNO — revisión de diseño; el contexto verificado va dentro del MENSAJE 2.

---

## AVISO — Qué haces tú, paso a paso (Director)

1. Conversación **NUEVA** de Gemini 3.1 Pro High (sin herencia de hilo).
2. Pega el bloque **MENSAJE 1** y espera su confirmación.
3. Pega TODO el bloque **MENSAJE 2** (desde `# Rol y regla de oro` hasta el final).
4. Si responde sin recomendación única por pregunta o sin demostrar las trampas: *"Revisión INVÁLIDA según el contrato. Reenvíala completa."*
5. Guarda la respuesta TAL CUAL como `auditorias/2026-07-30_selector_microfono/respuesta_diseno_ronda1.md` y avísame; yo anexo el anti-bluff y de ahí sale el diseño para tu G1.

---

## MENSAJE 1 — Inicialización de identidad (pegar y esperar confirmación)

```
Rol: Auditor del ciclo 2026-07-30_selector_microfono, metodología v2 del
ecosistema Express. Confirma recepción sin accionar; acepta únicamente
artefactos cuyo campo TURNO DE diga Auditor.
```

---

## MENSAJE 2 — Prompt de revisión de diseño (pegar íntegro tras la confirmación)

# Rol y regla de oro

Eres auditor adversarial del ecosistema Express. El Arquitecto (otra IA) propone un DISEÑO para "Selector de micrófono": cuando el detector de mic muerto (banner H4) avise, el usuario podrá cambiar de micrófono desde el propio banner SIN cortar la grabación, y la elección persistirá como default futuro. **Tu hipótesis de trabajo es que el diseño está mal o incompleto hasta que se demuestre lo contrario.** No eres un asistente conversacional: no agradezcas, no resumas, no elogies. El contexto técnico verificado del código existente va abajo y es la única base fáctica — lo no incluido es NO VERIFICABLE, prohibido suponerlo.

# Formato obligatorio

Para cada CLAIM: ANÁLISIS (contra el contexto, citando la línea que usas) → VERDICTO (SÓLIDO / DÉBIL con alternativa concreta / RECHAZADO con razón). Para cada PREGUNTA: recomendación ÚNICA y justificada — un "depende" sin resolución es no-respuesta. Si tu veredicto global es APROBADO (con o sin cambios), demuestra por qué cada TRAMPA no aplica.

# Contexto técnico VERIFICADO del código existente (ActaExpressWeb, commit 74e3d32, rama linux; verificado por el Arquitecto con lectura y grep)

- Caso real que motiva el ciclo (28-07, PC Windows del trabajo): Chrome tenía "Stereo Mix (Realtek)" como micrófono default → grabación en silencio → el banner H4 lo cazó; la única salida fue `chrome://settings/content/microphone`, inaceptable como UX.
- **Captura presencial** (`useAudioRecorder.ts:162-167`): `getUserMedia({ audio: { echoCancellation: false, noiseSuppression: false, autoGainControl: true } })` y ese stream CRUDO va DIRECTO al `MediaRecorder` (`:224` aprox., `new MediaRecorder(recordingStream)`); no hay AudioContext en este modo.
- **Captura virtual** (`mixAudioStreams`, `:95-120`): AudioContext + `createMediaStreamDestination()`; display source y mic source (`getUserMedia` con `echoCancellation: true, noiseSuppression: true`, `:110-112`) se conectan al destination; el recorder graba `dest.stream`. El mic puede faltar (mode `"system"`).
- **MediaRecorder NO tolera cambiar los tracks del stream que graba** (limitación de plataforma conocida): un hot-swap exige que el stream del recorder no cambie — de ahí el enrutamiento por Web Audio.
- **Detector H4** (`useMicLevel.ts`): hook con firma `useMicLevel(micStream, isRecording, modo)`; su `useEffect` depende de `[active, micStream]` → si `micStream` CAMBIA de instancia, se destruye el AnalyserNode viejo y se crea uno sobre el nuevo. Umbral RMS 0.01, ventana 5 s presencial / 10 s virtual, `lastLoudAt` se resetea a "ahora" mientras el contexto no esté `running`.
- **Banner H4** (`home.tsx:~505` zona del render): visible solo con `isRecording && micSilent`; rojo destructivo en presencial, ámbar pasivo en virtual. El detector jamás corta la grabación.
- **Limpieza** (`cleanupStreams`, `useAudioRecorder.ts:147-151`): para todos los tracks de display y mic y hace `audioCtxRef.current?.close().catch(() => {})` — el patrón de cierre de AudioContext ya existe.
- **Vault H6:** durante la grabación, chunks de 1 s van a IndexedDB (fire-and-forget); la sesión guarda `mimeType` del recorder. Un hot-swap NO debe reiniciar el MediaRecorder (reiniciarlo cambiaría de sesión/archivo).
- Persistencia por uid ya usa el patrón `actaexpress:<clave>:${user.uid}` en localStorage (p. ej. `modoReunion`).
- `enumerateDevices()` devuelve labels NO vacíos solo con permiso de mic concedido; durante una grabación el permiso está concedido por definición.
- Restricción de gobernanza: 100% frontend; sin cambios de schema, openapi ni server.

# Diseño propuesto (decisiones de producto YA fijadas en G0 — no cuestionar el QUÉ, auditar el CÓMO: hot-swap sin cortar; persiste como default; CTA solo en el banner)

**D-A. Módulo + hook `useMicDevices`:** `enumerateDevices()` filtrado a `audioinput` con labels (post-permiso), refresco con el evento `devicechange`, y persistencia `actaexpress:micDeviceId:${uid}` (`getPreferredMic`/`setPreferredMic`). Validación: un deviceId persistido que ya no está en la lista se trata como inexistente.

**D-B. Enrutamiento Web Audio del modo presencial:** `startRecording("presencial")` pasa a: `getUserMedia({ audio: { deviceId: preferido? {exact} : undefined, echoCancellation: false, noiseSuppression: false, autoGainControl: true } })` → mic CRUDO; crear `AudioContext` + `createMediaStreamDestination()`; `micSource.connect(dest)`; **el MediaRecorder graba `dest.stream`** (ya no el stream crudo). El stream crudo sigue siendo lo que se expone como `micStream` (para `useMicLevel`). El AudioContext se guarda en `audioCtxRef` (la limpieza existente ya lo cierra). Salvaguarda anti-silencio: tras crear el contexto, `resume()` si `suspended`, y solo llamar `mediaRecorder.start(1000)` cuando `audioCtx.state === "running"` (con timeout corto de cortesía; si no llega a running → fallback DECLARADO al camino actual sin Web Audio, grabando el stream crudo directo — la grabación JAMÁS se sacrifica por el enrutamiento).

**D-C. `swapMicrophone(deviceId)` en `useAudioRecorder`** (solo con `isRecording`): `getUserMedia` con `deviceId: {exact}` y las constraints DEL MODO vigente → newMicStream; **orden connect-nuevo → disconnect-viejo → stop tracks viejos** (cero hueco de audio); actualizar `micStreamRef` y `setMicStream(newMicStream)` (→ `useMicLevel` re-arma el análisis sobre el nuevo mic y el banner se apaga SOLO cuando haya señal real); al éxito, `setPreferredMic(uid, deviceId)`. Si `getUserMedia` falla: la grabación SIGUE con el mic anterior intacto, error vía toast, sin persistir. En virtual, el swap opera sobre el micSource del mix existente (guardando referencia al source actual); si el modo virtual está en `"system"` (sin mic), el swap queda fuera de alcance (ver Q4).

**D-D. CTA en el banner H4 (`home.tsx`):** dentro del banner (rojo o ámbar), un control "Cambiar micrófono" (`data-testid="cta-cambiar-mic"`) que despliega la lista de `useMicDevices` (labels amigables, marcando el actual); elegir → `swapMicrophone(deviceId)`. El banner NO se oculta optimistamente: se apaga solo cuando el detector vea RMS ≥ umbral. Swap fallido → toast + banner permanece.

**D-E. Mic persistido al INICIAR grabación:** presencial y virtual usan el preferido con `{exact}` si existe y está en la lista; si el `getUserMedia` con `{exact}` falla o el dispositivo ya no existe → **fallback DECLARADO** (toast "Tu micrófono preferido no está disponible; usando el predeterminado") y continuar con default. Nunca un fallo de preferencia impide grabar.

**Micro-tareas (G0):** MT-M1 useMicDevices · MT-M2 enrutamiento + swap · MT-M3 CTA en banner · MT-M4 preferido al iniciar · MT-M5 endurecimiento adversarial.

# Claims a verificar

- **C1:** El enrutamiento por Web Audio en presencial preserva la señal (mismas constraints en el track fuente; el destination re-emite el PCM) sin degradar la calidad del acta ni el bitrate que ve el guard 422 del server, y sin cambiar el `mimeType` del recorder (la sesión del vault H6 sigue siendo válida).
- **C2:** El hot-swap (connect-nuevo → disconnect-viejo) mantiene UN solo archivo/grabación continua: el `MediaRecorder` nunca ve cambiar su stream (graba `dest.stream` estable) y los chunks del vault siguen fluyendo con la misma sesión.
- **C3:** Pasar el `micStream` NUEVO a `useMicLevel` (dep `[active, micStream]`) re-arma el detector automáticamente: banner activo con mic malo → swap a mic bueno → señal → banner se apaga sin código nuevo en el detector.
- **C4:** Ningún fallo del ciclo (preferido inexistente, `exact` que falla, swap fallido, AudioContext que no llega a `running`) puede cortar ni impedir una grabación — todos los caminos degradan a un estado funcional DECLARADO.
- **C5:** El diseño respeta las restricciones: 100% frontend, cero cambios de schema/openapi/server, y el modo virtual conserva su semántica actual (incluido `"system"` sin mic).

# Preguntas de diseño (recomendación ÚNICA y justificada cada una)

- **Q1:** En presencial, ¿AudioContext NUEVO por grabación reutilizando `audioCtxRef` y la limpieza existente (`cleanupStreams:147-151`), o un contexto compartido de larga vida? Considera: cierre correcto, autoplay policy, y que virtual ya crea el suyo en `mixAudioStreams`.
- **Q2:** ¿Qué hacer con la persistencia cuando el preferido resulta inválido al iniciar: ignorar y mantener la clave, avisar y mantener, o avisar y LIMPIAR la clave? Considera el caso "mic USB que hoy no está enchufado pero mañana sí".
- **Q3:** Durante el swap, ¿el detector H4 debe resetear su ventana (`lastLoudAt` → ahora, vía el re-arme natural del useEffect) o hace falta lógica extra para evitar un banner pegado/parpadeo en los ~cientos de ms del cambio? Traza el timing con la ventana de 5 s.
- **Q4:** Virtual en modo `"system"` (usuario denegó el mic al inicio): ¿debe el CTA permitir AÑADIR un micrófono a mitad de grabación (upgrade a `"system+mic"`) o queda explícitamente fuera de alcance de este ciclo? Considera que el banner ámbar ni siquiera aparece sin `micStream`.

# Anti-aprobación-automática

Si tu veredicto global es APROBADO (con o sin cambios), demuestra por qué cada trampa NO aplica (con el mecanismo del diseño que la neutraliza):

- **T1 — Silencio total por AudioContext suspendido:** hoy presencial graba el track directo (sin ctx); con D-B, un contexto que naciera `suspended` y jamás corriera haría que el recorder grabe SILENCIO puro toda la reunión (mucho peor que el statu quo). ¿La salvaguarda de D-B (running-check + fallback al camino directo) cierra el riesgo por completo? ¿Qué pasa si el contexto se suspende A MITAD de la grabación?
- **T2 — Hueco de audio en el swap:** `getUserMedia` del mic nuevo puede tardar segundos. ¿Qué se graba mientras tanto y puede el orden connect→disconnect dejar solapamiento audible (dos mics a la vez) o hueco?
- **T3 — Desenchufe del mic activo a mitad de grabación:** el track muere (`ended`). ¿La grabación sigue (dest.stream no termina) + el detector H4 acaba avisando + el CTA permite cambiar al mic que queda? ¿O algún camino mata el recorder?
- **T4 — Preferido "fantasma" tras cambiar de máquina:** los deviceId de `enumerateDevices` son POR ORIGEN Y POR MÁQUINA (y pueden rotar al limpiar cookies). El uid viaja entre Linux y Windows (ecosistema bi-máquina). ¿El diseño tolera un deviceId persistido de OTRA máquina sin romper el arranque de grabación?
- **T5 — Doble swap rápido:** el usuario elige dispositivo A y de inmediato B (dos `getUserMedia` en vuelo). ¿Puede quedar conectado un source huérfano (dos fuentes mezcladas) o un track sin stop?

# Entregable final

UN ÚNICO documento markdown listo para archivar: 1. Tabla C1..C5 con verdictos. 2. Respuestas Q1..Q4 (recomendación única). 3. Demostración T1..T5 si apruebas. 4. Lista numerada de CAMBIOS obligatorios si el veredicto es APROBADO CON CAMBIOS. 5. Veredicto global (APROBADO / APROBADO CON CAMBIOS / RECHAZADO). Recuerda: "APROBADO CON CAMBIOS" significa que se implementará CON tus cambios — no son sugerencias.
