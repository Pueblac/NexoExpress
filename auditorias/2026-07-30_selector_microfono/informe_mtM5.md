# Informe MT-M5 — Endurecimiento adversarial del selector de micrófono (cierre de tanda)

**Ciclo:** 2026-07-30_selector_microfono · F4 · **Rol:** Ingeniero (Sonnet, rotación asistida)
**Repo:** `/home/pueblac/AndroidStudioProjects/ActaExpressWeb`, rama `linux`.
**Spec:** `spec_mtM5.md`

## Precondición

Verificada antes de tocar nada (`git status --short`):

```
 M artifacts/acta-express/src/hooks/useAudioRecorder.ts
 M artifacts/acta-express/src/pages/home.tsx
?? artifacts/acta-express/src/hooks/useMicDevices.ts
?? artifacts/acta-express/src/lib/micDevices.ts
```

Coincide con el conjunto de rutas exigido (mismo orden de estados que M1-M4, solo difiere el orden de listado literal del enunciado). Continué.

## Veredicto global

**Checklist 10/10 PASA. Cero cambios de código.** Los 4 archivos de la tanda ya cumplen la regla de oro, el diseño congelado (r1+G1, incluidos cambio 1 = resume en vuelo y cambio 2 = cerrojo+época) y las políticas Q2/Q3/Q4. No hubo ninguna FALLA que exigiera fix mínimo ni ninguna duda que exigiera detenerse.

## Checklist adversarial

| # | Punto | Veredicto | Cita / traza |
|---|-------|-----------|---------------|
| 1 | Regla de oro — ningún camino corta la grabación | **PASA** | Listado completo de `getUserMedia`/`getDisplayMedia` nuevos y su manejo: (a) `getDisplayAudioStream` L55/L73 — ambos `getDisplayMedia` con try/catch interno, retorna `null` en vez de lanzar; el llamador (`useAudioRecorder.ts` L270-275) hace `setError(...); return;` sin tocar streams previos. (b) `mixAudioStreams` preferido L124-126 dentro de try interno L123-131, catch → fallback default L130, ambos dentro del try externo L121-137 cuyo catch L137-139 no relanza ("Microphone unavailable — OK"). (c) `getMicWithPreference` preferido L198 en try/catch L197-202, catch no relanza, cae a reintento default L204 (sin wrap propio, pero ese reintento vive dentro del try externo preexistente de `startRecording` L223-232, catch L228-232 → `setError`+`return`). (d) `swapMicrophone` L407, envuelto en try/catch L403-425, catch L421-422 devuelve `{ok:false, message}` sin tocar el mic/grabación en curso. Ningún camino deja la grabación a medias ni lanza sin capturar. |
| 2 | T1 arranque — ctx que no llega a `running` | **PASA** | `useAudioRecorder.ts` L234-260: si `audioCtx.state !== "running"` tras el intento de `resume()` (L237-238), no se rutea (`routed` queda `false`, ctx se cierra L251), y el fallback declarado graba el stream crudo directo (`recordingStream = micRaw`, L258) marcando `routingDisabledRef.current = true` (L259) — idéntico al comportamiento pre-ciclo. `swapMicrophone` L398-399 comprueba ese mismo ref y responde `"El cambio de micrófono no está disponible en esta grabación."` sin intentar nada. |
| 3 | T1 en vuelo (cambio 1) — `onstatechange`→`resume()` en AMBOS modos | **PASA** | `attachStateWatch` (L144-151) hace `ctx.onstatechange = () => { if (ctx.state === "suspended") ctx.resume().catch(()=>{}); }`. Se invoca en presencial en **L247** (dentro del `if (audioCtx.state === "running")`, único caso donde el ctx queda enrutado) y en virtual (mix, `mixAudioStreams`) en **L291**, incondicional tras crear el ctx de mezcla. Las dos líneas cubren los dos modos de grabación con enrutamiento activo. |
| 4 | T5 (cambio 2) — cerrojo `isSwappingRef` + época | **PASA** | Doble click en dos mics: el segundo llamado a `swapMicrophone` se corta síncronamente en `if (isSwappingRef.current) return {ok:false,...}` (**L400**), antes de llegar a `getUserMedia`, porque el primero ya puso `isSwappingRef.current = true` (**L401**) y solo lo libera en el `finally` (**L424**) tras resolver por completo. Perdedor tardío: si mientras el `getUserMedia` del swap está en vuelo la grabación se detiene, el chequeo `epoch !== swapEpochRef.current \|\| !mediaRecorderRef.current \|\| mediaRecorderRef.current.state !== "recording"` (**L408**) detecta el estado obsoleto y `newMic.getTracks().forEach(t => t.stop())` (**L409**) detiene los tracks nuevos sin conectarlos, retornando `"El cambio llegó tarde y fue descartado."` (L410). Observación (no bloqueante, no FALLA): dado que el cerrojo `isSwappingRef` impide que dos swaps corran concurrentemente, la rama `epoch !== swapEpochRef.current` de la condición L408 es hoy inalcanzable en la práctica (dos clicks nunca llegan a competir por el `getUserMedia`); el comportamiento "perdedor tardío" que sí ocurre en producción se dispara por el chequeo de estado del `mediaRecorder` (grabación detenida durante el swap), no por la época. No es un bug — el resultado observable pedido por el checklist se cumple igual — pero se declara por transparencia; no toca firmas ni política, así que no amerita fix. |
| 5 | Orden del swap + cero referencias a MediaRecorder/vault | **PASA** | Orden literal en `swapMicrophone`: connect-nuevo `newSource.connect(destRef.current)` (**L413**) → disconnect-viejo `micSourceRef.current?.disconnect()` (**L414**) → stop-viejos `micStreamRef.current?.getTracks().forEach(t => t.stop())` (**L415**). Grep de `vault\|Vault` y de llamadas a métodos de `mediaRecorder.` dentro del cuerpo de la función (L396-426): cero resultados — el único uso relacionado es la LECTURA `mediaRecorderRef.current.state` (L408), necesaria para el chequeo "perdedor tardío" del punto 4, no una mutación del `MediaRecorder` ni del vault. `createSession`/`appendChunk`/`purgeStaleKeepNewest`/`isVaultAvailable` solo aparecen en `startRecording` (L321-341), fuera del swap — confirmado por grep del archivo completo. |
| 6 | Detector re-armado — `setMicStream(newMic)` con stream CRUDO | **PASA** | `swapMicrophone` L418: `setMicStream(newMic)` usa el `MediaStream` crudo devuelto por `getUserMedia`, no `dest.stream`. `useMicLevel.ts` L94, `}, [active, micStream]);` — el `useEffect` depende de `micStream`, así que al cambiar la referencia recrea `audioCtx`/`analyser`/`source` (L37-41) apuntando al mic nuevo. |
| 7 | Persistencia — éxito persiste, fallo no, preferido inválido al iniciar no borra | **PASA** | Éxito: `if (user) setPreferredMic(user.uid, deviceId);` (**L419**), solo alcanzable tras conectar el nuevo source con éxito (después de L412-417); ningún `return` de error anterior llega a esa línea. Fallo: los 4 `return {ok:false,...}` (L397, L399, L400, L410) y el `catch` (L421-422) retornan antes de L419 — nunca se persiste. Preferido inválido al iniciar: `getMicWithPreference` L199-202 y `mixAudioStreams` L127-129 comentan explícitamente "Q2: la clave NO se limpia" y ninguna de las dos funciones llama a una API de borrado; confirmado por grep de `removeItem` en `micDevices.ts` — cero resultados; `getPreferredMic`/`setPreferredMic` (`micDevices.ts` L8-14) son las únicas funciones que tocan esa entrada de `localStorage` y ninguna hace `removeItem`. |
| 8 | Fugas — tracks/ctx/listeners al parar | **PASA** | `cleanupStreams` (L182-192), invocado desde `mediaRecorder.onstop` (L357): detiene `displayStreamRef.current` y `micStreamRef.current` (que tras un swap exitoso apunta al mic NUEVO, L417, cubriendo también los tracks post-swap), cierra `audioCtxRef.current.close()` (implícitamente desconecta los `AudioNode` restantes del contexto), y anula `displayStreamRef/micStreamRef/audioCtxRef/micSourceRef/destRef` + `setMicStream(null)`. Los tracks viejos del swap ya se detuvieron en el propio swap (L415), sin esperar al `stop`. `useMicDevices.ts` L8-11: si `active` es `false` (banner apagado, `isRecording && micSilent` deja de ser `true`), el efecto hace `setMicrophones([]); return;` **antes** de llegar al `addEventListener` (L23), y el cleanup del efecto anterior (L24-26) ya removió el listener previo — sin listener huérfano. |
| 9 | Virtual `"system"` — sin mic, banner inalcanzable | **PASA** (con observación declarada) | Sin mic: `mixAudioStreams` deja `micStream = null` cuando falla el `getUserMedia` (catch L137-139), `setMicStream(mixMicStream)` (`home.tsx` vía hook, L292 de `useAudioRecorder.ts`) deja `micStream` en `null`; `useMicLevel.ts` L32-34: `if (!active \|\| !micStream) { setMicSilent(false); return; }` — con `micStream` nulo, `micSilent` nunca pasa a `true`, así que el banner (`home.tsx` L372, `{isRecording && micSilent && (`) nunca se renderiza y el CTA (dentro de ese bloque, L385-403) es inalcanzable. Grep de `swapMicrophone(` en todo `src/`: el único punto de invocación fuera del propio hook es `handleSwapMic` (`home.tsx` L233-240), y este solo se referencia desde el `onClick` del `DropdownMenuItem` dentro del banner (L397) — no existe ningún otro camino en la UI para llamar `swapMicrophone` sin pasar por el banner. Respecto a la pregunta de Q4 ("¿hace falta guard extra en `swapMicrophone`?"): el código de `swapMicrophone` en sí NO comprueba `micSourceRef.current` antes de conectar (`newSource.connect(destRef.current)` L413 es incondicional), así que si se lo llamara con `destRef` presente pero `micSourceRef` null (mic virtual ausente), SÍ conectaría un mic nuevo donde antes no había ninguno. Pero dado que hoy el único call site está detrás del guard de UI verificado arriba (banner requiere `micSilent`, que requiere `micStream` no nulo), esa condición es inalcanzable en producción. Conforme al dictamen Q4 ("el guard correcto es que sin banner no hay CTA"), esto es exactamente lo verificado — se declara la ausencia de guard interno en `swapMicrophone` como fiel al diseño aprobado, no como fix pendiente: añadir un guard ahí sería tocar la firma/lógica de la función swap, lo cual el propio Q4 puso fuera de alcance salvo desviación real, y no la hay. |
| 10 | Sin regresiones de ciclos previos | **PASA** | Vault H6: `recordingVault.ts` no aparece en `git status --short` (no tocado por la tanda); sus únicos puntos de uso en `useAudioRecorder.ts` (`createSession` L323, `appendChunk` L341, `purgeStaleKeepNewest` L330, `isVaultAvailable` L321) están intactos y fuera del swap (confirmado en el punto 5). Guard de captura confiable (texto Q3, sin fallback silencioso virtual): `home.tsx`/`useAudioRecorder.ts` conservan el mensaje de error de `getDisplayAudioStream` fallido ("No se capturó audio...", L271-273) sin cambios respecto al `git diff` (bloque no tocado por esta tanda ni por M1-M4). |

## DoD

### 1. `pnpm run typecheck` (salida literal)

```
$ pnpm run typecheck:libs && pnpm -r --filter "./artifacts/**" --filter "./scripts" --if-present run typecheck
$ tsc --build
Scope: 4 of 9 workspace projects
artifacts/acta-express typecheck$ tsc -p tsconfig.json --noEmit
artifacts/api-server typecheck$ tsc -p tsconfig.json --noEmit
artifacts/mockup-sandbox typecheck$ tsc -p tsconfig.json --noEmit
scripts typecheck$ tsc -p tsconfig.json --noEmit
scripts typecheck: Done
artifacts/api-server typecheck: Done
artifacts/mockup-sandbox typecheck: Done
artifacts/acta-express typecheck: Done
EXIT_CODE=0
```

### 2. `git diff --stat` de la tanda completa (working tree vs HEAD; acumula M1-M5)

```
 .../acta-express/src/hooks/useAudioRecorder.ts     | 158 +++++++++++++++++++--
 artifacts/acta-express/src/pages/home.tsx          |  52 ++++++-
 2 files changed, 192 insertions(+), 18 deletions(-)
```

(`micDevices.ts` y `useMicDevices.ts` son archivos nuevos `??`, no aparecen en `--stat` de `git diff` contra `HEAD` porque no están trackeados; su contenido íntegro se leyó y auditó igual — ver puntos 7-9 de la tabla.)

### 3. Diff literal de los fixes propios de MT-M5

**Checklist 10/10 PASA, cero cambios.** No se modificó ningún archivo de la tanda; el `git diff` de arriba es 100% obra de M1-M4, ya presente en la precondición.

## Desviaciones

Ninguna. No se tocó ningún archivo.

## Dudas

Ninguna que exigiera cambiar el contrato. La única observación no bloqueante es la redundancia de la época en el punto 4 (comportamiento correcto, mecanismo parcialmente decorativo dado el cerrojo) y la dependencia del guard UI-only en el punto 9 (explícitamente avalada por Q4). Ninguna requiere DETENTE.

## ¿Commiteable?

No se hizo commit (fuera de mandato explícito de esta MT). El working tree queda exactamente como en la precondición: los 4 archivos de M1-M4 sin cambios adicionales, `pnpm run typecheck` en verde (exit 0), checklist adversarial 10/10 PASA. Listo para que el Director/Arquitecto decida el cierre de la tanda y el commit.
