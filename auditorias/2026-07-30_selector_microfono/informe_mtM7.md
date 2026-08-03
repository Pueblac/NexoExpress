# Informe MT-M7 — Nombres amigables de micrófonos (F3′ tras E2E Linux r1)

**Ciclo:** 2026-07-30_selector_microfono · F3′→F4 · **Rol:** Ingeniero (Sonnet, rotación asistida)
**Repo:** `/home/pueblac/AndroidStudioProjects/ActaExpressWeb`, rama `linux`.
**Spec:** `spec_mtM7.md`

## Precondición

Verificada antes de tocar nada (`git status --short`):

```
 M artifacts/acta-express/src/hooks/useAudioRecorder.ts
 M artifacts/acta-express/src/pages/home.tsx
?? artifacts/acta-express/src/hooks/useMicDevices.ts
?? artifacts/acta-express/src/lib/micDevices.ts
```

Coincide con la tanda M exigida. Continué.

## Implementación

Solo se tocó `artifacts/acta-express/src/lib/micDevices.ts`:

1. `MicDevice` ampliado con `friendlyName: string` y `detail?: string` (gana campos, no rompe consumidores existentes).
2. Añadido `friendlyMicName(label, deviceId)` exactamente como en el contrato: `default`→"Predeterminado del sistema", `communications`→"Dispositivo de comunicaciones", luego los patrones heurísticos en el orden literal del contrato (monitor/stereo-mix primero → "Audio del sistema (no capta tu voz)"; auriculares/BT/USB/cámara/interno; fallback `label || "Micrófono"`).
3. `listMicrophones()` ahora rellena `friendlyName`/`detail` llamando a `friendlyMicName(d.label, d.deviceId)`; cuando `d.label` viene vacío, `friendlyName` cae al fallback existente `Micrófono ${i+1}` (no al resultado heurístico) y `detail` queda `undefined`, tal como pide el punto 2 del contrato.

No se tocaron `useAudioRecorder.ts`, `home.tsx` ni `useMicDevices.ts` (consumo diferido a MT-M6). No se hizo commit.

## DoD

### 1. `pnpm run typecheck` (salida literal, desde la raíz del repo)

```
$ pnpm run typecheck
$ pnpm run typecheck:libs && pnpm -r --filter "./artifacts/**" --filter "./scripts" --if-present run typecheck
$ tsc --build
Scope: 4 of 9 workspace projects
artifacts/acta-express typecheck$ tsc -p tsconfig.json --noEmit
artifacts/api-server typecheck$ tsc -p tsconfig.json --noEmit
artifacts/mockup-sandbox typecheck$ tsc -p tsconfig.json --noEmit
scripts typecheck$ tsc -p tsconfig.json --noEmit
scripts typecheck: Done
artifacts/api-server typecheck: Done
artifacts/acta-express typecheck: Done
artifacts/mockup-sandbox typecheck: Done
EXIT_CODE=0
```

`home.tsx` sigue compilando: `MicDevice` solo ganó campos, ningún consumidor existente se rompió.

### 2. `grep -n "friendlyMicName\|friendlyName\|stereo mix\|Predeterminado del sistema" artifacts/acta-express/src/lib/micDevices.ts`

```
4:  friendlyName: string;
20:export function friendlyMicName(label: string, deviceId: string): { friendlyName: string; detail?: string } {
21:  if (deviceId === "default") return { friendlyName: "Predeterminado del sistema", detail: label || undefined };
22:  if (deviceId === "communications") return { friendlyName: "Dispositivo de comunicaciones", detail: label || undefined };
24:  if (/monitor|stereo mix|mezcla estéreo|loopback/.test(l)) return { friendlyName: "Audio del sistema (no capta tu voz)", detail: label };
25:  if (/head|auricular|earph|airpod|buds|hands-?free/.test(l)) return { friendlyName: "Micrófono de auriculares", detail: label };
26:  if (/bluetooth|\bbt\b/.test(l)) return { friendlyName: "Micrófono Bluetooth", detail: label };
27:  if (/usb/.test(l)) return { friendlyName: "Micrófono USB", detail: label };
28:  if (/webcam|cámara|camera/.test(l)) return { friendlyName: "Micrófono de la cámara", detail: label };
29:  if (/built-?in|internal|interno|analógico|analog/.test(l)) return { friendlyName: "Micrófono interno del PC", detail: label };
30:  return { friendlyName: label || "Micrófono", detail: undefined };
42:      const { friendlyName, detail } = friendlyMicName(d.label, d.deviceId);
46:        friendlyName: d.label ? friendlyName : label,
```

### 3. A/B de la tabla de traducción (entrada → salida)

Verificado ejecutando `friendlyMicName` compilado a JS puro (vía `tsc` a un directorio temporal fuera del repo, invocado con `node -e`) — no requirió DOM ni mocks, la función es pura:

| Entrada (`label`, `deviceId`) | Salida obtenida | Esperado (spec) | Coincide |
|---|---|---|---|
| `"Built-in Audio Estéreo analógico"`, id normal | `{"friendlyName":"Micrófono interno del PC","detail":"Built-in Audio Estéreo analógico"}` | "Micrófono interno del PC" | Sí |
| `"Monitor of Built-in Audio Analog Stereo"`, id normal | `{"friendlyName":"Audio del sistema (no capta tu voz)","detail":"Monitor of Built-in Audio Analog Stereo"}` | "Audio del sistema (no capta tu voz)" | Sí |
| `""`, `deviceId: "default"` | `{"friendlyName":"Predeterminado del sistema"}` | "Predeterminado del sistema" | Sí |
| `"USB PnP Sound Device"`, id normal | `{"friendlyName":"Micrófono USB","detail":"USB PnP Sound Device"}` | "Micrófono USB" | Sí |
| `"WH-1000XM4 Hands-Free"`, id normal | `{"friendlyName":"Micrófono de auriculares","detail":"WH-1000XM4 Hands-Free"}` | "Micrófono de auriculares" | Sí |
| `""`, id normal (no `default`/`communications`), simulando el paso completo de `listMicrophones` (índice 0) | `{"deviceId":"xyz789","label":"Micrófono 1","friendlyName":"Micrófono 1"}` | "Micrófono N" (fallback, sin heurística) | Sí |

Las 6 filas del A/B coinciden exactamente con lo exigido en el punto 3 del DoD.

### 4. Contenido íntegro actualizado de `artifacts/acta-express/src/lib/micDevices.ts` (archivo `??`, untracked — no aplica `git diff`)

```ts
export interface MicDevice {
  deviceId: string;
  label: string;
  friendlyName: string;
  detail?: string;
}

const key = (uid: string) => `actaexpress:micDeviceId:${uid}`;

export function getPreferredMic(uid: string): string | null {
  return localStorage.getItem(key(uid)) || null;
}

export function setPreferredMic(uid: string, deviceId: string): void {
  localStorage.setItem(key(uid), deviceId);
}

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

export async function listMicrophones(): Promise<MicDevice[]> {
  if (!navigator.mediaDevices?.enumerateDevices) return [];

  const devices = await navigator.mediaDevices.enumerateDevices();

  return devices
    .filter((d) => d.kind === "audioinput" && d.deviceId !== "")
    .map((d, i) => {
      const label = d.label || `Micrófono ${i + 1}`;
      const { friendlyName, detail } = friendlyMicName(d.label, d.deviceId);
      return {
        deviceId: d.deviceId,
        label,
        friendlyName: d.label ? friendlyName : label,
        detail,
      };
    });
}
```

## Desviaciones

Ninguna. El texto en español y el orden de patrones se implementaron literalmente como en el contrato.

## Dudas

Ninguna que exigiera DETENTE.

## ¿Commiteable?

No se hizo commit (fuera de mandato de esta MT). Working tree queda con la misma tanda M de 4 archivos (2 `M` + 2 `??`), ahora con `micDevices.ts` conteniendo el traductor heurístico. `pnpm run typecheck` en verde (exit 0). Listo para que MT-M6 (hook/UI) consuma `friendlyName`/`detail`.
