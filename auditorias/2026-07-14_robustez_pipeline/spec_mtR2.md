# Spec MT-R2 — Centinelas anti-confabulación en prompts + heurística reconciliada

**Ciclo:** 2026-07-14_robustez_pipeline · F4 · **Rol:** Ingeniero (Sonnet, rotación asistida)
**Diseño aprobado:** r1 — cambio 3 del dictamen (texto Q3 LITERAL) + OBS-1 de la validación (reconciliar `looksEmpty`). Vinculante.
**Repo:** ActaExpressWeb. El working tree contiene MT-R1 sin commit (esperado, declararlo; no tocarlo).

## Contrato (solo `artifacts/api-server/src/routes/actas.ts`)

1. **ACTA_PROMPT** (≈líneas 19-46): añadir al FINAL de la sección "Reglas:" esta regla, LITERAL (texto Q3 del dictamen, no editar ni una palabra):
> - Si y solo si a lo largo de TODA la grabación no logras detectar ninguna voz humana inteligible (es decir, el audio es únicamente silencio continuo o ruidos de fondo de principio a fin), DEBES generar la salida con título exacto "Reunión sin contenido audible", iniciar el resumen obligatoriamente con la frase "No se detectó contenido audible.", y fijar participantes como un arreglo vacío []. Esta regla tiene prioridad absoluta. Sin embargo, si detectas AL MENOS UN fragmento de conversación humana, omite esta regla, ignora los silencios, redacta el acta y extrae el contenido normalmente en el idioma en que se realizó la reunión. PROHIBIDO inventar o inferir contenido que no esté en el audio; ante duda, declara la ausencia.

2. **SINTESIS_PROMPT** (≈líneas 51-69): añadir al FINAL de "Reglas:" (adaptación aprobada del mismo texto):
> - Si y solo si a lo largo de TODA la grabación no logras detectar ninguna voz humana inteligible, escribe en la sección ===TRANSCRIPCION=== únicamente la línea [SIN CONTENIDO AUDIBLE] y deja las demás secciones vacías. Esta regla tiene prioridad absoluta. Si detectas AL MENOS UN fragmento de conversación humana, omite esta regla e ignora los silencios. PROHIBIDO inventar o inferir contenido que no esté en el audio; ante duda, declara la ausencia.

3. **Heurística `looksEmpty`** (≈líneas 263-268) — reconciliación OBS-1, quedar EXACTAMENTE así:
```ts
const titulo = typeof actaData.titulo === "string" ? actaData.titulo : "";
const silenceKeywords = ["no se pudo", "no audible", "no hay audio", "sin contenido", "silencio", "no se detectó"];
const looksEmpty =
  titulo === "Reunión sin contenido audible" ||
  (participantes.length <= 1 &&
    silenceKeywords.some((kw) => resumen.toLowerCase().includes(kw)));
```
(`participantes` y `resumen` ya existen arriba; no duplicarlos.)

## Restricciones
Solo `actas.ts`. NO tocar la regla de idioma ni el resto de los prompts. No commit.

## DoD (salida literal al informe)
1. `pnpm run typecheck` → exit 0.
2. `grep -n "No se detectó contenido audible\|SIN CONTENIDO AUDIBLE\|no se detectó" artifacts/api-server/src/routes/actas.ts` → las 3 presentes (2 prompts + keyword).
3. Verificación A/B tsx de la expresión reconciliada (copiar la expresión a un script ad-hoc): con `{titulo:"Reunión sin contenido audible", participantes:["X","Y"], resumen:"..."}` → **true** (título manda aunque haya participantes fantasma); con `{titulo:"Reunión normal", participantes:["A","B","C"], resumen:"Se acordó X"}` → **false**; con la reconciliación neutralizada (sin el `titulo ===` y sin la keyword nueva) el resumen centinela `"no se detectó contenido audible."` → **false** (demuestra el hueco OBS-1 que este cambio cierra).
4. `git diff --stat` → solo `actas.ts` (+ lo heredado de MT-R1, declarado).
