# Expediente 2026-07-17_captura_confiable — Prompt de auditoría de CÓDIGO, ronda 1 (tanda MT-C1..C5)

**Generado:** 23-07-2026 por el Arquitecto (Fable 5), tras F5 completa (código + E2E real, ver `verificacion_f5.md`).
**TURNO DE:** Auditor (Gemini 3.1 Pro High).
**Base del diff:** ActaExpressWeb, rama `linux`, commit `c382c4c` + working tree sin commit (3 archivos).
**ADJUNTOS:** NINGUNO — todo el material verificable va incrustado en el MENSAJE 2 (diff íntegro + contenido completo de `useMicLevel.ts`, archivo nuevo untracked que no aparece en `git diff`).

---

## AVISO — Qué haces tú, paso a paso (Director)

1. Abre una conversación **NUEVA** de Gemini 3.1 Pro High (sin herencia de hilo).
2. Pega como primer mensaje el bloque **MENSAJE 1** (inicialización de identidad) y espera su confirmación.
3. Pega como segundo mensaje TODO el bloque **MENSAJE 2** (desde `# Rol y regla de oro` hasta el final del archivo). No adjuntes ficheros: el material va dentro.
4. Si la respuesta llega sin citas archivo:línea o sin trazas, responde únicamente: *"Auditoría INVÁLIDA según el contrato: faltan citas/trazas. Reenvíala completa."* — sin darle conversación.
5. Guarda la respuesta completa TAL CUAL en `auditorias/2026-07-17_captura_confiable/respuesta_auditoria_ronda1.md` y avísame; yo le anexo la validación anti-bluff.

---

## MENSAJE 1 — Inicialización de identidad (pegar y esperar confirmación)

```
Rol: Auditor del ciclo 2026-07-17_captura_confiable, metodología v2 del
ecosistema Express. Confirma recepción sin accionar; acepta únicamente
artefactos cuyo campo TURNO DE diga Auditor.
```

---

## MENSAJE 2 — Prompt de auditoría (pegar íntegro tras la confirmación)

# Rol y regla de oro

Eres auditor adversarial del ecosistema Express. El implementador (otra IA) afirma haber implementado en ActaExpressWeb la tanda "captura confiable" (5 micro-tareas): selector explícito de tipo de reunión presencial/virtual con persistencia, `startRecording(modo)` sin fallback silencioso de fuente de audio, detector de micrófono muerto en tiempo real (hook nuevo `useMicLevel`), banner de aviso por severidad y tarjeta prominente de procesamiento. **Tu hipótesis de trabajo es que está mal o incompleto hasta que demuestre lo contrario.** No eres un asistente conversacional: no agradezcas, no resumas, no elogies. Cada afirmación sin cita textual del material incrustado (archivo y nº de línea del diff o del archivo completo) se considera inventada.

# Formato obligatorio de CADA verificación

CLAIM → EVIDENCIA (cita textual, archivo:línea) → TRAZA (ejecución simbólica paso a paso con valores concretos) → VERDICTO (CONFIRMADO / BUG / NO VERIFICABLE CON LO ADJUNTO). Lo no incrustado en este mensaje es NO VERIFICABLE — prohibido rellenarlo con suposiciones.

# Contexto mínimo verificado (no es prosa del implementador)

- App: ActaExpressWeb (React + Vite). El flujo graba audio de reunión, lo envía a un backend que genera un acta con Gemini.
- Hallazgos que motivan la tanda: **H3** — en Linux, la captura de pestaña sin audio caía SILENCIOSAMENTE a solo-micrófono (el usuario creía grabar la reunión y grababa el mic); **H4** — un micrófono muteado en el SO solo se descubría al final (guard 422 del server), no al inicio.
- Diseño congelado en G1 (dictamen de diseño APROBADO CON CAMBIOS, 6 cambios incorporados + reconciliación de ventana por modo): default presencial; persistencia por uid; presencial = `getUserMedia` directo con `echoCancellation:false, noiseSuppression:false, autoGainControl:true`; virtual = pestaña+mic SIN fallback; umbral RMS 0.01; ventana 5 s presencial / 10 s virtual; el aviso NUNCA corta la grabación; banner rojo destructivo en presencial y ámbar pasivo en virtual.
- F5 ya ejecutada por el Arquitecto: typecheck verde (4 proyectos), greps de marcadores por MT, y E2E real en navegador con las 6 pruebas de la tabla de `verificacion_f5.md` PASADAS (banner rojo con mic muteado y desaparición al desmutear; regresión sin banner; virtual cancelado → error accionable sin arrancar; ámbar a ~10 s en virtual; persistencia tras reload; tarjeta de procesamiento y acta fiel). Tu trabajo NO es repetir el E2E: es encontrar lo que el E2E feliz no cubre.

# Material incrustado

## 1) `git diff` ÍNTEGRO del working tree (2 archivos modificados)

```diff
diff --git a/artifacts/acta-express/src/hooks/useAudioRecorder.ts b/artifacts/acta-express/src/hooks/useAudioRecorder.ts
index ce570b8..7b7c786 100644
--- a/artifacts/acta-express/src/hooks/useAudioRecorder.ts
+++ b/artifacts/acta-express/src/hooks/useAudioRecorder.ts
@@ -2,15 +2,18 @@ import { useState, useRef, useCallback } from "react";
 
 type CaptureMode = "system+mic" | "system" | "microphone" | null;
 
+export type ModoReunion = "presencial" | "virtual";
+
 interface UseAudioRecorderReturn {
   isRecording: boolean;
-  startRecording: () => Promise<void>;
+  startRecording: (modo: ModoReunion) => Promise<void>;
   stopRecording: () => Promise<void>;
   audioBlob: Blob | null;
   audioBase64: string | null;
   duration: number;
   error: string | null;
   captureMode: CaptureMode;
+  micStream: MediaStream | null;
 }
 
 function blobToBase64(blob: Blob): Promise<string> {
@@ -123,6 +126,7 @@ export function useAudioRecorder(): UseAudioRecorderReturn {
   const [duration, setDuration] = useState(0);
   const [error, setError] = useState<string | null>(null);
   const [captureMode, setCaptureMode] = useState<CaptureMode>(null);
+  const [micStream, setMicStream] = useState<MediaStream | null>(null);
 
   const mediaRecorderRef = useRef<MediaRecorder | null>(null);
   const displayStreamRef = useRef<MediaStream | null>(null);
@@ -139,9 +143,10 @@ export function useAudioRecorder(): UseAudioRecorderReturn {
     displayStreamRef.current = null;
     micStreamRef.current = null;
     audioCtxRef.current = null;
+    setMicStream(null);
   }, []);
 
-  const startRecording = useCallback(async () => {
+  const startRecording = useCallback(async (modo: ModoReunion) => {
     setError(null);
     setAudioBlob(null);
     setAudioBase64(null);
@@ -151,18 +156,40 @@ export function useAudioRecorder(): UseAudioRecorderReturn {
     let recordingStream: MediaStream;
     let mode: CaptureMode;
 
-    // --- Try system audio first ---
-    const displayResult = await getDisplayAudioStream();
+    if (modo === "presencial") {
+      // --- Presencial: micrófono directo, sin diálogo de compartir ---
+      try {
+        recordingStream = await navigator.mediaDevices.getUserMedia({
+          audio: { echoCancellation: false, noiseSuppression: false, autoGainControl: true },
+        });
+        micStreamRef.current = recordingStream;
+        setMicStream(recordingStream);
+        mode = "microphone";
+      } catch (err: unknown) {
+        const msg = err instanceof Error ? err.message : "No se pudo acceder al micrófono";
+        setError(msg);
+        return;
+      }
+    } else {
+      // --- Virtual: display + mix. Sin fallback silencioso a micrófono ---
+      const displayResult = await getDisplayAudioStream();
+
+      if (!displayResult) {
+        setError(
+          "No se capturó audio. Al compartir, asegúrate de seleccionar 'Pestaña de Chrome' y tener activa la casilla 'Compartir audio de la pestaña'."
+        );
+        return;
+      }
 
-    if (displayResult) {
       displayStreamRef.current = displayResult.stream;
 
       // Mix with microphone
-      const { mixedStream, audioCtx, micStream } = await mixAudioStreams(displayResult.stream);
+      const { mixedStream, audioCtx, micStream: mixMicStream } = await mixAudioStreams(displayResult.stream);
       audioCtxRef.current = audioCtx;
-      micStreamRef.current = micStream;
+      micStreamRef.current = mixMicStream;
+      setMicStream(mixMicStream);
       recordingStream = mixedStream;
-      mode = micStream ? "system+mic" : "system";
+      mode = mixMicStream ? "system+mic" : "system";
 
       // If display track ends (user stops sharing), stop the recording too
       displayResult.stream.getAudioTracks().forEach((track) => {
@@ -178,17 +205,6 @@ export function useAudioRecorder(): UseAudioRecorderReturn {
           }
         });
       });
-    } else {
-      // --- Fallback: microphone only ---
-      try {
-        recordingStream = await navigator.mediaDevices.getUserMedia({ audio: true });
-        micStreamRef.current = recordingStream;
-        mode = "microphone";
-      } catch (err: unknown) {
-        const msg = err instanceof Error ? err.message : "No se pudo acceder al micrófono";
-        setError(msg);
-        return;
-      }
     }
 
     setCaptureMode(mode);
@@ -257,5 +273,6 @@ export function useAudioRecorder(): UseAudioRecorderReturn {
     duration,
     error,
     captureMode,
+    micStream,
   };
 }
diff --git a/artifacts/acta-express/src/pages/home.tsx b/artifacts/acta-express/src/pages/home.tsx
index 158bdb3..dc77478 100644
--- a/artifacts/acta-express/src/pages/home.tsx
+++ b/artifacts/acta-express/src/pages/home.tsx
@@ -1,6 +1,7 @@
 import { useEffect, useRef, useState } from "react";
 import { useAuth } from "@/context/AuthContext";
-import { useAudioRecorder } from "@/hooks/useAudioRecorder";
+import { useAudioRecorder, type ModoReunion } from "@/hooks/useAudioRecorder";
+import { useMicLevel } from "@/hooks/useMicLevel";
 import { useListActas, useProcessAudio, useDeleteActa, getListActasQueryKey } from "@workspace/api-client-react";
 import { useQueryClient } from "@tanstack/react-query";
 import { format } from "date-fns";
@@ -13,6 +14,7 @@ import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
 import { Skeleton } from "@/components/ui/skeleton";
 import { Switch } from "@/components/ui/switch";
 import { Label } from "@/components/ui/label";
+import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
 import { useToast } from "@/hooks/use-toast";
 import {
   AlertDialog,
@@ -44,10 +46,11 @@ export default function Home() {
     isRecording, 
     startRecording, 
     stopRecording, 
-    audioBase64, 
-    duration, 
+    audioBase64,
+    duration,
     error,
-    captureMode
+    captureMode,
+    micStream
   } = useAudioRecorder();
 
   const { data: actas, isLoading: loadingActas } = useListActas();
@@ -67,6 +70,21 @@ export default function Home() {
     }
   };
 
+  const [modoReunion, setModoReunion] = useState<ModoReunion>(() => {
+    if (!user) return "presencial";
+    const saved = localStorage.getItem(`actaexpress:modoReunion:${user.uid}`);
+    return saved === "virtual" ? "virtual" : "presencial";
+  });
+  const modoReunionRef = useRef(modoReunion);
+  modoReunionRef.current = modoReunion;
+  const handleModoReunionChange = (modo: ModoReunion) => {
+    setModoReunion(modo);
+    if (user) localStorage.setItem(`actaexpress:modoReunion:${user.uid}`, modo);
+  };
+
+  // MT-C3: solo cablea el hook para producir micSilent; el banner es MT-C4.
+  const { micSilent } = useMicLevel(micStream, isRecording, modoReunion);
+
   const processAudio = useProcessAudio({
     mutation: {
       onSuccess: (acta, variables) => {
@@ -180,7 +198,7 @@ export default function Home() {
                     ? "bg-red-500 hover:bg-red-600 border-red-400" 
                     : "bg-primary hover:bg-primary/90 border-primary/50 hover:scale-105"
                 }`}
-                onClick={isRecording ? stopRecording : startRecording}
+                onClick={isRecording ? stopRecording : () => startRecording(modoReunionRef.current)}
                 disabled={processAudio.isPending}
               >
                 {processAudio.isPending ? (
@@ -198,14 +216,24 @@ export default function Home() {
             <h2 className="text-4xl font-mono tracking-tighter font-semibold">
               {formatDuration(duration)}
             </h2>
-            <div className="flex items-center justify-center gap-2 text-muted-foreground">
-              {isRecording && <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />}
-              <p className="font-medium">{getStatusMessage()}</p>
-            </div>
-            {processAudio.isPending && (
-              <p className="text-xs text-muted-foreground" data-testid="text-espera">
-                Esto puede tardar unos minutos — no cierres esta pestaña.
-              </p>
+            {processAudio.isPending ? (
+              <div
+                data-testid="card-procesando"
+                className="border border-primary/30 bg-primary/10 rounded-xl p-4 flex flex-col items-center gap-2"
+              >
+                <div className="flex items-center gap-2">
+                  <Loader2 className="h-5 w-5 animate-spin text-primary" />
+                  <p className="text-base font-semibold">Procesando con IA...</p>
+                </div>
+                <p className="text-xs text-muted-foreground" data-testid="text-espera">
+                  Esto puede tardar unos minutos — no cierres esta pestaña.
+                </p>
+              </div>
+            ) : (
+              <div className="flex items-center justify-center gap-2 text-muted-foreground">
+                {isRecording && <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />}
+                <p className="font-medium">{getStatusMessage()}</p>
+              </div>
             )}
 
             <AnimatePresence>
@@ -227,6 +255,63 @@ export default function Home() {
               )}
             </AnimatePresence>
 
+            {isRecording && micSilent && (
+              <div
+                data-testid="banner-mic-muerto"
+                className={
+                  modoReunion === "presencial"
+                    ? "flex items-center justify-center gap-2 text-destructive text-sm mt-2 bg-destructive/10 px-4 py-2 rounded-md"
+                    : "flex items-center justify-center gap-2 text-amber-500 text-sm mt-2 bg-amber-500/10 px-4 py-2 rounded-md"
+                }
+              >
+                <AlertCircle className="w-4 h-4" />
+                {modoReunion === "presencial"
+                  ? "⚠️ No se detecta señal de tu micrófono — revisa que no esté silenciado en el sistema."
+                  : "Tu micrófono no aporta señal. Si solo escuchas la reunión está bien; si querías hablar, revisa que no esté silenciado."}
+              </div>
+            )}
+
+            <div
+              data-testid="selector-modo-reunion"
+              className="flex justify-center pt-2"
+            >
+              <RadioGroup
+                value={modoReunion}
+                onValueChange={(value) => handleModoReunionChange(value as ModoReunion)}
+                disabled={isRecording || processAudio.isPending}
+                className="flex flex-col gap-3 sm:flex-row sm:gap-6"
+              >
+                <div className="flex items-start gap-2">
+                  <RadioGroupItem
+                    value="presencial"
+                    id="modo-presencial"
+                    data-testid="modo-presencial"
+                    className="mt-1"
+                  />
+                  <Label htmlFor="modo-presencial" className="cursor-pointer text-left">
+                    <span className="block font-medium">Reunión presencial</span>
+                    <span className="block text-xs text-muted-foreground">
+                      Sonido ambiente (micrófono directo)
+                    </span>
+                  </Label>
+                </div>
+                <div className="flex items-start gap-2">
+                  <RadioGroupItem
+                    value="virtual"
+                    id="modo-virtual"
+                    data-testid="modo-virtual"
+                    className="mt-1"
+                  />
+                  <Label htmlFor="modo-virtual" className="cursor-pointer text-left">
+                    <span className="block font-medium">Reunión virtual</span>
+                    <span className="block text-xs text-muted-foreground">
+                      Audio de la pestaña + micrófono
+                    </span>
+                  </Label>
+                </div>
+              </RadioGroup>
+            </div>
+
             <div className="flex items-center justify-center gap-2 pt-2">
               <Switch
                 id="switch-sintesis"
```

## 2) `useMicLevel.ts` COMPLETO (archivo NUEVO, untracked — por eso no aparece en el diff; 97 líneas)

```typescript
import { useEffect, useRef, useState } from "react";
import type { ModoReunion } from "./useAudioRecorder";

export const MIC_RMS_THRESHOLD = 0.01;
export const MIC_SILENT_WINDOW_PRESENCIAL_MS = 5000;
export const MIC_SILENT_WINDOW_VIRTUAL_MS = 10000;
const SAMPLE_INTERVAL_MS = 200;

/**
 * Analiza el nivel del micrófono CRUDO en tiempo real con un AnalyserNode
 * propio y expone `micSilent` cuando el RMS permanece por debajo de
 * MIC_RMS_THRESHOLD durante la ventana correspondiente al modo de reunión
 * (5s presencial / 10s virtual).
 *
 * Blindado contra AudioContext "suspended" (política de autoplay de Chrome):
 * mientras el contexto no esté "running" no se acumula silencio, para evitar
 * falsos positivos por buffers planos entregados durante el arranque.
 */
export function useMicLevel(
  micStream: MediaStream | null,
  active: boolean,
  modo: ModoReunion
): { micSilent: boolean } {
  const [micSilent, setMicSilent] = useState(false);

  // Ref para que el intervalo siempre lea el modo vigente sin forzar el
  // reinicio del AudioContext si `modo` cambiara mientras está activo.
  const modoRef = useRef(modo);
  modoRef.current = modo;

  useEffect(() => {
    if (!active || !micStream) {
      setMicSilent(false);
      return;
    }

    const audioCtx = new AudioContext();
    const analyser = audioCtx.createAnalyser();
    analyser.fftSize = 2048;
    const source = audioCtx.createMediaStreamSource(micStream);
    source.connect(analyser);

    if (audioCtx.state === "suspended") {
      audioCtx.resume().catch(() => {
        // Si el resume falla, el propio bucle de muestreo seguirá sin
        // acumular silencio mientras state !== "running".
      });
    }

    const bufferLength = analyser.fftSize;
    const dataArray = new Float32Array(bufferLength);

    let lastLoudAt = performance.now();
    let lastReportedSilent = false;

    const intervalId = window.setInterval(() => {
      const now = performance.now();

      if (audioCtx.state !== "running") {
        // No evaluar RMS mientras el contexto no esté corriendo: así no se
        // acumula silencio durante el arranque/suspensión (trampa T1).
        lastLoudAt = now;
      } else {
        analyser.getFloatTimeDomainData(dataArray);
        let sumSquares = 0;
        for (let i = 0; i < bufferLength; i++) {
          sumSquares += dataArray[i] * dataArray[i];
        }
        const rms = Math.sqrt(sumSquares / bufferLength);
        if (rms >= MIC_RMS_THRESHOLD) {
          lastLoudAt = now;
        }
      }

      const windowMs =
        modoRef.current === "virtual"
          ? MIC_SILENT_WINDOW_VIRTUAL_MS
          : MIC_SILENT_WINDOW_PRESENCIAL_MS;
      const silentNow = now - lastLoudAt >= windowMs;

      if (silentNow !== lastReportedSilent) {
        lastReportedSilent = silentNow;
        setMicSilent(silentNow);
      }
    }, SAMPLE_INTERVAL_MS);

    return () => {
      window.clearInterval(intervalId);
      source.disconnect();
      audioCtx.close().catch(() => {});
      setMicSilent(false);
      lastLoudAt = performance.now();
    };
  }, [active, micStream]);

  return { micSilent };
}
```

# Claims a verificar

- **C1 (MT-C1):** El selector `selector-modo-reunion` tiene default `"presencial"`, persiste el modo elegido en `localStorage` bajo la clave `actaexpress:modoReunion:${user.uid}` (por usuario, no global), lo restaura al montar, y queda deshabilitado durante la grabación Y durante el procesamiento.
- **C2 (MT-C2, corrección de H3):** `startRecording(modo)` con `modo === "virtual"` que recibe `null` de `getDisplayAudioStream()` (usuario cancela el diálogo) fija el error accionable y RETORNA sin arrancar la grabación: no existe NINGÚN camino de código por el que virtual degrade silenciosamente a solo-micrófono. El fallback histórico `getUserMedia({ audio: true })` fue eliminado, no movido.
- **C3 (MT-C2):** En presencial, las constraints son exactamente `echoCancellation: false, noiseSuppression: false, autoGainControl: true` (sonido ambiente: sin cancelación que mate voces lejanas, con AGC para niveles), y el hook expone `micStream` como estado React (no solo ref) para que `useMicLevel` re-renderice al obtenerlo.
- **C4 (MT-C3, corrección de H4):** `useMicLevel` solo declara `micSilent === true` cuando el RMS del mic CRUDO permanece < 0.01 durante la ventana completa del modo vigente (5000 ms presencial / 10000 ms virtual), no acumula silencio mientras `audioCtx.state !== "running"`, y al desactivarse (`active` false o `micStream` null) resetea a `false` y libera el `AudioContext` y el `AnalyserNode`.
- **C5 (MT-C4):** El banner `banner-mic-muerto` se renderiza SOLO con `isRecording && micSilent`, con severidad por modo (destructive/rojo en presencial, amber/pasivo en virtual, textos distintos), y no existe ningún camino por el que el detector detenga la grabación (`stopRecording` jamás se invoca desde la lógica de `micSilent`).
- **C6 (traza obligatoria, estado final literal):** Ejecuta simbólicamente el escenario completo: usuario con `uid = "u1"`, modo persistido `"presencial"`, mic muteado en el SO (buffers con todas las muestras en 0.0). t=0 pulsa grabar. Muestra: constraints pasadas a `getUserMedia`, valor de `mode`/`captureMode`, evolución de `lastLoudAt` y `silentNow` en t=200ms…5200ms (incluyendo el caso de arranque con `state === "suspended"` hasta t=600ms), instante exacto del primer `setMicSilent(true)`, y el JSX EXACTO del banner renderizado (clases y texto). Después: a t=8s desmutea (RMS pasa a 0.05) — instante del `setMicSilent(false)` y estado final de la UI.

# Dudas declaradas

Del Ingeniero (informes MT-C1..C5): ninguna — cero dudas declaradas en los 5 informes.

Del Arquitecto (Fable 5):
- **D1 — Margen fino del umbral:** una sola muestra a 0.5 entre 2047 ceros da RMS ≈ 0.011, apenas sobre el umbral 0.01. ¿Es robusto el par (umbral 0.01, fftSize 2048 a 48 kHz ≈ 42,7 ms de ventana por muestreo) frente a (a) ruido de piso de un mic sano en sala en silencio — riesgo de banner falso en presencial si nadie habla durante 5 s — y (b) clicks/pops espurios de un mic muerto que lo resetean? El E2E real pasó (prueba 2 sin falsos positivos hablando; prueba 1 detectó el mute), pero el caso "sala callada con mic sano" no se probó explícitamente.
- **D2 — Reloj del detector:** la ventana usa `performance.now()` leído dentro de un `setInterval` de 200 ms. En segundo plano Chrome puede throttlear timers (hasta 1 ejecución/minuto en pestañas ocultas) — y en modo virtual el usuario está PRECISAMENTE en otra pestaña (la compartida). ¿Puede el throttling (i) retrasar el aviso ámbar mucho más allá de 10 s, o (ii) producir un flash de banner falso al volver a la pestaña porque `now` saltó mientras `lastLoudAt` quedó atrás sin que se evaluara RMS en medio? Nota: el E2E de la prueba 4 mostró el ámbar a ~12 s, pero con la pestaña de la app probablemente visible.
- **D3 — Fatiga de alarma:** en virtual, si el usuario legítimamente solo escucha (mic muteado a propósito), el aviso ámbar queda fijo toda la reunión. ¿El texto pasivo elegido mitiga suficiente o recomiendas un mecanismo de descarte (cerrar el aviso)? Opinión fundada, no rediseño.
- **D4 — E2E fino pendiente:** la aparición del banner rojo en ≤5 s exactos se verificó por diseño (constantes) y captura a los 10 s de grabación, no con cronómetro. ¿Hay algo en el código que pudiera retrasarla más allá de ~5,2 s en pestaña visible?

# Preguntas de control (respóndelas TODAS; son parte del entregable)

- **Q1:** Copia TEXTUALMENTE, carácter a carácter: (a) el mensaje de error del camino virtual-cancelado en `useAudioRecorder.ts`; (b) el texto del banner presencial y (c) el del banner virtual en `home.tsx`.
- **Q2:** En `useMicLevel`, si `audioCtx.resume()` falla y el contexto queda `"suspended"` para siempre, ¿qué valor tiene `micSilent` a los 60 s de grabación con mic muteado? Traza con las líneas exactas que lo determinan y di si ese comportamiento es el correcto para H4 o un hueco.
- **Q3:** Traza de persistencia: usuario `uid = "u1"` elige "virtual" y recarga la página. ¿Qué clave EXACTA se lee, qué devuelve `localStorage.getItem` y qué valor inicial toma `modoReunion`? Repite para `saved === null` (primer uso) y para `saved === "basura"` (valor corrupto). Cita el inicializador del `useState`.
- **Q4:** En una grabación virtual donde el usuario comparte pestaña con audio pero DENIEGA el permiso de micrófono, ¿qué valor toma `mode`, qué recibe `useMicLevel` como `micStream` y, en consecuencia, puede aparecer el aviso ámbar? ¿Es ese comportamiento correcto o un hueco de H4? Cita las líneas del diff que lo determinan.

# Anti-aprobación-automática

Si tu veredicto global es APROBADO, debes ADEMÁS demostrar por qué cada una de estas trampas NO aplica (con evidencia y traza, no con "parece bien"):

- **T1 — Arranque suspendido:** Chrome entrega el `AudioContext` en `"suspended"` y los primeros buffers planos. ¿Puede el detector acumular esos ceros y disparar el banner ANTES de que el contexto corra (falso positivo de arranque)?
- **T2 — Cambio de modo en vivo:** el selector se deshabilita grabando, pero `useMicLevel` lee `modoRef.current` en cada tick. Si por cualquier vía (bug de la UI de RadioGroup, teclado, React DevTools) `modoReunion` cambiara DURANTE una grabación con 6 s de silencio acumulado, ¿qué hace el banner al pasar presencial→virtual y virtual→presencial? ¿Algún estado inconsistente (p. ej. banner rojo con textos de virtual)?
- **T3 — Doble grabación consecutiva:** grabación 1 termina (cleanup), el usuario graba de nuevo sin recargar. ¿Llega a `useMicLevel` el stream NUEVO (y no uno stale de la 1ª) y parte `micSilent` de `false`? Traza el ciclo `setMicStream(null)` → `setMicStream(nuevo)` y las dependencias del `useEffect`.
- **T4 — Fin de compartición en virtual:** durante virtual con banner ámbar visible, el usuario detiene la compartición de pestaña (track `ended` → `stopRecording()`). ¿Queda algún `AudioContext` del detector sin cerrar, algún intervalo vivo, o el banner visible tras parar?
- **T5 — Usuario nulo:** `user` es `null` en el primer render (carrera de auth). ¿Puede el inicializador del `useState` fijar "presencial" y luego, con el uid ya resuelto y un modo "virtual" persistido, quedarse la UI en el modo equivocado sin releer localStorage? ¿Con qué severidad?

# Entregable final

Entrega TODA tu respuesta como UN ÚNICO documento markdown listo para archivar, con: 1. Tabla C1..C6 con verdictos. 2. Respuestas Q1..Q4. 3. Demostración T1..T5 si apruebas. 4. Opinión fundada sobre D1..D4. 5. Veredicto global (APROBADO / APROBADO CON OBSERVACIONES / RECHAZADO). Una auditoría sin citas archivo:línea o sin las trazas obligatorias es INVÁLIDA y será devuelta.
