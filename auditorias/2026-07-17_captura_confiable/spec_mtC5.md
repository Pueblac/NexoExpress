# Spec MT-C5 — Estado de procesamiento prominente

**Ciclo:** 2026-07-17_captura_confiable · F4 · **Rol:** Ingeniero (Sonnet, rotación asistida)
**Diseño aprobado:** r1 + G1. Observación de UX del Director en la F5.2 del ciclo anterior (el mensaje de espera se veía pequeño). Vinculante.
**Repo:** `/home/pueblac/AndroidStudioProjects/ActaExpressWeb`. Arranca sobre el working tree con **MT-C1..C4 aplicadas**. Última MT de la tanda; toca SOLO lo de su contrato.

## Objetivo
Elevar la jerarquía visual del estado "Procesando con IA..." mientras `processAudio.isPending`: convertirlo en una tarjeta destacada (borde + fondo suave `primary`, `Loader2` girando, título prominente y el mensaje de espera debajo) para que el usuario perciba claramente que el sistema está trabajando. Sin cambios de lógica.

## Contexto mínimo verificado (código real, tras MT-C1..C4)
- `home.tsx:146-150` — `getStatusMessage()` devuelve "Procesando con IA..." cuando `processAudio.isPending`.
- `home.tsx:197-209` — bloque actual:
```tsx
<h2 className="text-4xl font-mono ...">{formatDuration(duration)}</h2>
<div className="flex items-center justify-center gap-2 text-muted-foreground">
  {isRecording && <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />}
  <p className="font-medium">{getStatusMessage()}</p>
</div>
{processAudio.isPending && (
  <p className="text-xs text-muted-foreground" data-testid="text-espera">
    Esto puede tardar unos minutos — no cierres esta pestaña.
  </p>
)}
```
- `Loader2` ya está importado de lucide-react (`home.tsx:10`) y se usa en el botón (`:187`). `Card`/`CardContent` de `@/components/ui/card` ya importados (`:12`).

## Contrato
1. Cuando `processAudio.isPending`, renderizar una **tarjeta destacada** en la columna central (sustituyendo o envolviendo el texto plano de estado + `text-espera`) con:
   - Borde y fondo suave (`border border-primary/30 bg-primary/10 rounded-xl`, padding cómodo).
   - `Loader2` con `animate-spin` (tamaño mediano) + título "Procesando con IA..." en cuerpo legible (p. ej. `text-base font-semibold`).
   - Debajo, el mensaje de espera CONSERVANDO `data-testid="text-espera"` y el texto exacto "Esto puede tardar unos minutos — no cierres esta pestaña." (no perder el testid: hay pruebas/DoD que lo referencian).
   - `data-testid="card-procesando"` en el contenedor de la tarjeta.
2. Cuando NO está `isPending`, el estado se muestra como hoy (timer + `getStatusMessage()` normal para "Grabando..."/"Listo para grabar"). No dupliques "Procesando con IA..." en dos sitios: durante `isPending` manda la tarjeta.
3. Sin cambios en `getStatusMessage`, el guard de envío, el timer, ni el botón. Puramente presentacional.

## Restricciones
Solo `home.tsx`. Sin dependencias nuevas. Conservar `data-testid="text-espera"` con su texto literal. No commit.

## DoD (salida literal al informe)
1. `pnpm run typecheck` → exit 0.
2. `grep -n "card-procesando\|text-espera\|Procesando con IA\|Esto puede tardar" artifacts/acta-express/src/pages/home.tsx` → la tarjeta, el testid conservado y los textos.
3. Confirma por diff que `text-espera` sigue existiendo con el texto exacto y que la tarjeta solo aparece con `isPending`. Cita líneas.
4. `git diff --stat` → SOLO `home.tsx`.
5. Nota E2E Director (no ejecutable aquí): al procesar, tarjeta prominente visible; al terminar, desaparece.

## Protocolo de dudas
Si la sustitución del bloque de estado por la tarjeta genera duda sobre cómo mostrar el timer durante `isPending`, opta por conservar el timer arriba y la tarjeta debajo (mínimo cambio), y **declara** la decisión. No toques lógica.

## Informe: formato estándar (qué se hizo / diff literal íntegro / evidencia DoD literal / desviaciones / dudas / estado commiteable).
