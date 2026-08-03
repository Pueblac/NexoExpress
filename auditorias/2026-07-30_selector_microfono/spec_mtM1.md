# Spec MT-M1 — Módulo `micDevices.ts` + hook `useMicDevices` (selector de micrófono)

**Ciclo:** 2026-07-30_selector_microfono · F4 · **Rol:** Ingeniero (Sonnet, rotación asistida)
**Diseño aprobado:** r1 APROBADO CON CAMBIOS (2) + G1 del Director (30-07). Decisiones G0 vinculantes: hot-swap sin cortar; la elección persiste como default por uid; CTA solo en el banner.
**Repo:** `/home/pueblac/AndroidStudioProjects/ActaExpressWeb`, rama `linux`, base `74e3d32`. Working tree LIMPIO — verifícalo; si no, DETENTE.

## Objetivo
La capa de datos del selector: enumerar micrófonos con nombre amigable, reaccionar a conexiones/desconexiones, y persistir la preferencia por usuario. SIN UI y SIN tocar la captura (eso es MT-M2/M3).

## Contexto mínimo verificado
- `enumerateDevices()` devuelve labels NO vacíos solo con permiso de micrófono concedido; sin permiso puede devolver `deviceId`/`label` vacíos. El consumidor principal (CTA del banner) corre DURANTE una grabación → permiso garantizado.
- Patrón de persistencia por uid ya existente: `actaexpress:<clave>:${uid}` en localStorage (p. ej. `actaexpress:modoReunion:${uid}` en home.tsx).
- Los `deviceId` son por origen y por máquina (ecosistema bi-máquina Linux/Windows): un id persistido puede no existir en la otra máquina — la VALIDACIÓN de existencia no va aquí (la resuelve MT-M4 con `{exact}`+fallback); este módulo solo lee/escribe.

## Contrato
1. **Nuevo** `artifacts/acta-express/src/lib/micDevices.ts`:
```ts
export interface MicDevice { deviceId: string; label: string; }

const key = (uid: string) => `actaexpress:micDeviceId:${uid}`;

export function getPreferredMic(uid: string): string | null;   // localStorage.getItem(key) ?? null; "" cuenta como null
export function setPreferredMic(uid: string, deviceId: string): void; // localStorage.setItem
export async function listMicrophones(): Promise<MicDevice[]>;
```
   `listMicrophones`: `navigator.mediaDevices.enumerateDevices()` → filtrar `kind === "audioinput"` → descartar entradas con `deviceId === ""` → mapear con `label` real o fallback `"Micrófono ${i + 1}"` si viene vacío. Si `navigator.mediaDevices?.enumerateDevices` no existe → devolver `[]` (nunca lanzar).
2. **Nuevo** `artifacts/acta-express/src/hooks/useMicDevices.ts`:
```ts
export function useMicDevices(active: boolean): { microphones: MicDevice[] }
```
   Comportamiento: cuando `active` pasa a true → `listMicrophones()` y set del estado; suscribirse a `navigator.mediaDevices.addEventListener("devicechange", refresh)` (con guard de existencia del API); cleanup: `removeEventListener`. Cuando `active` es false → estado `[]` y sin listener. Errores de `listMicrophones` → estado `[]` silencioso (nunca romper el render).
3. Sin dependencias nuevas. Sin tocar ningún archivo existente.

## Restricciones
Solo los 2 archivos nuevos. NO tocar useAudioRecorder, home.tsx ni useMicLevel. No commit.

## DoD (salida literal al informe)
1. `pnpm run typecheck` → exit 0.
2. `grep -n "getPreferredMic\|setPreferredMic\|listMicrophones\|devicechange\|actaexpress:micDeviceId" artifacts/acta-express/src/lib/micDevices.ts artifacts/acta-express/src/hooks/useMicDevices.ts`.
3. **A/B razonado** citando líneas: (a) permiso concedido → lista con labels reales; (b) API ausente o error → `[]` sin excepción; (c) `devicechange` (enchufar USB con `active`) → refresh; `active=false` → sin listener vivo (cleanup citado); (d) get/set de persistencia con uid "u1" → clave exacta `actaexpress:micDeviceId:u1`.
4. `git status --short` → exactamente los 2 archivos nuevos (`??`). Contenido ÍNTEGRO de ambos al informe (untracked, no salen en `git diff`).

## Protocolo de dudas
Firmas y clave de persistencia son CONTRATO. Detalles internos (useState vs useRef del refresh): lo más simple, declarado. Dudas de contrato → DETENTE.

## Informe: `informe_mtM1.md` — formato estándar.
