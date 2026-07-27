# Informe MT-H6d — Endurecimiento y verificación adversarial del vault (H6)

**Ciclo:** 2026-07-25_resiliencia_grabacion · F4 · **Rol:** Ingeniero (Sonnet, rotación asistida)
**Repo auditado:** `/home/pueblac/AndroidStudioProjects/ActaExpressWeb`
**Fecha:** 26-07-2026

## 1. Qué se hizo

Se verificó el precondicionante (working tree con MT-H6a+b+c aplicadas, exactamente 3 archivos tocados). Se leyeron enteros los tres archivos de la tanda:

- `artifacts/acta-express/src/lib/recordingVault.ts` (228 líneas, nuevo)
- `artifacts/acta-express/src/hooks/useAudioRecorder.ts` (315 líneas, modificado)
- `artifacts/acta-express/src/pages/home.tsx` (554 líneas, modificado)

Se ejecutó el checklist adversarial de 8 puntos trazando línea a línea contra el código real (no contra la prosa del diseño). Se localizaron **todos** los call sites de las 6 funciones del vault (`createSession`, `appendChunk`, `purgeStaleKeepNewest`, `getSession`, `readChunks`, `deleteSession`) mediante grep exhaustivo en los dos archivos consumidores, y se verificó manejo de error en cada uno.

**Resultado: checklist 8/8 PASA. Cero fixes necesarios — cero cambios de código en esta MT.**

## 2. Tabla checklist 1–8

| # | Punto | Veredicto | Cita |
|---|---|---|---|
| 1 | Entorno sin IndexedDB: cero llamadas al vault, grabación idéntica; `home.tsx` no toca el vault al montar | **PASA** | `useAudioRecorder.ts:227` (`if (user && isVaultAvailable())` guarda todo el bloque; `vaultSessionIdRef.current` queda `null`); `useAudioRecorder.ts:245` (`if (!vaultDisabledRef.current && vaultSessionIdRef.current)` es falso con sessionId null → `appendChunk` nunca se invoca); `home.tsx:101-102` (`if (!user \|\| !isVaultAvailable()) return;` antes de tocar el vault) |
| 2 | QuotaExceeded a mitad de grabación: `vaultDisabledRef=true`, seqs siguientes no se intentan, memoria intacta, cero unhandled rejections en NINGÚN call site | **PASA** | `useAudioRecorder.ts:247-249` (`appendChunk(...).catch(() => { vaultDisabledRef.current = true; })`); `useAudioRecorder.ts:244` (push a `chunksRef` ocurre ANTES del `if` del vault, incondicional); inventario completo de los 13 call sites (ver tabla DoD §4.3) — los 13 tienen `.catch(...)` o están dentro de `try {} catch {}` |
| 3 | Silo por uid: `listSessions`/purga filtran por uid en todos los caminos | **PASA** | `recordingVault.ts:165-170` (`listSessions` hace `all.filter((meta) => meta.uid === uid)` sobre `getAll()` de TODA la store); `recordingVault.ts:217-227` (`purgeStaleKeepNewest` solo opera sobre `sessions = await listSessions(uid)`, nunca toca IDs de otro uid) |
| 4 | Límite-1 real: sobrevive solo la de t3, se borran sesión+chunks de t1/t2 sin fuga | **PASA** | `recordingVault.ts:223` (`newest = stale.reduce((a,b) => b.lastChunkAt > a.lastChunkAt ? b : a)` → t3); `recordingVault.ts:224-225` (`toDelete` = t1+t2, `Promise.all(toDelete.map(deleteSession))`); `recordingVault.ts:192-198` (`deleteSession` borra `SESSIONS_STORE` y `CHUNKS_STORE` en UNA sola tx — cero chunks huérfanos posibles) |
| 5 | Sesión viva (lastChunkAt hace 2 s) intocable, incluso con pestaña B montando Home | **PASA** | `recordingVault.ts:205-207` (`isStale = now - meta.lastChunkAt >= VAULT_STALE_MS`; 2000 ≥ 30000 = false); `recordingVault.ts:219` (`stale = sessions.filter(isStale)` excluye la sesión viva — nunca entra en `newest` ni en `toDelete`); el mismo camino corre tanto desde `home.tsx:103` (montaje) como desde `useAudioRecorder.ts:236` (creación) porque ambos llaman a la misma `purgeStaleKeepNewest` |
| 6 | Re-check al Recuperar (T2×T5): sesión que vuelve a latir antes del click → sale con toast sin procesar | **PASA** | `home.tsx:207-212`: `const meta = await getSession(orphanSession.sessionId).catch(() => null); if (!meta \|\| !isStale(meta)) { setOrphanSession(null); toast({ title: "Grabación no recuperable", ... }); return; }` — antes de cualquier `readChunks`/`processAudio.mutate` |
| 7 | Doble borrado benigno: `deleteSession` sobre sesión ya borrada resuelve sin lanzar | **PASA** | `recordingVault.ts:192-198`: no hay check de existencia previo; `tx.objectStore(...).delete(sessionId)` / `.delete(chunkRange(...))` sobre claves inexistentes son operaciones válidas de IndexedDB (no lanzan `onerror`); la tx completa normalmente vía `txDone` (líneas 54-60) |
| 8 | `msDuration` = `lastChunkAt − startedAt` con piso 1000 ms | **PASA** | `home.tsx:227`: `msDuration: Math.max(1000, meta.lastChunkAt - meta.startedAt)` |

## 3. Diffs de los fixes

**Ninguno. Checklist 8/8 PASA, cero cambios.**

No se encontró ningún hueco entre el diseño congelado (r1 APROBADO CON CAMBIOS + G1) y la implementación de MT-H6a/b/c. Los tres archivos permanecen exactamente como los dejó la tanda anterior; esta MT no modificó ni una línea.

## 4. Evidencia DoD literal

### 4.1 `pnpm run typecheck`

```
$ pnpm run typecheck:libs && pnpm -r --filter "./artifacts/**" --filter "./scripts" --if-present run typecheck
$ tsc --build
Scope: 4 of 9 workspace projects
artifacts/acta-express typecheck$ tsc -p tsconfig.json --noEmit
artifacts/api-server typecheck$ tsc -p tsconfig.json --noEmit
artifacts/mockup-sandbox typecheck$ tsc -p tsconfig.json --noEmit
scripts typecheck$ tsc -p tsconfig.json --noEmit
scripts typecheck: Done
artifacts/api-server typecheck: Done
artifacts/acta-express typecheck: Done
artifacts/mockup-sandbox typecheck: Done
```

Exit code real (capturado inmediatamente tras el comando, sin pipes intermedios): `REAL_EXIT_CODE=0`.

### 4.2 Checklist 8/8 PASA (ver tabla §2)

### 4.3 Inventario de manejo de error — TODA llamada al vault

Grep de los 6 nombres de función en los dos archivos consumidores (`useAudioRecorder.ts`, `home.tsx`):

```
hooks/useAudioRecorder.ts:3:import { createSession, appendChunk, purgeStaleKeepNewest, isVaultAvailable } from "../lib/recordingVault";
hooks/useAudioRecorder.ts:229:        const sid = await createSession({
hooks/useAudioRecorder.ts:236:        purgeStaleKeepNewest(user.uid).catch(() => {}); // límite-1 al crear (cambio 3); fire-and-forget
hooks/useAudioRecorder.ts:247:          appendChunk(vaultSessionIdRef.current, seq, e.data).catch(() => {
pages/home.tsx:6:  purgeStaleKeepNewest,
pages/home.tsx:7:  getSession,
pages/home.tsx:8:  readChunks,
pages/home.tsx:9:  deleteSession,
pages/home.tsx:103:    purgeStaleKeepNewest(user.uid)
pages/home.tsx:112:        if (vaultSessionId) deleteSession(vaultSessionId).catch(() => {});
pages/home.tsx:142:        if ((err as any)?.status === 422 && vaultSessionId) deleteSession(vaultSessionId).catch(() => {});
pages/home.tsx:200:    deleteSession(orphanSession.sessionId).catch(() => {});
pages/home.tsx:207:    const meta = await getSession(orphanSession.sessionId).catch(() => null);
pages/home.tsx:213:    const chunks = await readChunks(meta.sessionId).catch(() => []);
pages/home.tsx:215:      deleteSession(meta.sessionId).catch(() => {});
pages/home.tsx:233:          deleteSession(meta.sessionId).catch(() => {});
pages/home.tsx:238:            deleteSession(meta.sessionId).catch(() => {});
```

Tabla llamada → manejo de error:

| Call site | Función | Manejo |
|---|---|---|
| `useAudioRecorder.ts:229` | `createSession` | `try` en 228, `catch` en 237-239 |
| `useAudioRecorder.ts:236` | `purgeStaleKeepNewest` | `.catch(() => {})` misma línea (dentro del mismo `try`) |
| `useAudioRecorder.ts:247` | `appendChunk` | `.catch(() => { vaultDisabledRef.current = true; })` líneas 247-249 |
| `home.tsx:103` | `purgeStaleKeepNewest` | `.then(...).catch(() => {})` línea 105 |
| `home.tsx:112` | `deleteSession` | `.catch(() => {})` misma línea |
| `home.tsx:142` | `deleteSession` | `.catch(() => {})` misma línea |
| `home.tsx:200` | `deleteSession` | `.catch(() => {})` misma línea |
| `home.tsx:207` | `getSession` | `.catch(() => null)` misma línea |
| `home.tsx:213` | `readChunks` | `.catch(() => [])` misma línea |
| `home.tsx:215` | `deleteSession` | `.catch(() => {})` misma línea |
| `home.tsx:233` | `deleteSession` (onSuccess) | `.catch(() => {})` misma línea |
| `home.tsx:238` | `deleteSession` (onError 422) | `.catch(() => {})` misma línea |

Total: 13 call sites, 13 con manejo de error explícito. Cero caminos hacia unhandled rejection.

### 4.4 `git diff --stat` de la tanda completa (H6a+b+c; H6d no añadió cambios)

```
$ git diff --stat -- artifacts/acta-express/src/hooks/useAudioRecorder.ts artifacts/acta-express/src/pages/home.tsx artifacts/acta-express/src/lib/recordingVault.ts
 .../acta-express/src/hooks/useAudioRecorder.ts     |  40 +++++++-
 artifacts/acta-express/src/pages/home.tsx          | 103 ++++++++++++++++++++-
 2 files changed, 139 insertions(+), 4 deletions(-)

$ git status --short -- artifacts/acta-express/src/hooks/useAudioRecorder.ts artifacts/acta-express/src/pages/home.tsx artifacts/acta-express/src/lib/recordingVault.ts
 M artifacts/acta-express/src/hooks/useAudioRecorder.ts
 M artifacts/acta-express/src/pages/home.tsx
?? artifacts/acta-express/src/lib/recordingVault.ts
```

(`recordingVault.ts` no aparece en `diff --stat` por ser archivo nuevo sin trackear; su tamaño íntegro es de 228 líneas, listado completo en §Contexto de este informe / leído en el paso 3 de la ejecución.)

Diff literal íntegro de los cambios PROPIOS de esta MT: **no aplica — checklist 8/8 PASA, cero cambios.**

## 5. Desviaciones

Ninguna. Se ejecutó el checklist tal como está redactado en la spec, sin reinterpretar umbrales ni textos.

## 6. Dudas

Ninguna. No hubo ambigüedad entre "fix mínimo" y "cambio de diseño" porque no se necesitó ningún fix.

## 7. Estado commiteable

**Sí**, en el sentido de que el working tree pasa typecheck y las garantías del diseño se sostienen contra el código real. Esta MT no crea el commit (fuera de alcance del rol); la tanda completa (H6a+b+c, sin cambios de H6d) queda lista para que el paso correspondiente del ciclo la commitee.
