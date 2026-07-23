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

## F5 parte 2 — E2E real con el Director (EJECUTADO 23-07-2026)

Entorno: `./dev.sh` reiniciado por el Arquitecto con el código de la tanda (API 8080 `Server listening`, Vite 5173 `ready`). Director ejecutando en Chrome sobre http://localhost:5173. Evidencia: reporte del Director + capturas de pantalla en el chat de la sesión (descritas por prueba).

| # | Prueba | Modo | Qué valida | Resultado |
|---|---|---|---|---|
| 1 | Grabar con mic MUTEADO en el SO | presencial | MT-C3+C4 detector+banner | ✅ **PASA.** Captura a 00:10: banner ROJO con el texto exacto "⚠️ No se detecta señal de tu micrófono — revisa que no esté silenciado en el sistema.", grabación sigue (badge "Solo micrófono", selector deshabilitado). Captura a 00:14 tras desmutear: banner desaparecido solo, grabación intacta. |
| 2 | Grabar hablando normal 15–20 s | presencial | Regresión detector | ✅ **PASA.** El banner nunca apareció. |
| 3 | Elegir "Virtual" y CANCELAR el diálogo de compartir | virtual | MT-C2 sin fallback (corrección H3) | ✅ **PASA.** Captura: timer en 00:00 "Listo para grabar" (la grabación NO arrancó, no cayó a solo-mic) + error accionable con el texto Q3 exacto: "No se capturó audio. Al compartir, asegúrate de seleccionar 'Pestaña de Chrome' y tener activa la casilla 'Compartir audio de la pestaña'." |
| 4 | Virtual con pestaña compartida + mic muteado | virtual | MT-C3+C4 ventana 10 s + banner pasivo | ✅ **PASA.** Captura a 00:12: aviso ÁMBAR (no rojo) "Tu micrófono no aporta señal. Si solo escuchas la reunión está bien; si querías hablar, revisa que no esté silenciado.", badge "Altavoces + micrófono", grabación sigue sin cortarse. |
| 5 | Recargar la página tras elegir un modo | ambos | MT-C1 persistencia | ✅ **PASA.** Virtual → F5 → sigue Virtual; Presencial → F5 → sigue Presencial (localStorage por uid). |
| 6 | Procesar una grabación | — | MT-C5 tarjeta "Procesando con IA…" | ✅ **PASA (23-07).** Captura a 01:18 de proceso: tarjeta prominente "Procesando con IA…" con spinner + texto conservado "Esto puede tardar unos minutos — no cierres esta pestaña" (`text-espera`). Acta generada fiel: el Director grabó una noticia del día (ataque a base en Jordania) y el acta refleja resumen y puntos coherentes (1 min, 1 participante). Tarjeta desaparece al terminar. |

**Nota de precisión (prueba 1):** la primera captura es a 00:10 de grabación; el DoD fino de la ventana de 5 s (banner visible en ≤5 s desde el inicio) queda pendiente de confirmación verbal del Director — el diseño lo garantiza por `MIC_SILENT_WINDOW_PRESENCIAL_MS=5000` con muestreo ~200 ms. Se traslada como observación a la auditoría F6.

## Veredicto F5 COMPLETO (23-07-2026)

**F5 parte 1 (código) + parte 2 (E2E de 6 pruebas): APROBADO por el Arquitecto.** Las 5 MTs funcionan end-to-end en el navegador real del Director; la corrección de H3 (sin fallback silencioso) y H4 (banner en los primeros segundos) verificadas con capturas. Único cabo suelto: confirmación verbal del instante exacto (≤5 s) de aparición del banner en presencial — registrado como observación para F6, no bloquea.

Siguiente: F6 (auditoría de código con diff íntegro, incluyendo `useMicLevel.ts` completo por ser untracked) → F7 (gate G2).
