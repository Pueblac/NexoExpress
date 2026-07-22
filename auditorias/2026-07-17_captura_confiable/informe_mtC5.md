# Informe de Implementación — MT-C5 (rotación asistida, Sonnet)

## 1. Qué se hizo
**`home.tsx` (único tocado por C5):** el bloque de estado (`<div>...{getStatusMessage()}</div>` + `<p data-testid="text-espera">` separado) se reemplazó por un condicional único `processAudio.isPending ? (tarjeta) : (estado normal)`:
- **isPending:** `<div data-testid="card-procesando" className="border border-primary/30 bg-primary/10 rounded-xl p-4 flex flex-col items-center gap-2">` con `Loader2 h-5 w-5 animate-spin text-primary` + "Procesando con IA..." (`text-base font-semibold`), y debajo `<p data-testid="text-espera">` con el texto exacto "Esto puede tardar unos minutos — no cierres esta pestaña."
- **else:** bloque original (punto rojo si isRecording + `getStatusMessage()`).
El `<h2>` del timer queda intacto arriba (mínimo cambio, protocolo de dudas). Sin cambios de lógica, sin imports nuevos (Loader2 ya importado).

## 2. Diff literal íntegro (delta MT-C5 sobre home.tsx)
```diff
-            <div className="flex items-center justify-center gap-2 text-muted-foreground">
-              {isRecording && <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />}
-              <p className="font-medium">{getStatusMessage()}</p>
-            </div>
-            {processAudio.isPending && (
-              <p className="text-xs text-muted-foreground" data-testid="text-espera">
-                Esto puede tardar unos minutos — no cierres esta pestaña.
-              </p>
+            {processAudio.isPending ? (
+              <div data-testid="card-procesando" className="border border-primary/30 bg-primary/10 rounded-xl p-4 flex flex-col items-center gap-2">
+                <div className="flex items-center gap-2">
+                  <Loader2 className="h-5 w-5 animate-spin text-primary" />
+                  <p className="text-base font-semibold">Procesando con IA...</p>
+                </div>
+                <p className="text-xs text-muted-foreground" data-testid="text-espera">
+                  Esto puede tardar unos minutos — no cierres esta pestaña.
+                </p>
+              </div>
+            ) : (
+              <div className="flex items-center justify-center gap-2 text-muted-foreground">
+                {isRecording && <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />}
+                <p className="font-medium">{getStatusMessage()}</p>
+              </div>
             )}
```
`git status`: useAudioRecorder.ts (M, C2), home.tsx (M, C1-C5), useMicLevel.ts (untracked, C3). Sin commit.

## 3. Evidencia literal del DoD
1. `pnpm run typecheck` → 4 proyectos Done, **EXIT_CODE=0**.
2. grep `card-procesando|text-espera|Procesando con IA|Esto puede tardar` → getStatusMessage (165), testid card (221), título (226), text-espera conservado (228), texto exacto (229).
3. Confirmado: `text-espera` intacto con em dash; tarjeta y título solo dentro de la rama `isPending`; sin duplicación.
4. `git diff --stat` → useAudioRecorder.ts (C2) + home.tsx; delta MT-C5 solo home.tsx.
5. Nota E2E Director: al procesar → tarjeta prominente; al terminar → desaparece, vuelve el estado normal.

## 4. Desviaciones
Ninguna. Timer arriba sin envolver (opción por defecto del protocolo de dudas).

## 5. Dudas del Ingeniero
Ninguna.

## 6. Estado commiteable
Verde. typecheck exit 0; solo home.tsx tocado por C5; sin commit. Tanda MT-C1..C5 COMPLETA.
