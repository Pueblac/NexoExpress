# Paquete de Especificación — MT-04b: Toggle "Análisis profundo" + envío del flag

**Ciclo:** 2026-07-09_mt04_toggle_sintesis · **Fase:** F4 (implementación según spec)
**Rol destinatario:** Ingeniero (Claude Sonnet) — sesión nueva, working tree limpio
**Prerrequisito:** MT-04a cerrada (clientes regenerados con `generarSintesis` y verificados en F5). NO empieces si `grep -rn "generarSintesis" lib/api-client-react/src/generated/` devuelve 0 resultados.
**Diseño aprobado:** rondas 1 y 2 del expediente (Gemini 3.1 Pro High). Esta spec es vinculante — no rediseñes ni "mejores" el parche: cada línea del guard fue auditada.

## 1. Objetivo

En **ActaExpressWeb** (`/home/pueblac/AndroidStudioProjects/ActaExpressWeb`), añadir a la pantalla de grabación un toggle persistente "Análisis profundo" que haga que el POST `/actas/process` incluya `generarSintesis` (boolean explícito), blindando además el efecto de disparo contra dobles envíos.

## 2. Contexto mínimo verificado (09-07-2026)

**Único archivo a modificar:** `artifacts/acta-express/src/pages/home.tsx` (319 líneas hoy).

- Imports actuales relevantes (línea 4): `useListActas, useProcessAudio, useDeleteActa, getListActasQueryKey` desde `@workspace/api-client-react`. El componente usa `const { user } = useAuth();` (línea 37) — `user?.uid` disponible.
- Efecto de disparo actual (líneas 100-110), literal:
  ```tsx
  useEffect(() => {
      if (audioBase64 && !isRecording && duration > 0) {
        processAudio.mutate({
          data: {
            audioBase64,
            mimeType: "audio/webm",
            msDuration: duration
          }
        });
      }
    }, [audioBase64, isRecording, duration]); // eslint-disable-line react-hooks/exhaustive-deps
  ```
- `onSuccess` del mutation (líneas 53-77): muestra toast "¡Acta generada! / Tu reunión ha sido procesada con éxito." (o el aviso destructivo de audio silencioso). En React Query v5, `onSuccess(data, variables, ...)` recibe las variables del mutate → `variables.data.generarSintesis` disponible.
- Zona de UI donde va el toggle: dentro del `<div className="space-y-2">` que contiene el contador y el mensaje de estado (líneas 170-204), DESPUÉS del bloque `<AnimatePresence>` del badge de captura y ANTES del bloque de `error`.
- Componentes disponibles (shadcn, ya en el repo): `src/components/ui/switch.tsx`, `src/components/ui/label.tsx`.
- Comportamiento del hook de grabación (NO lo toques): `startRecording` resetea `audioBase64` a `null` y `duration` a `0`; al parar, `onstop` repuebla `audioBase64`. El flujo soporta N grabaciones por carga de página.

## 3. Contrato (implementación EXACTA)

1. **Estado + persistencia por usuario:**
   - Clave: `` `actaexpress:generarSintesis:${user.uid}` `` en `localStorage` (valores `"true"`/`"false"`).
   - Estado `generarSintesis: boolean` inicializado desde la clave (default `false` si no existe o si no hay `user`).
   - Al cambiar el switch: actualizar estado y escribir la clave. Si `user` es null: mantener default `false` y NO persistir.
2. **Ref sincronizado (diseño C3):**
   ```tsx
   const generarSintesisRef = useRef(generarSintesis);
   generarSintesisRef.current = generarSintesis;
   ```
3. **Efecto blindado (diseño C7, APROBADO LITERALMENTE — replicar tal cual):**
   ```tsx
   const lastProcessedAudioRef = useRef<string | null>(null);

   useEffect(() => {
       if (
         audioBase64 && !isRecording && duration > 0 &&
         !processAudio.isPending &&
         lastProcessedAudioRef.current !== audioBase64
       ) {
         lastProcessedAudioRef.current = audioBase64;
         processAudio.mutate({
           data: {
             audioBase64,
             mimeType: "audio/webm",
             msDuration: duration,
             generarSintesis: generarSintesisRef.current
           }
         });
       }
     }, [audioBase64, isRecording, duration]); // eslint-disable-line react-hooks/exhaustive-deps
   ```
   Boolean **explícito siempre** (true y false). La marca se asigna ANTES del mutate y **NO se limpia en `onError`** (decisión Q6: ante error, el usuario regraba; `startRecording` resetea el estado).
4. **UI del toggle:** `Switch` + `Label` en la zona indicada (§2), etiqueta **"Análisis profundo"** con subtítulo **"Transcripción completa y análisis (tarda más)"** en `text-xs text-muted-foreground`; `data-testid="switch-sintesis"`; `disabled={isRecording || processAudio.isPending}`; sin layout shift (elemento siempre presente, no condicional).
5. **Toast extendido:** en `onSuccess`, si `variables.data.generarSintesis === true` (y no es el caso de audio silencioso), la descripción del toast pasa a: `"Tu reunión ha sido procesada con éxito. El análisis profundo se está generando en segundo plano."`.

## 4. Restricciones

- SOLO `home.tsx` (+ imports de componentes ya existentes). PROHIBIDO tocar `useAudioRecorder.ts`, archivos `generated/`, `openapi.yaml`, backend, dependencias.
- PROHIBIDO usar `as any` o casts para el campo (si el tipo no lo acepta, MT-04a no está cerrada → DETENTE y repórtalo).
- PROHIBIDO usar `processAudio.isSuccess` en el guard (bug confirmado B1 del expediente: bloquea toda grabación posterior a la primera).
- NO toques credenciales ni Firestore; NO hagas commit.

## 5. DoD ejecutable (corre TODOS y copia la salida literal al informe)

```bash
cd /home/pueblac/AndroidStudioProjects/ActaExpressWeb
git status --short          # 1) ANTES: limpio (solo lo de MT-04a si aún no se commiteó — decláralo)
pnpm run typecheck          # 2) exit 0
grep -n "isSuccess" artifacts/acta-express/src/pages/home.tsx        # 3) 0 resultados en el guard
grep -n "lastProcessedAudioRef\|generarSintesisRef\|switch-sintesis" artifacts/acta-express/src/pages/home.tsx   # 4) presentes
```
5) Si tu entorno permite levantar la app (`./dev.sh` o el flujo del repo) y abrirla: verifica render real del switch y su persistencia tras reload, y decláralo con lo observado. **Si tu entorno NO permite navegador/micrófono, decláralo como NO EJECUTADO — no es desviación:** la verificación E2E completa (POST real con flag → `sintesis/{actaId}` en Firestore) la ejecuta el Arquitecto con el Director en F5.

## 6. Protocolo de dudas

Ambigüedad → **DETENTE** y devuélvela en el informe (reabre F3). Implementar sobre un supuesto no declarado invalida la entrega.

## 7. Informe de Implementación (`informe_mt04b.md`, UN documento markdown listo para archivar)

1) Qué se hizo. 2) **Diff literal** (`git diff` + `git status`, íntegros). 3) Evidencia literal del DoD. 4) Desviaciones (o "ninguna"). 5) Tus dudas. 6) Estado commiteable. 7) AVISO actualizado.

━━ AVISO DE TRASPASO ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CICLO      : 2026-07-09_mt04_toggle_sintesis
FASE       : F3 → F4 — spec MT-04b (NO entregar hasta cerrar F5 de MT-04a)
TURNO DE   : Ingeniero (Claude Sonnet)
ENTREGAR   : este documento (spec_mt04b.md)
ADJUNTOS   : Ninguno (repo local es el material de trabajo)
DESTINO    : Sesión NUEVA de Claude Sonnet sobre el repo ActaExpressWeb —
             inicialización de identidad primero: "Rol: Ingeniero del ciclo
             2026-07-09_mt04_toggle_sintesis, metodología v2 del ecosistema
             Express. Confirma recepción sin accionar; acepta únicamente
             artefactos cuyo TURNO DE diga Ingeniero."
ACCIÓN     : Implementar EXACTAMENTE esta spec y producir el informe
VUELVE A   : Arquitecto, con el informe archivado como
             auditorias/2026-07-09_mt04_toggle_sintesis/informe_mt04b.md
             → F5 (verificación ejecutando el DoD + E2E)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
