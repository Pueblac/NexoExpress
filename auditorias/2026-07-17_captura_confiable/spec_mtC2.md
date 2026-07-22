# Spec MT-C2 — `startRecording(modo)` sin fallback silencioso + exponer `micStream`

**Ciclo:** 2026-07-17_captura_confiable · F4 · **Rol:** Ingeniero (Sonnet, rotación asistida)
**Diseño aprobado:** r1 + G1. Cambio 2 del dictamen (constraints presencial). Vinculante.
**Repo:** `/home/pueblac/AndroidStudioProjects/ActaExpressWeb`. Arranca sobre el working tree con **MT-C1 ya aplicada** (selector en home.tsx). Toca SOLO lo de su contrato.

## Objetivo
Cambiar la firma de `startRecording` a `startRecording(modo: ModoReunion)`: en presencial graba con el micrófono directo (sin diálogo de compartir) usando los constraints del cambio 2; en virtual conserva el flujo display+mix PERO **elimina el fallback silencioso a micrófono** (raíz de H3). Además, exponer el `micStream` crudo desde el hook para que MT-C3 lo analice.

## Contexto mínimo verificado (código real — `useAudioRecorder.ts`)
- `:3` — `type CaptureMode = "system+mic" | "system" | "microphone" | null;`
- `:43-85` `getDisplayAudioStream()` — devuelve `{stream, hadVideo}` o `null` (cancelación o sin audio tracks). NO tocar su interior.
- `:92-117` `mixAudioStreams(displayStream)` — crea `AudioContext`, conecta display, intenta `getUserMedia({audio:{echoCancellation:true,noiseSuppression:true}})`; devuelve `{mixedStream, audioCtx, micStream}`. `micStream` puede ser `null` si el mic falla.
- `:144-192` `startRecording` actual: SIEMPRE llama `getDisplayAudioStream()` primero; si `null`, cae a `getUserMedia({audio:true})` como `"microphone"` (← ESTE es el fallback silencioso a eliminar).
- `:119-133` refs del hook (`micStreamRef` ya existe en `:129`). `:135-142` `cleanupStreams`.
- `home.tsx` (tras MT-C1): existe `modoReunionRef`. El botón invoca `onClick={isRecording ? stopRecording : startRecording}` (`home.tsx:183`) — React pasa el `MouseEvent` como primer arg: hay que envolverlo.

## Contrato
1. Exportar `ModoReunion` desde el hook (o aceptar el tipo) — decláralo en `useAudioRecorder.ts` y que MT-C1 lo consuma vía import en un paso posterior no es necesario; por simplicidad **define `export type ModoReunion = "presencial" | "virtual";` en `useAudioRecorder.ts`** y en `home.tsx` importa ese tipo (elimina el `type` local que dejó MT-C1). Declara este ajuste en el informe.
2. Firma nueva: `startRecording: (modo: ModoReunion) => Promise<void>` en la interfaz `UseAudioRecorderReturn` y en la implementación.
3. Lógica por modo dentro de `startRecording`:
   - **`"presencial"`:**
```ts
try {
  recordingStream = await navigator.mediaDevices.getUserMedia({
    audio: { echoCancellation: false, noiseSuppression: false, autoGainControl: true },
  });
  micStreamRef.current = recordingStream;
  mode = "microphone";
} catch (err: unknown) {
  const msg = err instanceof Error ? err.message : "No se pudo acceder al micrófono";
  setError(msg);
  return;
}
```
   - **`"virtual"`:** llamar `getDisplayAudioStream()`. Si es `null` → `setError("No se capturó audio. Al compartir, asegúrate de seleccionar 'Pestaña de Chrome' y tener activa la casilla 'Compartir audio de la pestaña'.")` y `return` (NO arrancar, NO caer a micrófono). Si hay display → `mixAudioStreams` como hoy; `mode = micStream ? "system+mic" : "system"`; conservar el listener de "pestaña dejó de compartir" (`:168-180`).
4. Exponer el mic crudo: añadir `micStream: MediaStream | null` a `UseAudioRecorderReturn` y devolver `micStreamRef.current`. **Ojo:** para que React re-renderice cuando el mic aparece/desaparece, mantener también un estado `const [micStream, setMicStream] = useState<MediaStream|null>(null);` que se setea junto a `micStreamRef.current` (en presencial = el propio stream; en virtual = el `micStream` de `mixAudioStreams`, que puede ser null) y se limpia a `null` en `cleanupStreams`/al parar. Devuelve el ESTADO `micStream`, no el ref.
5. En `home.tsx`: cambiar la llamada del botón a `onClick={isRecording ? stopRecording : () => startRecording(modoReunionRef.current)}` (blindaje del MouseEvent). No tocar el efecto de envío ni el guard `lastProcessedAudioRef`.

## Restricciones
Solo `useAudioRecorder.ts` y `home.tsx` (llamada del botón + import del tipo + desestructurar `micStream`). NO tocar el interior de `getDisplayAudioStream`/`mixAudioStreams`. NO tocar el guard de envío. Sin dependencias nuevas. No commit.

## DoD (salida literal al informe)
1. `pnpm run typecheck` → exit 0.
2. `grep -n "startRecording(modo\|autoGainControl: true\|No se capturó audio\|micStream" artifacts/acta-express/src/hooks/useAudioRecorder.ts` → firma, constraints presencial, texto de error, estado micStream.
3. `grep -n "startRecording(modoReunionRef" artifacts/acta-express/src/pages/home.tsx` → 1 línea (la del botón).
4. **A/B manual declarado** (razonado, sin poder ejecutar navegador en el subagente): describe los 4 caminos y qué rama del código toma cada uno — (a) presencial OK, (b) virtual OK, (c) virtual cancelado (`null`→setError→return, sin `microphone`), (d) virtual display OK + mic falla (mode "system", micStream null). Cita las líneas resultantes de tu diff.
5. `git diff --stat` → SOLO los 2 archivos.

## Protocolo de dudas
Si la reestructuración del control de flujo por modo genera ambigüedad (p. ej. dónde declarar `recordingStream`/`mode` que hoy son `let` compartidos), NO supongas: implementa lo mínimo fiel al contrato y **declara la duda**. No reintroduzcas el fallback a micrófono bajo ninguna interpretación — su eliminación es el núcleo de la MT.

## Informe: formato estándar (qué se hizo / diff literal íntegro / evidencia DoD literal / desviaciones / dudas / estado commiteable).
