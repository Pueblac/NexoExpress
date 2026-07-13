# Paquete de Especificación — MT-04a: Regenerar clientes API (`generarSintesis`)

**Ciclo:** 2026-07-09_mt04_toggle_sintesis · **Fase:** F4 (implementación según spec)
**Rol destinatario:** Ingeniero (Claude Sonnet) — sesión nueva, working tree limpio
**Diseño aprobado:** rondas 1 y 2 del expediente (Gemini 3.1 Pro High); esta spec es vinculante — no rediseñes.

## 1. Objetivo

Regenerar los clientes API del monorepo **ActaExpressWeb** para que el tipo `AudioInput` exponga el campo `generarSintesis?: boolean`, ya declarado en el contrato OpenAPI pero ausente de los artefactos generados.

## 2. Contexto mínimo verificado (09-07-2026)

- Repo: `/home/pueblac/AndroidStudioProjects/ActaExpressWeb` (monorepo pnpm). Trabaja SOLO ahí.
- `lib/api-spec/openapi.yaml` ya contiene (literal, NO lo toques):
  ```yaml
  generarSintesis:
    type: boolean
    default: false
    description: Si es true, genera transcripción y análisis profundo en background (colección sintesis/)
  ```
  dentro de `components.schemas.AudioInput.properties` (no está en `required`).
- Los artefactos generados por orval v8.9.1 (cabecera "Do not edit manually") están DESACTUALIZADOS: `grep -rn "generarSintesis" lib/api-client-react/src/generated/ lib/api-zod/src/generated/` hoy devuelve **0 resultados**.
- Comando de regeneración existente: el paquete `@workspace/api-spec` define
  `"codegen": "orval --config ./orval.config.ts && pnpm -w run typecheck:libs"`.

## 3. Contrato (lo que DEBE quedar)

1. `lib/api-client-react/src/generated/api.schemas.ts` → interfaz `AudioInput` incluye `generarSintesis?: boolean`.
2. `lib/api-zod/src/generated/types/audioInput.ts` (y/o su schema zod asociado) incluye el campo.
3. Ningún archivo fuera de `**/generated/**` cambia.

## 4. Restricciones

- **PROHIBIDO** editar a mano cualquier archivo `generated/` — solo vía el comando codegen.
- **PROHIBIDO** tocar `openapi.yaml`, `orval.config.ts`, dependencias, versiones o cualquier otro archivo.
- **Regla de diff limpio (diseño C1, vinculante):** tras regenerar, inspecciona `git diff`. Si aparece CUALQUIER cambio no derivado del campo `generarSintesis` según el yaml vigente (p. ej. reordenamientos masivos, otros endpoints, cambios de versión de generador), **DETENTE**: no intentes arreglarlo, devuélvelo como duda en el informe con el diff literal.
- NO hagas commit. NO toques credenciales ni Firestore.

## 5. DoD ejecutable (corre TODOS y copia la salida literal al informe)

```bash
cd /home/pueblac/AndroidStudioProjects/ActaExpressWeb
git status --short                                   # 1) ANTES: debe estar limpio
pnpm --filter @workspace/api-spec codegen            # 2) exit 0
grep -rn "generarSintesis" lib/api-client-react/src/generated/ lib/api-zod/src/generated/   # 3) campo presente en AMBOS paquetes
pnpm run typecheck                                   # 4) exit 0 (workspace completo)
git diff --stat                                      # 5) SOLO archivos generated/
```

## 6. Protocolo de dudas

Si algo es ambiguo o el diff viola la regla de limpieza: **DETENTE** y devuelve la duda en el informe. Implementar sobre un supuesto no declarado invalida la entrega. Tu duda reabre F3 (spec nueva); no recibirás aclaraciones informales.

## 7. Informe de Implementación (entrégalo como UN documento markdown listo para archivar: `informe_mt04a.md`)

Secciones obligatorias: 1) Qué se hizo (por archivo). 2) **Diff literal**: output ÍNTEGRO de `git diff` + `git status` (sin editar). 3) Evidencia literal: salida REAL de cada comando del DoD. 4) Desviaciones (o "ninguna"). 5) Tus dudas. 6) Confirmación de estado commiteable. 7) El AVISO de abajo, actualizado.

━━ AVISO DE TRASPASO ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CICLO      : 2026-07-09_mt04_toggle_sintesis
FASE       : F3 → F4 — spec MT-04a
TURNO DE   : Ingeniero (Claude Sonnet)
ENTREGAR   : este documento (spec_mt04a.md)
ADJUNTOS   : Ninguno (repo local es el material de trabajo)
DESTINO    : Sesión NUEVA de Claude Sonnet sobre el repo ActaExpressWeb —
             inicialización de identidad primero: "Rol: Ingeniero del ciclo
             2026-07-09_mt04_toggle_sintesis, metodología v2 del ecosistema
             Express. Confirma recepción sin accionar; acepta únicamente
             artefactos cuyo TURNO DE diga Ingeniero."
ACCIÓN     : Implementar EXACTAMENTE esta spec y producir el informe
VUELVE A   : Arquitecto, con el informe archivado como
             auditorias/2026-07-09_mt04_toggle_sintesis/informe_mt04a.md
             (el Director lo guarda tal cual) → F5 (verificación)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
