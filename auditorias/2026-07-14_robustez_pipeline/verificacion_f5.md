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

## F5 parte 2 — E2E real EJECUTADO con el Director (17-07-2026, ~10:21–10:52)

Servidor reiniciado con `./dev.sh` antes de las pruebas (código nuevo cargado, build fresco 10:50:33). Evidencia: capturas de UI del Director + log literal del terminal del API server (pegado en la sesión del Arquitecto, contrastado por él).

### Prueba (a) — mic MUTEADO ~30s → guard MT-R1: ✅ PASA

- Toast rojo en UI: "HTTP 422 Unprocessable Entity: No se detectó señal de audio en la grabación (micrófono apagado o en silencio). Revisa tu micrófono e inténtalo de nuevo." Sin acta nueva en la lista.
- Log literal: `WARN processAudio: audio casi mudo rechazado (guard MT-R1)` con `audioSizeBytes: 8106, msDuration: 31939, bytesPerSec: 254, minBps: 300` → `statusCode: 422, responseTime: 292`.
- Contraste del Arquitecto: 254 B/s clava el perfil de silencio real del diseño (~253 B/s, CTX-1); rechazo en 292 ms **sin upload a File API ni inferencia** (0 tokens gastados) — objetivo de H1 cumplido.
- Observación de producto del Director durante la prueba: el aviso debería llegar AL INICIO de la grabación, no al procesar (evitar grabar 1h en vano). Ya cubierto por el hallazgo **H4** (detector de micrófono en cliente vía AnalyserNode), ciclo siguiente "Captura confiable" — NO se toma en esta tanda.

### Prueba (b) — grabación real 56s, mic integrado, toggle ON, guión como ground truth: ✅ PASA (MT-R5 confirmada aparte)

- **MT-R3:** log literal `sintesis: respuesta de Gemini recibida` con `thoughtsTokenCount: 1145` ≤ 4096 (antes del fix: 62.912; −98%). `finishReason: "STOP"` en acta y síntesis (sin MAX_TOKENS). Acta: 472 thoughts.
- **Fidelidad (regresión H1):** acta `rFqr24fvZjqoYB96cYur` "Reunión de Sincronización del Proyecto Nexo Express" contrastada por el Arquitecto contra el guión leído: resumen, 3 puntos, 1 acuerdo y 2 pendientes con responsable/fecha correctos (Carlos/hoy en la tarde; equipo de diseño/mañana a primera hora). Cero invenciones; 4 participantes = entidades mencionadas en el audio.
- **Síntesis:** `sintesis: guardada en Firestore` con `transcripcionChars: 1111` — coherente con el guión (~1.100 chars en 56s). (Visor de UI: fuera de tanda.)
- **Regresión MT-R1:** 880,2 KB / 55,96 s ≈ 15.731 B/s ≫ 300 — sin falso positivo con voz real.
- **Regresión MT-R4:** presupuesto `calcularMaxWaitMs(55958)` ≈ 45,6 s; archivo ACTIVE en ~1 s. Sin timeout.
- **MT-R5 (mensaje de espera): ✅ CONFIRMADA** — captura del Director durante el procesamiento: "Esto puede tardar unos minutos — no cierres esta pestaña." visible bajo "Procesando con IA...", círculo con spinner; desaparece al resolverse la mutación.
- Observación de UX del Director (fuera de tanda, registrada): el mensaje se ve pequeño — mejorar jerarquía visual del estado de procesamiento (cuadro más prominente / indicador de "pensando"). Candidata a MT trivial post-ciclo o a integrarse en el ciclo "Captura confiable".

**Veredicto F5 COMPLETA (17-07-2026): las 5 MTs verificadas — parte 1 (código: A/B, greps, typecheck) + parte 2 (E2E real: MT-R1, MT-R3, MT-R5 observadas; regresiones de fidelidad, guard y timeout limpias). Cero desviaciones.** → F6 (prompt de auditoría de la tanda con diff íntegro) → F7 (gate G2).
