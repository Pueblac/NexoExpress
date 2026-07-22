# Informe de Implementación — MT-C1 (rotación asistida, Sonnet)

## 1. Qué se hizo (resumen por archivo)

**`artifacts/acta-express/src/pages/home.tsx`** (único archivo tocado):
- Import nuevo: `RadioGroup`, `RadioGroupItem` desde `@/components/ui/radio-group`.
- Tipo `type ModoReunion = "presencial" | "virtual";` arriba del componente `Home`.
- Estado + ref + handler `modoReunion` calcados del patrón `generarSintesis`; clave `actaexpress:modoReunion:${user.uid}`, default `"presencial"`.
- UI: `<div data-testid="selector-modo-reunion">` con `RadioGroup` controlado (`value`/`onValueChange`), 2 `RadioGroupItem` (`modo-presencial`/`modo-virtual`) con labels y subtítulos exactos; `disabled={isRecording || processAudio.isPending}`.
- NO se tocó `useAudioRecorder.ts`, ni la firma/llamada de `startRecording`, ni el efecto de envío.

## 2. Diff literal íntegro

```diff
diff --git a/artifacts/acta-express/src/pages/home.tsx b/artifacts/acta-express/src/pages/home.tsx
index 158bdb3..42968b9 100644
--- a/artifacts/acta-express/src/pages/home.tsx
+++ b/artifacts/acta-express/src/pages/home.tsx
@@ -13,6 +13,7 @@ import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
 import { Skeleton } from "@/components/ui/skeleton";
 import { Switch } from "@/components/ui/switch";
 import { Label } from "@/components/ui/label";
+import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
 import { useToast } from "@/hooks/use-toast";
@@ -35,6 +36,8 @@ function formatCreatedAt(iso: unknown): string {
   }
 }
 
+type ModoReunion = "presencial" | "virtual";
+
 export default function Home() {
@@ -67,6 +70,18 @@ export default function Home() {
     }
   };
 
+  const [modoReunion, setModoReunion] = useState<ModoReunion>(() => {
+    if (!user) return "presencial";
+    const saved = localStorage.getItem(`actaexpress:modoReunion:${user.uid}`);
+    return saved === "virtual" ? "virtual" : "presencial";
+  });
+  const modoReunionRef = useRef(modoReunion);
+  modoReunionRef.current = modoReunion;
+  const handleModoReunionChange = (modo: ModoReunion) => {
+    setModoReunion(modo);
+    if (user) localStorage.setItem(`actaexpress:modoReunion:${user.uid}`, modo);
+  };
+
   const processAudio = useProcessAudio({
@@ -227,6 +242,47 @@ export default function Home() {
               )}
             </AnimatePresence>
 
+            <div data-testid="selector-modo-reunion" className="flex justify-center pt-2">
+              <RadioGroup
+                value={modoReunion}
+                onValueChange={(value) => handleModoReunionChange(value as ModoReunion)}
+                disabled={isRecording || processAudio.isPending}
+                className="flex flex-col gap-3 sm:flex-row sm:gap-6"
+              >
+                <div className="flex items-start gap-2">
+                  <RadioGroupItem value="presencial" id="modo-presencial" data-testid="modo-presencial" className="mt-1" />
+                  <Label htmlFor="modo-presencial" className="cursor-pointer text-left">
+                    <span className="block font-medium">Reunión presencial</span>
+                    <span className="block text-xs text-muted-foreground">Sonido ambiente (micrófono directo)</span>
+                  </Label>
+                </div>
+                <div className="flex items-start gap-2">
+                  <RadioGroupItem value="virtual" id="modo-virtual" data-testid="modo-virtual" className="mt-1" />
+                  <Label htmlFor="modo-virtual" className="cursor-pointer text-left">
+                    <span className="block font-medium">Reunión virtual</span>
+                    <span className="block text-xs text-muted-foreground">Audio de la pestaña + micrófono</span>
+                  </Label>
+                </div>
+              </RadioGroup>
+            </div>
+
             <div className="flex items-center justify-center gap-2 pt-2">
               <Switch
```
`git status`: solo `artifacts/acta-express/src/pages/home.tsx` modificado (sin stage, sin commit).

## 3. Evidencia literal del DoD

1. `pnpm run typecheck` → los 4 proyectos `Done`, **EXIT_CODE=0**.
2. grep `modoReunion|selector-modo-reunion|actaexpress:modoReunion` → estado (73), initializer con la clave (75), ref (78-79), handler con setItem (82), testid (246), value (250).
3. `git diff --stat` → `home.tsx | 56 +++`, 1 file changed, 56 insertions. SOLO home.tsx.
4. Vía de UI: `RadioGroup`+`RadioGroupItem` de shadcn (el archivo existe). No se usó la vía segmentada alternativa.

## 4. Desviaciones
Ninguna.

## 5. Dudas del Ingeniero
Los `data-testid` de opción se colocaron sobre el `RadioGroupItem` (control con `role="radio"`) en vez del `<div>` contenedor. Interpretación: el testid apunta al control interactivo (lo que se clickea/verifica `aria-checked`). No altera contrato. **Resolución del Arquitecto:** aceptada — es la ubicación correcta para tests de interacción; no reabre F3.

## 6. Estado commiteable
Verde. typecheck exit 0; solo home.tsx; sin cambios a medias; sin commit. Listo para MT-C2.
