# Expediente 2026-07-14_robustez_pipeline — Verificación F5 del Arquitecto (tanda MT-R1..R5)

**Fecha:** 17-07-2026 · **Modo:** rotación asistida (5 subagentes Sonnet secuenciales, contexto limpio cada uno, working tree encadenado). Informes literales en `informe_mtR1.md` … `informe_mtR5.md`.

## DoD re-EJECUTADO por el Arquitecto (no leído de los informes)

1. **`git status --short`** → exactamente 3 paths: `home.tsx` (M), `audioGuard.ts` (A), `actas.ts` (M). Coincide con los 5 informes. ✅
2. **A/B de `esAudioMudo` (ejecutado con tsx):** `(10752,42507)=true` (silencio real 253 B/s) · `(10.8M,3.6M)=false` (voz) · `(1.725M,3.6M)=false` (479 B/s, caso falso-positivo del dictamen) · `(<5s)=false` · **A/B neutralizado (`minBps=0`)=false** → el test protege el fix. ✅
3. **A/B de `calcularMaxWaitMs` (ejecutado):** `42507→44250.7` · `30min→220000` · `1h→400000` · `2h→600000` (techo) · `0→40000` (piso). Los 5 valores exactos del dictamen. ✅
4. **Greps sobre el código real:** `thinkingConfig` → 1 sola línea (200), dentro de la config de SÍNTESIS; centinelas presentes en ACTA_PROMPT y SINTESIS_PROMPT; `looksEmpty` reconciliada leída directamente (título centinela + keyword `"no se detectó"` — cierra OBS-1); `waitForFileActive` definición (111) + call-site único con `msDuration` (264); `text-espera` en home.tsx:206 condicionado a `isPending`. ✅
5. **`pnpm run typecheck`** re-ejecutado → los 4 proyectos `Done`, `TYPECHECK_EXIT=0`. ✅
6. **Contraste informes vs realidad (anti-bluff interno):** cero discrepancias; cero desviaciones no declaradas; los 5 informes declararon correctamente sus límites (R3/R5 con verificación runtime NO EJECUTADA, prevista para E2E). ✅

**Veredicto F5 parte 1 (código): las 5 MTs FIELES al diseño aprobado (r1 + cambios del dictamen + OBS-1).**

## Pendiente F5 parte 2 — E2E real con el Director

| Prueba | Qué valida | Resultado esperado |
|---|---|---|
| Grabar ~30s con micrófono MUTEADO a propósito | MT-R1 guard | Toast de error INMEDIATO "No se detectó señal de audio…" — sin acta creada, sin tokens gastados (log: `audio casi mudo rechazado`) |
| Grabación normal con toggle ON | MT-R3 + MT-R5 + regresión | Mensaje "Esto puede tardar unos minutos…" visible durante el procesamiento; acta y síntesis fieles; log `sintesis: respuesta` con `thoughtsTokenCount ≤ 4096` |
| (Se mantiene del diseño) | MT-R2 centinelas | Caso borderline difícil de fabricar manualmente — cobertura por prompt + guard; se observará en uso real |

Tras la parte 2 → F6 (prompt de auditoría de la tanda con diff íntegro) → F7 (gate G2).
