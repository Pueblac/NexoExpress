# Spec MT-H6c — Tarjeta de recuperación + ciclo de vida del vault en `home.tsx` (H6)

**Ciclo:** 2026-07-25_resiliencia_grabacion · F4 · **Rol:** Ingeniero (Sonnet, rotación asistida)
**Diseño aprobado:** r1 APROBADO CON CAMBIOS + G1 (25-07). Cambios vinculantes aquí: (1) `msDuration = lastChunkAt − startedAt`, (3) purga límite-1 al montar, (4) borrado también en 422 terminal (conservar en red/5xx), + mitigación T2×T5 del Arquitecto: **re-verificar heartbeat al pulsar Recuperar**. Decisión G0: recuperación OFRECIDA, nunca automática.
**Repo:** `/home/pueblac/AndroidStudioProjects/ActaExpressWeb`. Arranca sobre el working tree con **MT-H6a + MT-H6b aplicadas** (vault + `vaultSessionId` expuesto por el hook). Toca SOLO lo de tu contrato.

## Objetivo
Al abrir la app tras un crash, ofrecer recuperar la grabación interrumpida (tarjeta Recuperar/Descartar) y reinyectarla por el pipeline existente. Además, cerrar el ciclo de vida: borrar la sesión del vault cuando el acta se crea bien o cuando el server la rechaza con 422 (determinista), conservarla en errores transitorios.

## Contexto mínimo verificado
- `home.tsx:88-123`: mutación `processAudio` con `onSuccess`/`onError` centrales. Los errores del cliente generado son `ApiError` con propiedad **`.status: number`** (`lib/api-client-react/src/custom-fetch.ts:176`) → detectar 422 con `(err as any)?.status === 422`.
- `home.tsx:139-155`: useEffect de auto-proceso que dispara `processAudio.mutate({ data: { audioBase64, mimeType: "audio/webm", msDuration: duration, generarSintesis: generarSintesisRef.current } })`. La recuperación NO debe pasar por este efecto (ruta imperativa estanca, T4 del dictamen).
- `blobToBase64` vive en `useAudioRecorder.ts:19-32` como función de módulo NO exportada.
- El hook ya expone `vaultSessionId: string | null` (MT-H6b). `useAuth()` ya se usa en home (`user.uid` disponible; Home solo se monta con user resuelto).
- `react-query`: `mutation.mutate(variables, { onSuccess, onError })` ejecuta los callbacks per-call ADEMÁS de los centrales.

## Contrato
1. Modificar `artifacts/acta-express/src/pages/home.tsx` y UNA línea de `useAudioRecorder.ts`: exportar `blobToBase64` (`export function blobToBase64…`).
2. Imports en home desde `@/lib/recordingVault`: `listSessions` no hace falta — usar `purgeStaleKeepNewest, getSession, readChunks, deleteSession, isStale, isVaultAvailable`, tipo `VaultSessionMeta`; y `blobToBase64` desde `@/hooks/useAudioRecorder`.
3. Estado: `const [orphanSession, setOrphanSession] = useState<VaultSessionMeta | null>(null);`
4. **Detección al montar** — `useEffect` con deps `[user?.uid]`:
```ts
if (!user || !isVaultAvailable()) return;
purgeStaleKeepNewest(user.uid)         // límite-1 + devuelve la huérfana conservada
  .then((orphan) => setOrphanSession(orphan))
  .catch(() => {});                    // vault roto → sin tarjeta, app intacta
```
5. **Tarjeta** (`data-testid="card-recuperacion"`), render solo si `orphanSession && !isRecording && !processAudio.isPending`, colocada encima del selector de modo, estilo consistente con las cards existentes (borde `border-primary/30`, fondo suave): texto **"Se encontró una grabación interrumpida (~X min)"** con `X = Math.max(1, Math.round((orphanSession.lastChunkAt - orphanSession.startedAt) / 60000))`, y dos botones: **Recuperar** (`data-testid="btn-recuperar"`) y **Descartar** (`data-testid="btn-descartar"`, variante outline/ghost).
6. **Descartar:** `deleteSession(id).catch(() => {})`, `setOrphanSession(null)`, toast "Grabación descartada".
7. **Recuperar** (handler async, ruta imperativa — NO tocar el useEffect de auto-proceso ni `lastProcessedAudioRef`):
```ts
const meta = await getSession(orphanSession.sessionId).catch(() => null);
if (!meta || !isStale(meta)) {          // mitigación T2×T5: volvió a latir u desapareció
  setOrphanSession(null);
  toast({ title: "Grabación no recuperable", description: "Esa grabación sigue activa en otra pestaña o ya no existe." });
  return;
}
const chunks = await readChunks(meta.sessionId).catch(() => []);
if (chunks.length === 0) { deleteSession(meta.sessionId).catch(() => {}); setOrphanSession(null); /* toast destructive "grabación vacía" */ return; }
const blob = new Blob(chunks, { type: meta.mimeType || "audio/webm" });
const audioBase64 = await blobToBase64(blob);
processAudio.mutate(
  { data: { audioBase64, mimeType: "audio/webm", msDuration: Math.max(1000, meta.lastChunkAt - meta.startedAt), generarSintesis: generarSintesisRef.current } },
  {
    onSuccess: () => { deleteSession(meta.sessionId).catch(() => {}); setOrphanSession(null); },
    onError: (err: any) => { if (err?.status === 422) { deleteSession(meta.sessionId).catch(() => {}); setOrphanSession(null); } }, // red/5xx: conservar (tarjeta sigue)
  }
);
```
8. **Ciclo de vida del flujo NORMAL** (D-C + cambio 4) — en los callbacks CENTRALES de `processAudio`:
   - `onSuccess`: además de lo existente, `if (vaultSessionId) deleteSession(vaultSessionId).catch(() => {});`
   - `onError`: además del toast, `if ((err as any)?.status === 422 && vaultSessionId) deleteSession(vaultSessionId).catch(() => {});`
   (Nota: en la ruta de recuperación `vaultSessionId` del hook es normalmente `null` — los per-call del punto 7 cubren esa sesión. Si ambos corren, `deleteSession` sobre id ya borrado no debe romper: el vault lo tolera.)
9. Los textos y `data-testid` son contrato (los usa el E2E de F5). Ninguna llamada al vault puede lanzar sin catch.

## Restricciones
Solo `home.tsx` + la línea `export` en `useAudioRecorder.ts`. NO tocar `recordingVault.ts` ni el useEffect de auto-proceso (`:139-155`) más allá de lo especificado (que es: NO tocarlo). Sin dependencias nuevas. No commit.

## DoD (salida literal al informe)
1. `pnpm run typecheck` → exit 0.
2. `grep -n "card-recuperacion\|btn-recuperar\|btn-descartar\|purgeStaleKeepNewest\|getSession\|readChunks\|deleteSession\|isStale\|status === 422\|blobToBase64" artifacts/acta-express/src/pages/home.tsx` y `grep -n "export function blobToBase64" artifacts/acta-express/src/hooks/useAudioRecorder.ts`.
3. **A/B razonado de los 4 caminos del ciclo de vida** citando líneas del diff: (a) acta OK en flujo normal → `deleteSession(vaultSessionId)`; (b) 422 en flujo normal → ídem; (c) recuperación con acta OK → delete per-call + tarjeta fuera; (d) recuperación con error de RED → sesión CONSERVADA, tarjeta sigue. + traza de la mitigación T2×T5 (sesión que volvió a latir → toast y salida SIN procesar).
4. **A/B del doble disparo (T4):** demostrar citando líneas que Recuperar NO altera `audioBase64`/`duration`/`lastProcessedAudioRef` del hook → el useEffect de auto-proceso no puede re-disparar con el audio recuperado.
5. `git diff` → SOLO `home.tsx` y `useAudioRecorder.ts` (1 línea). Diff literal íntegro al informe.

## Protocolo de dudas
Los umbrales, textos, testids y la política 422-borra/red-conserva son DISEÑO CONGELADO. Si el tipado del `onError` per-call te da problemas, resuélvelo simple (`err: any`) y decláralo. Cualquier duda que exija cambiar el contrato → DETENTE y decláralo sin implementar.

## Informe: `informe_mtH6c.md` — formato estándar (qué se hizo / diff literal íntegro / evidencia DoD literal / desviaciones / dudas / estado commiteable).
