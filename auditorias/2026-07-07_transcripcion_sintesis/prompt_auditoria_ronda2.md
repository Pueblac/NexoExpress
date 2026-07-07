# Expediente 2026-07-07_transcripcion_sintesis — Prompt de auditoría de CÓDIGO (ronda 2)

**Ciclo:** Re-auditoría tras BUG confirmado en ronda 1 (D1: truncado por caracteres vs bytes). **Alcance: SOLO el fix D1 y la no-regresión.** Los claims C1–C5, C7 y C8 de la ronda 1 conservan su dictamen CONFIRMADO y no se re-litigan.

## Instrucciones de operación para el Director

1. Conversación **NUEVA** en Gemini 3.1 Pro High (no continuar el hilo de la ronda 1).
2. **Adjuntar EXACTAMENTE estos 3 archivos**:
   - `ActaExpressWeb/artifacts/api-server/src/lib/truncate.ts` (nuevo)
   - `ActaExpressWeb/artifacts/api-server/src/routes/actas.ts` (modificado)
   - `NexoExpress/auditorias/2026-07-07_transcripcion_sintesis/evidencia_fix_d1.md`
3. Pegar como primer mensaje lo que está entre `=== PROMPT ===`.
4. Guardar la respuesta TAL CUAL como `respuesta_auditoria_ronda2.md` en esta carpeta y avisar al Ingeniero.

---

=== PROMPT ===

# Rol y regla de oro
Eres auditor adversarial de código del ecosistema Express, en RONDA 2 de re-auditoría. En la ronda 1 confirmaste un BUG: el truncado de la transcripción operaba en caracteres UTF-16 (`.slice(0, 800000)`) mientras el límite de Firestore (1 MiB por documento) es en BYTES; exigiste refactorizar con `Buffer.byteLength`. El implementador afirma haberlo corregido. **Tu hipótesis de trabajo es que el fix está mal, incompleto, o rompió algo que antes funcionaba.** No agradezcas, no resumas, no elogies. Cada afirmación sin cita textual del material adjunto (archivo:línea) se considera inventada.

# Formato obligatorio de CADA verificación
CLAIM → EVIDENCIA (cita textual, archivo:línea) → TRAZA (ejecución simbólica con valores concretos) → VERDICTO (CONFIRMADO / BUG / NO VERIFICABLE CON LO ADJUNTO).

# Material adjunto
1. `truncate.ts` — helper puro nuevo `truncarPorBytes`.
2. `actas.ts` — integración del helper en `generarSintesisEnBackground`.
3. `evidencia_fix_d1.md` — salida literal del test A/B ejecutado y de la regresión E2E.

# Claims a verificar
- **C1 — Truncado por bytes correcto.** `truncarPorBytes(texto, maxBytes, sufijo)` garantiza que `Buffer.byteLength(resultado, "utf8") <= maxBytes` para TODA entrada, incluyendo: (a) texto que ya cabe (retorna intacto, sin sufijo), (b) texto multibyte masivo (CJK/emoji), (c) corte que cae en medio de un carácter multibyte (el U+FFFD del decode se elimina antes de concatenar el sufijo). Traza los tres casos con valores concretos de bytes.
- **C2 — Integración fiel.** `actas.ts` reemplazó la lógica vieja por `truncarPorBytes(parsed.transcripcion, SINTESIS_MAX_BYTES, SINTESIS_TRUNC_SUFFIX)` con `SINTESIS_MAX_BYTES = 800_000` (ahora en BYTES), y no queda NINGUNA referencia a la constante ni a la lógica vieja por caracteres.
- **C3 — Prueba A/B válida.** Según `evidencia_fix_d1.md`: el helper real compilado reduce una entrada de 2.828.584 bytes a ≤800.000 con sufijo y sin U+FFFD; y la lógica vieja neutralizada produce 2.200.056 bytes (>1 MiB), es decir, el test FALLA sin el fix (no es un test falso-positivo).
- **C4 — No-regresión.** El flujo E2E completo con el fix integrado siguió funcionando (201 + documento `sintesis/` real con transcripción íntegra de 492 chars, muy por debajo del límite → sin truncar y sin sufijo).

# Dudas declaradas por el implementador
- **D1:** `presupuesto = maxBytes - byteLength(sufijo)`: si alguien llamara al helper con `maxBytes` menor que el tamaño del sufijo (~57 bytes), `subarray(0, negativo)` produce buffer vacío y el resultado sería solo el sufijo (~57 bytes ≤ maxBytes solo si maxBytes ≥ 57; con maxBytes < 57 el resultado EXCEDE maxBytes). En producción `maxBytes` es la constante 800_000, así que lo considero teórico — ¿observación o exige guard?
- **D2:** el regex `/�+$/` elimina U+FFFD solo al FINAL del corte. Si la transcripción legítima contuviera U+FFFD exactamente en el punto de corte, se borrarían de más (pérdida de unos pocos chars legítimos). Lo considero cosmético e indistinguible del caso real.

# Preguntas de control (respóndelas TODAS)
- **Q1:** Copia textualmente el cuerpo completo de `truncarPorBytes` con números de línea.
- **Q2:** Traza `truncarPorBytes("ñ".repeat(10), 12, "!")`: cada `ñ` son 2 bytes (20 bytes total > 12). Calcula presupuesto, el contenido del subarray, si hay U+FFFD, y el resultado final exacto con su byteLength.
- **Q3:** ¿En qué línea exacta de `actas.ts` se invoca ahora el helper y qué se hace con el resultado?

# Anti-aprobación-automática
Si apruebas, demuestra por qué estas trampas NO aplican:
- **T1:** El sufijo mismo contiene caracteres multibyte (Ó en "TRANSCRIPCIÓN") — ¿su byteLength está descontado del presupuesto o el resultado puede exceder maxBytes por el sufijo?
- **T2:** Entrada vacía o más corta que el sufijo → ¿el helper retorna algo coherente sin lanzar?
- **T3:** El test A/B de `evidencia_fix_d1.md` — ¿prueba el código REAL compilado desde `truncate.ts` o una copia reimplementada? Verifica contra la descripción del método de compilación.

# Entregable final
1. Tabla C1..C4 con verdictos. 2. Respuestas Q1..Q3. 3. Refutación T1..T3 si apruebas. 4. Postura sobre D1..D2. 5. Veredicto global (APROBADO / APROBADO CON OBSERVACIONES / RECHAZADO).

**Formato de entrega:** redacta TODA tu respuesta como un único documento markdown listo para archivar tal cual (será guardado como `respuesta_auditoria_ronda2.md` sin edición). Sin citas archivo:línea o sin trazas = INVÁLIDA.

=== FIN PROMPT ===
