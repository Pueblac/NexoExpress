# Spec MT-C3 — Hook `useMicLevel` (detector de micrófono muerto, H4)

**Ciclo:** 2026-07-17_captura_confiable · F4 · **Rol:** Ingeniero (Sonnet, rotación asistida)
**Diseño aprobado:** r1 + G1. Cambios 1 (ventana POR MODO 5s/10s), 4 (resume si suspended), 6 (getFloatTimeDomainData permitido). Vinculante.
**Repo:** `/home/pueblac/AndroidStudioProjects/ActaExpressWeb`. Arranca sobre el working tree con **MT-C1 + MT-C2 aplicadas** (existe el estado `micStream` en el hook y `ModoReunion` exportado). Toca SOLO lo de su contrato.

## Objetivo
Crear el hook nuevo `useMicLevel` que analiza el nivel del micrófono CRUDO en tiempo real con `AnalyserNode` y expone `micSilent`. La ventana de silencio depende del modo: **5 s presencial / 10 s virtual** (decisión G1). Blindado contra el `AudioContext` suspendido (trampa T1). MT-C3 solo crea el hook y lo cablea para producir `micSilent`; el banner es MT-C4.

## Contexto mínimo verificado
- `mixAudioStreams` (`useAudioRecorder.ts:107-108`) usa el mic con `echoCancellation:true, noiseSuppression:true` en modo virtual — por eso en virtual el mic puede aplanar silencios legítimos y la ventana es más larga (10 s) + banner pasivo (MT-C4).
- Tras MT-C2 el hook expone `micStream: MediaStream | null` (estado) y `export type ModoReunion`.
- Dato empírico (CTX-8 del diseño): mic muteado en SO → PCM plano (RMS ≈ 0); voz/ambiente cruza 0.01 con holgura. El `AnalyserNode` lee muestras PCM crudas, no bitrate Opus.
- Política de autoplay de Chrome: un `AudioContext` creado fuera de un gesto puede nacer `suspended` y entregar buffers planos (constante) → falso positivo. DEBE `resume()` y no evaluar hasta `state === "running"`.

## Contrato
1. **Nuevo** `artifacts/acta-express/src/hooks/useMicLevel.ts`. Constantes exportadas:
```ts
export const MIC_RMS_THRESHOLD = 0.01;
export const MIC_SILENT_WINDOW_PRESENCIAL_MS = 5000;
export const MIC_SILENT_WINDOW_VIRTUAL_MS = 10000;
const SAMPLE_INTERVAL_MS = 200;
```
2. Firma: `export function useMicLevel(micStream: MediaStream | null, active: boolean, modo: ModoReunion): { micSilent: boolean }` (importa `ModoReunion` desde `./useAudioRecorder`).
3. Comportamiento:
   - Cuando `active && micStream`: crear un `AudioContext` propio + `AnalyserNode` (`fftSize: 2048`) desde `createMediaStreamSource(micStream)`. Si `audioCtx.state === "suspended"`, llamar `audioCtx.resume()`.
   - Muestrear cada `SAMPLE_INTERVAL_MS` (via `setInterval`): leer el buffer time-domain (`getFloatTimeDomainData` preferido — rango −1..1, RMS directo; o `getByteTimeDomainData` con resta de 128 y normalización /128) y calcular el **RMS** de las muestras.
   - Mantener un timestamp `lastLoudAt` que se actualiza a "ahora" cada vez que el RMS ≥ `MIC_RMS_THRESHOLD` **o** mientras el contexto no esté `running` (así no se acumula silencio durante el arranque/suspensión). El tiempo "ahora" se obtiene con `performance.now()`.
   - `window = modo === "virtual" ? MIC_SILENT_WINDOW_VIRTUAL_MS : MIC_SILENT_WINDOW_PRESENCIAL_MS`.
   - `micSilent = (now - lastLoudAt) >= window`. Inicializar `lastLoudAt = performance.now()` al empezar (así micSilent solo puede volverse true tras `window` ms de silencio continuo). Con una sola muestra ≥ umbral, `lastLoudAt` se resetea → `micSilent` vuelve a `false` de inmediato.
   - Exponer `micSilent` como estado React (setState solo cuando cambia el valor, para no re-renderizar en cada tick).
   - **Cleanup:** al desactivarse (`!active` o `micStream` null) o desmontar: limpiar el `setInterval`, `disconnect()` el source, `close()` el `AudioContext`, y resetear `micSilent=false`, `lastLoudAt`.
4. Sin dependencias nuevas. No cablear el banner (MT-C4). Puedes invocar el hook desde `home.tsx` para obtener `micSilent` (necesario para que compile y MT-C4 lo consuma), pero SIN pintar UI nueva todavía — si prefieres, deja el consumo para MT-C4 y en MT-C3 solo entrega el hook + un uso mínimo que no rompa el render. Declara en el informe qué hiciste.

## Restricciones
Solo `useMicLevel.ts` (nuevo) y, si hace falta para compilar, la línea de invocación en `home.tsx`. NO tocar `useAudioRecorder.ts`, NO tocar el guard de envío, NO añadir UI de banner. Sin dependencias nuevas. No commit.

## DoD (salida literal al informe)
1. `pnpm run typecheck` → exit 0.
2. `grep -n "MIC_RMS_THRESHOLD\|WINDOW_PRESENCIAL\|WINDOW_VIRTUAL\|resume()\|getFloatTimeDomainData\|getByteTimeDomainData" artifacts/acta-express/src/hooks/useMicLevel.ts`.
3. **A/B razonado del cálculo** (sin navegador): traza con valores — (a) buffer plano (todas las muestras = 0 en float / 128 en byte) → RMS = 0 < 0.01 → tras `window` ms `micSilent=true`; (b) buffer con una muestra de amplitud 0.5 → RMS ≥ 0.01 → `lastLoudAt` reset → `micSilent=false`; (c) `audioCtx.state==="suspended"` → no se acumula silencio (lastLoudAt se mantiene "ahora") → sin falso positivo. Cita las líneas de tu diff que producen cada rama.
4. `git diff --stat` → `useMicLevel.ts` (nuevo) [+ posible línea en `home.tsx`].

## Protocolo de dudas
Si dudas entre `getFloat`/`getByte` o sobre el manejo del cleanup del `AudioContext`, elige la opción más simple y correcta del contrato y **declárala**. El manejo de `suspended` (cambio 4) NO es opcional. Ante cualquier ambigüedad de umbral/ventana: son valores FIJOS del diseño G1, no los reinterpretes.

## Informe: formato estándar (qué se hizo / diff literal íntegro / evidencia DoD literal / desviaciones / dudas / estado commiteable).
