# Informe MT-M6 — Selector de micrófono en MODAL + nota del SO + ícono (F3′)

**Ciclo:** 2026-07-30_selector_microfono · F3′→F4 · **Rol:** Ingeniero (Sonnet, rotación asistida)
**Repo:** `/home/pueblac/AndroidStudioProjects/ActaExpressWeb`, rama `linux`.
**Spec:** `spec_mtM6.md`

## Precondición

Verificada antes de tocar nada (`git status --short`):

```
 M artifacts/acta-express/src/hooks/useAudioRecorder.ts
 M artifacts/acta-express/src/pages/home.tsx
?? artifacts/acta-express/src/hooks/useMicDevices.ts
?? artifacts/acta-express/src/lib/micDevices.ts
```

Coincide con la tanda M exigida (2 M + 2 ??). `micDevices.ts` ya tenía `friendlyName`/`detail` en `MicDevice` (MT-M7 aplicada). Continué.

## Implementación (solo `home.tsx`)

1. Import de `dialog.tsx` (`Dialog`, `DialogContent`, `DialogHeader`, `DialogTitle`, `DialogDescription`) en reemplazo del import de `dropdown-menu` (`DropdownMenu`/`DropdownMenuContent`/`DropdownMenuItem`/`DropdownMenuTrigger`), que quedó sin ningún uso tras el paso 2 y se eliminó por completo.
2. Estado nuevo `const [micSelectorOpen, setMicSelectorOpen] = useState(false);` junto a `deleteDialogActaId`.
3. El botón del banner (`data-testid="cta-cambiar-mic"`, mismo texto) dejó de ser `DropdownMenuTrigger`; ahora es un `Button` con `onClick={() => setMicSelectorOpen(true)}`.
4. Modal `Dialog` colocado inmediatamente después del bloque condicional del banner (`{isRecording && micSilent && (...)}`), fuera de esa condición — así, si el banner desaparece con el modal abierto, el modal sigue abierto (punto 5 del contrato, sin lógica añadida). Contenido, testids y texto de la nota del SO copiados literalmente del contrato.
5. `handleSwapMic`: en éxito (`res.ok`) se añadió `setMicSelectorOpen(false)` después del toast existente; en fallo el modal no se toca (queda abierto). El label del toast ahora usa `m.friendlyName` (pasado como segundo argumento de `handleSwapMic` desde las opciones del modal), sin cambiar la firma de la función.
6. Ícono del botón de grabar: el `<Mic>` del estado "listo para grabar" (zona `w-32 h-32 rounded-full`) subió de `h-12 w-12` a `h-14 w-14` — un paso en la escala de Tailwind (…10, 12, 14, 16…) tomando el valor real preexistente (`h-12 w-12`, no el `h-8 w-8` de ejemplo del spec) como base.

## DoD

### 1. `pnpm run typecheck` (salida literal)

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
EXIT_CODE=0
```

### 2. Grep de contrato

```
$ grep -n "dialog-selector-mic\|nota-so-mic\|micSelectorOpen\|friendlyName\|mic-option-" artifacts/acta-express/src/pages/home.tsx
122:  const [micSelectorOpen, setMicSelectorOpen] = useState(false);
396:            <Dialog open={micSelectorOpen} onOpenChange={setMicSelectorOpen}>
397:              <DialogContent data-testid="dialog-selector-mic" className="max-w-md">
412:                        data-testid={`mic-option-${m.deviceId}`}
414:                        onClick={() => handleSwapMic(m.deviceId, m.friendlyName)}
416:                        <span className="font-medium">{m.friendlyName}</span>
422:                <p className="text-xs text-muted-foreground border-t border-border/50 pt-3" data-testid="nota-so-mic">

$ grep -n "DropdownMenu" artifacts/acta-express/src/pages/home.tsx
(sin resultados — import y uso eliminados por completo)
```

### 3. A/B razonado

- **(a) CTA → modal superpuesto (no dropdown):** el `onClick` del botón `cta-cambiar-mic` solo hace `setMicSelectorOpen(true)`; ya no existe `DropdownMenu` en el archivo (grep vacío arriba). El `Dialog` de Radix (mismo primitive que el diálogo de borrado de actas) se porta fuera del árbol del banner mediante su `Portal` interno → overlay centrado sobre toda la pantalla, no un desplegable anclado al botón.
- **(b) swap ok → toast + modal se cierra + banner espera señal real:** en `handleSwapMic`, la rama `res.ok` dispara el toast "Micrófono cambiado" y luego `setMicSelectorOpen(false)`. El banner (`banner-mic-muerto`) no se toca aquí — sigue condicionado a `isRecording && micSilent`, que solo baja cuando `useMicLevel` detecte señal real; MT-M6 no le añade ni le quita lógica a esa condición.
- **(c) swap fallido → modal abierto + toast destructive:** la rama `else` de `handleSwapMic` solo hace el toast `destructive`; no hay ningún `setMicSelectorOpen(false)` en esa rama, así que el modal permanece `open` y el usuario puede intentar otra opción sin reabrir nada.
- **(d) doble click en dos opciones → segundo rechazado por el cerrojo del hook:** cada opción del modal llama a `handleSwapMic(m.deviceId, m.friendlyName)` → `swapMicrophone(deviceId)` (hook `useAudioRecorder`, no tocado por esta MT). El cerrojo `isSwappingRef` ya auditado en MT-M5 (punto 4 de esa tabla) sigue intacto: el segundo click, mientras el primero está en vuelo, recibe `{ok:false, message:"..."}` síncronamente antes de tocar `getUserMedia`. Ahora es observable en la UI porque ambas opciones son botones dentro del mismo modal abierto (antes, con el `DropdownMenu`, el menú se cerraba tras el primer click y ocultaba la carrera); con el modal, el usuario puede hacer los dos clicks reales sobre las dos opciones visibles sin que el menú se autocierre entre uno y otro.

### 4. `git diff` literal íntegro de `home.tsx`

```diff
diff --git a/artifacts/acta-express/src/pages/home.tsx b/artifacts/acta-express/src/pages/home.tsx
index 4a5ee63..aba7f08 100644
--- a/artifacts/acta-express/src/pages/home.tsx
+++ b/artifacts/acta-express/src/pages/home.tsx
@@ -2,6 +2,7 @@ import { useEffect, useRef, useState } from "react";
 import { useAuth } from "@/context/AuthContext";
 import { useAudioRecorder, type ModoReunion, blobToBase64 } from "@/hooks/useAudioRecorder";
 import { useMicLevel } from "@/hooks/useMicLevel";
+import { useMicDevices } from "@/hooks/useMicDevices";
 import {
   purgeStaleKeepNewest,
   getSession,
@@ -25,6 +26,13 @@ import { Switch } from "@/components/ui/switch";
 import { Label } from "@/components/ui/label";
 import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
 import { useToast } from "@/hooks/use-toast";
+import {
+  Dialog,
+  DialogContent,
+  DialogHeader,
+  DialogTitle,
+  DialogDescription,
+} from "@/components/ui/dialog";
 import {
   AlertDialog,
   AlertDialogAction,
@@ -61,7 +69,9 @@ export default function Home() {
     error,
     captureMode,
     micStream,
-    vaultSessionId
+    vaultSessionId,
+    swapMicrophone,
+    micFallbackNotice
   } = useAudioRecorder();
 
   const { data: actas, isLoading: loadingActas } = useListActas();
@@ -96,10 +106,21 @@ export default function Home() {
   // MT-C3: solo cablea el hook para producir micSilent; el banner es MT-C4.
   const { micSilent } = useMicLevel(micStream, isRecording, modoReunion);
 
+  const { microphones } = useMicDevices(isRecording && micSilent);
+
+  // MT-M4: aviso no bloqueante cuando el micrófono preferido no está disponible (fallback declarado).
+  useEffect(() => {
+    if (micFallbackNotice) {
+      toast({ title: "Micrófono", description: micFallbackNotice });
+    }
+  }, [micFallbackNotice]); // eslint-disable-line react-hooks/exhaustive-deps
+
   const [orphanSession, setOrphanSession] = useState<VaultSessionMeta | null>(null);
 
   const [deleteDialogActaId, setDeleteDialogActaId] = useState<string | null>(null);
 
+  const [micSelectorOpen, setMicSelectorOpen] = useState(false);
+
   // H6c+H6e: detección de sesión huérfana — al montar y re-chequeo periódico
   // (la sesión del crash tarda VAULT_STALE_MS en volverse stale; sin poll, la
   // tarjeta solo aparecía al remontar Home — bug del E2E 27-07).
@@ -212,6 +233,16 @@ export default function Home() {
     setDeleteDialogActaId(null);
   };
 
+  const handleSwapMic = async (deviceId: string, label: string) => {
+    const res = await swapMicrophone(deviceId);
+    if (res.ok) {
+      toast({ title: "Micrófono cambiado", description: `Ahora se usa "${label}". Verificando señal…` });
+      setMicSelectorOpen(false);
+    } else {
+      toast({ variant: "destructive", title: "No se pudo cambiar el micrófono", description: res.message });
+    }
+  };
+
   const handleDescartarOrphan = () => {
     if (!orphanSession) return;
     deleteSession(orphanSession.sessionId).catch(() => {});
@@ -293,7 +324,7 @@ export default function Home() {
                 ) : isRecording ? (
                   <Square className="h-10 w-10 text-white fill-current" />
                 ) : (
-                  <Mic className="h-12 w-12 text-white" />
+                  <Mic className="h-14 w-14 text-white" />
                 )}
               </Button>
             </div>
@@ -347,17 +378,55 @@ export default function Home() {
                 data-testid="banner-mic-muerto"
                 className={
                   modoReunion === "presencial"
-                    ? "flex items-center justify-center gap-2 text-destructive text-sm mt-2 bg-destructive/10 px-4 py-2 rounded-md"
-                    : "flex items-center justify-center gap-2 text-amber-500 text-sm mt-2 bg-amber-500/10 px-4 py-2 rounded-md"
+                    ? "flex items-center justify-center gap-2 flex-wrap text-destructive text-sm mt-2 bg-destructive/10 px-4 py-2 rounded-md"
+                    : "flex items-center justify-center gap-2 flex-wrap text-amber-500 text-sm mt-2 bg-amber-500/10 px-4 py-2 rounded-md"
                 }
               >
                 <AlertCircle className="w-4 h-4" />
                 {modoReunion === "presencial"
                   ? "⚠️ No se detecta señal de tu micrófono — revisa que no esté silenciado en el sistema."
                   : "Tu micrófono no aporta señal. Si solo escuchas la reunión está bien; si querías hablar, revisa que no esté silenciado."}
+                <Button size="sm" variant="outline" data-testid="cta-cambiar-mic" className="ml-2 shrink-0" onClick={() => setMicSelectorOpen(true)}>
+                  <Mic className="mr-1 h-3 w-3" />
+                  Cambiar micrófono
+                </Button>
               </div>
             )}
 
+            <Dialog open={micSelectorOpen} onOpenChange={setMicSelectorOpen}>
+              <DialogContent data-testid="dialog-selector-mic" className="max-w-md">
+                <DialogHeader>
+                  <DialogTitle>Cambiar micrófono</DialogTitle>
+                  <DialogDescription>
+                    Elige el dispositivo que quieres usar. La grabación continúa sin cortarse.
+                  </DialogDescription>
+                </DialogHeader>
+                <div className="flex flex-col gap-2">
+                  {microphones.length === 0 ? (
+                    <p className="text-sm text-muted-foreground">No se encontraron micrófonos.</p>
+                  ) : (
+                    microphones.map((m) => (
+                      <Button
+                        key={m.deviceId}
+                        variant="outline"
+                        data-testid={`mic-option-${m.deviceId}`}
+                        className="justify-start h-auto py-2 flex-col items-start"
+                        onClick={() => handleSwapMic(m.deviceId, m.friendlyName)}
+                      >
+                        <span className="font-medium">{m.friendlyName}</span>
+                        {m.detail && <span className="text-xs text-muted-foreground">{m.detail}</span>}
+                      </Button>
+                    ))
+                  )}
+                </div>
+                <p className="text-xs text-muted-foreground border-t border-border/50 pt-3" data-testid="nota-so-mic">
+                  Nota: tu sistema operativo puede cambiar el micrófono activo por su cuenta (por ejemplo, al
+                  conectar auriculares). Si el que eliges no responde, revisa que no esté silenciado en el
+                  sistema, o desconecta el dispositivo que interfiere.
+                </p>
+              </DialogContent>
+            </Dialog>
+
             {orphanSession && !isRecording && !processAudio.isPending && (
               <div
                 data-testid="card-recuperacion"
```

Nota: el diff mostrado es el íntegro de `home.tsx` respecto a `HEAD` (incluye el acumulado no commiteado de MT-M3/M4, ya presente en la precondición, más el trabajo propio de esta MT: import de `dialog`, eliminación de `dropdown-menu`, estado `micSelectorOpen`, botón sin dropdown, modal con nota del SO, cierre en éxito de `handleSwapMic`, e ícono `h-14 w-14`). `git diff --stat` de solo `home.tsx`: `1 file changed, 73 insertions(+), 4 deletions(-)`.

## Desviaciones

Ninguna respecto al contrato. Único punto donde se ejerció criterio dentro de lo declarado por el propio spec: el ejemplo de tamaño de ícono (`h-8 w-8` → `h-10 w-10`) no correspondía al valor real preexistente (`h-12 w-12`); se aplicó "un paso arriba" sobre el valor real, resultando en `h-14 w-14`, tal como el punto 6 del contrato pedía explícitamente declarar.

## Dudas

Ninguna que exigiera DETENTE.

## ¿Commiteable?

No se hizo commit (fuera de mandato). `pnpm run typecheck` en verde (exit 0), grep de contrato conforme, `DropdownMenu` totalmente eliminado de `home.tsx`. Listo para handoff al siguiente rol del ciclo.
