# Validación anti-bluff del Arquitecto — respuesta de auditoría de código ronda 1 (tanda MT-H6a..e)

**Fecha:** 28-07-2026 · **Valida:** `respuesta_auditoria_ronda1.md` · **Método:** citas y textos verificados EJECUTANDO greps y lecturas sobre el código real de ActaExpressWeb (commit `2871a74`, rama `linux`).

## 1. Preguntas de control (detector de bluff) — VERIFICADAS EJECUTANDO

- **Q1a** (texto de la tarjeta con la expresión JSX del cálculo): coincide carácter a carácter con `home.tsx:364-366` (citó 363-366, deriva ±1). ✅
- **Q1b** (toast del re-check): coincide carácter a carácter con `home.tsx:225` (citó 223, deriva ±2). ✅
- **Q1c** (comentario del catch del poll): coincide con `home.tsx:113` (citó 114, deriva ±1). ✅
- **Q2** (purga concurrente durante appendChunk): traza correcta — `tx.abort()` + throw en `recordingVault.ts:130-134`, catch del llamador apaga el vault (`useAudioRecorder.ts:247-248`), RAM intacta. ✅
- **Q3** (apagado del poll): orden cleanup→re-ejecución→guarda temprana correcto contra `home.tsx:106,117-121`. ✅
- **Q4** (chunkCount vs realidad): análisis correcto y fino — detectó que la recuperación no usa `chunkCount` (usa `readChunks` + timestamps, `home.tsx:242`), luego la divergencia posible es inocua. ✅

## 2. Citas archivo:línea — muestreo ejecutado

Todas las citas muestreadas existen con derivas de ±1-3 líneas y contenido correcto (esperable: numeró sobre el diff del commit): C1 (`useAudioRecorder.ts:227-238` try/catch, `:245-248` fire-and-forget, cero `deleteSession` — confirmado por grep propio en F5), C4 (`home.tsx:116-121` poll y cleanup, `:222-226` re-check), C5 (`:235-243` ruta imperativa), T1/T5 (`:359` condición de render — cita EXACTA). Ninguna cita a código inexistente. La traza C6 es aritméticamente correcta (detección al cruzar 30 s vía polls de 10 s; payload `msDuration: 45000`).

## 3. El "BUG" de C3 — análisis del Arquitecto

**Qué encontró:** el enunciado del claim C3 decía "Ningún otro punto del código borra sesiones" y el Auditor demostró dos caminos adicionales de borrado: (a) recuperación con `chunks.length === 0` (`home.tsx:229-231` real; citó 228, deriva ±2) y (b) la propia purga límite-1 (`recordingVault.ts:225`).

**Dictamen del Arquitecto: imprecisión del CLAIM (autoría mía al redactar el prompt), NO bug de código.** Ambos caminos son DISEÑO CONGELADO: la purga es literalmente el cambio 3 del dictamen de diseño del propio Auditor, y el borrado de sesiones vacías está en el contrato de `spec_mtH6c.md` (punto 7). El propio Auditor lo reconoce en su veredicto global ("no representa un fallo orgánico sino una imprecisión en el claim"). **Cero cambios de código requeridos → no reabre ronda.** Registrado como lección para futuros prompts: enumerar TODOS los caminos de borrado en el claim, incluidos los internos del módulo.

## 4. Trampas y dudas

- **T1-T5:** las 5 demostradas con citas correctas. Valiosas: T3 confirma que tras quota-llena la tarjeta ofrecería audio PARCIAL sin aviso explícito en UI (observación menor → backlog), y T2 valida que la pérdida por límite-1 con doble crash simultáneo es la decisión G0, no un bug.
- **D1 (OOM base64 en recuperaciones largas):** "aceptable para MVP, ticket al backlog" — acepto; registrado en backlog (streaming/chunked upload futuro).
- **D2 (bucle tarjeta si el descarte falla):** aceptable (fallo excepcional, sin interferencia con grabaciones). Acepto.
- **D3 (pestañas concurrentes):** traza correcta, incluye el caso B-grabando-mientras-A-crashea (tarjeta diferida hasta parar por la condición de render). Acepto.
- **D4 (timing):** cuadra exactamente con lo observado en el E2E. Acepto.

## 5. Veredicto de la validación

**Anti-bluff: VÁLIDA.** Preguntas de control con el contenido real (verificado ejecutando), citas sin código inexistente, trazas con valores concretos, trampas demostradas.

**Veredicto efectivo de la ronda: APROBADO CON OBSERVACIONES, cero bugs de código confirmados** (el único "BUG" es una imprecisión del enunciado de un claim, reconocida como tal por el propio Auditor). Observaciones al backlog: (1) OOM/memoria en recuperaciones de reuniones muy largas (D1), (2) aviso de "audio parcial" cuando la recuperación proviene de un vault truncado por quota (T3). La tanda MT-H6a..e queda lista para **G2 de cierre del Director** → F7 (el código ya está commiteado y pusheado en `2871a74`; falta cierre de expediente + bitácora + ECOSISTEMA_VISION.md).
