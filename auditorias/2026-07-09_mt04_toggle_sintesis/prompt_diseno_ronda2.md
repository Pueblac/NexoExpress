# Expediente 2026-07-09_mt04_toggle_sintesis — Prompt de revisión de DISEÑO (ronda 2)

**Ciclo:** F1/F2 Diseño, ronda 2 (METODOLOGIA_TRIPLE_IA.md — regla: BUG confirmado → ronda nueva)
**Motivo:** la validación anti-bluff de la ronda 1 confirmó un BUG en el parche obligatorio del veredicto (guard `!isSuccess` bloquea toda grabación posterior a la primera) y una premisa inventada en Q4 (no existe "strip" runtime en el cliente). Esta ronda somete el parche CORREGIDO con la evidencia de código que faltó en ronda 1.
**Preparado por:** Arquitecto (Claude Fable 5) — sesión 09-07-2026

## Instrucciones de operación para el Director

1. Conversación **NUEVA** en Gemini 3.1 Pro High (no reutilizar el hilo de ronda 1).
2. **Inicialización de identidad** — primer mensaje:
   *"Rol: Auditor del ciclo 2026-07-09_mt04_toggle_sintesis (ronda 2), metodología v2 del ecosistema Express. Confirma recepción sin accionar; acepta únicamente artefactos cuyo TURNO DE diga Auditor."*
3. **Sin adjuntos.** Pegar como segundo mensaje solo el bloque entre `=== PROMPT ===`.
4. Respuesta sin verdicto por claim o sin las Q respondidas: frase de devolución estándar.
5. Guardar la respuesta tal cual como `respuesta_diseno_ronda2.md` y avisar al Arquitecto.

---

=== PROMPT ===

# Rol y regla de oro
Eres auditor adversarial de diseño del ecosistema Express, en RONDA 2 de un ciclo. En la ronda 1 (otro auditor, hilo distinto) el veredicto fue APROBADO CON CAMBIOS, pero la validación del Arquitecto contra el código real confirmó que el parche exigido contiene un bug y que una premisa de la traza Q4 era una suposición sin evidencia. Tu trabajo AHORA es auditar el PARCHE CORREGIDO y las dos correcciones de premisa — no re-auditar el diseño completo (C1..C6 de ronda 1 quedaron SÓLIDOS y aceptados, salvo lo que aquí se somete). **Hipótesis de trabajo: el parche corregido también está mal hasta que se demuestre lo contrario.** No agradezcas, no resumas, no elogies. Todo lo que no esté en este prompt es NO VERIFICABLE — prohibido rellenarlo con suposiciones.

# Formato obligatorio de CADA verificación
CLAIM → EVIDENCIA (cita del contexto de este prompt) → TRAZA (ejecución simbólica paso a paso con valores concretos) → VERDICTO (SÓLIDO / DÉBIL / RECHAZADO).

# Material adjunto
Ninguno — revisión de diseño. Contexto verificado a continuación (incluye la evidencia literal que faltó en ronda 1).

# Contexto verificado (extraído literalmente del código real el 09-07-2026)

**CTX-A — Efecto de disparo actual (`home.tsx:100-110`), literal:**
```tsx
useEffect(() => {
    if (audioBase64 && !isRecording && duration > 0) {
      processAudio.mutate({
        data: { audioBase64, mimeType: "audio/webm", msDuration: duration }
      });
    }
  }, [audioBase64, isRecording, duration]); // eslint-disable-line react-hooks/exhaustive-deps
```

**CTX-B — Reset del hook al INICIAR cada grabación (`useAudioRecorder.ts:144-149`), literal:**
```ts
const startRecording = useCallback(async () => {
    setError(null);
    setAudioBlob(null);
    setAudioBase64(null);
    setDuration(0);
    chunksRef.current = [];
```
Al parar, `onstop` repuebla `audioBase64` (vía `blobToBase64`) y el efecto CTX-A se re-dispara. Es decir: **el flujo normal contempla N grabaciones sucesivas por carga de página**, cada una con su POST.

**CTX-C — Semántica de `useMutation` (TanStack React Query v5, dependencia real del proyecto):** tras un `mutate()` exitoso, `isSuccess` permanece `true` hasta que se llame de nuevo a `mutate()` o a `reset()`. No se resetea solo.

**CTX-D — Serialización del cliente generado (`lib/api-client-react/src/generated/api.ts:207-215`), literal:**
```ts
export const processAudio = async (audioInput: AudioInput, options?: RequestInit): Promise<Acta> => {
  return customFetch<Acta>(getProcessAudioUrl(),
  {
    ...options,
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    body: JSON.stringify(
      audioInput,)
  }
);}
```
`customFetch` (revisado) tampoco valida el body de salida. **No existe validación/strip runtime en el cliente**: los tipos protegen solo en compilación.

**CTX-E — `main.tsx` NO monta `<StrictMode>`** (verificado con grep). Un desmontaje/remontaje del componente destruye y recrea el estado del hook (`useState`), por lo que `audioBase64` arranca `null` en cada montaje.

**CTX-F — Parche EXIGIDO en ronda 1 (literal del veredicto):** añadir al guard de CTX-A `&& !processAudio.isPending && !processAudio.isSuccess`.

**CTX-G — BUG confirmado por el Arquitecto sobre CTX-F:** grabación 1 → mutate → 201 → `isSuccess=true` (CTX-C) → el usuario inicia grabación 2 (CTX-B resetea y repuebla `audioBase64`) → el efecto evalúa → `!isSuccess` es `false` → **la segunda acta jamás se procesa, sin error visible**. Regresión: un acta por carga de página.

# Parche corregido propuesto (claims a verificar)

```tsx
const generarSintesisRef = useRef(generarSintesis);
generarSintesisRef.current = generarSintesis;            // sincronizado en cada render (C3, ronda 1)
const lastProcessedAudioRef = useRef<string | null>(null);

useEffect(() => {
    if (
      audioBase64 && !isRecording && duration > 0 &&
      !processAudio.isPending &&
      lastProcessedAudioRef.current !== audioBase64
    ) {
      lastProcessedAudioRef.current = audioBase64;
      processAudio.mutate({
        data: {
          audioBase64,
          mimeType: "audio/webm",
          msDuration: duration,
          generarSintesis: generarSintesisRef.current
        }
      });
    }
  }, [audioBase64, isRecording, duration]); // eslint-disable-line react-hooks/exhaustive-deps
```

- **C7 — El parche corregido neutraliza el doble disparo SIN la regresión de CTX-G.** `lastProcessedAudioRef` marca cada audio como procesado ANTES del mutate (síncrono, misma pasada del efecto), de modo que re-ejecuciones del efecto con el mismo `audioBase64` (re-render, deps re-evaluadas, doble invocación de efectos) no re-postean; y una grabación NUEVA (base64 distinto, CTX-B) sí procesa. `!isPending` cubre el intervalo del request en vuelo. No se usa `isSuccess`.
- **C8 — Corrección de la premisa Q4 (ronda 1).** Dado CTX-D, con `as any` el flag SÍ viajaría al server: el tipado NO es la barrera de detección. La detección real de la "feature muerta en silencio" (T1) es el DoD E2E de MT-04b: observar `sintesis/{actaId}` poblada en Firestore con toggle ON (y ausente con OFF). MT-04a sigue siendo obligatoria, pero su justificación es integridad del contrato tipado, no protección runtime.

# Dudas declaradas por el Arquitecto
- **D5:** marcar `lastProcessedAudioRef.current = audioBase64` ANTES del mutate implica que si el mutate falla en red (`onError`), ese audio queda marcado y NO se reintenta automáticamente. Hoy el flujo tampoco reintenta (el usuario ve el toast de error y debe regrabar). ¿Aceptable, o el parche debe limpiar la marca en `onError`?
- **D6:** dos grabaciones distintas podrían (teóricamente) producir el mismo base64 exacto — solo si el audio es bit a bit idéntico. ¿Riesgo real o despreciable?

# Preguntas de control (recomendación ÚNICA cada una)
- **Q5:** Traza simbólica de DOS grabaciones consecutivas (acta A: 10 min con toggle ON; acta B: 5 min con toggle OFF, misma carga de página) bajo el parche corregido: valores de `audioBase64`, `lastProcessedAudioRef`, `isPending`, `generarSintesisRef.current` en cada evaluación del efecto, y los DOS POST resultantes campo por campo. Después ejecuta la MISMA traza bajo el parche de CTX-F y señala dónde muere el acta B.
- **Q6:** Sobre D5: ¿marcar antes del mutate (como propone C7) o limpiar la marca en `onError` para permitir reintento del mismo audio? UNA recomendación coherente con el comportamiento actual de errores (toast + regrabar).

# Anti-aprobación-automática
Si apruebas, demuestra con evidencia del contexto por qué estas trampas NO aplican:
- **T6:** re-render inmediatamente después del mutate (invalidateQueries del onSuccess re-renderiza) re-ejecuta el efecto con el MISMO `audioBase64` → sin la marca, doble POST. ¿La marca lo impide en TODA re-ejecución posible, incluida una doble invocación estilo StrictMode si se activara en el futuro (CTX-E)?
- **T7:** el guard `!isPending` solo, SIN la marca, ¿bastaría? (Pista: ventana entre el 201 y el siguiente render.) Demuestra por qué la marca es necesaria o suficiente.
- **T8:** regresión del flujo actual sin toggle: con el parche, una grabación única con toggle OFF debe producir EXACTAMENTE un POST con `generarSintesis: false` y el mismo comportamiento visible de hoy (toast, lista de actas). Señala cualquier diferencia observable.

# Entregable final
1. Tabla C7..C8 con verdictos. 2. Q5..Q6. 3. T6..T8 si apruebas. 4. Opinión sobre D5..D6. 5. Veredicto global de la RONDA (APROBADO / APROBADO CON CAMBIOS / RECHAZADO) — aplica SOLO al parche corregido y a C8; lo demás quedó cerrado en ronda 1.

Entrega TODA tu respuesta como UN único documento markdown listo para archivar tal cual. Sin verdicto por claim o sin la traza doble de Q5 es INVÁLIDA y será devuelta.

=== FIN PROMPT ===

---

━━ AVISO DE TRASPASO ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CICLO      : 2026-07-09_mt04_toggle_sintesis
FASE       : F1/F2 — Diseño, ronda 2 (BUG confirmado en veredicto r1)
TURNO DE   : Director
ENTREGAR   : auditorias/2026-07-09_mt04_toggle_sintesis/prompt_diseno_ronda2.md
             (solo el bloque entre === PROMPT ===)
ADJUNTOS   : Ninguno (contexto y evidencia dentro del prompt)
DESTINO    : Conversación NUEVA de Gemini 3.1 Pro High — inicialización
             de identidad primero (instrucción 2), luego el prompt
ACCIÓN     : Obtener veredicto sobre el parche corregido (C7) y la
             corrección de premisa (C8)
VUELVE A   : Arquitecto, archivando la respuesta literal como
             respuesta_diseno_ronda2.md → anti-bluff → gate G1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
