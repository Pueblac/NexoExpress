# Spec MT-R5 — UX de expectativa durante el procesamiento (frontend)

**Ciclo:** 2026-07-14_robustez_pipeline · F4 · **Rol:** Ingeniero (Sonnet, rotación asistida)
**Diseño aprobado:** r1 C5 SÓLIDO. Vinculante.
**Repo:** ActaExpressWeb. Working tree con MT-R1..R4 sin commit (esperado, declararlo; no tocarlo).

## Contrato (solo `artifacts/acta-express/src/pages/home.tsx`)

En el bloque de estado (donde `getStatusMessage()` renderiza "Procesando con IA..." — dentro del `<div className="flex items-center justify-center gap-2 text-muted-foreground">` o inmediatamente después de él), añadir:
```tsx
{processAudio.isPending && (
  <p className="text-xs text-muted-foreground" data-testid="text-espera">
    Esto puede tardar unos minutos — no cierres esta pestaña.
  </p>
)}
```
Colocado de modo que aparezca BAJO el mensaje de estado, solo mientras `isPending`. No tocar el toggle de MT-04 ni el efecto de disparo.

## Restricciones
Solo `home.tsx`, solo ese bloque. No commit.

## DoD (salida literal al informe)
1. `pnpm run typecheck` → exit 0.
2. `grep -n "text-espera\|no cierres esta pestaña" artifacts/acta-express/src/pages/home.tsx` → presente, condicionado a `processAudio.isPending`.
3. Render real si el entorno lo permite; si no, **NO EJECUTADO** (queda para F5 E2E con el Director) — no es desviación.
