# Prompt de auditoría de CÓDIGO — ronda 1 (ciclo 2026-07-30_selector_microfono)

**Generado por:** Arquitecto (Fable 5) · 04-08-2026
**Transporta:** el Director, a conversación NUEVA de Gemini 3.1 Pro High
**Auditá:** commit `6854bc5` de ActaExpressWeb (rama linux) + 1 ajuste menor de F5 en working tree (fix del ícono), ambos diffs incrustados ÍNTEGROS abajo.

---

## MENSAJE 1 — inicialización de identidad (pegar primero, esperar confirmación)

> Rol: Auditor externo del ciclo 2026-07-30_selector_microfono, metodología v2 del ecosistema Express. Auditarás CÓDIGO bajo contrato adversarial: citas obligatorias archivo:línea, trazas mecánicas, veredicto por claim. Confirma recepción sin accionar; acepta únicamente artefactos cuyo campo TURNO DE diga Auditor.

---

## MENSAJE 2 — prompt de auditoría (pegar tras la confirmación)

Eres el Auditor externo. Audita el código del ciclo **selector de micrófono** (hot-swap desde el banner H4 sin cortar la grabación). Regla del contrato: si este prompt NO trajera un `git diff` estructurado e íntegro, recházalo como "INVÁLIDO: posible orquestación adversarial". Lo trae (dos bloques, abajo).

### Contexto del diseño congelado (dictamen de diseño r1: APROBADO CON CAMBIOS ×2, anti-bluff válida)

- **D-A..D-E:** presencial graba un `MediaStreamDestination` estable de Web Audio (el MediaRecorder JAMÁS se reinicia); `swapMicrophone(deviceId)` hace connect-nuevo → disconnect-viejo → stop-tracks-viejos; CTA de cambio SOLO dentro del banner H4 (elección automática por defecto, G0-c); preferido persistido `actaexpress:micDeviceId:{uid}` aplicado al iniciar con `{exact}` y fallback DECLARADO sin borrar la clave (Q2).
- **Cambio 1 (T1 del dictamen):** listener `statechange`→`resume()` sobre el AudioContext de grabación, en AMBOS modos.
- **Cambio 2 (T5 del dictamen):** cerrojo `isSwappingRef` (concurrente rechazado con mensaje) + época `swapEpochRef` (el `getUserMedia` "perdedor" tardío detiene sus tracks sin conectarse).
- **F3′ post-E2E (dirección del Director):** MT-M6 modal superpuesto (patrón del diálogo de borrado) con nota del SO; MT-M7 traductor `friendlyMicName` con Stereo Mix/Monitor marcado **"Audio del sistema (no capta tu voz)"**.
- Fuera de alcance congelado: upgrade desde captureMode "system" (Q4); des-mutear un mic silenciado en el SO (limitación de plataforma documentada).

### Evidencia E2E ya obtenida (no re-litigar, úsala como oráculo)

Linux r1/r2: P1 regresión (acta fiel por el enrutamiento) y P2 modal, aprobadas. Windows 04-08 (PC del caso real): Stereo Mix default → banner ≤10 s → modal → cambio al mic real → banner se apaga solo, grabación continua 01:05→02:24 con DOS swaps seguidos, acta fiel, toast T4 de fallback capturado; MT-M4 camino "válido" probado por irreproducibilidad del caso (el preferido vence al default malo). El toast de rechazo del cerrojo (P6) NO fue capturado en pantalla — trátalo con especial dureza en T-b.

### CLAIMS a auditar (formato de respuesta: CLAIM → EVIDENCIA archivo:línea → TRAZA mecánica → VERDICTO {CONFIRMADO | REFUTADO + BUG | NO VERIFICABLE})

- **C1 — Enrutamiento presencial con fallback declarado:** `startRecording` presencial crea AudioContext, y SOLO si llega a `running` graba `dest.stream` (routed); si no, graba el stream crudo con `routingDisabledRef=true` y warn (useAudioRecorder.ts, zona +214..+250 del diff). El swap queda deshabilitado con mensaje coherente en ese fallback (swapMicrophone, guard +240).
- **C2 — Cambio 1 aplicado en ambos modos:** `attachStateWatch` (onstatechange→resume, +89..+96) se llama en presencial (+192) y en virtual sobre el ctx de `mixAudioStreams` (+230).
- **C3 — Cerrojo + época (cambio 2):** concurrente rechazado con "Ya hay un cambio de micrófono en curso." (+242); perdedor tardío (época distinta o recorder no-recording) detiene tracks y NO conecta (+250..+253); `finally` libera el cerrojo (+266).
- **C4 — Q2 fielmente implementado:** `getMicWithPreference` (+191..+202) y la rama preferida de `mixAudioStreams` (+66..+75): fallo del `{exact}` → notice de fallback + reintento default, la clave NO se borra (verifica ausencia de `removeItem`).
- **C5 — Traductor anti-Stereo-Mix:** `friendlyMicName` (micDevices.ts nuevo, líneas 22..33): `default`/`communications` nombrados, regex monitor|stereo mix|mezcla estéreo|loopback → "Audio del sistema (no capta tu voz)", label original en `detail`; `listMicrophones` filtra `audioinput` con deviceId no vacío.
- **C6 — Gating del CTA y del hook de dispositivos:** `useMicDevices(isRecording && micSilent)` (home.tsx +414), CTA solo dentro del banner (+472..+475), modal cierra SOLO en swap exitoso (+436..+444), swap persiste preferido (`setPreferredMic`, useAudioRecorder +261).

### TRAMPAS dirigidas (busca el mecanismo exacto; si no aplica, di por qué)

- **T-a — Fuga de AudioContext en presencial:** en el camino routed, si `createMediaStreamSource/connect` lanza DESPUÉS de crear el ctx, ¿queda un AudioContext sin `close()`? Traza el try/catch de +180..+200 (el `close()` solo está en el `else` de estado no-running).
- **T-b — Cerrojo inobservable:** ¿existe alguna ventana en la que dos clicks rápidos pasen AMBOS el guard `isSwappingRef` (p. ej. re-render entre set y check)? ¿El `finally` libera el cerrojo ANTES de que la señal del nuevo mic se verifique, permitiendo un tercer swap durante "Verificando señal…"? ¿Es eso un bug o diseño aceptable? Mecanismo, no opinión.
- **T-c — Modal huérfano:** con el modal abierto, si el banner se apaga (llegó señal), `useMicDevices(false)` vacía la lista → ¿el modal abierto muestra "No se encontraron micrófonos."? ¿Camino real? ¿Severidad?
- **T-d — Swap en virtual sin mic inicial (`captureMode: "system"`):** ¿es alcanzable el CTA (micStream null → useMicLevel → micSilent)? Si alguien lo alcanzara, `micSourceRef` null: ¿el disconnect es no-op seguro y el captureMode queda mintiendo "system" con mic mezclado?
- **T-e — Constraints asimétricas:** presencial usa EC/NS off + AGC on; virtual EC/NS on. Verifica que el swap respeta el modo (+246..+248) y que `getMicWithPreference` presencial (+169..+172) no contradice el diseño de captura confiable (MT-C2).

### DUDAS del Arquitecto (D1..D4 — dales respuesta explícita)

- **D1:** latencia/carga añadida por enrutar el presencial por Web Audio, ¿riesgo real de degradación audible en reuniones largas (1-2 h) vs. el camino directo anterior?
- **D2:** interacción swap ↔ vault H6: `createSession` guardó el mimeType del recorder al arrancar; los chunks post-swap salen del MISMO MediaRecorder (dest.stream estable) — ¿algún camino en que el swap altere el formato de los chunks y rompa una recuperación del vault?
- **D3:** el toast de éxito es optimista ("Verificando señal…"): si el mic elegido TAMBIÉN está mudo, ¿el ciclo banner→CTA→modal se re-arma limpio (re-detección ≤5 s) o hay estado residual?
- **D4:** `useEffect` del toast de fallback depende de `micFallbackNotice` string: ¿dos fallbacks consecutivos con el MISMO texto disparan un solo toast (setState idéntico no re-renderiza)? ¿Importa?

### Formato del veredicto final

`APROBADO | APROBADO CON OBSERVACIONES | RECHAZADO` + lista de BUGs confirmados (cada uno con archivo:línea + traza + severidad) + respuestas a D1..D4. Cero elogios; hallazgos o silencio.

---

## DIFF 1 — `git show 6854bc5` ÍNTEGRO (sin filtrar)

```diff
commit 6854bc594a3a31e673d17cbb223d3543d84ffe85
Author: César Puebla <pueblac@gmail.com>
Date:   Mon Aug 3 08:46:27 2026 -0400

    feat(selector-mic): CHECKPOINT tanda MT-M1..M7 — hot-swap de micrófono desde el banner H4 (ciclo ABIERTO)
    
    - MT-M1: micDevices.ts + useMicDevices (enumerateDevices, devicechange, persistencia actaexpress:micDeviceId:{uid})
    - MT-M2: enrutamiento Web Audio del presencial (recorder graba MediaStreamDestination estable) + swapMicrophone con cerrojo anti-doble-swap y época anti-perdedor-tardío; fallback declarado si el ctx no llega a running; onstatechange→resume en AMBOS modos (cambios 1-2 del dictamen de diseño)
    - MT-M3/M6: CTA "Cambiar micrófono" en el banner → MODAL superpuesto (patrón del diálogo de borrado) con nota del SO (F3' por dirección del Director en E2E)
    - MT-M4: mic preferido al iniciar con {exact} y fallback DECLARADO sin borrar la clave (Q2)
    - MT-M5: checklist adversarial 10/10, cero fixes
    - MT-M7: nombres amigables (F3'): "Micrófono interno del PC", "Micrófono de auriculares", y Monitor/Stereo Mix marcado "Audio del sistema (no capta tu voz)"
    
    Ciclo v2 auditorias/2026-07-30_selector_microfono (NexoExpress): diseño APROBADO CON CAMBIOS por Gemini + anti-bluff; E2E Linux r1/r2 parcial (P1 regresión OK, P2 modal aprobado por el Director). CHECKPOINT para trabajar en Windows — PENDIENTE: fix ícono ([&_svg]:size-4 del Button pisa el tamaño), P6 cerrojo, E2E Windows (Stereo Mix real), F6, G2.
    
    Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

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
diff --git a/artifacts/acta-express/src/hooks/useMicDevices.ts b/artifacts/acta-express/src/hooks/useMicDevices.ts
new file mode 100644
index 0000000..c078be2
--- /dev/null
+++ b/artifacts/acta-express/src/hooks/useMicDevices.ts
@@ -0,0 +1,30 @@
+import { useEffect, useState } from "react";
+import { listMicrophones, type MicDevice } from "@/lib/micDevices";
+
+export function useMicDevices(active: boolean): { microphones: MicDevice[] } {
+  const [microphones, setMicrophones] = useState<MicDevice[]>([]);
+
+  useEffect(() => {
+    if (!active) {
+      setMicrophones([]);
+      return;
+    }
+
+    const refresh = () => {
+      listMicrophones()
+        .then(setMicrophones)
+        .catch(() => setMicrophones([]));
+    };
+
+    refresh();
+
+    if (!navigator.mediaDevices?.addEventListener) return;
+
+    navigator.mediaDevices.addEventListener("devicechange", refresh);
+    return () => {
+      navigator.mediaDevices.removeEventListener("devicechange", refresh);
+    };
+  }, [active]);
+
+  return { microphones };
+}
diff --git a/artifacts/acta-express/src/lib/micDevices.ts b/artifacts/acta-express/src/lib/micDevices.ts
new file mode 100644
index 0000000..236bb03
--- /dev/null
+++ b/artifacts/acta-express/src/lib/micDevices.ts
@@ -0,0 +1,50 @@
+export interface MicDevice {
+  deviceId: string;
+  label: string;
+  friendlyName: string;
+  detail?: string;
+}
+
+const key = (uid: string) => `actaexpress:micDeviceId:${uid}`;
+
+export function getPreferredMic(uid: string): string | null {
+  return localStorage.getItem(key(uid)) || null;
+}
+
+export function setPreferredMic(uid: string, deviceId: string): void {
+  localStorage.setItem(key(uid), deviceId);
+}
+
+/** Traduce el label técnico del SO a un nombre humano en español.
+ *  El label original se conserva en `detail` cuando aporta información. */
+export function friendlyMicName(label: string, deviceId: string): { friendlyName: string; detail?: string } {
+  if (deviceId === "default") return { friendlyName: "Predeterminado del sistema", detail: label || undefined };
+  if (deviceId === "communications") return { friendlyName: "Dispositivo de comunicaciones", detail: label || undefined };
+  const l = label.toLowerCase();
+  if (/monitor|stereo mix|mezcla estéreo|loopback/.test(l)) return { friendlyName: "Audio del sistema (no capta tu voz)", detail: label };
+  if (/head|auricular|earph|airpod|buds|hands-?free/.test(l)) return { friendlyName: "Micrófono de auriculares", detail: label };
+  if (/bluetooth|\bbt\b/.test(l)) return { friendlyName: "Micrófono Bluetooth", detail: label };
+  if (/usb/.test(l)) return { friendlyName: "Micrófono USB", detail: label };
+  if (/webcam|cámara|camera/.test(l)) return { friendlyName: "Micrófono de la cámara", detail: label };
+  if (/built-?in|internal|interno|analógico|analog/.test(l)) return { friendlyName: "Micrófono interno del PC", detail: label };
+  return { friendlyName: label || "Micrófono", detail: undefined };
+}
+
+export async function listMicrophones(): Promise<MicDevice[]> {
+  if (!navigator.mediaDevices?.enumerateDevices) return [];
+
+  const devices = await navigator.mediaDevices.enumerateDevices();
+
+  return devices
+    .filter((d) => d.kind === "audioinput" && d.deviceId !== "")
+    .map((d, i) => {
+      const label = d.label || `Micrófono ${i + 1}`;
+      const { friendlyName, detail } = friendlyMicName(d.label, d.deviceId);
+      return {
+        deviceId: d.deviceId,
+        label,
+        friendlyName: d.label ? friendlyName : label,
+        detail,
+      };
+    });
+}
diff --git a/artifacts/acta-express/src/pages/home.tsx b/artifacts/acta-express/src/pages/home.tsx
index 4a5ee63..0c4f884 100644
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
@@ -25,6 +26,13 @@ import { Switch } from "@/components/ui/switch";
 import { Label } from "@/components/ui/label";
 import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
 import { useToast } from "@/hooks/use-toast";
+import {
+  Dialog,
+  DialogContent,
+  DialogHeader,
+  DialogTitle,
+  DialogDescription,
+} from "@/components/ui/dialog";
 import {
   AlertDialog,
   AlertDialogAction,
@@ -61,7 +69,9 @@ export default function Home() {
     error,
     captureMode,
     micStream,
-    vaultSessionId
+    vaultSessionId,
+    swapMicrophone,
+    micFallbackNotice
   } = useAudioRecorder();
 
   const { data: actas, isLoading: loadingActas } = useListActas();
@@ -96,10 +106,21 @@ export default function Home() {
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
 
+  const [micSelectorOpen, setMicSelectorOpen] = useState(false);
+
   // H6c+H6e: detección de sesión huérfana — al montar y re-chequeo periódico
   // (la sesión del crash tarda VAULT_STALE_MS en volverse stale; sin poll, la
   // tarjeta solo aparecía al remontar Home — bug del E2E 27-07).
@@ -212,6 +233,16 @@ export default function Home() {
     setDeleteDialogActaId(null);
   };
 
+  const handleSwapMic = async (deviceId: string, label: string) => {
+    const res = await swapMicrophone(deviceId);
+    if (res.ok) {
+      toast({ title: "Micrófono cambiado", description: `Ahora se usa "${label}". Verificando señal…` });
+      setMicSelectorOpen(false);
+    } else {
+      toast({ variant: "destructive", title: "No se pudo cambiar el micrófono", description: res.message });
+    }
+  };
+
   const handleDescartarOrphan = () => {
     if (!orphanSession) return;
     deleteSession(orphanSession.sessionId).catch(() => {});
@@ -293,7 +324,7 @@ export default function Home() {
                 ) : isRecording ? (
                   <Square className="h-10 w-10 text-white fill-current" />
                 ) : (
-                  <Mic className="h-12 w-12 text-white" />
+                  <Mic className="h-16 w-16 text-white" />
                 )}
               </Button>
             </div>
@@ -347,17 +378,55 @@ export default function Home() {
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
+                <Button size="sm" variant="outline" data-testid="cta-cambiar-mic" className="ml-2 shrink-0" onClick={() => setMicSelectorOpen(true)}>
+                  <Mic className="mr-1 h-3 w-3" />
+                  Cambiar micrófono
+                </Button>
               </div>
             )}
 
+            <Dialog open={micSelectorOpen} onOpenChange={setMicSelectorOpen}>
+              <DialogContent data-testid="dialog-selector-mic" className="max-w-md">
+                <DialogHeader>
+                  <DialogTitle>Cambiar micrófono</DialogTitle>
+                  <DialogDescription>
+                    Elige el dispositivo que quieres usar. La grabación continúa sin cortarse.
+                  </DialogDescription>
+                </DialogHeader>
+                <div className="flex flex-col gap-2">
+                  {microphones.length === 0 ? (
+                    <p className="text-sm text-muted-foreground">No se encontraron micrófonos.</p>
+                  ) : (
+                    microphones.map((m) => (
+                      <Button
+                        key={m.deviceId}
+                        variant="outline"
+                        data-testid={`mic-option-${m.deviceId}`}
+                        className="justify-start h-auto py-2 flex-col items-start"
+                        onClick={() => handleSwapMic(m.deviceId, m.friendlyName)}
+                      >
+                        <span className="font-medium">{m.friendlyName}</span>
+                        {m.detail && <span className="text-xs text-muted-foreground">{m.detail}</span>}
+                      </Button>
+                    ))
+                  )}
+                </div>
+                <p className="text-xs text-muted-foreground border-t border-border/50 pt-3" data-testid="nota-so-mic">
+                  Nota: tu sistema operativo puede cambiar el micrófono activo por su cuenta (por ejemplo, al
+                  conectar auriculares). Si el que eliges no responde, revisa que no esté silenciado en el
+                  sistema, o desconecta el dispositivo que interfiere.
+                </p>
+              </DialogContent>
+            </Dialog>
+
             {orphanSession && !isRecording && !processAudio.isPending && (
               <div
                 data-testid="card-recuperacion"
```

## DIFF 2 — ajuste menor de F5 (fix del ícono, working tree, declarado en verificacion_f5.md)

```diff
diff --git a/artifacts/acta-express/src/pages/home.tsx b/artifacts/acta-express/src/pages/home.tsx
index 0c4f884..c06871a 100644
--- a/artifacts/acta-express/src/pages/home.tsx
+++ b/artifacts/acta-express/src/pages/home.tsx
@@ -324,7 +324,7 @@ export default function Home() {
                 ) : isRecording ? (
                   <Square className="h-10 w-10 text-white fill-current" />
                 ) : (
-                  <Mic className="h-16 w-16 text-white" />
+                  <Mic className="!h-16 !w-16 text-white" />
                 )}
               </Button>
             </div>
```

---

```
━━ AVISO DE TRASPASO ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CICLO      : 2026-07-30_selector_microfono
FASE       : F6 — AUDITORÍA de código, ronda 1
TURNO DE   : Auditor
ENTREGAR   : este archivo completo (MENSAJE 1, luego MENSAJE 2 con los 2 diffs)
ADJUNTOS   : Ninguno (los diffs viajan incrustados en este .md)
DESTINO    : conversación NUEVA de Gemini 3.1 Pro High
ACCIÓN     : auditar C1..C6 + T-a..T-e + D1..D4 y emitir veredicto
VUELVE A   : Arquitecto, archivando la respuesta literal como
             respuesta_auditoria_ronda1.md (anti-bluff antes de aceptar)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
