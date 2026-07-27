# Spec MT-H6b — Escritura al vuelo en `useAudioRecorder` (heartbeat, H6)

**Ciclo:** 2026-07-25_resiliencia_grabacion · F4 · **Rol:** Ingeniero (Sonnet, rotación asistida)
**Diseño aprobado:** r1 APROBADO CON CAMBIOS + G1 (25-07). Vinculante. Regla de oro del ciclo: **la grabación JAMÁS falla por culpa del vault** (C1 del dictamen).
**Repo:** `/home/pueblac/AndroidStudioProjects/ActaExpressWeb`. Arranca sobre el working tree con **MT-H6a aplicada** (existe `artifacts/acta-express/src/lib/recordingVault.ts`). Toca SOLO lo de tu contrato.

## Objetivo
Copiar cada chunk de 1 s a IndexedDB al vuelo (fire-and-forget) durante la grabación, con heartbeat `lastChunkAt`, sin alterar EN NADA el flujo actual memoria→blob→base64. El borrado de sesiones NO va aquí (es MT-H6c: solo se borra con acta creada, descarte o 422).

## Contexto mínimo verificado
- `useAudioRecorder.ts`: `mediaRecorder.start(1000)` (`:231`) emite `ondataavailable` cada ~1 s; los chunks se acumulan en `chunksRef.current` (`:215-217`). El `mimeType` REAL solo se conoce tras instanciar: `mediaRecorder.mimeType` (`:220`).
- El hook se usa únicamente dentro de `home.tsx`, que está bajo `AuthProvider` → puedes llamar `useAuth()` dentro del hook (`import { useAuth } from "@/context/AuthContext"`).
- `startRecording(modo: ModoReunion)` ya recibe el modo (`:149`). Dos caminos construyen el stream (presencial `:159-172`, virtual `:173-208`) y confluyen en la creación del MediaRecorder (`:212`).

## Contrato
1. Modificar SOLO `artifacts/acta-express/src/hooks/useAudioRecorder.ts`.
2. Imports nuevos: `useAuth` y, de `../lib/recordingVault`: `createSession, appendChunk, purgeStaleKeepNewest, isVaultAvailable`.
3. Estado/refs nuevos: `const [vaultSessionId, setVaultSessionId] = useState<string | null>(null);` + `vaultSessionIdRef`, `vaultDisabledRef` (boolean), `chunkSeqRef` (number). Exponer `vaultSessionId: string | null` en el objeto de retorno y en `UseAudioRecorderReturn` (lo consume MT-H6c).
4. En `startRecording`, DESPUÉS de `new MediaRecorder(recordingStream)` y ANTES de `mediaRecorder.start(1000)`:
```ts
vaultDisabledRef.current = false;
chunkSeqRef.current = 0;
vaultSessionIdRef.current = null;
setVaultSessionId(null);
if (user && isVaultAvailable()) {
  try {
    const sid = await createSession({
      uid: user.uid,
      modo,
      mimeType: mediaRecorder.mimeType || "audio/webm",
    });
    vaultSessionIdRef.current = sid;
    setVaultSessionId(sid);
    purgeStaleKeepNewest(user.uid).catch(() => {}); // límite-1 al crear (cambio 3); fire-and-forget
  } catch {
    vaultDisabledRef.current = true; // vault caído → grabar como hoy
  }
}
```
5. En `ondataavailable` (mantener INTACTO el push a memoria):
```ts
if (e.data.size > 0) {
  chunksRef.current.push(e.data);
  if (!vaultDisabledRef.current && vaultSessionIdRef.current) {
    const seq = chunkSeqRef.current++;
    appendChunk(vaultSessionIdRef.current, seq, e.data).catch(() => {
      vaultDisabledRef.current = true; // QuotaExceeded/IDB roto → vault off, grabación sigue
    });
  }
}
```
6. **PROHIBIDO borrar sesiones del vault en este archivo**: ni en `onstop`, ni en `cleanupStreams`, ni en `stopRecording`. `vaultSessionId` debe seguir expuesto tras parar (lo necesita `home.tsx` para borrar cuando el acta se cree).
7. Ningún `await` nuevo dentro de `ondataavailable` (fire-and-forget puro). Ningún cambio en la lógica existente de streams, timer, base64, captureMode, micStream.

## Restricciones
Solo `useAudioRecorder.ts`. NO tocar `recordingVault.ts`, `home.tsx` ni UI. Sin dependencias nuevas. No commit.

## DoD (salida literal al informe)
1. `pnpm run typecheck` → exit 0.
2. `grep -n "createSession\|appendChunk\|purgeStaleKeepNewest\|vaultDisabledRef\|vaultSessionId\|chunkSeqRef\|isVaultAvailable" artifacts/acta-express/src/hooks/useAudioRecorder.ts`.
3. `grep -n "deleteSession" artifacts/acta-express/src/hooks/useAudioRecorder.ts` → **sin resultados** (prohibición del punto 6).
4. **A/B razonado** citando líneas del diff: (a) camino feliz — 3 chunks → seq 0,1,2 persistidos con heartbeat; (b) `appendChunk` rechaza en seq 1 → `vaultDisabledRef=true`, seq 2 NO se intenta persistir, PERO `chunksRef.current` contiene los 3 y el flujo blob→base64 es idéntico al actual; (c) `user` null o `isVaultAvailable()` false → cero llamadas al vault, grabación idéntica a hoy; (d) `createSession` lanza → catch → `vaultDisabledRef=true`, `mediaRecorder.start(1000)` se ejecuta igual.
5. `git diff` → SOLO `useAudioRecorder.ts`. Diff literal íntegro al informe.

## Protocolo de dudas
El orden (crear MediaRecorder → createSession con su mimeType real → start) es DISEÑO CONGELADO. Si `useAuth` dentro del hook te genera dudas de tipado, resuélvelas de la forma más simple y decláralo. Cualquier duda que exija cambiar el contrato → DETENTE y decláralo sin implementar.

## Informe: `informe_mtH6b.md` — formato estándar (qué se hizo / diff literal íntegro / evidencia DoD literal / desviaciones / dudas / estado commiteable).
