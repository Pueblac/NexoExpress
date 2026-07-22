# Informe de Implementación — MT-C2 (rotación asistida, Sonnet)

## 1. Qué se hizo
**`useAudioRecorder.ts`:** `export type ModoReunion`; `startRecording` → `(modo: ModoReunion)`; añadido `micStream: MediaStream|null` a la interfaz, estado (`useState`) y retorno; `cleanupStreams` hace `setMicStream(null)`. `startRecording` reestructurado `if(presencial){getUserMedia con echoCancellation:false,noiseSuppression:false,autoGainControl:true} else {getDisplayAudioStream(); null→setError(texto Q3)+return SIN fallback; mix; mode=mixMicStream?"system+mic":"system"}`. Interior de `getDisplayAudioStream`/`mixAudioStreams` intacto. Variable desestructurada renombrada `micStream`→`mixMicStream` para no chocar con el estado.
**`home.tsx`:** import `type ModoReunion` desde el hook (elimina el type local de C1); `micStream` desestructurado; botón `onClick={isRecording ? stopRecording : () => startRecording(modoReunionRef.current)}`. Efecto de envío y guard intactos.

## 2. Diff literal íntegro
(Diff completo capturado en la sesión del Arquitecto; se regenera íntegro en F6 vía `git diff HEAD`. Cambios clave de useAudioRecorder.ts:)
```diff
+export type ModoReunion = "presencial" | "virtual";
-  startRecording: () => Promise<void>;
+  startRecording: (modo: ModoReunion) => Promise<void>;
+  micStream: MediaStream | null;
...
+  const [micStream, setMicStream] = useState<MediaStream | null>(null);
...
-  const startRecording = useCallback(async () => {
+  const startRecording = useCallback(async (modo: ModoReunion) => {
...
+    if (modo === "presencial") {
+      try {
+        recordingStream = await navigator.mediaDevices.getUserMedia({
+          audio: { echoCancellation: false, noiseSuppression: false, autoGainControl: true },
+        });
+        micStreamRef.current = recordingStream;
+        setMicStream(recordingStream);
+        mode = "microphone";
+      } catch (err: unknown) { setError(...); return; }
+    } else {
+      const displayResult = await getDisplayAudioStream();
+      if (!displayResult) {
+        setError("No se capturó audio. Al compartir, asegúrate de seleccionar 'Pestaña de Chrome' y tener activa la casilla 'Compartir audio de la pestaña'.");
+        return;
+      }
       displayStreamRef.current = displayResult.stream;
+      const { mixedStream, audioCtx, micStream: mixMicStream } = await mixAudioStreams(displayResult.stream);
+      micStreamRef.current = mixMicStream; setMicStream(mixMicStream);
+      mode = mixMicStream ? "system+mic" : "system";
       // listener "pestaña dejó de compartir" conservado
-    } else {  // ← FALLBACK SILENCIOSO A MICRÓFONO: ELIMINADO
-      recordingStream = await navigator.mediaDevices.getUserMedia({ audio: true });
-      mode = "microphone";
     }
```
home.tsx: `-import { useAudioRecorder }` → `+import { useAudioRecorder, type ModoReunion }`; `+micStream` en desestructuración; `onClick` con wrapper `() => startRecording(modoReunionRef.current)`.
`git status`: solo `useAudioRecorder.ts` + `home.tsx` (home.tsx acumula C1+C2), sin commit.

## 3. Evidencia literal del DoD
1. `pnpm run typecheck` → 4 proyectos Done, **EXIT_CODE=0**.
2. grep useAudioRecorder.ts: interfaz `micStream: MediaStream|null` (16), estado (129), constraints presencial `autoGainControl: true` (163), texto Q3 (179), mixMicStream (187-189), retorno micStream (276).
3. grep home.tsx: `onClick=... startRecording(modoReunionRef.current)` → 1 línea (197).
4. **A/B 4 caminos:** (a) presencial → getUserMedia directo, mode "microphone", micStream=stream · (b) virtual OK → mix, mode "system+mic" · (c) virtual cancelado → getDisplayAudioStream null → setError+return, NO llega a MediaRecorder, NO cae a microphone (H3 corregido) · (d) virtual+mic falla → mixMicStream null → mode "system", micStream null.
5. `git diff --stat` → useAudioRecorder.ts + home.tsx, 2 files, +96/−24. Repo-wide `git status --porcelain`: solo esos 2.

## 4. Desviaciones
Ninguna. El type ModoReunion en el hook (no home.tsx) es ajuste mandatado por el contrato punto 1.

## 5. Dudas del Ingeniero
Ninguna.

## 6. Estado commiteable
Verde. typecheck exit 0; solo 2 archivos; sin commit. Listo para MT-C3.
