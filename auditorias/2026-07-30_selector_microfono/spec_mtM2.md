# Spec MT-M2 — Enrutamiento Web Audio del presencial + `swapMicrophone` (hot-swap sin cortar)

**Ciclo:** 2026-07-30_selector_microfono · F4 · **Rol:** Ingeniero (Sonnet, rotación asistida)
**Diseño aprobado:** r1 APROBADO CON CAMBIOS + G1 (30-07). Cambios del dictamen VINCULANTES aquí: **(1)** listener `statechange` con `resume()` automático en el AudioContext de grabación de AMBOS modos (T1 en vuelo); **(2)** cerrojo de concurrencia en el swap + el stream "perdedor" se detiene si resuelve tarde (T5). Regla de oro: **la grabación JAMÁS falla ni se degrada por el selector**.
**Repo:** `/home/pueblac/AndroidStudioProjects/ActaExpressWeb`, rama `linux`. Arranca con **MT-M1 aplicada** (existen `lib/micDevices.ts` y `hooks/useMicDevices.ts`, nada más). Toca SOLO `useAudioRecorder.ts`.

## Contexto mínimo verificado
- Presencial hoy (`useAudioRecorder.ts`, bloque `modo === "presencial"`): `getUserMedia({audio:{echoCancellation:false, noiseSuppression:false, autoGainControl:true}})` → ese stream crudo ES `recordingStream` y va directo a `new MediaRecorder(recordingStream)`.
- Virtual hoy: `mixAudioStreams(displayStream)` (líneas ~95-120) crea `AudioContext` + `createMediaStreamDestination()`, conecta displaySource y micSource (mic con `echoCancellation:true, noiseSuppression:true`) y devuelve `{ mixedStream, audioCtx, micStream }`. El recorder graba `mixedStream` (= dest.stream). El micSource NO se devuelve (habrá que exponerlo para el swap).
- `cleanupStreams` (:147-151) ya para tracks de display/mic y hace `audioCtxRef.current?.close().catch(() => {})`.
- MediaRecorder NO tolera cambiar los tracks del stream que graba → el hot-swap se hace conectando/desconectando sources sobre un destination ESTABLE.
- El vault H6 persiste chunks por `ondataavailable` — nada del swap debe reiniciar el MediaRecorder ni cambiar su `mimeType`.
- `useMicLevel` depende de `[active, micStream]`: exponer el stream CRUDO nuevo tras el swap re-arma el detector solo.

## Contrato (todo en `useAudioRecorder.ts`)

### 1. Refs nuevos
`destRef` (MediaStreamAudioDestinationNode | null), `micSourceRef` (MediaStreamAudioSourceNode | null), `isSwappingRef` (boolean), `swapEpochRef` (number), `routingDisabledRef` (boolean), `modoRef` (ModoReunion | null — el modo de la grabación en curso).

### 2. Presencial enrutado (reemplaza la asignación directa)
Tras el `getUserMedia` presencial exitoso (`micRaw`):
```ts
let routed = false;
try {
  const audioCtx = new AudioContext();
  if (audioCtx.state === "suspended") { await audioCtx.resume().catch(() => {}); }
  if (audioCtx.state === "running") {
    const dest = audioCtx.createMediaStreamDestination();
    const source = audioCtx.createMediaStreamSource(micRaw);
    source.connect(dest);
    audioCtxRef.current = audioCtx;
    destRef.current = dest;
    micSourceRef.current = source;
    attachStateWatch(audioCtx);          // ver punto 4
    recordingStream = dest.stream;
    routed = true;
  } else {
    audioCtx.close().catch(() => {});
  }
} catch { /* enrutamiento fallido */ }
if (!routed) {
  // FALLBACK DECLARADO (T1 arranque): grabar el stream crudo directo, como hoy.
  recordingStream = micRaw;
  routingDisabledRef.current = true;
  console.warn("[selector-mic] AudioContext no llegó a running: grabación directa, hot-swap deshabilitado");
}
```
En ambos caminos: `micStreamRef.current = micRaw; setMicStream(micRaw); mode = "microphone";` (el detector SIEMPRE ve el crudo). `routingDisabledRef.current = false` al inicio de cada `startRecording`, junto a los resets existentes; `modoRef.current = modo`.

### 3. Virtual: exponer el micSource y vigilar el contexto
`mixAudioStreams` amplía su retorno a `{ mixedStream, audioCtx, micStream, micSource }` (micSource: el `MediaStreamAudioSourceNode` del mic o null). En el bloque virtual de `startRecording`: guardar `micSourceRef.current = micSource`, `destRef.current` = el destination (exponlo también en el retorno como `dest`), y `attachStateWatch(audioCtx)`.

### 4. `attachStateWatch(audioCtx)` — cambio 1 del dictamen (AMBOS modos)
```ts
const attachStateWatch = (ctx: AudioContext) => {
  ctx.onstatechange = () => {
    if (ctx.state === "suspended") {
      console.warn("[selector-mic] AudioContext suspendido en vuelo; intentando resume()");
      ctx.resume().catch(() => {});
    }
  };
};
```

### 5. `swapMicrophone(deviceId)` — expuesto en el retorno del hook
Firma: `swapMicrophone: (deviceId: string) => Promise<{ ok: boolean; message?: string }>`. Añadirla a `UseAudioRecorderReturn`.
```ts
const swapMicrophone = useCallback(async (deviceId: string) => {
  if (!isRecording) return { ok: false, message: "No hay grabación activa." };
  if (routingDisabledRef.current || !audioCtxRef.current || !destRef.current)
    return { ok: false, message: "El cambio de micrófono no está disponible en esta grabación." };
  if (isSwappingRef.current) return { ok: false, message: "Ya hay un cambio de micrófono en curso." };  // cambio 2
  isSwappingRef.current = true;
  const epoch = ++swapEpochRef.current;
  try {
    const constraints = modoRef.current === "virtual"
      ? { deviceId: { exact: deviceId }, echoCancellation: true, noiseSuppression: true }
      : { deviceId: { exact: deviceId }, echoCancellation: false, noiseSuppression: false, autoGainControl: true };
    const newMic = await navigator.mediaDevices.getUserMedia({ audio: constraints });
    if (epoch !== swapEpochRef.current || !mediaRecorderRef.current || mediaRecorderRef.current.state !== "recording") {
      newMic.getTracks().forEach((t) => t.stop());              // "perdedor" tardío (cambio 2)
      return { ok: false, message: "El cambio llegó tarde y fue descartado." };
    }
    const newSource = audioCtxRef.current.createMediaStreamSource(newMic);
    newSource.connect(destRef.current);                          // connect-nuevo…
    micSourceRef.current?.disconnect();                          // …disconnect-viejo…
    micStreamRef.current?.getTracks().forEach((t) => t.stop());  // …stop tracks viejos
    micSourceRef.current = newSource;
    micStreamRef.current = newMic;
    setMicStream(newMic);                                        // re-arma useMicLevel
    if (user) setPreferredMic(user.uid, deviceId);               // persiste como default (G0-b)
    return { ok: true };
  } catch (err) {
    return { ok: false, message: err instanceof Error ? err.message : "No se pudo cambiar el micrófono." };
  } finally {
    isSwappingRef.current = false;
  }
}, [isRecording, user]);
```
Import `setPreferredMic` desde `../lib/micDevices`. PROHIBIDO tocar el MediaRecorder, el vault o `stopRecording` desde el swap.

### 6. Limpieza
`cleanupStreams` añade: `micSourceRef.current = null; destRef.current = null;` (el `close()` del ctx ya existe). `stopRecording` no cambia.

## Restricciones
Solo `useAudioRecorder.ts`. NO tocar home.tsx, useMicLevel, micDevices (solo importarlo). Sin dependencias nuevas. No commit.

## DoD (salida literal al informe)
1. `pnpm run typecheck` → exit 0.
2. `grep -n "swapMicrophone\|attachStateWatch\|routingDisabledRef\|isSwappingRef\|swapEpochRef\|createMediaStreamDestination\|onstatechange\|setPreferredMic" artifacts/acta-express/src/hooks/useAudioRecorder.ts`.
3. **A/B razonado** citando líneas del diff: (a) presencial con ctx `running` → recorder graba `dest.stream`, detector ve el crudo; (b) ctx que no llega a `running` → fallback directo declarado + `routingDisabledRef` + swap responde "no disponible" (T1 arranque); (c) swap feliz: orden connect→disconnect→stop y CERO cambios en `mediaRecorderRef`; (d) doble swap → segundo intento rechazado por cerrojo (T5); (e) swap que resuelve tras `stopRecording` → tracks del perdedor detenidos, sin conexión (T5); (f) `onstatechange` a suspended en vuelo → `resume()` (cambio 1, citar en presencial Y virtual).
4. `git diff` → SOLO `useAudioRecorder.ts`. Diff literal íntegro al informe.

## Protocolo de dudas
El orden del swap, el cerrojo, la época y el fallback son DISEÑO CONGELADO. Detalles de tipado: lo más simple, declarado. Dudas de contrato → DETENTE.

## Informe: `informe_mtM2.md` — formato estándar.
