# Informe de Implementación — MT-C3 (rotación asistida, Sonnet)

## 1. Qué se hizo
**`useMicLevel.ts` (NUEVO):** hook `useMicLevel(micStream, active, modo)` — `AudioContext`+`AnalyserNode` (fftSize 2048) sobre `createMediaStreamSource(micStream)`; `resume()` si `suspended`; muestreo cada 200ms con `getFloatTimeDomainData`+RMS; `lastLoudAt` se actualiza si RMS≥0.01 O mientras `state!=="running"` (no acumula silencio en arranque/suspensión); `micSilent=(now-lastLoudAt)>=window`, window 5s presencial/10s virtual (via `modoRef`); setState solo al cambiar; cleanup completo (clearInterval, disconnect, close, reset).
**`home.tsx`:** cableado mínimo — import + `const { micSilent } = useMicLevel(micStream, isRecording, modoReunion); void micSilent;` (uso diferido a MT-C4, sin UI). NO tocó useAudioRecorder.ts.

## 2. Contenido íntegro del archivo nuevo `useMicLevel.ts`
```ts
import { useEffect, useRef, useState } from "react";
import type { ModoReunion } from "./useAudioRecorder";

export const MIC_RMS_THRESHOLD = 0.01;
export const MIC_SILENT_WINDOW_PRESENCIAL_MS = 5000;
export const MIC_SILENT_WINDOW_VIRTUAL_MS = 10000;
const SAMPLE_INTERVAL_MS = 200;

export function useMicLevel(
  micStream: MediaStream | null,
  active: boolean,
  modo: ModoReunion
): { micSilent: boolean } {
  const [micSilent, setMicSilent] = useState(false);
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
      audioCtx.resume().catch(() => {});
    }
    const bufferLength = analyser.fftSize;
    const dataArray = new Float32Array(bufferLength);
    let lastLoudAt = performance.now();
    let lastReportedSilent = false;

    const intervalId = window.setInterval(() => {
      const now = performance.now();
      if (audioCtx.state !== "running") {
        lastLoudAt = now;
      } else {
        analyser.getFloatTimeDomainData(dataArray);
        let sumSquares = 0;
        for (let i = 0; i < bufferLength; i++) sumSquares += dataArray[i] * dataArray[i];
        const rms = Math.sqrt(sumSquares / bufferLength);
        if (rms >= MIC_RMS_THRESHOLD) lastLoudAt = now;
      }
      const windowMs = modoRef.current === "virtual"
        ? MIC_SILENT_WINDOW_VIRTUAL_MS : MIC_SILENT_WINDOW_PRESENCIAL_MS;
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
`home.tsx` delta MT-C3 (3 líneas): `import { useMicLevel } from "@/hooks/useMicLevel";` + `const { micSilent } = useMicLevel(micStream, isRecording, modoReunion); void micSilent;`.
`git status`: useAudioRecorder.ts (M, de C2), home.tsx (M, C1+C2+C3), useMicLevel.ts (untracked, nuevo). Sin commit.

## 3. Evidencia literal del DoD
1. `pnpm run typecheck` → 4 proyectos Done, **EXIT_CODE=0**.
2. grep constantes/resume/getFloat: MIC_RMS_THRESHOLD (4), WINDOW_PRESENCIAL (5), WINDOW_VIRTUAL (6), resume() (44), getFloatTimeDomainData (64), umbral (70). Sin getByteTimeDomainData (se usó la vía float, permitida por cambio 6).
3. `git diff --stat` → useAudioRecorder.ts (de C2) + home.tsx; useMicLevel.ts confirmado untracked/nuevo en git status. Delta MT-C3 en home.tsx = 3 líneas.
4. **A/B RMS razonado:** (a) buffer plano (RMS=0<0.01) → lastLoudAt no avanza → tras window ms micSilent=true · (b) muestra 0.5 → rms=sqrt(0.25/2048)≈0.011≥0.01 → lastLoudAt=now → micSilent=false inmediato · (c) state suspended → rama que no lee analyser, lastLoudAt=now cada tick → sin falso positivo (+ resume() al crear).

## 4. Desviaciones
Ninguna. Valores fijos del diseño respetados; resume() y no-acumular-hasta-running implementados.

## 5. Dudas del Ingeniero
Ninguna. Elegida vía `getFloatTimeDomainData` (preferida por contrato). `noUnusedLocals: false` confirmado (typecheck no falla por micSilent); aun así `void micSilent;` marca el uso diferido a MT-C4.

## 6. Estado commiteable
Verde. typecheck exit 0; hook nuevo autocontenido + 3 líneas en home.tsx; sin commit. Listo para MT-C4.
