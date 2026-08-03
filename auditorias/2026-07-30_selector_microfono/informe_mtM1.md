# Informe MT-M1 — Módulo `micDevices.ts` + hook `useMicDevices`

**Ciclo:** 2026-07-30_selector_microfono · F4 · **Rol:** Ingeniero (Sonnet, rotación asistida)
**Repo:** `/home/pueblac/AndroidStudioProjects/ActaExpressWeb`, rama `linux`
**Precondición verificada:** `git status --short` LIMPIO, rama `linux`, HEAD `74e3d3230a69618088d16889c2e6421bf6ebcfdf` (prefijo `74e3d32` coincide con el exigido en la spec). Se procedió.

## Qué se hizo

Implementados exactamente los 2 archivos nuevos del contrato, sin tocar ningún archivo existente:

1. `artifacts/acta-express/src/lib/micDevices.ts` — capa de datos pura: `getPreferredMic`/`setPreferredMic` (persistencia localStorage por uid) y `listMicrophones` (enumeración async con fallback de label).
2. `artifacts/acta-express/src/hooks/useMicDevices.ts` — hook que envuelve `listMicrophones` reaccionando a `active` y al evento `devicechange`.

No se agregaron dependencias. No se tocó `useAudioRecorder`, `home.tsx` ni `useMicLevel`.

## Contenido íntegro de los archivos nuevos

### `artifacts/acta-express/src/lib/micDevices.ts`

```ts
export interface MicDevice {
  deviceId: string;
  label: string;
}

const key = (uid: string) => `actaexpress:micDeviceId:${uid}`;

export function getPreferredMic(uid: string): string | null {
  return localStorage.getItem(key(uid)) || null;
}

export function setPreferredMic(uid: string, deviceId: string): void {
  localStorage.setItem(key(uid), deviceId);
}

export async function listMicrophones(): Promise<MicDevice[]> {
  if (!navigator.mediaDevices?.enumerateDevices) return [];

  const devices = await navigator.mediaDevices.enumerateDevices();

  return devices
    .filter((d) => d.kind === "audioinput" && d.deviceId !== "")
    .map((d, i) => ({
      deviceId: d.deviceId,
      label: d.label || `Micrófono ${i + 1}`,
    }));
}
```

### `artifacts/acta-express/src/hooks/useMicDevices.ts`

```ts
import { useEffect, useState } from "react";
import { listMicrophones, type MicDevice } from "@/lib/micDevices";

export function useMicDevices(active: boolean): { microphones: MicDevice[] } {
  const [microphones, setMicrophones] = useState<MicDevice[]>([]);

  useEffect(() => {
    if (!active) {
      setMicrophones([]);
      return;
    }

    const refresh = () => {
      listMicrophones()
        .then(setMicrophones)
        .catch(() => setMicrophones([]));
    };

    refresh();

    if (!navigator.mediaDevices?.addEventListener) return;

    navigator.mediaDevices.addEventListener("devicechange", refresh);
    return () => {
      navigator.mediaDevices.removeEventListener("devicechange", refresh);
    };
  }, [active]);

  return { microphones };
}
```

## Evidencia DoD (salida literal)

### 1. `pnpm run typecheck` → exit 0

```
$ pnpm run typecheck:libs && pnpm -r --filter "./artifacts/**" --filter "./scripts" --if-present run typecheck
$ tsc --build
Scope: 4 of 9 workspace projects
artifacts/api-server typecheck$ tsc -p tsconfig.json --noEmit
artifacts/mockup-sandbox typecheck$ tsc -p tsconfig.json --noEmit
artifacts/acta-express typecheck$ tsc -p tsconfig.json --noEmit
scripts typecheck$ tsc -p tsconfig.json --noEmit
scripts typecheck: Done
artifacts/api-server typecheck: Done
artifacts/mockup-sandbox typecheck: Done
artifacts/acta-express typecheck: Done
EXIT:0
```

### 2. `grep -n "getPreferredMic\|setPreferredMic\|listMicrophones\|devicechange\|actaexpress:micDeviceId" ...`

```
artifacts/acta-express/src/lib/micDevices.ts:6:const key = (uid: string) => `actaexpress:micDeviceId:${uid}`;
artifacts/acta-express/src/lib/micDevices.ts:8:export function getPreferredMic(uid: string): string | null {
artifacts/acta-express/src/lib/micDevices.ts:12:export function setPreferredMic(uid: string, deviceId: string): void {
artifacts/acta-express/src/lib/micDevices.ts:16:export async function listMicrophones(): Promise<MicDevice[]> {
artifacts/acta-express/src/hooks/useMicDevices.ts:2:import { listMicrophones, type MicDevice } from "@/lib/micDevices";
artifacts/acta-express/src/hooks/useMicDevices.ts:14:      listMicrophones()
artifacts/acta-express/src/hooks/useMicDevices.ts:23:    navigator.mediaDevices.addEventListener("devicechange", refresh);
artifacts/acta-express/src/hooks/useMicDevices.ts:25:      navigator.mediaDevices.removeEventListener("devicechange", refresh);
```

### 3. A/B razonado

**(a) Permiso concedido → lista con labels reales.**
`listMicrophones` (micDevices.ts:16-27): tras `enumerateDevices()`, filtra `kind === "audioinput"` y `deviceId !== ""` (línea 22), y mapea `label: d.label || ...` (línea 25). Con permiso concedido, `d.label` viene poblado por el navegador, así que el `||` nunca cae al fallback y la lista devuelta trae los nombres reales del hardware.

**(b) API ausente o error → `[]` sin excepción.**
Dos guardas independientes cubren este caso:
- En `micDevices.ts:17`, `if (!navigator.mediaDevices?.enumerateDevices) return [];` cubre la ausencia del API (SSR, navegadores sin soporte) antes de tocar `enumerateDevices`.
- En el hook (`useMicDevices.ts:14-16`), `listMicrophones().then(setMicrophones).catch(() => setMicrophones([]))` captura cualquier rechazo de la promesa (p. ej. `enumerateDevices()` lanzando en un contexto restringido) y fuerza `[]` sin que la excepción se propague al render.

**(c) `devicechange` (enchufar USB con `active`) → refresh; `active=false` → sin listener vivo.**
Con `active === true` (useMicDevices.ts:6-24): el efecto llama `refresh()` una vez al montar/activar (línea 16) y luego registra `navigator.mediaDevices.addEventListener("devicechange", refresh)` (línea 23) tras verificar que el API existe (línea 20). Al enchufar/desenchufar un USB, el evento `devicechange` dispara `refresh`, que vuelve a llamar `listMicrophones()` y actualiza el estado — hot-refresh sin cortar nada (consistente con la decisión G0 de hot-swap sin cortar, resuelta en capas superiores por MT-M2/M3).
Con `active === false` (useMicDevices.ts:8-11): el efecto retorna temprano tras `setMicrophones([])`, sin ejecutar `refresh()` ni registrar el listener — nunca se llega a la línea 23. Cleanup citado (useMicDevices.ts:24-26): `return () => { navigator.mediaDevices.removeEventListener("devicechange", refresh); }` — se ejecuta cuando `active` pasa de `true` a `false` (o al desmontar), garantizando que no quede un listener vivo tras la desactivación.

**(d) get/set de persistencia con uid "u1" → clave exacta `actaexpress:micDeviceId:u1`.**
`key = (uid) => \`actaexpress:micDeviceId:${uid}\`` (micDevices.ts:6). Con `uid = "u1"`: `key("u1")` → `"actaexpress:micDeviceId:u1"`. `getPreferredMic("u1")` (línea 8-10) hace `localStorage.getItem("actaexpress:micDeviceId:u1") || null` — si no hay valor o es `""`, el `||` devuelve `null` (cumple "'' cuenta como null"). `setPreferredMic("u1", deviceId)` (línea 12-14) hace `localStorage.setItem("actaexpress:micDeviceId:u1", deviceId)`. Misma clave en ambos lados, generada por la única función `key`.

### 4. `git status --short` → exactamente los 2 archivos nuevos

```
?? artifacts/acta-express/src/hooks/useMicDevices.ts
?? artifacts/acta-express/src/lib/micDevices.ts
```

## Desviaciones

Ninguna. El contrato se implementó al pie de la letra: firmas idénticas a la spec, clave de persistencia idéntica, comportamiento de `listMicrophones` y `useMicDevices` conforme a lo descrito.

Nota de detalle interno (no contractual, declarada por transparencia): se usó `useState` simple para `microphones` (no `useRef`), y `refresh` se redefine en cada ejecución del efecto — es la opción "más simple, declarada" que habilita el protocolo de dudas de la spec para detalles internos.

## Dudas

Ninguna. No hubo necesidad de tocar el contrato.

## Commiteable

Sí, en cuanto a alcance y contenido (2 archivos nuevos, contrato cumplido, típecheck en verde). Recordatorio: por rol, el Ingeniero NO commitea — queda a criterio del Director/rotación siguiente decidir el commit.
