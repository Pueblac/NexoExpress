# Spec MT-M7 — Nombres amigables de micrófonos (F3′ tras E2E Linux r1)

**Ciclo:** 2026-07-30_selector_microfono · F3′→F4 · **Rol:** Ingeniero (Sonnet, rotación asistida)
**Origen:** E2E r1 del Director (30-07): los labels del navegador ("Built-in Audio Estéreo analógico", "Predeterminado") no son intuitivos; pide nombres tipo "Micrófono del PC", "Micrófono de auriculares".
**Repo:** `/home/pueblac/AndroidStudioProjects/ActaExpressWeb`, rama `linux`. Working tree esperado: la tanda M (2 nuevos + 2 M). Toca SOLO `lib/micDevices.ts`.

## Contrato
1. En `micDevices.ts`, ampliar la interfaz y añadir el traductor heurístico:
```ts
export interface MicDevice { deviceId: string; label: string; friendlyName: string; detail?: string; }

/** Traduce el label técnico del SO a un nombre humano en español.
 *  El label original se conserva en `detail` cuando aporta información. */
export function friendlyMicName(label: string, deviceId: string): { friendlyName: string; detail?: string } {
  if (deviceId === "default") return { friendlyName: "Predeterminado del sistema", detail: label || undefined };
  if (deviceId === "communications") return { friendlyName: "Dispositivo de comunicaciones", detail: label || undefined };
  const l = label.toLowerCase();
  if (/monitor|stereo mix|mezcla estéreo|loopback/.test(l)) return { friendlyName: "Audio del sistema (no capta tu voz)", detail: label };
  if (/head|auricular|earph|airpod|buds|hands-?free/.test(l)) return { friendlyName: "Micrófono de auriculares", detail: label };
  if (/bluetooth|\bbt\b/.test(l)) return { friendlyName: "Micrófono Bluetooth", detail: label };
  if (/usb/.test(l)) return { friendlyName: "Micrófono USB", detail: label };
  if (/webcam|cámara|camera/.test(l)) return { friendlyName: "Micrófono de la cámara", detail: label };
  if (/built-?in|internal|interno|analógico|analog/.test(l)) return { friendlyName: "Micrófono interno del PC", detail: label };
  return { friendlyName: label || "Micrófono", detail: undefined };
}
```
2. `listMicrophones()` rellena `friendlyName`/`detail` con este traductor (manteniendo el fallback "Micrófono N" como `friendlyName` cuando el label venga vacío).
3. El orden de los patrones ES CONTRATO (monitor/stereo-mix primero: es el caso Stereo Mix que motivó el ciclo — debe quedar claramente marcado como NO-micrófono).

## Restricciones
Solo `micDevices.ts`. NO tocar el hook ni la UI (el consumo es MT-M6). No commit.

## DoD (salida literal al informe)
1. `pnpm run typecheck` → exit 0 (home.tsx sigue compilando: `MicDevice` solo GANA campos).
2. `grep -n "friendlyMicName\|friendlyName\|stereo mix\|Predeterminado del sistema" artifacts/acta-express/src/lib/micDevices.ts`.
3. **A/B de la tabla de traducción** (entrada → salida): "Built-in Audio Estéreo analógico" → "Micrófono interno del PC"; "Monitor of Built-in Audio…" → "Audio del sistema (no capta tu voz)"; deviceId "default" → "Predeterminado del sistema"; "USB PnP Sound Device" → "Micrófono USB"; "WH-1000XM4 Hands-Free" → "Micrófono de auriculares"; label vacío → "Micrófono N".
4. `git diff artifacts/acta-express/src/lib/micDevices.ts`… es untracked: incluir el CONTENIDO ÍNTEGRO actualizado en el informe.

## Protocolo de dudas
Los textos en español y el orden de patrones son CONTRATO. Dudas de contrato → DETENTE.

## Informe: `informe_mtM7.md` — formato estándar.
