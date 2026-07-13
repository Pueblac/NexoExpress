# Expediente 2026-07-09_mt04_toggle_sintesis — Evidencia F5 parte 2 (E2E real)

**Fecha de las pruebas:** 11-07-2026, ~12:30 hora local (16:30 UTC), ejecutadas por el Director en Chrome/Linux contra la app local (`dev.sh`) y Firestore real del proyecto `actaexpress`.
**Fuentes:** logs literales del api-server (pegados por el Director) + lecturas directas de Firestore vía REST (ejecutadas por el Arquitecto) + testimonio del Director sobre el contenido real de la grabación.

---

## 1. DoD de MT-04b — estado

| Criterio | Estado | Evidencia |
|---|---|---|
| Toggle ON → POST lleva `generarSintesis: true` y `sintesis/{actaId}` se puebla | ✅ | Log req id:3 (12:30:46): POST → 201 → tarea background del MISMO request (`req.id: 3`) escribe `sintesis/XSj4f2aKhWEICLx6qRC3` a las 12:34:58 (`transcripcionChars: 230`). Lectura Firestore confirma el documento con transcripción, análisis (863 chars) y temas. |
| Toggle OFF → sin síntesis | ✅ | Log req id:7 (12:32:22): POST → 201, NINGUNA línea de síntesis para ese request. Lectura Firestore: `sintesis/x55aAPUVthWMoBMxaQQb` → NOT_FOUND. Colección `sintesis/` completa contiene solo el doc del acta ON. |
| Multi-grabación en la misma carga (regresión B1) | ✅ | Dos POST procesados en la misma sesión de página (id:3 y id:7, con 95s de diferencia); ambos 201, ambas actas en Firestore. |
| Persistencia del toggle tras reload | ⏳ PENDIENTE | El Director hará las pruebas restantes (incluye paso de reload). Código verificado en F5 parte 1. |
| Render real del switch | ✅ | Screenshot del Director: switch "Análisis profundo / Transcripción completa y análisis (tarda más)" visible bajo el timer, encendido. Vite optimizó `@radix-ui/react-switch` y `react-label` al vuelo (log 12:28:30) — primera vez que se usan: confirma que el componente es el nuevo. |

**Veredicto parcial F5-2: la plomería de MT-04 (flag end-to-end) FUNCIONA.** Falta solo la confirmación visual de persistencia (pruebas restantes del Director).

---

## 2. HALLAZGO H1 — Doble alucinación sobre el mismo audio (fuera del alcance de MT-04, ciclo propio)

**Ground truth (testimonio del Director):** la grabación de las 12:30 decía que a la 1:00 pm empezaban las clases de artes marciales, que había que ordenar a las 12:30 para salir a las 12:50 a practicar; personas: César Puebla (desarrollador y practicante) y Patricio Córdova (profesor de kickboxing y Sanda). Nada de proyectos.

**Lo que produjo Gemini sobre ese audio (`files/7rfhklraeby5`):**
- Llamada ACTA: "Actualización de Proyectos Semanal y Quincenal" — proyecto de la semana entregado, quincena en proceso, reunión de seguimiento. **Inventado.**
- Llamada SÍNTESIS (mismo `fileUri`, verificado por `promptTokensDetails.AUDIO = 1358` idéntico en ambas llamadas): "Hola. Eh, estoy en la sala, pero no hay nadie... La reunión es a las 11 y son las 11:05". **Inventado, y distinto al del acta.**

**Causa raíz probable — audio casi mudo:** `msDuration: 42507` con `audioSizeKB: 10.5` ≈ **2 kbps efectivos** (Opus/WebM con voz normal produce ~25-35 kbps → ~130-180 KB para 42s). El códec comprimió a casi nada porque apenas había señal — captura de micrófono fallida/muteada durante las pruebas de compartir pantalla. La grabación 2 (36s, 8.9KB) tuvo el mismo perfil y el acta la declaró correctamente "sin contenido audible". Con basura de entrada, cada llamada confabuló una reunión plausible distinta (temperature 0.2 no lo impide; llamadas stateless — **no hay contexto de actas previas involucrado**, el modelo solo ve audio + prompt).

**Defecto expuesto:** la heurística anti-silencio (`participantes <= 1` + keywords en el resumen) es **bypasseada por alucinación**: si el modelo inventa contenido plausible en vez de declarar silencio, nada lo detecta. Señal disponible y desaprovechada: el ratio bytes/segundo del audio (10.5KB/42s es detectable server-side ANTES de llamar a Gemini).

**Propuesta para ciclo propio (no tomar sin F0..F7):** (a) guard server-side por bitrate mínimo (rechazo o warning "posible micrófono mudo" antes de gastar tokens); (b) endurecer ACTA_PROMPT y SINTESIS_PROMPT: "si el audio es ininteligible o casi mudo, decláralo explícitamente; PROHIBIDO inferir contenido no audible"; (c) misma familia que el pendiente "actas en inglés salen en español" (fidelidad del modelo) — candidato a ciclo conjunto.

---

## 3. HALLAZGO H2 — El "thinking" devora el presupuesto de la síntesis (ciclo propio)

Log de la síntesis (req id:3, 12:34:58): `totalTokenCount: 64897` de los cuales **`thoughtsTokenCount: 62912`** y solo `candidatesTokenCount: 410`. Es decir: el 97% del presupuesto (`maxOutputTokens: 65536`, que en gemini-2.5-flash INCLUYE los thoughts) se fue en razonamiento interno, con `finishReason: STOP` rozando el techo. Consecuencias:
- **Latencia**: ~4 minutos (12:30:57 → 12:34:58) para transcribir 42s de audio.
- **Riesgo real de MAX_TOKENS en reuniones reales**: una transcripción larga + 60k de thoughts NO cabe — la síntesis se truncaría (y el diseño vigente, correctamente, no reintenta).

**Propuesta para ciclo propio:** fijar `thinkingConfig: { thinkingBudget: 0 }` (o un tope bajo) en la llamada de síntesis — transcribir no requiere razonamiento extendido — liberando el presupuesto completo para el texto. Verificar con reunión real de >30 min.

---

## 4. HALLAZGO H3 — Captura de audio de sistema en Linux (limitación de plataforma, documentar)

Confirmado en las pruebas: en Chrome/Linux el audio del sistema SOLO se entrega compartiendo una **pestaña** con "Compartir también el audio de la pestaña"; "Ventana" y "Toda la pantalla" no dan audio → fallback a micrófono (y si el sonido va por audífonos, no se captura nada → "Reunión sin contenido audible"). Uso recomendado con Teams/Meet: abrir la reunión en pestaña de Chrome y compartir esa pestaña con audio. **Sobre avisos:** ActaExpress no notifica nada a ningún participante (no se integra con las plataformas de reunión); el único indicador es la barra local de Chrome, visible solo para quien graba. Requisito de independencia del Director: satisfecho sin cambios. La gobernanza de consentimiento queda como decisión del Director (pendiente de privacidad ya abierto).

---

## 4a. Dirección de producto del Director para H3 (12-07-2026)

El Director define el rumbo del futuro ciclo de captura: **selector explícito de modo antes de grabar** — "Reunión virtual" (audio de pestaña + micrófono mezclados, como ya hace `mixAudioStreams`) vs **"Reunión presencial / sonido ambiente"** (directo a micrófono, sin diálogo de compartir). Hoy el modo ambiente existe solo como fallback oculto (cancelar el diálogo); debe ser una opción de primera clase. Queda como ciclo propio (F0 pendiente de priorización), fusionado con H3.

## 4b. ADENDA — Segunda ronda de pruebas (12-07-2026, ~17:46 local)

Grabación real del Director: almuerzo a las 18h, hervir verduras y luego la carne; personas: César Puebla y Gabriela Quijada. Ambas pruebas con opción **"Ventana"** (eligiendo la ventana de Chrome del propio ActaExpressWeb).

| Prueba | Acta | Síntesis |
|---|---|---|
| Toggle ON (17:46) | `8XKYxvz3Vf7zJ0EUTPIw` "Saludo inicial de reunión" | ✅ EXISTE — transcripción literal: `"Participante 1: Silencio."` (creada 21:46:42Z) |
| Toggle OFF (17:48) | `45YLu3pJe9kggycKMNMU` "Reunión de Trabajo General" | ✅ NO existe (NOT_FOUND) |

**Flag re-verificado por segundo día consecutivo** (y multi-grabación ON→OFF en la misma sesión, de nuevo sin B1).

**Diagnóstico de captura refinado:** la transcripción "Silencio." es la prueba directa de que el audio que llega a Gemini está VACÍO. Dos causas apiladas: (1) "Ventana" jamás entrega audio de sistema en Chrome/Linux (H3) — y además la ventana compartida fue la del propio ActaExpress, que no emite sonido; (2) el fallback a micrófono capturó silencio → **problema de micrófono a nivel de SO/Chrome** (dispositivo de entrada muteado o incorrecto), no de la app. Pendiente: prueba de aislamiento de micrófono y prueba de pestaña con audio.

**Nota sobre H1:** en esta ronda Gemini NO confabuló (declaró "saludo inicial" / "sin temas" honestamente) — la alucinación del 11-07 es intermitente, lo que confirma que el guard de bitrate + endurecimiento de prompts (H1) sigue siendo necesario: no se puede confiar en que el modelo siempre confiese el silencio.

**CAUSA RAÍZ CONFIRMADA (12-07, Director):** el micrófono estaba APAGADO a nivel de sistema operativo. Cadena completa demostrada: mic muteado → captura de silencio (~2 kbps) → Gemini recibe audio vacío → a veces lo confiesa ("Silencio."), a veces confabula (actas del 11-07). La app nunca advirtió que no entraba señal en 4 grabaciones consecutivas.

## 4c. HALLAZGO H4 — Detector de señal de micrófono en el cliente (ciclo propio, UX del Director)

Propuesta del Director (12-07): la app debe detectar micrófono muerto/muteado y avisar en el momento — *"hey, tu micrófono está apagado, ¿estás seguro de que quieres que se mantenga así?"*. Viable con lo ya existente: el hook ya crea `AudioContext` para mezclar; un `AnalyserNode` midiendo nivel RMS de la entrada puede disparar un aviso al iniciar la grabación (y/o mantener un indicador de nivel en vivo junto al timer). Complementa al guard server-side de bitrate (H1): H4 previene ANTES de grabar; H1 protege el gasto de tokens si igual llega audio vacío. Candidato natural a fusionarse con el ciclo H3 (selector de modo de captura) en un solo ciclo de "captura confiable".

## 4d. ADENDA — Tercera ronda (12-07-2026, tarde): PRIMERA ACTA FIEL

Con el micrófono del SO ya encendido, prueba presencial (Cancelar → modo "Solo micrófono"), toggle OFF (modo rápido), ~47s simulando reunión de coordinación con 5 participantes ficticios. **Resultado: acta "Revisión de Actividades y Coordinación de Pendientes" EXACTAMENTE fiel a lo hablado** (testimonio del Director): 5 participantes correctos (María González, Juan Pérez, Ana Rojas, Carlos Muñoz, César Puebla), acuerdos y pendientes con responsables y fechas correctos. El pipeline completo funciona cuando entra señal de audio real.

Observación de UX del Director confirmada: llegar al modo micrófono vía "Cancelar" es poco intuitivo → refuerza H3/H4 (selector explícito).

## 4e. HALLAZGO H5 — Expectativas de espera y riesgos con audios largos (ciclo propio)

Pregunta del Director: grabación de 47s tardó ~similar en entregar el acta — ¿1 hora tardará 1 hora? **No — la latencia NO escala lineal** (desglose del log del 11-07: ~11s totales = ~3s subida + ~0.4s file ACTIVE + ~8s inferencia; la inferencia escala sублineal con los tokens de audio (32 tok/s) → 1h ≈ 115k tokens ≈ decenas de segundos, más subida de un archivo grande: estimado total minutos, no horas). PERO la inspección del código expone 2 riesgos reales para audios largos + 1 brecha de UX:

1. **Timeout duro en `waitForFileActive` (actas.ts:108-117):** sondea 20×2s = máx 40s esperando que el archivo esté ACTIVE en la File API. Un audio de 1h puede tardar más de 40s en procesarse → "Timeout: el archivo tardó demasiado" y el usuario pierde el acta. Fix candidato: timeout proporcional a la duración del audio.
2. **Procesamiento atado a la pestaña:** el POST lo hace el navegador; si el usuario cierra la pestaña durante "Procesando con IA...", el acta se pierde. Para reuniones de 1h el riesgo es real. (Solución de fondo — jobs server-side — es Fase posterior; mitigación barata: advertir "no cierres esta pestaña".)
3. **UX de expectativa (propuesta del Director):** indicar como Gemini/NotebookLM que "esto puede tardar unos minutos, puedes seguir haciendo otras cosas"; y la síntesis en background hoy es INVISIBLE — no hay UI que muestre cuándo terminó ni dónde verla (solo el toast inicial). Con H2 (`thinkingBudget: 0`) la síntesis además bajaría de ~4 min a decenas de segundos.

## 4f. HALLAZGO H6 — Resiliencia de grabación (ciclo propio, dirección del Director 13-07)

Preocupación del Director: caída de luz/internet o cierre de pestaña a mitad de una reunión pierde TODO (hoy el audio vive solo en memoria del navegador; `audioStoragePath: null` por diseño). Propone autoguardado cada 1 minuto y evaluar transcripción incremental por trozos con unión posterior.

**Evaluación del Arquitecto:**
- **Fase 1 (alto valor / bajo costo):** persistir los chunks (ya existen: `mediaRecorder.start(1000)`) en IndexedDB cada ~1 min + flujo de recuperación al reabrir ("tienes una grabación sin procesar, ¿procesarla?"). Solo frontend; sin Storage ni billing.
- **Transcripción incremental por minuto:** posible pero con costos: chunks WebM no autónomos (re-encapsulado), palabras cortadas en bordes, pérdida de continuidad de hablantes. NO recomendada como parche; la vía correcta es streaming (Gemini Live API) en Fase 3.
- **Aclaración registrada:** el timeout de `waitForFileActive` NO es cola del tier gratuito — es procesamiento del archivo en la File API (ocurre igual pagando); el fix es timeout proporcional (H5.1). El tier pagado/Vertex se justifica por privacidad (pendiente de gobernanza #4) y rate limits, y depende del billing (pendiente #3).

## 4g. ADENDA FINAL — Cuarta ronda (13-07-2026): TRANSCRIPCIÓN FIEL CON GROUND TRUTH — F5 CERRADA

Prueba con **guion escrito leído en voz alta** (~77s, toggle ON, modo micrófono presencial). Acta `g1oWHvziNoalE9ESxepg` (10:40:20Z) + síntesis creada a las 10:40:30Z.

- **Acta:** fiel al guion (5 participantes correctos, acuerdos/pendientes con responsables y plazos correctos). Confirmado por el Director contra su texto original.
- **Transcripción (1.250 chars, leída de Firestore):** fiel línea a línea, con diarización correcta (asigna parlamentos a María González, Juan Pérez, Ana Rojas). **Prueba de oro de que transcribe el audio real y no reconstruye:** capturó un lapsus del Director al leer ("¿Cómo va la actualización con la con el tablero de indicadores? Patricio... perdón, Juan") que NO está en el guion — y el análisis profundo incluso lo comenta como matiz. Preguntas sin resolver pertinentes (ej. rol de los participantes que no intervinieron).
- **Latencias medidas:** acta ~10s tras detener (audio 77s); **síntesis solo +10s después del acta** — vs los ~4 min del 11-07. Conclusión para H2: el gasto de thinking es VARIABLE e impredecible (62.912 tokens un día, mínimo al siguiente); el cap de `thinkingBudget` sigue recomendado para acotar el peor caso, no el promedio.

**F5 CERRADA.** DoD de la meta MT-04 ("request real del frontend con el flag y síntesis generada end-to-end") CUMPLIDO con evidencia literal. Punto menor pendiente de confirmación visual del Director: persistencia del toggle tras reload (respaldada por código: `ProtectedRoute` garantiza `user` resuelto al montar Home — App.tsx:41).

## 5. Estado del ciclo (actualizado 13-07-2026)

- **F5 CERRADA** (§4g): flag E2E verificado ambos sentidos, transcripción fiel con ground truth, latencias medidas. Persistencia tras reload: respaldada por código, confirmación visual pendiente (paso 1 del AVISO F6).
- **F6 EN CURSO:** `prompt_auditoria_ronda1.md` (tanda MT-04a+b, diff íntegro incrustado) listo, esperando transporte del Director a Gemini.
- **Checkpoint autorizado por el Director (13-07):** documentación y código pusheados a sus repos ANTES del veredicto F6 — decisión explícita del Director ("documenta todo y pushea"); el ciclo queda ABIERTO y el diff auditable quedó congelado dentro del prompt F6. El cierre formal (F7) sigue condicionado al APROBADO del Auditor + gate G2.
- Hallazgos H1–H6: registrados con ciclos propios candidatos; no bloquean MT-04.
