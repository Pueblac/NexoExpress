# Informe de Implementación — MT-C4 (rotación asistida, Sonnet)

## 1. Qué se hizo
**`home.tsx` (único tocado por C4):** eliminado `void micSilent;` (ya se consume). Bloque nuevo `{isRecording && micSilent && (...)}` con `data-testid="banner-mic-muerto"`, insertado entre el `AnimatePresence` del badge `captureMode` y el selector. Un solo bloque con ternario sobre `modoReunion`: presencial → `text-destructive`/`bg-destructive/10` + texto "⚠️ No se detecta señal de tu micrófono — revisa que no esté silenciado en el sistema."; virtual → `text-amber-500`/`bg-amber-500/10` + texto "Tu micrófono no aporta señal. Si solo escuchas la reunión está bien; si querías hablar, revisa que no esté silenciado." Icono `AlertCircle`. Sin `stopRecording` ni setState (presentacional).

## 2. Diff literal íntegro (delta MT-C4 sobre home.tsx)
```diff
-  const { micSilent } = useMicLevel(micStream, isRecording, modoReunion);
-  void micSilent;
+  const { micSilent } = useMicLevel(micStream, isRecording, modoReunion);
...
+            {isRecording && micSilent && (
+              <div
+                data-testid="banner-mic-muerto"
+                className={
+                  modoReunion === "presencial"
+                    ? "flex items-center justify-center gap-2 text-destructive text-sm mt-2 bg-destructive/10 px-4 py-2 rounded-md"
+                    : "flex items-center justify-center gap-2 text-amber-500 text-sm mt-2 bg-amber-500/10 px-4 py-2 rounded-md"
+                }
+              >
+                <AlertCircle className="w-4 h-4" />
+                {modoReunion === "presencial"
+                  ? "⚠️ No se detecta señal de tu micrófono — revisa que no esté silenciado en el sistema."
+                  : "Tu micrófono no aporta señal. Si solo escuchas la reunión está bien; si querías hablar, revisa que no esté silenciado."}
+              </div>
+            )}
```
`git status`: useAudioRecorder.ts (M, C2), home.tsx (M, C1-C4), useMicLevel.ts (untracked, C3). Sin commit.

## 3. Evidencia literal del DoD
1. `pnpm run typecheck` → 4 proyectos Done, **EXIT_CODE=0**.
2. grep `banner-mic-muerto|micSilent|No se detecta señal|no aporta señal` → hook (86), condición `isRecording && micSilent` (248), testid (250), ambos textos (259, 260).
3. Confirmado por lectura: bloque dentro de `isRecording && micSilent`; className y texto bifurcados por `modoReunion`; icono AlertCircle; sin stopRecording/setState.
4. `git diff --stat` → useAudioRecorder.ts + home.tsx; useMicLevel.ts untracked. Delta MT-C4 solo en home.tsx.
5. Nota E2E Director: mic muteado presencial → banner rojo ≤5s; virtual → ámbar ≤10s; recuperar señal → desaparece.

## 4. Desviaciones
Ninguna. Banner en la columna central; `mt-2` bastó, sin margen extra.

## 5. Dudas del Ingeniero
Ninguna. (Observación menor del Arquitecto: el comentario "// MT-C3: solo cablea..." quedó obsoleto sobre la línea del hook; cosmético, sin efecto — se limpia en cualquier MT posterior o queda sin consecuencia.)

## 6. Estado commiteable
Verde. typecheck exit 0; solo home.tsx tocado por C4; sin commit. Listo para MT-C5.
