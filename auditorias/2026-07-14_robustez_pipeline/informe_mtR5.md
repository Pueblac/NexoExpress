> **Rotación asistida** (subagente Sonnet, contexto limpio, 17-07-2026). Informe archivado literal. Verificación del Arquitecto: `verificacion_f5.md`.

# Informe de Implementación — MT-R5 (UX de expectativa durante el procesamiento)

## 1. Qué se hizo
Se añadió, en `artifacts/acta-express/src/pages/home.tsx`, un párrafo condicionado a `processAudio.isPending` inmediatamente después del bloque de estado (`<div className="flex items-center justify-center gap-2 text-muted-foreground">...</div>`), tal como especifica el contrato. No se tocó el toggle "Análisis profundo" ni el efecto `lastProcessedAudioRef`, ni ningún otro archivo.

## 2. Hunk + git status
git status ANTES: `audioGuard.ts` (A) + `actas.ts` (M). DESPUÉS: + `home.tsx` (M).
```diff
@@ -202,7 +202,12 @@ export default function Home() {
               {isRecording && <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />}
               <p className="font-medium">{getStatusMessage()}</p>
             </div>
-            
+            {processAudio.isPending && (
+              <p className="text-xs text-muted-foreground" data-testid="text-espera">
+                Esto puede tardar unos minutos — no cierres esta pestaña.
+              </p>
+            )}
+
             <AnimatePresence>
```

## 3. Evidencia DoD
1. git status ANTES/DESPUÉS: coincide con lo esperado.
2. `pnpm run typecheck` → **exit 0** (4 workspaces Done).
3. grep: líneas 206-207 — `text-espera` + texto, condicionado a `processAudio.isPending` (línea 205), hermano siguiente del div de estado.
4. Hunk: arriba.
5. Render real: **NO EJECUTADO** — queda para F5 E2E con el Director (no es desviación).

## 4. Desviaciones
Ninguna.

## 5. Dudas
Ninguna.

## 6. Estado commiteable
Sí. Typecheck verde; working tree con MT-R1..R4 intactos + `home.tsx` de esta MT. Sin commit.

## 7. AVISO
F4→F5, TURNO DE: Arquitecto. Pendiente E2E: render del mensaje durante `isPending`.
