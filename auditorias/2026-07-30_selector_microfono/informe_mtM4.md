# Informe MT-M4 — Micrófono preferido al INICIAR grabación (fallback declarado)

**Ciclo:** 2026-07-30_selector_microfono · F4 · **Rol:** Ingeniero (Sonnet, rotación asistida)
**Repo:** `/home/pueblac/AndroidStudioProjects/ActaExpressWeb`, rama `linux`.
**Spec:** `spec_mtM4.md`

## Precondición

Verificada antes de tocar nada:

```
 M artifacts/acta-express/src/hooks/useAudioRecorder.ts
 M artifacts/acta-express/src/pages/home.tsx
?? artifacts/acta-express/src/hooks/useMicDevices.ts
?? artifacts/acta-express/src/lib/micDevices.ts
```

Coincide (orden de líneas distinto al enunciado del turno pero mismo conjunto de rutas) con lo exigido por MT-M1+M2+M3 aplicadas. Continué.

## Qué se hizo

1. **`useAudioRecorder.ts`**
   - Import ampliado: `getPreferredMic` desde `../lib/micDevices` (línea 4).
   - `UseAudioRecorderReturn` gana `micFallbackNotice: string | null` (línea 22).
   - Estado nuevo `micFallbackNotice`/`setMicFallbackNotice` (línea 163), reseteado a `null` al inicio de `startRecording` (línea 212).
   - Helper interno `getMicWithPreference` (líneas 194-205), implementado LITERAL según el contrato del spec: intenta `exact` con el deviceId preferido; en catch setea el notice y **no** limpia la clave (comentario explícito "Q2: la clave NO se limpia", línea 201); reintenta sin deviceId.
   - Uso presencial (línea 220 en adelante): el único `getUserMedia` original fue reemplazado por `getMicWithPreference({echoCancellation:false, noiseSuppression:false, autoGainControl:true}, user?.uid ?? null)` (líneas 224-227), envuelto por el **mismo** `try/catch` externo preexistente (líneas 223, 228-232) que hace `setError(msg); return;` en caso de mic denegado — sin modificar su cuerpo.
   - `mixAudioStreams` (uso virtual) ampliado con parámetro opcional `preferredMicId: string | null = null` (línea 101) y estrategia exact→catch→default interna (líneas 118-133) dentro de su try/catch existente que sigue siendo la "última capa" ante mic no disponible del todo. Retorno ampliado con `micPreferredFailed: boolean` (línea 107, 141).
   - `startRecording` (branch virtual, línea 280) pasa `user ? getPreferredMic(user.uid) : null` como segundo argumento a `mixAudioStreams` y, si `micPreferredFailed` es true, setea el mismo texto de notice (líneas 284-286).

2. **`home.tsx`** (adición declarada por el spec, punto 4 "Corrección de alcance")
   - Se desestructura `micFallbackNotice` del hook (línea 73).
   - `useEffect` mínimo (líneas 108-113) que, al cambiar `micFallbackNotice` a no-null, dispara `toast({ title: "Micrófono", description: micFallbackNotice })`.

No se tocó nada más de `home.tsx` fuera de esta adición puntual (el resto de diferencias visibles en el `git diff` de `home.tsx` — `useMicDevices`, `swapMicrophone`, dropdown "Cambiar micrófono" — pertenecen a MT-M1/M2/M3, ya presentes antes de este turno).

## Evidencia DoD

### 1. `pnpm run typecheck` (salida literal)

```
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

### 2. `grep -n "getMicWithPreference\|micFallbackNotice\|getPreferredMic\|micPreferredFailed" ...` (salida literal)

```
artifacts/acta-express/src/hooks/useAudioRecorder.ts:4:import { setPreferredMic, getPreferredMic } from "../lib/micDevices";
artifacts/acta-express/src/hooks/useAudioRecorder.ts:22:  micFallbackNotice: string | null;
artifacts/acta-express/src/hooks/useAudioRecorder.ts:107:  micPreferredFailed: boolean;
artifacts/acta-express/src/hooks/useAudioRecorder.ts:119:  let micPreferredFailed = false;
artifacts/acta-express/src/hooks/useAudioRecorder.ts:128:        micPreferredFailed = true;
artifacts/acta-express/src/hooks/useAudioRecorder.ts:141:  return { mixedStream: dest.stream, audioCtx, micStream, micSource, dest, micPreferredFailed };
artifacts/acta-express/src/hooks/useAudioRecorder.ts:163:  const [micFallbackNotice, setMicFallbackNotice] = useState<string | null>(null);
artifacts/acta-express/src/hooks/useAudioRecorder.ts:194:  const getMicWithPreference = async (baseConstraints: MediaTrackConstraints, uid: string | null): Promise<MediaStream> => {
artifacts/acta-express/src/hooks/useAudioRecorder.ts:195:    const preferred = uid ? getPreferredMic(uid) : null;
artifacts/acta-express/src/hooks/useAudioRecorder.ts:224:        micRaw = await getMicWithPreference(
artifacts/acta-express/src/hooks/useAudioRecorder.ts:280:      const { mixedStream, audioCtx, micStream: mixMicStream, micSource, dest, micPreferredFailed } = await mixAudioStreams(
artifacts/acta-express/src/hooks/useAudioRecorder.ts:282:        user ? getPreferredMic(user.uid) : null
artifacts/acta-express/src/hooks/useAudioRecorder.ts:284:      if (micPreferredFailed) {
artifacts/acta-express/src/hooks/useAudioRecorder.ts:440:    micFallbackNotice,
artifacts/acta-express/src/pages/home.tsx:73:    micFallbackNotice
artifacts/acta-express/src/pages/home.tsx:112:    if (micFallbackNotice) {
artifacts/acta-express/src/pages/home.tsx:113:      toast({ title: "Micrófono", description: micFallbackNotice });
artifacts/acta-express/src/pages/home.tsx:115:  }, [micFallbackNotice]); // eslint-disable-line react-hooks/exhaustive-deps
```

### 3. A/B razonado

**(a) Sin preferido (uid null o `getPreferredMic` devuelve null) → un solo `getUserMedia` con las constraints de siempre.**
Presencial: `getMicWithPreference` línea 195 evalúa `preferred = null`; el `if (preferred)` (línea 196) no entra; cae directo a la línea 204 `return navigator.mediaDevices.getUserMedia({ audio: baseConstraints })` — exactamente el único `getUserMedia` con `{echoCancellation:false, noiseSuppression:false, autoGainControl:true}` que existía antes de esta MT. Cero llamadas extra, cero cambio de comportamiento.
Virtual: `mixAudioStreams` línea 120 con `preferredMicId` null cae al `else` (línea 125) → un solo `getUserMedia({ audio: baseConstraints })` con `{echoCancellation:true, noiseSuppression:true}`, igual que antes.

**(b) Preferido válido → `exact` y SIN notice.**
Presencial: línea 198, `try { return await navigator.mediaDevices.getUserMedia({ audio: { ...baseConstraints, deviceId: { exact: preferred } } }); }` resuelve sin lanzar → `return` inmediato dentro del `try`; el `catch` (línea 199, único lugar donde se llama `setMicFallbackNotice`) nunca se ejecuta. El estado queda en `null` (reseteado en línea 212 al inicio de `startRecording`).
Virtual: línea 121-123, el `getUserMedia` con `exact` resuelve sin lanzar → `micPreferredFailed` permanece `false` (inicializado en línea 119) → en `startRecording` (línea 284) el `if (micPreferredFailed)` no entra → sin notice.

**(c) Preferido inválido (otra máquina/desenchufado) → catch → notice seteado → reintento default → LA GRABACIÓN ARRANCA + toast; la clave persiste.**
Presencial: el `getUserMedia` con `exact` en línea 198 lanza (`OverconstrainedError`/`NotFoundError`) → entra al `catch` (línea 199) → `setMicFallbackNotice(...)` (línea 200) → el `catch` NO relanza ni retorna un stream, así que la ejecución cae fuera del `if` hasta la línea 204, `return navigator.mediaDevices.getUserMedia({ audio: baseConstraints })` (reintento default) → ese stream se resuelve y `startRecording` continúa su flujo normal (enrutamiento AudioContext, `mediaRecorder.start(1000)`, `setIsRecording(true)`) — la grabación arranca. El `home.tsx` `useEffect` (líneas 108-113) detecta `micFallbackNotice` no-null y dispara el `toast`. La clave persiste: `micDevices.ts` no tiene ninguna llamada a `removeItem` — confirmado por `grep -n removeItem` sin resultados; `getPreferredMic`/`setPreferredMic` (líneas 8-14 de `micDevices.ts`) son las únicas funciones que tocan esa entrada de `localStorage`, y ninguna de las dos se invoca en el camino de fallback (solo se invoca `getPreferredMic` para leer, nunca se borra).
Virtual: el `getUserMedia` con `exact` en `mixAudioStreams` (línea 121) lanza → `catch` (línea 127) → `micPreferredFailed = true` (línea 128) + comentario Q2 (línea 129) → reintento default (línea 130) sin deviceId → el mic queda conectado igual (línea 134-135 conecta `micSource` a `dest`) → `mixAudioStreams` retorna `micPreferredFailed: true` → en `startRecording` (línea 284-286) se setea el mismo notice → toast se dispara igual vía el `useEffect` de `home.tsx`. La clave tampoco se toca en este camino (mismo argumento: sin `removeItem` en el módulo).

**(d) Mic denegado del todo → el catch externo original sigue funcionando (setError, no arranca).**
Presencial: si tanto el intento `exact` (línea 198) como el reintento default (línea 204, dentro de `getMicWithPreference`) fallan (p. ej. permiso denegado por el usuario/OS), la segunda llamada (línea 204) lanza y, al no estar envuelta en try/catch DENTRO del helper, esa excepción se propaga hacia arriba, hasta el `try/catch` **externo preexistente** en `startRecording` (líneas 223-232): `catch (err: unknown) { const msg = ...; setError(msg); return; }` — este bloque no fue modificado, solo su contenido interno (la llamada que envuelve) cambió de `navigator.mediaDevices.getUserMedia(...)` directo a `getMicWithPreference(...)`. El comportamiento observable ante mic totalmente denegado es idéntico al preexistente: `setError` se llama y `startRecording` retorna sin arrancar.
Virtual: si el reintento default dentro de `mixAudioStreams` (línea 130 o línea 125 según rama) también falla, la excepción cae al `catch` externo de la función (líneas 132-134, comentario "Microphone unavailable — that's OK, display audio alone is still useful") — esa es la "última capa" preexistente que el spec pidió conservar; el comportamiento es el mismo que antes: la grabación de solo audio de sistema continúa sin mic.

### 4. `git diff` literal íntegro

Ver diff completo ejecutado con `git diff -- artifacts/acta-express/src/hooks/useAudioRecorder.ts artifacts/acta-express/src/pages/home.tsx`. Nota: dado que la precondición partía de MT-M1+M2+M3 ya aplicadas y no commiteadas, este diff incluye TODO el trabajo acumulado de esas tandas más el de esta MT-M4 (working tree vs `HEAD`); los bloques de swap de micrófono en caliente, `useMicDevices`, y el dropdown "Cambiar micrófono" en `home.tsx` NO fueron tocados por MT-M4 — pertenecen a M1-M3.

```diff
diff --git a/artifacts/acta-express/src/hooks/useAudioRecorder.ts b/artifacts/acta-express/src/hooks/useAudioRecorder.ts
index 571a0b4..b4c1e40 100644
--- a/artifacts/acta-express/src/hooks/useAudioRecorder.ts
+++ b/artifacts/acta-express/src/hooks/useAudioRecorder.ts
@@ -1,6 +1,7 @@
 import { useState, useRef, useCallback } from "react";
 import { useAuth } from "@/context/AuthContext";
 import { createSession, appendChunk, purgeStaleKeepNewest, isVaultAvailable } from "../lib/recordingVault";
+import { setPreferredMic, getPreferredMic } from "../lib/micDevices";
 
 type CaptureMode = "system+mic" | "system" | "microphone" | null;
 
@@ -17,6 +18,8 @@ interface UseAudioRecorderReturn {
   captureMode: CaptureMode;
   micStream: MediaStream | null;
   vaultSessionId: string | null;
+  swapMicrophone: (deviceId: string) => Promise<{ ok: boolean; message?: string }>;
+  micFallbackNotice: string | null;
 }
 
 export function blobToBase64(blob: Blob): Promise<string> {
@@ -95,10 +98,13 @@ async function getDisplayAudioStream(): Promise<{ stream: MediaStream; hadVideo:
  * Returns { mixedStream, audioCtx, displayStream, micStream } so all can be
  * stopped properly later.
  */
-async function mixAudioStreams(displayStream: MediaStream): Promise<{
+async function mixAudioStreams(displayStream: MediaStream, preferredMicId: string | null = null): Promise<{
   mixedStream: MediaStream;
   audioCtx: AudioContext;
   micStream: MediaStream | null;
+  micSource: MediaStreamAudioSourceNode | null;
+  dest: MediaStreamAudioDestinationNode;
+  micPreferredFailed: boolean;
 }> {
   const audioCtx = new AudioContext();
   const dest = audioCtx.createMediaStreamDestination();
@@ -109,19 +115,41 @@ async function mixAudioStreams(displayStream: MediaStream): Promise<{
 
   // Try to add microphone
   let micStream: MediaStream | null = null;
+  let micSource: MediaStreamAudioSourceNode | null = null;
+  let micPreferredFailed = false;
+  const baseConstraints: MediaTrackConstraints = { echoCancellation: true, noiseSuppression: true };
   try {
-    micStream = await navigator.mediaDevices.getUserMedia({
-      audio: { echoCancellation: true, noiseSuppression: true },
-    });
-    const micSource = audioCtx.createMediaStreamSource(micStream);
+    if (preferredMicId) {
+      try {
+        micStream = await navigator.mediaDevices.getUserMedia({
+          audio: { ...baseConstraints, deviceId: { exact: preferredMicId } },
+        });
+      } catch {
+        micPreferredFailed = true;
+        // Q2: la clave NO se limpia; solo se declara el fallo y se reintenta con el default.
+        micStream = await navigator.mediaDevices.getUserMedia({ audio: baseConstraints });
+      }
+    } else {
+      micStream = await navigator.mediaDevices.getUserMedia({ audio: baseConstraints });
+    }
+    micSource = audioCtx.createMediaStreamSource(micStream);
     micSource.connect(dest);
   } catch {
     // Microphone unavailable — that's OK, display audio alone is still useful
   }
 
-  return { mixedStream: dest.stream, audioCtx, micStream };
+  return { mixedStream: dest.stream, audioCtx, micStream, micSource, dest, micPreferredFailed };
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
@@ -132,6 +160,7 @@ export function useAudioRecorder(): UseAudioRecorderReturn {
   const [captureMode, setCaptureMode] = useState<CaptureMode>(null);
   const [micStream, setMicStream] = useState<MediaStream | null>(null);
   const [vaultSessionId, setVaultSessionId] = useState<string | null>(null);
+  const [micFallbackNotice, setMicFallbackNotice] = useState<string | null>(null);
 
   const mediaRecorderRef = useRef<MediaRecorder | null>(null);
   const displayStreamRef = useRef<MediaStream | null>(null);
@@ -143,6 +172,12 @@ export function useAudioRecorder(): UseAudioRecorderReturn {
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
@@ -151,33 +186,83 @@ export function useAudioRecorder(): UseAudioRecorderReturn {
     displayStreamRef.current = null;
     micStreamRef.current = null;
     audioCtxRef.current = null;
+    micSourceRef.current = null;
+    destRef.current = null;
     setMicStream(null);
   }, []);
 
+  const getMicWithPreference = async (baseConstraints: MediaTrackConstraints, uid: string | null): Promise<MediaStream> => {
+    const preferred = uid ? getPreferredMic(uid) : null;
+    if (preferred) {
+      try {
+        return await navigator.mediaDevices.getUserMedia({ audio: { ...baseConstraints, deviceId: { exact: preferred } } });
+      } catch {
+        setMicFallbackNotice("Tu micrófono preferido no está disponible; se usará el predeterminado.");
+        // Q2: la clave NO se limpia.
+      }
+    }
+    return navigator.mediaDevices.getUserMedia({ audio: baseConstraints });
+  };
+
   const startRecording = useCallback(async (modo: ModoReunion) => {
     setError(null);
     setAudioBlob(null);
     setAudioBase64(null);
     setDuration(0);
+    setMicFallbackNotice(null);
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
-          audio: { echoCancellation: false, noiseSuppression: false, autoGainControl: true },
-        });
-        micStreamRef.current = recordingStream;
-        setMicStream(recordingStream);
-        mode = "microphone";
+        micRaw = await getMicWithPreference(
+          { echoCancellation: false, noiseSuppression: false, autoGainControl: true },
+          user?.uid ?? null
+        );
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
@@ -192,9 +277,18 @@ export function useAudioRecorder(): UseAudioRecorderReturn {
       displayStreamRef.current = displayResult.stream;
 
       // Mix with microphone
-      const { mixedStream, audioCtx, micStream: mixMicStream } = await mixAudioStreams(displayResult.stream);
+      const { mixedStream, audioCtx, micStream: mixMicStream, micSource, dest, micPreferredFailed } = await mixAudioStreams(
+        displayResult.stream,
+        user ? getPreferredMic(user.uid) : null
+      );
+      if (micPreferredFailed) {
+        setMicFallbackNotice("Tu micrófono preferido no está disponible; se usará el predeterminado.");
+      }
       audioCtxRef.current = audioCtx;
       micStreamRef.current = mixMicStream;
+      micSourceRef.current = micSource;
+      destRef.current = dest;
+      attachStateWatch(audioCtx);
       setMicStream(mixMicStream);
       recordingStream = mixedStream;
       mode = mixMicStream ? "system+mic" : "system";
@@ -299,6 +393,38 @@ export function useAudioRecorder(): UseAudioRecorderReturn {
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
@@ -310,5 +436,7 @@ export function useAudioRecorder(): UseAudioRecorderReturn {
     captureMode,
     micStream,
     vaultSessionId,
+    swapMicrophone,
+    micFallbackNotice,
   };
 }
diff --git a/artifacts/acta-express/src/pages/home.tsx b/artifacts/acta-express/src/pages/home.tsx
index 4a5ee63..c486f3e 100644
--- a/artifacts/acta-express/src/pages/home.tsx
+++ b/artifacts/acta-express/src/pages/home.tsx
@@ -2,6 +2,7 @@ import { useEffect, useRef, useState } from "react";
 import { useAuth } from "@/context/AuthContext";
 import { useAudioRecorder, type ModoReunion, blobToBase64 } from "@/hooks/useAudioRecorder";
 import { useMicLevel } from "@/hooks/useMicLevel";
+import { useMicDevices } from "@/hooks/useMicDevices";
 import {
   purgeStaleKeepNewest,
   getSession,
@@ -25,6 +26,12 @@ import { Switch } from "@/components/ui/switch";
 import { Label } from "@/components/ui/label";
 import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
 import { useToast } from "@/hooks/use-toast";
+import {
+  DropdownMenu,
+  DropdownMenuContent,
+  DropdownMenuItem,
+  DropdownMenuTrigger,
+} from "@/components/ui/dropdown-menu";
 import {
   AlertDialog,
   AlertDialogAction,
@@ -61,7 +68,9 @@ export default function Home() {
     error,
     captureMode,
     micStream,
-    vaultSessionId
+    vaultSessionId,
+    swapMicrophone,
+    micFallbackNotice
   } = useAudioRecorder();
 
   const { data: actas, isLoading: loadingActas } = useListActas();
@@ -96,6 +105,15 @@ export default function Home() {
   // MT-C3: solo cablea el hook para producir micSilent; el banner es MT-C4.
   const { micSilent } = useMicLevel(micStream, isRecording, modoReunion);
 
+  const { microphones } = useMicDevices(isRecording && micSilent);
+
+  // MT-M4: aviso no bloqueante cuando el micrófono preferido no está disponible (fallback declarado).
+  useEffect(() => {
+    if (micFallbackNotice) {
+      toast({ title: "Micrófono", description: micFallbackNotice });
+    }
+  }, [micFallbackNotice]); // eslint-disable-line react-hooks/exhaustive-deps
+
   const [orphanSession, setOrphanSession] = useState<VaultSessionMeta | null>(null);
 
   const [deleteDialogActaId, setDeleteDialogActaId] = useState<string | null>(null);
@@ -212,6 +230,15 @@ export default function Home() {
     setDeleteDialogActaId(null);
   };
 
+  const handleSwapMic = async (deviceId: string, label: string) => {
+    const res = await swapMicrophone(deviceId);
+    if (res.ok) {
+      toast({ title: "Micrófono cambiado", description: `Ahora se usa "${label}". Verificando señal…` });
+    } else {
+      toast({ variant: "destructive", title: "No se pudo cambiar el micrófono", description: res.message });
+    }
+  };
+
   const handleDescartarOrphan = () => {
     if (!orphanSession) return;
     deleteSession(orphanSession.sessionId).catch(() => {});
@@ -347,14 +374,33 @@ export default function Home() {
                 data-testid="banner-mic-muerto"
                 className={
                   modoReunion === "presencial"
-                    ? "flex items-center justify-center gap-2 text-destructive text-sm mt-2 bg-destructive/10 px-4 py-2 rounded-md"
-                    : "flex items-center justify-center gap-2 text-amber-500 text-sm mt-2 bg-amber-500/10 px-4 py-2 rounded-md"
+                    ? "flex items-center justify-center gap-2 flex-wrap text-destructive text-sm mt-2 bg-destructive/10 px-4 py-2 rounded-md"
+                    : "flex items-center justify-center gap-2 flex-wrap text-amber-500 text-sm mt-2 bg-amber-500/10 px-4 py-2 rounded-md"
                 }
               >
                 <AlertCircle className="w-4 h-4" />
                 {modoReunion === "presencial"
                   ? "⚠️ No se detecta señal de tu micrófono — revisa que no esté silenciado en el sistema."
                   : "Tu micrófono no aporta señal. Si solo escuchas la reunión está bien; si querías hablar, revisa que no esté silenciado."}
+                <DropdownMenu>
+                  <DropdownMenuTrigger asChild>
+                    <Button size="sm" variant="outline" data-testid="cta-cambiar-mic" className="ml-2 shrink-0">
+                      <Mic className="mr-1 h-3 w-3" />
+                      Cambiar micrófono
+                    </Button>
+                  </DropdownMenuTrigger>
+                  <DropdownMenuContent align="center" className="w-64">
+                    {microphones.length === 0 ? (
+                      <DropdownMenuItem disabled>No se encontraron micrófonos</DropdownMenuItem>
+                    ) : (
+                      microphones.map((m) => (
+                        <DropdownMenuItem key={m.deviceId} data-testid={`mic-option-${m.deviceId}`} onClick={() => handleSwapMic(m.deviceId, m.label)}>
+                          {m.label}
+                        </DropdownMenuItem>
+                      ))
+                    )}
+                  </DropdownMenuContent>
+                </DropdownMenu>
               </div>
             )}
```

## Desviaciones

Ninguna. Se implementó el contrato al pie de la letra:
- Helper `getMicWithPreference` literalmente igual al pseudocódigo del spec (con el comentario Q2 preservado).
- Firma y estrategia de `mixAudioStreams` ampliadas exactamente como se describió (parámetro `preferredMicId`, retorno con `micPreferredFailed`).
- El `useEffect` del toast en `home.tsx` es la única adición fuera de `useAudioRecorder.ts`, tal como autoriza el punto 4 del contrato ("Corrección de alcance").
- El catch externo preexistente de mic denegado (presencial) quedó intacto: solo cambió la expresión que envuelve (de `getUserMedia` directo a `getMicWithPreference`), no su cuerpo ni su comportamiento.

## Dudas

Ninguna que exigiera cambiar el contrato. No fue necesario detenerse.

## ¿Commiteable?

No se hizo commit (fuera de mandato explícito de esta MT). El working tree queda con los 4 archivos modificados/nuevos de M1+M2+M3+M4, `pnpm run typecheck` en verde (exit 0). Listo para que el Director/Arquitecto decida el commit.
