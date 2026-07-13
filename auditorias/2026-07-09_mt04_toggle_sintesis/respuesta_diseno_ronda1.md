# Expediente 2026-07-09_mt04_toggle_sintesis — Respuesta de revisión de DISEÑO (ronda 1)

**Auditor:** Gemini 3.1 Pro High (conversación nueva, con inicialización de identidad)
**Recibida:** 09-07-2026, pegada por el Director en la sesión del Arquitecto (pegado aplanado; texto literal, encabezados reconstruidos sin alterar redacción).
**Veredicto global:** APROBADO CON CAMBIOS (1 cambio obligatorio)
**Validación anti-bluff:** ver ANEXO — **el cambio obligatorio contiene un BUG CONFIRMADO (B1) y Q4 contiene una afirmación inventada (B2) → RONDA 2 obligatoria** (`prompt_diseno_ronda2.md`).

---

# 1. Tabla de Verificación (Claims C1..C6)

## C1 — Regeneración como micro-tarea previa (MT-04a)
- **CLAIM:** Regenerar clientes usando codegen y detenerse si hay diffs ajenos.
- **EVIDENCIA:** CTX-3 (Clientes desactualizados rechazan el campo en compilación); CTX-5 (MT-04a aprobada).
- **TRAZA:** Comando pnpm --filter @workspace/api-spec codegen → el tipo AudioInput de Zod/Orval incorpora generarSintesis: boolean → el diff garantiza que solo cambian los artefactos generados derivados de CTX-2.
- **VERDICTO:** SÓLIDO.

## C2 — Estado y persistencia
- **CLAIM:** Estado React inicializado y persistido en localStorage con clave actaexpress:generarSintesis:{uid}. Default false.
- **EVIDENCIA:** CTX-5 (Exigencia de toggle persistente y default OFF).
- **TRAZA:** Render inicial → lee localStorage.getItem('actaexpress:generarSintesis:{uid}') → si es null, usa false → al cambiar, actualiza la clave específica del usuario, evadiendo colisiones.
- **VERDICTO:** SÓLIDO.

## C3 — Envío sin closure stale
- **CLAIM:** Lectura del flag vía useRef sincronizado dentro del efecto de CTX-1.
- **EVIDENCIA:** CTX-1 (Efecto con deps congeladas y disparo automático).
- **TRAZA:** Render actualiza ref.current = generarSintesis → grabación se detiene (isRecording falso, audioBase64 disponible) → efecto se ejecuta evaluando las deps de captura → el payload lee ref.current obteniendo el valor vivo del último render, sin estar en el array de deps.
- **VERDICTO:** DÉBIL. (Aunque evita el closure stale, la estructura original de CTX-1 es vulnerable a dobles disparos en remontajes porque no limpia la variable que detona el efecto. Ver refutación T4 y veredicto global).

## C4 — UI del toggle
- **CLAIM:** Switch de shadcn bajo el botón, bloqueado si graba o procesa, sin layout shift.
- **EVIDENCIA:** CTX-4 (UI existente del grabador) y CTX-5 (Reglas de UX: persistente, bloqueado durante acción).
- **TRAZA:** Componente evaluado con isRecording=true o isPending=true → prop disabled del Switch recibe true → usuario no puede alternar en mitad del proceso.
- **VERDICTO:** SÓLIDO.

## C5 — Feedback asíncrono honesto
- **CLAIM:** Toast de éxito añade aviso asíncrono si el flag era true, sin hacer polling.
- **EVIDENCIA:** CTX-1 (El backend retorna un éxito inicial) y CTX-5 (Prohibición de cambiar backend).
- **TRAZA:** processAudio.mutate finaliza con 201 → onSuccess lee si el request llevaba generarSintesis: true → muestra toast modificado ("...generando en segundo plano") → no hay bloqueos de UI ni promesas adicionales.
- **VERDICTO:** SÓLIDO.

## C6 — Alcance cerrado
- **CLAIM:** Cero cambios en backend, schema o reglas.
- **EVIDENCIA:** CTX-5 (Restricción de fase explícita del Director).
- **TRAZA:** Todo el código propuesto ocurre en home.tsx y librerías generadas autolocalizadas. La API del backend (CTX-2) ya soporta el flag.
- **VERDICTO:** SÓLIDO.

# 2. Preguntas de Control (Q1..Q4)

## Q1: Para evitar el closure stale de CTX-1 (Estrategia única)
**Recomendación:** Ref sincronizado (C3).
**Justificación:** Si se introdujera generarSintesis en las deps, alternar el switch cuando audioBase64 tiene un remanente en memoria redispararía la mutación. Pasar el valor como parámetro desde stopRecording exigiría refactorizar el flujo asíncrono de obtención del blob de audio (que usualmente se resuelve después del stop). El useRef es la única vía que preserva el diseño del efecto reactivo (CTX-1) permitiendo leer el estado vivo sin detonarlo.

## Q2: Boolean explícito vs omitir false (D2)
**Recomendación:** Boolean explícito siempre.
**Justificación:** Basado en CTX-2, el servidor admite el campo. Enviar false de forma explícita deja constancia en los logs y telemetría de red de que el cliente actuó intencionalmente bajo la versión de la UI que soporta la feature, separando los casos de "usuario apagó el flag" versus "versión de frontend antigua/cacheada sin el flag".

## Q3: Nivel de persistencia (D1)
**Recomendación:** localStorage por uid.
**Justificación:** Almacenar en users/{uid} obligaría a modificar el schema de Firestore y las reglas de seguridad, violando directa y explícitamente la restricción de fase de CTX-5 ("cero cambios de backend, schema Firestore o reglas"). El localStorage global filtra el estado si dos usuarios comparten máquina. localStorage con {uid} cumple la regla y aísla la preferencia.

## Q4: Traza simbólica completa
- Contexto: Usuario con uid: "abc123" hace click en el switch (ON).
- Persistencia: Se escribe en localStorage: clave actaexpress:generarSintesis:abc123 = "true".
- Acción: Graba durante 10 minutos exactos (duration = 600000) y pulsa detener.
- Disparo: isRecording pasa a false, el blob se resuelve y puebla audioBase64 = "data:audio/webm;base64,...". El efecto (CTX-1) se activa.
- Payload (POST /actas/process):
```json
{
  "audioBase64": "data:audio/webm;base64,...",
  "mimeType": "audio/webm",
  "msDuration": 600000,
  "generarSintesis": true
}
```
- Estado Backend: Se crea el documento en Firestore actas/{id} y el servidor responde HTTP 201. En background, el servidor inicia la creación de sintesis/{id}.
- Toast Frontend: "¡Acta generada! El análisis profundo se está generando en segundo plano."
- **Punto EXACTO de fallo sin MT-04a + as any:** Si el Ingeniero evita regenerar y usa as any en el frontend, el request muere en el cliente (Zod/Orval interceptor). Las librerías generadas (CTX-3) usan schemas estrictos; al serializar la petición contra un schema viejo que no contiene el flag, la librería hará strip (descarte) del campo generarSintesis. El POST volará a la red sin el flag, el backend aplicará su default (false), pero no habrá error en consola ni red. Lo detectaría el usuario o el QA al ver que la síntesis nunca llega a la base de datos a pesar de haber pulsado el toggle.

# 3. Refutación de Trampas (T1..T5)

- **T1 — Feature muerta en silencio:** Neutralizada por C1. Al obligar la ejecución de MT-04a, se reconstruye el schema en api-zod. El cliente transmitirá exitosamente el payload sin mutilar el campo y sin necesidad de evadir el tipado con as any.
- **T2 — Closure stale:** Neutralizada por C3. El payload del POST accede a la referencia de memoria (heap) de ref.current en lugar del valor primitivo capturado en el closure del efecto, asegurando enviar el estado exacto del switch en el instante en que finalizó la grabación.
- **T3 — Fuga entre cuentas:** Neutralizada por C2. Al atar la clave de persistencia al uid (actaexpress:generarSintesis:{uid}), el logout y login con otra cuenta intentará leer una clave diferente.
- **T4 — Doble disparo:** NO NEUTRALIZADA (ver Veredicto Global). El código de CTX-1 disparado en StrictMode (o un re-montaje) con un audioBase64 residual evaluará las dependencias y volverá a disparar la mutación. El diseño de C3 no protege contra esto; exige un parche adicional en CTX-1 para ser seguro.
- **T5 — Regresión del flujo principal:** Neutralizada por C5. El frontend detiene el ciclo de vida de la feature tras mostrar el toast asíncrono y no se queda haciendo await ni polling a colecciones que no existen todavía (garantizando desacople del background).

# 4. Opinión sobre Dudas del Arquitecto (D1..D4)

- **D1 (Persistencia temporal):** La opción de localStorage es imperativa para esta fase debido al bloqueo de schema. Escalar a Firestore en un ciclo futuro es válido, pero es un scope diferente.
- **D2 (Boolean explícito):** Siempre enviar el campo explícito aporta fiabilidad en observabilidad (DataDog/GCP).
- **D3 (Diffs colaterales en MT-04a):** La directriz de revisar el diff y detenerse es la ÚNICA manera segura de operar en un ecosistema que usa codegen. Si el diff trae más cosas que el boolean, significa que hay contratos backend no integrados, y empujarlos causaría regressions.
- **D4 (Toggle bloqueado):** El bloqueo previene una de las inconsistencias más frustrantes: el usuario graba un audio largo, cambia de opinión, pero no sabe si el click aplicó o no porque la grabación ya inició. Bloquear documenta visualmente que la decisión se inyecta en el envío.

# 5. Veredicto Global

**APROBADO CON CAMBIOS.**

El diseño general es hermético respecto a las restricciones de backend y UI, pero falla en la resistencia a dobles disparos provocados por el useEffect existente (T4).

Cambios EXACTOS y obligatorios para aprobación definitiva:

**Parche en CTX-1 (Efecto de proceso):** Para prevenir el T4 (doble disparo por remontaje que causaría doble cobro de tokens), el efecto original de home.tsx debe ser fortificado para no mutar si ya está en curso o ya terminó con éxito, o limpiar el estado base de forma explícita. Se debe reemplazar el CTX-1 por:
```tsx
useEffect(() => {
    // Se añade validación de isPending y isSuccess para prevenir re-envíos
    if (audioBase64 && !isRecording && duration > 0 && !processAudio.isPending && !processAudio.isSuccess) {
      processAudio.mutate({
        data: {
          audioBase64,
          mimeType: "audio/webm",
          msDuration: duration,
          generarSintesis: ref.current // C3 implementado
        }
      });
    }
}, [audioBase64, isRecording, duration]); // eslint-disable-line react-hooks/exhaustive-deps
```

---
---

# ANEXO — Validación anti-bluff del Arquitecto (09-07-2026)

**Checklist del contrato:** verdicto por claim ✅ (5 SÓLIDO, 1 DÉBIL) · Q1..Q4 con recomendación única ✅ · T1..T5 tratadas (T4 declarada NO neutralizada — correcto) ✅ · D1..D4 opinadas ✅ · veredicto global con cambio exacto ✅ · citas a CTX fieles ✅.

**PERO la verificación contra el código real (grep + lectura, requisito de la skill) encontró dos hallazgos que obligan a RONDA 2:**

## B1 — BUG CONFIRMADO en el cambio obligatorio (guard `!processAudio.isSuccess`)

El parche exacto exigido por el auditor **rompe toda grabación posterior a la primera**:
- `useAudioRecorder.ts:146-148` (verificado): `startRecording` resetea `audioBase64` a `null` y `duration` a `0` — cada grabación nueva repuebla esos estados al parar y el efecto se re-dispara. Correcto.
- Semántica de React Query (`useMutation`): `isSuccess` queda `true` tras el primer 201 y **solo** vuelve a `false` con un nuevo `mutate()` o `reset()`. El guard propuesto impide precisamente ese nuevo `mutate()`.
- **Traza del bug:** grabación 1 → mutate → 201 → `isSuccess=true` → usuario graba acta 2 → stop → efecto evalúa → `!processAudio.isSuccess` es `false` → **la segunda acta jamás se procesa, sin error visible**. Regresión: un acta por carga de página. Es exactamente la clase de "feature muerta en silencio" (T1) que el propio auditor debía cazar.

## B2 — Afirmación INVENTADA en Q4 (mecanismo de "strip")

El auditor afirmó como hecho que "las librerías generadas usan schemas estrictos; la librería hará strip del campo". **Falso en este código** (verificado): `lib/api-client-react/src/generated/api.ts:207-215` hace `body: JSON.stringify(audioInput)` sin validación runtime alguna; `custom-fetch.ts` tampoco valida el body de salida. Con `as any` el flag **SÍ llegaría al server y funcionaría**. El mecanismo interno del cliente NO estaba en el contexto del prompt → el contrato exigía declararlo NO VERIFICABLE, no inventarlo. Consecuencias: (a) la traza de fallo de Q4 es incorrecta; (b) la detección de T1 NO la garantiza el tipado sino el DoD E2E de MT-04b (observar `sintesis/` poblada), que ya estaba en el plan.

## Observaciones menores
- La premisa "StrictMode" de T4 no aplica: `main.tsx` NO monta `<StrictMode>` (verificado con grep) y el remontaje resetea el estado del hook (el estado vive en `useState`). El riesgo real de doble disparo es más estrecho de lo afirmado — aun así, blindar el efecto es defensa barata y se acepta la INTENCIÓN del cambio.
- El resto de la auditoría (C1-C6, Q1-Q3, T1-T3, T5, D1-D4) está bien fundamentado en el contexto entregado y SE ACEPTA.

## Resolución (regla del ciclo: BUG confirmado → ronda NUEVA)
- Veredicto de validación: **respuesta PARCIALMENTE VÁLIDA** — se aceptan las recomendaciones Q1/Q2/Q3 y la intención del cambio (blindar el efecto), se **RECHAZA el parche literal** por B1 y se corrige la premisa de Q4 por B2.
- Contra-parche del Arquitecto (a validar en ronda 2): guard `!processAudio.isPending` + **ref del último audio procesado** (`lastProcessedAudioRef`), que neutraliza el doble disparo sin bloquear grabaciones sucesivas.
- Ronda 2: `prompt_diseno_ronda2.md` (conversación nueva, claims nuevos sobre el fix, con la evidencia literal del código que faltó en ronda 1).
