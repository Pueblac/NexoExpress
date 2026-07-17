# Spec MT-R3 — thinkingBudget acotado en la llamada de síntesis

**Ciclo:** 2026-07-14_robustez_pipeline · F4 · **Rol:** Ingeniero (Sonnet, rotación asistida)
**Diseño aprobado:** r1 — cambio 2 del dictamen: **`thinkingBudget: 4096`** (NO 0, NO otro valor). Vinculante.
**Repo:** ActaExpressWeb. Working tree con MT-R1 y MT-R2 sin commit (esperado, declararlo; no tocarlo).

## Contrato (solo `artifacts/api-server/src/routes/actas.ts`)

En `generarSintesisEnBackground` (≈líneas 191-195), la config de la llamada pasa de:
```ts
{ temperature: 0.2, maxOutputTokens: 65536, responseMimeType: "text/plain" }
```
a:
```ts
{ temperature: 0.2, maxOutputTokens: 65536, responseMimeType: "text/plain", thinkingConfig: { thinkingBudget: 4096 } }
```
**PROHIBIDO** tocar la llamada del ACTA (≈líneas 251-255) — conserva su comportamiento (decisión C3 del diseño: un cambio a la vez).

Nota técnica: `callGemini` pasa `generationConfig` tal cual al body del request v1beta; `thinkingConfig.thinkingBudget` es un campo válido de `generationConfig` para gemini-2.5-flash. No hace falta tocar `callGemini`.

## Restricciones
Solo esa config. No commit.

## DoD (salida literal al informe)
1. `pnpm run typecheck` → exit 0.
2. `grep -n "thinkingBudget" artifacts/api-server/src/routes/actas.ts` → exactamente 1 resultado, dentro de la config de síntesis.
3. `grep -n "thinkingConfig" artifacts/api-server/src/routes/actas.ts` → 1 resultado (la llamada del acta NO lo tiene).
4. La verificación runtime (log `usageMetadata` con `thoughtsTokenCount ≤ 4096` y síntesis íntegra) queda para F5 E2E con el Director — decláralo NO EJECUTADO, no es desviación.
