# Spec MT-R4 — Timeout proporcional en waitForFileActive

**Ciclo:** 2026-07-14_robustez_pipeline · F4 · **Rol:** Ingeniero (Sonnet, rotación asistida)
**Diseño aprobado:** r1 — fórmula `clamp(40_000, 40_000 + msDuration/10, 600_000)` (C4 SÓLIDO + D4 confirmada). Vinculante.
**Repo:** ActaExpressWeb. Working tree con MT-R1..R3 sin commit (esperado, declararlo; no tocarlo).

## Contrato

1. En `artifacts/api-server/src/lib/audioGuard.ts` (creado en MT-R1), añadir helper PURO:
```ts
/** Espera máxima para que la File API active el archivo, proporcional a la duración del audio. */
export function calcularMaxWaitMs(msDuration: number): number {
  return Math.min(Math.max(40_000, 40_000 + msDuration / 10), 600_000);
}
```
2. En `routes/actas.ts`, `waitForFileActive` (≈líneas 108-117) pasa a recibir la duración y a iterar por presupuesto de tiempo:
```ts
async function waitForFileActive(fileName: string, msDuration: number): Promise<GeminiFile> {
  const maxWaitMs = calcularMaxWaitMs(msDuration);
  const maxAttempts = Math.ceil(maxWaitMs / 2000);
  for (let i = 0; i < maxAttempts; i++) {
    ... (cuerpo idéntico al actual) ...
  }
  throw new Error("Timeout: el archivo tardó demasiado en procesarse");
}
```
3. Único call-site (≈línea 248): `waitForFileActive(uploadedFile.name, msDuration)`.

## Restricciones
Solo `audioGuard.ts` y `actas.ts`. No commit.

## DoD (salida literal al informe)
1. `pnpm run typecheck` → exit 0.
2. Verificación A/B tsx (ad-hoc, no commitear):
   - `calcularMaxWaitMs(42_507)` → **44_250.7** (≈44s; audio corto apenas sube del piso)
   - `calcularMaxWaitMs(1_800_000)` → **220_000** (30 min → 3,6 min de espera; caso del dictamen)
   - `calcularMaxWaitMs(3_600_000)` → **400_000** (1 h → 6,67 min; caso Q4)
   - `calcularMaxWaitMs(7_200_000)` → **600_000** (techo)
   - `calcularMaxWaitMs(0)` → **40_000** (piso)
   - **A/B:** con la fórmula neutralizada (retornar 40_000 fijo) los casos de 30/60 min dan 40_000 → demuestra qué protege.
3. `grep -n "waitForFileActive" artifacts/api-server/src/routes/actas.ts` → definición + 1 call-site con `msDuration`.
