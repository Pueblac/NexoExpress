# Expediente 2026-07-14_robustez_pipeline — Respuesta de revisión de DISEÑO (ronda 1)

**Auditor:** Gemini 3.1 Pro High (conversación nueva, con inicialización de identidad)
**Recibida:** 14-07-2026, pegada por el Director (pegado aplanado; texto literal, tabla/encabezados reconstruidos sin alterar redacción).
**Veredicto global:** APROBADO CON CAMBIOS (3 cambios exactos)
**Validación anti-bluff:** ver ANEXO — VÁLIDA con OBS-1 (refutación de T2 incorrecta; reconciliación incorporada a la spec, sin ronda nueva).

---

# 1. Tabla de Claims (C1..C6)

**C1 - Guard de audio mudo — DÉBIL (Requiere cambio).** CLAIM: Guard con MIN_AUDIO_BPS en 500 B/s previene gastar tokens. EVIDENCIA: CTX-1: "Silencio real ... ≈ 253 B/s ... Voz en Opus produce típicamente ≥ 2.000-4.000 B/s". TRAZA: Una reunión de 60 minutos con solo 5 minutos de voz genera: (300s × 3000 B/s) + (3300s × 250 B/s) = 900.000 + 825.000 = 1.725.000 B. Promedio: 479 B/s. El umbral propuesto de 500 rechazaría reuniones legítimas con largas pausas, causando falsos positivos destructivos. CAMBIO: Bajar MIN_AUDIO_BPS a 300 B/s.

**C2 - Centinelas anti-confabulación — SÓLIDO.** CLAIM: Añadir reglas de audibilidad deterministas con prohibición de inventar. EVIDENCIA: CTX-4: Heurística downstream looksEmpty, sin instrucciones ante silencio. CTX-1: "CONFABULÓ actas ... con acuerdos inventados". TRAZA: La regla dura fuerza los arrays vacíos y el texto estricto. Esto se alinea matemáticamente con looksEmpty (participantes.length <= 1 y match del texto centinela), cerrando la brecha por la cual el modelo se inventaba datos al verse sin directrices sobre el silencio.

**C3 - thinkingBudget acotado a 0 — DÉBIL (Requiere cambio).** CLAIM: thinkingBudget: 0 en síntesis libera presupuesto y baja latencia. EVIDENCIA: CTX-1: "62.912 de 65.536 tokens ... en razonamiento". CTX-5: "ANALISIS_PROFUNDO". TRAZA: Reducir a 0 detiene la confabulación masiva, pero destruye la capacidad reflexiva necesaria para la sección de ANALISIS_PROFUNDO. CAMBIO: Usar thinkingBudget: 4096. Asigna un techo rígido que impide agotar los 65.536 tokens limitando el gasto interno sin deshabilitar por completo el razonamiento analítico.

**C4 - Timeout proporcional — SÓLIDO.** CLAIM: clamp(40_000, 40_000 + msDuration/10, 600_000). EVIDENCIA: CTX-3: "Techo fijo: 20×2 s = 40 s". TRAZA: Un audio de 30 minutos (1.800.000 ms) tendrá 40_000 + 180_000 = 220_000 ms (3,6 min). Esto previene que la aplicación haga timeout prematuro durante el procesamiento del servidor de Gemini File API de archivos largos, manteniendo un techo seguro (10 min).

**C5 - UX de expectativa — SÓLIDO.** CLAIM: Texto secundario permanente durante isPending. EVIDENCIA: CTX-6: "botón muestra spinner y el estado dice 'Procesando con IA...'". TRAZA: Proveer texto de mitigación reduce el porcentaje de aborto del request por parte del usuario sin alterar el flujo de control backend.

**C6 - Alcance cerrado — SÓLIDO.** CLAIM: Sin cambios en schemas ni OpenAPI. EVIDENCIA: "Sin schema, reglas, openapi.yaml". TRAZA: Todos los cambios propuestos (cálculos en handler, prompt, config de llamada Gemini, mensajes de UI) se ejecutan dentro del espacio de la implementación existente sin tocar contratos externos.

# 2. Respuestas a Preguntas de Control (Q1..Q4)

**Q1: Umbral: 300 B/s.** Justificación: El silencio puro mide ~250 B/s (CTX-1). Un valor de 500 B/s rechazaría reuniones de 1 hora donde solo se habla intermitentemente por menos del 15% del tiempo (promediando < 500 B/s global), resultando en un falso positivo donde el usuario pierde su grabación irremediablemente. 300 B/s da 50 B/s de margen sobre el piso absoluto de silencio para ruido electrónico residual, minimizando los falsos positivos (solo se pierde el audio si genuinamente nadie hizo un sonido inteligible por el 98% de la duración). El trade-off compensa gastar algunos tokens de API en un falso negativo (audio de puro ruido blanco) antes que causar pérdida de datos al usuario.

**Q2: Recomendación: 4096.** Justificación: La síntesis genera 4 secciones (CTX-5). Tres de ellas (PREGUNTAS_SIN_RESOLVER, ANALISIS_PROFUNDO, TEMAS_CLAVE) demandan inferencia sobre el contexto de la transcripción. 0 suprime esta capacidad de modelo 2.5-flash mermando drásticamente el valor de estas secciones. 4096 tokens de techo bloquea rigurosamente el bucle infinito observado (62.912 tokens en CTX-1) salvando ~61.440 tokens limpios para asegurar que la transcripción en sí misma no tope con maxOutputTokens.

**Q3 (texto exacto de la regla de audibilidad):**

> Si y solo si a lo largo de TODA la grabación no logras detectar ninguna voz humana inteligible (es decir, el audio es únicamente silencio continuo o ruidos de fondo de principio a fin), DEBES generar la salida con título exacto "Reunión sin contenido audible", iniciar el resumen obligatoriamente con la frase "No se detectó contenido audible.", y fijar participantes como un arreglo vacío []. Esta regla tiene prioridad absoluta. Sin embargo, si detectas AL MENOS UN fragmento de conversación humana, omite esta regla, ignora los silencios, redacta el acta y extrae el contenido normalmente en el idioma en que se realizó la reunión. PROHIBIDO inventar o inferir contenido que no esté en el audio; ante duda, declara la ausencia.

**Q4: Traza Completa (Reunión REAL 60 min, 130.000 chars de transcripción esperada):**
1. Guard: Audio 60 min (3.600.000 ms) en voz normal (~3.000 B/s). audioSizeBytes = 10.800.000 bytes. bytesPerSec = 3000 B/s. Al ser 3000 >= 300, el request supera la validación y avanza sin emitir el 422.
2. Timeout aplicado: clamp(40000, 40000 + 3600000 / 10, 600000) = clamp(40000, 400000, 600000). El maxWaitMs será de 400.000 ms (6,67 minutos).
3. Tokens estimados síntesis (Q2 = 4096): 130.000 chars equivalen aproximadamente a 32.500 tokens de texto. Output total = 32.500 (texto) + 4.096 (thoughts) = 36.596 tokens. Esto pasa el límite holgadamente (< 65.536).
4. Estado final actas/{id}: Persistido correctamente; request retorna 201 al frontend.
5. Estado final sintesis/{id}: Creado en background con éxito total. Tamaño ~130 KB (muy por debajo del límite teórico de Firebase Firestore 1 MB, no aplica truncado de 800 KB).
6. **Riesgo residual más grande:** La llamada 1 (el Acta JSON síncrona, procesada durante la conexión HTTP abierta) consumirá la latencia nativa de inferencia del LLM procesando la ventana de 1 hora de audio (fácilmente 30 a 90 segundos). Si el servidor Express o el Reverse Proxy (Nginx/Cloudflare) tienen un timeout de lectura HTTP predeterminado bajo (ej. 60s), se cortará la conexión con el cliente (504 Gateway Timeout o Socket Hang Up) antes de poder responder 201, a pesar de que el proceso del LLM se complete.

# 3. Refutación de Trampas (T1..T5)

- **T1 — Falso positivo del guard:** Neutralizada por la imposición del cambio de MIN_AUDIO_BPS de 500 a 300 (según C1/Q1) y por tratarse de un promedio aritmético. Si alguien habla muy suavemente y produce picos de 600 B/s intercalados con silencio a 250 B/s, la media se estabilizará muy por encima de los 300 B/s, garantizando que el audio pase. El diseño modificado condena exclusivamente micrófonos totalmente silenciados a nivel hardware o software.
- **T2 — Doble mecanismo inconsistente:** Neutralizada por la redacción del prompt exacto (Q3). El texto fuerza determinísticamente que participantes: [] y el texto estricto "No se detectó contenido audible.". La lógica de la heurística (participantes.length <= 1 && resumen.toLowerCase().includes("no se ... audible")) encajará siempre como un guante en la salida determinista. No existen contradicciones.
- **T3 — Costo de calidad del thinking:** Neutralizada por el presupuesto forzado a 4096 (Q2) en vez del 0 propuesto. El LLM dispondrá de espacio suficiente para su cadena de razonamiento y diarización (una ventana típica de CoT consume entre 1k a 3k tokens en gemini-2.5-flash). Se preserva la detección de lapsus y matices, impidiendo únicamente la alucinación descontrolada de 62k tokens.
- **T4 — Reunión de 2+ horas:** El pipeline reventará primero en el límite maxOutputTokens: 65536 de la Llamada 2 (Síntesis background). Una transcripción de 2 horas (260.000+ chars) con los thoughts de 4096 tokens superará invariablemente la cuota. Sin embargo, el diseño degrada con gracia: la Llamada 1 (acta) genera un JSON que extrae un resumen y consume pocos tokens de salida. Esto permite devolver 201 y guardar el acta estructurada exitosamente. La síntesis en background fallará ruidosamente en el log, pero los datos primordiales del acta prevalecen.
- **T5 — Mensaje de espera fuera de lugar:** Neutralizada por el ciclo de vida intrínseco de react-query o estados atados al scope de la promesa POST. Si processAudio.isPending es exclusivo del mutation de procesamiento del archivo y el handler rechaza 422 o responde 201/500, el estado muta a false. El DOM se desmontará automáticamente cuando la mutación se resuelva o rechace.

# 4. Opinión Fundada (D1..D4)

- **D1 (Umbral BPS):** 500 B/s es imprudente y punitivo. Como se demostró, asume una densidad de voz constante. Recomiendo 300 B/s como margen estricto sobre el ruido de base del Opus DTX sin amenazar casos válidos.
- **D2 (422 vs Warning):** Confirmado rechazo 422. Los silencios absolutos consumen facturación en Gemini File API e Inferencia por un JSON de basura que ensucia la DB. El bloqueo duro con error amigable informa de inmediato al usuario que su hardware falló, ahorrándole expectativas erróneas.
- **D3 (Budget en Síntesis):** Imponer 0 es un paso atrás en la calidad. El budget fijo de 4096 protege ambos frentes: evita que el pipeline estalle por bucles reflexivos y conserva los superpoderes analíticos del modelo para extraer los matices y temas clave.
- **D4 (Fórmula Timeout):** El factor msDuration/10 es seguro y acertado bajo la matemática presentada, con el clamp de techo de 10 min salvaguardando el thread del backend de quedarse zombie en la eternidad si File API cuelga.

# 5. Veredicto Global

**APROBADO CON CAMBIOS**

Cambios EXACTOS requeridos para proceder a implementación:
1. En C1 (Guard), reemplazar MIN_AUDIO_BPS default de 500 B/s por **300 B/s**.
2. En C3 (Config LLM), reemplazar thinkingBudget: 0 por **thinkingBudget: 4096** en la llamada de la síntesis.
3. Inyectar el **texto literal provisto en la respuesta Q3** en el prompt de Acta y Síntesis para robustecer el centinela sin conflicto con la detección de idioma.

---
---

# ANEXO — Validación anti-bluff del Arquitecto (14-07-2026)

**Checklist del contrato:** verdicto por claim (2 DÉBIL con cambio, 4 SÓLIDO) ✅ · Q1..Q4 con recomendación única (Q3 con texto exacto, Q4 con traza y riesgo residual) ✅ · T1..T5 tratadas ✅ · D1..D4 opinadas ✅ · cambios exactos enumerados ✅.

**Aritmética verificada por ejecución (no de memoria):**
- Traza de C1: (300×3000 + 3300×250)/3600 = **479,17 B/s** ✅ — el falso positivo del umbral 500 es real y la corrección a 300 B/s queda justificada con datos.
- Traza de Q4: 130.000/4 = 32.500 tokens; 32.500 + 4.096 = **36.596** ✅.
- Riesgo residual de Q4 (timeout HTTP de proxy en la llamada síncrona con audios largos): pertinente para despliegue futuro; en dev local no hay proxy. **Registrado como riesgo residual del ciclo** (familia H5, se retoma al desplegar).

**OBS-1 — Refutación de T2 INCORRECTA (verificado contra el código real):** el auditor afirma que el resumen centinela "No se detectó contenido audible." matchea la heurística, citando una keyword `"no se ... audible"` que NO existe. Las keywords reales (`actas.ts:265`) son `["no se pudo","no audible","no hay audio","sin contenido","silencio"]` y **ninguna es substring del resumen centinela** (verificado por ejecución). La trampa T2 aplicaba parcialmente. **Resolución sin ronda nueva:** la divergencia queda cerrada por el propio diseño aprobado — C2 ya mandata sumar el *match exacto del título centinela* a `looksEmpty` — y la spec de MT-R2 lo hará explícito con doble vía: (a) `silenceKeywords` incorpora `"no se detectó"`, (b) `looksEmpty` también dispara con `titulo === "Reunión sin contenido audible"`. No se re-litiga el veredicto: los 3 cambios mandatados son sólidos e independientes de esta imprecisión.

**Veredicto de la validación: RESPUESTA VÁLIDA — APROBADO CON CAMBIOS aceptado.** Diseño final: guard 422 con **MIN_AUDIO_BPS=300** (env-configurable, `msDuration>=5000`); centinelas con el **texto Q3 literal** en ambos prompts (+ adaptación de secciones para SINTESIS_PROMPT: `[SIN CONTENIDO AUDIBLE]` en TRANSCRIPCION) y `looksEmpty` reconciliada (OBS-1); **thinkingBudget: 4096** solo en síntesis; timeout `clamp(40s, 40s + msDuration/10, 600s)`; UX de espera. Pendiente: GATE G1 del Director → F3 (specs).