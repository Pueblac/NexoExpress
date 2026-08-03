# Informe MT-M2 — Enrutamiento Web Audio del presencial + `swapMicrophone` (hot-swap sin cortar)

**Ciclo:** 2026-07-30_selector_microfono · F4 · **Rol:** Ingeniero (Sonnet, rotación asistida)
**Repo:** `/home/pueblac/AndroidStudioProjects/ActaExpressWeb`, rama `linux`.
**Archivo tocado:** SOLO `artifacts/acta-express/src/hooks/useAudioRecorder.ts`.

## Precondición (paso 2 del protocolo)

```
$ git -C /home/pueblac/AndroidStudioProjects/ActaExpressWeb status --short
?? artifacts/acta-express/src/hooks/useMicDevices.ts
?? artifacts/acta-express/src/lib/micDevices.ts
```

Exactamente los 2 nuevos de MT-M1, nada más. OK para continuar.

## Qué se hizo

Leído `useAudioRecorder.ts` completo (314 líneas originales) antes de tocar nada. Implementado el contrato al pie de la letra:

1. **Import** de `setPreferredMic` desde `../lib/micDevices`.
2. **`UseAudioRecorderReturn`** amplía con `swapMicrophone: (deviceId: string) => Promise<{ ok: boolean; message?: string }>`.
3. **`mixAudioStreams`** amplía su retorno a `{ mixedStream, audioCtx, micStream, micSource, dest }` (antes `micSource` era local y se perdía; ahora se expone).
4. **`attachStateWatch(ctx)`** — función a nivel de módulo (no depende de closures del hook, solo del `ctx` recibido), asignada como `ctx.onstatechange`; en `suspended` intenta `resume()`. Cambio 1 del dictamen, cableada en AMBOS modos.
5. **Refs nuevos**: `destRef`, `micSourceRef`, `isSwappingRef`, `swapEpochRef`, `routingDisabledRef`, `modoRef` — todos declarados junto a los refs existentes.
6. **Presencial enrutado**: se separó la obtención de `micRaw` (con su try/catch original que sigue devolviendo error de UI si falla `getUserMedia`) del enrutamiento por `AudioContext` (try/catch silencioso, "enrutamiento fallido"). Si el contexto llega a `running`: crea `dest`, conecta `micRaw` → `dest`, guarda refs, arma `attachStateWatch`, `recordingStream = dest.stream`. Si no llega a `running` (ni tras `resume()`): fallback declarado, `recordingStream = micRaw`, `routingDisabledRef.current = true`, `console.warn`. En ambos caminos: `micStreamRef.current = micRaw; setMicStream(micRaw); mode = "microphone"` — el detector de nivel SIEMPRE ve el stream crudo, tal como pide el contrato.
7. **Virtual**: el bloque ahora desestructura también `micSource` y `dest` de `mixAudioStreams`, los guarda en `micSourceRef`/`destRef`, y arma `attachStateWatch(audioCtx)`.
8. **`routingDisabledRef.current = false`** y **`modoRef.current = modo`** al inicio de cada `startRecording`, junto a los resets existentes (antes de la ramificación presencial/virtual, ya que el contrato indica que `modoRef` se fija con independencia del modo).
9. **`swapMicrophone`** — implementado exactamente como en el contrato: guardas de "no hay grabación" / "no disponible" (routing deshabilitado o sin `audioCtxRef`/`destRef`) / cerrojo de concurrencia (`isSwappingRef`) → época (`swapEpochRef`) → `getUserMedia` con constraints según `modoRef.current` → chequeo de época+estado del recorder (perdedor tardío: para tracks y devuelve mensaje) → `connect` nuevo → `disconnect` viejo → `stop` tracks viejos → actualiza refs/estado → persiste preferencia con `setPreferredMic` si hay `user` → `finally` libera el cerrojo. No toca `mediaRecorderRef`, el vault ni `stopRecording`.
10. **`cleanupStreams`** añade `micSourceRef.current = null; destRef.current = null;` (el `close()` del ctx ya existía). `stopRecording` sin cambios.
11. Retorno del hook añade `swapMicrophone`.

## Diff literal íntegro

```diff
diff --git a/artifacts/acta-express/src/hooks/useAudioRecorder.ts b/artifacts/acta-express/src/hooks/useAudioRecorder.ts
index 571a0b4..a6d92f5 100644
--- a/artifacts/acta-express/src/hooks/useAudioRecorder.ts
+++ b/artifacts/acta-express/src/hooks/useAudioRecorder.ts
@@ -1,6 +1,7 @@
 import { useState, useRef, useCallback } from "react";
 import { useAuth } from "@/context/AuthContext";
 import { createSession, appendChunk, purgeStaleKeepNewest, isVaultAvailable } from "../lib/recordingVault";
+import { setPreferredMic } from "../lib/micDevices";
 
 type CaptureMode = "system+mic" | "system" | "microphone" | null;
 
@@ -17,6 +18,7 @@ interface UseAudioRecorderReturn {
   captureMode: CaptureMode;
   micStream: MediaStream | null;
   vaultSessionId: string | null;
+  swapMicrophone: (deviceId: string) => Promise<{ ok: boolean; message?: string }>;
 }
 
 export function blobToBase64(blob: Blob): Promise<string> {
@@ -99,6 +101,8 @@ async function mixAudioStreams(displayStream: MediaStream): Promise<{
   mixedStream: MediaStream;
   audioCtx: AudioContext;
   micStream: MediaStream | null;
+  micSource: MediaStreamAudioSourceNode | null;
+  dest: MediaStreamAudioDestinationNode;
 }> {
   const audioCtx = new AudioContext();
   const dest = audioCtx.createMediaStreamDestination();
@@ -109,19 +113,29 @@ async function mixAudioStreams(displayStream: MediaStream): Promise<{
 
   // Try to add microphone
   let micStream: MediaStream | null = null;
+  let micSource: MediaStreamAudioSourceNode | null = null;
   try {
     micStream = await navigator.mediaDevices.getUserMedia({
       audio: { echoCancellation: true, noiseSuppression: true },
     });
-    const micSource = audioCtx.createMediaStreamSource(micStream);
+    micSource = audioCtx.createMediaStreamSource(micStream);
     micSource.connect(dest);
   } catch {
     // Microphone unavailable — that's OK, display audio alone is still useful
   }
 
-  return { mixedStream: dest.stream, audioCtx, micStream };
+  return { mixedStream: dest.stream, audioCtx, micStream, micSource, dest };
 }
 
+const attachStateWatch = (ctx: AudioContext) => {
+  ctx.onstatechange = () => {
+    if (ctx.state === "suspended") {
+      console.warn("[selector-mic] AudioContext suspendido en vuelo; intentando resume()");
+      ctx.resume().catch(() => {});
+    }
+  };
+};
+
 export function useAudioRecorder(): UseAudioRecorderReturn {
   const { user } = useAuth();
   const [isRecording, setIsRecording] = useState(false);
@@ -143,6 +157,12 @@ export function useAudioRecorder(): UseAudioRecorderReturn {
   const vaultSessionIdRef = useRef<string | null>(null);
   const vaultDisabledRef = useRef<boolean>(false);
   const chunkSeqRef = useRef<number>(0);
+  const destRef = useRef<MediaStreamAudioDestinationNode | null>(null);
+  const micSourceRef = useRef<MediaStreamAudioSourceNode | null>(null);
+  const isSwappingRef = useRef<boolean>(false);
+  const swapEpochRef = useRef<number>(0);
+  const routingDisabledRef = useRef<boolean>(false);
+  const modoRef = useRef<ModoReunion | null>(null);
 
   const cleanupStreams = useCallback(() => {
     displayStreamRef.current?.getTracks().forEach((t) => t.stop());
@@ -151,6 +171,8 @@ export function useAudioRecorder(): UseAudioRecorderReturn {
     displayStreamRef.current = null;
     micStreamRef.current = null;
     audioCtxRef.current = null;
+    micSourceRef.current = null;
+    destRef.current = null;
     setMicStream(null);
   }, []);
 
@@ -160,24 +182,57 @@ export function useAudioRecorder(): UseAudioRecorderReturn {
     setAudioBase64(null);
     setDuration(0);
     chunksRef.current = [];
+    routingDisabledRef.current = false;
+    modoRef.current = modo;
 
-    let recordingStream: MediaStream;
+    let recordingStream!: MediaStream;
     let mode: CaptureMode;
 
     if (modo === "presencial") {
-      // --- Presencial: micrófono directo, sin diálogo de compartir ---
+      // --- Presencial: micrófono directo, enrutado por Web Audio para permitir hot-swap ---
+      let micRaw: MediaStream;
       try {
-        recordingStream = await navigator.mediaDevices.getUserMedia({
+        micRaw = await navigator.mediaDevices.getUserMedia({
           audio: { echoCancellation: false, noiseSuppression: false, autoGainControl: true },
         });
-        micStreamRef.current = recordingStream;
-        setMicStream(recordingStream);
-        mode = "microphone";
       } catch (err: unknown) {
         const msg = err instanceof Error ? err.message : "No se pudo acceder al micrófono";
         setError(msg);
         return;
       }
+
+      let routed = false;
+      try {
+        const audioCtx = new AudioContext();
+        if (audioCtx.state === "suspended") {
+          await audioCtx.resume().catch(() => {});
+        }
+        if (audioCtx.state === "running") {
+          const dest = audioCtx.createMediaStreamDestination();
+          const source = audioCtx.createMediaStreamSource(micRaw);
+          source.connect(dest);
+          audioCtxRef.current = audioCtx;
+          destRef.current = dest;
+          micSourceRef.current = source;
+          attachStateWatch(audioCtx);
+          recordingStream = dest.stream;
+          routed = true;
+        } else {
+          audioCtx.close().catch(() => {});
+        }
+      } catch {
+        /* enrutamiento fallido */
+      }
+      if (!routed) {
+        // FALLBACK DECLARADO (T1 arranque): grabar el stream crudo directo, como hoy.
+        recordingStream = micRaw;
+        routingDisabledRef.current = true;
+        console.warn("[selector-mic] AudioContext no llegó a running: grabación directa, hot-swap deshabilitado");
+      }
+
+      micStreamRef.current = micRaw;
+      setMicStream(micRaw);
+      mode = "microphone";
     } else {
       // --- Virtual: display + mix. Sin fallback silencioso a micrófono ---
       const displayResult = await getDisplayAudioStream();
@@ -192,9 +247,14 @@ export function useAudioRecorder(): UseAudioRecorderReturn {
       displayStreamRef.current = displayResult.stream;
 
       // Mix with microphone
-      const { mixedStream, audioCtx, micStream: mixMicStream } = await mixAudioStreams(displayResult.stream);
+      const { mixedStream, audioCtx, micStream: mixMicStream, micSource, dest } = await mixAudioStreams(
+        displayResult.stream
+      );
       audioCtxRef.current = audioCtx;
       micStreamRef.current = mixMicStream;
+      micSourceRef.current = micSource;
+      destRef.current = dest;
+      attachStateWatch(audioCtx);
       setMicStream(mixMicStream);
       recordingStream = mixedStream;
       mode = mixMicStream ? "system+mic" : "system";
@@ -299,6 +359,38 @@ export function useAudioRecorder(): UseAudioRecorderReturn {
     });
   }, [isRecording]);
 
+  const swapMicrophone = useCallback(async (deviceId: string) => {
+    if (!isRecording) return { ok: false, message: "No hay grabación activa." };
+    if (routingDisabledRef.current || !audioCtxRef.current || !destRef.current)
+      return { ok: false, message: "El cambio de micrófono no está disponible en esta grabación." };
+    if (isSwappingRef.current) return { ok: false, message: "Ya hay un cambio de micrófono en curso." }; // cambio 2
+    isSwappingRef.current = true;
+    const epoch = ++swapEpochRef.current;
+    try {
+      const constraints = modoRef.current === "virtual"
+        ? { deviceId: { exact: deviceId }, echoCancellation: true, noiseSuppression: true }
+        : { deviceId: { exact: deviceId }, echoCancellation: false, noiseSuppression: false, autoGainControl: true };
+      const newMic = await navigator.mediaDevices.getUserMedia({ audio: constraints });
+      if (epoch !== swapEpochRef.current || !mediaRecorderRef.current || mediaRecorderRef.current.state !== "recording") {
+        newMic.getTracks().forEach((t) => t.stop());              // "perdedor" tardío (cambio 2)
+        return { ok: false, message: "El cambio llegó tarde y fue descartado." };
+      }
+      const newSource = audioCtxRef.current.createMediaStreamSource(newMic);
+      newSource.connect(destRef.current);                          // connect-nuevo…
+      micSourceRef.current?.disconnect();                          // …disconnect-viejo…
+      micStreamRef.current?.getTracks().forEach((t) => t.stop());  // …stop tracks viejos
+      micSourceRef.current = newSource;
+      micStreamRef.current = newMic;
+      setMicStream(newMic);                                        // re-arma useMicLevel
+      if (user) setPreferredMic(user.uid, deviceId);               // persiste como default (G0-b)
+      return { ok: true };
+    } catch (err) {
+      return { ok: false, message: err instanceof Error ? err.message : "No se pudo cambiar el micrófono." };
+    } finally {
+      isSwappingRef.current = false;
+    }
+  }, [isRecording, user]);
+
   return {
     isRecording,
     startRecording,
@@ -310,5 +402,6 @@ export function useAudioRecorder(): UseAudioRecorderReturn {
     captureMode,
     micStream,
     vaultSessionId,
+    swapMicrophone,
   };
 }
```

## Evidencia DoD (salidas literales)

### 1. `pnpm run typecheck` → exit 0

```
$ pnpm run typecheck
$ pnpm run typecheck:libs && pnpm -r --filter "./artifacts/**" --filter "./scripts" --if-present run typecheck
$ tsc --build
Scope: 4 of 9 workspace projects
artifacts/acta-express typecheck$ tsc -p tsconfig.json --noEmit
artifacts/api-server typecheck$ tsc -p tsconfig.json --noEmit
artifacts/mockup-sandbox typecheck$ tsc -p tsconfig.json --noEmit
scripts typecheck$ tsc -p tsconfig.json --noEmit
scripts typecheck: Done
artifacts/api-server typecheck: Done
artifacts/mockup-sandbox typecheck: Done
artifacts/acta-express typecheck: Done
EXIT_CODE=0
```

### 2. `grep -n` de los símbolos clave

```
4:import { setPreferredMic } from "../lib/micDevices";
21:  swapMicrophone: (deviceId: string) => Promise<{ ok: boolean; message?: string }>;
108:  const dest = audioCtx.createMediaStreamDestination();
130:const attachStateWatch = (ctx: AudioContext) => {
131:  ctx.onstatechange = () => {
162:  const isSwappingRef = useRef<boolean>(false);
163:  const swapEpochRef = useRef<number>(0);
164:  const routingDisabledRef = useRef<boolean>(false);
185:    routingDisabledRef.current = false;
211:          const dest = audioCtx.createMediaStreamDestination();
217:          attachStateWatch(audioCtx);
229:        routingDisabledRef.current = true;
257:      attachStateWatch(audioCtx);
362:  const swapMicrophone = useCallback(async (deviceId: string) => {
364:    if (routingDisabledRef.current || !audioCtxRef.current || !destRef.current)
366:    if (isSwappingRef.current) return { ok: false, message: "Ya hay un cambio de micrófono en curso." }; // cambio 2
367:    isSwappingRef.current = true;
368:    const epoch = ++swapEpochRef.current;
374:      if (epoch !== swapEpochRef.current || !mediaRecorderRef.current || mediaRecorderRef.current.state !== "recording") {
385:      if (user) setPreferredMic(user.uid, deviceId);               // persiste como default (G0-b)
390:      isSwappingRef.current = false;
405:    swapMicrophone,
```

### 3. A/B razonado (citando líneas del diff)

- **(a) Presencial con `ctx` `running` → recorder graba `dest.stream`, detector ve el crudo.**
  Líneas del diff: bloque `if (audioCtx.state === "running") { const dest = ...; ...; recordingStream = dest.stream; routed = true; }` (dentro del `try` de enrutamiento). Fuera del `if/else` de routed: `micStreamRef.current = micRaw; setMicStream(micRaw);` se ejecuta SIEMPRE, sea cual sea el camino. `new MediaRecorder(recordingStream)` (línea 280, sin cambios) recibe `dest.stream` en este camino. `useMicLevel` (fuera de este archivo) consume `micStream` del estado, que aquí es `micRaw` — el crudo — nunca `dest.stream`. Confirmado: recorder graba el stream enrutado, el detector ve el crudo.

- **(b) `ctx` que no llega a `running` → fallback directo declarado + `routingDisabledRef` + swap responde "no disponible" (T1 arranque).**
  Líneas: `} else { audioCtx.close().catch(() => {}); }` seguido de `if (!routed) { recordingStream = micRaw; routingDisabledRef.current = true; console.warn(...); }`. En `swapMicrophone`: `if (routingDisabledRef.current || !audioCtxRef.current || !destRef.current) return { ok: false, message: "El cambio de micrófono no está disponible en esta grabación." };` — como en este camino `audioCtxRef.current` NUNCA se asigna (queda en su valor previo, `null` al inicio de una grabación nueva ya que `cleanupStreams`/inicialización lo deja `null`), la guarda dispara igualmente aunque `routingDisabledRef` no se chequeara sola. Doble cinturón: mensaje "no disponible" garantizado.

- **(c) Swap feliz: orden connect→disconnect→stop y CERO cambios en `mediaRecorderRef`.**
  Líneas: `const newSource = audioCtxRef.current.createMediaStreamSource(newMic); newSource.connect(destRef.current);` (connect nuevo) → `micSourceRef.current?.disconnect();` (disconnect viejo) → `micStreamRef.current?.getTracks().forEach((t) => t.stop());` (stop tracks viejos) — orden literal connect→disconnect→stop tal como exige el contrato. En ningún punto de `swapMicrophone` se lee ni escribe `mediaRecorderRef.current` salvo para LEER su `.state` en el chequeo de época (línea `!mediaRecorderRef.current || mediaRecorderRef.current.state !== "recording"`), nunca se reasigna ni se llama método sobre él. El `MediaRecorder` sigue grabando el mismo `dest.stream` (destination estable), inmutado.

- **(d) Doble swap → segundo intento rechazado por cerrojo (T5).**
  Líneas: `if (isSwappingRef.current) return { ok: false, message: "Ya hay un cambio de micrófono en curso." };` evaluado ANTES de `isSwappingRef.current = true;`. Si se invoca `swapMicrophone` mientras uno anterior sigue `await navigator.mediaDevices.getUserMedia(...)`, el segundo entra, ve `isSwappingRef.current === true` (puesto por el primero antes de su `await`) y retorna inmediatamente sin tocar nada. El `finally { isSwappingRef.current = false; }` libera el cerrojo solo cuando el primero termina (éxito o error), nunca antes.

- **(e) Swap que resuelve tras `stopRecording` → tracks del perdedor detenidos, sin conexión (T5).**
  Líneas: tras el `await navigator.mediaDevices.getUserMedia(...)`, el chequeo `if (epoch !== swapEpochRef.current || !mediaRecorderRef.current || mediaRecorderRef.current.state !== "recording") { newMic.getTracks().forEach((t) => t.stop()); return { ok: false, message: "El cambio llegó tarde y fue descartado." }; }`. `stopRecording` (sin cambios, líneas 335-360) llama `mediaRecorderRef.current.stop()` que deja `mediaRecorderRef.current.state !== "recording"` — la condición se cumple, el `newMic` recién obtenido se detiene con `.stop()` en cada track SIN llegar a `createMediaStreamSource`/`.connect()`. Ninguna conexión al grafo de audio se crea para el perdedor.

- **(f) `onstatechange` a `suspended` en vuelo → `resume()` (cambio 1), citado en presencial Y virtual.**
  Presencial: línea `attachStateWatch(audioCtx);` dentro del bloque `if (audioCtx.state === "running") { ... }` (justo tras `micSourceRef.current = source;`). Virtual: línea `attachStateWatch(audioCtx);` en el bloque virtual, tras `destRef.current = dest;` y antes de `setMicStream(mixMicStream);`. `attachStateWatch` (única definición, nivel de módulo): `ctx.onstatechange = () => { if (ctx.state === "suspended") { console.warn(...); ctx.resume().catch(() => {}); } };` — el mismo listener se arma para el `AudioContext` de AMBOS modos.

### 4. `git diff` → SOLO `useAudioRecorder.ts`

```
$ git status --short
 M artifacts/acta-express/src/hooks/useAudioRecorder.ts
?? artifacts/acta-express/src/hooks/useMicDevices.ts
?? artifacts/acta-express/src/lib/micDevices.ts
```

Confirmado: el único archivo modificado (tracked, ` M`) es `useAudioRecorder.ts`; los otros dos siguen `??` (untracked, intactos de MT-M1). El diff literal íntegro está en la sección "Diff literal íntegro" arriba.

## Desviaciones

Una desviación de tipado, sin cambio de contrato ni de lógica:

- `let recordingStream: MediaStream;` → `let recordingStream!: MediaStream;` (aserción de asignación definitiva). TypeScript no puede probar estáticamente, con el flujo `try { if (running) { ...; routed = true; } else { ... } } catch {} ; if (!routed) { recordingStream = micRaw; }`, que `recordingStream` queda siempre asignada antes de `new MediaRecorder(recordingStream)` — aunque en runtime SIEMPRE lo está (o `routed=true` la asignó, o el fallback la asigna). Sin la aserción, `tsc` reportaba `error TS2454: Variable 'recordingStream' is used before being assigned.` Es exactamente el tipo de "detalle de tipado: lo más simple, declarado" que el protocolo de dudas delega al Ingeniero sin requerir DETENTE. No se tocó la lógica del contrato en absoluto.

## Dudas

Ninguna. El contrato se siguió al pie de la letra; no hubo ambigüedades que exigieran cambiar el diseño congelado (orden del swap, cerrojo, época, fallback).

## Commiteable

No se hizo commit (instrucción explícita: "no commiteas"). El diff queda en el working tree de `/home/pueblac/AndroidStudioProjects/ActaExpressWeb`, rama `linux`, listo para que el Director/Arquitecto decida el commit.
