# Validación anti-bluff del Arquitecto — respuesta de auditoría ronda 1 (tanda MT-C1..C5)

**Fecha:** 23-07-2026 · **Valida:** `respuesta_auditoria_ronda1.md` · **Método:** greps y lecturas EJECUTADOS sobre el código real de ActaExpressWeb (working tree, rama `linux`), no de memoria.

## 1. Preguntas de control (detector de bluff) — VERIFICADAS EJECUTANDO

- **Q1a** (error virtual cancelado): texto citado por el Auditor coincide **carácter a carácter** con `useAudioRecorder.ts:179`. ✅
- **Q1b** (banner presencial): coincide carácter a carácter con `home.tsx:269`. ✅
- **Q1c** (banner virtual): coincide carácter a carácter con `home.tsx:270`. ✅
- **Q2** (suspended permanente → `micSilent=false` a los 60 s): traza correcta — `useMicLevel.ts:59-62` resetea `lastLoudAt` en cada tick mientras `state !== "running"`. La lectura del Auditor (comportamiento correcto; el guard 422 queda de última defensa) es razonable. ✅
- **Q3** (persistencia): las 3 trazas (`"virtual"`/`null`/`"basura"`) correctas contra el inicializador real de `home.tsx:73-77`, citado textual. ✅
- **Q4** (virtual con mic denegado → `mode="system"`, hook inerte, sin ámbar): traza correcta contra `useAudioRecorder.ts:187-192` y `useMicLevel.ts:32`. Coincide con el diseño G1 (display OK + mic falla → `"system"`). ✅

## 2. Citas archivo:línea — muestreo ejecutado

| Cita del Auditor | Real | Dictamen |
|---|---|---|
| home.tsx:73-77 useState init | 73-77 | ✅ exacta |
| home.tsx:80-83 handler persistencia | 80-83 | ✅ exacta |
| home.tsx:269/270 textos banner | 269/270 | ✅ exactas |
| home.tsx:258-272 bloque banner | 258-272 | ✅ exacta |
| home.tsx:277/285 `disabled={isRecording}` | 281: `disabled={isRecording \|\| processAudio.isPending}` | ⚠️ deriva ±4 y cita incompleta (omite `processAudio.isPending`, que REFUERZA C1). Contenido real → no es bluff |
| useAudioRecorder.ts:174-179 camino virtual-null | 174-182 | ✅ (deriva ±3) |
| useAudioRecorder.ts:161-163 constraints | 162-164 | ✅ (deriva ±1) |
| useAudioRecorder.ts:129 estado micStream / :165 setMicStream / :186 mixMicStream / :188 ternario mode / :146 setMicStream(null) | 129 / 166 / 187 / 192 / 146 | ✅ (derivas ±1-4, contenido correcto) |
| useMicLevel.ts:4 / :60-63 / :89-93 / :32 | 4 / 59-62 / 87-93 / 32 | ✅ (derivas ±1-2) |

Ninguna cita apunta a código inexistente. Derivas dentro del margen tolerado (esperables: el Auditor numeró sobre el diff, no sobre el archivo). La traza C6 es aritméticamente coherente con `SAMPLE_INTERVAL_MS=200` y ventana 5000 ms, y el JSX citado coincide con `home.tsx:259-271`.

## 3. El "BUG" de T5 — REPRODUCCIÓN INTENTADA: **REFUTADO**

**Afirmación del Auditor:** carrera de auth → `Home` se monta con `user === null` → el inicializador fija `"presencial"` y nunca relee localStorage → preferencia pisada en cada arranque limpio. Severidad MEDIA; ordena sub-tarea (useEffect reactivo a `user`).

**Refutación con evidencia (ejecutada por el Arquitecto):**
1. `Home` tiene UN único punto de montaje: `App.tsx:54` — `<Route path="/" component={() => <ProtectedRoute component={Home} />} />` (grep sobre `src/`: ninguna otra referencia a `pages/home`).
2. `ProtectedRoute` (`App.tsx:23-48`): con `loading === true` renderiza un spinner y NO monta `Home` (`App.tsx:33-39`); con `!user` devuelve `null` y NO monta `Home` (`App.tsx:41`). `Home` solo se monta cuando `loading === false && user !== null` — la rama `if (!user) return "presencial"` del inicializador es inalcanzable en la app real (código defensivo).
3. Logout → `user` null → `ProtectedRoute` desmonta `Home`; el siguiente login remonta y el inicializador re-corre con el uid nuevo (persistencia por-uid intacta).
4. **Evidencia empírica:** E2E prueba 5 (23-07, `verificacion_f5.md`) — recarga de página real y el selector RECORDÓ el modo, en ambos sentidos. Si T5 se manifestara, la recarga habría reseteado a "presencial".

**Dictamen:** BUG **NO CONFIRMADO** → según metodología, no reabre ronda ni exige sub-tarea. Nota de contrato: la premisa de T5 dependía de código NO adjunto (`App.tsx`); lo riguroso habría sido `NO VERIFICABLE CON LO ADJUNTO` en vez de `BUG`. La trampa T5 (formulada por el Arquitecto) invitaba a ese análisis, así que se computa como observación menor del Auditor, no como bluff — sus 4 descartes de trampas restantes (T1–T4) están correctamente trazados sobre el material adjunto.

**Acción registrada (no bloqueante, sin ciclo ahora):** el `useEffect` defensivo que sugiere el Auditor solo aportaría si algún día `Home` se montara sin guard; queda anotado como defensa-en-profundidad en el backlog, no como fix de la tanda.

## 4. Opiniones D1–D4

- **D1 (sala callada, falso positivo presencial):** opinión técnicamente fundada (-40 dBFS es plausible como piso). Riesgo real pero acotado por diseño G0: el aviso solo avisa, nunca corta; el costo de un falso positivo es un banner. Ajuste de umbral/calibración → backlog, no bloquea.
- **D2 (throttling):** correcto — la delta con `performance.now()` sigue siendo válida tras throttling; solo se retrasa la visualización. Acepto.
- **D3 (fatiga de alarma):** recomienda botón de descarte. Coincide con mi duda; candidato a mejora UX en ciclo futuro, no bloquea (cambio de diseño post-G1).
- **D4 (≤5 s):** desviación máxima mecánica ≈ 1 tick (200 ms) + jitter. Compatible con el DoD. Acepto.

## 5. Veredicto de la validación

**Anti-bluff: VÁLIDA.** Preguntas de control respondidas con el contenido real (verificado ejecutando), trazas con valores concretos, citas sin código inexistente, NO VERIFICABLE respetado en el resto del material. Única mancha: T5 declarado BUG sobre premisa no adjunta — **refutado con evidencia** (App.tsx + E2E prueba 5).

**Veredicto efectivo de la ronda: APROBADO CON OBSERVACIONES, sin ningún BUG confirmado.** Las observaciones (D1 umbral, D3 descarte, useEffect defensivo) pasan al backlog como pendientes no bloqueantes. La tanda MT-C1..C5 queda lista para **G2 del Director** → F7 (commit en ActaExpressWeb rama `linux` + cierre de expediente + bitácora + ECOSISTEMA_VISION.md).
