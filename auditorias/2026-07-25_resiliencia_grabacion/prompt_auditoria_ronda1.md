# Expediente 2026-07-25_resiliencia_grabacion — Prompt de auditoría de CÓDIGO, ronda 1 (tanda MT-H6a..e)

**Generado:** 28-07-2026 por el Arquitecto (Fable 5), tras F5 completa (código + E2E en 2 rondas, ver `verificacion_f5.md`).
**TURNO DE:** Auditor (Gemini 3.1 Pro High).
**Base:** ActaExpressWeb, rama `linux`, commit **`2871a74`** (tanda completa commiteada como checkpoint por orden del Director; el ciclo sigue abierto hasta tu dictamen + G2 de cierre).
**ADJUNTOS:** NINGUNO — todo el material va incrustado en el MENSAJE 2 (`git show 2871a74` ÍNTEGRO: incluye `recordingVault.ts` completo por ser archivo nuevo del commit).

---

## AVISO — Qué haces tú, paso a paso (Director)

1. Conversación **NUEVA** de Gemini 3.1 Pro High (sin herencia de hilo).
2. Pega el bloque **MENSAJE 1** (init de identidad) y espera su confirmación.
3. Pega TODO el bloque **MENSAJE 2** (desde `# Rol y regla de oro` hasta el final del archivo). Sin adjuntos.
4. Si responde sin citas archivo:línea o sin trazas: *"Auditoría INVÁLIDA según el contrato: faltan citas/trazas. Reenvíala completa."* — sin darle conversación.
5. Guarda la respuesta TAL CUAL como `auditorias/2026-07-25_resiliencia_grabacion/respuesta_auditoria_ronda1.md` y avísame; yo anexo la validación anti-bluff.

---

## MENSAJE 1 — Inicialización de identidad (pegar y esperar confirmación)

```
Rol: Auditor del ciclo 2026-07-25_resiliencia_grabacion, metodología v2 del
ecosistema Express. Confirma recepción sin accionar; acepta únicamente
artefactos cuyo campo TURNO DE diga Auditor.
```

---

## MENSAJE 2 — Prompt de auditoría (pegar íntegro tras la confirmación)

# Rol y regla de oro

Eres auditor adversarial del ecosistema Express. El implementador (otra IA) afirma haber implementado en ActaExpressWeb la tanda "resiliencia de grabación" (5 micro-tareas): una bóveda IndexedDB que persiste al vuelo los chunks de 1 s del MediaRecorder, y una tarjeta de recuperación que reconstruye y procesa la grabación tras un crash o cierre de pestaña. **Tu hipótesis de trabajo es que está mal o incompleto hasta que demuestre lo contrario.** No eres un asistente conversacional: no agradezcas, no resumas, no elogies. Cada afirmación sin cita textual del material incrustado (archivo y nº de línea del diff) se considera inventada.

# Formato obligatorio de CADA verificación

CLAIM → EVIDENCIA (cita textual, archivo:línea) → TRAZA (ejecución simbólica paso a paso con valores concretos) → VERDICTO (CONFIRMADO / BUG / NO VERIFICABLE CON LO ADJUNTO). Lo no incrustado es NO VERIFICABLE — prohibido rellenarlo con suposiciones.

# Contexto mínimo verificado (no es prosa del implementador)

- App React+Vite que graba reuniones (chunks de 1 s vía `MediaRecorder.start(1000)`) y genera actas vía backend con Gemini File API. Hallazgo H6 que motiva la tanda: los chunks vivían SOLO en memoria — cerrar la pestaña a mitad de una reunión perdía todo el audio.
- Diseño congelado en G1 tras auditoría de diseño (tu propio dictamen r1 APROBADO CON CAMBIOS): vault IndexedDB con heartbeat `lastChunkAt`; escritura fire-and-forget (la grabación JAMÁS falla por el vault); borrado SOLO en acta-OK/descarte/422 terminal (conservar en red/5xx); `msDuration = lastChunkAt − startedAt`; silo por uid; purga límite-1 que jamás toca sesiones vivas; `STALE_MS = 30000`; recuperación OFRECIDA (tarjeta), con re-check de heartbeat al pulsar Recuperar (mitigación T2×T5). MT-H6e (post-E2E): re-chequeo periódico de huérfanas cada 10 s (el chequeo solo-al-montar nunca veía la sesión porque a los pocos segundos de reabrir aún no era stale).
- El cliente HTTP generado lanza `ApiError` con propiedad `.status: number` — el 422 del guard anti-audio-mudo del server se detecta con `err?.status === 422`.
- F5 COMPLETA ejecutada por el Arquitecto y el Director: typecheck verde, greps por MT, y E2E real en 2 rondas — crash real de pestaña grabando → tarjeta automática a ~30-35 s → recuperación con ACTA FIEL al guion; descarte definitivo; caso feliz sin tarjeta; multi-pestaña sin falso positivo. Tu trabajo NO es repetir el E2E: es encontrar lo que el E2E no cubre.

# Material incrustado — `git show 2871a74` ÍNTEGRO (3 archivos: recordingVault.ts NUEVO completo, useAudioRecorder.ts, home.tsx)

```diff
commit 2871a7401606613042f6a6818430f183d5de24a9
Author: César Puebla <pueblac@gmail.com>
Date:   Mon Jul 27 08:16:47 2026 -0400

    feat(resiliencia-grabacion): MT-H6a..e — vault IndexedDB de chunks al vuelo + recuperación de grabaciones interrumpidas (H6)
    
    - MT-H6a: recordingVault.ts — sesiones con heartbeat lastChunkAt, chunks por [sessionId,seq], silo por uid, purgeStaleKeepNewest que jamás toca sesiones vivas (STALE_MS 30s, dictamen)
    - MT-H6b: useAudioRecorder — createSession con mimeType real + appendChunk fire-and-forget por chunk de 1s; fallo del vault degrada al comportamiento actual sin cortar la grabación; prohibido borrar desde el recorder
    - MT-H6c: home.tsx — tarjeta "Se encontró una grabación interrumpida" (Recuperar/Descartar), re-check de heartbeat al recuperar (T2×T5), msDuration por timestamps, borrado solo en acta OK / descarte / 422 terminal (conserva en red/5xx)
    - MT-H6d: endurecimiento adversarial 8/8 (cero fixes necesarios)
    - MT-H6e: re-chequeo periódico de huérfanas cada 10s (fix del E2E r1: la tarjeta no aparecía sin remontar Home)
    
    Ciclo v2 auditorias/2026-07-25_resiliencia_grabacion (NexoExpress): diseño APROBADO CON CAMBIOS (5) por Gemini + anti-bluff; F5 parte 1 verificada por el Arquitecto; checkpoint por orden del Director 27-07 — E2E ronda 2 y auditoría F6 PENDIENTES (ciclo abierto).
    
    Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

diff --git a/artifacts/acta-express/src/hooks/useAudioRecorder.ts b/artifacts/acta-express/src/hooks/useAudioRecorder.ts
index 7b7c786..571a0b4 100644
--- a/artifacts/acta-express/src/hooks/useAudioRecorder.ts
+++ b/artifacts/acta-express/src/hooks/useAudioRecorder.ts
@@ -1,4 +1,6 @@
 import { useState, useRef, useCallback } from "react";
+import { useAuth } from "@/context/AuthContext";
+import { createSession, appendChunk, purgeStaleKeepNewest, isVaultAvailable } from "../lib/recordingVault";
 
 type CaptureMode = "system+mic" | "system" | "microphone" | null;
 
@@ -14,9 +16,10 @@ interface UseAudioRecorderReturn {
   error: string | null;
   captureMode: CaptureMode;
   micStream: MediaStream | null;
+  vaultSessionId: string | null;
 }
 
-function blobToBase64(blob: Blob): Promise<string> {
+export function blobToBase64(blob: Blob): Promise<string> {
   return new Promise((resolve, reject) => {
     const reader = new FileReader();
     reader.onloadend = () => {
@@ -120,6 +123,7 @@ async function mixAudioStreams(displayStream: MediaStream): Promise<{
 }
 
 export function useAudioRecorder(): UseAudioRecorderReturn {
+  const { user } = useAuth();
   const [isRecording, setIsRecording] = useState(false);
   const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
   const [audioBase64, setAudioBase64] = useState<string | null>(null);
@@ -127,6 +131,7 @@ export function useAudioRecorder(): UseAudioRecorderReturn {
   const [error, setError] = useState<string | null>(null);
   const [captureMode, setCaptureMode] = useState<CaptureMode>(null);
   const [micStream, setMicStream] = useState<MediaStream | null>(null);
+  const [vaultSessionId, setVaultSessionId] = useState<string | null>(null);
 
   const mediaRecorderRef = useRef<MediaRecorder | null>(null);
   const displayStreamRef = useRef<MediaStream | null>(null);
@@ -135,6 +140,9 @@ export function useAudioRecorder(): UseAudioRecorderReturn {
   const chunksRef = useRef<Blob[]>([]);
   const startTimeRef = useRef<number>(0);
   const timerIntervalRef = useRef<number | null>(null);
+  const vaultSessionIdRef = useRef<string | null>(null);
+  const vaultDisabledRef = useRef<boolean>(false);
+  const chunkSeqRef = useRef<number>(0);
 
   const cleanupStreams = useCallback(() => {
     displayStreamRef.current?.getTracks().forEach((t) => t.stop());
@@ -212,8 +220,35 @@ export function useAudioRecorder(): UseAudioRecorderReturn {
     const mediaRecorder = new MediaRecorder(recordingStream);
     mediaRecorderRef.current = mediaRecorder;
 
+    vaultDisabledRef.current = false;
+    chunkSeqRef.current = 0;
+    vaultSessionIdRef.current = null;
+    setVaultSessionId(null);
+    if (user && isVaultAvailable()) {
+      try {
+        const sid = await createSession({
+          uid: user.uid,
+          modo,
+          mimeType: mediaRecorder.mimeType || "audio/webm",
+        });
+        vaultSessionIdRef.current = sid;
+        setVaultSessionId(sid);
+        purgeStaleKeepNewest(user.uid).catch(() => {}); // límite-1 al crear (cambio 3); fire-and-forget
+      } catch {
+        vaultDisabledRef.current = true; // vault caído → grabar como hoy
+      }
+    }
+
     mediaRecorder.ondataavailable = (e) => {
-      if (e.data.size > 0) chunksRef.current.push(e.data);
+      if (e.data.size > 0) {
+        chunksRef.current.push(e.data);
+        if (!vaultDisabledRef.current && vaultSessionIdRef.current) {
+          const seq = chunkSeqRef.current++;
+          appendChunk(vaultSessionIdRef.current, seq, e.data).catch(() => {
+            vaultDisabledRef.current = true; // QuotaExceeded/IDB roto → vault off, grabación sigue
+          });
+        }
+      }
     };
 
     mediaRecorder.onstop = async () => {
@@ -274,5 +309,6 @@ export function useAudioRecorder(): UseAudioRecorderReturn {
     error,
     captureMode,
     micStream,
+    vaultSessionId,
   };
 }
diff --git a/artifacts/acta-express/src/lib/recordingVault.ts b/artifacts/acta-express/src/lib/recordingVault.ts
new file mode 100644
index 0000000..8ce0cb2
--- /dev/null
+++ b/artifacts/acta-express/src/lib/recordingVault.ts
@@ -0,0 +1,227 @@
+/**
+ * recordingVault.ts — bóveda local de grabaciones en IndexedDB (H6).
+ *
+ * Los chunks de 1 s del MediaRecorder viven hoy solo en memoria
+ * (chunksRef.current en useAudioRecorder.ts), así que un crash o cierre de
+ * pestaña los pierde. Este módulo los copia a IndexedDB al vuelo para poder
+ * recuperarlos al reabrir. Este archivo solo define la API de persistencia;
+ * no se integra con useAudioRecorder.ts ni home.tsx (eso es MT-H6b/H6c).
+ */
+
+const DB_NAME = "actaexpress-vault";
+const DB_VERSION = 1;
+const SESSIONS_STORE = "sessions";
+const CHUNKS_STORE = "chunks";
+
+/** Umbral de inactividad (ms) a partir del cual una sesión se considera huérfana. */
+export const VAULT_STALE_MS = 30000; // cambio 5 del dictamen — NO reinterpretar
+
+export interface VaultSessionMeta {
+  sessionId: string;
+  uid: string;
+  modo: "presencial" | "virtual";
+  mimeType: string;
+  startedAt: number; // Date.now() al crear
+  lastChunkAt: number; // Date.now() del último chunk (heartbeat)
+  chunkCount: number;
+}
+
+interface VaultChunkRecord {
+  sessionId: string;
+  seq: number;
+  data: Blob;
+}
+
+let dbPromise: Promise<IDBDatabase> | null = null;
+
+/**
+ * Guard de entorno: indica si IndexedDB existe (por ejemplo, false en SSR o
+ * navegadores/entornos sin soporte). Toda función async de este módulo
+ * rechaza con Error("vault-unavailable") en vez de fallar de forma confusa
+ * al intentar usar un `indexedDB` inexistente.
+ */
+export function isVaultAvailable(): boolean {
+  return typeof indexedDB !== "undefined";
+}
+
+function requestToPromise<T>(req: IDBRequest<T>): Promise<T> {
+  return new Promise((resolve, reject) => {
+    req.onsuccess = () => resolve(req.result);
+    req.onerror = () => reject(req.error ?? new Error("vault-request-error"));
+  });
+}
+
+function txDone(tx: IDBTransaction): Promise<void> {
+  return new Promise((resolve, reject) => {
+    tx.oncomplete = () => resolve();
+    tx.onerror = () => reject(tx.error ?? new Error("vault-tx-error"));
+    tx.onabort = () => reject(tx.error ?? new Error("vault-tx-aborted"));
+  });
+}
+
+function openVault(): Promise<IDBDatabase> {
+  if (!isVaultAvailable()) {
+    return Promise.reject(new Error("vault-unavailable"));
+  }
+  if (!dbPromise) {
+    dbPromise = new Promise((resolve, reject) => {
+      const req = indexedDB.open(DB_NAME, DB_VERSION);
+      req.onupgradeneeded = () => {
+        const db = req.result;
+        if (!db.objectStoreNames.contains(SESSIONS_STORE)) {
+          db.createObjectStore(SESSIONS_STORE, { keyPath: "sessionId" });
+        }
+        if (!db.objectStoreNames.contains(CHUNKS_STORE)) {
+          db.createObjectStore(CHUNKS_STORE, { keyPath: ["sessionId", "seq"] });
+        }
+      };
+      req.onsuccess = () => resolve(req.result);
+      req.onerror = () => reject(req.error ?? new Error("vault-open-error"));
+    });
+  }
+  return dbPromise;
+}
+
+/** Rango de clave compuesta que cubre todos los chunks de una sesión, en orden ascendente de seq. */
+function chunkRange(sessionId: string): IDBKeyRange {
+  return IDBKeyRange.bound([sessionId, 0], [sessionId, Number.MAX_SAFE_INTEGER]);
+}
+
+/**
+ * Crea una sesión nueva en la bóveda. startedAt y lastChunkAt arrancan
+ * iguales: hasta que llegue el primer chunk, "recién creada" y "con vida"
+ * son la misma cosa.
+ */
+export async function createSession(input: {
+  uid: string;
+  modo: "presencial" | "virtual";
+  mimeType: string;
+}): Promise<string> {
+  const db = await openVault();
+  const sessionId = crypto.randomUUID();
+  const now = Date.now();
+  const meta: VaultSessionMeta = {
+    sessionId,
+    uid: input.uid,
+    modo: input.modo,
+    mimeType: input.mimeType,
+    startedAt: now,
+    lastChunkAt: now,
+    chunkCount: 0,
+  };
+  const tx = db.transaction([SESSIONS_STORE], "readwrite");
+  tx.objectStore(SESSIONS_STORE).put(meta);
+  await txDone(tx);
+  return sessionId;
+}
+
+/**
+ * Guarda un chunk y actualiza el latido (lastChunkAt) de la sesión en UNA
+ * sola transacción: si la pestaña muere a medias, IndexedDB garantiza que
+ * quedan ambos escritos o ninguno — nunca un chunk huérfano sin el
+ * heartbeat que lo respalda, ni un heartbeat sin su chunk.
+ */
+export async function appendChunk(sessionId: string, seq: number, data: Blob): Promise<void> {
+  const db = await openVault();
+  const tx = db.transaction([CHUNKS_STORE, SESSIONS_STORE], "readwrite");
+  const sessionsStore = tx.objectStore(SESSIONS_STORE);
+  const chunksStore = tx.objectStore(CHUNKS_STORE);
+
+  const meta = await requestToPromise<VaultSessionMeta | undefined>(sessionsStore.get(sessionId));
+  if (!meta) {
+    tx.abort();
+    throw new Error(`vault-session-not-found: ${sessionId}`);
+  }
+
+  const record: VaultChunkRecord = { sessionId, seq, data };
+  chunksStore.put(record);
+
+  const updated: VaultSessionMeta = {
+    ...meta,
+    lastChunkAt: Date.now(),
+    chunkCount: Math.max(meta.chunkCount, seq + 1),
+  };
+  sessionsStore.put(updated);
+
+  await txDone(tx);
+}
+
+/** Lee los metadatos de una sesión, o null si no existe. */
+export async function getSession(sessionId: string): Promise<VaultSessionMeta | null> {
+  const db = await openVault();
+  const tx = db.transaction([SESSIONS_STORE], "readonly");
+  const result = await requestToPromise<VaultSessionMeta | undefined>(
+    tx.objectStore(SESSIONS_STORE).get(sessionId)
+  );
+  return result ?? null;
+}
+
+/**
+ * Lista las sesiones de un uid (silo por uid, cambio 2 del dictamen): se
+ * leen todas las sesiones de la bóveda y se filtran por uid en JS. Los
+ * volúmenes son ínfimos (a lo sumo unas pocas sesiones huérfanas), así que
+ * no hace falta un índice secundario para esto.
+ */
+export async function listSessions(uid: string): Promise<VaultSessionMeta[]> {
+  const db = await openVault();
+  const tx = db.transaction([SESSIONS_STORE], "readonly");
+  const all = await requestToPromise<VaultSessionMeta[]>(tx.objectStore(SESSIONS_STORE).getAll());
+  return all.filter((meta) => meta.uid === uid);
+}
+
+/**
+ * Devuelve los Blobs de una sesión en orden ascendente de seq. La clave
+ * compuesta [sessionId, seq] hace que IndexedDB mantenga los registros ya
+ * ordenados por seq dentro de cada sesión; el rango acotado evita traer
+ * chunks de otras sesiones.
+ */
+export async function readChunks(sessionId: string): Promise<Blob[]> {
+  const db = await openVault();
+  const tx = db.transaction([CHUNKS_STORE], "readonly");
+  const records = await requestToPromise<VaultChunkRecord[]>(
+    tx.objectStore(CHUNKS_STORE).getAll(chunkRange(sessionId))
+  );
+  return records.map((r) => r.data);
+}
+
+/**
+ * Borra una sesión y todos sus chunks en una sola transacción — nunca deja
+ * chunks huérfanos sin la sesión que los referencia, ni una sesión sin sus
+ * chunks.
+ */
+export async function deleteSession(sessionId: string): Promise<void> {
+  const db = await openVault();
+  const tx = db.transaction([SESSIONS_STORE, CHUNKS_STORE], "readwrite");
+  tx.objectStore(SESSIONS_STORE).delete(sessionId);
+  tx.objectStore(CHUNKS_STORE).delete(chunkRange(sessionId));
+  await txDone(tx);
+}
+
+/**
+ * Pura y sincrónica: una sesión está "stale" si no ha recibido un chunk en
+ * los últimos VAULT_STALE_MS. Es la señal que distingue una grabación
+ * huérfana (pestaña cerrada o crasheada) de una viva en otra pestaña.
+ */
+export function isStale(meta: VaultSessionMeta, now: number = Date.now()): boolean {
+  return now - meta.lastChunkAt >= VAULT_STALE_MS;
+}
+
+/**
+ * Purga las sesiones huérfanas (stale) de un uid, conservando solo la más
+ * reciente por si el usuario quiere recuperarla. Las sesiones vivas
+ * (latido reciente, probablemente otra pestaña grabando ahora mismo) se
+ * ignoran por completo: la purga JAMÁS debe tocar una grabación en curso
+ * (T2 del dictamen) — por eso esta función conserva-y-purga en vez de
+ * ofrecer un "borrar todo excepto" genérico.
+ */
+export async function purgeStaleKeepNewest(uid: string): Promise<VaultSessionMeta | null> {
+  const sessions = await listSessions(uid);
+  const stale = sessions.filter((meta) => isStale(meta));
+  if (stale.length === 0) {
+    return null;
+  }
+  const newest = stale.reduce((a, b) => (b.lastChunkAt > a.lastChunkAt ? b : a));
+  const toDelete = stale.filter((meta) => meta.sessionId !== newest.sessionId);
+  await Promise.all(toDelete.map((meta) => deleteSession(meta.sessionId)));
+  return newest;
+}
diff --git a/artifacts/acta-express/src/pages/home.tsx b/artifacts/acta-express/src/pages/home.tsx
index dc77478..b5d5ef2 100644
--- a/artifacts/acta-express/src/pages/home.tsx
+++ b/artifacts/acta-express/src/pages/home.tsx
@@ -1,7 +1,16 @@
 import { useEffect, useRef, useState } from "react";
 import { useAuth } from "@/context/AuthContext";
-import { useAudioRecorder, type ModoReunion } from "@/hooks/useAudioRecorder";
+import { useAudioRecorder, type ModoReunion, blobToBase64 } from "@/hooks/useAudioRecorder";
 import { useMicLevel } from "@/hooks/useMicLevel";
+import {
+  purgeStaleKeepNewest,
+  getSession,
+  readChunks,
+  deleteSession,
+  isStale,
+  isVaultAvailable,
+  type VaultSessionMeta,
+} from "@/lib/recordingVault";
 import { useListActas, useProcessAudio, useDeleteActa, getListActasQueryKey } from "@workspace/api-client-react";
 import { useQueryClient } from "@tanstack/react-query";
 import { format } from "date-fns";
@@ -37,6 +46,8 @@ function formatCreatedAt(iso: unknown): string {
   }
 }
 
+const ORPHAN_POLL_MS = 10000; // constante de módulo, junto a los imports o encima del componente
+
 export default function Home() {
   const { user } = useAuth();
   const { toast } = useToast();
@@ -50,7 +61,8 @@ export default function Home() {
     duration,
     error,
     captureMode,
-    micStream
+    micStream,
+    vaultSessionId
   } = useAudioRecorder();
 
   const { data: actas, isLoading: loadingActas } = useListActas();
@@ -85,10 +97,34 @@ export default function Home() {
   // MT-C3: solo cablea el hook para producir micSilent; el banner es MT-C4.
   const { micSilent } = useMicLevel(micStream, isRecording, modoReunion);
 
+  const [orphanSession, setOrphanSession] = useState<VaultSessionMeta | null>(null);
+
+  // H6c+H6e: detección de sesión huérfana — al montar y re-chequeo periódico
+  // (la sesión del crash tarda VAULT_STALE_MS en volverse stale; sin poll, la
+  // tarjeta solo aparecía al remontar Home — bug del E2E 27-07).
+  useEffect(() => {
+    if (!user || !isVaultAvailable() || orphanSession) return;
+    let cancelled = false;
+    const check = () => {
+      purgeStaleKeepNewest(user.uid)
+        .then((orphan) => {
+          if (!cancelled && orphan) setOrphanSession(orphan);
+        })
+        .catch(() => {}); // vault roto → sin tarjeta, app intacta
+    };
+    check();
+    const intervalId = window.setInterval(check, ORPHAN_POLL_MS);
+    return () => {
+      cancelled = true;
+      window.clearInterval(intervalId);
+    };
+  }, [user?.uid, orphanSession]);
+
   const processAudio = useProcessAudio({
     mutation: {
       onSuccess: (acta, variables) => {
         queryClient.invalidateQueries({ queryKey: getListActasQueryKey() });
+        if (vaultSessionId) deleteSession(vaultSessionId).catch(() => {});
 
         // Detect silent/empty audio result
         const silenceKeywords = ["no se pudo", "no audible", "no hay audio", "sin contenido", "silencio"];
@@ -118,6 +154,7 @@ export default function Home() {
           title: "Error al procesar",
           description: err.message || "Hubo un problema analizando el audio.",
         });
+        if ((err as any)?.status === 422 && vaultSessionId) deleteSession(vaultSessionId).catch(() => {});
       }
     }
   });
@@ -173,6 +210,54 @@ export default function Home() {
     deleteActa.mutate({ actaId: id });
   };
 
+  const handleDescartarOrphan = () => {
+    if (!orphanSession) return;
+    deleteSession(orphanSession.sessionId).catch(() => {});
+    setOrphanSession(null);
+    toast({ title: "Grabación descartada" });
+  };
+
+  const handleRecuperarOrphan = async () => {
+    if (!orphanSession) return;
+    const meta = await getSession(orphanSession.sessionId).catch(() => null);
+    if (!meta || !isStale(meta)) { // mitigación T2×T5: volvió a latir u desapareció
+      setOrphanSession(null);
+      toast({ title: "Grabación no recuperable", description: "Esa grabación sigue activa en otra pestaña o ya no existe." });
+      return;
+    }
+    const chunks = await readChunks(meta.sessionId).catch(() => []);
+    if (chunks.length === 0) {
+      deleteSession(meta.sessionId).catch(() => {});
+      setOrphanSession(null);
+      toast({ variant: "destructive", title: "Grabación vacía" });
+      return;
+    }
+    const blob = new Blob(chunks, { type: meta.mimeType || "audio/webm" });
+    const audioBase64Recuperado = await blobToBase64(blob);
+    processAudio.mutate(
+      {
+        data: {
+          audioBase64: audioBase64Recuperado,
+          mimeType: "audio/webm",
+          msDuration: Math.max(1000, meta.lastChunkAt - meta.startedAt),
+          generarSintesis: generarSintesisRef.current,
+        },
+      },
+      {
+        onSuccess: () => {
+          deleteSession(meta.sessionId).catch(() => {});
+          setOrphanSession(null);
+        },
+        onError: (err: any) => {
+          if (err?.status === 422) {
+            deleteSession(meta.sessionId).catch(() => {});
+            setOrphanSession(null);
+          } // red/5xx: conservar (tarjeta sigue)
+        },
+      }
+    );
+  };
+
   return (
     <div className="space-y-12 pb-12">
       {/* Recorder Section */}
@@ -271,6 +356,35 @@ export default function Home() {
               </div>
             )}
 
+            {orphanSession && !isRecording && !processAudio.isPending && (
+              <div
+                data-testid="card-recuperacion"
+                className="border border-primary/30 bg-primary/10 rounded-xl p-4 flex flex-col items-center gap-3 mt-2"
+              >
+                <p className="text-sm font-medium">
+                  Se encontró una grabación interrumpida (~
+                  {Math.max(1, Math.round((orphanSession.lastChunkAt - orphanSession.startedAt) / 60000))} min)
+                </p>
+                <div className="flex items-center gap-2">
+                  <Button
+                    data-testid="btn-recuperar"
+                    size="sm"
+                    onClick={handleRecuperarOrphan}
+                  >
+                    Recuperar
+                  </Button>
+                  <Button
+                    data-testid="btn-descartar"
+                    size="sm"
+                    variant="outline"
+                    onClick={handleDescartarOrphan}
+                  >
+                    Descartar
+                  </Button>
+                </div>
+              </div>
+            )}
+
             <div
               data-testid="selector-modo-reunion"
               className="flex justify-center pt-2"
```

# Claims a verificar

- **C1 (MT-H6b, regla de oro):** La grabación JAMÁS puede fallar ni degradarse por culpa del vault: `createSession` va en try/catch que solo apaga el vault, `appendChunk` es fire-and-forget con catch que apaga el vault, ningún `await` nuevo bloquea `ondataavailable`, y con `user` null o IndexedDB ausente el flujo es byte a byte el actual. El recorder tiene PROHIBIDO borrar sesiones (cero referencias a `deleteSession`).
- **C2 (MT-H6a):** `purgeStaleKeepNewest(uid)` opera en silo por uid, ignora TODA sesión no-stale (viva), conserva la stale más reciente y borra las demás CON sus chunks (sin fuga). `appendChunk` actualiza chunk + heartbeat + chunkCount en UNA transacción y rechaza si la sesión no existe.
- **C3 (MT-H6c, ciclo de vida):** la sesión del vault se borra exactamente en: acta OK (flujo normal y recuperación), descarte explícito, y error 422 (flujo normal y recuperación); se CONSERVA en errores de red/5xx. Ningún otro punto del código borra sesiones.
- **C4 (MT-H6c+H6e, detección):** una huérfana se detecta SOLA (poll de 10 s + stale 30 s) sin remontar Home; el poll se apaga al detectarla (sin fuga de intervalos, cleanup correcto); una sesión viva (heartbeat < 30 s) jamás se ofrece ni se purga; y al pulsar Recuperar se RE-verifica el heartbeat (si volvió a latir → toast y salida sin procesar).
- **C5 (MT-H6c, aislamiento T4):** la ruta de recuperación es imperativa y estanca: construye su propio base64 local, no escribe `audioBase64`/`duration`/`lastProcessedAudioRef` del hook → el useEffect de auto-proceso no puede re-disparar el mismo audio (cero dobles actas).
- **C6 (traza obligatoria, estado final literal):** ejecuta simbólicamente: `uid="u1"`, grabación presencial arranca en t=0 (`startedAt=lastChunkAt=T0`), 45 chunks (seq 0..44, último a T0+45 000), crash a t=46 s. Reapertura en t=60 s. Muestra: qué devuelve `purgeStaleKeepNewest` en el check del montaje (t=60 s) y en cada poll, el instante en que `setOrphanSession` dispara, el texto EXACTO renderizado de la tarjeta (con el cálculo de minutos), y al pulsar Recuperar: resultado del re-check, tamaño del array de `readChunks`, y el payload EXACTO de `processAudio.mutate` (valor numérico de `msDuration` incluido).

# Dudas declaradas

Del Ingeniero (informes MT-H6a..e): ninguna — cero dudas declaradas en los 5 informes.

Del Arquitecto (Fable 5):
- **D1 — Memoria en recuperaciones largas:** `readChunks` carga TODOS los Blobs y `blobToBase64` produce un string base64 completo en RAM. Para una reunión de 2 h (~100 MB de webm → ~133 MB de string) ¿hay riesgo real de OOM/jank en el click de Recuperar, y merece mitigación futura (streaming/chunked upload) o es aceptable para el MVP?
- **D2 — Carrera poll vs descarte fallido:** `handleDescartarOrphan` hace `deleteSession(...).catch(() => {})` y `setOrphanSession(null)`; si el borrado FALLA silenciosamente, el poll reactivado re-ofrecerá la misma huérfana (~10 s después). ¿Bucle molesto o comportamiento aceptable (el fallo de IndexedDB es excepcional)?
- **D3 — Pestañas concurrentes escribiendo:** dos pestañas grabando a la vez crean sesiones distintas (UUID) y solo una escribe cada sessionId; pero ambas ejecutan `purgeStaleKeepNewest` en sus polls. ¿Puede una purga de la pestaña A borrar una stale que la pestaña B está por ofrecer (tarjeta ya renderizada en B) y qué pasa al pulsar Recuperar en B? (Pista: el re-check devolvería null → salida limpia. Verifícalo.)
- **D4 — Timing observado:** en el E2E la tarjeta apareció ~20 s tras reabrir (~30-35 s desde el último chunk). ¿Cuadra exactamente con STALE 30 s + poll 10 s o hay un camino que pudiera adelantarla indebidamente (<30 s desde el último chunk)?

# Preguntas de control (respóndelas TODAS; son parte del entregable)

- **Q1:** Copia TEXTUALMENTE del diff: (a) el texto completo de la tarjeta de recuperación (incluida la expresión JSX del cálculo de minutos); (b) el toast del re-check fallido de Recuperar; (c) el comentario de la línea del catch del poll.
- **Q2:** En `appendChunk`, ¿qué ocurre exactamente (traza de la transacción) si la sesión fue borrada por una purga concurrente un instante antes? ¿Y cómo reacciona el llamador en `useAudioRecorder`? Cita las líneas de ambos lados.
- **Q3:** Traza el apagado del poll: `orphanSession` pasa de null a una sesión → ¿qué hace el efecto, en qué orden (cleanup vs re-ejecución), y por qué no queda ningún interval vivo? Cita las líneas.
- **Q4:** ¿En qué caso `chunkCount` puede diferir del número real de chunks persistidos (pista: fallo intermitente de `appendChunk` que NO apaga el vault… ¿existe ese camino?) y qué usa realmente la recuperación para el blob y para `msDuration`? ¿Alguna inconsistencia posible entre ambos? Cita líneas.

# Anti-aprobación-automática

Si tu veredicto global es APROBADO (con o sin observaciones), demuestra por qué cada trampa NO aplica (con evidencia y traza):

- **T1 — Doble acta:** algún camino (auto-proceso + recuperación, doble click en Recuperar, recuperar durante `isPending`) que produzca DOS procesamientos del mismo audio.
- **T2 — Pérdida por límite-1:** dos pestañas grabando a la vez crashean ambas → 2 huérfanas → la purga conserva solo la más reciente: la grabación más antigua SE PIERDE. ¿Es comportamiento aprobado en G0 (máx. 1 huérfana) o un bug? Justifica con el dictamen de diseño.
- **T3 — Quota a mitad de reunión:** QuotaExceeded en el chunk N de M → ¿la grabación sigue?, ¿qué queda en el vault?, y si LUEGO crashea la pestaña, ¿qué ofrece la tarjeta (audio parcial hasta N con qué msDuration)? ¿El usuario recibe alguna pista de que es parcial?
- **T4 — Logout/cambio de cuenta:** usuario u1 crashea grabando; u2 se loguea en el mismo navegador → ¿ve la tarjeta de u1?, ¿puede borrarla?; u1 vuelve → ¿sigue pudiendo recuperar?
- **T5 — El poll durante una grabación activa:** el poll sigue corriendo mientras grabas (no hay guarda de `isRecording`). Demuestra que (a) jamás purga la sesión en curso, (b) si setea una huérfana vieja durante la grabación, la tarjeta NO se muestra hasta parar (cita la condición de render) y recuperar después funciona.

# Entregable final

UN ÚNICO documento markdown listo para archivar: 1. Tabla C1..C6 con verdictos. 2. Respuestas Q1..Q4. 3. Demostración T1..T5 si apruebas. 4. Opinión fundada sobre D1..D4. 5. Veredicto global (APROBADO / APROBADO CON OBSERVACIONES / RECHAZADO). Una auditoría sin citas archivo:línea o sin las trazas obligatorias es INVÁLIDA y será devuelta.
