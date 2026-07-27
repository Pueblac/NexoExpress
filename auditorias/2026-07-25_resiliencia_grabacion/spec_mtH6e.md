# Spec MT-H6e — Re-chequeo periódico de huérfanas (F3′, fix del E2E de F5)

**Ciclo:** 2026-07-25_resiliencia_grabacion · F3′→F4 · **Rol:** Ingeniero (Sonnet, rotación asistida)
**Origen:** BUG de comportamiento encontrado por el Director en el E2E de F5 parte 2 (27-07): tras cerrar la pestaña grabando y reabrir, la tarjeta de recuperación NO aparece sola — solo tras remontar Home (navegar a un acta y volver). Causa raíz confirmada por el Arquitecto: el chequeo corre UNA vez al montar (`home.tsx:101-106`) y en ese instante la sesión todavía no es stale (`VAULT_STALE_MS = 30000` es intocable, dictamen cambio 5).
**Repo:** `/home/pueblac/AndroidStudioProjects/ActaExpressWeb`. Arranca sobre el working tree con la tanda MT-H6a..d aplicada (3 archivos M/??; NO debe haber nada más).

## Objetivo
Que la tarjeta aparezca SOLA, sin navegación del usuario: re-chequear huérfanas periódicamente hasta encontrar una. Latencia máxima aceptada: ~40 s tras el crash (30 s de stale + 10 s de poll).

## Contrato
1. Modificar SOLO `artifacts/acta-express/src/pages/home.tsx`, reemplazando el useEffect de detección actual (`:100-106`) por:
```ts
const ORPHAN_POLL_MS = 10000; // constante de módulo, junto a los imports o encima del componente

// H6c+H6e: detección de sesión huérfana — al montar y re-chequeo periódico
// (la sesión del crash tarda VAULT_STALE_MS en volverse stale; sin poll, la
// tarjeta solo aparecía al remontar Home — bug del E2E 27-07).
useEffect(() => {
  if (!user || !isVaultAvailable() || orphanSession) return;
  let cancelled = false;
  const check = () => {
    purgeStaleKeepNewest(user.uid)
      .then((orphan) => {
        if (!cancelled && orphan) setOrphanSession(orphan);
      })
      .catch(() => {}); // vault roto → sin tarjeta, app intacta
  };
  check();
  const intervalId = window.setInterval(check, ORPHAN_POLL_MS);
  return () => {
    cancelled = true;
    window.clearInterval(intervalId);
  };
}, [user?.uid, orphanSession]);
```
2. Semántica exacta: el poll corre mientras NO haya huérfana detectada; al encontrarla se detiene (la dep `orphanSession` re-ejecuta el efecto, que retorna temprano). Si el usuario Descarta o Recupera (orphanSession vuelve a null), el poll se reactiva solo — correcto: podría haber quedado otra huérfana más antigua NO (la purga conserva solo 1), pero el poll reactivado es inocuo e idempotente.
3. NO añadir guardas de `isRecording`/`isPending` al poll: la sesión de una grabación en curso late (no es stale) y `purgeStaleKeepNewest` la ignora por diseño; la tarjeta ya está condicionada a `!isRecording && !processAudio.isPending` en el render. No tocar nada más del archivo.

## Restricciones
Solo `home.tsx` (el bloque indicado + la constante). NO tocar `recordingVault.ts`, `useAudioRecorder.ts`, `VAULT_STALE_MS`, ni la tarjeta ni los handlers. Sin dependencias nuevas. No commit.

## DoD (salida literal al informe)
1. `pnpm run typecheck` → exit 0.
2. `grep -n "ORPHAN_POLL_MS\|setInterval(check" artifacts/acta-express/src/pages/home.tsx`.
3. **A/B razonado con timeline** citando líneas del diff: crash en t=0 (último chunk t=−1 s) → reapertura en t=5 s → check del montaje en t≈5 s: sesión NO stale (delta 6 s < 30 s) → sin tarjeta; polls en t≈15 s, 25 s: sin tarjeta; poll en t≈35 s: delta 36 s ≥ 30 s → `setOrphanSession` → tarjeta visible SIN navegación. Y el caso viejo (código anterior): mismo timeline → tarjeta jamás aparece (demostración del bug).
4. **A/B del apagado del poll:** al setear `orphanSession`, el efecto se re-ejecuta y retorna temprano → interval limpiado (citar el cleanup).
5. `git diff artifacts/acta-express/src/pages/home.tsx` → SOLO el bloque del efecto + constante. Diff literal íntegro al informe.

## Protocolo de dudas
`ORPHAN_POLL_MS = 10000` y `VAULT_STALE_MS = 30000` son FIJOS. Cualquier duda que exija cambiar el contrato → DETENTE y decláralo sin implementar.

## Informe: `informe_mtH6e.md` — formato estándar (qué se hizo / diff literal íntegro / evidencia DoD literal / desviaciones / dudas / estado commiteable).
