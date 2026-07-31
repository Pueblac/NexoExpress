# Expediente 2026-07-29_bug_basurero — Verificación F5 del Arquitecto (MT-B1 r2 + MT-B2)

**Fecha:** 29-07-2026 · **Modo:** rotación asistida (3 subagentes Sonnet: B1 r1, B2, B1 r2). Informes en `informe_mtB1.md` (r1, SUSTITUIDA), `informe_mtB2.md`, `informe_mtB1_r2.md`.
**G0 del Director:** ambas MTs aprobadas ("Apruebo los dos, haz ambos y luego los verificamos"). Ciclo corto sin ronda de diseño F2; F6 a decidir con el diff.

## Incidencia clave del ciclo: BUG DE SPEC cazado en F5 (F3′ → r2)

La spec r1 de MT-B1 ordenaba `preventDefault` en el `AlertDialogTrigger`. **Error de diseño del Arquitecto:** Radix compone los onClick del usuario con sus handlers internos y los SALTA si `event.defaultPrevented` — verificado EJECUTANDO grep sobre el código instalado: `@radix-ui/primitive/dist/index.mjs:6` (la condición), `react-dialog/dist/index.mjs:74` (Trigger→open), `:271` (Close→cierre). La r1 habría dejado el basurero MUERTO (sin navegar pero sin abrir diálogo) y Cancelar sin cerrar. **F5 lo detectó ANTES del E2E**; F3′ produjo la r2: **diálogo controlado por estado** (`deleteDialogActaId`), botón fuera del Trigger, Cancel restaurado, cierre explícito en `handleDelete`.

## DoD re-EJECUTADO por el Arquitecto

1. `git status --short` → exactamente `M home.tsx` + `M acta.tsx` (rama `linux`, base `3ca3b1d`). ✅
2. `pnpm run typecheck` re-ejecutado → 4 paquetes Done, EXIT=0. ✅
3. **MT-B1 r2 sobre el código real:** estado en `home.tsx:101`; AlertDialog controlado `open={deleteDialogActaId === acta.id}` (:506) con `onOpenChange` que limpia (:507); Button con `preventDefault + stopPropagation + set` (:514) SIN pasar por Radix; `AlertDialogTrigger` ELIMINADO (grep sin resultados, import incluido); Cancel restaurado a solo `stopPropagation` (:526); `handleDelete` cierra explícito (:212). ✅
4. **MT-B2 sobre el código real:** `acta.tsx` con imports nuevos (Trash2, useDeleteActa, getListActasQueryKey, useQueryClient, useLocation, AlertDialog*), mutación con invalidación + toast + `setLocation("/")`, botón `button-delete-acta` al final de las acciones con textos idénticos a la lista, `disabled={deleteActa.isPending}`, `{ actaId: actaId as string }` (desviación menor DECLARADA por el Ingeniero: wouter tipa `actaId` como `string | undefined`; verificada correcta). Sin `<Link>` envolvente → sin preventDefault (correcto). ✅
5. Contraste informes vs realidad: sin discrepancias no declaradas. ✅

**Veredicto F5 parte 1 (código): APROBADO** — 2 archivos, diff pequeño y acotado.

## Pendiente F5 parte 2 — E2E con el Director

| # | Prueba | Resultado esperado |
|---|---|---|
| 1 | En la lista, clic en el **basurero** de un acta | El diálogo "¿Eliminar acta?" se abre EN PRIMER PLANO y **NO navega** al detalle |
| 2 | En el diálogo, **Cancelar** | Cierra el diálogo, sigues en la lista, sin navegar |
| 3 | Basurero → **Eliminar** | Acta desaparece de la lista + toast "Acta eliminada"; sin navegación |
| 4 | Entrar a un acta → botón **Eliminar** (nuevo, junto a Compartir) → confirmar | Acta borrada + toast + **redirige a la lista** donde ya no está |
| 5 | En el detalle, **Cancelar** en el diálogo | Cierra y sigues en el detalle |

## E2E EJECUTADO (29-07) — F5 CERRADA ✅

**Reporte del Director con capturas:** "Funciona, en ambos casos las listas se borran de forma permanente."
- Lista: clic en basurero → diálogo "¿Eliminar acta?" EN PRIMER PLANO, **sin navegar** (captura 1 — el bug original, corregido) → Eliminar → borrado permanente.
- Detalle: botón Eliminar nuevo junto a Compartir → diálogo (captura 2) → borrado permanente + retorno a la lista.

**Veredicto F5 COMPLETO: APROBADO.** Pendiente: decisión del Director sobre F6 (ronda ligera con Gemini vs. diferir al siguiente ciclo — diff pequeño de 2 archivos ya verificado contra el código de Radix instalado) + G2 (commit).
