# Informe MT-H6e — Re-chequeo periódico de huérfanas (F3′, fix del E2E de F5)

**Rol:** Ingeniero (Sonnet, rotación asistida) · **Repo:** `/home/pueblac/AndroidStudioProjects/ActaExpressWeb`

## Precondición (verificada antes de implementar)

```
$ git -C /home/pueblac/AndroidStudioProjects/ActaExpressWeb status --short
 M artifacts/acta-express/src/hooks/useAudioRecorder.ts
 M artifacts/acta-express/src/pages/home.tsx
?? artifacts/acta-express/src/lib/recordingVault.ts
```

Coincide EXACTAMENTE con lo exigido en el paso 2 de las instrucciones. Se continuó.

## 1. Qué se hizo

Se modificó **solo** `artifacts/acta-express/src/pages/home.tsx`:

1. Se añadió la constante de módulo `const ORPHAN_POLL_MS = 10000;` justo antes de `export default function Home()` (después de `formatCreatedAt`).
2. Se reemplazó el useEffect de detección de huérfana al montar (el bloque comentado `// H6c: detección de sesión huérfana al montar...`, líneas 100-106 antes del cambio) por el bloque exacto del contrato: mismo chequeo al montar + `setInterval` cada `ORPHAN_POLL_MS` mientras no haya `orphanSession`, con `cancelled`/`clearInterval` en el cleanup y dependencias `[user?.uid, orphanSession]`.

No se tocó nada más: ni `recordingVault.ts`, ni `useAudioRecorder.ts`, ni la tarjeta de recuperación, ni los handlers `handleDescartarOrphan`/`handleRecuperarOrphan` (esos ya existían en el working tree de MT-H6a..d, precondición confirmada arriba).

## 2. git diff literal íntegro

**Nota importante sobre el alcance de este diff:** `HEAD` (commit `35580f0`) corresponde a la versión de `home.tsx` previa a toda la tanda H6 (verificado con `git show HEAD:...home.tsx`, que no tiene `orphanSession`, `recordingVault`, ni handlers de recuperación). Es decir, el working tree ya traía **sin commitear** todo el trabajo de MT-H6a..d antes de que esta MT-H6e empezara (así lo confirma la precondición del paso 2: `home.tsx` ya estaba en estado `M`). Por eso `git diff artifacts/acta-express/src/pages/home.tsx` contra `HEAD` incluye ese trabajo previo además del cambio de esta MT — **no** puede mostrar "solo el bloque del efecto + constante" tal como sugiere el punto 5 del DoD, porque no hay un commit intermedio contra el cual aislar únicamente el delta de H6e. Se reporta el diff completo (literal, tal como pide el DoD) y, más abajo, se aísla explícitamente el delta propio de MT-H6e.

```diff
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

### Delta aislado de MT-H6e (dentro del diff anterior)

Únicamente estos dos hunks son atribuibles a esta MT (verificado: solo se ejecutaron dos operaciones de edición, ambas sobre estas líneas):

```diff
@@ -37,6 +46,8 @@ function formatCreatedAt(iso: unknown): string {
   }
 }
 
+const ORPHAN_POLL_MS = 10000; // constante de módulo, junto a los imports o encima del componente
+
 export default function Home() {
```

```diff
-  // H6c: detección de sesión huérfana al montar (crash/cierre de pestaña previo).
-  useEffect(() => {
-    if (!user || !isVaultAvailable()) return;
-    purgeStaleKeepNewest(user.uid)
-      .then((orphan) => setOrphanSession(orphan))
-      .catch(() => {}); // vault roto → sin tarjeta, app intacta
-  }, [user?.uid]);
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
```

Todo lo demás en el diff completo (import `blobToBase64`, import de `@/lib/recordingVault`, `vaultSessionId` desestructurado, `deleteSession` en `onSuccess`/`onError` de `processAudio`, `handleDescartarOrphan`, `handleRecuperarOrphan` y la tarjeta JSX `card-recuperacion`) ya estaba presente en el working tree **antes** de que esta MT comenzara — es el trabajo de MT-H6a..d que la precondición del paso 2 confirmó como estado de partida.

## 3. Evidencia DoD literal

### 3.1 `pnpm run typecheck`

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

### 3.2 `grep -n "ORPHAN_POLL_MS\|setInterval(check" artifacts/acta-express/src/pages/home.tsx`

```
49:const ORPHAN_POLL_MS = 10000; // constante de módulo, junto a los imports o encima del componente
116:    const intervalId = window.setInterval(check, ORPHAN_POLL_MS);
```

### 3.3 A/B razonado con timeline (citando líneas del diff)

**Contexto compartido:** `isStale` (en `recordingVault.ts:205-206`, no tocado) define `now - meta.lastChunkAt >= VAULT_STALE_MS` con `VAULT_STALE_MS = 30000` (línea 17, fijo — "cambio 5 del dictamen, NO reinterpretar"). `purgeStaleKeepNewest` solo devuelve una sesión cuando está stale.

Escenario: crash en **t=0** (el último chunk quedó grabado en **t=−1 s**, o sea `lastChunkAt = t0 − 1000ms`). El usuario reabre la pestaña en **t=5 s**.

**Timeline B — código ANTERIOR (bug, sin poll):**
```
- (H6c original, líneas 100-106 antes del cambio)
useEffect(() => {
    if (!user || !isVaultAvailable()) return;
    purgeStaleKeepNewest(user.uid)
      .then((orphan) => setOrphanSession(orphan))
      .catch(() => {});
  }, [user?.uid]);
```
- `t≈5 s`: Home monta. El efecto corre UNA vez porque `user?.uid` es la única dependencia y no cambia entre renders del mismo usuario. `purgeStaleKeepNewest` calcula `delta = 5s − (−1s) = 6s`; `6000 < 30000` → NO stale → no hay huérfana → `setOrphanSession(null)`.
- El efecto **no vuelve a ejecutarse** (su única dep, `user?.uid`, sigue igual) — no hay ningún mecanismo que lo reintente.
- `t=35 s` (delta real = 36 s ≥ 30 s, la sesión YA es stale): nada la detecta. La tarjeta **jamás aparece** sin que el usuario navegue (p. ej. entrar a un acta y volver, lo que remonta `Home` y vuelve a disparar el efecto una sola vez). Esto es exactamente el bug reportado por el Director en el E2E de F5 parte 2 (27-07).

**Timeline A — código NUEVO (con poll, líneas citadas del diff arriba):**
```
useEffect(() => {
    if (!user || !isVaultAvailable() || orphanSession) return;
    let cancelled = false;
    const check = () => { ... };
    check();
    const intervalId = window.setInterval(check, ORPHAN_POLL_MS); // ORPHAN_POLL_MS = 10000
    return () => { cancelled = true; window.clearInterval(intervalId); };
  }, [user?.uid, orphanSession]);
```
- `t≈5 s`: Home monta. `check()` corre inmediatamente (línea `check();` antes del `setInterval`). `delta = 6s < 30s` → no stale → sin tarjeta. Se arma el `setInterval(check, 10000)`.
- `t≈15 s`: poll #1. `delta = 16s < 30s` → sin tarjeta.
- `t≈25 s`: poll #2. `delta = 26s < 30s` → sin tarjeta.
- `t≈35 s`: poll #3. `delta = 36s ≥ 30s` → `isStale` verdadero → `purgeStaleKeepNewest` devuelve la huérfana → `if (!cancelled && orphan) setOrphanSession(orphan)` → `orphanSession` deja de ser `null` → la tarjeta `card-recuperacion` se renderiza (condicionada además a `!isRecording && !processAudio.isPending`, sin tocar) **sin que el usuario haya navegado**.
- Latencia total observada: ~35-40 s tras el crash, dentro del límite aceptado por el contrato (~40 s = 30 s stale + 10 s de poll).

### 3.4 A/B del apagado del poll (cleanup)

Al ejecutarse `setOrphanSession(orphan)` en el poll de `t≈35 s`, el estado `orphanSession` cambia de `null` a la meta de la sesión. Como `orphanSession` es dependencia del efecto (`}, [user?.uid, orphanSession]);`), React:
1. Ejecuta primero el **cleanup** de la instancia anterior del efecto: `cancelled = true; window.clearInterval(intervalId);` — el `setInterval` corriendo desde `t≈5 s` queda limpiado.
2. Vuelve a ejecutar el cuerpo del efecto con el nuevo valor: `if (!user || !isVaultAvailable() || orphanSession) return;` — como `orphanSession` ahora es truthy, la condición corta y retorna temprano **sin crear un nuevo `setInterval`**.

Resultado: el poll queda apagado en cuanto se detecta y muestra la huérfana, tal como exige el contrato (punto 2 del spec: "al encontrarla se detiene"). Si el usuario luego Descarta o Recupera (`orphanSession` vuelve a `null` vía `handleDescartarOrphan`/`onSuccess` de `handleRecuperarOrphan`, ninguno tocado), el efecto se re-ejecuta y el poll se reactiva — comportamiento descrito como inocuo e idempotente en el punto 2 del contrato, no exigía verificación adicional.

## 4. Desviaciones

Ninguna respecto al contrato de implementación (se tocó únicamente el bloque indicado + la constante, en `home.tsx`, sin dependencias nuevas, sin tocar `recordingVault.ts`/`useAudioRecorder.ts`/`VAULT_STALE_MS`/tarjeta/handlers).

Una aclaración factual sobre el DoD (no es una desviación de implementación, es una discrepancia entre lo que el punto 5 del DoD anticipaba y lo que el comando literal produce): `git diff artifacts/acta-express/src/pages/home.tsx` no puede mostrar "solo el bloque del efecto + constante" porque `HEAD` no tiene commiteado el trabajo previo de MT-H6a..d (confirmado: `git show HEAD:...home.tsx` no tiene `orphanSession` ni nada de la tanda H6). El diff completo, por tanto, incluye ese trabajo previo además del cambio de esta MT. Se reportó el diff íntegro literal (sección 2) y, aparte, se aisló explícitamente el delta propio de MT-H6e para dejar trazado que la implementación de esta MT se ciñó al contrato.

## 5. Dudas

Ninguna. `ORPHAN_POLL_MS = 10000` y `VAULT_STALE_MS = 30000` se dejaron fijos, sin reinterpretación.

## 6. Estado commiteable

No se hizo commit (fuera de alcance de esta MT, según el rol). El working tree queda con:
```
 M artifacts/acta-express/src/hooks/useAudioRecorder.ts
 M artifacts/acta-express/src/pages/home.tsx
?? artifacts/acta-express/src/lib/recordingVault.ts
```
`typecheck` en verde (exit 0). A criterio del Arquitecto/Director si se considera "commiteable sí" (DoD de código cumplido) o si se prefiere esperar a un E2E adicional antes de commitear la tanda completa H6a..e.
