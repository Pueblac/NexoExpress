# Spec MT-B2 — Borrado desde la vista de detalle del acta (mini-feature)

**Ciclo:** 2026-07-29_bug_basurero · **Rol:** Ingeniero (Sonnet, rotación asistida)
**G0 del Director (29-07):** aprobada junto a MT-B1. Verificado por el Arquitecto: `pages/acta.tsx` (438 líneas) NO tiene ninguna capacidad de borrado (cero referencias a Trash/useDeleteActa/AlertDialog) — esto es añadir la acción, clonando el patrón ya existente en `home.tsx`.
**Repo:** `/home/pueblac/AndroidStudioProjects/ActaExpressWeb`, rama `linux`. Arranca sobre el working tree con **MT-B1 aplicada** (`M artifacts/acta-express/src/pages/home.tsx` y nada más).

## Contexto verificado
- `acta.tsx` importa de wouter solo `useParams, Link` (:1); botones de acción en la cabecera: div `flex gap-2` (:267) con Copiar (:268), Descargar .docx (:273) y Compartir (:278-...). Usa `useGetActa` (:2), `useToast` (:12). NO importa `useQueryClient` ni `useDeleteActa` todavía.
- Patrón de referencia (home.tsx): `useDeleteActa` con `onSuccess` → `queryClient.invalidateQueries({ queryKey: getListActasQueryKey() })` + toast "Acta eliminada"; diálogo con título "¿Eliminar acta?" y descripción «Esta acción no se puede deshacer. Se eliminará permanentemente el acta "{titulo}".»

## Contrato
1. Modificar SOLO `artifacts/acta-express/src/pages/acta.tsx`.
2. Imports nuevos: `Trash2` (lucide), `useDeleteActa, getListActasQueryKey` (`@workspace/api-client-react`), `useQueryClient` (`@tanstack/react-query`), `useLocation` (wouter, junto a los existentes), y `AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger` (`@/components/ui/alert-dialog`).
3. Mutación:
```tsx
const [, setLocation] = useLocation();
const queryClient = useQueryClient();
const deleteActa = useDeleteActa({
  mutation: {
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: getListActasQueryKey() });
      toast({ title: "Acta eliminada", description: "El acta fue eliminada permanentemente." });
      setLocation("/");
    },
  },
});
```
4. Botón nuevo AL FINAL del div de acciones (:267, tras el bloque Compartir): `AlertDialog` con trigger
```tsx
<Button variant="outline" size="sm" data-testid="button-delete-acta"
        className="text-destructive hover:text-destructive hover:bg-destructive/10">
  <Trash2 className="mr-2 h-4 w-4" />
  Eliminar
</Button>
```
y contenido idéntico en textos al de home.tsx (título "¿Eliminar acta?", descripción con el título del acta, Cancelar / Eliminar con `className="bg-destructive text-destructive-foreground hover:bg-destructive/90"`). La acción confirma con `deleteActa.mutate({ actaId })` (el `actaId` de `useParams`). Deshabilitar la acción mientras `deleteActa.isPending`.
5. Aquí NO hay `<Link>` envolvente → no hacen falta preventDefault/stopPropagation; no los añadas.

## DoD (salida literal al informe)
1. `pnpm run typecheck` → exit 0.
2. `grep -n "button-delete-acta\|useDeleteActa\|setLocation(\"/\")\|Eliminar acta" artifacts/acta-express/src/pages/acta.tsx`.
3. **A/B razonado:** traza del flujo — clic Eliminar → diálogo → confirmar → `deleteActa.mutate({actaId})` → onSuccess invalida la lista, toast y `setLocation("/")` (el usuario aterriza en Home sin el acta). Y el camino Cancelar → sin mutación, sigue en el detalle.
4. `git diff` → home.tsx (M, de MT-B1) + acta.tsx (M). Diff literal íntegro de acta.tsx al informe.

## Protocolo de dudas
Textos, testid y colocación son contrato. Si el tipado del parámetro de `useDeleteActa` difiere (`{ actaId }` vs otro nombre), usa el REAL del cliente generado (verifícalo con grep en `lib/api-client-react`) y decláralo. Cualquier duda mayor → DETENTE. No commit.

## Informe: `informe_mtB2.md` en este expediente — formato estándar.
