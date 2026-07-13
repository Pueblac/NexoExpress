# Expediente 2026-07-09_mt04_toggle_sintesis — Respuesta de revisión de DISEÑO (ronda 2)

**Auditor:** Gemini 3.1 Pro High (conversación nueva, con inicialización de identidad)
**Recibida:** 09-07-2026, pegada por el Director en la sesión del Arquitecto (pegado aplanado; texto literal, encabezados reconstruidos sin alterar redacción).
**Alcance de la ronda:** SOLO el parche corregido (C7) y la corrección de premisa (C8); C1..C6/Q1..Q3 quedaron cerrados en ronda 1.
**Veredicto global:** APROBADO
**Validación anti-bluff:** ver ANEXO (VÁLIDA, con 1 observación sobre el razonamiento de T7 que no altera el veredicto).

---

# Auditoría de Diseño - Ronda 2: Parche Corregido

## 1. Verificación de Claims (C7-C8)

### C7 — El parche corregido neutraliza el doble disparo SIN la regresión de CTX-G.
- **EVIDENCIA:** CTX-B (setAudioBase64(null) en startRecording), CTX-A (el efecto depende de audioBase64), CTX-G (la regresión donde isSuccess=true bloqueaba la grabación 2).
- **TRAZA:**
  1. Estado inicial: lastProcessedAudioRef.current = null.
  2. Finaliza Acta A: audioBase64 = "data:A", duration = 15000, isRecording = false.
  3. Render 1: El efecto evalúa sus dependencias. audioBase64 ("data:A") && !isRecording && duration > 0 && !processAudio.isPending (true) && lastProcessedAudioRef.current !== audioBase64 (null !== "data:A"). ¡Pasa el guard!
  4. Ejecución 1: lastProcessedAudioRef.current se asigna a "data:A". Se invoca mutate(). Mutación en curso (isPending=true, luego false).
  5. Usuario inicia Acta B: startRecording resetea audioBase64 a null (CTX-B).
  6. Finaliza Acta B: audioBase64 = "data:B", duration = 5000, isRecording = false.
  7. Render 2: El efecto evalúa. audioBase64 ("data:B") && ... && lastProcessedAudioRef.current !== audioBase64 ("data:A" !== "data:B"). ¡Pasa el guard! Se ejecuta la mutación y la marca se actualiza a "data:B". No sufre el bloqueo de isSuccess documentado en CTX-G.
- **VERDICTO:** SÓLIDO.

### C8 — Corrección de la premisa Q4 (ronda 1).
- **EVIDENCIA:** CTX-D (body: JSON.stringify(audioInput) en lib/api-client-react/src/generated/api.ts).
- **TRAZA:**
  1. Desarrollador decide omitir la actualización del generador (MT-04a) pero inyecta el payload como data: { ... , generarSintesis: true } as any en la UI.
  2. En tiempo de compilación, TypeScript lo permite por el bypass (any).
  3. En tiempo de ejecución, el cliente REST construido vía customFetch toma el objeto literal proporcionado y aplica JSON.stringify(audioInput).
  4. El string resultante incluye "generarSintesis":true y viaja en la red hasta el endpoint.
  5. El tipado frontend no es barrera de protección en el runtime (el cliente generado no hace limpieza de propiedades desconocidas). La prueba E2E en Firestore (MT-04b) es la verdadera y única validación empírica de que la feature no está muerta.
- **VERDICTO:** SÓLIDO.

## 2. Preguntas de Control (Q5-Q6)

### Q5: Traza simbólica de DOS grabaciones consecutivas (A: 10 min ON, B: 5 min OFF)

**Bajo el PARCHE CORREGIDO:**
1. Fin Acta A: audioBase64="baseA", lastProcessedAudioRef=null, isPending=false, generarSintesisRef.current=true. El efecto se dispara. Guarda "baseA" en la ref.
2. POST Acta A: { audioBase64: "baseA", mimeType: "audio/webm", msDuration: 600000, generarSintesis: true }. Request finaliza con éxito.
3. Inicio Acta B: audioBase64 asume null por CTX-B al clickear el usuario startRecording.
4. Fin Acta B: audioBase64="baseB", lastProcessedAudioRef="baseA", isPending=false, generarSintesisRef.current=false. El efecto evalúa "baseA" !== "baseB" (true). Guarda "baseB" en la ref.
5. POST Acta B: { audioBase64: "baseB", mimeType: "audio/webm", msDuration: 300000, generarSintesis: false }. Ambas actas exitosas.

**Bajo el PARCHE EXIGIDO EN RONDA 1 (CTX-F):**
1. Fin Acta A: audioBase64="baseA", isPending=false, isSuccess=false, generarSintesisRef.current=true. El efecto se dispara. POST Acta A en vuelo. Request finaliza, mutación queda con isSuccess=true de manera persistente (CTX-C).
2. Inicio Acta B: audioBase64 asume null.
3. Fin Acta B: audioBase64="baseB", isPending=false, isSuccess=true, generarSintesisRef.current=false. El efecto se evalúa: comprueba !processAudio.isSuccess... ¡FALSE!
4. **Muerte Acta B:** El guard falla. El POST no se emite, el acta desaparece en silencio sin error visible.

### Q6: Sobre D5 (Reintento ante fallos de red)
**Recomendación:** Marcar antes del mutate (C7) y NO limpiar en onError.
**Justificación:** El contexto establece explícitamente que "hoy el flujo tampoco reintenta (el usuario ve el toast de error y debe regrabar)". Limpiar la referencia en onError para permitir que el mismo estado audioBase64 reintente en red requeriría un mecanismo adicional (ej: un botón manual) porque sin cambiar las dependencias, el hook de efecto no se relanza espontáneamente. Dado que la UX es "regrabar", startRecording limpiará todo a null (CTX-B) y un audio nuevo saltará la ref sin problemas. Conservar la lógica actual de marcaje evita complejidad inútil y se ajusta a la respuesta UI existente.

## 3. Anti-aprobación-automática (T6-T8)

- **T6 (Re-render Inmediato tras Mutate):** Una vez que el mutate finaliza (ej. un onSuccess lanza un invalidateQueries que provoca un render), el audioBase64 es idéntico al anterior ("data:A"). Al evaluar el efecto, lastProcessedAudioRef.current === audioBase64 (ambos valen "data:A"). La mutación extra NO se lanza. Adicionalmente, el contexto indica (CTX-E) que main.tsx NO monta <StrictMode>. Por lo tanto, el re-render convencional retiene la referencia intacta, neutralizando por completo el doble POST provocado por el ciclo natural de React.
- **T7 (¿Basta con !isPending?):** NO BASTA. isPending solo protege contra reentrancias mientras el request HTTP está en vuelo. Cuando la mutación finaliza y isPending vuelve a false, se detona un re-render en React. En ese instante, si el audioBase64 sigue en memoria, el efecto detectaría !isPending (true) y dispararía el request OTRA vez. Esto generaría una cascada de loops infinitos (mutate success -> render -> mutate -> ...). La marca refánica es imprescindible como latch de consumición.
- **T8 (Regresión Flujo Sin Toggle):** Si un usuario entra hoy y graba con toggle en OFF bajo este parche, el comportamiento observable de la app (toast, lista) será idéntico al anterior. El único cambio estructural debajo es que el payload POST incluirá un boolean generarSintesis: false. Asumiendo el contrato API base (MT-04a) debidamente alineado con el backend, no hay ninguna diferencia perjudicial observable por el cliente.

## 4. Dudas Declaradas del Arquitecto (D5-D6)

- **D5 (Error y reintentos en red):** Duda saldada en Q6. Como la aplicación obliga al usuario a regrabar ante el error (toast + regrabar), retener la marca hasta que la siguiente grabación formatee todos los hooks a null (vía CTX-B) es el comportamiento seguro y coherente con el paradigma actual.
- **D6 (Colisión de Base64 entre grabaciones distintas):** El riesgo es totalmente DESPRECIABLE. Las grabaciones de audio enviadas como WebM (vía API del navegador) contienen cabeceras temporales de la sesión, metadata dinámica del encoder, y ruido electromagnético y ambiental. Conseguir que dos grabaciones diferentes emitidas en instantes distintos originen una cadena Base64 idéntica bit a bit y colisionen el guard de referencia es logísticamente un evento nulo.

## 5. Veredicto Global de la Ronda

**APROBADO**

El parche corregido soluciona de forma elegante y blindada la regresión generada en la Ronda 1. Emplea correctamente los mecanismos de useRef para desvincular el estado asíncrono de la mutación de TanStack de los ciclos de montajes/efectos de React, salvaguardando las actas sucesivas. Las premisas (C7, C8) son lógicamente verificables con el contexto dado.

---
---

# ANEXO — Validación anti-bluff del Arquitecto (09-07-2026)

**Checklist del contrato:** verdicto por claim (C7, C8: SÓLIDO ambos) ✅ · Q5 con la traza DOBLE exigida (incluye el punto exacto de muerte del acta B bajo el parche de r1) ✅ · Q6 con recomendación única ✅ · T6..T8 refutadas ✅ · D5..D6 opinadas ✅ · veredicto global APROBADO, acotado al alcance de la ronda ✅ · citas a CTX-A..G fieles ✅.

**Verificación de las trazas contra el comportamiento real:**
- Q5/C7 contrastadas paso a paso contra `useAudioRecorder.ts` (reset en start, repoblado en onstop) y la semántica de `useMutation` v5: **correctas**. La traza de la muerte del acta B bajo CTX-F coincide exactamente con el BUG B1 confirmado en la validación de ronda 1.
- Q6/D5: coherente con el flujo real de errores (toast + regrabar; sin mecanismo de reintento hoy). Aceptada.

**OBS-1 (sobre T7 — razonamiento impreciso, conclusión aceptada):** el auditor afirma que sin la marca habría "cascada de loops infinitos (mutate success → render → mutate → …)". Impreciso: un re-render NO re-ejecuta un `useEffect` cuyas dependencias (`[audioBase64, isRecording, duration]`) no cambiaron — React compara deps entre renders y omite el efecto. El riesgo real sin la marca es más estrecho: remontajes con estado preservado inexistentes hoy (CTX-E), una futura adopción de StrictMode, o un refactor de deps. La marca sigue siendo la defensa correcta y barata (latch idempotente), así que la conclusión de T7 ("la marca es imprescindible") se acepta como defensa-en-profundidad aunque su mecanismo citado sea incorrecto. No altera el diseño aprobado ni amerita ronda: el parche fue verificado con traza propia del Arquitecto, no sobre la justificación del auditor.

**Veredicto de la validación: RESPUESTA VÁLIDA — APROBADO aceptado.** Diseño final del ciclo (ronda 1 + ronda 2):
1. MT-04a: regeneración de clientes (`pnpm --filter @workspace/api-spec codegen`), diff revisado, stop si hay cambios ajenos.
2. MT-04b: Switch shadcn bajo el botón (default OFF, `disabled` al grabar/procesar, `data-testid="switch-sintesis"`), persistencia `localStorage` por uid, `generarSintesisRef` sincronizado, **parche del efecto con `lastProcessedAudioRef` + `!isPending`** (sin `isSuccess`), boolean explícito siempre, toast extendido cuando el flag fue `true`, marca NO se limpia en `onError`.

Pendiente: **GATE G1** (el Director adopta el veredicto) → F3: `spec_mt04a.md` y `spec_mt04b.md` para el Ingeniero (Sonnet).
