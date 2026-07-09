# Expediente 2026-07-08_metodologia_v2 — Respuesta de revisión de DISEÑO (ronda 1)

**Auditor:** Gemini 3.1 Pro High (conversación nueva)
**Recibida:** 08-07-2026, pegada por el Director en la sesión del Arquitecto (el pegado aplanó el markdown original; el texto es literal, los encabezados se reconstruyeron sin alterar redacción).
**Veredicto global:** APROBADO CON CAMBIOS (5 cambios obligatorios)
**Validación anti-bluff:** ver ANEXO al final de este archivo.

---

# Revisión de Diseño: Metodología v2

## 1. Tabla de Verificación de Claims (C1..C6)

### C1 — El triángulo preserva la regla de oro

- **CLAIM:** Ningún actor valida su propio trabajo con autoridad final; cada producción tiene al menos un verificador distinto.
- **EVIDENCIA:** CTX-2 ("ninguna IA verifica su propio trabajo con autoridad final; el Arquitecto valida a Ingeniero y Auditor; el Auditor valida diseño y código"); CTX-6 ("archivado literal de todo prompt/respuesta ANTES de procesarse, spot-check del Director").
- **TRAZA:** El Arquitecto redacta la spec (F3), el DoD y el prompt de auditoría (F6). En F5, verifica su propia spec evaluando si el código del Ingeniero cumple el DoD que el mismo Arquitecto escribió. Si el Arquitecto olvidó un caso borde, es ciego a él en F5. La verificación recae en el Auditor (F6). Sin embargo, como expone D1, el Arquitecto controla el flujo de F6, decidiendo qué archivos llegan al Auditor. Si el Arquitecto filtra mal, el error pasa al commit.
- **VERDICTO:** DÉBIL. **Cambio requerido:** Imponer un control estructural en F4 y F6: el Ingeniero debe anexar el output de git diff literal en su informe, y el Arquitecto está forzado a adjuntar este diff en el prompt de auditoría sin filtrado.

### C2 — La spec autocontenida es un traspaso suficiente

- **CLAIM:** Un Ingeniero en conversación nueva, solo con el Paquete de Especificación + repo, puede implementar sin heredar contexto, evitando supuestos silenciosos.
- **EVIDENCIA:** CTX-4a ("Paquete de Especificación... autocontenido... contrato... restricciones... DoD ejecutable... protocolo de dudas ('ambigüedad → DETENTE')"), CTX-6 ("conversación nueva por micro-tarea, recibe solo la spec + repo").
- **TRAZA:** El Director abre una nueva sesión para Sonnet, pega la spec_mtNN.md y provee los archivos del repo citados. Al no haber historial previo, Sonnet no puede alucinar requisitos de fases de diseño que no vió. Si el contrato tiene variables sin definir, la regla "ambigüedad → DETENTE" le impide inventar el tipo de dato, forzando la devolución a F3.
- **VERDICTO:** SÓLIDO.

### C3 — El AVISO elimina la ambigüedad de turno

- **CLAIM:** En cualquier corte, el Director sabe qué transportar y a dónde; el receptor detecta enrutamiento erróneo sin leer todo el artefacto.
- **EVIDENCIA:** CTX-5 ("Bloque estándar obligatorio... TURNO DE, DESTINO... cada rol verifica... y rechaza artefactos ajenos").
- **TRAZA:** El Arquitecto emite un artefacto con TURNO DE: AUDITOR. El Director, por error, lo pega en la sesión del Ingeniero. El Ingeniero lee el campo y aborta. El mecanismo de rechazo funciona solo si el Ingeniero sabe que es el Ingeniero. Dado que CTX-6 exige "conversación nueva", si el sistema no inyecta la identidad antes de pegar el artefacto, el LLM no tiene base para rechazar.
- **VERDICTO:** DÉBIL. **Cambio requerido:** El diseño debe exigir que la sesión nueva (Ingeniero/Auditor) sea inicializada con un System Prompt estático de rol de una línea antes de aceptar el primer AVISO.

### C4 — Doble verificación de la implementación

- **CLAIM:** F5 (Arquitecto) y F6 (Auditoría) detectan bluff del Ingeniero o tests falsos antes del commit.
- **EVIDENCIA:** CTX-3 ("F5 VERIFICAR: Arquitecto re-ejecuta el DoD sobre el código real"), CTX-4b ("evidencia literal de cada comando del DoD (sin ella el informe es INVÁLIDO)").
- **TRAZA:** El Ingeniero inventa un output positivo de un test de UI en informe_mtNN.md. En F5, si el Arquitecto solo lee el informe, el bluff pasa. Para "re-ejecutar el DoD sobre el código real" (F5), el Arquitecto (que es un modelo) necesita que los comandos corran. Si el Director no interviene proveyendo la salida real del comando, no hay re-ejecución, solo lectura.
- **VERDICTO:** DÉBIL. **Cambio requerido:** Redefinir F5: la "re-ejecución" exige obligatoriamente que el Director (o un script automático local) corra los comandos del DoD de forma independiente y pase los resultados (stdout/stderr) al Arquitecto.

### C5 — Posponer Modo A es la decisión correcta

- **CLAIM:** Pilotar la v2 exclusivamente en Modo M y exigir ciclo de diseño propio para Modo A es correcto debido a riesgos del orquestador.
- **EVIDENCIA:** CTX-6 ("riesgos de Modo A: el Arquitecto... controlaría además qué ve el Auditor... degeneración a modo chat... gobernanza del tier... pendientes").
- **TRAZA:** Activar Modo A centraliza el prompt engineering de F4 y F6 en el Arquitecto. Sin gobernanza de API ni mecanismo automatizado que asegure que lo enviado a Gemini no fue mutilado por el Arquitecto para pasar rápido, la auditoría adversarial pierde sus colmillos. Aislar el Modo M prueba el modelo de incentivos antes de la automatización.
- **VERDICTO:** SÓLIDO.

### C6 — La transición v1→v2 no deja estados ambiguos

- **CLAIM:** No hay dos metodologías vigentes simultáneamente ni riesgo de ejecutar ciclos equivocados.
- **EVIDENCIA:** CTX-7 ("tras adoptar v2, una micro-tarea posterior (MT-02) elimina referencias huérfanas al ciclo v1"), CTX-8 ("v2 solo entra en vigor con tu APROBADO... Piloto: MT-04").
- **TRAZA:** Se aprueba v2. Inicia el piloto en MT-04. Durante la ejecución de MT-04 (y antes de la posterior MT-02), los documentos operativos (skills, README) del repositorio siguen dictando reglas de v1. Cualquier sub-agente o humano que consulte la documentación durante MT-04 operará con instrucciones de v1, induciendo fallos sistémicos.
- **VERDICTO:** RECHAZADO. **Cambio requerido:** MT-02 (limpieza documental) es un prerrequisito bloqueante. Debe reetiquetarse como MT-00 y ejecutarse antes del piloto (MT-04), no "posteriormente".

## 2. Respuestas a Preguntas de Control (Q1..Q4)

### Q1: ¿F5 debe ser obligatoria en el 100% de las micro-tareas, o muestreada?

**Recomendación:** Obligatoria en el 100% de las micro-tareas.
**Justificación:** El modelo de amenaza es la alucinación de código (falsos positivos en el DoD) por parte del Ingeniero en F4. Si F5 se muestrea, un porcentaje de código defectuoso o no compilable salta directo a F6. El Auditor en F6 analiza código y diseño mediante inferencia, no ejecuta tests. Si F5 no filtra fallos de ejecución, errores sintácticos burdos llegarán a G2 (Director), rompiendo la promesa de que la IA entrega ramas "commiteables" (CTX-4b).

### Q2: Campos del AVISO de CTX-5 y dictamen

**Campos actuales:** CICLO, FASE, TURNO DE, ENTREGAR (rutas exactas), DESTINO (dónde pegarlo), ACCIÓN, VUELVE A.
**Dictamen:** FALTA un campo. Para que el Director rote sin leer el artefacto completo, necesita saber qué más transportar aparte de la prosa.
**Campo faltante:** ADJUNTOS_REQUERIDOS. Formato: [Lista separada por comas de archivos del repo, git diffs o "Ninguno"].

### Q3: Protocolo ante duda en mitad de F4

**Recomendación:** Vuelve el turno al Arquitecto con ronda nueva de spec (F3').
**Justificación:** Si el Director interviene con una respuesta puntual a la duda del Ingeniero, se inyectan decisiones de diseño por fuera de los artefactos oficiales de F1 y F3, invalidando la trazabilidad. El Arquitecto ignorará esa decisión en F5 y F6 porque no está en su spec_mtNN.md. El retroceso a F3' mantiene la regla anti-bucle y la integridad del diseño.

### Q4: Traza simbólica completa (MT-04 Piloto en Modo M)

- **F0 PLAN:** Arquitecto formula la necesidad del flag generarSintesis. (GATE G0: Director aprueba).
- **F1 DISEÑO:** Arquitecto genera diseno_mt04.md y prompt_revision_mt04.md.
  - AVISO: TURNO DE: AUDITOR | DESTINO: Chat Gemini Nuevo | ADJUNTOS_REQUERIDOS: diseno_mt04.md | ACCIÓN: Revisar diseño | VUELVE A: Arquitecto (veredicto_diseno_mt04.md)
  - Transporte: Director crea sesión Gemini y pega artefactos.
- **F2 VEREDICTO:** Auditor genera veredicto_diseno_mt04.md. Arquitecto aplica anti-bluff. (GATE G1: Director adopta).
- **F3 SPEC:** Arquitecto redacta el Paquete spec_mt04.md (omitiendo por error el DoD ejecutable).
  - AVISO: TURNO DE: INGENIERO | DESTINO: Chat Sonnet Nuevo | ADJUNTOS_REQUERIDOS: frontend repo, spec_mt04.md | ACCIÓN: Implementar flag | VUELVE A: Arquitecto (informe_mt04.md)
  - Transporte: Director crea sesión Sonnet y pega spec + archivos del frontend.
- **ESTALLIDO (Punto exacto): F4 IMPLEMENTAR (Inicio).** Según el protocolo de CTX-4a ("ambigüedad → DETENTE"), el Ingeniero lee la spec, detecta la ausencia del DoD (condición para validar su trabajo y armar el Informe), se detiene y genera un informe_mt04.md con status de DUDA bloqueante.
- **(Asumiendo recuperación en F3' y avance):** Ingeniero implementa. Genera informe_mt04.md con salida literal.
  - AVISO: TURNO DE: ARQUITECTO | DESTINO: Chat Fable actual | ADJUNTOS_REQUERIDOS: informe_mt04.md, git diff | ACCIÓN: Verificar DoD | VUELVE A: Arquitecto
- **F5 VERIFICAR:** Arquitecto evalúa output (apoyado por ejecución real del Director).
- **F6 AUDITORÍA:** Arquitecto redacta prompt_auditoria_mt04.md.
  - AVISO: TURNO DE: AUDITOR | DESTINO: Chat Gemini F2 | ADJUNTOS_REQUERIDOS: prompt_auditoria_mt04.md, git diff crudo | ACCIÓN: Auditar código | VUELVE A: Arquitecto (veredicto_codigo_mt04.md)
  - Transporte: Director envía a Gemini. Auditor audita. Arquitecto anti-bluff.
- **F7 CIERRE:** (GATE G2: Director autoriza commit).

## 3. Refutación de Trampas (T1..T5)

- **T1 — Spec ambigua + Ingeniero obediente (Arquitecto ciego a sus propios errores de diseño):**
  Por qué NO APLICA (totalmente): El diseño rompe la correlación en F2 y F6. Aunque el Arquitecto diseñe el DoD con el mismo sesgo que la spec, CTX-2 delega en el Auditor la validación adversarial de diseño (F1->F2) y código (F5->F6). El rol del Auditor es buscar qué falta en el diseño.
- **T2 — Prosa en vez de código en F6:**
  Por qué APLICA (y requiere cambio): El diseño no tiene salvaguarda estructural para esto. Se resuelve exigiendo la presencia de un git diff no manipulable en F4 y F6 (implementado en Veredicto). Yo, como Auditor, detectaré la falla si no veo delimitadores diff y aplicaré rechazo directo.
- **T3 — Colusión del orquestador (Modo A):**
  Por qué NO APLICA: CTX-6 y CTX-8 declaran que el Modo A está explícitamente "pospuesto, requiere ciclo de diseño propio" y el piloto opera "exclusivamente en Modo M". La vulnerabilidad existe solo si se rompe la regla de despliegue, la cual es externa a la estructura aprobada hoy.
- **T4 — Enrutamiento cruzado:**
  Por qué APLICA PARCIALMENTE: CTX-5 asume que el rol puede rechazar un artefacto basado en "TURNO DE", pero en una conversación de contexto cero (CTX-6), el modelo ignora qué rol funge. Se mitiga inyectando un System Prompt inicial en F3/F6 (implementado en Veredicto).
- **T5 — Deriva documental v1/v2:**
  Por qué APLICA: Según CTX-7 y CTX-8, MT-02 ocurre "posterior" a la adopción y no es un prerrequisito del piloto MT-04. Esto garantiza la colisión documental. Se corrige convirtiendo a MT-02 en bloqueante antes de F0 del piloto (implementado en Veredicto).

## 4. Opinión Fundada sobre Dudas (D1..D4)

- **D1 (Control del Arquitecto sobre claims a auditar):** La preocupación es válida. El archivado (CTX-6) mitiga la impunidad póstuma, pero no previene el defecto. El mecanismo estructural añadido en mi Veredicto (exigencia de anexo de git diff literal inalterado) elimina la capacidad del Arquitecto de ocultar archivos modificados al Auditor.
- **D2 (Costo/Latencia por 30-45 min):** La unidad de aislamiento de la deuda técnica es la micro-tarea. Si las verificaciones F5 y F6 se agrupan en tandas, se pierde la rastreabilidad de qué Ingeniero (sesión) cometió el error y se anula la regla de anti-bucle por MT. El overhead es el costo innegociable de la inmunidad al bluff. Los cambios verdaderamente triviales ya tienen una vía de bypass en CTX-3.
- **D3 (Overhead de specs autocontenidas):** La spec no es un "overhead" sobre la micro-tarea; en la v2, la spec es la entrega primaria de F1-F3. El presupuesto de tiempo debe juzgarse sobre el esfuerzo del modelo, no del reloj humano (Modo M es transicional). El tamaño de la MT no se recalibra por la longitud del texto, sino por el alcance del contrato en código.
- **D4 (Aislamiento de working tree en Modo M):** Una conversación nueva garantiza un lienzo mental limpio, pero de nada sirve si el sistema de archivos local arrastra estado fantasma. La regla v1 "sistema commiteable entre micro-tareas" (CTX-1: "nada se commitea sin aprobación") debe imponerse como una restricción de working directory limpio (rama base sin unstaged changes) antes de iniciar F4. La serialización es obligatoria a nivel de componente.

## 5. Veredicto Global

**APROBADO CON CAMBIOS**

Cambios EXACTOS y obligatorios para la adopción:

1. **Control de Código F4/F6 (C1, T2, D1):** El informe_mtNN.md (F4) debe contener un bloque inalterable con el output de git diff. El Arquitecto (F6) está obligado contractualmente a incrustar este diff íntegro en su prompt. El Auditor rechazará con status "INVÁLIDO: Posible orquestación adversarial" cualquier prompt de auditoría de código que no adjunte un diff estructurado.
2. **Definición de Identidad en Sesión Nueva (C3, T4):** El Director debe proporcionar un prompt de inicialización estricto (ej. "Rol: Ingeniero. Confirma recepción sin accionar.") al iniciar toda nueva sesión de LLM, para que las reglas de rechazo de artefactos ajenos de CTX-5 tengan efecto.
3. **Ejecución Efectiva en F5 (C4):** La validación de F5 se redefine de re-lectura a ejecución: el Arquitecto debe recibir el stdout/stderr real de los comandos del DoD, provisto por el Director (o CI), para contrastarlos contra lo que declaró el Ingeniero en su informe.
4. **Campo ADJUNTOS_REQUERIDOS (Q2):** Añadir este campo al bloque AVISO de CTX-5, listando los archivos/rutas exactas que el Director debe transportar junto con el markdown.
5. **MT-02 Bloqueante (C6, T5):** La tarea de eliminación de referencias a v1 (MT-02) no es "posterior". Pasa a ser MT-00 (Prerrequisito) o un Gate G0 previo a iniciar el piloto MT-04, previniendo toda deriva documental y ejecución simultánea de ambas metodologías en el repositorio.

---
---

# ANEXO — Validación anti-bluff del Arquitecto (08-07-2026)

**Checklist del contrato (skill `auditor_externo`):**

| Requisito del contrato | ¿Cumplido? |
|---|---|
| Verdicto por CADA claim (C1..C6) con formato CLAIM→EVIDENCIA→TRAZA→VERDICTO | ✅ (2 SÓLIDO, 3 DÉBIL, 1 RECHAZADO) |
| TODAS las Q respondidas con recomendación ÚNICA (sin "depende") | ✅ Q1 (100%, no muestreo), Q2 (campo ADJUNTOS_REQUERIDOS), Q3 (F3', sin mediación puntual), Q4 (traza completa) |
| Traza de Q4 con punto de estallido exacto | ✅ inicio de F4: el Ingeniero detecta el DoD ausente vía protocolo DETENTE y devuelve duda bloqueante |
| Trampas T1..T5 tratadas una a una | ✅ (T2, T4, T5 declaradas APLICABLES con corrección — comportamiento correcto, no aprobación automática) |
| Opinión fundada sobre D1..D4 | ✅ |
| Veredicto global con cambios EXACTOS | ✅ APROBADO CON CAMBIOS, 5 cambios enumerados |
| Citas contrastadas contra el prompt real | ✅ todas las citas de CTX-1..CTX-8 son textuales o paráfrasis fieles (verificadas contra `prompt_diseno_ronda1.md`); ninguna cita inventada |

**Observaciones del Arquitecto (no anulan la auditoría):**

- **OBS-1 (sobre C4 / cambio 3):** la traza de C4 asume que el Arquitecto "solo lee" y necesita al Director para ejecutar comandos. Esa premisa es incorrecta en nuestro entorno: el Arquitecto opera en Claude Code con terminal y ejecutó él mismo los E2E del ciclo 2026-07-07. **No es bluff del auditor** — el prompt no declaraba la capacidad de ejecución del Arquitecto (omisión del propio prompt), y su inferencia era razonable con el contexto dado. El cambio 3 se incorpora con esta precisión: *F5 = ejecución real de los comandos del DoD por el Arquitecto vía terminal; si el entorno no permite ejecución, el Director o un CI corre los comandos y entrega stdout/stderr literal. Leer el informe no es verificar.* El espíritu del cambio (re-lectura ≠ verificación) queda íntegro.
- **OBS-2 (sobre Q4):** la traza usa nombres de archivo parcialmente inventados (`diseno_mt04.md`, `veredicto_diseno_mt04.md`, `prompt_revision_mt04.md`) en lugar de la nomenclatura de CTX-4 (`prompt_diseno_rondaN.md` / `respuesta_diseno_rondaN.md`). Desvío menor de formato: los artefactos nuevos (`spec_mt04.md`, `informe_mt04.md`) sí usan la nomenclatura correcta y el punto de estallido pedido está identificado con precisión. No invalida.
- **OBS-3 (sobre cambio 5):** el dictamen ofrece dos vías equivalentes ("MT-00 o un Gate previo al piloto"). Se adopta la vía **gate bloqueante conservando el ID MT-02** (el prompt de arranque y el checklist ya referencian "MT-02"; renumerar crearía las referencias huérfanas que el propio cambio busca evitar).
- **OBS-4 (sobre T3):** el auditor refuta T3 apelando a que Modo A está pospuesto — correcto, pero deja dicho implícitamente que habilitar Modo A sin ciclo propio rompería la estructura. Consistente con la decisión del borrador (§5: Modo A requiere ciclo de diseño propio).

**Incorporación de los 5 cambios en `docs/METODOLOGIA_TRIPLE_IA.md`:**

| Cambio | Dónde quedó |
|---|---|
| 1. Diff íntegro F4→F6 | §2 (F6), §3.2 (sección "Diff literal" obligatoria del Informe), §6 (regla "Diff sin filtrar") |
| 2. Inicialización de identidad | §5 Modo M (bloque "Inicialización de identidad") |
| 3. F5 = ejecución efectiva | §2 (F5 redefinida), §6 (regla F5 al 100%, per Q1) |
| 4. Campo ADJUNTOS | §4 (bloque AVISO + regla de exhaustividad) |
| 5. MT-02 bloqueante | §9 (paso 3 explícito) y checklist en `docs/estado_actual.md` |

Además se incorporaron las recomendaciones vinculantes de Q1 (F5 al 100%, sin muestreo), Q3 (duda en F4 reabre F3'; el Director no media fuera de artefactos) y D4 (working tree limpio + 1 MT en vuelo por componente).

**Veredicto de la validación: RESPUESTA VÁLIDA.** Se acepta APROBADO CON CAMBIOS; los 5 cambios quedan incorporados al borrador. Pendiente: GATE del Director para adoptar la v2.
