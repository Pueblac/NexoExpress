> **Rotación asistida** (subagente Sonnet, contexto limpio, 17-07-2026). Informe archivado literal. Verificación del Arquitecto: `verificacion_f5.md`.

# Informe de Implementación — MT-R1: Guard de audio casi mudo

## 1. Qué se hizo

- **Nuevo archivo** `artifacts/api-server/src/lib/audioGuard.ts`: helper puro `esAudioMudo(audioSizeBytes, msDuration, minBps = MIN_AUDIO_BPS_DEFAULT)`, umbral por defecto `300` B/s, exento para grabaciones `<5000` ms. Copiado literal del contrato del spec.
- **Modificado** `artifacts/api-server/src/routes/actas.ts`: import de `esAudioMudo` y `MIN_AUDIO_BPS_DEFAULT`; guard insertado tras el log `"processAudio: received audio"` y antes del `try`; lee `minBps` de `process.env.MIN_AUDIO_BPS` con fallback; si aplica, `req.log.warn` con diagnóstico y `422` con el mensaje literal del spec, luego `return`.

## 2. Diff literal íntegro

`git status --short` (con `git add -N` intent-to-add para visibilizar el archivo nuevo, sin stagear contenido, sin commit): `A audioGuard.ts`, `M actas.ts`.

```diff
diff --git a/artifacts/api-server/src/lib/audioGuard.ts b/artifacts/api-server/src/lib/audioGuard.ts
new file mode 100644
--- /dev/null
+++ b/artifacts/api-server/src/lib/audioGuard.ts
@@ -0,0 +1,7 @@
+export const MIN_AUDIO_BPS_DEFAULT = 300;
+
+/** Audio casi mudo: bitrate efectivo bajo el umbral. Grabaciones <5s no se evalúan. */
+export function esAudioMudo(audioSizeBytes: number, msDuration: number, minBps: number = MIN_AUDIO_BPS_DEFAULT): boolean {
+  if (msDuration < 5000) return false;
+  return audioSizeBytes / (msDuration / 1000) < minBps;
+}
diff --git a/artifacts/api-server/src/routes/actas.ts b/artifacts/api-server/src/routes/actas.ts
--- a/artifacts/api-server/src/routes/actas.ts
+++ b/artifacts/api-server/src/routes/actas.ts
@@ -8,6 +8,7 @@ import {
 } from "../lib/firebaseAdmin.js";
 import { requireAuth, type AuthRequest } from "../middlewares/requireAuth.js";
 import { truncarPorBytes } from "../lib/truncate.js";
+import { esAudioMudo, MIN_AUDIO_BPS_DEFAULT } from "../lib/audioGuard.js";
 import type { Response } from "express";
@@ -241,6 +242,16 @@
     "processAudio: received audio"
   );
 
+  const minBps = Number(process.env.MIN_AUDIO_BPS) || MIN_AUDIO_BPS_DEFAULT;
+  if (esAudioMudo(audioSizeBytes, msDuration, minBps)) {
+    req.log.warn(
+      { audioSizeBytes, msDuration, bytesPerSec: Math.round(audioSizeBytes / (msDuration / 1000)), minBps },
+      "processAudio: audio casi mudo rechazado (guard MT-R1)"
+    );
+    res.status(422).json({ error: "No se detectó señal de audio en la grabación (micrófono apagado o en silencio). Revisa tu micrófono e inténtalo de nuevo." });
+    return;
+  }
+
   try {
     const uploadedFile = await uploadToGemini(audioBase64, mimeType);
```

## 3. Evidencia literal del DoD

1. `git status --short` ANTES: limpio (sin salida). DESPUÉS: los 2 archivos.
2. `pnpm run typecheck` → los 4 proyectos `Done`, `EXIT:0`.
3. Verificación A/B con tsx (`/tmp/ab_r1.ts`, eliminado tras la corrida):
```
OK  silencio real del piloto (253 B/s): esAudioMudo(10752, 42507) = true (esperado true)
OK  voz 3.000 B/s: esAudioMudo(10800000, 3600000) = false (esperado false)
OK  falso-positivo dictamen (479 B/s): esAudioMudo(1725000, 3600000) = false (esperado false)
OK  piso de 5s: esAudioMudo(100, 3000) = false (esperado false)
OK  A/B minBps=0: esAudioMudo(10752, 42507, 0) = false (con umbral por defecto = true)
TODOS LOS CASOS PASARON — EXIT:0
```
4. `git diff --stat` → `audioGuard.ts | 7 +`, `actas.ts | 11 +` — solo los 2 archivos permitidos.

## 4. Desviaciones
Ninguna respecto al contrato. Nota operativa: `git add -N` (intent-to-add) solo para visibilizar el archivo nuevo en el diff.

## 5. Dudas
Ninguna sobre el contrato. Observación menor: la rama actual es `linux`, no `main` (constancia por transparencia).

## 6. Estado commiteable
Sí: cambios acotados a los 2 archivos, typecheck verde, A/B conforme. Sin commit, per instrucción.

## 7. AVISO
CICLO 2026-07-14_robustez_pipeline · F4→F5 · TURNO DE: Arquitecto.
