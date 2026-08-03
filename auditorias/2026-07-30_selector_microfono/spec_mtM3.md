# Spec MT-M3 — CTA "Cambiar micrófono" dentro del banner H4 (`home.tsx`)

**Ciclo:** 2026-07-30_selector_microfono · F4 · **Rol:** Ingeniero (Sonnet, rotación asistida)
**Diseño aprobado:** r1 + G1 (30-07). Decisión G0-c vinculante: CTA **SOLO en el banner** (sin selector permanente). Sin ocultamiento optimista: el banner se apaga únicamente cuando el detector vea señal real.
**Repo:** `/home/pueblac/AndroidStudioProjects/ActaExpressWeb`, rama `linux`. Arranca con **MT-M1 + MT-M2 aplicadas** (`?? lib/micDevices.ts`, `?? hooks/useMicDevices.ts`, `M hooks/useAudioRecorder.ts`). Toca SOLO `home.tsx`.

## Contexto mínimo verificado
- Banner H4 en `home.tsx` (~:505 zona render): div `data-testid="banner-mic-muerto"` visible con `isRecording && micSilent`, con bifurcación de estilos presencial (destructive) / virtual (ámbar) y textos por modo.
- El hook `useAudioRecorder` ya expone `swapMicrophone(deviceId): Promise<{ ok, message? }>` (MT-M2).
- `useMicDevices(active): { microphones }` (MT-M1) — labels amigables; permiso garantizado durante grabación.
- home.tsx NO importa `DropdownMenu` aún (sí existe en `@/components/ui/dropdown-menu`, lo usa acta.tsx).
- `useToast` ya en uso en home.

## Contrato (solo `home.tsx`)
1. Imports: `DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger` de `@/components/ui/dropdown-menu`; `useMicDevices` de `@/hooks/useMicDevices`; `Mic` de lucide (ya hay imports de lucide en el archivo — añadir el símbolo si falta). Destructurar `swapMicrophone` del `useAudioRecorder()` existente.
2. `const { microphones } = useMicDevices(isRecording && micSilent);` — la lista solo se puebla cuando el banner está activo (G0-c).
3. Dentro del div del banner (`banner-mic-muerto`), tras el texto, añadir:
```tsx
<DropdownMenu>
  <DropdownMenuTrigger asChild>
    <Button size="sm" variant="outline" data-testid="cta-cambiar-mic" className="ml-2 shrink-0">
      <Mic className="mr-1 h-3 w-3" />
      Cambiar micrófono
    </Button>
  </DropdownMenuTrigger>
  <DropdownMenuContent align="center" className="w-64">
    {microphones.length === 0 ? (
      <DropdownMenuItem disabled>No se encontraron micrófonos</DropdownMenuItem>
    ) : (
      microphones.map((m) => (
        <DropdownMenuItem key={m.deviceId} data-testid={`mic-option-${m.deviceId}`} onClick={() => handleSwapMic(m.deviceId, m.label)}>
          {m.label}
        </DropdownMenuItem>
      ))
    )}
  </DropdownMenuContent>
</DropdownMenu>
```
   Ajusta el layout del banner si hace falta (p. ej. `flex-wrap`) sin cambiar textos ni estilos de severidad existentes.
4. Handler:
```tsx
const handleSwapMic = async (deviceId: string, label: string) => {
  const res = await swapMicrophone(deviceId);
  if (res.ok) {
    toast({ title: "Micrófono cambiado", description: `Ahora se usa "${label}". Verificando señal…` });
  } else {
    toast({ variant: "destructive", title: "No se pudo cambiar el micrófono", description: res.message });
  }
};
```
5. PROHIBIDO ocultar el banner manualmente tras el swap (nada de tocar `micSilent` ni estados del detector): se apaga solo cuando `useMicLevel` vea RMS ≥ umbral con el stream nuevo.

## Restricciones
Solo `home.tsx`. NO tocar useAudioRecorder, useMicLevel ni micDevices. Sin dependencias nuevas. No commit.

## DoD (salida literal al informe)
1. `pnpm run typecheck` → exit 0.
2. `grep -n "cta-cambiar-mic\|useMicDevices\|handleSwapMic\|mic-option-" artifacts/acta-express/src/pages/home.tsx`.
3. **A/B razonado:** (a) banner activo → hook `active=true` → lista poblada; banner apagado → `active=false` → sin listener; (b) swap ok → toast informativo, banner PERMANECE hasta señal real (citar que ningún estado del detector se toca); (c) swap fallido → toast destructive con el message del hook.
4. `git diff artifacts/acta-express/src/pages/home.tsx` literal íntegro al informe.

## Protocolo de dudas
Textos, testids y la prohibición de ocultamiento optimista son CONTRATO. Dudas de contrato → DETENTE.

## Informe: `informe_mtM3.md` — formato estándar.
