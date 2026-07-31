# Informe MT-B1 r2 — Fix del basurero con diálogo CONTROLADO

**Ciclo:** 2026-07-29_bug_basurero · **Rol:** Ingeniero (Sonnet, rotación asistida)
**Repo:** `/home/pueblac/AndroidStudioProjects/ActaExpressWeb`, rama `linux`.
**Archivo tocado:** `artifacts/acta-express/src/pages/home.tsx` (único; `acta.tsx` no se tocó).

## Precondición

```
$ git -C /home/pueblac/AndroidStudioProjects/ActaExpressWeb status --short
 M artifacts/acta-express/src/pages/acta.tsx
 M artifacts/acta-express/src/pages/home.tsx
```

Coincide exactamente con lo exigido por el turno. Se procedió.

## Qué se hizo

1. Añadido el estado `deleteDialogActaId` junto a los demás `useState` del componente (justo después de `orphanSession`, línea ~101).
2. Reestructurado el bloque del `AlertDialog` de cada card (zona ~503-534):
   - Se eliminó `<AlertDialogTrigger asChild>` (y el `</AlertDialogTrigger>` de cierre).
   - `AlertDialog` pasó a controlado: `open={deleteDialogActaId === acta.id}` y `onOpenChange={(open) => { if (!open) setDeleteDialogActaId(null); }}`.
   - El `Button` de la papelera quedó como hijo directo del `AlertDialog` (ya no como Trigger), con `onClick={(e) => { e.preventDefault(); e.stopPropagation(); setDeleteDialogActaId(acta.id); }}`.
   - `AlertDialogCancel` volvió a `onClick={e => e.stopPropagation()}` (sin `preventDefault`).
   - Cabecera, textos y `AlertDialogAction` quedaron intactos (solo se limpiaron espacios finales sobrantes en las etiquetas `Button`/`AlertDialogAction`, sin cambio funcional).
3. Import: se eliminó `AlertDialogTrigger` del import de `@/components/ui/alert-dialog` (confirmado sin otro uso en el archivo antes de quitarlo).
4. En `handleDelete` (ahora ~207-212): se añadió `setDeleteDialogActaId(null);` tras `deleteActa.mutate(...)`.

No se tocó `acta.tsx` (MT-B2, ajeno a esta MT).

## Diff literal íntegro (`git diff artifacts/acta-express/src/pages/home.tsx`)

```diff
diff --git a/artifacts/acta-express/src/pages/home.tsx b/artifacts/acta-express/src/pages/home.tsx
index b5d5ef2..4a5ee63 100644
--- a/artifacts/acta-express/src/pages/home.tsx
+++ b/artifacts/acta-express/src/pages/home.tsx
@@ -34,7 +34,6 @@ import {
   AlertDialogFooter,
   AlertDialogHeader,
   AlertDialogTitle,
-  AlertDialogTrigger,
 } from "@/components/ui/alert-dialog";
 
 function formatCreatedAt(iso: unknown): string {
@@ -99,6 +98,8 @@ export default function Home() {
 
   const [orphanSession, setOrphanSession] = useState<VaultSessionMeta | null>(null);
 
+  const [deleteDialogActaId, setDeleteDialogActaId] = useState<string | null>(null);
+
   // H6c+H6e: detección de sesión huérfana — al montar y re-chequeo periódico
   // (la sesión del crash tarda VAULT_STALE_MS en volverse stale; sin poll, la
   // tarjeta solo aparecía al remontar Home — bug del E2E 27-07).
@@ -208,6 +209,7 @@ export default function Home() {
     e.preventDefault();
     e.stopPropagation();
     deleteActa.mutate({ actaId: id });
+    setDeleteDialogActaId(null);
   };
 
   const handleDescartarOrphan = () => {
@@ -500,18 +502,19 @@ export default function Home() {
                       <CardTitle className="text-lg line-clamp-1 leading-tight" title={acta.titulo}>
                         {acta.titulo}
                       </CardTitle>
-                      <AlertDialog>
-                        <AlertDialogTrigger asChild>
-                          <Button 
-                            data-testid={`button-delete-${acta.id}`}
-                            variant="ghost" 
-                            size="icon" 
-                            className="h-8 w-8 text-muted-foreground hover:text-destructive opacity-0 group-hover:opacity-100 transition-opacity -mt-1 -mr-2 shrink-0"
-                            onClick={(e) => e.stopPropagation()}
-                          >
-                            <Trash2 className="h-4 w-4" />
-                          </Button>
-                        </AlertDialogTrigger>
+                      <AlertDialog
+                        open={deleteDialogActaId === acta.id}
+                        onOpenChange={(open) => { if (!open) setDeleteDialogActaId(null); }}
+                      >
+                        <Button
+                          data-testid={`button-delete-${acta.id}`}
+                          variant="ghost"
+                          size="icon"
+                          className="h-8 w-8 text-muted-foreground hover:text-destructive opacity-0 group-hover:opacity-100 transition-opacity -mt-1 -mr-2 shrink-0"
+                          onClick={(e) => { e.preventDefault(); e.stopPropagation(); setDeleteDialogActaId(acta.id); }}
+                        >
+                          <Trash2 className="h-4 w-4" />
+                        </Button>
                         <AlertDialogContent onClick={e => e.stopPropagation()}>
                           <AlertDialogHeader>
                             <AlertDialogTitle>¿Eliminar acta?</AlertDialogTitle>
@@ -521,7 +524,7 @@ export default function Home() {
                           </AlertDialogHeader>
                           <AlertDialogFooter>
                             <AlertDialogCancel onClick={e => e.stopPropagation()}>Cancelar</AlertDialogCancel>
-                            <AlertDialogAction 
+                            <AlertDialogAction
                               onClick={(e) => handleDelete(acta.id, e as any)}
                               className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                             >
```

Nota: este `git diff` es contra el último commit (HEAD), no contra r1 aisladamente — la r1 nunca se commiteó, así que las líneas `-` que se ven arriba (p.ej. `onClick={(e) => e.stopPropagation()}` en el Button original, sin `preventDefault`) corresponden al código anterior a r1, no a la r1 intermedia. Es el diff literal e íntegro pedido por el DoD.

## Evidencia DoD (salidas literales)

### 1. `pnpm run typecheck` desde la raíz de ActaExpressWeb

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

### 2. `grep -n "deleteDialogActaId\|AlertDialogTrigger" artifacts/acta-express/src/pages/home.tsx`

```
101:  const [deleteDialogActaId, setDeleteDialogActaId] = useState<string | null>(null);
506:                        open={deleteDialogActaId === acta.id}
```

El estado aparece (declaración + uso en `open`); `AlertDialogTrigger` no aparece en ninguna línea (ni en el import, ni en JSX).

### 3. A/B razonado citando Radix instalado

- **(r1, roto):** el `Button` era `AlertDialogTrigger asChild`. Su `onClick` del usuario llamaba `e.preventDefault()`. Radix compone el `onClick` del usuario con su handler interno vía `composeEventHandlers` (`@radix-ui/primitive/dist/index.mjs:6`), y ese wrapper **salta** el handler interno si `event.defaultPrevented` es verdadero. El Trigger de `react-dialog/dist/index.mjs:74` abre el diálogo (`onOpenToggle`) desde ese handler interno — con `preventDefault` puesto por el usuario, ese `onOpenToggle` nunca corre. Resultado: clic en la papelera → no navega (el `preventDefault`/`stopPropagation` sí frenan la navegación del `<Link>`/`<a>`) pero el diálogo tampoco abre. Botón muerto.
- **(r2, este cambio):** el `Button` ya no es `AlertDialogTrigger`; es un hijo directo del `AlertDialog`, fuera del camino de `composeEventHandlers` de Radix para la apertura. Su `onClick` hace `preventDefault()` (mata la navegación del `<a>` de wouter), `stopPropagation()` (mata el burbujeo hacia el `onClick` del `<Link>`) y `setDeleteDialogActaId(acta.id)`. El `AlertDialog` recibe `open={deleteDialogActaId === acta.id}` → se abre por la prop controlada, sin que Radix decida la apertura vía su propio Trigger.
- **Cancelar:** `AlertDialogCancel` con solo `stopPropagation()` (sin `preventDefault`) → `event.defaultPrevented` es falso → `composeEventHandlers` (`react-dialog/dist/index.mjs:271`) SÍ ejecuta el cierre interno de Radix, que a su vez dispara `onOpenChange(false)` → `setDeleteDialogActaId(null)` → el `open` prop pasa a `false`. Cierra correctamente.
- **Confirmar (Eliminar):** `AlertDialogAction` llama `handleDelete(acta.id, e)`, que hace `preventDefault()` + `stopPropagation()` (esto sí saltaría el cierre interno de Radix vía `composeEventHandlers` por el `defaultPrevented`), por eso el cierre ahora es **explícito por estado**: `handleDelete` llama `deleteActa.mutate(...)` y luego `setDeleteDialogActaId(null)`, cerrando el diálogo sin depender del cierre interno de Radix que el `preventDefault` habría bloqueado.

## Desviaciones del contrato

Ninguna. Se siguió el bloque JSX del contrato al pie de la letra, incluyendo el orden de props del `AlertDialog` (`open` antes de `onOpenChange`), el `onClick` exacto del `Button`, y el `AlertDialogCancel` restaurado a solo `stopPropagation()`. Único detalle no normativo: al reescribir el bloque desaparecieron espacios finales sobrantes tras algunos atributos JSX (`Button`, `AlertDialogAction`) que estaban en el código previo — no son cambios funcionales, solo higiene de espacios en blanco que el propio contrato ya mostraba así en su ejemplo.

## Dudas

Ninguna que exija cambiar el contrato.

## ¿Commiteable?

No se hizo commit (fuera de alcance de esta MT). El working tree queda con `M home.tsx` (r2 aplicada) + `M acta.tsx` (MT-B2, sin tocar), listo para que el rol correspondiente decida el commit tras integrar ambas MTs.
