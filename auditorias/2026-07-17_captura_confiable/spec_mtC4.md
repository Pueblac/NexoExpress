# Spec MT-C4 — Banner de micrófono muerto (aviso H4)

**Ciclo:** 2026-07-17_captura_confiable · F4 · **Rol:** Ingeniero (Sonnet, rotación asistida)
**Diseño aprobado:** r1 + G1. Cambio 3 (severidad por modo: rojo presencial / pasivo virtual). El aviso SOLO avisa, nunca corta (decisión G0). Vinculante.
**Repo:** `/home/pueblac/AndroidStudioProjects/ActaExpressWeb`. Arranca sobre el working tree con **MT-C1..C3 aplicadas** (existe `micSilent` disponible vía `useMicLevel`). Toca SOLO lo de su contrato.

## Objetivo
Pintar en `home.tsx`, durante la grabación, un banner que avise cuando `micSilent` es true: **rojo destructivo en presencial**, **ámbar pasivo en virtual** (silencio legítimo). Aparece solo con `isRecording && micSilent`, desaparece solo al detectar señal. Nunca detiene la grabación.

## Contexto mínimo verificado
- Tras MT-C1..C3: `home.tsx` tiene `modoReunion` (estado) y consume `useMicLevel(micStream, isRecording, modoReunion)` → `micSilent`. Confirma cómo quedó cableado por MT-C3 y reutilízalo (no dupliques la invocación del hook).
- `home.tsx:201-209` — zona bajo el estado ("Grabando..." / "Procesando...") donde vive `text-espera`. El banner del mic va en esta columna central, visible durante la grabación.
- El proyecto ya usa el patrón de aviso destructivo: `home.tsx:248-253` (bloque `error`) con `bg-destructive/10`, `text-destructive`, icono `AlertCircle` (ya importado de lucide). Para el ámbar usa utilidades Tailwind existentes (`text-amber-500`, `bg-amber-500/10`) — sin añadir config.

## Contrato
1. Bloque nuevo condicionado a `isRecording && micSilent`, con `data-testid="banner-mic-muerto"`:
   - **presencial** (`modoReunion === "presencial"`): estilo destructivo (rojo), icono `AlertCircle`, texto: **"⚠️ No se detecta señal de tu micrófono — revisa que no esté silenciado en el sistema."**
   - **virtual** (`modoReunion === "virtual"`): estilo pasivo (ámbar/gris suave, sin fondo rojo), mismo icono en tono ámbar, texto: **"Tu micrófono no aporta señal. Si solo escuchas la reunión está bien; si querías hablar, revisa que no esté silenciado."**
2. Un solo bloque que elige clases/texto según `modoReunion` (ternario), NO dos bloques duplicados. Colócalo de forma que conviva con el badge de `captureMode` y con `text-espera` sin romper el layout (el banner es de grabación; `text-espera` es de procesamiento — no coinciden en el tiempo porque `isRecording` y `isPending` son mutuamente excluyentes).
3. El banner NO llama a `stopRecording` ni cambia ningún estado — es puramente presentacional.

## Restricciones
Solo `home.tsx`. NO tocar `useMicLevel.ts` ni `useAudioRecorder.ts`. NO detener la grabación. Sin dependencias nuevas. No commit.

## DoD (salida literal al informe)
1. `pnpm run typecheck` → exit 0.
2. `grep -n "banner-mic-muerto\|micSilent\|No se detecta señal\|no aporta señal" artifacts/acta-express/src/pages/home.tsx` → el bloque, la condición y AMBOS textos.
3. Confirma por lectura del diff: el banner está dentro de `isRecording && micSilent` y el estilo se bifurca por `modoReunion`. Cita las líneas.
4. `git diff --stat` → SOLO `home.tsx`.
5. Nota para el E2E del Director (no ejecutable aquí): mic muteado en presencial → banner rojo en ≤5 s; en virtual → aviso ámbar en ≤10 s; desmutear → desaparece.

## Protocolo de dudas
Si el layout hace que el banner empuje el badge/toggle de forma fea, resuélvelo con el mínimo estilo (margen), y **declara** cualquier decisión visual. La severidad por modo (cambio 3) y la regla "solo avisa, nunca corta" (G0) NO son negociables.

## Informe: formato estándar (qué se hizo / diff literal íntegro / evidencia DoD literal / desviaciones / dudas / estado commiteable).
