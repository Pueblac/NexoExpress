# Informe MT-H6c — Tarjeta de recuperación + ciclo de vida del vault en `home.tsx`

**Ciclo:** 2026-07-25_resiliencia_grabacion · F4 · Rol: Ingeniero (Sonnet, rotación asistida)
**Repo tocado:** `/home/pueblac/AndroidStudioProjects/ActaExpressWeb`

## 1. Qué se hizo

Precondición verificada antes de tocar nada: `git status --short` en ActaExpressWeb mostró EXACTAMENTE:
```
 M artifacts/acta-express/src/hooks/useAudioRecorder.ts
?? artifacts/acta-express/src/lib/recordingVault.ts
```
(MT-H6a+H6b aplicadas, nada más — precondición OK, se procedió).

Cambios implementados, ciñéndose al contrato de la spec `spec_mtH6c.md`:

1. **`useAudioRecorder.ts`** — única línea tocada: `function blobToBase64` → `export function blobToBase64` (línea 22). El resto del diff de este archivo ya existía antes de mi turno (MT-H6a+H6b).
2. **`home.tsx`**:
   - Imports: `blobToBase64` añadido al import existente de `@/hooks/useAudioRecorder`; nuevo import agrupado desde `@/lib/recordingVault` con `purgeStaleKeepNewest, getSession, readChunks, deleteSession, isStale, isVaultAvailable, type VaultSessionMeta`.
   - `vaultSessionId` desestructurado del hook `useAudioRecorder()`.
   - Estado `orphanSession: VaultSessionMeta | null`.
   - `useEffect` de detección al montar (deps `[user?.uid]`) que llama `purgeStaleKeepNewest(user.uid)` y setea `orphanSession`, con `.catch(() => {})`.
   - Tarjeta `data-testid="card-recuperacion"` con texto "Se encontró una grabación interrumpida (~X min)" y botones `btn-recuperar` / `btn-descartar`, colocada justo encima de `selector-modo-reunion`, renderizada solo si `orphanSession && !isRecording && !processAudio.isPending`.
   - `handleDescartarOrphan`: `deleteSession` + `setOrphanSession(null)` + toast "Grabación descartada".
   - `handleRecuperarOrphan`: re-verifica heartbeat (`getSession` + `isStale`) antes de procesar (mitigación T2×T5), lee chunks, arma el Blob, convierte a base64 con `blobToBase64`, y llama `processAudio.mutate(...)` con callbacks per-call (`onSuccess` borra y limpia tarjeta; `onError` borra solo si 422, conserva en red/5xx).
   - Ciclo de vida del flujo normal en los callbacks CENTRALES de `processAudio`: `onSuccess` añade `if (vaultSessionId) deleteSession(vaultSessionId).catch(() => {});`; `onError` añade `if ((err as any)?.status === 422 && vaultSessionId) deleteSession(vaultSessionId).catch(() => {});`.

No se tocó `recordingVault.ts` ni el `useEffect` de auto-proceso (línea 161-177 en el archivo final, antes 139-155). No se añadieron dependencias nuevas. No se hizo commit.

## 2. Git diff literal íntegro

```diff
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
diff --git a/artifacts/acta-express/src/pages/home.tsx b/artifacts/acta-express/src/pages/home.tsx
index dc77478..0e984cc 100644
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
@@ -50,7 +59,8 @@ export default function Home() {
     duration,
     error,
     captureMode,
-    micStream
+    micStream,
+    vaultSessionId
   } = useAudioRecorder();
 
   const { data: actas, isLoading: loadingActas } = useListActas();
@@ -85,10 +95,21 @@ export default function Home() {
   // MT-C3: solo cablea el hook para producir micSilent; el banner es MT-C4.
   const { micSilent } = useMicLevel(micStream, isRecording, modoReunion);
 
+  const [orphanSession, setOrphanSession] = useState<VaultSessionMeta | null>(null);
+
+  // H6c: detección de sesión huérfana al montar (crash/cierre de pestaña previo).
+  useEffect(() => {
+    if (!user || !isVaultAvailable()) return;
+    purgeStaleKeepNewest(user.uid)
+      .then((orphan) => setOrphanSession(orphan))
+      .catch(() => {}); // vault roto → sin tarjeta, app intacta
+  }, [user?.uid]);
+
   const processAudio = useProcessAudio({
     mutation: {
       onSuccess: (acta, variables) => {
         queryClient.invalidateQueries({ queryKey: getListActasQueryKey() });
+        if (vaultSessionId) deleteSession(vaultSessionId).catch(() => {});
 
         // Detect silent/empty audio result
         const silenceKeywords = ["no se pudo", "no audible", "no hay audio", "sin contenido", "silencio"];
@@ -118,6 +139,7 @@ export default function Home() {
           title: "Error al procesar",
           description: err.message || "Hubo un problema analizando el audio.",
         });
+        if ((err as any)?.status === 422 && vaultSessionId) deleteSession(vaultSessionId).catch(() => {});
       }
     }
   });
@@ -173,6 +195,54 @@ export default function Home() {
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
@@ -271,6 +341,35 @@ export default function Home() {
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

**Nota sobre el diff de `useAudioRecorder.ts`:** el precondicionante ya mostraba este archivo como `M` (MT-H6a+H6b aplicadas antes de mi turno). Mi único cambio en él es la línea `function blobToBase64` → `export function blobToBase64` (bloque `@@ -14,9 +16,10 @@` / `@@ -17,3 +19,3 @@` en el hunk del blobToBase64). El resto del contenido de ese diff (createSession, appendChunk, vaultSessionId, etc.) ya estaba en el working tree por MT-H6a+H6b y no fue tocado por mí, tal como exige la restricción de la spec ("SOLO... la línea `export`").

## 3. Evidencia DoD literal

### 3.1 `pnpm run typecheck` → exit 0

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
artifacts/mockup-sandbox typecheck: Done
artifacts/acta-express typecheck: Done
```
Comando de verificación de código de salida ejecutado por separado:
```
$ pnpm run typecheck > .../typecheck_out.txt 2>&1; echo "EXIT=$?"
EXIT=0
```

### 3.2 Grep de identificadores contractuales

```
$ grep -n "card-recuperacion\|btn-recuperar\|btn-descartar\|purgeStaleKeepNewest\|getSession\|readChunks\|deleteSession\|isStale\|status === 422\|blobToBase64" artifacts/acta-express/src/pages/home.tsx
3:import { useAudioRecorder, type ModoReunion, blobToBase64 } from "@/hooks/useAudioRecorder";
6:  purgeStaleKeepNewest,
7:  getSession,
8:  readChunks,
9:  deleteSession,
10:  isStale,
103:    purgeStaleKeepNewest(user.uid)
112:        if (vaultSessionId) deleteSession(vaultSessionId).catch(() => {});
142:        if ((err as any)?.status === 422 && vaultSessionId) deleteSession(vaultSessionId).catch(() => {});
200:    deleteSession(orphanSession.sessionId).catch(() => {});
207:    const meta = await getSession(orphanSession.sessionId).catch(() => null);
208:    if (!meta || !isStale(meta)) { // mitigación T2×T5: volvió a latir u desapareció
213:    const chunks = await readChunks(meta.sessionId).catch(() => []);
215:      deleteSession(meta.sessionId).catch(() => {});
221:    const audioBase64Recuperado = await blobToBase64(blob);
233:          deleteSession(meta.sessionId).catch(() => {});
237:          if (err?.status === 422) {
238:            deleteSession(meta.sessionId).catch(() => {});
346:                data-testid="card-recuperacion"
355:                    data-testid="btn-recuperar"
362:                    data-testid="btn-descartar"
```

```
$ grep -n "export function blobToBase64" artifacts/acta-express/src/hooks/useAudioRecorder.ts
22:export function blobToBase64(blob: Blob): Promise<string> {
```

### 3.3 A/B razonado de los 4 caminos del ciclo de vida (citando líneas del archivo final `home.tsx`)

**(a) Acta OK en flujo normal → borra la sesión del vault.**
En los callbacks CENTRALES de `processAudio` (`onSuccess`, línea 110-112):
```
110:      onSuccess: (acta, variables) => {
111:        queryClient.invalidateQueries({ queryKey: getListActasQueryKey() });
112:        if (vaultSessionId) deleteSession(vaultSessionId).catch(() => {});
```
`vaultSessionId` es el de la grabación EN CURSO del hook (expuesto por MT-H6b); si existe, se borra al confirmarse éxito del acta.

**(b) 422 en flujo normal → ídem (borra).**
`onError` central, línea 136-142:
```
136:      onError: (err: any) => {
137:        toast({
138:          variant: "destructive",
139:          title: "Error al procesar",
140:          description: err.message || "Hubo un problema analizando el audio.",
141:        });
142:        if ((err as any)?.status === 422 && vaultSessionId) deleteSession(vaultSessionId).catch(() => {});
```
Solo se borra si `status === 422` (rechazo determinista del server); cualquier otro código (red, 5xx) NO entra en el `if` y la sesión se conserva.

**(c) Recuperación con acta OK → delete per-call + tarjeta fuera.**
Callback per-call dentro de `handleRecuperarOrphan`, línea 232-235:
```
232:        onSuccess: () => {
233:          deleteSession(meta.sessionId).catch(() => {});
234:          setOrphanSession(null);
235:        },
```
Este `onSuccess` per-call se ejecuta ADEMÁS del central (línea 110-112, react-query invoca ambos); en la ruta de recuperación `vaultSessionId` del hook es `null` (no hay grabación en curso), así que el central no hace nada útil y este per-call cubre la sesión recuperada (`meta.sessionId`), borrándola y retirando la tarjeta.

**(d) Recuperación con error de RED → sesión CONSERVADA, tarjeta sigue.**
`onError` per-call, línea 236-240:
```
236:        onError: (err: any) => {
237:          if (err?.status === 422) {
238:            deleteSession(meta.sessionId).catch(() => {});
239:            setOrphanSession(null);
240:          } // red/5xx: conservar (tarjeta sigue)
```
Si `err.status` no es 422 (timeout de red, 5xx, etc.), el `if` no entra: no se borra `meta.sessionId` ni se limpia `orphanSession`, por lo que la tarjeta `card-recuperacion` (línea 344, condición `orphanSession && !isRecording && !processAudio.isPending`) sigue visible al terminar el pending — el usuario puede reintentar Recuperar.

**Traza de la mitigación T2×T5 (heartbeat re-verificado al pulsar Recuperar):**
Línea 206-212:
```
206:    if (!orphanSession) return;
207:    const meta = await getSession(orphanSession.sessionId).catch(() => null);
208:    if (!meta || !isStale(meta)) { // mitigación T2×T5: volvió a latir u desapareció
209:      setOrphanSession(null);
210:      toast({ title: "Grabación no recuperable", description: "Esa grabación sigue activa en otra pestaña o ya no existe." });
211:      return;
212:    }
```
Antes de leer chunks o procesar nada, se relee `meta` fresco del vault (no el `orphanSession` cacheado en el estado de React, que puede estar desactualizado) y se comprueba `isStale(meta)` con el `now` actual. Si la sesión volvió a latir (otra pestaña la sigue grabando: `lastChunkAt` reciente → `isStale` false) o si ya no existe (`meta === null`, p.ej. porque otra pestaña la completó y la borró), se limpia la tarjeta, se muestra el toast "Grabación no recuperable" y se hace `return` — **se sale sin llamar a `readChunks`, sin construir el Blob y sin invocar `processAudio.mutate`**. Esto es exactamente la salida-sin-procesar que exige la mitigación T2×T5 del Arquitecto.

### 3.4 A/B del doble disparo (T4) — Recuperar NO puede re-disparar el `useEffect` de auto-proceso

El `useEffect` de auto-proceso (líneas 161-177 del archivo final) depende exclusivamente del estado interno del hook `useAudioRecorder()`:
```
159:  const lastProcessedAudioRef = useRef<string | null>(null);
160:
161:  useEffect(() => {
162:      if (
163:        audioBase64 && !isRecording && duration > 0 &&
164:        !processAudio.isPending &&
165:        lastProcessedAudioRef.current !== audioBase64
166:      ) {
167:        lastProcessedAudioRef.current = audioBase64;
168:        processAudio.mutate({
169:          data: {
170:            audioBase64,
171:            mimeType: "audio/webm",
172:            msDuration: duration,
173:            generarSintesis: generarSintesisRef.current
174:          }
175:        });
176:      }
177:    }, [audioBase64, isRecording, duration]); // eslint-disable-line react-hooks/exhaustive-deps
```
Se dispara cuando cambian `audioBase64`, `isRecording` o `duration` — las tres son valores de estado **del hook `useAudioRecorder()`** (`audioBase64`, `duration` desestructurados en las líneas 45-64 del componente).

`handleRecuperarOrphan` (líneas 205-244) construye su propia variable local `audioBase64Recuperado` (línea 221: `const audioBase64Recuperado = await blobToBase64(blob);`) a partir del `Blob` reconstruido con los chunks del vault (línea 220) — **nunca llama a `setAudioBase64`, `setDuration` ni a ningún setter del hook**. El hook `useAudioRecorder()` no expone ningún setter de esos campos hacia `home.tsx` (su `UseAudioRecorderReturn` solo expone getters: `audioBase64`, `duration`, etc. — ver `useAudioRecorder.ts` líneas 9-20). Por tanto:
- `audioBase64` (el del hook, usado en el efecto) permanece intacto durante y después de la recuperación.
- `duration` (el del hook) permanece intacto.
- `lastProcessedAudioRef.current` (línea 159) no se toca en `handleRecuperarOrphan` — solo se escribe dentro del propio efecto (línea 167), que no se ejecuta porque sus deps no cambiaron.

Como ninguna de las tres dependencias del efecto (`audioBase64`, `isRecording`, `duration`) cambia como consecuencia de `handleRecuperarOrphan`, React no vuelve a evaluar el cuerpo del efecto, y aunque lo evaluara, la condición `lastProcessedAudioRef.current !== audioBase64` seguiría en su estado previo (ninguno de los dos lados cambió). El disparo de `processAudio.mutate` para el audio recuperado ocurre EXCLUSIVAMENTE en la ruta imperativa de `handleRecuperarOrphan` (línea 222), como exige la spec. No hay doble disparo posible.

## 4. Desviaciones

Ninguna. El contrato se implementó literalmente: mismos nombres de función/handler explícitos en la spec (`handleDescartarOrphan`/`handleRecuperarOrphan` son los nombres naturales para los botones "Descartar"/"Recuperar" — la spec no fijó nombre de función, solo el comportamiento y los `data-testid`), mismos textos, mismos `data-testid`, misma política 422-borra/red-conserva, misma fórmula de minutos, mismo umbral `Math.max(1000, ...)` en `msDuration` de recuperación.

Nota menor no funcional: el tipado del `onError` per-call en `handleRecuperarOrphan` (línea 236) se resolvió con `err: any` tal como autoriza el "Protocolo de dudas" de la spec ante problemas de tipado.

## 5. Dudas

Ninguna.

## 6. Estado commiteable

Sí (típecheck en verde, contrato cumplido, sin tocar `recordingVault.ts` ni el efecto de auto-proceso, sin dependencias nuevas). No se hizo commit — fuera del alcance de esta micro-tarea.
