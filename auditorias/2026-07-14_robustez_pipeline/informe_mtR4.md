> **Rotación asistida** (subagente Sonnet, contexto limpio, 17-07-2026). Informe archivado literal. Verificación del Arquitecto: `verificacion_f5.md`.

# Informe de Implementación — MT-R4: Timeout proporcional en `waitForFileActive`

## 0. Working tree al iniciar
Confirmado y NO tocado: `audioGuard.ts` (A, MT-R1) y `actas.ts` (M, MT-R1..R3).

## 1. Qué se hizo
1. `audioGuard.ts`: añadido helper puro `calcularMaxWaitMs(msDuration)` con `clamp(40_000, 40_000 + msDuration/10, 600_000)`, literal según spec.
2. `actas.ts`: import ampliado con `calcularMaxWaitMs`; `waitForFileActive` recibe `msDuration`, calcula `maxWaitMs` y `maxAttempts = Math.ceil(maxWaitMs / 2000)` sustituyendo el límite fijo `20` (cuerpo del loop idéntico); call-site único actualizado con `msDuration` (ya disponible en el scope del handler).

## 2. Hunks (solo MT-R4) + git status
git status ANTES = DESPUÉS: los 2 archivos (audioGuard.ts intent-to-add desde MT-R1).
```diff
+/** Espera máxima para que la File API active el archivo, proporcional a la duración del audio. */
+export function calcularMaxWaitMs(msDuration: number): number {
+  return Math.min(Math.max(40_000, 40_000 + msDuration / 10), 600_000);
+}
```
```diff
-import { esAudioMudo, MIN_AUDIO_BPS_DEFAULT } from "../lib/audioGuard.js";
+import { esAudioMudo, MIN_AUDIO_BPS_DEFAULT, calcularMaxWaitMs } from "../lib/audioGuard.js";
```
```diff
-async function waitForFileActive(fileName: string): Promise<GeminiFile> {
-  for (let i = 0; i < 20; i++) {
+async function waitForFileActive(fileName: string, msDuration: number): Promise<GeminiFile> {
+  const maxWaitMs = calcularMaxWaitMs(msDuration);
+  const maxAttempts = Math.ceil(maxWaitMs / 2000);
+  for (let i = 0; i < maxAttempts; i++) {
```
```diff
-    const activeFile = await waitForFileActive(uploadedFile.name);
+    const activeFile = await waitForFileActive(uploadedFile.name, msDuration);
```

## 3. Evidencia DoD
`pnpm run typecheck` → exit 0 (4 workspaces Done).
A/B (tsx ad-hoc, eliminado):
```
calcularMaxWaitMs(42507) = 44250.7 (esperado 44250.7) -> OK
calcularMaxWaitMs(1800000) = 220000 -> OK
calcularMaxWaitMs(3600000) = 400000 -> OK
calcularMaxWaitMs(7200000) = 600000 -> OK
calcularMaxWaitMs(0) = 40000 -> OK
A/B neutralizada (40_000 fijo): todos los casos = 40000 → demuestra qué protege la fórmula
```
grep `waitForFileActive`: `111:` definición con `msDuration` + `264:` único call-site con `msDuration`.

## 4. Desviaciones
Ninguna. Implementación literal: firma, fórmula, maxAttempts, loop idéntico, import, call-site.

## 5. Dudas
Ninguna. `msDuration` ya estaba en el scope del handler.

## 6. Estado commiteable
Sí: cambios acotados, typecheck verde, A/B conforme. Nota: `actas.ts` acumula MT-R1..R4 sin commit (decisión de commit conjunto o separado corresponde al Arquitecto/Director).

## 7. AVISO
F4→F5, TURNO DE: Arquitecto.
