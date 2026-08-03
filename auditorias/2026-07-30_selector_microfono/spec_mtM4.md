# Spec MT-M4 — Micrófono preferido al INICIAR grabación (fallback declarado)

**Ciclo:** 2026-07-30_selector_microfono · F4 · **Rol:** Ingeniero (Sonnet, rotación asistida)
**Diseño aprobado:** r1 + G1 (30-07). Q2 del dictamen VINCULANTE: si el preferido no está disponible → **avisar y MANTENER la clave** (no purgarla: mañana el USB puede volver). Regla de oro: un fallo de preferencia JAMÁS impide grabar.
**Repo:** `/home/pueblac/AndroidStudioProjects/ActaExpressWeb`, rama `linux`. Arranca con **MT-M1+M2+M3 aplicadas** (2 nuevos + `M useAudioRecorder.ts` + `M home.tsx`). Toca SOLO `useAudioRecorder.ts`.

## Contexto mínimo verificado
- Antes del PRIMER permiso, `enumerateDevices()` puede devolver deviceIds vacíos → validar "está en la lista" es imposible pre-permiso. Estrategia congelada: **intentar `{ deviceId: { exact } }` directamente y capturar el fallo** (`OverconstrainedError`/`NotFoundError`) → reintentar SIN deviceId (default) + declarar con `setError`-no… NO: con aviso NO bloqueante (el hook no tiene toast; expone el aviso — ver contrato).
- deviceIds son por máquina (bi-máquina Linux↔Windows): el id persistido en una máquina fallará con `exact` en la otra → ese fallo cae en el mismo camino de fallback declarado (T4 del dictamen).
- MT-M2 ya dejó: `getPreferredMic` importable, presencial enrutado, `mixAudioStreams` ampliado.

## Contrato (solo `useAudioRecorder.ts`)
1. Estado nuevo expuesto: `micFallbackNotice: string | null` (+ en `UseAudioRecorderReturn`). Se resetea a `null` al inicio de cada `startRecording`. Import de `getPreferredMic` desde `../lib/micDevices`.
2. Helper interno:
```ts
const getMicWithPreference = async (baseConstraints: MediaTrackConstraints, uid: string | null): Promise<MediaStream> => {
  const preferred = uid ? getPreferredMic(uid) : null;
  if (preferred) {
    try {
      return await navigator.mediaDevices.getUserMedia({ audio: { ...baseConstraints, deviceId: { exact: preferred } } });
    } catch {
      setMicFallbackNotice("Tu micrófono preferido no está disponible; se usará el predeterminado.");
      // Q2: la clave NO se limpia.
    }
  }
  return navigator.mediaDevices.getUserMedia({ audio: baseConstraints });
};
```
3. Usos: (a) presencial: reemplazar el `getUserMedia` actual por `getMicWithPreference({echoCancellation:false, noiseSuppression:false, autoGainControl:true}, user?.uid ?? null)` — el catch EXTERNO existente (mic denegado → setError + return) se mantiene intacto envolviendo la llamada; (b) virtual: `mixAudioStreams` recibe un nuevo parámetro opcional `preferredMicId: string | null` y aplica la misma estrategia exact→fallback en su `getUserMedia` interno del mic (su try/catch actual de "mic unavailable" se conserva como última capa); `startRecording` le pasa `user ? getPreferredMic(user.uid) : null` y, si `mixAudioStreams` cayó al default por fallo del exact, debe poder saberse: amplía su retorno con `micPreferredFailed: boolean` y en ese caso setea el mismo `micFallbackNotice`.
4. En `home.tsx` NO tocas nada (el toast del aviso es de MT-M5 si hace falta… NO: para mantener la tanda cerrada, expón solo el estado; el consumo visual del notice se hace AQUÍ mismo si es trivial —) **Corrección de alcance:** SÍ puedes añadir en `home.tsx` un `useEffect` mínimo que al cambiar `micFallbackNotice` a no-null dispare `toast({ title: "Micrófono", description: micFallbackNotice })`. Es UNA adición pequeña y cierra el flujo de "declarado" en esta MT; decláralo en el informe.

## Restricciones
`useAudioRecorder.ts` + el `useEffect` mínimo del toast en `home.tsx`. Nada más. Sin dependencias nuevas. No commit.

## DoD (salida literal al informe)
1. `pnpm run typecheck` → exit 0.
2. `grep -n "getMicWithPreference\|micFallbackNotice\|getPreferredMic\|micPreferredFailed" artifacts/acta-express/src/hooks/useAudioRecorder.ts artifacts/acta-express/src/pages/home.tsx`.
3. **A/B razonado** citando líneas: (a) sin preferido → un solo `getUserMedia` con las constraints de siempre (cero cambios de comportamiento); (b) preferido válido → `exact` y SIN notice; (c) preferido inválido (otra máquina/desenchufado) → catch → notice seteado → reintento default → LA GRABACIÓN ARRANCA + toast; la clave persiste (citar ausencia de removeItem); (d) mic denegado del todo → el catch externo original sigue funcionando (setError, no arranca — comportamiento pre-existente intacto).
4. `git diff` de ambos archivos, literal íntegro al informe.

## Protocolo de dudas
La política Q2 (mantener la clave) y la estrategia exact→catch→default son DISEÑO CONGELADO. Dudas de contrato → DETENTE.

## Informe: `informe_mtM4.md` — formato estándar.
