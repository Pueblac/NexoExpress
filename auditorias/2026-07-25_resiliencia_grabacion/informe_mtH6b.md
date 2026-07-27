# Informe MT-H6b — Escritura al vuelo en `useAudioRecorder` (heartbeat, H6)

**Rol:** Ingeniero (Sonnet, rotación asistida) · **Ciclo:** 2026-07-25_resiliencia_grabacion · F4
**Repo:** `/home/pueblac/AndroidStudioProjects/ActaExpressWeb`
**Precondición verificada antes de empezar:** `git status --short` mostraba exactamente
`?? artifacts/acta-express/src/lib/recordingVault.ts` (MT-H6a aplicada, nada más). OK, se procedió.

## 1. Qué se hizo

Se modificó únicamente `artifacts/acta-express/src/hooks/useAudioRecorder.ts` siguiendo el contrato al pie de la letra:

1. Imports nuevos: `useAuth` (`@/context/AuthContext`) y, de `../lib/recordingVault`: `createSession, appendChunk, purgeStaleKeepNewest, isVaultAvailable`.
2. `vaultSessionId: string | null` añadido a `UseAudioRecorderReturn` y al objeto de retorno del hook.
3. Dentro de `useAudioRecorder()`: `const { user } = useAuth();`, nuevo estado `vaultSessionId`/`setVaultSessionId`, y refs `vaultSessionIdRef`, `vaultDisabledRef` (boolean), `chunkSeqRef` (number).
4. En `startRecording`, entre `new MediaRecorder(recordingStream)` y `mediaRecorder.start(1000)`: reseteo de refs/estado y, si `user && isVaultAvailable()`, `createSession(...)` con el `mimeType` real del `MediaRecorder` ya instanciado; en éxito guarda `sid` en ref+estado y dispara `purgeStaleKeepNewest(user.uid)` fire-and-forget; en `catch`, `vaultDisabledRef.current = true`.
5. En `ondataavailable`: se mantuvo intacto `chunksRef.current.push(e.data)` y se añadió, sin `await`, `appendChunk(vaultSessionIdRef.current, seq, e.data).catch(() => { vaultDisabledRef.current = true; })` cuando el vault está activo y hay sesión.
6. No se tocó `onstop`, `cleanupStreams`, `stopRecording` — ninguna sesión se borra en este archivo. `vaultSessionId` queda expuesto tras parar la grabación.
7. No se tocó `recordingVault.ts`, `home.tsx` ni UI. Sin dependencias nuevas. Sin commit.

## 2. Diff literal íntegro

```diff
diff --git a/artifacts/acta-express/src/hooks/useAudioRecorder.ts b/artifacts/acta-express/src/hooks/useAudioRecorder.ts
index 7b7c786..8cd1309 100644
--- a/artifacts/acta-express/src/hooks/useAudioRecorder.ts
+++ b/artifacts/acta-express/src/hooks/useAudioRecorder.ts
@@ -1,4 +1,6 @@
 import { useState, useRef, useCallback } from "react";
+import { useAuth } from "@/context/AuthContext";
+import { createSession, appendChunk, purgeStaleKeepNewest, isVaultAvailable } from "../lib/recordingVault";
 
 type CaptureMode = "system+mic" | "system" | "microphone" | null;
 
@@ -14,6 +16,7 @@ interface UseAudioRecorderReturn {
   error: string | null;
   captureMode: CaptureMode;
   micStream: MediaStream | null;
+  vaultSessionId: string | null;
 }
 
 function blobToBase64(blob: Blob): Promise<string> {
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
```

`git status --short` tras el cambio:

```
 M artifacts/acta-express/src/hooks/useAudioRecorder.ts
?? artifacts/acta-express/src/lib/recordingVault.ts
```

(el `??` de `recordingVault.ts` es preexistente de MT-H6a, no de esta micro-tarea).

## 3. Evidencia DoD literal

### 3.1 `pnpm run typecheck` (desde la raíz de ActaExpressWeb)

```
$ pnpm run typecheck:libs && pnpm -r --filter "./artifacts/**" --filter "./scripts" --if-present run typecheck
$ tsc --build
Scope: 4 of 9 workspace projects
artifacts/acta-express typecheck$ tsc -p tsconfig.json --noEmit
artifacts/mockup-sandbox typecheck$ tsc -p tsconfig.json --noEmit
artifacts/api-server typecheck$ tsc -p tsconfig.json --noEmit
scripts typecheck$ tsc -p tsconfig.json --noEmit
scripts typecheck: Done
artifacts/api-server typecheck: Done
artifacts/mockup-sandbox typecheck: Done
artifacts/acta-express typecheck: Done
EXIT_CODE=0
```

Exit 0 ✔.

### 3.2 Grep de los símbolos del contrato

```
$ grep -n "createSession\|appendChunk\|purgeStaleKeepNewest\|vaultDisabledRef\|vaultSessionId\|chunkSeqRef\|isVaultAvailable" artifacts/acta-express/src/hooks/useAudioRecorder.ts
3:import { createSession, appendChunk, purgeStaleKeepNewest, isVaultAvailable } from "../lib/recordingVault";
19:  vaultSessionId: string | null;
134:  const [vaultSessionId, setVaultSessionId] = useState<string | null>(null);
143:  const vaultSessionIdRef = useRef<string | null>(null);
144:  const vaultDisabledRef = useRef<boolean>(false);
145:  const chunkSeqRef = useRef<number>(0);
223:    vaultDisabledRef.current = false;
224:    chunkSeqRef.current = 0;
225:    vaultSessionIdRef.current = null;
227:    if (user && isVaultAvailable()) {
229:        const sid = await createSession({
234:        vaultSessionIdRef.current = sid;
236:        purgeStaleKeepNewest(user.uid).catch(() => {}); // límite-1 al crear (cambio 3); fire-and-forget
238:        vaultDisabledRef.current = true; // vault caído → grabar como hoy
245:        if (!vaultDisabledRef.current && vaultSessionIdRef.current) {
246:          const seq = chunkSeqRef.current++;
247:          appendChunk(vaultSessionIdRef.current, seq, e.data).catch(() => {
248:            vaultDisabledRef.current = true; // QuotaExceeded/IDB roto → vault off, grabación sigue
312:    vaultSessionId,
```

### 3.3 Grep de `deleteSession` (prohibición del punto 6)

```
$ grep -n "deleteSession" artifacts/acta-express/src/hooks/useAudioRecorder.ts
EXIT_CODE=1
```

Sin resultados (exit 1 de grep = no matches). ✔ Ninguna sesión se borra en este archivo.

### 3.4 A/B razonado (4 caminos, citando líneas del diff/archivo final)

**(a) Camino feliz — 3 chunks → seq 0,1,2 persistidos con heartbeat.**
Con `user` autenticado y `isVaultAvailable()` true, al construir el `MediaRecorder` (línea 220) se ejecuta el bloque 223-240: se resetean las refs y `createSession(...)` (229-233) crea la sesión con el `mimeType` real (`mediaRecorder.mimeType`, ya conocido en este punto porque el recorder ya fue instanciado — cumple el diseño congelado del orden create→createSession→start). Al llegar cada chunk por `ondataavailable` (242-252), primero se empuja a memoria (244, INTACTO respecto al original) y luego, como `vaultDisabledRef.current` es `false` y `vaultSessionIdRef.current` tiene el `sid`, se llama `appendChunk(sid, seq, e.data)` con `seq` tomado de `chunkSeqRef.current++` (246): la primera vez `seq=0`, la segunda `seq=1`, la tercera `seq=2`. Cada llamada a `appendChunk` en `recordingVault.ts` actualiza `lastChunkAt` (heartbeat) en la misma transacción IDB (líneas 139-144 de `recordingVault.ts`). Resultado: 3 chunks persistidos con seq 0,1,2 y heartbeat actualizado en cada uno, sin ningún `await` nuevo en `ondataavailable` (fire-and-forget puro, `.catch()` en 247-249).

**(b) `appendChunk` rechaza en seq 1 → `vaultDisabledRef=true`, seq 2 NO se intenta persistir, pero `chunksRef.current` tiene los 3 y blob→base64 es idéntico.**
En el chunk con `seq=1`, la promesa de `appendChunk` se rechaza (p.ej. `QuotaExceededError`); el `.catch()` en 247-249 se ejecuta y pone `vaultDisabledRef.current = true`. Cuando llega el tercer chunk (`seq` habría sido 2), la condición `!vaultDisabledRef.current && vaultSessionIdRef.current` (245) ahora es falsa porque `vaultDisabledRef.current` es `true`, así que el `if` de la línea 245 no entra y **no se llama a `appendChunk` para ese chunk** (ni se incrementa `chunkSeqRef`, ya que el incremento está dentro del `if`). Pero la línea 244 (`chunksRef.current.push(e.data)`) se ejecutó para los 3 chunks sin condición alguna — es la primera línea del bloque `if (e.data.size > 0)` y no depende del estado del vault. En `onstop` (254-264), el blob se construye igual que hoy a partir de `chunksRef.current` (3 chunks) y se codifica a base64 sin cambios: el flujo memoria→blob→base64 es exactamente el actual, no afectado por el fallo del vault.

**(c) `user` null o `isVaultAvailable()` false → cero llamadas al vault, grabación idéntica a hoy.**
Si `user` es `null` (no autenticado) o `isVaultAvailable()` devuelve `false` (sin soporte IndexedDB), la condición de la línea 227 es falsa, así que el bloque 228-239 completo (incluida la llamada a `createSession`) nunca se ejecuta; `vaultSessionIdRef.current` permanece `null` (reseteado en 225) y `vaultDisabledRef.current` permanece `false` (reseteado en 223, nunca se marca `true` porque no hay `catch`). En `ondataavailable`, la condición de la línea 245 (`!vaultDisabledRef.current && vaultSessionIdRef.current`) es falsa porque `vaultSessionIdRef.current` es `null` — nunca se llama a `appendChunk`. El único código que corre es `chunksRef.current.push(e.data)` (244), idéntico al comportamiento anterior a esta micro-tarea.

**(d) `createSession` lanza → catch → `vaultDisabledRef=true`, `mediaRecorder.start(1000)` se ejecuta igual.**
Si `createSession(...)` (229-233) rechaza (p.ej. `openVault()` falla), el `catch` de la línea 237-239 se ejecuta y pone `vaultDisabledRef.current = true` (`vaultSessionIdRef.current` queda `null`, tal como se reseteó en 225 — nunca se sobreescribe porque el `throw` ocurre antes de la línea 234). El bloque `if` completo (227-240) está *antes* de la asignación de `mediaRecorder.ondataavailable` (242) y de `mediaRecorder.start(1000)` (más abajo en el archivo, fuera de este fragmento pero sin cambios respecto al original), y no hay ningún `return` ni `throw` sin capturar que corte el flujo de `startRecording`: el `try/catch` absorbe el error y la ejecución continúa secuencialmente hacia `ondataavailable` y `start(1000)`, que se ejecutan exactamente igual que si el vault nunca hubiera fallado. La grabación arranca con normalidad; solo queda desactivada la persistencia al vault para toda la sesión (por el `vaultDisabledRef.current = true` que también gobierna la rama (c)/(b) en `ondataavailable`).

### 3.5 `git diff` → solo `useAudioRecorder.ts`

Confirmado en la sección 2: `git status --short` solo marca ` M artifacts/acta-express/src/hooks/useAudioRecorder.ts` como modificado; `recordingVault.ts` sigue como `??` preexistente de MT-H6a, sin tocar.

## 4. Desviaciones

Ninguna. Se implementó el contrato exactamente como está especificado (imports, refs, orden create→start, ausencia de `await` nuevos en `ondataavailable`, prohibición de borrar sesiones en este archivo).

## 5. Dudas

Ninguna. El tipado de `useAuth()` dentro del hook no generó ambigüedad: `user` es `User | null` (Firebase Auth, vía `AuthContextType`), y `user.uid` es válido en el branch `if (user && isVaultAvailable())`.

## 6. Estado commiteable

Sí, en cuanto a la implementación de esta micro-tarea (typecheck verde, DoD cumplido, diff acotado a `useAudioRecorder.ts`, sin desviaciones). No se realizó ningún commit — está fuera del rol de esta micro-tarea, según instrucción explícita del turno.

**Nota operativa:** durante la ejecución de esta tarea se activó momentáneamente una señal de "modo Plan" del harness que detuvo la ejecución después de aplicar el código pero antes de correr el DoD; el coordinador confirmó su desactivación y se retomó la tarea exactamente donde había quedado, sin reabrir ni modificar el código ya aplicado.
