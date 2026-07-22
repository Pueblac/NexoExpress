# Spec MT-C1 — Selector de tipo de reunión (presencial / virtual)

**Ciclo:** 2026-07-17_captura_confiable · F4 · **Rol:** Ingeniero (Sonnet, rotación asistida)
**Diseño aprobado:** r1 APROBADO CON CAMBIOS + G1 del Director. Default **presencial**. Vinculante, no rediseñar.
**Repo:** `/home/pueblac/AndroidStudioProjects/ActaExpressWeb` (working tree limpio al iniciar). Esta es la MT-C1 de una tanda de 5 encadenadas; toca SOLO lo de su contrato.

## Objetivo
Añadir a `home.tsx` un selector persistente de tipo de reunión (`"presencial" | "virtual"`, default `"presencial"`), con estado + ref espejo + persistencia por uid, siguiendo EXACTAMENTE el patrón ya auditado del toggle `generarSintesis`. MT-C1 NO cambia todavía cómo graba el hook (eso es MT-C2); solo introduce el estado y la UI del selector.

## Contexto mínimo verificado (código real)
- `home.tsx:55-68` — patrón de persistencia por uid a reutilizar literalmente:
```tsx
const [generarSintesis, setGenerarSintesis] = useState<boolean>(() => {
  if (!user) return false;
  return localStorage.getItem(`actaexpress:generarSintesis:${user.uid}`) === "true";
});
const generarSintesisRef = useRef(generarSintesis);
generarSintesisRef.current = generarSintesis;
const handleGenerarSintesisChange = (checked: boolean) => {
  setGenerarSintesis(checked);
  if (user) localStorage.setItem(`actaexpress:generarSintesis:${user.uid}`, String(checked));
};
```
- `home.tsx:230-246` — el bloque del `Switch` "Análisis profundo" (justo debajo del badge `captureMode`). El selector nuevo va ENCIMA del botón de grabar o junto al toggle, en la misma columna centrada.
- `home.tsx:44-51` — el hook se desestructura aquí (`startRecording` incluido). **NO cambiar la llamada `onClick` todavía** (MT-C2 lo hará).
- El proyecto usa componentes shadcn en `@/components/ui/`. Existe `@/components/ui/label`. Para el selector, usar **`RadioGroup` + `RadioGroupItem`** de `@/components/ui/radio-group` si existe; si NO existe ese archivo, usar dos `<button>` con estilo segmentado y `role="radiogroup"`/`role="radio"` + `aria-checked` (accesibilidad exigida por el diseño D2). Verifica con `ls artifacts/acta-express/src/components/ui/radio-group.tsx` antes de decidir; declara en el informe cuál vía usaste.

## Contrato
1. Tipo `type ModoReunion = "presencial" | "virtual";` (decláralo en `home.tsx`, arriba del componente; MT-C2 lo importará/moverá si hace falta — por ahora local a home.tsx).
2. Estado + ref + handler, calcados del patrón anterior, clave `actaexpress:modoReunion:${user.uid}`, default `"presencial"`:
```tsx
const [modoReunion, setModoReunion] = useState<ModoReunion>(() => {
  if (!user) return "presencial";
  const saved = localStorage.getItem(`actaexpress:modoReunion:${user.uid}`);
  return saved === "virtual" ? "virtual" : "presencial";
});
const modoReunionRef = useRef(modoReunion);
modoReunionRef.current = modoReunion;
const handleModoReunionChange = (modo: ModoReunion) => {
  setModoReunion(modo);
  if (user) localStorage.setItem(`actaexpress:modoReunion:${user.uid}`, modo);
};
```
3. UI del selector en la columna central del recorder (cerca del toggle de síntesis), con dos opciones:
   - **"Reunión presencial"** con subtítulo "Sonido ambiente (micrófono directo)".
   - **"Reunión virtual"** con subtítulo "Audio de la pestaña + micrófono".
   `data-testid="selector-modo-reunion"` en el contenedor; cada opción con `data-testid="modo-presencial"` / `data-testid="modo-virtual"`.
4. El selector se deshabilita con `isRecording || processAudio.isPending` (igual que el Switch).

## Restricciones
Solo `home.tsx`. NO tocar `useAudioRecorder.ts`, NO cambiar la firma ni la llamada de `startRecording`, NO tocar el efecto de envío (`home.tsx:121-137`). Sin dependencias nuevas. No commit.

## DoD (salida literal al informe)
1. `pnpm run typecheck` → exit 0 (los 4 proyectos Done).
2. `grep -n "modoReunion\|selector-modo-reunion\|actaexpress:modoReunion" artifacts/acta-express/src/pages/home.tsx` → muestra estado, ref, handler, clave y los testids.
3. `git diff --stat` → SOLO `home.tsx`.
4. Declara qué vía de UI usaste (RadioGroup existente vs segmentado accesible) y por qué.

## Protocolo de dudas
Si algo es ambiguo (p. ej. no existe `radio-group.tsx` y dudas del estilo), NO supongas en silencio: implementa la vía segmentada accesible descrita y **declara la decisión como duda en el informe**. Una duda que altere el contrato reabre F3.

## Informe: formato estándar (qué se hizo / diff literal íntegro `git diff` + `git status` / evidencia DoD literal / desviaciones / dudas / estado commiteable).
