# Informe MT-M3 — CTA "Cambiar micrófono" en el banner H4 (`home.tsx`)

**Ciclo:** 2026-07-30_selector_microfono · F4 · **Rol:** Ingeniero (Sonnet, rotación asistida)
**Repo:** `/home/pueblac/AndroidStudioProjects/ActaExpressWeb`, rama `linux`.

## Precondición (verificada antes de tocar nada)

```
$ git -C /home/pueblac/AndroidStudioProjects/ActaExpressWeb status --short
 M artifacts/acta-express/src/hooks/useAudioRecorder.ts
?? artifacts/acta-express/src/hooks/useMicDevices.ts
?? artifacts/acta-express/src/lib/micDevices.ts
```

Coincide con lo exigido por la spec (MT-M1 + MT-M2 aplicadas, nada más). Se procedió.

## Qué se hizo

Se editó **solo** `artifacts/acta-express/src/pages/home.tsx`, siguiendo el contrato literal:

1. Imports añadidos: `useMicDevices` (de `@/hooks/useMicDevices`) y `DropdownMenu`, `DropdownMenuContent`, `DropdownMenuItem`, `DropdownMenuTrigger` (de `@/components/ui/dropdown-menu`). `Mic` ya estaba importado de `lucide-react`, no requirió cambio.
2. Se destructuró `swapMicrophone` del `useAudioRecorder()` existente.
3. Se agregó `const { microphones } = useMicDevices(isRecording && micSilent);` justo después del hook `useMicLevel` — la lista solo se puebla con el banner activo (gate G0-c).
4. Se insertó el `DropdownMenu` con el botón `cta-cambiar-mic` y los `DropdownMenuItem` (`mic-option-${deviceId}` o el item deshabilitado "No se encontraron micrófonos") dentro del div `banner-mic-muerto`, tras el texto existente, sin alterar textos ni clases de severidad (destructive/ámbar). Se añadió `flex-wrap` al contenedor del banner para acomodar el nuevo botón, tal como permitía la spec.
5. Se agregó el handler `handleSwapMic(deviceId, label)` con la lógica exacta del contrato (toast informativo en éxito, toast destructivo con `res.message` en fallo).
6. No se tocó `micSilent`, `useMicLevel`, ni ningún estado del detector: el banner se sigue apagando únicamente cuando `useMicLevel` detecte señal real con el nuevo stream.

## Diff literal íntegro

```diff
diff --git a/artifacts/acta-express/src/pages/home.tsx b/artifacts/acta-express/src/pages/home.tsx
index 4a5ee63..31da874 100644
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
@@ -25,6 +26,12 @@ import { Switch } from "@/components/ui/switch";
 import { Label } from "@/components/ui/label";
 import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
 import { useToast } from "@/hooks/use-toast";
+import {
+  DropdownMenu,
+  DropdownMenuContent,
+  DropdownMenuItem,
+  DropdownMenuTrigger,
+} from "@/components/ui/dropdown-menu";
 import {
   AlertDialog,
   AlertDialogAction,
@@ -61,7 +68,8 @@ export default function Home() {
     error,
     captureMode,
     micStream,
-    vaultSessionId
+    vaultSessionId,
+    swapMicrophone
   } = useAudioRecorder();
 
   const { data: actas, isLoading: loadingActas } = useListActas();
@@ -96,6 +104,8 @@ export default function Home() {
   // MT-C3: solo cablea el hook para producir micSilent; el banner es MT-C4.
   const { micSilent } = useMicLevel(micStream, isRecording, modoReunion);
 
+  const { microphones } = useMicDevices(isRecording && micSilent);
+
   const [orphanSession, setOrphanSession] = useState<VaultSessionMeta | null>(null);
 
   const [deleteDialogActaId, setDeleteDialogActaId] = useState<string | null>(null);
@@ -212,6 +222,15 @@ export default function Home() {
     setDeleteDialogActaId(null);
   };
 
+  const handleSwapMic = async (deviceId: string, label: string) => {
+    const res = await swapMicrophone(deviceId);
+    if (res.ok) {
+      toast({ title: "Micrófono cambiado", description: `Ahora se usa "${label}". Verificando señal…` });
+    } else {
+      toast({ variant: "destructive", title: "No se pudo cambiar el micrófono", description: res.message });
+    }
+  };
+
   const handleDescartarOrphan = () => {
     if (!orphanSession) return;
     deleteSession(orphanSession.sessionId).catch(() => {});
@@ -347,14 +366,33 @@ export default function Home() {
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
+                <DropdownMenu>
+                  <DropdownMenuTrigger asChild>
+                    <Button size="sm" variant="outline" data-testid="cta-cambiar-mic" className="ml-2 shrink-0">
+                      <Mic className="mr-1 h-3 w-3" />
+                      Cambiar micrófono
+                    </Button>
+                  </DropdownMenuTrigger>
+                  <DropdownMenuContent align="center" className="w-64">
+                    {microphones.length === 0 ? (
+                      <DropdownMenuItem disabled>No se encontraron micrófonos</DropdownMenuItem>
+                    ) : (
+                      microphones.map((m) => (
+                        <DropdownMenuItem key={m.deviceId} data-testid={`mic-option-${m.deviceId}`} onClick={() => handleSwapMic(m.deviceId, m.label)}>
+                          {m.label}
+                        </DropdownMenuItem>
+                      ))
+                    )}
+                  </DropdownMenuContent>
+                </DropdownMenu>
               </div>
             )}
 
```

## Evidencia DoD

### 1. `pnpm run typecheck` → exit 0

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
EXIT_CODE=0
```

### 2. `grep -n "cta-cambiar-mic\|useMicDevices\|handleSwapMic\|mic-option-" artifacts/acta-express/src/pages/home.tsx`

```
5:import { useMicDevices } from "@/hooks/useMicDevices";
107:  const { microphones } = useMicDevices(isRecording && micSilent);
225:  const handleSwapMic = async (deviceId: string, label: string) => {
379:                    <Button size="sm" variant="outline" data-testid="cta-cambiar-mic" className="ml-2 shrink-0">
389:                        <DropdownMenuItem key={m.deviceId} data-testid={`mic-option-${m.deviceId}`} onClick={() => handleSwapMic(m.deviceId, m.label)}>
```

### 3. A/B razonado

**(a) Poblado condicionado al banner (G0-c):**
`const { microphones } = useMicDevices(isRecording && micSilent);` (línea 107). El hook `useMicDevices(active)` (código ya existente, MT-M1) solo llama a `listMicrophones()` y registra el listener `devicechange` cuando `active === true`; si `active` es `false` limpia el array y no registra listener (ver `useMicDevices.ts` líneas 7-11 y 21-26). Como `active = isRecording && micSilent` es exactamente la misma condición que gatilla `banner-mic-muerto` (línea ~354 del archivo, `{isRecording && micSilent && (...)}`), la lista de micrófonos solo se puebla mientras el banner está visible; en cuanto el banner se apaga (`micSilent` pasa a `false`), `active` se vuelve `false`, el hook limpia `microphones` a `[]` y desregistra el listener `devicechange`. No hay listener activo con el banner apagado.

**(b) Swap OK → banner permanece hasta señal real:**
En `handleSwapMic` (líneas 225-231), tras `swapMicrophone(deviceId)` con `res.ok === true`, el único efecto es `toast({ title: "Micrófono cambiado", ... })` — no hay ninguna llamada a `setMicSilent`, ni se toca el estado devuelto por `useMicLevel`, ni se desmonta/oculta manualmente el div `banner-mic-muerto`. El banner sigue condicionado exclusivamente a `isRecording && micSilent` (línea 354, sin cambios), y `micSilent` es un valor que solo `useMicLevel` (archivo no tocado en esta MT) puede mutar al observar RMS ≥ umbral en el `micStream` nuevo tras el swap. Por tanto el banner permanece renderizado hasta que el detector confirme señal real por sí mismo — cero ocultamiento optimista.

**(c) Swap fallido → toast destructivo:**
Si `res.ok === false` (por ejemplo `swapMicrophone` retorna `{ ok: false, message: "..." }` en cualquiera de sus ramas de error, ver `useAudioRecorder.ts` líneas 363-388), el handler ejecuta `toast({ variant: "destructive", title: "No se pudo cambiar el micrófono", description: res.message })`, propagando literalmente el `message` del hook. Tampoco en esta rama se toca `micSilent` ni el banner.

### 4. `git diff artifacts/acta-express/src/pages/home.tsx` literal íntegro

(Incluido arriba en la sección "Diff literal íntegro" — idéntico al capturado con `git diff -- artifacts/acta-express/src/pages/home.tsx`.)

## Desviaciones

Ninguna respecto al contrato de texto/testids/handler. Única adición no textual: se agregó `flex-wrap` a las dos ramas del `className` del banner (presencial/virtual) para acomodar el nuevo botón sin romper el layout en pantallas angostas — explícitamente permitido por la spec ("Ajusta el layout del banner si hace falta ... sin cambiar textos ni estilos de severidad existentes"). No se tocaron colores, iconos de severidad ni copy.

## Dudas

Ninguna que exija cambiar el contrato. No fue necesario detenerse.

## Estado de `git status --short` tras la implementación

```
 M artifacts/acta-express/src/hooks/useAudioRecorder.ts
 M artifacts/acta-express/src/pages/home.tsx
?? artifacts/acta-express/src/hooks/useMicDevices.ts
?? artifacts/acta-express/src/lib/micDevices.ts
```

Solo `home.tsx` fue modificado por esta MT (el `M` en `useAudioRecorder.ts` y los `??` en `micDevices.ts`/`useMicDevices.ts` son precondición heredada de MT-M1/MT-M2, no tocados aquí).

## Commiteable

Sí, a criterio del contrato cumplido — **no se hizo commit** (fuera de alcance del rol Ingeniero; corresponde a rotación posterior según metodología v2).
