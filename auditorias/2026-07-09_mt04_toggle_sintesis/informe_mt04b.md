# Expediente 2026-07-09_mt04_toggle_sintesis — Informe de Implementación MT-04b

**Modo de rotación:** ASISTIDA (decisión del Director, 09-07-2026): el Ingeniero corrió como subagente Sonnet con contexto limpio lanzado desde la sesión del Arquitecto, recibiendo únicamente la spec archivada (`spec_mt04b.md`) + inicialización de identidad. Informe archivado literal abajo; F5 ejecutada por el Arquitecto sobre el repo real. Gates y tramo Auditor siguen manuales.
**Validación F5:** ver ANEXO al final.

---

# Informe de Implementación — MT-04b: Toggle "Análisis profundo" + envío del flag

**Ciclo:** 2026-07-09_mt04_toggle_sintesis · **Fase:** F4 (implementación según spec) · **Rol:** Ingeniero

## 1. Qué se hizo

Se modificó únicamente `artifacts/acta-express/src/pages/home.tsx` según el contrato §3 de la spec:

1. **Estado + persistencia por usuario**: nuevo estado `generarSintesis` inicializado desde `localStorage["actaexpress:generarSintesis:${user.uid}"]` (default `false` si no hay clave o no hay `user`). El handler `handleGenerarSintesisChange` actualiza el estado y persiste solo si `user` existe.
2. **Ref sincronizado**: `generarSintesisRef` replicado literal (diseño C3).
3. **Efecto blindado**: se reemplazó el efecto de disparo original por la versión literal del diseño C7 — guard con `!processAudio.isPending` y `lastProcessedAudioRef.current !== audioBase64`, marca asignada antes del `mutate`, sin limpieza en `onError`, y `generarSintesis` enviado como boolean explícito desde `generarSintesisRef.current`.
4. **UI del toggle**: bloque `Switch` + `Label` insertado dentro del `<div className="space-y-2">`, después del `<AnimatePresence>` del badge de captura y antes del bloque `error`, con `data-testid="switch-sintesis"`, etiqueta "Análisis profundo", subtítulo "Transcripción completa y análisis (tarda más)" en `text-xs text-muted-foreground`, `disabled={isRecording || processAudio.isPending}`, elemento siempre presente (sin condicional, sin layout shift).
5. **Toast extendido**: `onSuccess` ahora recibe `(acta, variables)`; cuando `variables.data.generarSintesis === true` y no es el caso de audio silencioso, la descripción cambia al texto extendido especificado.

Se usó el campo `generarSintesis?: boolean` ya presente en `AudioInput` (`lib/api-client-react/src/generated/api.schemas.ts:53`, sin tocar) — confirma que MT-04a está cerrada; no fue necesario ningún cast.

## 2. Diff literal

### `git status --short` (tras la implementación)

```
 M artifacts/acta-express/src/pages/home.tsx
 M lib/api-client-react/src/generated/api.schemas.ts
 M lib/api-zod/src/generated/api.ts
 M lib/api-zod/src/generated/types/acta.ts
 M lib/api-zod/src/generated/types/audioInput.ts
 M lib/api-zod/src/generated/types/index.ts
?? lib/api-zod/src/generated/types/actaPlataforma.ts
```

Los 5 `M` bajo `lib/*/generated/` y el `?? actaPlataforma.ts` son exactamente los cambios sin commit heredados de MT-04a (declarados como prerrequisito en §0 de la spec) — no se tocaron ni revirtieron. El único archivo nuevo modificado por esta tarea es `artifacts/acta-express/src/pages/home.tsx`.

### `git diff -- artifacts/acta-express/src/pages/home.tsx`

```diff
diff --git a/artifacts/acta-express/src/pages/home.tsx b/artifacts/acta-express/src/pages/home.tsx
index 75f7c89..741c2ba 100644
--- a/artifacts/acta-express/src/pages/home.tsx
+++ b/artifacts/acta-express/src/pages/home.tsx
@@ -1,4 +1,4 @@
-import { useEffect } from "react";
+import { useEffect, useRef, useState } from "react";
 import { useAuth } from "@/context/AuthContext";
 import { useAudioRecorder } from "@/hooks/useAudioRecorder";
 import { useListActas, useProcessAudio, useDeleteActa, getListActasQueryKey } from "@workspace/api-client-react";
@@ -11,6 +11,8 @@ import { Mic, Square, Trash2, Clock, Users, FileText, Loader2, Volume2, AlertCir
 import { Button } from "@/components/ui/button";
 import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
 import { Skeleton } from "@/components/ui/skeleton";
+import { Switch } from "@/components/ui/switch";
+import { Label } from "@/components/ui/label";
 import { useToast } from "@/hooks/use-toast";
 import {
   AlertDialog,
@@ -49,10 +51,25 @@ export default function Home() {
   } = useAudioRecorder();
 
   const { data: actas, isLoading: loadingActas } = useListActas();
-  
+
+  const [generarSintesis, setGenerarSintesis] = useState<boolean>(() => {
+    if (!user) return false;
+    return localStorage.getItem(`actaexpress:generarSintesis:${user.uid}`) === "true";
+  });
+
+  const generarSintesisRef = useRef(generarSintesis);
+  generarSintesisRef.current = generarSintesis;
+
+  const handleGenerarSintesisChange = (checked: boolean) => {
+    setGenerarSintesis(checked);
+    if (user) {
+      localStorage.setItem(`actaexpress:generarSintesis:${user.uid}`, String(checked));
+    }
+  };
+
   const processAudio = useProcessAudio({
     mutation: {
-      onSuccess: (acta) => {
+      onSuccess: (acta, variables) => {
         queryClient.invalidateQueries({ queryKey: getListActasQueryKey() });
 
         // Detect silent/empty audio result
@@ -71,7 +88,9 @@ export default function Home() {
         } else {
           toast({
             title: "¡Acta generada!",
-            description: "Tu reunión ha sido procesada con éxito.",
+            description: variables.data.generarSintesis === true
+              ? "Tu reunión ha sido procesada con éxito. El análisis profundo se está generando en segundo plano."
+              : "Tu reunión ha sido procesada con éxito.",
           });
         }
       },
@@ -97,17 +116,25 @@ export default function Home() {
     }
   });
 
+  const lastProcessedAudioRef = useRef<string | null>(null);
+
   useEffect(() => {
-    if (audioBase64 && !isRecording && duration > 0) {
-      processAudio.mutate({
-        data: {
-          audioBase64,
-          mimeType: "audio/webm",
-          msDuration: duration
-        }
-      });
-    }
-  }, [audioBase64, isRecording, duration]); // eslint-disable-line react-hooks/exhaustive-deps
+      if (
+        audioBase64 && !isRecording && duration > 0 &&
+        !processAudio.isPending &&
+        lastProcessedAudioRef.current !== audioBase64
+      ) {
+        lastProcessedAudioRef.current = audioBase64;
+        processAudio.mutate({
+          data: {
+            audioBase64,
+            mimeType: "audio/webm",
+            msDuration: duration,
+            generarSintesis: generarSintesisRef.current
+          }
+        });
+      }
+    }, [audioBase64, isRecording, duration]); // eslint-disable-line react-hooks/exhaustive-deps
 
   const formatDuration = (ms: number) => {
     const totalSeconds = Math.floor(ms / 1000);
@@ -195,6 +222,24 @@ export default function Home() {
               )}
             </AnimatePresence>
 
+            <div className="flex items-center justify-center gap-2 pt-2">
+              <Switch
+                id="switch-sintesis"
+                data-testid="switch-sintesis"
+                checked={generarSintesis}
+                onCheckedChange={handleGenerarSintesisChange}
+                disabled={isRecording || processAudio.isPending}
+              />
+              <div className="text-left">
+                <Label htmlFor="switch-sintesis" className="cursor-pointer">
+                  Análisis profundo
+                </Label>
+                <p className="text-xs text-muted-foreground">
+                  Transcripción completa y análisis (tarda más)
+                </p>
+              </div>
+            </div>
+
             {error && (
               <div className="flex items-center justify-center gap-2 text-destructive text-sm mt-4 bg-destructive/10 px-4 py-2 rounded-md">
                 <AlertCircle className="w-4 h-4" />
```

## 3. Evidencia literal del DoD

**1) `git status --short` — ANTES de tocar `home.tsx`:** los 5 archivos `generated/` modificados + 1 nuevo de MT-04a, sin commit — coincide con el prerrequisito. No se tocaron ni revirtieron.

**2) `pnpm run typecheck`:** los 4 proyectos `Done`, exit 0. Confirma que `AudioInput.generarSintesis` ya existe tipado (sin `as any` ni casts).

**3) `grep -n "isSuccess" home.tsx`:** sin salida — 0 resultados (bug B1 evitado).

**4) `grep -n "lastProcessedAudioRef\|generarSintesisRef\|switch-sintesis" home.tsx`:** presentes en líneas 60-61, 119, 125, 127, 133, 227-228, 234.

**5) Verificación E2E en navegador:** **NO EJECUTADO** — entorno del agente sin sesión Firebase autenticada ni dispositivo de audio. Declarado conforme a §5.5 de la spec (no es desviación); queda para F5 con el Director.

## 4. Desviaciones

Ninguna. La implementación replica literalmente el efecto blindado (diseño C7) y el ref sincronizado (diseño C3) tal como fueron aprobados, sin modificaciones de diseño.

## 5. Dudas

Ninguna.

## 6. Estado commiteable

Working tree: cambios de MT-04a (generated/, heredados) + `home.tsx` (esta tarea). Sin commit, según instrucción. Typecheck exit 0.

## 7. AVISO DE TRASPASO FINAL

**CICLO:** 2026-07-09_mt04_toggle_sintesis · **FASE:** F4→F5 · **TURNO DE:** Arquitecto · **ENTREGAR:** informe_mt04b.md · **ACCIÓN:** verificación F5.

---
---

# ANEXO — Verificación F5 del Arquitecto (09-07-2026) — parte 1: código

**DoD re-EJECUTADO por el Arquitecto sobre el repo real (no leído del informe):**

1. `git status --short` → idéntico al declarado (6 M + 1 ??; único archivo de esta MT: `home.tsx`). ✅
2. `grep -n "isSuccess" home.tsx` → exit 1, 0 resultados. ✅
3. `pnpm run typecheck` → re-ejecutado: 4 proyectos `Done`, `TYPECHECK_EXIT=0`. ✅
4. Lectura directa del efecto implementado (`home.tsx:119-138`): **idéntico línea a línea al parche aprobado en ronda 2** (marca antes del mutate, `!isPending`, sin `isSuccess`, boolean explícito vía ref). ✅
5. Contrato verificado en el archivo real: clave `actaexpress:generarSintesis:${user.uid}` (líneas 57 y 66), toast extendido condicionado a `variables.data.generarSintesis === true` (línea 92), Switch con testid/disabled/subtítulo según spec. ✅
6. `grep "as any"` → 3 ocurrencias, TODAS preexistentes (heurística de silencio líneas 77-78 y `handleDelete` línea 321); **0 en el diff de esta MT** (verificado: `git diff | grep -c "as any"` = 0). La prohibición de la spec no se violó. *(Nota fuera de alcance: esas 3 preexistentes son candidatas a limpieza en un ciclo futuro.)*
7. Adición menor no especificada: `id="switch-sintesis"` en el Switch — necesaria para el `htmlFor` del Label (accesibilidad); se acepta, no altera el diseño.

**Veredicto F5 parte 1: código FIEL al diseño aprobado.**
**Pendiente F5 parte 2 (con el Director): E2E real** — grabación en navegador con toggle ON → verificar `sintesis/{actaId}` poblada en Firestore (evidencia literal → `evidencia_mt04.md`); segunda grabación con toggle OFF en la misma sesión (verifica multi-grabación y flag `false`). Después: F6 (auditoría de la tanda MT-04a+b con diff íntegro).
