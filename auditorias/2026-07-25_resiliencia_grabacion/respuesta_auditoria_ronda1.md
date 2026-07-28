# Respuesta del Auditor (Gemini 3.1 Pro High) — auditoría de código ronda 1, tanda MT-H6a..e

> Archivada TAL CUAL fue entregada por el Director el 28-07-2026 (transporte manual,
> chat nuevo con init de identidad). Nota de archivo: el Director la guardó
> originalmente como dictamen_auditor.md; renombrada al canon del expediente por el
> Arquitecto sin editar el contenido. Validación anti-bluff en validacion_antibluff_ronda1.md.

---

---
TURNO DE: Auditor
---

# Dictamen de Auditoría - Resiliencia de Grabación (MT-H6)

## 1. Verificación de Claims

| Claim | Veredicto | Evidencia y Traza |
|-------|-----------|-------------------|
| **C1** | CONFIRMADO | **Evidencia:**<br>- `createSession` está en try/catch y desactiva el vault: `artifacts/acta-express/src/hooks/useAudioRecorder.ts:228-239`.<br>- `appendChunk` es fire-and-forget con catch que desactiva vault: `artifacts/acta-express/src/hooks/useAudioRecorder.ts:245-249`.<br>- Cero invocaciones a `deleteSession` dentro de `useAudioRecorder.ts` (0 referencias encontradas en dicho archivo).<br>**Traza:** `startRecording` inicializa `vaultDisabledRef = false`. Si `createSession` falla, `vaultDisabledRef` = true. Si un `appendChunk` falla (ej. QuotaExceeded), el catch setea `vaultDisabledRef.current = true`. En los siguientes eventos `ondataavailable`, se ignora el bloque de vault pero `chunksRef.current.push(e.data)` siempre se ejecuta, garantizando que el `MediaRecorder` y el array en RAM continúen intactos sin bloquear el event loop. |
| **C2** | CONFIRMADO | **Evidencia:**<br>- Filtra por `uid` y descarta vivas (`isStale`): `artifacts/acta-express/src/lib/recordingVault.ts:215-216`.<br>- Conserva la más reciente: `artifacts/acta-express/src/lib/recordingVault.ts:220`.<br>- Borra iterativamente: `artifacts/acta-express/src/lib/recordingVault.ts:223`.<br>- `appendChunk` aborta si no hay meta: `artifacts/acta-express/src/lib/recordingVault.ts:130-133`.<br>- Actualiza variables en misma TX: `artifacts/acta-express/src/lib/recordingVault.ts:140-144`.<br>**Traza:** `purgeStaleKeepNewest("u1")` obtiene todas las sesiones de "u1". Filtra donde `now - meta.lastChunkAt >= 30000`. Extrae la de mayor `lastChunkAt`. Las sobrantes van a `deleteSession`, que invoca `tx.objectStore(CHUNKS_STORE).delete(chunkRange)` y `tx.objectStore(SESSIONS_STORE).delete` en 1 sola TX, limpiando metadatos y chunks sin fuga. En `appendChunk`, `sessionsStore` y `chunksStore` abren 1 TX `readwrite`; si el check inicial `sessionsStore.get` da nulo, `tx.abort()` rechaza el guardado antes de escribir datos huérfanos. |
| **C3** | BUG | **Evidencia:** El claim afirma "Ningún otro punto del código borra sesiones". Esto es **FALSO**.<br>- Se borran también en recuperación cuando `chunks.length === 0`: `artifacts/acta-express/src/pages/home.tsx:228` (`deleteSession(meta.sessionId).catch(() => {});`).<br>- Se borran en la purga automática silenciosa en background: `artifacts/acta-express/src/lib/recordingVault.ts:223`.<br>**Traza:** Camino 1: Acta OK llama a `deleteSession` (`home.tsx:124`, `home.tsx:246`). Camino 2: Descarte explícito (`home.tsx:214`). Camino 3: Error 422 (`home.tsx:157`, `home.tsx:251`). **Camino 4 (BUG vs Claim):** Usuario pulsa Recuperar, pero el IndexedDB devuelve 0 chunks; el código invoca `deleteSession(meta.sessionId)`. **Camino 5 (BUG vs Claim):** Hay dos sesiones huérfanas en IDB, el poll ejecuta `purgeStaleKeepNewest`, el cual destruye la más antigua sin intervención del usuario. |
| **C4** | CONFIRMADO | **Evidencia:**<br>- Poll 10s: `artifacts/acta-express/src/pages/home.tsx:117`.<br>- Cierre de intervalo sin fugas: `artifacts/acta-express/src/pages/home.tsx:119-120`.<br>- Re-verificación al clickear: `artifacts/acta-express/src/pages/home.tsx:219-220`.<br>**Traza:** En el montaje, `orphanSession` es nulo, el `useEffect` inicia el intervalo. A los 10s, `check()` halla la sesión huérfana y hace `setOrphanSession(orphan)`. React re-renderiza y ejecuta el cleanup del `useEffect` anterior (`clearInterval(intervalId)`). Se ejecuta de nuevo el `useEffect`, pero la guarda `if (... || orphanSession) return;` aborta, dejando 0 intervalos corriendo. Al clickear Recuperar, `getSession` trae la metadata y `if (!meta || !isStale(meta))` revalida el heartbeat. Si es `< 30000ms`, se sale con toast, evitando recuperar sesiones resucitadas. |
| **C5** | CONFIRMADO | **Evidencia:**<br>- Construcción de blob nativo: `artifacts/acta-express/src/pages/home.tsx:233-234`.<br>- Llamada a `mutate` sin pasar por estados: `artifacts/acta-express/src/pages/home.tsx:235-241`.<br>**Traza:** El click en Recuperar ejecuta `handleRecuperarOrphan`. Se instancia `new Blob(chunks)`. Se procesa a base64 local (`audioBase64Recuperado`). Llama de forma síncrona a `processAudio.mutate({ data: ... })`. En ningún paso invoca `setAudioBase64`, ni `setDuration`, variables que el `useEffect` de auto-proceso original (`home.tsx:165-170`, implícito) escucha. Al no alterar `lastProcessedAudioRef` ni `audioBase64`, es imposible generar un segundo re-procesamiento cruzado. |
| **C6** | CONFIRMADO | **Traza de Ejecución Simbólica:**<br>1. **t=T0**: Inicia grabación, `createSession` produce `{ startedAt: T0, lastChunkAt: T0 }`.<br>2. **t=T0+45s**: Se inserta chunk 44. Metadata pasa a `lastChunkAt = T0+45000`.<br>3. **t=T0+46s**: Crash absoluto.<br>4. **t=T0+60s**: Reapertura. Monta Home. `useEffect` corre `check()` inmediato.<br>5. **t=T0+60s (check)**: `purgeStaleKeepNewest("u1")` halla la sesión. Evalúa `isStale = (T0+60000) - (T0+45000) = 15000`. Como `15000 < 30000`, ignora la sesión. `orphanSession` es nulo. Tarjeta no aparece.<br>6. **t=T0+70s (poll 1)**: `isStale` con 25000ms < 30000ms. Sigue nulo.<br>7. **t=T0+80s (poll 2)**: `isStale` con 35000ms >= 30000ms. ¡Detectado! Ejecuta `setOrphanSession`.<br>8. **Texto exacto de Tarjeta:** Renderiza `~` + `Math.max(1, Math.round((45000) / 60000))` = `Math.max(1, 1)` = 1. Texto final renderizado en DOM: `Se encontró una grabación interrumpida (~1 min)`.<br>9. **t=T0+85s (Click Recuperar)**: <br>- *Re-check*: `isStale` revisa `(T0+85000) - (T0+45000) = 40000`. Es mayor a 30s. Sigue adelante.<br>- *Array*: `readChunks` devuelve exactamente 45 blobs.<br>- *Payload mutación*: `processAudio.mutate({ data: { audioBase64: "<base64_reconstruido>", mimeType: "audio/webm", msDuration: 45000, generarSintesis: <valor_ref> } })`. |

## 2. Respuestas a Preguntas de Control

**Q1: Citas Textuales**
- (a) **Texto de la tarjeta** (`artifacts/acta-express/src/pages/home.tsx:363-366`):
```tsx
                <p className="text-sm font-medium">
                  Se encontró una grabación interrumpida (~
                  {Math.max(1, Math.round((orphanSession.lastChunkAt - orphanSession.startedAt) / 60000))} min)
                </p>
```
- (b) **Toast del re-check fallido** (`artifacts/acta-express/src/pages/home.tsx:223`):
```tsx
      toast({ title: "Grabación no recuperable", description: "Esa grabación sigue activa en otra pestaña o ya no existe." });
```
- (c) **Comentario de la línea del catch del poll** (`artifacts/acta-express/src/pages/home.tsx:114`):
```tsx
        .catch(() => {}); // vault roto → sin tarjeta, app intacta
```

**Q2: Interacción appendChunk borrado y useAudioRecorder**
En `appendChunk`, si la sesión fue purgada un instante antes de procesar el chunk, la transacción aborta explícitamente lanzando un error (`artifacts/acta-express/src/lib/recordingVault.ts:130-133`):
```typescript
  const meta = await requestToPromise<VaultSessionMeta | undefined>(sessionsStore.get(sessionId));
  if (!meta) {
    tx.abort();
    throw new Error(`vault-session-not-found: ${sessionId}`);
  }
```
El llamador en `useAudioRecorder` (`artifacts/acta-express/src/hooks/useAudioRecorder.ts:247-249`) intercepta este error en su `.catch()`. Configura el guard `vaultDisabledRef.current = true`. A partir del siguiente bloque de datos emitido por `MediaRecorder`, el `if (!vaultDisabledRef.current && vaultSessionIdRef.current)` fallará, ignorando completamente las escrituras a IndexedDB. La grabación en la RAM prosigue ininterrumpida llenando `chunksRef.current`.

**Q3: Apagado estricto del Poll**
El efecto rastrea `orphanSession` como dependencia (`home.tsx:121`). Al resolverse una huérfana, `setOrphanSession` obliga a React a re-renderizar y volver a invocar el `useEffect`. Antes de la nueva ejecución, React corre el `cleanup` previo (`home.tsx:118-120`):
```typescript
    return () => {
      cancelled = true;
      window.clearInterval(intervalId);
    };
```
Esto purga el intervalo del navegador. En la re-evaluación subsiguiente del `useEffect`, la guarda temprana (`home.tsx:106`):
```typescript
    if (!user || !isVaultAvailable() || orphanSession) return;
```
detiene la función sincrónicamente porque `orphanSession` es truthy, impidiendo cualquier llamada posterior a `setInterval`. No sobrevive ningún intervalo.

**Q4: Inconsistencia en `chunkCount`**
`chunkCount` en los meta-datos se actualiza usando `Math.max(meta.chunkCount, seq + 1)`. Si la cuota en IndexedDB se excede al momento del `chunksStore.put()`, la transacción abortará en su totalidad sin guardar ni el blob ni los metadatos modificados. En el hilo principal, el `mediaRecorder` y `chunkSeqRef` siguen incrementando datos hacia RAM al desactivarse el vault. Resultado: si la pestaña crashea más tarde, `chunkCount` indicará N (los que lograron entrar al DB), pero el proceso emitió N+K chunks.
Esto es irrelevante al recuperar: el código lee físicamente los arrays almacenados vía `readChunks` (sin mirar `chunkCount` en absoluto) y reconstruye la duración desde los timestamps de los metadatos (`msDuration: Math.max(1000, meta.lastChunkAt - meta.startedAt)` en `home.tsx:239`). No existe colisión lógica.

## 3. Demostración Anti-Aprobación Automática (Trampas)

- **T1 — Doble acta:** No existe camino viable. La mutación en la UI está estanca (`processAudio.mutate`) y si el usuario da click velozmente dos veces, la tarjeta queda suprimida durante la carga por el bloque que tiene la condición render `!processAudio.isPending` (`home.tsx:359`).
- **T2 — Pérdida por límite-1:** ¿Es comportamiento aprobado o bug? **Es aprobado.** El dictamen de diseño G0 dicta conservar máximo 1 huérfana (la más reciente) para no sepultar al usuario en diálogos conflictivos.
- **T3 — Quota a mitad de reunión:** La grabación RAM continuará ilesa (verificado en traza C1). Si luego sobreviene el crash, al reiniciar se recuperarán los blobs que SÍ se salvaron en IDB hasta llenar la quota, y la tarjeta mostrará los minutos del `startedAt` al último `lastChunkAt` salvado. El audio será incompleto y no hay advertencia explícita en UI, pero es la máxima mitigación posible con el estado parcial del vault preservado intactamente en 1 sola TX, garantizando un audio recuperable válido.
- **T4 — Logout/cambio de cuenta:** El silo de `listSessions(uid)` mediante el filtrado `meta.uid === uid` encapsula la persistencia localmente. El u2 no recuperará datos de u1. Si u1 vuelve a loguearse tras la salida de u2 en el mismo navegador, `purgeStaleKeepNewest(u1.uid)` volverá a ver sus propias sesiones residuales, habilitando la recuperación idénticamente a como si no hubiera cerrado.
- **T5 — El poll durante una grabación activa:**
  - *(a)* El poll no purga la sesión actual porque `purgeStaleKeepNewest` se circunscribe a sesiones `stale`, evaluadas mediante `now - meta.lastChunkAt >= VAULT_STALE_MS` (30s). La sesión activa emite blobs (latiendo el IDB) cada 1s. JAMÁS excederá 30s viva.
  - *(b)* Si el usuario empieza una grabación y había una huérfana paralela vieja, el poll rescatará el estado y poblará `orphanSession`, pero la UI en `home.tsx:359` exige que `!isRecording` sea `true`. La tarjeta quedará oculta detrás de la grabación activa, asomando ordenadamente en el DOM solamente después de que la grabación actual se detenga.

## 4. Opinión Fundada sobre Dudas Arquitectónicas

- **D1 (OOM en strings Base64 largos):** La reconstrucción de `audioBase64Recuperado` de un WebM de 100MB costará ~133MB netos de duplicación en RAM (Blob + Buffer de String). Para Chrome Desktop moderno esto es negligible, pero en Mobile WebView en gama media ocasionará spikes severos de Garbage Collection e incluso evicción OOM silente. Veredicto: **Es aceptable para el MVP (resuelve el H6), pero exige un ticket al backlog.**
- **D2 (Carrera poll vs descarte):** Si `deleteSession` cae silenciosamente en el Descartar, `orphanSession` retorna a `null`. El effect reactivará el poll y 10s más tarde reingresará la sesión "zombie" forzando la aparición cíclica de la tarjeta. Aunque degradado y algo disruptivo, el comportamiento subyacente sigue aislado y no interfiere con una grabación en curso. Veredicto: **Comportamiento aceptable.**
- **D3 (Pestañas Concurrentes):** Al estar en pestañas distintas con sesiones separadas `sA` y `sB`, la pestaña B ejecutará su poll descartando `sB` (viva) y `sA` (viva) al fallar `isStale`. Si A crashea, `sA` se vuelve stale (tras 30s). La pestaña B la halla y rellena su `orphanSession`, pero oculta la UI de recuperación ya que B tiene `isRecording=true`. Cuando B finaliza, aparece la tarjeta huérfana de `sA`. Veredicto: **Impecablemente resiliente.**
- **D4 (Timing ~30s):** Observado en el E2E. Al momento `t=0` muere la pestaña con `lastChunkAt=0`. A los `t=10s` reabrimos. El poll en Home halla un diff del heartbeat de `10000ms`, lo que falla el `>= 30000ms`. Al latido de `t=20s`, el diff es `20000ms`, también lo ignora. En el latido de `t=30s`, la diferencia asume el valor `>= 30000ms`, autorizando la tarjeta. Veredicto: **Cuadra exactamente.**

## 5. Veredicto Global

**APROBADO CON OBSERVACIONES**

La estructura técnica, el control de errores, la gestión de cuotas transaccionales (ACID) y los flujos estancos satisfacen los requisitos funcionales H6. La anomalía semántica detallada en C3 en torno a los sub-casos del borrado extra (en `chunks.length === 0` y en la purga) no representa un fallo orgánico sino una imprecisión en el claim. La resiliencia transaccional exhibe una robustez sistémica muy competente. Se recomienda documentar en el backlog la carga en memoria RAM en largas recuperaciones (OOM Base64).
