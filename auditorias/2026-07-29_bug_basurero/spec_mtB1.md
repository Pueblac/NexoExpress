# Spec MT-B1 — Fix del basurero en la lista de actas (navega en vez de borrar)

**Ciclo:** 2026-07-29_bug_basurero · **Rol:** Ingeniero (Sonnet, rotación asistida)
**G0 del Director (29-07):** aprobadas MT-B1 + MT-B2. Micro-ciclo corto sin ronda de diseño (fix trivial de patrón ya existente); F6 se decide con el diff.
**Repo:** `/home/pueblac/AndroidStudioProjects/ActaExpressWeb`, rama `linux`, base `3ca3b1d`. Working tree LIMPIO — verifícalo; si no lo está, DETENTE.

## Bug (verificado por el Arquitecto, 2 veces reproducido en E2E por el Director)
En la lista de actas, cada Card vive dentro de un `<Link>` de wouter (home.tsx:492) que renderiza un `<a>`. El botón del basurero (`AlertDialogTrigger asChild`, home.tsx:505-513) tiene `onClick={(e) => e.stopPropagation()}` (home.tsx:510) — detiene la burbuja React pero NO la navegación por defecto del ancla → al hacer clic, el diálogo se abre pero el navegador NAVEGA a `/acta/:id`, tapándolo. `handleDelete` (home.tsx:192-196) ya hace `preventDefault + stopPropagation` correctamente.

## Contrato
1. Modificar SOLO `artifacts/acta-express/src/pages/home.tsx`, línea 510: el onClick del trigger pasa a
```tsx
onClick={(e) => { e.preventDefault(); e.stopPropagation(); }}
```
2. Mismo tratamiento defensivo en `AlertDialogCancel` (home.tsx:523): añadir `e.preventDefault()` a su onClick existente. (El contenido del diálogo se porta fuera del `<a>` vía portal de Radix, pero el patrón queda uniforme y a prueba de refactors.)
3. NADA más: no tocar `handleDelete`, ni el diálogo, ni estilos, ni otros archivos.

## DoD (salida literal al informe)
1. `pnpm run typecheck` → exit 0.
2. `grep -n "preventDefault" artifacts/acta-express/src/pages/home.tsx` → aparece en el trigger (~:510), en Cancel (~:523) y en handleDelete (:193).
3. **A/B razonado:** con el código viejo, clic en el basurero → default del `<a>` no cancelado → navegación; con el nuevo → `preventDefault` en el trigger → el `<a>` no navega y el diálogo queda en primer plano. Cita las líneas.
4. `git diff` → SOLO home.tsx, 2 líneas tocadas. Diff literal íntegro al informe.

## Protocolo de dudas
Contrato cerrado; cualquier duda que lo cambie → DETENTE y decláralo sin implementar. No commit.

## Informe: `informe_mtB1.md` en este expediente — formato estándar (qué se hizo / diff literal / evidencia DoD / desviaciones / dudas / commiteable).
