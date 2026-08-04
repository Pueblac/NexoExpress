# Prompt de auditoría de CÓDIGO — ronda 2 (ciclo 2026-07-30_selector_microfono)

**Generado por:** Arquitecto (Fable 5) · 04-08-2026
**Transporta:** el Director, a conversación NUEVA de Gemini 3.1 Pro High
**Alcance:** SOLO los fixes de la ronda 1 (BUG 1 y BUG 2 confirmados) + el fix del ícono ya auditado en r1. Diff del working tree sobre `6854bc5`, incrustado ÍNTEGRO abajo.

---

## MENSAJE 1 — inicialización de identidad (pegar primero, esperar confirmación)

> Rol: Auditor externo del ciclo 2026-07-30_selector_microfono, metodología v2 del ecosistema Express, ronda 2 (verificación de fixes). Confirma recepción sin accionar; acepta únicamente artefactos cuyo campo TURNO DE diga Auditor.

---

## MENSAJE 2 — prompt de auditoría (pegar tras la confirmación)

Eres el Auditor externo, ronda 2. En la ronda 1 emitiste APROBADO CON OBSERVACIONES con 3 BUGs; el anti-bluff del Arquitecto confirmó 2 y refutó 1:

- **BUG 1 CONFIRMADO (Media-Alta):** fuga de AudioContext en el camino de fallo del enrutamiento presencial (el `close()` solo existía en la rama no-running).
- **BUG 2 CONFIRMADO (Baja/UX):** modal del selector huérfano mostrando "No se encontraron micrófonos" cuando el banner se apaga con el modal abierto.
- **BUG 3 REFUTADO con evidencia:** `useMicLevel.ts:32-35` — `if (!active || !micStream) { setMicSilent(false); return; }`: con `micStream null` (virtual sin mic, captureMode "system") jamás hay `micSilent`, el banner no se monta y el CTA es inalcanzable; tu premisa "el nivel de audio evaluará a silencio" era falsa (el archivo no venía en el diff de r1 y no se tocó en este ciclo). Si disientes, cita el mecanismo que produce `micSilent=true` con `micStream null`.

Audita AHORA únicamente el diff de fixes incrustado abajo (regla del contrato: sin diff estructurado → "INVÁLIDO"):

### CLAIMS de la ronda 2

- **CF-A — Fix del BUG 1:** el ctx de enrutamiento ahora vive en `routingCtx` (visible por el catch) y el catch hace `routingCtx?.close().catch(() => {})`. Verifica: (1) ningún camino de fallo deja un AudioContext `running` sin cerrar; (2) el camino exitoso (routed) NO cierra el ctx; (3) la rama no-running conserva su close original; (4) el renombre `audioCtx`→`routingCtx` no altera ninguna otra semántica (refs, attachStateWatch, dest.stream).
- **CF-B — Fix del BUG 2:** nuevo `useEffect` en home.tsx: `if (!(isRecording && micSilent)) setMicSelectorOpen(false)` con deps `[isRecording, micSilent]`. Verifica: (1) cierra el modal huérfano en cuanto el banner deja de aplicar (señal recuperada o grabación detenida); (2) NO impide abrir el modal mientras el banner está activo (el CTA solo existe con `isRecording && micSilent` true); (3) no interfiere con el cierre por swap exitoso ni con el flujo del cerrojo; (4) sin bucles de render (el efecto solo hace set cuando el estado cambiaría).
- **CF-C — Fix del ícono (ya auditado en r1 como DIFF 2, sin observaciones):** confirma que sigue siendo el único cambio en esa zona (`!h-16 !w-16`).

### Trampa dirigida única

- **TF-1:** ¿introduce el `useEffect` de CF-B alguna carrera con `handleSwapMic` (que también hace `setMicSelectorOpen(false)` en éxito) o con el gating de `useMicDevices`? ¿Puede el modal cerrarse ANTES de que el usuario alcance a hacer un swap legítimo (p. ej. un pico de ruido espurio apaga el banner a mitad de la elección)? Si sí, ¿es un comportamiento aceptable dado que el banner (y el problema) desaparecieron, o es un bug?

### Formato del veredicto

`APROBADO | APROBADO CON OBSERVACIONES | RECHAZADO` + BUGs con archivo:línea + traza + severidad. Cero elogios; hallazgos o silencio.

---

## DIFF — working tree sobre `6854bc5` (fix ícono + Fix A + Fix B) ÍNTEGRO

```diff
diff --git a/artifacts/acta-express/src/hooks/useAudioRecorder.ts b/artifacts/acta-express/src/hooks/useAudioRecorder.ts
index b4c1e40..da08b03 100644
--- a/artifacts/acta-express/src/hooks/useAudioRecorder.ts
+++ b/artifacts/acta-express/src/hooks/useAudioRecorder.ts
@@ -232,26 +232,28 @@ export function useAudioRecorder(): UseAudioRecorderReturn {
       }
 
       let routed = false;
+      let routingCtx: AudioContext | null = null;
       try {
-        const audioCtx = new AudioContext();
-        if (audioCtx.state === "suspended") {
-          await audioCtx.resume().catch(() => {});
+        routingCtx = new AudioContext();
+        if (routingCtx.state === "suspended") {
+          await routingCtx.resume().catch(() => {});
         }
-        if (audioCtx.state === "running") {
-          const dest = audioCtx.createMediaStreamDestination();
-          const source = audioCtx.createMediaStreamSource(micRaw);
+        if (routingCtx.state === "running") {
+          const dest = routingCtx.createMediaStreamDestination();
+          const source = routingCtx.createMediaStreamSource(micRaw);
           source.connect(dest);
-          audioCtxRef.current = audioCtx;
+          audioCtxRef.current = routingCtx;
           destRef.current = dest;
           micSourceRef.current = source;
-          attachStateWatch(audioCtx);
+          attachStateWatch(routingCtx);
           recordingStream = dest.stream;
           routed = true;
         } else {
-          audioCtx.close().catch(() => {});
+          routingCtx.close().catch(() => {});
         }
       } catch {
-        /* enrutamiento fallido */
+        // Fix F6-BUG1: si la topología falla con el ctx ya running, no dejarlo huérfano.
+        routingCtx?.close().catch(() => {});
       }
       if (!routed) {
         // FALLBACK DECLARADO (T1 arranque): grabar el stream crudo directo, como hoy.
diff --git a/artifacts/acta-express/src/pages/home.tsx b/artifacts/acta-express/src/pages/home.tsx
index 0c4f884..39b23e8 100644
--- a/artifacts/acta-express/src/pages/home.tsx
+++ b/artifacts/acta-express/src/pages/home.tsx
@@ -121,6 +121,14 @@ export default function Home() {
 
   const [micSelectorOpen, setMicSelectorOpen] = useState(false);
 
+  // Fix F6-BUG2: si el banner se apaga (volvió la señal o paró la grabación),
+  // el modal quedaría huérfano con la lista vacía — se cierra solo.
+  useEffect(() => {
+    if (!(isRecording && micSilent)) {
+      setMicSelectorOpen(false);
+    }
+  }, [isRecording, micSilent]);
+
   // H6c+H6e: detección de sesión huérfana — al montar y re-chequeo periódico
   // (la sesión del crash tarda VAULT_STALE_MS en volverse stale; sin poll, la
   // tarjeta solo aparecía al remontar Home — bug del E2E 27-07).
@@ -324,7 +332,7 @@ export default function Home() {
                 ) : isRecording ? (
                   <Square className="h-10 w-10 text-white fill-current" />
                 ) : (
-                  <Mic className="h-16 w-16 text-white" />
+                  <Mic className="!h-16 !w-16 text-white" />
                 )}
               </Button>
             </div>
```

---

```
━━ AVISO DE TRASPASO ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CICLO      : 2026-07-30_selector_microfono
FASE       : F6 — AUDITORÍA de código, ronda 2 (fixes)
TURNO DE   : Auditor
ENTREGAR   : este archivo completo (MENSAJE 1, luego MENSAJE 2 con el diff)
ADJUNTOS   : Ninguno (el diff viaja incrustado)
DESTINO    : conversación NUEVA de Gemini 3.1 Pro High
ACCIÓN     : auditar CF-A..CF-C + TF-1 y emitir veredicto
VUELVE A   : Arquitecto, archivando la respuesta literal como
             respuesta_auditoria_ronda2.md (anti-bluff antes de aceptar)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
