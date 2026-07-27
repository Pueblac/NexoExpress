# Informe MT-H6a — Módulo `recordingVault.ts` (bóveda IndexedDB, H6)

**Ciclo:** 2026-07-25_resiliencia_grabacion · F4 · **Rol:** Ingeniero (Sonnet, rotación asistida)
**Repo objetivo:** `/home/pueblac/AndroidStudioProjects/ActaExpressWeb`
**Precondición verificada:** `git -C ActaExpressWeb status --short` devolvió salida VACÍA antes de tocar nada (base `35580f0`, rama `linux`) — working tree limpio, precondición cumplida.

## 1. Qué se hizo

Se creó el archivo nuevo `artifacts/acta-express/src/lib/recordingVault.ts` con el módulo de persistencia local de grabaciones en IndexedDB, implementando al pie de la letra el contrato de la spec `spec_mtH6a.md`:

- Constantes `DB_NAME`, `DB_VERSION`, `SESSIONS_STORE`, `CHUNKS_STORE` y la constante exportada `VAULT_STALE_MS = 30000`.
- Interfaz exportada `VaultSessionMeta` con los 7 campos exactos de la spec, e interfaz interna `VaultChunkRecord` para los registros del store `chunks`.
- Esquema IndexedDB creado en `onupgradeneeded`: store `sessions` (`keyPath: "sessionId"`) y store `chunks` (`keyPath: ["sessionId", "seq"]`, clave compuesta).
- Conexión `IDBDatabase` cacheada en la variable de módulo `dbPromise` (una sola apertura de la BD, reutilizada por todas las llamadas).
- Dos helpers internos de promisificación: `requestToPromise` (envuelve un `IDBRequest`) y `txDone` (espera `oncomplete`/rechaza en `onerror`/`onabort`).
- Las 9 funciones públicas del contrato: `isVaultAvailable`, `createSession`, `appendChunk`, `getSession`, `listSessions`, `readChunks`, `deleteSession`, `isStale`, `purgeStaleKeepNewest` — todas devuelven `Promise` (salvo `isVaultAvailable` e `isStale`, que son sincrónicas por contrato) y ninguna traga errores: todo rechazo de un `IDBRequest`/`IDBTransaction` se propaga.
- JSDoc breve en cada función pública explicando el porqué (heartbeat en `appendChunk`, silo por uid en `listSessions`, purga que ignora sesiones vivas en `purgeStaleKeepNewest`, guard de entorno en `isVaultAvailable`).

No se tocó ningún otro archivo (ni `useAudioRecorder.ts`, ni `home.tsx`, ni `package.json`). No se añadieron dependencias. No se hizo commit.

### Decisiones de simplicidad declaradas (protocolo de dudas, sin cambiar contrato)

- **`listSessions`**: se usa `objectStore.getAll()` (trae todos los registros del store) y se filtra por `uid` en JS, tal como habilita explícitamente el punto 4 del contrato ("leer todas y filtrar por uid en JS es aceptable").
- **`readChunks`**: se usa `objectStore.getAll(range)` sobre el rango acotado por clave compuesta, en vez de cursor manual — `getAll` con rango es la forma más simple y devuelve los registros en orden ascendente de clave (garantía estructural de IndexedDB), que es exactamente el orden ascendente de `seq` que pide la spec.
- **`deleteSession`** y la purga en `purgeStaleKeepNewest`: se usa `objectStore.delete(range)` (que IndexedDB permite pasar un `IDBKeyRange` directamente a `delete`, no solo una clave puntual) para borrar todos los chunks de una sesión en una sola llamada, en vez de iterar con cursor y borrar registro a registro.
- **`appendChunk`**: al detectar que la sesión no existe, se llama a `tx.abort()` antes de lanzar el `Error` explícito — no es estrictamente necesario (aún no se había escrito nada), pero es defensivo y barato; no cambia la semántica del contrato.

## 2. Contenido íntegro del archivo nuevo

Archivo: `artifacts/acta-express/src/lib/recordingVault.ts` (es *untracked*, no aparece en `git diff`; se transcribe completo tal como quedó en disco tras el DoD):

```ts
/**
 * recordingVault.ts — bóveda local de grabaciones en IndexedDB (H6).
 *
 * Los chunks de 1 s del MediaRecorder viven hoy solo en memoria
 * (chunksRef.current en useAudioRecorder.ts), así que un crash o cierre de
 * pestaña los pierde. Este módulo los copia a IndexedDB al vuelo para poder
 * recuperarlos al reabrir. Este archivo solo define la API de persistencia;
 * no se integra con useAudioRecorder.ts ni home.tsx (eso es MT-H6b/H6c).
 */

const DB_NAME = "actaexpress-vault";
const DB_VERSION = 1;
const SESSIONS_STORE = "sessions";
const CHUNKS_STORE = "chunks";

/** Umbral de inactividad (ms) a partir del cual una sesión se considera huérfana. */
export const VAULT_STALE_MS = 30000; // cambio 5 del dictamen — NO reinterpretar

export interface VaultSessionMeta {
  sessionId: string;
  uid: string;
  modo: "presencial" | "virtual";
  mimeType: string;
  startedAt: number; // Date.now() al crear
  lastChunkAt: number; // Date.now() del último chunk (heartbeat)
  chunkCount: number;
}

interface VaultChunkRecord {
  sessionId: string;
  seq: number;
  data: Blob;
}

let dbPromise: Promise<IDBDatabase> | null = null;

/**
 * Guard de entorno: indica si IndexedDB existe (por ejemplo, false en SSR o
 * navegadores/entornos sin soporte). Toda función async de este módulo
 * rechaza con Error("vault-unavailable") en vez de fallar de forma confusa
 * al intentar usar un `indexedDB` inexistente.
 */
export function isVaultAvailable(): boolean {
  return typeof indexedDB !== "undefined";
}

function requestToPromise<T>(req: IDBRequest<T>): Promise<T> {
  return new Promise((resolve, reject) => {
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error ?? new Error("vault-request-error"));
  });
}

function txDone(tx: IDBTransaction): Promise<void> {
  return new Promise((resolve, reject) => {
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error ?? new Error("vault-tx-error"));
    tx.onabort = () => reject(tx.error ?? new Error("vault-tx-aborted"));
  });
}

function openVault(): Promise<IDBDatabase> {
  if (!isVaultAvailable()) {
    return Promise.reject(new Error("vault-unavailable"));
  }
  if (!dbPromise) {
    dbPromise = new Promise((resolve, reject) => {
      const req = indexedDB.open(DB_NAME, DB_VERSION);
      req.onupgradeneeded = () => {
        const db = req.result;
        if (!db.objectStoreNames.contains(SESSIONS_STORE)) {
          db.createObjectStore(SESSIONS_STORE, { keyPath: "sessionId" });
        }
        if (!db.objectStoreNames.contains(CHUNKS_STORE)) {
          db.createObjectStore(CHUNKS_STORE, { keyPath: ["sessionId", "seq"] });
        }
      };
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error ?? new Error("vault-open-error"));
    });
  }
  return dbPromise;
}

/** Rango de clave compuesta que cubre todos los chunks de una sesión, en orden ascendente de seq. */
function chunkRange(sessionId: string): IDBKeyRange {
  return IDBKeyRange.bound([sessionId, 0], [sessionId, Number.MAX_SAFE_INTEGER]);
}

/**
 * Crea una sesión nueva en la bóveda. startedAt y lastChunkAt arrancan
 * iguales: hasta que llegue el primer chunk, "recién creada" y "con vida"
 * son la misma cosa.
 */
export async function createSession(input: {
  uid: string;
  modo: "presencial" | "virtual";
  mimeType: string;
}): Promise<string> {
  const db = await openVault();
  const sessionId = crypto.randomUUID();
  const now = Date.now();
  const meta: VaultSessionMeta = {
    sessionId,
    uid: input.uid,
    modo: input.modo,
    mimeType: input.mimeType,
    startedAt: now,
    lastChunkAt: now,
    chunkCount: 0,
  };
  const tx = db.transaction([SESSIONS_STORE], "readwrite");
  tx.objectStore(SESSIONS_STORE).put(meta);
  await txDone(tx);
  return sessionId;
}

/**
 * Guarda un chunk y actualiza el latido (lastChunkAt) de la sesión en UNA
 * sola transacción: si la pestaña muere a medias, IndexedDB garantiza que
 * quedan ambos escritos o ninguno — nunca un chunk huérfano sin el
 * heartbeat que lo respalda, ni un heartbeat sin su chunk.
 */
export async function appendChunk(sessionId: string, seq: number, data: Blob): Promise<void> {
  const db = await openVault();
  const tx = db.transaction([CHUNKS_STORE, SESSIONS_STORE], "readwrite");
  const sessionsStore = tx.objectStore(SESSIONS_STORE);
  const chunksStore = tx.objectStore(CHUNKS_STORE);

  const meta = await requestToPromise<VaultSessionMeta | undefined>(sessionsStore.get(sessionId));
  if (!meta) {
    tx.abort();
    throw new Error(`vault-session-not-found: ${sessionId}`);
  }

  const record: VaultChunkRecord = { sessionId, seq, data };
  chunksStore.put(record);

  const updated: VaultSessionMeta = {
    ...meta,
    lastChunkAt: Date.now(),
    chunkCount: Math.max(meta.chunkCount, seq + 1),
  };
  sessionsStore.put(updated);

  await txDone(tx);
}

/** Lee los metadatos de una sesión, o null si no existe. */
export async function getSession(sessionId: string): Promise<VaultSessionMeta | null> {
  const db = await openVault();
  const tx = db.transaction([SESSIONS_STORE], "readonly");
  const result = await requestToPromise<VaultSessionMeta | undefined>(
    tx.objectStore(SESSIONS_STORE).get(sessionId)
  );
  return result ?? null;
}

/**
 * Lista las sesiones de un uid (silo por uid, cambio 2 del dictamen): se
 * leen todas las sesiones de la bóveda y se filtran por uid en JS. Los
 * volúmenes son ínfimos (a lo sumo unas pocas sesiones huérfanas), así que
 * no hace falta un índice secundario para esto.
 */
export async function listSessions(uid: string): Promise<VaultSessionMeta[]> {
  const db = await openVault();
  const tx = db.transaction([SESSIONS_STORE], "readonly");
  const all = await requestToPromise<VaultSessionMeta[]>(tx.objectStore(SESSIONS_STORE).getAll());
  return all.filter((meta) => meta.uid === uid);
}

/**
 * Devuelve los Blobs de una sesión en orden ascendente de seq. La clave
 * compuesta [sessionId, seq] hace que IndexedDB mantenga los registros ya
 * ordenados por seq dentro de cada sesión; el rango acotado evita traer
 * chunks de otras sesiones.
 */
export async function readChunks(sessionId: string): Promise<Blob[]> {
  const db = await openVault();
  const tx = db.transaction([CHUNKS_STORE], "readonly");
  const records = await requestToPromise<VaultChunkRecord[]>(
    tx.objectStore(CHUNKS_STORE).getAll(chunkRange(sessionId))
  );
  return records.map((r) => r.data);
}

/**
 * Borra una sesión y todos sus chunks en una sola transacción — nunca deja
 * chunks huérfanos sin la sesión que los referencia, ni una sesión sin sus
 * chunks.
 */
export async function deleteSession(sessionId: string): Promise<void> {
  const db = await openVault();
  const tx = db.transaction([SESSIONS_STORE, CHUNKS_STORE], "readwrite");
  tx.objectStore(SESSIONS_STORE).delete(sessionId);
  tx.objectStore(CHUNKS_STORE).delete(chunkRange(sessionId));
  await txDone(tx);
}

/**
 * Pura y sincrónica: una sesión está "stale" si no ha recibido un chunk en
 * los últimos VAULT_STALE_MS. Es la señal que distingue una grabación
 * huérfana (pestaña cerrada o crasheada) de una viva en otra pestaña.
 */
export function isStale(meta: VaultSessionMeta, now: number = Date.now()): boolean {
  return now - meta.lastChunkAt >= VAULT_STALE_MS;
}

/**
 * Purga las sesiones huérfanas (stale) de un uid, conservando solo la más
 * reciente por si el usuario quiere recuperarla. Las sesiones vivas
 * (latido reciente, probablemente otra pestaña grabando ahora mismo) se
 * ignoran por completo: la purga JAMÁS debe tocar una grabación en curso
 * (T2 del dictamen) — por eso esta función conserva-y-purga en vez de
 * ofrecer un "borrar todo excepto" genérico.
 */
export async function purgeStaleKeepNewest(uid: string): Promise<VaultSessionMeta | null> {
  const sessions = await listSessions(uid);
  const stale = sessions.filter((meta) => isStale(meta));
  if (stale.length === 0) {
    return null;
  }
  const newest = stale.reduce((a, b) => (b.lastChunkAt > a.lastChunkAt ? b : a));
  const toDelete = stale.filter((meta) => meta.sessionId !== newest.sessionId);
  await Promise.all(toDelete.map((meta) => deleteSession(meta.sessionId)));
  return newest;
}
```

## 3. Evidencia DoD (salidas literales)

### 3.1 `pnpm run typecheck` → exit 0

```
$ pnpm run typecheck
$ pnpm run typecheck:libs && pnpm -r --filter "./artifacts/**" --filter "./scripts" --if-present run typecheck
$ tsc --build
Scope: 4 of 9 workspace projects
artifacts/acta-express typecheck$ tsc -p tsconfig.json --noEmit
artifacts/api-server typecheck$ tsc -p tsconfig.json --noEmit
artifacts/mockup-sandbox typecheck$ tsc -p tsconfig.json --noEmit
scripts typecheck$ tsc -p tsconfig.json --noEmit
scripts typecheck: Done
artifacts/api-server typecheck: Done
artifacts/mockup-sandbox typecheck: Done
artifacts/acta-express typecheck: Done
EXIT:0
```

### 3.2 Grep de la API pública

Comando: `grep -n "VAULT_STALE_MS\|purgeStaleKeepNewest\|isStale\|appendChunk\|readChunks\|deleteSession\|createSession\|listSessions\|getSession\|isVaultAvailable" artifacts/acta-express/src/lib/recordingVault.ts`

```
17:export const VAULT_STALE_MS = 30000; // cambio 5 del dictamen — NO reinterpretar
43:export function isVaultAvailable(): boolean {
63:  if (!isVaultAvailable()) {
95:export async function createSession(input: {
124:export async function appendChunk(sessionId: string, seq: number, data: Blob): Promise<void> {
150:export async function getSession(sessionId: string): Promise<VaultSessionMeta | null> {
165:export async function listSessions(uid: string): Promise<VaultSessionMeta[]> {
178:export async function readChunks(sessionId: string): Promise<Blob[]> {
192:export async function deleteSession(sessionId: string): Promise<void> {
202: * los últimos VAULT_STALE_MS. Es la señal que distingue una grabación
205:export function isStale(meta: VaultSessionMeta, now: number = Date.now()): boolean {
206:  return now - meta.lastChunkAt >= VAULT_STALE_MS;
217:export async function purgeStaleKeepNewest(uid: string): Promise<VaultSessionMeta | null> {
218:  const sessions = await listSessions(uid);
219:  const stale = sessions.filter((meta) => isStale(meta));
225:  await Promise.all(toDelete.map((meta) => deleteSession(meta.sessionId)));
```

Las 9 funciones del contrato y `VAULT_STALE_MS` aparecen, todas `export`.

### 3.3 A/B razonado (traza sin navegador, citando líneas del archivo)

**(a) `appendChunk(s, 3, blob)` sobre sesión con `chunkCount=3`:**

- L126: se abre una única transacción `readwrite` sobre `[CHUNKS_STORE, SESSIONS_STORE]`.
- L130: `meta = get(sessionId)` → llega `{ ..., chunkCount: 3 }`.
- L131-134: `meta` existe, no se aborta.
- L136-137: `record = { sessionId, seq: 3, data: blob }`; `chunksStore.put(record)` encola la escritura del chunk `seq=3` **dentro de la misma transacción abierta en L126**.
- L139-143: `updated = { ...meta, lastChunkAt: Date.now(), chunkCount: Math.max(3, 3+1) }` → `chunkCount` pasa a **4**.
- L144: `sessionsStore.put(updated)` encola la escritura de la sesión, también dentro de la misma transacción.
- L146: `await txDone(tx)` espera `oncomplete`.

**¿Qué pasa si la transacción aborta a medias?** Ambas escrituras (L137 y L144) están encoladas en la *misma* `IDBTransaction` (L126), sin ningún `await` intermedio entre ellas que permita que la transacción se cierre sola. IndexedDB garantiza atomicidad por transacción: si aborta (por ejemplo `QuotaExceededError` al persistir el Blob, o el navegador la fuerza a abortar), **revierte TODAS las escrituras de esa transacción**, tanto el chunk como la actualización de la sesión — no queda ni el chunk `seq=3` guardado ni el `chunkCount=4` aplicado; el estado persistido vuelve a `chunkCount=3` sin el chunk nuevo. El handler `tx.onabort` (L58) rechaza la promesa de `txDone`, que se propaga hacia arriba a través del `await` en L146, así que la promesa devuelta por `appendChunk` rechaza y el llamador se entera (no hay estado a medias que reconciliar; puede reintentar con el mismo `seq`).

**(b) `purgeStaleKeepNewest("u1")` con A (u1, stale vieja), B (u1, stale reciente), C (u1, VIVA, latido hace 2 s), D (u2, stale):**

- L218: `sessions = listSessions("u1")` → L169 filtra por `uid === "u1"` → devuelve `[A, B, C]`; **D nunca entra** (uid distinto, descartado en el filtro de `listSessions`, ni siquiera llega a la lógica de purga).
- L219: `stale = sessions.filter(isStale)`. `isStale` (L205-206): `now - lastChunkAt >= 30000`.
  - A: stale vieja → `true`.
  - B: stale reciente → sigue siendo `true` (es "stale" igual, solo menos vieja que A).
  - C: latido hace 2000 ms → `2000 >= 30000` es `false` → **excluida de `stale`**, nunca se evalúa para borrado.
  - `stale = [A, B]`.
- L220-222: `stale.length = 2 ≠ 0`, continúa.
- L223: `newest = reduce(...)` compara `lastChunkAt`; B es más reciente que A → `newest = B`.
- L224: `toDelete = stale.filter(sessionId !== newest.sessionId)` → `toDelete = [A]`.
- L225: `Promise.all([deleteSession(A.sessionId)])` → solo A se borra (sesión + sus chunks, L192-198). B, C y D **nunca** se pasan a `deleteSession`.
- L226: `return newest` → devuelve B.

Resultado: se borra SOLO A; se conserva y devuelve B; C no se toca (nunca entra al array `stale`); D no se toca (nunca entra al array `sessions`, filtrado por uid antes de llegar a la lógica de stale/purga). Coincide exactamente con lo exigido.

**(c) `readChunks` con seqs insertados en orden 2, 0, 1:**

Cada inserción (vía `appendChunk`/`put`, L137 o equivalente) escribe un registro cuya clave es la clave compuesta `[sessionId, seq]` (definida en el `keyPath` del store `chunks`, L75). IndexedDB es un almacén ordenado por clave: independientemente del orden de inserción, los registros quedan siempre ordenados internamente por su clave (garantía estructural del motor, no del código de este módulo). Con inserciones en orden 2, 0, 1, las claves persistidas son `[sessionId,2]`, `[sessionId,0]`, `[sessionId,1]`, pero el store las mantiene ordenadas como `[sessionId,0] < [sessionId,1] < [sessionId,2]`.

- L178-185: `readChunks` abre `tx` readonly (L180), llama `chunksStore.getAll(chunkRange(sessionId))` (L182), donde `chunkRange` (L86-88) acota el rango a `[sessionId,0] .. [sessionId,MAX_SAFE_INTEGER]`. `getAll` sin dirección explícita recorre en orden ascendente de clave (comportamiento por defecto de IndexedDB, `direction: "next"`).
- Por lo tanto `records` llega en el orden `seq=0, seq=1, seq=2`, sin necesidad de ningún `sort()` adicional en el código.
- L184: `records.map((r) => r.data)` preserva ese orden → devuelve `[blob(seq=0), blob(seq=1), blob(seq=2)]`, es decir, el orden `[0,1,2]` exigido por la spec.

### 3.4 `git status --short` final

```
?? artifacts/acta-express/src/lib/recordingVault.ts
```

Coincide exactamente con lo exigido por el DoD (un único archivo untracked, el módulo nuevo; ningún otro archivo tocado).

## 4. Desviaciones

Ninguna. Se implementó el contrato al pie de la letra: nombres, firmas, constantes y semántica de `purgeStaleKeepNewest` sin reinterpretar. Las únicas decisiones tomadas fueron de "cómo" (elección de `getAll` con rango en vez de cursor manual, y `delete(range)` en vez de iterar y borrar registro a registro), explícitamente habilitadas por el protocolo de dudas de la spec y declaradas en la sección 1 de este informe.

## 5. Dudas

Ninguna que exija cambiar el contrato.

## 6. Estado commiteable

Sí. El único cambio en el árbol de trabajo es el archivo nuevo `artifacts/acta-express/src/lib/recordingVault.ts` (untracked), el typecheck pasa con exit 0, y no se tocó ningún otro archivo del repo. No se realizó commit (instrucción explícita del rol Ingeniero: no commitea).
