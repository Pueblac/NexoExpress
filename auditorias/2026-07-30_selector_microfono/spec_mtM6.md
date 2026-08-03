# Spec MT-M6 — Selector de micrófono en MODAL + nota del SO + ícono del botón (F3′ tras E2E Linux r1)

**Ciclo:** 2026-07-30_selector_microfono · F3′→F4 · **Rol:** Ingeniero (Sonnet, rotación asistida)
**Origen (dirección del Director en E2E r1, 30-07):** (1) el dropdown debe ser un **cuadro superpuesto a la pantalla** "similar a cuando uno borra un acta"; (2) falta una **nota explicativa** de que el SO puede pisar la selección (auriculares enchufados / mute del sistema); (3) corrección visual: **el ícono de micrófono del botón de grabar, un poco más grande**. Hallazgo de plataforma documentado: cambiar de dispositivo NO puede des-mutear un mic silenciado en el SO, y "Predeterminado" sigue al SO por definición.
**Repo:** `/home/pueblac/AndroidStudioProjects/ActaExpressWeb`, rama `linux`. Arranca con **MT-M7 aplicada** (existe `friendlyName`/`detail` en `MicDevice`). Toca SOLO `home.tsx`.

## Contexto mínimo verificado
- Existe `@/components/ui/dialog` (Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription).
- El CTA actual (MT-M3) es un DropdownMenu dentro del banner (`cta-cambiar-mic`, `mic-option-*`, `handleSwapMic`) — se REEMPLAZA la presentación; el handler y el hook quedan.
- El banner vive dentro de la zona de grabación; el Dialog de Radix se porta con overlay → se superpone a todo, como el de borrar actas.
- Ícono del botón de grabar: el `<Mic>` dentro del botón principal (zona `w-32 h-32 rounded-full`, busca `<Mic` con className de tamaño actual `h-*`).

## Contrato (solo `home.tsx`)
1. Estado nuevo: `const [micSelectorOpen, setMicSelectorOpen] = useState(false);`
2. El botón del banner (mismo `data-testid="cta-cambiar-mic"`, mismo texto "Cambiar micrófono") deja de ser DropdownMenuTrigger: `onClick={() => setMicSelectorOpen(true)}`. Eliminar el DropdownMenu del banner (y sus imports si quedan sin uso).
3. **Modal** (patrón visual del diálogo de borrado — overlay centrado):
```tsx
<Dialog open={micSelectorOpen} onOpenChange={setMicSelectorOpen}>
  <DialogContent data-testid="dialog-selector-mic" className="max-w-md">
    <DialogHeader>
      <DialogTitle>Cambiar micrófono</DialogTitle>
      <DialogDescription>
        Elige el dispositivo que quieres usar. La grabación continúa sin cortarse.
      </DialogDescription>
    </DialogHeader>
    <div className="flex flex-col gap-2">
      {microphones.length === 0 ? (
        <p className="text-sm text-muted-foreground">No se encontraron micrófonos.</p>
      ) : (
        microphones.map((m) => (
          <Button
            key={m.deviceId}
            variant="outline"
            data-testid={`mic-option-${m.deviceId}`}
            className="justify-start h-auto py-2 flex-col items-start"
            onClick={() => handleSwapMic(m.deviceId, m.friendlyName)}
          >
            <span className="font-medium">{m.friendlyName}</span>
            {m.detail && <span className="text-xs text-muted-foreground">{m.detail}</span>}
          </Button>
        ))
      )}
    </div>
    <p className="text-xs text-muted-foreground border-t border-border/50 pt-3" data-testid="nota-so-mic">
      Nota: tu sistema operativo puede cambiar el micrófono activo por su cuenta (por ejemplo, al
      conectar auriculares). Si el que eliges no responde, revisa que no esté silenciado en el
      sistema, o desconecta el dispositivo que interfiere.
    </p>
  </DialogContent>
</Dialog>
```
   Colocado junto a los otros diálogos del componente. `microphones` sigue viniendo de `useMicDevices(isRecording && micSilent)`; toasts de `handleSwapMic` sin cambios (usa `friendlyName` como label del toast).
4. Tras un swap **exitoso** (`res.ok`), cerrar el modal: `setMicSelectorOpen(false)` dentro de `handleSwapMic`. En fallo, el modal QUEDA abierto (el usuario puede probar otro dispositivo; el cerrojo anti-doble-swap del hook sigue protegiendo — y ahora SÍ es testeable con dos clicks rápidos en dos opciones).
5. Si el banner desaparece (señal recuperada) con el modal abierto, el modal puede quedar abierto hasta que el usuario lo cierre — aceptable, no añadir lógica.
6. **Ícono del botón de grabar:** aumentar UN paso el tamaño del `<Mic>` del botón principal (p. ej. de `h-8 w-8` a `h-10 w-10` — usa el valor actual como base y sube un nivel; decláralo).

## Restricciones
Solo `home.tsx`. NO tocar hooks ni micDevices. Sin dependencias nuevas. No commit.

## DoD (salida literal al informe)
1. `pnpm run typecheck` → exit 0.
2. `grep -n "dialog-selector-mic\|nota-so-mic\|micSelectorOpen\|friendlyName\|mic-option-" artifacts/acta-express/src/pages/home.tsx` y grep de que el DropdownMenu del banner ya no existe (si el import quedó sin uso, eliminado).
3. **A/B razonado:** (a) CTA → modal superpuesto (no dropdown); (b) swap ok → toast + modal se cierra + banner espera señal real; (c) swap fallido → modal abierto + toast destructive; (d) doble click en dos opciones → segundo rechazado por el cerrojo del hook (ahora observable).
4. `git diff artifacts/acta-express/src/pages/home.tsx` literal íntegro al informe.

## Protocolo de dudas
Textos (incluida la nota del SO), testids y el patrón modal son CONTRATO. Dudas de contrato → DETENTE.

## Informe: `informe_mtM6.md` — formato estándar.
