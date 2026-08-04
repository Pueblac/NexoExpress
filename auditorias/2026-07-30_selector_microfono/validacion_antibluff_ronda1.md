# Validación anti-bluff del Arquitecto — auditoría de código ronda 1 (selector de micrófono)

**Fecha:** 04-08-2026 · **Valida:** `respuesta_auditoria_ronda1.md` · **Método:** re-lectura del código real (no del diff) y ejecución de trazas.

## 1. Checklist anti-bluff

- **¿Citas reales?** Sí. Todas las citas (+líneas del diff) corresponden a hunks existentes del material incrustado; ninguna referencia a código inexistente. Verificado contra `useAudioRecorder.ts`, `micDevices.ts`, `useMicDevices.ts` y `home.tsx` reales del working tree. ✅
- **¿Trazas mecánicas, no opinión?** Sí en C1..C6, T-a, T-b, T-c y D2/D3/D4. D1 es análisis de riesgo (aceptable como respuesta a duda). ✅
- **¿Veredictos por claim con formato pedido?** Sí, 6/6 CONFIRMADO + 5 trampas resueltas con mecanismo. ✅
- **¿Degeneración a modo chat?** No. Cero elogios, formato contractual. ✅

## 2. Contraste de los 3 BUGs alegados contra el código real

### BUG 1 — Fuga de AudioContext en presencial (T-a): **CONFIRMADO por el Arquitecto** ✅
Traza re-ejecutada sobre `useAudioRecorder.ts` (zona startRecording presencial): si `createMediaStreamDestination`/`createMediaStreamSource`/`connect` lanza DESPUÉS de que el ctx llegó a `running`, el flujo cae al `catch { /* enrutamiento fallido */ }` externo y el único `close()` existente vive en el `else` (estado no-running) — el ctx `running` queda huérfano sin cerrar. Mecanismo exacto, camino real (p. ej. micRaw con tracks en estado inválido). Severidad Media-Alta razonable (tope de AudioContexts por página). **BUG REAL → exige fix y ronda nueva.** (Nota de mérito del proceso: la trampa T-a la plantó el Arquitecto al releer el diff; el Auditor la confirmó con la traza correcta en vez de tragarse el claim C1 tal cual.)

### BUG 2 — Modal huérfano "No se encontraron micrófonos" (T-c): **CONFIRMADO por el Arquitecto** ✅
`home.tsx`: `useMicDevices(isRecording && micSilent)` vacía la lista cuando el silencio se resuelve, pero `micSelectorOpen` es estado independiente → modal abierto renderiza el empty-state técnico. Camino real (señal espontánea con el modal abierto). Severidad Baja correcta. **BUG REAL (UX) → fix trivial.**

### BUG 3 — captureMode desactualizado tras swap desde "system" (T-d): **REFUTADO CON EVIDENCIA** ❌
La premisa del Auditor — "El nivel de audio evaluará a silencio (micSilent=true)" con virtual sin mic — es **falsa**: `useMicLevel.ts:32-35` hace `if (!active || !micStream) { setMicSilent(false); return; }` — con `micStream null` el hook NUNCA produce `micSilent`, el banner no se monta y el CTA/modal son inalcanzables. El "estado que miente" exigiría un swap que no puede dispararse. Coincide con la observación 2 del checklist adversarial de MT-M5 y con Q4 ("upgrade desde system fuera de alcance", dictamen de diseño). Causa del error del Auditor: `useMicLevel.ts` NO venía en el diff (no se tocó en este ciclo) y extrapoló su comportamiento sin el código a la vista — mismo patrón que el T5 refutado del ciclo captura confiable. **NO es bug alcanzable.** Se anota como candidato de defensa-en-profundidad, sin obligación de fix.

## 3. Dudas D1..D4 — evaluación

- **D1 (drift/latencia):** respuesta plausible y honesta (riesgo en máquinas débiles/throttling). Sin acción en este ciclo; queda como observación de monitoreo para reuniones de 1-2 h reales.
- **D2 (vault H6):** mecánicamente correcta — la pista del `dest.stream` no se renegocia; coincide con la verificación F5.1. Cierra la duda.
- **D3 (re-armado):** correcta; coincide con el diseño (re-arme natural, Q3 del dictamen).
- **D4 (toast repetido):** correcta y verificada: `setMicFallbackNotice(null)` al inicio de cada `startRecording` garantiza la transición null→string. Cierra la duda.

## 4. Conclusión

**Anti-bluff: VÁLIDA** (citas y mecanismos verificados; sin código inexistente) **con 1 refutación**: BUG 3 (T-d) cae por evidencia `useMicLevel.ts:32`. Quedan **2 BUGs confirmados**:

1. **Fix A (Media-Alta):** cerrar el AudioContext en el camino de fallo del enrutamiento presencial (mover la creación a variable visible por el catch + `close()` en el fallo).
2. **Fix B (Baja, UX):** cerrar el modal del selector cuando el banner se apaga (o mantener la lista mientras el modal esté abierto — decisión menor de diseño).

**Regla del ciclo: BUG confirmado → F4 (fix) → ronda NUEVA de auditoría.** Turno del Director para decidir el modo del fix (colapso v1 vs Ingeniero) y autorizar la ronda 2.
