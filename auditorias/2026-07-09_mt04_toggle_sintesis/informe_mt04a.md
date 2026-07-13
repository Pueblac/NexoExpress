# Informe de Implementación — MT-04a: Regenerar clientes API (`generarSintesis`)

**Ciclo:** 2026-07-09_mt04_toggle_sintesis · **Fase:** F4 → **DETENIDO, no se completó (ver §5 Dudas)**
**Rol:** Ingeniero (Claude Sonnet)
**Repo de trabajo:** `/home/pueblac/AndroidStudioProjects/ActaExpressWeb`

## 1. Qué se hizo (por archivo)

1. Verifiqué working tree limpio en `ActaExpressWeb` (`git status --short` sin salida).
2. Ejecuté `pnpm --filter @workspace/api-spec codegen` (orval + `typecheck:libs`). Exit 0.
3. Confirmé vía grep que `generarSintesis` aparece en ambos paquetes generados.
4. Ejecuté `pnpm run typecheck` (workspace completo). Exit 0.
5. Inspeccioné `git diff` / `git diff --stat` según la regla de diff limpio (diseño C1).

**Resultado: el diff NO es limpio.** Junto con `generarSintesis` (el cambio esperado), el codegen introdujo cambios adicionales derivados de campos que ya existían en `lib/api-spec/openapi.yaml` pero que aún no estaban reflejados en los artefactos generados:

- Nuevo tipo `ActaPlataforma` (enum `web`/`android`) en `api.schemas.ts` y nuevo archivo `lib/api-zod/src/generated/types/actaPlataforma.ts`.
- Campo `plataforma?: ActaPlataforma` añadido a `Acta`.
- Campo `updatedAt?: string | null` añadido a `Acta`.
- Export correspondiente en `lib/api-zod/src/generated/types/index.ts`.

No edité `openapi.yaml` ni ningún archivo fuera de `generated/`. Verifiqué que `plataforma` y `updatedAt` ya estaban presentes en el yaml antes de correr el comando (`grep -n "plataforma\|updatedAt\|ActaPlataforma" lib/api-spec/openapi.yaml` → líneas 192 y 197), es decir, no los introduje yo: son drift preexistente entre el contrato y los artefactos generados, capturado como efecto colateral al regenerar.

Por la regla vinculante del diseño C1 ("si aparece CUALQUIER cambio no derivado del campo `generarSintesis`... DETENTE: no intentes arreglarlo, devuélvelo como duda"), **no intenté aislar ni revertir estos cambios adicionales**. El working tree de `ActaExpressWeb` queda actualmente en este estado mixto (ver diff abajo) a la espera de instrucción del Arquitecto.

## 2. Diff literal

### `git status --short` (ANTES de regenerar)

```
(sin salida — working tree limpio)
```

### `git status --short` (DESPUÉS de regenerar)

```
 M lib/api-client-react/src/generated/api.schemas.ts
 M lib/api-zod/src/generated/api.ts
 M lib/api-zod/src/generated/types/acta.ts
 M lib/api-zod/src/generated/types/audioInput.ts
 M lib/api-zod/src/generated/types/index.ts
?? lib/api-zod/src/generated/types/actaPlataforma.ts
```

### `git diff --stat`

```
 lib/api-client-react/src/generated/api.schemas.ts | 13 +++++++++++++
 lib/api-zod/src/generated/api.ts                  | 13 ++++++++++---
 lib/api-zod/src/generated/types/acta.ts           |  4 ++++
 lib/api-zod/src/generated/types/audioInput.ts     |  2 ++
 lib/api-zod/src/generated/types/index.ts          |  1 +
 5 files changed, 30 insertions(+), 3 deletions(-)
```

### `git diff` (completo)

```diff
diff --git a/lib/api-client-react/src/generated/api.schemas.ts b/lib/api-client-react/src/generated/api.schemas.ts
index fee878b..3666fbc 100644
--- a/lib/api-client-react/src/generated/api.schemas.ts
+++ b/lib/api-client-react/src/generated/api.schemas.ts
@@ -17,6 +17,14 @@ export interface Pendiente {
   fecha: string | null;
 }
 
+export type ActaPlataforma = typeof ActaPlataforma[keyof typeof ActaPlataforma];
+
+
+export const ActaPlataforma = {
+  web: 'web',
+  android: 'android',
+} as const;
+
 export interface Acta {
   id: string;
   titulo: string;
@@ -30,14 +38,19 @@ export interface Acta {
   acuerdos: string[];
   pendientes: Pendiente[];
   ownerId: string;
+  plataforma?: ActaPlataforma;
   /** @nullable */
   createdAt?: string | null;
+  /** @nullable */
+  updatedAt?: string | null;
 }
 
 export interface AudioInput {
   audioBase64: string;
   mimeType: string;
   msDuration: number;
+  /** Si es true, genera transcripción y análisis profundo en background (colección sintesis/) */
+  generarSintesis?: boolean;
 }
 
 export interface DeleteResult {
diff --git a/lib/api-zod/src/generated/api.ts b/lib/api-zod/src/generated/api.ts
index de32cbd..37db263 100644
--- a/lib/api-zod/src/generated/api.ts
+++ b/lib/api-zod/src/generated/api.ts
@@ -39,7 +39,9 @@ export const ListActasResponseItem = zod.object({
   "fecha": zod.string().nullable()
 })),
   "ownerId": zod.string(),
-  "createdAt": zod.string().nullish()
+  "plataforma": zod.enum(['web', 'android']).optional(),
+  "createdAt": zod.string().nullish(),
+  "updatedAt": zod.string().nullish()
 })
 export const ListActasResponse = zod.array(ListActasResponseItem)
 
@@ -51,10 +53,13 @@ export const ProcessAudioHeader = zod.object({
   "authorization": zod.string()
 })
 
+export const processAudioBodyGenerarSintesisDefault = false;
+
 export const ProcessAudioBody = zod.object({
   "audioBase64": zod.string(),
   "mimeType": zod.string(),
-  "msDuration": zod.number()
+  "msDuration": zod.number(),
+  "generarSintesis": zod.boolean().default(processAudioBodyGenerarSintesisDefault).describe('Si es true, genera transcripción y análisis profundo en background (colección sintesis\/)')
 })
 
 
@@ -84,7 +89,9 @@ export const GetActaResponse = zod.object({
   "fecha": zod.string().nullable()
 })),
   "ownerId": zod.string(),
-  "createdAt": zod.string().nullish()
+  "plataforma": zod.enum(['web', 'android']).optional(),
+  "createdAt": zod.string().nullish(),
+  "updatedAt": zod.string().nullish()
 })
 
 
diff --git a/lib/api-zod/src/generated/types/acta.ts b/lib/api-zod/src/generated/types/acta.ts
index 1bbd7a6..6f6e574 100644
--- a/lib/api-zod/src/generated/types/acta.ts
+++ b/lib/api-zod/src/generated/types/acta.ts
@@ -5,6 +5,7 @@
  * ActaExpress API — procesa audio de reuniones y genera actas con IA
  * OpenAPI spec version: 0.1.0
  */
+import type { ActaPlataforma } from './actaPlataforma';
 import type { Pendiente } from './pendiente';
 
 export interface Acta {
@@ -20,6 +21,9 @@ export interface Acta {
   acuerdos: string[];
   pendientes: Pendiente[];
   ownerId: string;
+  plataforma?: ActaPlataforma;
   /** @nullable */
   createdAt?: string | null;
+  /** @nullable */
+  updatedAt?: string | null;
 }
diff --git a/lib/api-zod/src/generated/types/audioInput.ts b/lib/api-zod/src/generated/types/audioInput.ts
index 352dbc1..bdd9a63 100644
--- a/lib/api-zod/src/generated/types/audioInput.ts
+++ b/lib/api-zod/src/generated/types/audioInput.ts
@@ -10,4 +10,6 @@ export interface AudioInput {
   audioBase64: string;
   mimeType: string;
   msDuration: number;
+  /** Si es true, genera transcripción y análisis profundo en background (colección sintesis/) */
+  generarSintesis?: boolean;
 }
diff --git a/lib/api-zod/src/generated/types/index.ts b/lib/api-zod/src/generated/types/index.ts
index 5310bd6..599d4ad 100644
--- a/lib/api-zod/src/generated/types/index.ts
+++ b/lib/api-zod/src/generated/types/index.ts
@@ -7,6 +7,7 @@
  */
 
 export * from './acta';
+export * from './actaPlataforma';
 export * from './audioInput';
 export * from './deleteResult';
 export * from './healthStatus';
```

(El archivo nuevo `lib/api-zod/src/generated/types/actaPlataforma.ts` es untracked (`??`), no aparece en `git diff` por defecto; su contenido es el enum `ActaPlataforma` con valores `web`/`android`, análogo al bloque ya mostrado en `api.schemas.ts`.)

## 3. Evidencia literal — DoD

### 1) `git status --short` (antes)

```
$ git status --short
(sin salida)
```

### 2) `pnpm --filter @workspace/api-spec codegen`

```
$ pnpm --filter @workspace/api-spec codegen
$ orval --config ./orval.config.ts && pnpm -w run typecheck:libs
🍻 orval v8.9.1 - A swagger client generator for typescript
api-client-react Cleaning output folder
🎉 api-client-react - Your OpenAPI spec has been converted into ready to use orval!
zod Cleaning output folder
🎉 zod - Your OpenAPI spec has been converted into ready to use orval!
$ tsc --build
EXIT:0
```

### 3) `grep -rn "generarSintesis" lib/api-client-react/src/generated/ lib/api-zod/src/generated/`

```
lib/api-zod/src/generated/api.ts:62:  "generarSintesis": zod.boolean().default(processAudioBodyGenerarSintesisDefault).describe('Si es true, genera transcripción y análisis profundo en background (colección sintesis\/)')
lib/api-client-react/src/generated/api.schemas.ts:53:  generarSintesis?: boolean;
lib/api-zod/src/generated/types/audioInput.ts:14:  generarSintesis?: boolean;
EXIT:0
```

### 4) `pnpm run typecheck`

```
$ pnpm run typecheck
$ pnpm run typecheck:libs && pnpm -r --filter "./artifacts/**" --filter "./scripts" --if-present run typecheck
$ tsc --build
Scope: 4 of 9 workspace projects
artifacts/api-server typecheck$ tsc -p tsconfig.json --noEmit
artifacts/acta-express typecheck$ tsc -p tsconfig.json --noEmit
artifacts/mockup-sandbox typecheck$ tsc -p tsconfig.json --noEmit
scripts typecheck$ tsc -p tsconfig.json --noEmit
scripts typecheck: Done
artifacts/api-server typecheck: Done
artifacts/mockup-sandbox typecheck: Done
artifacts/acta-express typecheck: Done
EXIT:0
```

### 5) `git diff --stat`

```
 lib/api-client-react/src/generated/api.schemas.ts | 13 +++++++++++++
 lib/api-zod/src/generated/api.ts                  | 13 ++++++++++---
 lib/api-zod/src/generated/types/acta.ts           |  4 ++++
 lib/api-zod/src/generated/types/audioInput.ts     |  2 ++
 lib/api-zod/src/generated/types/index.ts          |  1 +
 5 files changed, 30 insertions(+), 3 deletions(-)
```

**Nota:** el paso 5 del DoD ("SOLO archivos generated/") se cumple en cuanto a *ubicación* (todos los archivos tocados están bajo `generated/`), pero NO se cumple en cuanto a *contenido* — el diff incluye cambios no derivados de `generarSintesis`. Ver §5.

## 4. Desviaciones

Una desviación, forzosa por la regla de diff limpio (C1): el comando de codegen indicado por la spec (`pnpm --filter @workspace/api-spec codegen`) es el único mecanismo permitido para regenerar, y al ejecutarlo — sin editar `openapi.yaml` ni ningún otro archivo — el resultado arrastra drift preexistente del contrato (campos `plataforma`, `updatedAt`, tipo `ActaPlataforma`) que ya estaba en `openapi.yaml` antes de esta tarea pero nunca se había regenerado. No hay forma de correr el codegen y obtener SOLO el cambio de `generarSintesis` sin editar a mano el yaml o el output generado, ambos prohibidos por la spec. Por tanto, **no completé el contrato del §3 de la spec** (working tree con diff limpio) y dejo el repo en el estado intermedio descrito arriba, sin commit.

## 5. Dudas

**Duda que reabre F3, según protocolo §6:**

El diff de la regeneración no es atribuible únicamente a `generarSintesis`. `openapi.yaml` ya contenía (antes de esta tarea, no modificado por mí) los campos `plataforma` y `updatedAt` en el schema `Acta` (líneas 192 y 197), que nunca se habían propagado a los artefactos `generated/`. Al ejecutar el único comando de codegen permitido, ambos drifts se resuelven a la vez — no hay manera de aislar `generarSintesis` sin tocar a mano archivos `generated/` (prohibido) o el `openapi.yaml`/`orval.config.ts` (prohibido).

Preguntas para el Arquitecto:
1. ¿El drift de `plataforma`/`updatedAt`/`ActaPlataforma` es un cambio de contrato ya aprobado en otro ciclo (y por tanto aceptable dejarlo entrar junto con `generarSintesis`), o es trabajo en curso de otra rama/tarea que no debía mezclarse aquí?
2. Si es aceptable, ¿autorizas incluirlo en el mismo diff/commit de MT-04a, o prefieres que se separe en dos commits (uno solo con el hunk de `generarSintesis`, otro con el resto) aunque ambos provengan del mismo comando de codegen?
3. Si NO es aceptable, ¿cómo se espera que se aísle `generarSintesis` dado que las únicas dos rutas (editar generated a mano, o editar yaml/config) están explícitamente prohibidas por esta misma spec?

No tomé ninguna decisión unilateral sobre estas preguntas. El working tree de `ActaExpressWeb` queda tal como está (sin commit) a la espera de spec nueva.

## 6. Confirmación de estado commiteable

**NO commiteable según el contrato original de la spec** (el diff no es limpio). El working tree de `ActaExpressWeb` tiene 5 archivos modificados + 1 archivo nuevo untracked, todos bajo `generated/`, sin commit, sin tocar credenciales ni Firestore, sin editar `openapi.yaml`/`orval.config.ts`/dependencias. No se hizo `git add` ni `git commit`.

## 7. Aviso de traspaso

━━ AVISO DE TRASPASO ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CICLO      : 2026-07-09_mt04_toggle_sintesis
FASE       : F4 → F3 (reabierta por duda, ver §5) — spec MT-04a DETENIDA
TURNO DE   : Arquitecto (Fable)
ENTREGAR   : este documento (informe_mt04a.md)
ADJUNTOS   : Ninguno (repo local `ActaExpressWeb` es el material de trabajo;
             working tree con cambios sin commit, ver §2)
DESTINO    : Sesión de Arquitecto del ciclo 2026-07-09_mt04_toggle_sintesis
ACCIÓN     : Resolver la duda de §5 (drift `plataforma`/`updatedAt`/
             `ActaPlataforma` mezclado con `generarSintesis` en el mismo
             codegen) y emitir spec MT-04a v2 (o instrucción explícita)
VUELVE A   : Ingeniero (Claude Sonnet), sesión nueva sobre
             `ActaExpressWeb`, con la spec actualizada
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

---
---

# ANEXO — Verificación F5 del Arquitecto (09-07-2026)

**Resolución de la duda:** `spec_mt04a_r2.md` (F3') — drift ACEPTADO como contrato aprobado del ciclo `2026-07-07` (verificado: `git log -- lib/api-spec/openapi.yaml` → último cambio `6811f56`, el commit de ese ciclo); alcance de MT-04a ampliado a "sincronizar clientes con el yaml vigente"; un solo diff/commit. Sin trabajo nuevo para el Ingeniero.

**F5 — DoD re-EJECUTADO por el Arquitecto sobre el working tree real (no leído del informe):**

1. `git status --short` → coincide exactamente con §2 del informe (5 M + 1 ?? bajo `generated/`). ✅
2. `grep -rn "generarSintesis" lib/api-client-react/src/generated/ lib/api-zod/src/generated/` → 3 resultados, idénticos a los del informe (`api.schemas.ts:53`, `types/audioInput.ts:14`, `api.ts:62`). ✅
3. `pnpm run typecheck` → re-ejecutado: los 4 proyectos `Done`, `EXIT=0`. ✅
4. Mapeo hunk→yaml verificado: `plataforma` enum `["web","android"]` (yaml líneas 192-194) ↔ `ActaPlataforma`; `updatedAt` nullable (líneas 197-198) ↔ `updatedAt?: string | null`; `generarSintesis` (línea 218) ↔ AudioInput. Ningún hunk sin origen en el yaml. ✅
5. Contraste informe vs realidad (anti-bluff interno): sin discrepancias; desviación declarada correctamente; ninguna desviación no declarada. ✅

**Veredicto F5: MT-04a CERRADA — entregable aceptado con el alcance ampliado de la r2.** El comportamiento del Ingeniero fue el especificado (DETENTE + duda, cero decisiones unilaterales). Siguiente: F4 de MT-04b sobre este working tree (la spec_mt04b ya contempla declararlo en su DoD 1).