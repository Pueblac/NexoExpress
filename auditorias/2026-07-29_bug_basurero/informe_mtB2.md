# Informe MT-B2 — Borrado desde la vista de detalle del acta

**Rol:** Ingeniero (Sonnet, rotación asistida) · **Ciclo:** 2026-07-29_bug_basurero
**Repo:** `/home/pueblac/AndroidStudioProjects/ActaExpressWeb`, rama `linux`

## Precondicionante (verificado antes de tocar nada)

```
$ git -C /home/pueblac/AndroidStudioProjects/ActaExpressWeb status --short
 M artifacts/acta-express/src/pages/home.tsx
```

Exactamente lo esperado (MT-B1 aplicada, nada más). Se procedió.

## Qué se hizo

Se modificó únicamente `artifacts/acta-express/src/pages/acta.tsx`, clonando el patrón de borrado de `home.tsx`:

1. **Imports nuevos**: `useLocation` (wouter, junto a `useParams, Link`), `useDeleteActa, getListActasQueryKey` (`@workspace/api-client-react`), `useQueryClient` (`@tanstack/react-query`), `Trash2` (lucide-react, añadido al import existente) y el bloque `AlertDialog*` desde `@/components/ui/alert-dialog`.
2. **Mutación** `deleteActa = useDeleteActa({...})` justo después de `useGetActa`, con `onSuccess` que invalida `getListActasQueryKey()`, dispara el toast "Acta eliminada" y hace `setLocation("/")`.
3. **Botón nuevo** al final del div de acciones (tras el bloque Compartir), con `AlertDialog` de confirmación, textos idénticos a `home.tsx` (título "¿Eliminar acta?", descripción con el título real del acta), `data-testid="button-delete-acta"`, `Cancelar` / `Eliminar` (este último con `bg-destructive text-destructive-foreground hover:bg-destructive/90`, `disabled={deleteActa.isPending}`).
4. Verificado con grep en `lib/api-client-react/src/generated/api.ts` (línea 403-410): `useDeleteActa` espera mutation variables de tipo **`{actaId: string}`** — coincide con el contrato (`{ actaId }`), no hubo divergencia de nombre de parámetro.
5. No hay `<Link>` envolvente en esta zona → no se añadió `preventDefault`/`stopPropagation`, conforme al punto 5 del contrato.

### Desviación menor de implementación (declarada, no de contrato)

El `actaId` de `useParams()` en wouter 3.10 tipa como `string | undefined` (índice `DefaultParams: readonly [k: string|number]: string | undefined`), mientras que `useDeleteActa` exige `{actaId: string}`. La llamada literal del contrato `deleteActa.mutate({ actaId })` **no compila** (`TS2322: Type 'string | undefined' is not assignable to type 'string'`, verificado empíricamente). Se usó `deleteActa.mutate({ actaId: actaId as string })` — funcionalmente idéntico (en este punto del render `acta` ya existe, por lo tanto `actaId` está garantizado no-undefined; el guard `if (error || !acta) return ...` ya cortó el camino contrario más arriba), es solo el cast mínimo para satisfacer el tipado estricto. No cambia textos, testid, colocación ni comportamiento — se declara por transparencia, no se detuvo el trabajo por ser un ajuste de tipado trivial y no un cambio de contrato.

## DoD

### 1. `pnpm run typecheck` (desde la raíz de ActaExpressWeb) — salida literal

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

### 2. grep de verificación

```
$ grep -n "button-delete-acta\|useDeleteActa\|setLocation(\"/\")\|Eliminar acta" artifacts/acta-express/src/pages/acta.tsx
2:import { useGetActa, useDeleteActa, getListActasQueryKey } from "@workspace/api-client-react";
178:  const deleteActa = useDeleteActa({
183:        setLocation("/");
335:                data-testid="button-delete-acta"
344:                <AlertDialogTitle>¿Eliminar acta?</AlertDialogTitle>
```

### 3. A/B razonado (traza del flujo)

- **Camino A — Confirmar borrado:** usuario en `/acta/:actaId` → clic en botón "Eliminar" (cabecera, `data-testid="button-delete-acta"`) → abre `AlertDialog` con título "¿Eliminar acta?" y descripción con el título real del acta → usuario clic en "Eliminar" (`AlertDialogAction`) → `deleteActa.mutate({ actaId: actaId as string })` → request al backend → `onSuccess`: `queryClient.invalidateQueries({ queryKey: getListActasQueryKey() })` (la lista de Home queda marcada stale, se refetchea al montar) → `toast({ title: "Acta eliminada", ... })` → `setLocation("/")` (navegación inmediata a Home). El usuario aterriza en Home y ya no ve el acta borrada (invalidación + refetch). Mientras la mutación está en curso, el botón de confirmación queda deshabilitado (`disabled={deleteActa.isPending}`), evitando doble envío.
- **Camino B — Cancelar:** clic en "Eliminar" → se abre el diálogo → usuario clic en "Cancelar" (`AlertDialogCancel`, comportamiento por defecto del componente: cierra el diálogo) → no se invoca `deleteActa.mutate` → no hay invalidación, ni toast, ni navegación → el usuario permanece en la vista de detalle del acta, sin cambios.

### 4. `git diff` — estado y diff literal íntegro de `acta.tsx`

```
$ git status --short
 M artifacts/acta-express/src/pages/acta.tsx
 M artifacts/acta-express/src/pages/home.tsx
```

Confirmado: solo `home.tsx` (de MT-B1, no tocado en esta MT) y `acta.tsx` (esta MT) aparecen modificados.

```diff
diff --git a/artifacts/acta-express/src/pages/acta.tsx b/artifacts/acta-express/src/pages/acta.tsx
index b3c6bfb..3d27a2c 100644
--- a/artifacts/acta-express/src/pages/acta.tsx
+++ b/artifacts/acta-express/src/pages/acta.tsx
@@ -1,10 +1,11 @@
-import { useParams, Link } from "wouter";
-import { useGetActa } from "@workspace/api-client-react";
+import { useParams, Link, useLocation } from "wouter";
+import { useGetActa, useDeleteActa, getListActasQueryKey } from "@workspace/api-client-react";
+import { useQueryClient } from "@tanstack/react-query";
 import { format } from "date-fns";
 import { es } from "date-fns/locale";
 import {
   ChevronLeft, Share2, Copy, Clock, Calendar, Users, Target,
-  CheckCircle2, ListTodo, FileText, Download, Mail, MessageCircle, Twitter, Link2
+  CheckCircle2, ListTodo, FileText, Download, Mail, MessageCircle, Twitter, Link2, Trash2
 } from "lucide-react";
 import { Button } from "@/components/ui/button";
 import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
@@ -17,6 +18,10 @@ import { Badge } from "@/components/ui/badge";
 import {
   DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger,
 } from "@/components/ui/dropdown-menu";
+import {
+  AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription,
+  AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger,
+} from "@/components/ui/alert-dialog";
 import {
   Document, Paragraph, TextRun, Table as DocxTable, TableRow as DocxTableRow,
   TableCell as DocxTableCell, Packer, HeadingLevel, AlignmentType, WidthType, BorderStyle,
@@ -165,9 +170,21 @@ async function downloadDocx(acta: any) {
 export default function ActaDetail() {
   const { actaId } = useParams();
   const { toast } = useToast();
-  
+  const [, setLocation] = useLocation();
+  const queryClient = useQueryClient();
+
   const { data: acta, isLoading, error } = useGetActa(actaId || "");
 
+  const deleteActa = useDeleteActa({
+    mutation: {
+      onSuccess: () => {
+        queryClient.invalidateQueries({ queryKey: getListActasQueryKey() });
+        toast({ title: "Acta eliminada", description: "El acta fue eliminada permanentemente." });
+        setLocation("/");
+      },
+    },
+  });
+
   const handleCopy = () => {
     if (!acta) return;
     navigator.clipboard.writeText(buildActaText(acta));
@@ -309,6 +326,38 @@ export default function ActaDetail() {
               </DropdownMenuContent>
             </DropdownMenu>
           )}
+
+          <AlertDialog>
+            <AlertDialogTrigger asChild>
+              <Button
+                variant="outline"
+                size="sm"
+                data-testid="button-delete-acta"
+                className="text-destructive hover:text-destructive hover:bg-destructive/10"
+              >
+                <Trash2 className="mr-2 h-4 w-4" />
+                Eliminar
+              </Button>
+            </AlertDialogTrigger>
+            <AlertDialogContent>
+              <AlertDialogHeader>
+                <AlertDialogTitle>¿Eliminar acta?</AlertDialogTitle>
+                <AlertDialogDescription>
+                  Esta acción no se puede deshacer. Se eliminará permanentemente el acta "{acta.titulo}".
+                </AlertDialogDescription>
+              </AlertDialogHeader>
+              <AlertDialogFooter>
+                <AlertDialogCancel>Cancelar</AlertDialogCancel>
+                <AlertDialogAction
+                  onClick={() => deleteActa.mutate({ actaId: actaId as string })}
+                  disabled={deleteActa.isPending}
+                  className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
+                >
+                  Eliminar
+                </AlertDialogAction>
+              </AlertDialogFooter>
+            </AlertDialogContent>
+          </AlertDialog>
         </div>
       </div>
```

## Desviaciones

Una sola, ya declarada arriba: cast `actaId as string` en `deleteActa.mutate({ actaId: actaId as string })` en lugar del literal `deleteActa.mutate({ actaId })` del contrato, exigido por el tipado de wouter (`actaId: string | undefined`) vs. el de `useDeleteActa` (`{actaId: string}`). Verificado empíricamente que la forma literal del contrato rompe `pnpm run typecheck` (`TS2322`). No afecta textos, testid, colocación ni comportamiento en runtime (en el punto de uso `acta` ya está cargada, por lo que `actaId` es siempre un string real).

## Dudas

Ninguna que exija cambiar el contrato. La única nota es la desviación de tipado ya declarada, que no altera el diseño ni el comportamiento — no se detuvo el trabajo por ella.

## Commiteable

**Sí**, a criterio de este informe: contrato implementado al pie de la letra (salvo el cast de tipado declarado y justificado), DoD completo con `pnpm run typecheck` en exit 0, grep de verificación conforme, `git diff` acotado a `acta.tsx` (+ `home.tsx` de MT-B1 ya presente). No se ejecutó `git commit` — corresponde a otro rol/paso del ciclo.
