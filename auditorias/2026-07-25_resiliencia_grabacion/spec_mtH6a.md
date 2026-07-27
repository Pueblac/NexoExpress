# Spec MT-H6a — Módulo `recordingVault.ts` (bóveda IndexedDB, H6)

**Ciclo:** 2026-07-25_resiliencia_grabacion · F4 · **Rol:** Ingeniero (Sonnet, rotación asistida)
**Diseño aprobado:** r1 APROBADO CON CAMBIOS + G1 del Director (25-07). Cambios vinculantes incorporados: (1) msDuration por timestamps, (2) silo por uid, (3) purga límite-1 en montaje y createSession, (5) STALE_MS=30000. Vinculante.
**Repo:** `/home/pueblac/AndroidStudioProjects/ActaExpressWeb`. Working tree LIMPIO (base `35580f0`, rama linux). Toca SOLO lo de tu contrato.

## Objetivo
Crear el módulo de persistencia local de grabaciones: los chunks de 1 s del `MediaRecorder` se copiarán a IndexedDB al vuelo (MT-H6b) para sobrevivir a un crash/cierre de pestaña, y se recuperarán al reabrir (MT-H6c). MT-H6a entrega SOLO el módulo, sin integrarlo.

## Contexto mínimo verificado
- No hay ninguna persistencia hoy: los chunks viven en `chunksRef.current` (memoria) en `useAudioRecorder.ts:215-217`.
- El módulo será consumido por `useAudioRecorder.ts` (escritura) y `home.tsx` (recuperación/purgas). Sus errores NO deben tragarse internamente: los llamadores deciden (fire-and-forget en grabación, manejo explícito en recuperación).
- Regla crítica del diseño (T2 del dictamen): una sesión "viva" (otra pestaña grabando ahora) se distingue de una "huérfana" por el latido `lastChunkAt`; la purga JAMÁS puede tocar sesiones vivas — por eso la API de purga es `purgeStaleKeepNewest`, no un "borrar todo excepto".

## Contrato
1. **Nuevo** `artifacts/acta-express/src/lib/recordingVault.ts`. Sin dependencias nuevas (IndexedDB nativo, sin librerías).
2. Constantes y tipos exportados:
```ts
const DB_NAME = "actaexpress-vault";
const DB_VERSION = 1;
export const VAULT_STALE_MS = 30000; // cambio 5 del dictamen — NO reinterpretar

export interface VaultSessionMeta {
  sessionId: string;
  uid: string;
  modo: "presencial" | "virtual";
  mimeType: string;
  startedAt: number;    // Date.now() al crear
  lastChunkAt: number;  // Date.now() del último chunk (heartbeat)
  chunkCount: number;
}
```
3. Esquema IndexedDB (creado en `onupgradeneeded`): store `sessions` con `keyPath: "sessionId"`; store `chunks` con `keyPath: ["sessionId", "seq"]` (clave compuesta; cada registro `{ sessionId, seq, data: Blob }`).
4. API pública (todas devuelven `Promise` y RECHAZAN en fallo — nunca tragan errores; conexión `IDBDatabase` cacheada en variable de módulo):
   - `isVaultAvailable(): boolean` — `typeof indexedDB !== "undefined"` (guard de entorno; toda función async debe rechazar con `Error("vault-unavailable")` si es false).
   - `createSession(input: { uid: string; modo: "presencial" | "virtual"; mimeType: string }): Promise<string>` — `sessionId = crypto.randomUUID()`, `startedAt = lastChunkAt = Date.now()`, `chunkCount = 0`. Devuelve el `sessionId`.
   - `appendChunk(sessionId: string, seq: number, data: Blob): Promise<void>` — en UNA transacción `readwrite` sobre `["chunks","sessions"]`: guarda el chunk Y actualiza la sesión (`lastChunkAt = Date.now()`, `chunkCount = Math.max(chunkCount, seq + 1)`). Si la sesión no existe, rechazar.
   - `getSession(sessionId: string): Promise<VaultSessionMeta | null>`.
   - `listSessions(uid: string): Promise<VaultSessionMeta[]>` — SOLO las del uid (silo, cambio 2): leer todas y filtrar por `uid` en JS es aceptable (volúmenes ínfimos).
   - `readChunks(sessionId: string): Promise<Blob[]>` — los Blobs en orden ascendente de `seq` (rango `IDBKeyRange.bound([sessionId, 0], [sessionId, Number.MAX_SAFE_INTEGER])` sobre la clave compuesta).
   - `deleteSession(sessionId: string): Promise<void>` — borra la sesión Y todos sus chunks (mismo rango).
   - `isStale(meta: VaultSessionMeta, now?: number): boolean` — `(now ?? Date.now()) - meta.lastChunkAt >= VAULT_STALE_MS`. Función pura, sincrónica.
   - `purgeStaleKeepNewest(uid: string): Promise<VaultSessionMeta | null>` — de las sesiones del uid: las NO stale se ignoran (vivas, intocables); de las stale, conserva la de `lastChunkAt` más reciente y borra (sesión+chunks) el resto. Devuelve la conservada o `null` si no había stale.
5. JSDoc breve por función pública explicando el porqué (heartbeat, silo por uid, por qué la purga ignora vivas).

## Restricciones
Solo el archivo nuevo `recordingVault.ts`. NO tocar `useAudioRecorder.ts`, `home.tsx` ni nada más. Sin dependencias nuevas. No commit.

## DoD (salida literal al informe)
1. `pnpm run typecheck` → exit 0.
2. `grep -n "VAULT_STALE_MS\|purgeStaleKeepNewest\|isStale\|appendChunk\|readChunks\|deleteSession\|createSession\|listSessions\|getSession\|isVaultAvailable" artifacts/acta-express/src/lib/recordingVault.ts`.
3. **A/B razonado** (sin navegador; traza con valores citando líneas de tu diff): (a) `appendChunk(s, 3, blob)` sobre sesión con `chunkCount=3` → chunk guardado + `lastChunkAt` actualizado + `chunkCount=4` EN LA MISMA transacción (¿qué pasa si la transacción aborta a medias?); (b) `purgeStaleKeepNewest("u1")` con: sesión A de u1 stale vieja, B de u1 stale reciente, C de u1 VIVA (lastChunkAt hace 2 s), D de u2 stale → borra SOLO A; conserva B (devuelta), no toca C ni D; (c) `readChunks` con seqs insertados en orden 2,0,1 → devuelve [0,1,2].
4. `git status --short` → exactamente `?? artifacts/acta-express/src/lib/recordingVault.ts`. Incluir el CONTENIDO COMPLETO del archivo nuevo en el informe (es untracked: no sale en `git diff`).

## Protocolo de dudas
Si dudas sobre detalles de IndexedDB (cursor vs getAll, promisificación), elige lo más simple y correcto y **decláralo**. Los nombres, firmas, constantes y semántica de `purgeStaleKeepNewest` son DISEÑO CONGELADO: no los reinterpretes. Cualquier duda que exija cambiar el contrato → DETENTE y decláralo en el informe sin implementar.

## Informe: `informe_mtH6a.md` — formato estándar (qué se hizo / contenido íntegro del archivo nuevo / evidencia DoD literal / desviaciones / dudas / estado commiteable).
