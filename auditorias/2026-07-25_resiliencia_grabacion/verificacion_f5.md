# Expediente 2026-07-25_resiliencia_grabacion — Verificación F5 del Arquitecto (tanda MT-H6a..d)

**Fecha:** 25-07-2026 · **Modo:** rotación asistida (4 subagentes Sonnet secuenciales, contexto limpio cada uno, working tree encadenado). Informes literales en `informe_mtH6a.md` … `informe_mtH6d.md`.
**Incidencia de la rotación (registrada):** el subagente de MT-H6b quedó pausado a mitad por una activación del modo Plan del harness (código ya aplicado, DoD pendiente); se reanudó con aprobación del Director sin reabrir el código. Cero impacto en el contenido.

## DoD re-EJECUTADO por el Arquitecto (no leído de los informes)

1. **`git status --short`** → exactamente 3 paths: `useAudioRecorder.ts` (M), `home.tsx` (M), `recordingVault.ts` (?? nuevo, 227 líneas). Coincide con los 4 informes. ✅
2. **`pnpm run typecheck`** re-ejecutado → los 4 proyectos `Done`, `TYPECHECK_EXIT=0`. ✅
3. **Marcadores por MT sobre el código real (grep + lectura):**
   - MT-H6a: `VAULT_STALE_MS = 30000` (recordingVault.ts:17, cambio 5), stores con keyPath `sessionId` (:72) y compuesta `["sessionId","seq"]` (:75), `isStale` puro (:205), `purgeStaleKeepNewest` que SOLO purga stale y conserva la más reciente — las vivas intocables, T2 (:217-226), `deleteSession` atómico sesión+chunks (:192-198), `appendChunk` con heartbeat y chunkCount en la MISMA transacción + abort si la sesión no existe (:130-147). ✅
   - MT-H6b: imports del vault (useAudioRecorder.ts:3), `vaultSessionId` expuesto (:19, :134), `createSession` entre `new MediaRecorder` y `start(1000)` con el mimeType real (:227-239), purga límite-1 al crear (:236, cambio 3), `appendChunk` fire-and-forget con catch que apaga el vault (:245-248), **grep de `deleteSession` en el recorder: SIN RESULTADOS** (prohibición cumplida — el borrado solo vive en home). ✅
   - MT-H6c: `export function blobToBase64` (useAudioRecorder.ts:22); detección al montar vía `purgeStaleKeepNewest` con catch (home.tsx:101-106); borrado central en acta-OK (:112) y en 422 (:142, cambio 4); handler Recuperar con **re-check heartbeat T2×T5** (:207-212), chunks vacíos → borrar+salir (:213-219), `msDuration = lastChunkAt − startedAt` piso 1000 (:227, cambio 1), per-call onSuccess/onError con política 422-borra/red-conserva (:231-242); tarjeta `card-recuperacion` + `btn-recuperar`/`btn-descartar` solo con `orphanSession && !isRecording && !isPending` (:344-371); ruta imperativa con `audioBase64Recuperado` local — no toca el estado del hook ni `lastProcessedAudioRef` → el useEffect de auto-proceso (:161-177) no puede re-disparar (T4). ✅
   - MT-H6d: checklist adversarial 8/8 PASA, cero fixes (informe con citas); verificado por el Arquitecto por muestreo: los call sites del vault en recorder y home tienen todos `.catch`/`try-catch`. ✅
4. **Contraste informes vs realidad (anti-bluff interno):** cero discrepancias; cero desviaciones no declaradas; cero dudas en los 4 informes.

**Veredicto F5 parte 1 (código): las 4 MTs FIELES al diseño congelado en G1** (D-A..D-E + los 5 cambios del dictamen + mitigación T2×T5). Typecheck verde, alcance cerrado (frontend, 3 archivos), sin dependencias nuevas.

## Pendiente F5 parte 2 — E2E real con el Director

| # | Prueba | Qué valida | Resultado esperado |
|---|---|---|---|
| 1 | Grabar ~1 min hablando (presencial) y **CERRAR la pestaña sin parar** (Ctrl+W) → reabrir la app | Núcleo de H6 (MT-H6a+b+c) | Tarjeta "Se encontró una grabación interrumpida (~1 min)" → **Recuperar** → tarjeta "Procesando con IA…" → **acta fiel a lo hablado** |
| 2 | Repetir con grabación corta → reabrir → **Descartar** | Descarte | Tarjeta desaparece; recargar de nuevo → NO reaparece (vault vacío) |
| 3 | Grabar y parar NORMAL → acta OK → recargar página | Limpieza en caso feliz (D-C) | NUNCA aparece tarjeta (sesión borrada en onSuccess); flujo normal idéntico al de siempre |
| 4 | Con la pestaña A grabando, abrir la app en una **pestaña B** | T2 sesión viva | B NO muestra tarjeta de recuperación (heartbeat late) |
| 5 | Durante una grabación: DevTools → Application → IndexedDB → `actaexpress-vault` | Persistencia al vuelo (MT-H6b) | Chunks creciendo ~1/s en el store `chunks`; sesión en `sessions` con `lastChunkAt` avanzando |
| 6 | (Opcional) Mic muteado ~40 s → cerrar pestaña → reabrir → Recuperar | 422 terminal (cambio 4) | El server rechaza (422) → la tarjeta desaparece y NO reaparece tras recargar (sin bucle) |

Recordar: **reiniciar `./dev.sh`** antes del E2E (lo hace el Arquitecto). Tras la parte 2 → F6 (auditoría de código con diff íntegro + `recordingVault.ts` completo por ser untracked) → F7 (gate G2).

## E2E ronda 1 (27-07) — resultado parcial y fix F3′

**Ejecutado por el Director.** Hallazgos:
- **Núcleo VALIDADO:** recuperación tras cierre real de pestaña → acta FIEL a lo hablado (captura); Descartar funciona con toast "Grabación descartada" (captura); tarjeta con texto y estimación correctos; persistencia del selector intacta tras el crash.
- **BUG confirmado (bloqueante):** la tarjeta NO aparecía sin navegar — el chequeo corría una sola vez al montar (`home.tsx:101-106` versión previa) cuando la sesión aún no cumplía los 30 s de stale; solo un remontaje de Home (entrar a un acta y volver) la hacía aparecer. Reproducido en pruebas 1 y 2.
- **Fix MT-H6e (F3′ → F4 → F5):** `spec_mtH6e.md` + `informe_mtH6e.md`. Re-chequeo periódico `ORPHAN_POLL_MS = 10000` hasta detectar huérfana, con apagado del poll al encontrarla y cleanup correcto. Verificado por el Arquitecto: typecheck exit 0 re-ejecutado, lectura del bloque (`home.tsx:49`, `:105-121`). Latencia máxima esperada de aparición: ~40 s tras el crash (30 s stale del dictamen + 10 s de poll) — el umbral de 30 s es intocable sin re-auditar (cambio 5).
- **Hallazgos NUEVOS registrados (fuera de tanda, ciclo propio):** (a) **bug PREEXISTENTE** del botón borrar en la lista de actas: navega al acta en vez de (solo) borrar — el trigger `home.tsx:495` hace `stopPropagation` sin `preventDefault` dentro del `<Link>`; el diff de la tanda no toca esa zona; (b) **dirección de producto:** "Continuar reunión" desde un acta (anexar audio a un acta existente tras un corte) — candidata a ciclo propio, toca pipeline.

**Pendiente: E2E ronda 2** — repetir las 6 pruebas de la tabla, esperando hasta ~40 s la aparición automática de la tarjeta (sin navegar).
