# Validación anti-bluff del Arquitecto — respuesta de diseño ronda 1 (selector de micrófono)

**Fecha:** 30-07-2026 · **Valida:** `respuesta_diseno_ronda1.md`

## 1. Checklist anti-bluff

- **¿Citas al contexto reales?** Sí: `useAudioRecorder.ts:162-167`, `:224`, `mixAudioStreams :95-120`, `cleanupStreams:147-151`, deps de `useMicLevel`, `home.tsx:~505` — todas son exactamente las del contexto incrustado, que yo verifiqué contra el código real antes de enviar. No cita nada fuera del material. ✅
- **¿Recomendación ÚNICA por pregunta?** Las 4: Q1 contexto NUEVO por grabación (autoplay heredada del gesto + limpieza existente) · Q2 avisar y MANTENER la clave (fallo transitorio, p. ej. USB no enchufado hoy) · Q3 re-arme natural del detector sin lógica extra (la ventana de 5 s absorbe el hueco del swap) · Q4 upgrade desde `"system"` FUERA DE ALCANCE. Cero "depende". ✅
- **¿Trampas con mecanismo?** T2 (sin hueco: el mic viejo sigue conectado durante el `getUserMedia`; la transición topológica es síncrona), T3 (track muerto → silencio → el propio H4+CTA rescata), T4 (validación contra `enumerateDevices` local + fallback declarado) — correctas técnicamente (verificado: un source con track `ended` emite silencio y el `dest.stream` NO termina). ✅
- **¿Los "APLICA" son reales?** Sí, ambos:
  - **T1 (en vuelo):** cierto — mi salvaguarda solo cubría el ARRANQUE; una suspensión asíncrona del AudioContext A MITAD de grabación grabaría silencio sin recuperación. Hallazgo legítimo del Auditor.
  - **T5 (doble swap):** cierto — D-C no gestionaba concurrencia; dos `getUserMedia` en vuelo podían dejar una fuente huérfana mezclada (doble entrada + hardware cautivo). Hallazgo legítimo.
- **¿Coherencia interna?** Cambios 1-2 responden exactamente a T1/T5; C4 anotado "SÓLIDO (salvo T1)" es consistente. ✅

**Anti-bluff: VÁLIDA.**

## 2. Los 2 cambios, aceptados e incorporados al diseño congelable

1. **Recuperación activa del AudioContext (T1):** listener de `statechange` sobre el contexto de grabación; si transiciona a `suspended` con la grabación activa → `resume()` automático + log. **Extensión del Arquitecto (endurece sin contradecir):** el listener se aplica al contexto de grabación en AMBOS modos — el virtual ya usa AudioContext hoy (`mixAudioStreams`) y sufre el mismo riesgo en vuelo desde antes de este ciclo; cerrarlo aquí es gratis.
2. **Cerrojo de concurrencia en `swapMicrophone` (T5):** `isSwappingRef` — un swap en vuelo rechaza intentos concurrentes (toast "cambio en curso"), y token de época: si un `getUserMedia` "perdedor" resuelve tarde, sus tracks se detienen inmediatamente sin conectarse.

## 3. Conclusión

Veredicto del Auditor: **APROBADO CON CAMBIOS (2)** — anti-bluff VÁLIDA. Diseño congelable = D-A..D-E + cambio 1 (con extensión a virtual) + cambio 2 + las 4 recomendaciones Q adoptadas (contexto nuevo por grabación; avisar-y-mantener la clave; re-arme natural del detector; upgrade desde "system" fuera de alcance). Listo para **G1 del Director**; con G1 siguen las specs F3 (MT-M1..M5) y la rotación F4.
