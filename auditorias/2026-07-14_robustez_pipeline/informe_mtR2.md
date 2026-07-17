> **Rotación asistida** (subagente Sonnet, contexto limpio, 17-07-2026). Informe archivado literal. Verificación del Arquitecto: `verificacion_f5.md`.

# Informe de Implementación — MT-R2: Centinelas anti-confabulación en prompts + heurística reconciliada

## 1) Qué se hizo

Working tree al iniciar contenía MT-R1 sin commit (declarado, no tocado). Sobre `artifacts/api-server/src/routes/actas.ts` se aplicaron los 3 cambios del contrato, literales:

1. Añadida al final de "Reglas:" de `ACTA_PROMPT` la regla del centinela anti-confabulación (título "Reunión sin contenido audible", resumen que inicia con "No se detectó contenido audible.", participantes `[]`, prioridad absoluta, prohibición de inventar).
2. Añadida al final de "Reglas:" de `SINTESIS_PROMPT` la regla equivalente para `===TRANSCRIPCION===` → `[SIN CONTENIDO AUDIBLE]`.
3. Reemplazada la heurística `looksEmpty` por la versión reconciliada: `titulo` extraído de `actaData.titulo`, keyword `"no se detectó"` añadida, y condición `titulo === "Reunión sin contenido audible" || (participantes.length <= 1 && silenceKeywords.some(...))`.

No se tocó la regla de idioma ni los cambios de MT-R1.

## 2) Diff literal (hunks de esta MT; el diff completo incluye MT-R1 preexistente)

```diff
@@ -43,7 +44,8 @@ Reglas:
 - Si no identificas nombres usa "Participante 1", "Participante 2", etc.
 - Si no hubo acuerdos explícitos devuelve "acuerdos": []
 - Si no hay tareas pendientes devuelve "pendientes": []
-- No incluyas texto ni explicaciones fuera del JSON`;
+- No incluyas texto ni explicaciones fuera del JSON
+- Si y solo si a lo largo de TODA la grabación no logras detectar ninguna voz humana inteligible (es decir, el audio es únicamente silencio continuo o ruidos de fondo de principio a fin), DEBES generar la salida con título exacto "Reunión sin contenido audible", iniciar el resumen obligatoriamente con la frase "No se detectó contenido audible.", y fijar participantes como un arreglo vacío []. Esta regla tiene prioridad absoluta. Sin embargo, si detectas AL MENOS UN fragmento de conversación humana, omite esta regla, ignora los silencios, redacta el acta y extrae el contenido normalmente en el idioma en que se realizó la reunión. PROHIBIDO inventar o inferir contenido que no esté en el audio; ante duda, declara la ausencia.`;
@@ -66,7 +68,8 @@
 Reglas:
 - No escribas NADA fuera de las cuatro secciones.
-- Los delimitadores deben aparecer EXACTAMENTE como se muestran, cada uno en su propia línea.`;
+- Los delimitadores deben aparecer EXACTAMENTE como se muestran, cada uno en su propia línea.
+- Si y solo si a lo largo de TODA la grabación no logras detectar ninguna voz humana inteligible, escribe en la sección ===TRANSCRIPCION=== únicamente la línea [SIN CONTENIDO AUDIBLE] y deja las demás secciones vacías. Esta regla tiene prioridad absoluta. Si detectas AL MENOS UN fragmento de conversación humana, omite esta regla e ignora los silencios. PROHIBIDO inventar o inferir contenido que no esté en el audio; ante duda, declara la ausencia.`;
@@ -262,10 +275,12 @@
     const participantes = Array.isArray(actaData.participantes) ? actaData.participantes : [];
     const resumen = typeof actaData.resumen === "string" ? actaData.resumen : "";
-    const silenceKeywords = ["no se pudo", "no audible", "no hay audio", "sin contenido", "silencio"];
+    const titulo = typeof actaData.titulo === "string" ? actaData.titulo : "";
+    const silenceKeywords = ["no se pudo", "no audible", "no hay audio", "sin contenido", "silencio", "no se detectó"];
     const looksEmpty =
-      participantes.length <= 1 &&
-      silenceKeywords.some((kw) => resumen.toLowerCase().includes(kw));
+      titulo === "Reunión sin contenido audible" ||
+      (participantes.length <= 1 &&
+        silenceKeywords.some((kw) => resumen.toLowerCase().includes(kw)));
```

## 3) Evidencia DoD

1. git status ANTES = DESPUÉS: `audioGuard.ts` (A) + `actas.ts` (M).
2. `pnpm run typecheck` → exit 0 (4 proyectos Done).
3. grep centinelas: línea 48 (ACTA_PROMPT), línea 72 (SINTESIS_PROMPT), línea 279 (keyword) — las tres presentes.
4. **Verificación A/B (tsx ad-hoc, eliminado tras la corrida):**
```
Caso 1 (título manda con participantes fantasma): NUEVO: true (esperado true) ✓
Caso 2 (reunión normal): NUEVO: false (esperado false) ✓
Caso 3 (OBS-1, resumen centinela + 0 participantes):
  VIEJO: false ← demuestra el hueco original
  NUEVO: true  ← corregido por la reconciliación
```
Los 5 resultados coinciden con lo especificado.

## 4) Desviaciones
Ninguna respecto al contrato textual. Nota operativa: DoD 4 ejecutado con `scripts/node_modules/.bin/tsx` (no había tsx global).

## 5) Dudas
Ninguna.

## 6) Estado commiteable
Sí: compila, contiene MT-R1 (intacto) + MT-R2 (verificado por DoD 3 y 4). Sin commit.

## 7) AVISO
F4→F5, TURNO DE: Arquitecto. Punto clave a confirmar: el A/B del DoD 4 demuestra el cierre del hueco OBS-1.
