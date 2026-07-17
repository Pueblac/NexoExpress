# Spec MT-R1 — Guard de audio casi mudo (422 antes de gastar tokens)

**Ciclo:** 2026-07-14_robustez_pipeline · F4 · **Rol:** Ingeniero (Sonnet, rotación asistida)
**Diseño aprobado:** r1 APROBADO CON CAMBIOS — umbral **300 B/s** (cambio 1 del dictamen). Vinculante, no rediseñar.
**Repo:** `/home/pueblac/AndroidStudioProjects/ActaExpressWeb` (working tree limpio al iniciar).

## Contrato

1. **Nuevo** `artifacts/api-server/src/lib/audioGuard.ts` (helper PURO, patrón `truncate.ts`):
```ts
export const MIN_AUDIO_BPS_DEFAULT = 300;

/** Audio casi mudo: bitrate efectivo bajo el umbral. Grabaciones <5s no se evalúan. */
export function esAudioMudo(audioSizeBytes: number, msDuration: number, minBps: number = MIN_AUDIO_BPS_DEFAULT): boolean {
  if (msDuration < 5000) return false;
  return audioSizeBytes / (msDuration / 1000) < minBps;
}
```
2. En `routes/actas.ts`, tras calcular `audioSizeBytes` y el log "received audio" (≈línea 242) y ANTES del `try { uploadToGemini`:
```ts
const minBps = Number(process.env.MIN_AUDIO_BPS) || MIN_AUDIO_BPS_DEFAULT;
if (esAudioMudo(audioSizeBytes, msDuration, minBps)) {
  req.log.warn(
    { audioSizeBytes, msDuration, bytesPerSec: Math.round(audioSizeBytes / (msDuration / 1000)), minBps },
    "processAudio: audio casi mudo rechazado (guard MT-R1)"
  );
  res.status(422).json({ error: "No se detectó señal de audio en la grabación (micrófono apagado o en silencio). Revisa tu micrófono e inténtalo de nuevo." });
  return;
}
```
Import correspondiente arriba (junto a `truncarPorBytes`).

## Restricciones
Solo `audioGuard.ts` (nuevo) y `actas.ts` (guard + import). Nada más. No commit. No tocar credenciales/Firestore.

## DoD (salida literal al informe)
1. `pnpm run typecheck` → exit 0.
2. Verificación A/B con tsx (script ad-hoc, NO commitear; ejecutar p. ej. `pnpm --filter @workspace/scripts exec tsx /tmp/ab_r1.ts` importando el helper por ruta relativa):
   - `esAudioMudo(10752, 42507)` → **true** (silencio real del piloto, 253 B/s)
   - `esAudioMudo(10_800_000, 3_600_000)` → **false** (voz 3.000 B/s)
   - `esAudioMudo(1_725_000, 3_600_000)` → **false** (479 B/s — caso falso-positivo del dictamen)
   - `esAudioMudo(100, 3000)` → **false** (piso de 5s)
   - **A/B:** con el umbral neutralizado (`minBps=0`) el primer caso da **false** → demuestra que el test protege el fix.
3. `git diff --stat` → solo los 2 archivos.

## Informe: formato estándar (qué se hizo / diff literal íntegro / evidencia DoD / desviaciones / dudas / estado commiteable).
