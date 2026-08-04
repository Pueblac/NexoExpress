# Respuesta del Auditor — auditoría de código ronda 1 (ciclo 2026-07-30_selector_microfono)

**Archivada literal por el Arquitecto el 04-08-2026 (transportada por el Director desde Gemini 3.1 Pro High, conversación nueva). Sin ediciones.**

---

INFORME DE AUDITORÍA (Fase F6) — TURNO DE: Auditor
Ciclo: 2026-07-30_selector_microfono Veredicto: APROBADO CON OBSERVACIONES

1. CLAIMS AUDITADOS
C1 — Enrutamiento presencial con fallback declarado:

EVIDENCIA: useAudioRecorder.ts (+243..+261). Guard de swap: useAudioRecorder.ts (+397).
TRAZA: startRecording envuelve la creación de la topología en un try/catch. Si el ctx llega a running, el routing es exitoso. Si la conexión falla, routed queda false. En el fallback (!routed), se asigna directamente recordingStream = micRaw y se fija routingDisabledRef.current = true. En swapMicrophone, se verifica routingDisabledRef antes de continuar.
VEREDICTO: CONFIRMADO.
C2 — Cambio 1 aplicado en ambos modos:

EVIDENCIA: useAudioRecorder.ts (+128..+134 para declaración, +255 presencial, +287 virtual).
TRAZA: La función attachStateWatch envuelve ctx.onstatechange comprobando si el estado es suspended e invocando .resume(). Esta es llamada correctamente en la inicialización exitosa del AudioContext en presencial y en el mixAudioStreams del virtual.
VEREDICTO: CONFIRMADO.
C3 — Cerrojo + época (cambio 2):

EVIDENCIA: useAudioRecorder.ts (+396..+425).
TRAZA: Se lee isSwappingRef.current síncronamente al entrar. La época se incrementa ++swapEpochRef.current antes del evento asíncrono getUserMedia. Al resolver, se cruza la época guardada con la global y el estado de grabación; si hay mismatch, se ejecuta newMic.getTracks().forEach(t => t.stop()). El finally resetea el cerrojo sin falta.
VEREDICTO: CONFIRMADO.
C4 — Q2 fielmente implementado:

EVIDENCIA: useAudioRecorder.ts (+120..+127 en mixAudioStreams, +191..+202 en getMicWithPreference).
TRAZA: Ambos bloques intentan resolver el deviceId: { exact: preferred } en un try. En el catch, se establece el mensaje de fallback (micPreferredFailed=true o setMicFallbackNotice) y se dispara una segunda llamada default navigator.mediaDevices.getUserMedia. Ningún bloque invoca borrado en localStorage.
VEREDICTO: CONFIRMADO.
C5 — Traductor anti-Stereo-Mix:

EVIDENCIA: micDevices.ts (+20..+31 para regex, +39 filtrado).
TRAZA: La función friendlyMicName comprueba con regex estricto la presencia de monitor, stereo mix, mezcla estéreo o loopback, forzando el retorno del nombre "Audio del sistema (no capta tu voz)". listMicrophones descarta entradas sin deviceId válido (que previenen swaps vacíos) e incluye kind === "audioinput".
VEREDICTO: CONFIRMADO.
C6 — Gating del CTA y del hook de dispositivos:

EVIDENCIA: home.tsx (+109 gating del hook, +388..+391 botón CTA, +238 éxito modal, useAudioRecorder.ts +415 persistencia).
TRAZA: useMicDevices(isRecording && micSilent) garantiza que enumerateDevices corra sólo cuando el banner aplica. El CTA se ubica exclusivamente dentro de div data-testid="banner-mic-muerto". Si swapMicrophone retorna ok: true, se cierra el diálogo explícitamente y se invoca setPreferredMic.
VEREDICTO: CONFIRMADO.
2. ANÁLISIS DE TRAMPAS DIRIGIDAS (BUG TRAPPING)
T-a — Fuga de AudioContext en presencial:

EVIDENCIA: useAudioRecorder.ts (+251..+252).
TRAZA: Si createMediaStreamSource(micRaw) o source.connect(dest) arrojan una excepción (e.g. micRaw defectuoso), la ejecución salta al catch genérico vacío (línea 259). En ese flujo, routed es false, por lo que se entra al bloque fallback, pero el objeto audioCtx local en memoria que estaba en estado running (porque pasó el if) pierde su referencia sin invocar nunca audioCtx.close().
VEREDICTO: REFUTADO + BUG. Fuga confirmada de objetos AudioContext de hardware.
T-b — Cerrojo inobservable:

TRAZA: En JS puro y React event loops, if (ref.current) return; ref.current = true; es atómico e indivisible porque no hay await intermedio (no ocurre una yield de la call stack). Es imposible pasar dos veces síncronamente. Respecto a que el finally libere la ref antes de la verificación (antes de que useMicLevel apague el banner), es un comportamiento aceptable porque swapEpochRef garantiza que un tercer swap entrante simplemente desplazará al segundo de manera segura, cerrando los tracks de los intentos huérfanos.
VEREDICTO: REFUTADO. El diseño es concurrente seguro. NO es un bug.
T-c — Modal huérfano:

EVIDENCIA: home.tsx (+403) y useMicDevices.ts (+8..+10).
TRAZA: Si un ruido despierta el micrófono original, micSilent pasa a false. El componente se re-renderiza y oculta el banner del DOM. Al mismo tiempo, se invoca useMicDevices(false), lo que vacía el array microphones a []. Sin embargo, micSelectorOpen (estado de UI) permanece true, dejando el diálogo abierto. Con microphones vacío, la UI pinta "No se encontraron micrófonos.", degradando severamente la UX en esa ventana de tiempo.
VEREDICTO: CONFIRMADO + BUG.
T-d — Swap en virtual sin mic inicial (captureMode: "system"):

EVIDENCIA: useAudioRecorder.ts (+420..+423).
TRAZA: Si un usuario arranca un virtual sin micrófono, captureMode es "system". El nivel de audio evaluará a silencio (micSilent=true), habilitando el banner y el swap. Al ejecutar el swap, swapMicrophone empalmará exitosamente el nuevo micrófono al destRef (que estaba grabando la pantalla). El micSourceRef.current?.disconnect() es un no-op inofensivo. Sin embargo, no hay instrucción para promover captureMode a "system+mic". El estado miente hasta el fin de la sesión.
VEREDICTO: CONFIRMADO + BUG.
T-e — Constraints asimétricas:

EVIDENCIA: useAudioRecorder.ts (+191..+202 getMic y +404..+406 swapMicrophone).
TRAZA: swapMicrophone inyecta las constraints correctas dinámicamente observando modoRef.current. startRecording inicializa presencial con { echoCancellation: false, noiseSuppression: false, autoGainControl: true }.
VEREDICTO: CONFIRMADO.
3. LISTADO DE BUGS CONFIRMADOS
[Fuga de Memoria] AudioContext sin cerrar en el try/catch de enrutamiento

Archivo: useAudioRecorder.ts:259 (aprox. línea +259 del diff)
Traza: Error interno en nodos durante el running evita llegar a audioCtxRef.current = audioCtx y salta al catch de inicialización, abandonando el audioCtx sin hacer close().
Severidad: Media-Alta (filtración de buffers y handles de audio hardware; los navegadores imponen topes de AudioContexts por página).
[UX] Modal huérfano dice "No se encontraron micrófonos" al llegar audio

Archivo: home.tsx:109 (aprox. línea +109 del diff)
Traza: Si el CTA se pulsa pero se resuelve el silencio subyacente (llega un audio espontáneo), useMicDevices se vacía, pero el modal sigue renderizándose mostrándole al usuario un estado técnico de fallo (array vacío) en lugar de ocultar o cerrar el diálogo, ya que el banner desaparece de fondo.
Severidad: Baja (confusión transitoria del usuario, el modal puede cerrarse a mano).
[Metadatos] captureMode desactualizado tras hacer hot-swap inicial

Archivo: useAudioRecorder.ts:420 (aprox. zona final de swapMicrophone)
Traza: Un salto exitoso desde system en modo virtual no escala el tag semántico a system+mic, desalineando posibles etiquetas que persista createSession al vault u otros checks de métricas.
Severidad: Baja.
4. RESPUESTAS AL ARQUITECTO (D1..D4)
D1 (Riesgo de latencia/carga en Web Audio vs. MediaStream directo): Sí, existe un riesgo técnico de drift (desvío temporal) o clicks audibles en sesiones prolongadas (1-2 h). El enrutamiento por nodos en el AudioContext de Chrome está sujeto a la programación de hilos del renderizador y las frecuencias de resampleo del SO, y exige más ciclos de CPU sostenidos que grabar la tubería directa de C++ que usa el MediaStream puro. Si la máquina de campo tiene poca potencia o sufre throttling, podrían existir microcortes indetectables que a las horas deforman la temporización de la pista frente al display.

D2 (Interacción swap ↔ Vault H6 y mimeTypes): No hay riesgo de que el swap corrompa el códec. Al usar la arquitectura de MediaStreamDestination (dest.stream), el MediaRecorder consume un canal lógico que mantiene propiedades constantes (sample rate y channels de destino). Acoplar/desacoplar sources dinámicamente es soportado nativamente, el contenedor webm persistirá chunks contiguos válidos porque la pista receptora jamás se reinicia ni se renegocia.

D3 (Re-armado de UI si nuevo mic también está mudo): El ciclo se re-arma de manera impecable y sin residuos. Al cerrarse el modal exitosamente (setMicSelectorOpen(false)) e inyectar el stream nuevo, useMicLevel reinicia la evaluación desde cero sobre los tracks. En 5 segundos, la compuerta de silencio se reabre, invocando el renderizado del banner y repoblando las microphones options, dejándolo listo para un nuevo intento limpio.

D4 (Disparo único de fallback idéntico en React): Es correcto que llamadas repetidas con idéntico string no disparen renders. Sin embargo, no importa funcionalmente: en cada arranque de startRecording, el valor de micFallbackNotice se borra explícitamente a null de antemano (setMicFallbackNotice(null) zona +172 diff). Si un fallback idéntico vuelve a ocurrir en la siguiente grabación, el estado viajará null → string, garantizando el disparo del useEffect e invocando el toast cada vez que suceda un inicio con degradación.
