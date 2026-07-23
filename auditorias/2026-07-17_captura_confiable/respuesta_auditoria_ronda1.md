# Respuesta del Auditor (Gemini 3.1 Pro High) — auditoría de código ronda 1, tanda MT-C1..C5

> Archivada TAL CUAL fue entregada por el Director el 23-07-2026 (transporte manual,
> chat nuevo con inicialización de identidad). Nota de archivo: el pegado en el chat
> degradó el formato de la tabla de veredictos (la fila C1 llega truncada en
> "`disabled={isRecording"); el contenido se conserva sin edición.
> La validación anti-bluff del Arquitecto va en `validacion_antibluff_ronda1.md`.

---

Auditoría Adversarial - Captura Confiable (Ciclo 2026-07-17)
1. Veredictos (C1..C6)
ID	Veredicto	Evidencia y Traza
C1	CONFIRMADO	Evidencia: home.tsx:73-77 (inicialización de estado) y home.tsx:80-83 (persistencia en handleModoReunionChange), más home.tsx:277 (`disabled={isRecording
C2	CONFIRMADO	Evidencia: useAudioRecorder.ts:174-179 (return sin arrancar tras fallo en getDisplayAudioStream). El diff muestra que el bloque try { getUserMedia } del antiguo fallback fue eliminado en lugar de reubicado (líneas eliminadas 208-218 del diff).
Traza: Al llamar startRecording("virtual"), se invoca getDisplayAudioStream(). Si se cancela, displayResult es null, se asigna el error en setError y ocurre el return. La ejecución se interrumpe y la app no arranca ninguna grabación ni setea isRecording=true.
C3	CONFIRMADO	Evidencia: useAudioRecorder.ts:161-163 para constraints (echoCancellation: false, noiseSuppression: false, autoGainControl: true). Y useAudioRecorder.ts:129 (const [micStream, setMicStream] = useState...).
Traza: En modo presencial, el hook solicita el mic. Si es exitoso, invoca setMicStream(recordingStream) (línea 165), lo cual hace re-renderizar la UI exportando la instancia válida, permitiendo a useMicLevel recibirlo y arrancar su ciclo.
C4	CONFIRMADO	Evidencia: useMicLevel.ts:4 (MIC_RMS_THRESHOLD = 0.01), useMicLevel.ts:60-63 (if audioCtx.state !== "running", asigna lastLoudAt = now), useMicLevel.ts:89-93 (cleanup con setMicSilent(false)).
Traza: Dentro de setInterval, si el micro no pasa 0.01 y el contexto corre, lastLoudAt no se actualiza. A los 5000/10000ms la difierecia dispara setMicSilent(true). Al desactivar, el cleanup desmonta todo y resetea la flag.
C5	CONFIRMADO	Evidencia: home.tsx:258-272 (condición isRecording && micSilent), y estilos en ternario usando modoReunion. El detector en useMicLevel.ts solo retorna micSilent, no invoca la parada.
Traza: Cuando se reporta micSilent=true y isRecording=true, el bloque del banner en el JSX se renderiza. No hay callbacks en el hook que puedan abortar la grabación.
C6	CONFIRMADO	Traza: t=0 usuario pulsa grabar (presencial). t=100 getUserMedia({ audio: { echoCancellation: false, noiseSuppression: false, autoGainControl: true } }) resuelve. t=160 estado actualiza micStream. t=170 hook useMicLevel corre; audioCtx es suspended y corre resume(). t=370 y t=570 contexto no corre, lastLoudAt es actualizado forzosamente a now (570). t=600 pasa a running. t=770 buffers con 0.0, rms 0.0 < 0.01, lastLoudAt no se actualiza (se queda en 570). t=5570 ocurre que 5570 - 570 = 5000 >= 5000. Dispara setMicSilent(true).
JSX renderizado: <div data-testid="banner-mic-muerto" className="flex items-center justify-center gap-2 text-destructive text-sm mt-2 bg-destructive/10 px-4 py-2 rounded-md"><AlertCircle className="w-4 h-4" />⚠️ No se detecta señal de tu micrófono — revisa que no esté silenciado en el sistema.</div>
t=8000 desmutea (RMS 0.05). t=8170 tick del hook mide 0.05. Actualiza lastLoudAt = 8170. Diferencia es 0. Dispara setMicSilent(false). Banner desaparece.
2. Preguntas de Control (Q1..Q4)
Q1:

(a) Error de virtual cancelado (useAudioRecorder.ts:176): "No se capturó audio. Al compartir, asegúrate de seleccionar 'Pestaña de Chrome' y tener activa la casilla 'Compartir audio de la pestaña'."
(b) Banner presencial (home.tsx:269): "⚠️ No se detecta señal de tu micrófono — revisa que no esté silenciado en el sistema."
(c) Banner virtual (home.tsx:270): "Tu micrófono no aporta señal. Si solo escuchas la reunión está bien; si querías hablar, revisa que no esté silenciado."
Q2: Si el audioCtx.resume() falla y se queda en "suspended" permanentemente, useMicLevel.ts:60 continuará ejecutando lastLoudAt = now; en cada tick. A los 60 s, now - lastLoudAt será siempre ~0, por lo que micSilent será false. Este comportamiento es CORRECTO para la mitigación del autoplay de los navegadores: si no tenemos permiso de procesamiento crudo, disparar un falso positivo por "micrófono muerto" cuando el hardware está sano y capta audio confundiría y engañaría al usuario, degradando enormemente la confianza en la UI.

Q3:

saved === "virtual" (persistencia): localStorage.getItem("actaexpress:modoReunion:u1") se invoca (home.tsx:75). Retorna "virtual". El condicional ternario asume "virtual" y el useState lo inicializa en modoReunion = "virtual".
saved === null (primer uso): Se invoca la misma clave. Retorna null. Ternario devuelve "presencial". modoReunion inicializa en "presencial".
saved === "basura" (corrupto): Retorna "basura". Ternario devuelve "presencial". Inicializador citado:
typescript
const [modoReunion, setModoReunion] = useState<ModoReunion>(() => {
    if (!user) return "presencial";
    const saved = localStorage.getItem(`actaexpress:modoReunion:${user.uid}`);
    return saved === "virtual" ? "virtual" : "presencial";
  });
Q4: Si deniega el micrófono en virtual, mixAudioStreams en el backend devuelve un stream mixto sin track de micro. En useAudioRecorder.ts:186, mixMicStream es null. mode se asigna a "system" (línea 188: mode = mixMicStream ? "system+mic" : "system";). El micStream recibido por el hook será null. En useMicLevel.ts:32, el if (!active || !micStream) retorna rápido, dejando micSilent = false. NO aparecerá el aviso ámbar. Es un comportamiento ACEPTABLE/CORRECTO: el usuario denegó explícitamente el permiso, por lo que el sistema asume que el usuario es consciente de no grabar su micro; el aviso de micrófono muerto tiene sentido para micrófonos autorizados pero mudos en software/hardware por debajo del sistema operativo.

3. Demostración Anti-Trampas (T1..T5)
T1 (Arranque suspendido): DESCARTADA. Según useMicLevel.ts:60, si state !== "running", el reloj no acumula diferencia y la variable lastLoudAt se sincroniza con el tiempo actual impidiendo la suma de tiempo en silencio.
T2 (Cambio de modo en vivo): DESCARTADA. El RadioGroup posee disabled={isRecording} (home.tsx:285), por ende el usuario no interactúa con él. Aún si se fuerza por DevTools, modoRef.current se lee instantáneamente, por lo que el banner usaría el tiempo windowMs del nuevo modo sin inconsistencias internas de estado.
T3 (Doble grabación consecutiva): DESCARTADA. Tras la primera sesión, stopRecording invoca setMicStream(null) (useAudioRecorder.ts:146), lo cual desmonta el efecto de useMicLevel, dispara clearInterval y limpia recursos. Al grabar la segunda vez, se inicializa nuevo hardware y ciclo.
T4 (Fin compartición virtual): DESCARTADA. Al terminar el track (ended), se dispara stopRecording() (useAudioRecorder.ts:192). Esto establece active=false y limpia micStream. El useEffect del detector ejecuta su cleanup cerrando AudioContext y desapareciendo el banner al emitir setMicSilent(false).
T5 (Usuario nulo): ¡VERIFICADA (BUG ENCONTRADO)! En el primer render por carrera de autenticación, user es null. El useState de home.tsx:74 ejecuta if (!user) return "presencial". Cuando la promise de auth resuelve, se re-renderiza Home, PERO useState ignora su callback de inicialización. No hay un useEffect reactivo a los cambios de user para releer el localStorage. Por lo tanto, el usuario tendrá un modo permanentemente pisado por "presencial" en arranques limpios a pesar de sus preferencias persistidas, rompiendo C1 en escenario real. Severidad MEDIA.
4. Opinión Fundada (D1..D4)
D1 (Umbral y Sala Callada): El riesgo de falso positivo en presencial por una sala muy silenciosa es alto. El noise floor puede decaer por debajo del 0.01 si no hay voces u otros ruidos ambientales (es -40 dBFS). Se sugiere un modo de calibración y/o la consideración de umbrales como 0.005 o un botón explícito de ignorar banner, de modo que el E2E cubra la condición "sala vacía sin voz por más de 5s".
D2 (Reloj Throttled): Las pestañas visibles no son mitigadas y performance.now() mantiene un reloj relativo correcto. Incluso ante throttling (1 tick por seg/min), now - lastLoudAt calculará correctamente la delta al regresar a la ejecución, solo introduciendo latencia al visualizado, lo cual es de riesgo mínimo frente al valor del feature.
D3 (Fatiga de Alarma Virtual): Dado el aviso ámbar sin función para cerrarse y en caso de usuario oyente legítimo sin intención de compartir voz, habrá fatiga de alarma. Es altamente recomendable la introducción de un botón (X) o "descartar aviso" con su propio estado React ignorado localmente, sin rediseño del hook original.
D4 (E2E Fino): Solo la saturación asíncrona del event loop podría desviar la latencia de 5.2s. Dado el setInterval en 200 ms, es mecánicamente esperable una desviación de hasta esa ventana si React prioriza updates u ocurren tirones del encoder de MediaRecorder.
5. Veredicto Global
VEREDICTO GLOBAL: APROBADO CON OBSERVACIONES

La estructura y requerimientos fundamentales de la "captura confiable" funcionan como se diseñaron y pasaron el modelo adversarial exceptuando el bug de ciclo de vida detectado por la Trampa 5. Se ordena enviar una sub-tarea para parchear la persistencia sobre home.tsx integrando un useEffect a cambios en user para leer correctamente el localStorage durante el montaje final.
