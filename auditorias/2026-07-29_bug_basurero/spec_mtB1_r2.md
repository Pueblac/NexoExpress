# Spec MT-B1 r2 — Fix del basurero con diálogo CONTROLADO (F3′ tras F5 del Arquitecto)

**Ciclo:** 2026-07-29_bug_basurero · **Rol:** Ingeniero (Sonnet, rotación asistida)
**Por qué hay r2 (BUG de la spec r1, cazado en F5 ANTES del E2E):** Radix compone los onClick del usuario con sus handlers internos vía `composeEventHandlers`, que SALTA el handler interno si `event.defaultPrevented` (verificado en el código instalado: `@radix-ui/primitive/dist/index.mjs:6`; Trigger→open en `react-dialog/dist/index.mjs:74`; Close→cierre en `:271`). El `preventDefault` de la r1 en el Trigger habría dejado el botón MUERTO (sin navegar, pero sin abrir el diálogo) y en Cancel habría impedido cerrar. La solución es sacar a Radix del click conflictivo: **diálogo controlado por estado**.
**Repo:** `/home/pueblac/AndroidStudioProjects/ActaExpressWeb`, rama `linux`. Working tree actual: `M home.tsx` (r1 aplicada — la REEMPLAZAS) + `M acta.tsx` (MT-B2, NO tocar).

## Contrato (solo `artifacts/acta-express/src/pages/home.tsx`)
1. Estado nuevo junto a los demás useState del componente:
```tsx
const [deleteDialogActaId, setDeleteDialogActaId] = useState<string | null>(null);
```
2. Reestructurar el bloque del diálogo de cada card (zona actual :503-532): el `AlertDialog` pasa a controlado y el botón deja de ser Trigger:
```tsx
<AlertDialog
  open={deleteDialogActaId === acta.id}
  onOpenChange={(open) => { if (!open) setDeleteDialogActaId(null); }}
>
  <Button
    data-testid={`button-delete-${acta.id}`}
    variant="ghost"
    size="icon"
    className="h-8 w-8 text-muted-foreground hover:text-destructive opacity-0 group-hover:opacity-100 transition-opacity -mt-1 -mr-2 shrink-0"
    onClick={(e) => { e.preventDefault(); e.stopPropagation(); setDeleteDialogActaId(acta.id); }}
  >
    <Trash2 className="h-4 w-4" />
  </Button>
  <AlertDialogContent onClick={e => e.stopPropagation()}>
    ...cabecera y textos EXACTAMENTE como están...
    <AlertDialogFooter>
      <AlertDialogCancel onClick={e => e.stopPropagation()}>Cancelar</AlertDialogCancel>
      <AlertDialogAction
        onClick={(e) => handleDelete(acta.id, e as any)}
        className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
      >
        Eliminar
      </AlertDialogAction>
    </AlertDialogFooter>
  </AlertDialogContent>
</AlertDialog>
```
Es decir: se ELIMINA el `<AlertDialogTrigger asChild>` (y su import si queda sin uso), el Button queda como hijo directo del AlertDialog, y `AlertDialogCancel` VUELVE a su onClick original (`e.stopPropagation()` solo — el stopPropagation sí hace falta: el contenido del portal burbujea por el árbol de React hasta el `<Link>`).
3. En `handleDelete` (:192-196): añadir `setDeleteDialogActaId(null);` tras `deleteActa.mutate(...)` (cierre explícito — el composeEventHandlers de Action saltará su cierre interno por el preventDefault de handleDelete).
4. Nada más. No tocar `acta.tsx` (es de MT-B2).

## DoD (salida literal al informe)
1. `pnpm run typecheck` → exit 0.
2. `grep -n "deleteDialogActaId\|AlertDialogTrigger" artifacts/acta-express/src/pages/home.tsx` → el estado aparece; `AlertDialogTrigger` NO aparece (ni en el import si quedó sin otro uso).
3. **A/B razonado citando Radix instalado:** (r1, roto) clic → preventDefault → `composeEventHandlers` salta `onOpenToggle` (dialog:74) → diálogo nunca abre; (r2) el Button no pasa por composeEventHandlers: preventDefault mata la navegación del `<a>`, stopPropagation mata el onClick de wouter, `setDeleteDialogActaId` abre el diálogo vía prop `open` — Radix ya no decide la apertura. Cancelar: sin preventDefault → `onOpenChange(false)` (dialog:271) corre y cierra. Confirmar → handleDelete muta y el cierre es explícito por estado.
4. `git diff artifacts/acta-express/src/pages/home.tsx` literal íntegro al informe.

## Protocolo de dudas
Contrato cerrado. Si `AlertDialogTrigger` se usa en OTRO sitio del archivo, deja el import. Cualquier duda que cambie el contrato → DETENTE. No commit.

## Informe: `informe_mtB1_r2.md` — formato estándar.
