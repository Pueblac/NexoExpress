# Spec MT-H6d — Endurecimiento y verificación adversarial del vault (H6)

**Ciclo:** 2026-07-25_resiliencia_grabacion · F4 · **Rol:** Ingeniero (Sonnet, rotación asistida)
**Diseño aprobado:** r1 APROBADO CON CAMBIOS + G1 (25-07). Esta MT cierra la tanda: audita ADVERSARIALMENTE lo implementado en MT-H6a..c contra el diseño congelado, corrige los huecos que encuentres (fix mínimo dentro del alcance) y deja la evidencia A/B.
**Repo:** `/home/pueblac/AndroidStudioProjects/ActaExpressWeb`. Arranca sobre el working tree con **MT-H6a + H6b + H6c aplicadas** (3 archivos tocados: `recordingVault.ts` nuevo, `useAudioRecorder.ts`, `home.tsx`). Puedes tocar ESOS TRES archivos, nada más.

## Objetivo
Que las garantías del diseño no sean prosa: verificarlas contra el código real con trazas ejecutadas mentalmente línea a línea, y parchear lo que falle. La regla de oro a proteger: **la grabación jamás falla por culpa del vault** y **una sesión viva jamás se purga**.

## Checklist adversarial (ejecutar TODAS; cada una con veredicto PASA/FALLA+fix)
1. **Entorno sin IndexedDB** (`isVaultAvailable() === false`): traza `startRecording` completa → cero llamadas al vault, cero rechazos sin catch, grabación idéntica a la actual. Y en `home.tsx`: el useEffect de montaje retorna sin tocar el vault.
2. **QuotaExceeded a mitad de grabación**: `appendChunk` rechaza en seq N → `vaultDisabledRef=true`, seqs siguientes ni se intentan, `chunksRef` (memoria) completo, stop→blob→base64→acta intactos. ¿Hay ALGÚN camino donde un rechazo del vault llegue sin catch a la consola como unhandled rejection? (busca cada llamada: `createSession`, `appendChunk`, `purgeStaleKeepNewest`, `getSession`, `readChunks`, `deleteSession` — TODAS deben tener `.catch` o `try/catch` en su sitio de llamada, salvo las await del handler Recuperar que ya especifica catch).
3. **Silo por uid**: traza `purgeStaleKeepNewest("u1")` con sesiones stale de u1 y u2 → las de u2 intactas. ¿`listSessions`/purga filtran por uid en TODOS los caminos?
4. **Límite-1 real**: 3 sesiones stale de u1 (lastChunkAt t1<t2<t3) → sobreviven SOLO la de t3; se borra sesión+chunks de t1 y t2 (verifica que los chunks huérfanos no queden — fuga de disco).
5. **Sesión viva intocable (T2)**: sesión de u1 con `lastChunkAt` hace 2 s (< 30 000) → ni se ofrece ni se purga, con la pestaña B montando Home en ese instante.
6. **Re-check al Recuperar (T2×T5)**: sesión stale al montar que vuelve a latir antes del click → el handler sale con toast sin procesar. Cita las líneas exactas.
7. **Doble borrado benigno**: `deleteSession(id)` sobre sesión ya borrada (carrera central-vs-per-call en MT-H6c) → debe resolver sin lanzar (IndexedDB `delete` sobre clave inexistente resuelve OK; verifica que el código no añada un rechazo artificial, p. ej. un check de existencia que lance).
8. **`msDuration` correcto**: el payload de recuperación usa `lastChunkAt − startedAt` (cambio 1), con piso 1000 ms.

## Contrato de fixes
Cada FALLA del checklist → fix MÍNIMO en el archivo correspondiente, declarado en el informe con su traza antes/después (A/B). Si un fix exigiera cambiar el diseño congelado (firmas, política de borrado, umbrales) → DETENTE y decláralo sin implementar.

## Restricciones
Solo los 3 archivos de la tanda. Sin dependencias nuevas. No commit. NO añadir features (ni botones, ni configuraciones): esto es endurecimiento.

## DoD (salida literal al informe)
1. `pnpm run typecheck` → exit 0.
2. Tabla checklist 1–8 con veredicto PASA (cita archivo:línea de la garantía) o FALLA→FIX (diff del fix + traza A/B).
3. `grep -n "\.catch\|try {" artifacts/acta-express/src/hooks/useAudioRecorder.ts artifacts/acta-express/src/pages/home.tsx | grep -i -c "" ` — o equivalente: evidencia de que TODA llamada al vault tiene manejo de error (lista llamada→línea del catch).
4. `git diff --stat` final de la TANDA COMPLETA (los 3 archivos) + diff literal íntegro de los cambios PROPIOS de esta MT (si no hubo fixes, decláralo: "checklist 8/8 PASA, cero cambios").

## Protocolo de dudas
Ambigüedad entre "fix mínimo" y "cambio de diseño": si el fix cabe sin tocar firmas ni política, hazlo y decláralo; si no, DETENTE. No reinterpretes umbrales ni textos.

## Informe: `informe_mtH6d.md` — formato estándar (qué se hizo / tabla checklist / diffs de fixes / evidencia DoD literal / desviaciones / dudas / estado commiteable).
