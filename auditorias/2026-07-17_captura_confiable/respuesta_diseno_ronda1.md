# Expediente 2026-07-17_captura_confiable — Respuesta de revisión de DISEÑO (ronda 1)

**Auditor:** Gemini 3.1 Pro High (conversación nueva, con inicialización de identidad)
**Recibida:** 22-07-2026, pegada por el Director (texto literal; tabla C1..C6 reconstruida sin alterar redacción).
**Veredicto global:** APROBADO CON CAMBIOS (6 cambios enumerados)
**Validación anti-bluff:** ver ANEXO — VÁLIDA con 2 observaciones (OBS-1: cambio 5 ya implementado; OBS-2: contradicción interna cambios 1↔2 que afecta el DoD de MT-C4 — decisión del Director en G1).

---

## 1. Verificación de Claims (C1..C6)

- **C1 — El selector elimina H3 sin regresión. SÓLIDO.** EVIDENCIA: "D-2 (MT-C2) — startRecording(modo) sin fallback silencioso... la grabación NO arranca". TRAZA: al forzar la elección y eliminar el fallback, cancelar el diálogo → `getDisplayAudioStream()` null → `setError` en vez de degradar en secreto a microphone. Elimina H3 sin afectar presencial.
- **C2 — "Virtual sin mic → system + aviso H4" es la degradación correcta. SÓLIDO.** El valor primario en virtual es el audio de los demás; detener descartaría el 100%. Preservar como 'system' + banner H4 comunica el estado deficiente.
- **C3 — El detector RMS es fiable para el caso real. DÉBIL.** Con `noiseSuppression: true` el ruido de una sala en silencio se anula; una ventana de 3 s hace que una pausa respiratoria/de pensamiento de 3 s dispare la alerta de "micrófono muerto".
- **C4 — Analizar el mic crudo (no el mix) es correcto en virtual. SÓLIDO.** El stream mezclado elevaría la amplitud con la voz de la pestaña → falso "mic vivo". Aislar la pista pura audita solo la aportación del Director.
- **C5 — El cambio de firma es seguro. SÓLIDO.** El closure `() => startRecording(modoReunionRef.current)` aísla del MouseEvent y el ref evita stale-closure.
- **C6 — Alcance cerrado y defensa en profundidad. SÓLIDO.** Los cambios UI no alteran la carga útil; si H4 falla total, el archivo mudo (<300 B/s) → 422 del backend (CTX-6).

## 2. Respuestas Q1..Q4 (recomendaciones únicas)

**Q1 — Umbral y ventana:** `RMS < 0.01` apropiado para silencio muerto. La ventana de 3 s es inaceptablemente corta e inducirá falsos positivos por la supresión de ruido que aplana pausas normales. **Recomendación: elevar la ventana deslizante a 10 s, evaluando RMS solo a partir de t ≥ 10 s.**

**Q2 — Constraints presencial:** no usar los filtros por defecto de Chrome (anulan audios lejanos, asumen voz a 20 cm). **Recomendación: `{ audio: { echoCancellation: false, noiseSuppression: false, autoGainControl: true } }`. Eleva orgánicamente el RMS base, blindando el detector (Q1) contra falsos positivos.**

**Q3 — Texto del error virtual cancelado/sin audio:** *"No se capturó audio. Al compartir, asegúrate de seleccionar 'Pestaña de Chrome' y tener activa la casilla 'Compartir audio de la pestaña'."*

**Q4 — Traza defensa en profundidad:** t=0 inicia presencial (mic muteado en OS); t=10 s (ventana corregida) 10 s de amplitud plana → `micSilent=true` + banner; t=30 s el usuario ignora la alerta y detiene → mutación → "Procesando con IA..."; server recibe ~7,6 KB DTX, promedia <300 B/s → HTTP 422 → toast de error. Hueco residual: ninguna acta alucinada ni pérdida de datos legítimos; el único perjuicio es 30 s de un usuario que se niega a leer el banner.

## 3. Refutación/neutralización de Trampas (T1..T5)

- **T1 — AudioContext suspendido. NEUTRALIZACIÓN (mandato):** `new AudioContext()` fuera del handler del click puede heredar `suspended` y emitir ceros. `useMicLevel` DEBE revisar `audioCtx.state === "suspended"` y llamar `audioCtx.resume()`; no contar muestras como silencio mientras el estado no sea `running`.
- **T2 — Doble AudioContext sobre el mismo track. REFUTACIÓN:** bifurcar un `MediaStreamTrack` hacia dos `MediaStreamSourceNode` bajo distintos contextos no degrada los datos ni destruye el buffer del `MediaRecorder`. Menos eficiente, pero funcionalmente inocuo.
- **T3 — Silencio legítimo en virtual. NEUTRALIZACIÓN (mandato):** quedar 15 min en silencio en Meet es habitual; un banner destructivo arruina la UX. D-4 debe degradar la jerarquía del banner a warning pasivo (ámbar/gris) en modo virtual, reservando el rojo para presencial.
- **T4 — Regresión del guard de envío. NEUTRALIZACIÓN (mandato):** el botón `isRecording ? stopRecording : startRecording` DEBE poseer `disabled={processAudio.isPending}` para anular doble-clic durante el loader.
- **T5 — Selector vs permisos. REFUTACIÓN:** mantener el selector en "Reunión Virtual" preserva la intención original; el badge técnico ("Solo altavoces") comunica el resultado del fallback. Cambiar el selector falsearía la intención pasada.

## 4. Opinión fundada (D1..D4)

- **D1:** default "presencial" pragmáticamente correcto (fricción cero en campo físico).
- **D2:** si es Segmented Control custom, exigir `role="radiogroup"`/`role="radio"` + navegación por flechas; si no, radios nativos estilizados.
- **D3:** aísla la manipulación de bajo nivel de Web Audio manteniendo el scope de `useAudioRecorder` enfocado. A favor de hook separado.
- **D4:** `getByteTimeDomainData` invade la solución técnica; el Ingeniero podría usar `getFloatTimeDomainData` (−1..1 float32, sin la resta heurística de 128), simplificando el RMS. Flexibilizar.

## 5. Veredicto global

**APROBADO CON CAMBIOS**

Cambios EXACTOS:
1. Ventana del detector RMS en `useMicLevel` a **10 s** de inactividad (en vez de 3).
2. Constraint `{ echoCancellation: false, noiseSuppression: false, autoGainControl: true }` en el inicio de captura modo **presencial**.
3. Degradar la severidad del banner H4 en modo **virtual** a warning pasivo (silencio extendido es legítimo).
4. `useMicLevel` debe `.resume()` mientras su `AudioContext` esté `suspended` y no contar buffers hasta `running`.
5. Botón principal en `home.tsx` con `disabled={processAudio.isPending}` para anular dobles/regresiones.
6. Permitir `getFloatTimeDomainData` en vez de dictar rígidamente `getByteTimeDomainData`.

---
---

# ANEXO — Validación anti-bluff del Arquitecto (22-07-2026)

**Checklist del contrato:** C1..C6 con verdicto (5 SÓLIDO, 1 DÉBIL) ✅ · Q1..Q4 con recomendación única y trazas de valores (Q1 número exacto, Q4 traza t=0→30 s) ✅ · T1..T5 tratadas (3 mandatos + 2 refutaciones) ✅ · D1..D4 opinadas ✅ · 6 cambios exactos enumerados ✅. Respuesta pertenece al ciclo correcto (habla de selector, `useMicLevel`, RMS, AnalyserNode — NO del ciclo de robustez; el primer envío fue un artefacto ajeno y se rechazó sin accionar).

**Citas verificadas contra el prompt real y el código:**
- D-1/D-2/D-3/CTX-2/CTX-4/CTX-5/CTX-6 citados existen literalmente en `prompt_diseno_ronda1.md` ✅.
- Aritmética Q4: 30 s muteado ≈ 7,6 KB → 7600/30 = **253 B/s** < 300 → 422 ✅ (consistente con el E2E real del ciclo anterior: 8106 B/31,9 s = 254 B/s).

**OBS-1 — Cambio 5 YA ESTÁ IMPLEMENTADO (verificado en código real).** El Auditor mandata añadir `disabled={processAudio.isPending}` al botón, y su evidencia en T4 afirma que "CTX-4 dispara startRecording sin tener en cuenta processAudio.isPending". **Falso por omisión:** `home.tsx:184` ya tiene `disabled={processAudio.isPending}` (verificado por grep). El cambio 5 es un NO-OP — sin trabajo nuevo; solo se anota que el guard ya existía. (El prompt citó CTX-4 solo la línea 183 del `onClick`, sin incluir la 184 — de ahí la lectura incompleta del Auditor. La protección existe.)

**OBS-2 — Contradicción interna cambios 1 ↔ 2 que colisiona con el DoD de MT-C4 (requiere decisión del Director en G1).** El cambio 1 sube la ventana a **10 s** para evitar falsos positivos por `noiseSuppression`. Pero el cambio 2 **apaga** `noiseSuppression` en presencial (y el propio Auditor dice en Q2 que eso "blinda aún más el detector contra falsos positivos"). Es decir: en **presencial**, la causa que motivaba los 10 s desaparece con el cambio 2 → la ventana larga es sobre-corrección. La ventana de 10 s en presencial además **viola el DoD de MT-C4** ("aviso visible en **≤5 s** desde el inicio") y tu pedido explícito de F5.2 ("el aviso debe llegar AL INICIO"). El riesgo de falso positivo por NS solo persiste en **virtual**, donde el mic conserva `noiseSuppression: true` (`useAudioRecorder.ts:108`) — y ahí el cambio 3 ya lo mitiga volviendo el banner pasivo. **Reconciliación propuesta por el Arquitecto para F3 (a validar por el Director en G1):** ventana **por modo** — presencial **5 s** (NS off ⇒ ruido ambiente sostiene el RMS base, falso positivo improbable, cumple el DoD ≤5 s); virtual **10 s** + banner pasivo (silencio legítimo tolerado). Umbral `RMS < 0.01` y el resto de cambios (2, 3, 4, 6) se adoptan tal cual.

**Veredicto de la validación: RESPUESTA VÁLIDA — APROBADO CON CAMBIOS aceptado**, con cambio 5 marcado "ya implementado" y cambio 1 sujeto a la reconciliación de OBS-2 que el Director resuelve en G1. Los cambios 2, 3, 4 y 6 son sólidos e independientes. No se re-litiga el veredicto (las 2 observaciones lo refinan, no lo contradicen).

━━ AVISO DE TRASPASO ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CICLO      : 2026-07-17_captura_confiable
FASE       : F2 — Veredicto de diseño (GATE G1)
TURNO DE   : Director
ENTREGAR   : Decisión de G1: adoptar el diseño con los 6 cambios y
             resolver OBS-2 (ventana por modo 5 s/10 s, o ventana única)
ADJUNTOS   : Ninguno
DESTINO    : Sesión del Arquitecto (esta misma)
ACCIÓN     : Conceder G1 y elegir la opción de ventana del detector
VUELVE A   : Arquitecto, que redacta las 5 specs (F3) con el diseño
             final e inicia la rotación asistida (F4)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
