# Expediente 2026-07-17_captura_confiable — Verificación F5 del Arquitecto (tanda MT-C1..C5)

**Fecha:** 22-07-2026 · **Modo:** rotación asistida (5 subagentes Sonnet secuenciales, contexto limpio cada uno, working tree encadenado). Informes literales en `informe_mtC1.md` … `informe_mtC5.md`.

## DoD re-EJECUTADO por el Arquitecto (no leído de los informes)

1. **`git status --short`** → exactamente 3 paths: `useAudioRecorder.ts` (M), `home.tsx` (M), `useMicLevel.ts` (?? nuevo). Coincide con los 5 informes. ✅
2. **`pnpm run typecheck`** re-ejecutado → los 4 proyectos `Done`, `TYPECHECK_EXIT=0`. ✅
3. **Marcadores por MT sobre el código real (grep):**
   - MT-C1: 11 coincidencias de `modoReunion`/`selector-modo-reunion`/`actaexpress:modoReunion` en home.tsx. ✅
   - MT-C2: constraints presencial `echoCancellation:false, noiseSuppression:false, autoGainControl:true` (useAudioRecorder.ts:163); texto Q3 exacto (:179); **el fallback silencioso `getUserMedia({ audio: true })` YA NO EXISTE** (grep sin resultados) — raíz de H3 eliminada. ✅
   - MT-C3: `MIC_RMS_THRESHOLD = 0.01` (:4), `PRESENCIAL_MS = 5000` (:5), `VIRTUAL_MS = 10000` (:6), `resume()` (:44), guardia `state !== "running"` (:59). ✅
   - MT-C4: `banner-mic-muerto` (:260) con bifurcación `text-destructive`/`bg-destructive/10` (presencial, :263) vs `text-amber-500`/`bg-amber-500/10` (virtual, :264). ✅
   - MT-C5: `card-procesando` (:221) + `text-espera` conservado (:228) con su texto exacto. ✅
4. **Contraste informes vs realidad (anti-bluff interno):** cero discrepancias; cero desviaciones no declaradas. Dudas menores de C1 (testid en el control) y C4 (comentario obsoleto) resueltas por el Arquitecto sin reabrir F3.

**Veredicto F5 parte 1 (código): las 5 MTs FIELES al diseño congelado en G1** (6 cambios del dictamen + ventana por modo 5s/10s). typecheck verde, alcance cerrado (frontend, 3 archivos), sin dependencias nuevas.

## Pendiente F5 parte 2 — E2E real con el Director

| Prueba | Modo | Qué valida | Resultado esperado |
|---|---|---|---|
| Grabar con mic MUTEADO en el SO | **presencial** | MT-C3+C4 detector+banner | Banner ROJO "⚠️ No se detecta señal de tu micrófono…" en **≤5 s** desde el inicio; desmutear → desaparece |
| Grabar hablando normal | presencial | Regresión detector | El banner NUNCA aparece; acta fiel |
| Elegir "Virtual" y CANCELAR el diálogo de compartir | **virtual** | MT-C2 sin fallback | Error accionable (texto Q3), la grabación NO arranca, NO cae a solo-mic |
| Virtual con pestaña compartida pero mic muteado | virtual | MT-C3+C4 ventana 10s + banner pasivo | Aviso ÁMBAR (no rojo) tras ~10 s; grabación sigue |
| Recargar la página tras elegir un modo | ambos | MT-C1 persistencia | El selector recuerda el modo elegido (localStorage por uid) |
| Procesar cualquier grabación | — | MT-C5 tarjeta | Tarjeta "Procesando con IA…" prominente durante el proceso; desaparece al terminar |

Recordar al Director: **reiniciar `./dev.sh`** para cargar el código nuevo antes del E2E. Tras la parte 2 → F6 (auditoría de código con diff íntegro) → F7 (gate G2).
