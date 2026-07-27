# Validación anti-bluff del Arquitecto — respuesta de diseño ronda 1 (H6)

**Fecha:** 25-07-2026 · **Valida:** `respuesta_diseno_ronda1.md`

## 1. Checklist anti-bluff (revisión de DISEÑO: la base fáctica es el contexto del prompt, verificado previamente contra el código real)

- **¿Citas al contexto reales?** Sí: `:215-217` (chunks solo en memoria) y `:141-155` (useEffect de auto-proceso) son exactamente las líneas del contexto incrustado, que yo verifiqué contra `useAudioRecorder.ts` y `home.tsx` reales antes de enviar. No cita nada fuera del material. ✅
- **¿Recomendación ÚNICA por pregunta?** Sí, las 4: Q1 `lastChunkAt − startedAt` · Q2 purga en ambos puntos + nunca tocar otros uids · Q3 descarte automático solo en error terminal (422), conservar en transitorios · Q4 `STALE_MS = 30 000`. Cero "depende". ✅
- **¿Trampas demostradas con el mecanismo que las neutraliza?** Las 5, cada una anclada a la pieza del diseño (D-C para T1, D-D para T2, D-B para T3, la ruta imperativa de D-E para T4, no-remontaje de Home para T5). ✅
- **¿Coherencia interna de los 5 cambios?** Sin contradicciones: C3-DÉBIL ↔ Q4 ↔ cambio 5 alineados (30 s); Q3 ↔ cambio 4 alineados; Q2 ↔ cambios 2-3 alineados; Q1 ↔ cambio 1 alineados. ✅
- **¿Inventó capacidades no verificables?** El único punto no verificable con lo adjunto es la afirmación de C4 de que Gemini File API acepta webm "live stream" sin Cues — coincide con mi propio análisis y con el precedente empírico del ciclo anterior (webm de MediaRecorder procesado E2E), pero el caso "chunks truncados por crash real" se probará en el DoD E2E de MT-H6c (matar pestaña de verdad). Registrado, no invalida. ⚠️→DoD

**Anti-bluff: VÁLIDA.**

## 2. Los 5 cambios, aceptados e incorporados al diseño congelable

1. **msDuration = `lastChunkAt − startedAt`** (no `chunkCount × 1000`). Nota del Arquitecto: con opus a ~12 KB/s el margen sobre el guard (300 B/s) es ~40×, así que la imprecisión residual de cualquiera de las dos fuentes era inocua; se adopta la del dictamen por ser la más fiel al tiempo real.
2. **Silo por uid**: `listSessions`/`purgeAllExcept` filtran SIEMPRE por uid autenticado; sesiones de otros uids ni se ofrecen ni se borran.
3. **Purga (límite 1) en ambos puntos**: montaje de Home Y `createSession`.
4. **Borrado también en error terminal**: `onError` con HTTP 422 → `deleteSession` (flujo normal y recuperación); errores transitorios (red, 5xx) conservan la sesión.
5. **`STALE_MS = 30 000`**.

## 3. Observación residual del Arquitecto (combinación T2×T5, no cubierta por el dictamen)

Portátil suspendido 1 h con la pestaña A grabando + el usuario abre una pestaña B nueva: para B la sesión de A está stale (lastChunkAt de hace 1 h) → la tarjeta se OFRECE, y si el usuario pulsa "Recuperar" justo cuando A despierta, habría carrera. Mitigación mínima que incorporo a la spec de MT-H6c (endurece D-D sin contradecir el dictamen): **re-verificar el heartbeat en el instante de pulsar "Recuperar"** — si la sesión volvió a latir (lastChunkAt reciente), la tarjeta se retira sin procesar. Escenario de probabilidad baja y la recuperación es ofrecida (decisión G0), nunca automática.

## 4. Conclusión

Veredicto del Auditor: **APROBADO CON CAMBIOS (5)** — anti-bluff VÁLIDA. Diseño congelable = D-A..D-E + los 5 cambios + mitigación T2×T5 del §3. Listo para **G1 del Director** (adopción de diseño); con G1 concedido siguen las specs F3 (MT-H6a..d) y la rotación asistida F4.
