# Respuesta de diseño — Ronda 1 (Gemini 3.1 Pro High)

**Expediente:** 2026-07-07_transcripcion_sintesis
**Recibida:** 07-07-2026 (transportada por el Director)
**Veredicto del auditor:** APROBADO CON CAMBIOS

---

## 1. Respuesta literal del auditor

C1 → EVIDENCIA: CTX-1 (actualmente no pide transcripción) y CTX-2 (una sola llamada a generateContent). → TRAZA: Acoplar la generación del acta corta (pocos tokens) con la transcripción completa (decenas de miles de tokens) en una sola respuesta JSON síncrona incrementa radicalmente la latencia percibida por el usuario HTTP. Si la llamada masiva falla o se trunca, el reintento propuesto duplica el costo de procesar el archivo de audio. → VEREDICTO: DÉBIL (Requiere cambio a llamadas separadas, ver Q1).

C2 → EVIDENCIA: CTX-2 (maxOutputTokens: 4096). → TRAZA: Subir el límite a 65536 permite al modelo devolver outputs de hasta ~260,000 caracteres, suficiente para reuniones largas. → VEREDICTO: SÓLIDO (Correcto para evitar el truncamiento por token limit).

C3 → EVIDENCIA: CTX-2 (no inspecciona finishReason). → TRAZA: El reintento condicionado a "MAX_TOKENS" o fallo de parse salva el acta básica, pero requiere pagar por segunda vez el cómputo del input (audio) y sumar secuencialmente ambas latencias (la fallida masiva + la básica), resultando en un probable timeout del HTTP request (típicamente 30-60s en balanceadores). → VEREDICTO: DÉBIL (La estrategia de degradación daña severamente la latencia. Ver Q2).

C4 → EVIDENCIA: CTX-3 (...actaData derrama todo en Firestore). → TRAZA: Extraer variables mediante destructuring (const { transcripcion, analisis_profundo, preguntas_sin_resolver, temas_clave, ...actaLimpia } = actaData) antes del insert en actas/{id} purga efectivamente los campos pesados del documento principal. → VEREDICTO: SÓLIDO.

C5 → EVIDENCIA: CTX-6 (colección sintesis/{actaId} documentada). → TRAZA: Los cuatro campos nuevos solicitados al LLM mapean exactamente a las propiedades ya especificadas en el contrato, sin añadir divergencias. → VEREDICTO: SÓLIDO.

C6 → EVIDENCIA: CTX-6 (Límite duro de Firestore: 1 MiB). → TRAZA: 800,000 caracteres en UTF-8 equivalen aproximadamente a 800 KB (asumiendo caracteres ASCII mayormente y tildes de 2 bytes). Esto deja ~200 KB de margen para analisis_profundo y metadatos, garantizando matemáticamente que la escritura de firestoreSet nunca alcance 1,048,576 bytes. → VEREDICTO: SÓLIDO.

Respuestas a Preguntas de Control

Q1: DOS LLAMADAS SEPARADAS Y PARALELAS. Justificación: Ligar el JSON corto del acta a la transcripción masiva destruye la latencia síncrona del endpoint y arriesga romper el JSON por errores de escape del LLM en strings kilométricos. El endpoint HTTP debe hacer una llamada rápida y confiable solo para el acta (como hoy) para retornar rápido al usuario; simultáneamente (o despachado en background sin bloquear la respuesta), se ejecuta la segunda llamada pidiendo texto plano (text/plain) con la transcripción, la cual se guarda directo en sintesis/. Aunque se pague el input (audio) dos veces, el costo es asumible frente a evitar la destrucción de la UX por latencia HTTP y fallos de parseo.

Q2: PARTIR EN DOS LLAMADAS (ACTA SÍNCRONA, SÍNTESIS BACKGROUND). Justificación: El reintento propuesto (C3) obliga al cliente a esperar secuencialmente la caída del prompt pesado y la regeneración del liviano, garantizando casi con seguridad un HTTP 504 Gateway Timeout antes de terminar. Al separar el proceso (acta síncrona sin síntesis; transcripción asíncrona fire-and-forget), se elimina el riesgo de perder el acta principal, haciendo innecesario el reintento de degradación sobre el endpoint síncrono.

Q3: SOLO EL ACTA BÁSICA (sin los campos de síntesis). Justificación: El frontend "no consume la síntesis" y la transcripción pesa "cientos de KB". Retornar todo en el 201 inflaría el payload de respuesta HTTP masivamente (demora en serialización, ancho de banda y tiempo de descarga en móviles), degradando el rendimiento percibido sin entregar valor en la UI actual.

Q4: Traza de escenario (90 minutos, ~110.000 caracteres de transcripción): Si el diseño propuesto se ejecutara exactamente como está planteado (1 llamada):

Generación de ~110,000 caracteres implica aprox. 27,500 tokens de salida, más los tokens del análisis. Total estimado: ~30,000 tokens.
Si el límite siguiera en 4096 (CTX-2): El modelo cortaría la salida a la mitad de la transcripción. finishReason sería "MAX_TOKENS". Fallaría JSON.parse (línea 109). Entraría el reintento C3, demorando el doble pero guardando solo el acta vacía de síntesis.
Con el diseño propuesto (Límite 65536): Finaliza exitosamente en ~30,000 tokens.
actas/{id} estado final: { titulo, fecha, duracionMinutos: 90, participantes, resumen, puntosImportantes, acuerdos, pendientes, ownerId, plataforma: "web", audioStoragePath: null, createdAt, updatedAt }. (Ningún campo extra, gracias a C4).
sintesis/{id} estado final: { actaId, ownerId, transcripcion: "texto... (110k chars)", analisis_profundo: "...", preguntas_sin_resolver: [...], temas_clave: [...], contexto_previo: "", createdAt }. (Sin sufijo de truncamiento porque 110,000 < 800,000, gracias a C6).

Refutación de Trampas (Asumiendo el rediseño forzado)

T1: (Exceso de tokens rompe el JSON y pierde el acta). Neutralizado por el cambio forzado de separar en dos llamadas (Q1/Q2). La llamada del acta es corta y nunca trunca; la transcripción plana no depende de JSON, así que si trunca, simplemente se guarda incompleta pero no rompe el flujo principal. T2: (Spread derrama transcripcion en actas/). Neutralizado por C4 (destructuring de actaData), que purga los campos pesados del objeto antes de llamar a firestoreAdd (CTX-3). T3: (Documento excede 1 MiB). Neutralizado por C6. Truncar a 800.000 caracteres garantiza un tamaño máximo en bytes seguro para Firestore antes de llegar a firestoreSet. T4: (Cambio de nombres de claves o texto fuera de JSON). Al quitar la inmensa transcripción del interior del JSON (por el cambio de separar llamadas), el modelo vuelve a focalizarse en un output corto, reduciendo la alucinación de claves. Además, el manejo estricto por defecto (degradación a arrays vacíos) en el bloque de síntesis (CTX-4) absorbe sin caerse claves mal formadas. T5: (Paridad con Android que no escribe sintesis/). Neutralizado por C5. Android puede continuar usando su flujo nativo sin escribir sintesis/, dado que el esquema documentado (CTX-6) estipula colecciones separadas, no alterando la estructura requerida de actas/.

Opinión sobre Dudas del Implementador

D1: Tu sospecha es totalmente correcta. Forzar application/json con valores string gigantes causa que el LLM cometa frecuentemente errores de escape (comillas internas en la transcripción), rompiendo el parseo. Apoya la decisión de separar las llamadas. D2: Es indispensable loggear usageMetadata. Sin él, operarás a ciegas sobre la distribución del tamaño de las respuestas y no podrás calcular el impacto financiero de la feature ni diagnosticar truncamientos silenciosos futuros. D3: Sí es un riesgo inaceptable. Duplicar o triplicar el token out por acta sin cobrárselo al usuario destruye la unidad económica. El diseño DEBE incluir un flag opcional (generarSintesis: boolean false por defecto) habilitable solo por requerimiento del usuario. D4: La heurística (CTX-5) inspecciona el string resumen basándose en silenceKeywords. Si el modelo responde, su resumen para un audio mudo seguirá utilizando la misma semántica (ej. "No hay contenido audible"). La heurística resistirá sin cambios estructurales inmediatos.

VEREDICTO GLOBAL
APROBADO CON CAMBIOS.

Cambios EXACTOS e indispensables para su paso a implementación:

1. Separación de llamadas (Rechazo de C1): Modificar el backend para realizar DOS llamadas a la API de Gemini:
   - Llamada síncrona 1: Prompt actual (Acta), maxTokens=4096, responseMimeType="application/json". Bloquea y responde el 201 al frontend.
   - Llamada asíncrona 2 (Background no bloqueante): Nuevo Prompt solo-transcripción y análisis, pidiendo text/plain o texto crudo, maxTokens=65536. Escribe exclusivamente a sintesis/{id}.
2. Rechazo de C3 (Reintento secuencial): Eliminar el bloque de reintento "MAX_TOKENS". La resiliencia se logra mediante el desacople de las llamadas en el paso 1.
3. Payload del Endpoint: Retornar explícitamente en el 201 Created únicamente la estructura del Acta, descartando de la respuesta HTTP los campos asíncronos en procesamiento.
4. Flag de Costo (Resolución de D3): Agregar un parámetro opcional generarSintesis: boolean (default false) en el payload del POST para evitar disparar el costo masivo de output tokens en todas las actas automáticamente.

---

## 2. Validación anti-bluff del Ingeniero (07-07-2026)

Checklist del contrato (skill `auditor_externo`), verificado contra el código real:

| Verificación | Método | Resultado |
|---|---|---|
| Cita "JSON.parse (línea 109)" | `grep -n "JSON.parse" actas.ts` | Real: **línea 111**, contenido exacto. Deriva de 2 líneas = tolerable (±1–3), NO es bluff. ✅ |
| Premisa "no se inspecciona finishReason" | `grep -n "finishReason" actas.ts` | 0 ocurrencias. Premisa correcta. ✅ |
| Aritmética C2 (65536 tokens ≈ ~260k chars) | ejecución python | 65536×4 = 262.144. ✅ |
| Aritmética Q4 (110k chars ≈ 27.500 tokens) | ejecución python | 110000/4 = 27.500. ✅ |
| Aritmética C6 (800k chars < 1 MiB) | ejecución python con texto español típico (~5% chars de 2 bytes) | 882.051 bytes < 1.048.576; margen real ~166 KB (auditor estimó ~200 KB — direccionalmente correcto, sigue siendo seguro). ✅ |
| Q1–Q4 con recomendación única | lectura | Sí, sin "depende". ✅ |
| Traza Q4 con estado final campo a campo | lectura | Presente y coherente con CTX-3/CTX-4/C4/C6. ✅ |
| T1–T5 refutadas con evidencia | lectura | Presentes; T1/T4 se apoyan en el rediseño exigido (consistente con el veredicto). ✅ |
| Verdicto por claim | lectura | C1 DÉBIL, C2 SÓLIDO, C3 DÉBIL, C4–C6 SÓLIDO. Completo. ✅ |

**Resultado: auditoría VÁLIDA.**

## 3. Dictamen final de la ronda

**APROBADO CON CAMBIOS** → se implementa CON los cambios (regla del ciclo). Diseño final vinculante para MT-02:

1. **Dos llamadas**: llamada 1 síncrona = flujo actual intacto (`ACTA_PROMPT`, 4096 tokens, JSON) → responde `201` solo con el acta; llamada 2 en background no bloqueante (reutilizando el `fileUri` ya subido a la File API) = prompt nuevo de transcripción+análisis, **text/plain**, 65536 tokens → escribe solo `sintesis/{id}`.
2. **Sin reintento MAX_TOKENS** (C3 rechazado); resiliencia por desacople.
3. **C4, C5 y C6 vigentes**: destructuring defensivo antes del spread; sin cambio de schema; truncado a 800k chars con sufijo.
4. **Flag `generarSintesis: boolean` (default `false`)** en el body del POST.
5. **Logging de `usageMetadata`** (D2: el auditor lo declara indispensable; se adopta).

**Interpretaciones declaradas por el Ingeniero** (el auditor las dejó abiertas; se someterán a la auditoría de código de la ronda siguiente):

- **I-1:** "text/plain o texto crudo" para la llamada 2, que debe producir 4 campos (1 string largo + 1 string + 2 arrays): se implementa como texto plano con delimitadores de sección fijos (`===TRANSCRIPCION===`, `===ANALISIS_PROFUNDO===`, `===PREGUNTAS_SIN_RESOLVER===`, `===TEMAS_CLAVE===`) parseados por código. Respeta la razón del rechazo de C1 (nada de JSON con strings kilométricos) y puebla el contrato de `sintesis/` completo.
- **I-2:** El "fire-and-forget" llevará `.catch` explícito con `log.error` (un promise rejection sin manejar tumbaría el proceso Node) y usará el `idToken` del request original (vigencia ~1h ≫ duración de la tarea).
- **I-3:** El flag default `false` implica que el frontend Web deberá enviar `generarSintesis: true` para activar la feature → micro-tarea propia de frontend (MT-04), fuera del alcance de MT-02 (backend). Las pruebas de MT-02 usan el flag explícito.
