# Informe MT-B1 — Fix del basurero en la lista de actas (navega en vez de borrar)

**Ciclo:** 2026-07-29_bug_basurero · **Rol:** Ingeniero (Sonnet, rotación asistida)
**Repo:** `/home/pueblac/AndroidStudioProjects/ActaExpressWeb`, rama `linux`, base `3ca3b1d`

## Precondición verificada
```
$ git -C /home/pueblac/AndroidStudioProjects/ActaExpressWeb status --short
(sin salida — working tree limpio)
$ git -C /home/pueblac/AndroidStudioProjects/ActaExpressWeb branch --show-current
linux
$ git -C /home/pueblac/AndroidStudioProjects/ActaExpressWeb rev-parse HEAD
3ca3b1deedb8832a7f4b29dfa1f7df099dfdca08
```
Coincide con la base declarada en el spec (`3ca3b1d`). OK para proceder.

## Qué se hizo
Se modificó exclusivamente `artifacts/acta-express/src/pages/home.tsx`, dos líneas, tal como manda el contrato:

1. **Línea 510** (onClick del `AlertDialogTrigger asChild` sobre el `Button` del basurero): se añadió `e.preventDefault()` antes del `e.stopPropagation()` existente.
2. **Línea 523** (onClick del `AlertDialogCancel`): se añadió `e.preventDefault()` a su onClick existente, manteniendo el `e.stopPropagation()` ya presente.

No se tocó `handleDelete` (línea 207-211, ya tenía `preventDefault` + `stopPropagation` correctos), ni el diálogo, ni estilos, ni ningún otro archivo.

## Diff literal íntegro
```diff
diff --git a/artifacts/acta-express/src/pages/home.tsx b/artifacts/acta-express/src/pages/home.tsx
index b5d5ef2..a4d4ee8 100644
--- a/artifacts/acta-express/src/pages/home.tsx
+++ b/artifacts/acta-express/src/pages/home.tsx
@@ -507,7 +507,7 @@ export default function Home() {
                             variant="ghost" 
                             size="icon" 
                             className="h-8 w-8 text-muted-foreground hover:text-destructive opacity-0 group-hover:opacity-100 transition-opacity -mt-1 -mr-2 shrink-0"
-                            onClick={(e) => e.stopPropagation()}
+                            onClick={(e) => { e.preventDefault(); e.stopPropagation(); }}
                           >
                             <Trash2 className="h-4 w-4" />
                           </Button>
@@ -520,7 +520,7 @@ export default function Home() {
                             </AlertDialogDescription>
                           </AlertDialogHeader>
                           <AlertDialogFooter>
-                            <AlertDialogCancel onClick={e => e.stopPropagation()}>Cancelar</AlertDialogCancel>
+                            <AlertDialogCancel onClick={e => { e.preventDefault(); e.stopPropagation(); }}>Cancelar</AlertDialogCancel>
                             <AlertDialogAction 
                               onClick={(e) => handleDelete(acta.id, e as any)}
                               className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
```

## Evidencia DoD

### 1. `pnpm run typecheck` → exit 0
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
EXIT:0
```

### 2. `grep -n "preventDefault" artifacts/acta-express/src/pages/home.tsx`
```
208:    e.preventDefault();
510:                            onClick={(e) => { e.preventDefault(); e.stopPropagation(); }}
523:                            <AlertDialogCancel onClick={e => { e.preventDefault(); e.stopPropagation(); }}>Cancelar</AlertDialogCancel>
```
Aparece en `handleDelete` (línea 208, dentro de la función que arranca en 207), en el trigger (línea 510) y en Cancel (línea 523). Cumple lo pedido (el spec estimaba handleDelete en ~192-196; en el archivo real la función `handleDelete` está en 207-211 con `preventDefault` en 208 — desviación puramente numérica de línea, sin relevancia funcional, ver sección Desviaciones).

### 3. A/B razonado
- **Código viejo** (línea 510: `onClick={(e) => e.stopPropagation()}`): al hacer clic en el botón del basurero, `stopPropagation()` detiene la burbuja del evento sintético de React hacia los ancestros (incluido el `<Link>`/`<a>` de wouter en la línea 492), pero **no** cancela el comportamiento por defecto del `<a>` (navegar al `href`). El navegador procesa el clic sobre el ancla y navega a `/acta/${acta.id}` aunque el `AlertDialog` se haya abierto — el diálogo queda "tapado" por la navegación.
- **Código nuevo** (línea 510: `onClick={(e) => { e.preventDefault(); e.stopPropagation(); }}`): `preventDefault()` cancela explícitamente la acción por defecto del evento de clic — es decir, el navegador ya no sigue el `href` del `<a>` contenedor. Combinado con `stopPropagation()` (que sigue evitando que el clic dispare handlers de React en ancestros, como un posible onClick del `Link`), el resultado es que el clic en el basurero abre el `AlertDialog` sin navegar. El mismo razonamiento aplica al `AlertDialogCancel` (línea 523): aunque su contenido vive fuera del `<a>` gracias al portal de Radix (por lo que en la práctica el `<a>` no está en la cadena de ancestros DOM real del botón Cancelar), el `preventDefault` añadido deja el patrón defensivo uniforme entre los tres onClick relacionados con este flujo (trigger, cancel, `handleDelete`), a prueba de futuros refactors que pudieran alterar el portal o el árbol DOM.

### 4. `git diff` → solo home.tsx, 2 líneas tocadas
Ver diff literal íntegro arriba. Confirmado con `git status --short`:
```
$ git status --short
 M artifacts/acta-express/src/pages/home.tsx
```
Único archivo modificado, ninguno más.

## Desviaciones
- El spec ubicaba `handleDelete` en "home.tsx:192-196"; en el HEAD real (3ca3b1d) la función está en las líneas 207-211 (con `preventDefault` en 208). Es una discrepancia de numeración de línea entre la referencia del spec y el archivo real, sin impacto en el contrato: el patrón defensivo ya existía ahí tal como describía el spec, y no se tocó. No se considera una duda que cambie el contrato.

## Dudas
Ninguna. Contrato cerrado, implementado al pie de la letra.

## Commiteable
Sí. Cambio mínimo (2 líneas), típico defensivo, sin ambigüedad, DoD verde (typecheck exit 0, grep conforme, diff acotado a home.tsx). No se realizó commit — corresponde a F6/al Director según el protocolo del ciclo.
