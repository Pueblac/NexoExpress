# Respuesta de auditoría de código — Ronda 1 (Gemini 3.1 Pro High)

**Expediente:** 2026-07-07_transcripcion_sintesis
**Recibida:** 07-07-2026 (transportada por el Director, pegada en chat)
**Veredicto del auditor:** APROBADO CON OBSERVACIONES — 1 BUG confirmado (D1)

---

## 1. Respuesta literal del auditor

C1 → EVIDENCIA (actas.ts:252-256, actas.ts:312, actas.ts:314-324, actas.ts:190-194, actas.ts:213): La llamada síncrona llama a callGemini con ACTA_PROMPT y maxOutputTokens: 4096. El res.status(201) se ejecuta antes de generarSintesisEnBackground. La función background llama a callGemini usando el mismo activeFile.uri (subido en uploadToGemini), SINTESIS_PROMPT, maxOutputTokens: 65536 y responseMimeType: "text/plain", guardando con firestoreSet en sintesis/. → TRAZA: El flujo síncrono no se ve afectado y devuelve la respuesta HTTP. Posteriormente, la ejecución asíncrona aprovecha el archivo en caché de la API File de Gemini, cumple las reglas de tokens y mimeType, y no escribe fuera del scope de la colección secundaria. → VEREDICTO: CONFIRMADO.

C2 → EVIDENCIA (actas.ts:318-323): generarSintesisEnBackground(...).catch((sintesisErr: unknown) => { ... req.log.error(...) }) se invoca sin la palabra clave await. → TRAZA: Al invocarse como fire-and-forget, la promesa no suspende el stack síncrono. Cualquier rechazo dentro de ella (como un error de red o timeout de Gemini) invoca la cláusula .catch(), registrando el log de error de forma segura en req.log pero sin generar una unhandled promise rejection ni retrasar al cliente que ya recibió su JSON. → VEREDICTO: CONFIRMADO.

C3 → EVIDENCIA (actas.ts:295-309): const actaLimpia = { ...actaData }; delete actaLimpia.transcripcion; delete actaLimpia.analisis_profundo; delete actaLimpia.preguntas_sin_resolver; delete actaLimpia.temas_clave; const docData: Record<string, unknown> = { ...actaLimpia, ... }; → TRAZA: La variable actaData contiene el JSON en crudo de Gemini. Al clonar las propiedades en actaLimpia y ejecutar explícitamente delete para los 4 campos de síntesis, se garantiza que actaLimpia pierde esas propiedades. Luego, la construcción final del objeto docData es la que se envía a firestoreAdd("actas"), garantizando un documento purgado de sobrecargas. → VEREDICTO: CONFIRMADO.

C4 → EVIDENCIA (actas.ts:314): if (generarSintesis === true) { → TRAZA: req.body.generarSintesis es casteado pero no forzado a booleano antes de evaluarse. Usar el operador de identidad estricta (===) asegura que valores falsy, ausentes (undefined), numéricos (1) o strings ("true") evaluarán a false. La promesa de background sólo se gatilla con un tipo de dato explícitamente booleano true. → VEREDICTO: CONFIRMADO.

C5 → EVIDENCIA (actas.ts:160-176): const markers = [...raw.matchAll(/===(TRANSCRIPCION|ANALISIS_PROFUNDO|PREGUNTAS_SIN_RESOLVER|TEMAS_CLAVE)===/g)]; y const toList = (s: string) => s.split("\n").map((l) => l.replace(/^-\s*/, "").trim()).filter(Boolean);. → TRAZA: Si no hay coincidencias de regex, el bucle de mapeo no se ejecuta y las propiedades inician vacías (""). toList("") genera un array con un string vacío, el cual se recorta y es destruido por .filter(Boolean), retornando []. Si la sección existe, slice captura el contenido, y las líneas con guiones son transformadas de forma aséptica. No hay uso destructivo de métodos inseguros sobre objetos no definidos. → VEREDICTO: CONFIRMADO.

C6 → EVIDENCIA (actas.ts:70-71, actas.ts:200-202): parsed.transcripcion.length > SINTESIS_MAX_CHARS ? parsed.transcripcion.slice(0, SINTESIS_MAX_CHARS) + SINTESIS_TRUNC_SUFFIX : parsed.transcripcion; → TRAZA: Se extrae exactamente el número de posiciones de string indicado (800,000) y se concatena el aviso de truncamiento de manera controlada. → VEREDICTO: CONFIRMADO.

C7 → EVIDENCIA (firebaseAdmin.ts:114-116): const fieldMask = Object.keys(fields).map((k) => `updateMask.fieldPaths=${encodeURIComponent(k)}`).join("&"); → TRAZA: Object.keys({ actaId: "123", ownerId: "456" }) genera ["actaId", "ownerId"]. El map arroja ["updateMask.fieldPaths=actaId", "updateMask.fieldPaths=ownerId"]. El join("&") consolida la string como updateMask.fieldPaths=actaId&updateMask.fieldPaths=ownerId, previniendo el error INVALID_ARGUMENT de Firestore API REST que prohíbe comas en el path. → VEREDICTO: CONFIRMADO.

C8 → EVIDENCIA (actas.ts:220-330, evidencia_mt02.md:12-75): POST /actas/process. → TRAZA: Petición de audio wav, msDuration: 29300, generarSintesis: true. Se genera y sube activeFile.uri. Llamada 1 devuelve acta de 1 minuto (línea 289 calcula Math.round(29300/60000) = 0 pero se solapa con actaData.duracionMinutos === 1). Se responde el 201. Inicia asíncrono, llama a callGemini y obtiene síntesis plana. Parse captura sin truncar porque transcripción pesa <1 KB. Se insertan en sintesis/{id} los campos actaId, ownerId, transcripcion, analisis_profundo, preguntas_sin_resolver, temas_clave, y createdAt. El documento final es exactamente el observado en REST vía evidencia_mt02.md. → VEREDICTO: CONFIRMADO.

Respuestas a Preguntas de Control

Q1:

```typescript
295:     const actaLimpia = { ...actaData };
296:     delete actaLimpia.transcripcion;
297:     delete actaLimpia.analisis_profundo;
298:     delete actaLimpia.preguntas_sin_resolver;
299:     delete actaLimpia.temas_clave;
```

Q2: Devuelve un objeto con secciones vacías o arrays vacíos por defecto. Al fallar el regex matchAll, el array markers queda vacío []. No se sobrescriben las propiedades base de sections, quedando intactas. Traza de campos retornados: transcripcion: "" / analisis_profundo: "" / preguntas_sin_resolver: [] (Resultado de toList(""): separa en [""], reemplaza -, trimea, y .filter(Boolean) elimina los vacíos) / temas_clave: []

Q3: https://firestore.googleapis.com/v1/projects/actaexpress/databases/(default)/documents/sintesis/abc?updateMask.fieldPaths=actaId&updateMask.fieldPaths=ownerId

Q4: No puede leerla. Regla de evaluación (firestore_rules_desplegadas.rules:21): allow read, update, delete: if request.auth != null && request.auth.uid == resource.data.ownerId; Traza: El request.auth.uid corresponde al usuario A, pero el campo resource.data.ownerId del documento pertenece al usuario B. Ya que A !== B, la regla de Firestore prohíbe explícitamente el acceso devolviendo false (y emitiendo un código 403 Forbidden).

Anti-aprobación-automática (Refutación)

T1 (Concurrencia cruzada): No aplica. En actas.ts:310, se crea una ID única por petición para el acta. La promesa de generarSintesisEnBackground captura esta id y las credenciales vía closure de variables léxicas. No hay variables globales modificables, cada ejecución de background asume su propio espacio en memoria con su propia actaId. No pueden cruzarse ni pisarse.
T2 (Delimitadores desordenados/duplicados): No lanza. El parser usa matchAll iterativo. Para duplicados, evalúa el nombre extraído markers[i][1], por lo que el último duplicado sobrescribe el valor del diccionario sin lanzar excepciones. Para desorden, el bloque usa un substring dinámico dependiente de la posición actual de match hasta el índice del próximo match.
T3 (Pérdida silenciosa sin logging): No aplica. El error del .catch incluye req.log.error({ err: sintesisErr, errMsg: msg, actaId: id }, "sintesis: falló la generación en background"); (actas.ts:322). Esto garantiza trazabilidad centralizada de caídas de la feature secundaria asociando el ID del acta.
T4 (Abuso de tokens): Riesgo aceptado. No existe control explícito de rate limiting de background-tokens dentro de esta porción de código. La API expuesta está protegida por Firebase Auth (requireAuth), pero un usuario legítimo podría abusar. Corresponde a la carencia estructural ya prevista.
T5 (Derrame espontáneo): Purga comprobada. El código de C3 destruye metódicamente las 4 claves indeseadas usando delete actaLimpia.[key] pre-inserción. Si el LLM decide agregarlas a su JSON, son ignoradas y no ingresan al registro Firestore.

Dudas del Implementador

D1 (Truncado por bytes): BUG. El truncado usa .length (basado en caracteres UTF-16, actas.ts:200) sobre 800_000, sin embargo, Firestore restringe a 1.048.576 BYTES el payload total HTTP. Caracteres Unicode multiybte pueden sobrepasar ese byte-limit. firestoreSet fallará devolviendo un 400 y el error será atrapado por el catch de generarSintesisEnBackground, muriendo en silencio de cara al cliente (aunque se loggeará internamente). Obliga a refactorizar usando cálculo posicional de BYTES (Buffer.byteLength).
D2 (Delimitador inyectado en transcripción): Observación aceptable. Dado el uso de regex de captura sobre raw completo y considerando que STT del LLM procesa audio hablado, emitir una string perfecta de sintaxis markdown para delimitadores es absurdamente baja y estadísticamente irrelevante.
D3 (Caducidad del idToken): Observación aceptable. Si el upload se bloquea 55 minutos el token fallaría, pero el timeout base de fetch / TCP no permite mantener conexiones muertas en un balanceador estándar Node por ese volumen sin interrupciones. La operación regular toma segundos.
D4 (Parser unit test): Deuda aceptable documentada. Si bien un parser sobre texto arbitrario sufre, se diseñó con control defensivo por defecto que retorna vacío y no emite excepciones crudas, evitando caídas letales y previniendo errores de sistema.
D5 (Heurística de silencio): Observación aceptable. El LLM genera tokens base reportando nulos contenidos para un audio sin habla, consumiendo tokens proporcionales muy mínimos para SINTESIS_PROMPT. El costo es insignificante comparado con la reingeniería de validación previa en esta fase.

Veredicto Global

APROBADO CON OBSERVACIONES

Se confirma fidelidad al diseño, estructura robusta frente a demoras y caídas mediante background-tasks seguras, y parseo aséptico de texto sin excepciones por desorden LLM. Queda mandatario el ajuste por BUG del cálculo de truncado (D1), el cual deberá ser refactorizado para limitar por Buffer.byteLength(string, 'utf8') previo a despliegues en producción definitiva para no violar restricciones de arquitectura REST Firestore.

---

## 2. Validación anti-bluff del Ingeniero (07-07-2026)

Todas las citas verificadas por ejecución (`sed`/`grep` sobre los archivos reales):

| Cita del auditor | Verificación | Resultado |
|---|---|---|
| actas.ts:252-256 (llamada 1: ACTA_PROMPT, 4096, JSON) | sed | Coincide textual. ✅ |
| actas.ts:310/312/314/318-323 (firestoreAdd → 201 → flag `=== true` → `.catch` con log.error en 322) | sed | Coincide, orden correcto. ✅ |
| actas.ts:295-299 (Q1, purga) | sed | Coincidencia TEXTUAL exacta de las 5 líneas. ✅ |
| actas.ts:190-194 / 200-202 / 213 (llamada 2, truncado, firestoreSet) | sed | Coincide. ✅ |
| actas.ts:70-71 (constantes) / 160-163 (parser) | sed | Coincide. ✅ |
| firebaseAdmin.ts:114-116 (fix updateMask) | sed | Coincide textual. ✅ |
| firestore_rules_desplegadas.rules:21 (Q4) | sed | La línea 21 es exactamente `allow read, update, delete...` del bloque `sintesis/`. ✅ |
| Q2 (traza del parser sin delimitadores) | lectura del código | Correcta: markers=[], sections intactas, toList("")→[]. ✅ |
| Q3 (URL de firestoreSet) | derivación del código | Correcta. ✅ |
| C8 (Math.round(29300/60000)=0, solapado por duracionMinutos=1 del modelo) | aritmética + evidencia_mt02 | Correcto. ✅ |

**Resultado: auditoría VÁLIDA.**

## 3. Dictamen final de la ronda

**APROBADO CON OBSERVACIONES + 1 BUG confirmado → se corrige y se abre RONDA 2** (regla del ciclo: BUG confirmado = corregir + ronda nueva).

- **BUG D1 (confirmado por ambas partes):** truncado por caracteres cuando el límite de Firestore es por bytes. **Corrección mandatada:** truncar por `Buffer.byteLength` UTF-8. Se implementa como helper puro exportado (`truncarPorBytes`) con verificación A/B ejecutada (el test debe fallar con la lógica vieja de caracteres).
- **T4 (abuso de tokens): riesgo aceptado y documentado** — sin rate limiting en esta fase; queda registrado aquí como carencia estructural conocida, ligada a la restricción de billing (tier gratuito de Gemini) anotada por el Director.
- **D2, D3, D5: observaciones aceptables** sin acción.
- **D4 (test unitario del parser): deuda aceptable** — mitigada parcialmente en ronda 2, porque el helper de truncado nace con test A/B ejecutable.
- Alcance de ronda 2: SOLO el fix D1 + no-regresión del flujo (los claims C1-C5, C7, C8 quedan con dictamen vigente de esta ronda).
