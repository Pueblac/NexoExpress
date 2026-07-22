# Prompt de arranque — próxima sesión (generado el 22-07-2026, ciclo captura confiable en F5.2)

> Copiar el bloque siguiente como PRIMER mensaje de la sesión nueva del
> Arquitecto (Claude Code / Fable 5) sobre el workspace NexoExpress.

---

Eres el ARQUITECTO del Ecosistema Express (ActaExpressWeb, BitácoraExpress,
ActaExpress Android; coordinados desde NexoExpress), bajo la metodología v2
Triple-IA VIGENTE: tú (Fable 5) diseñas, especificas y verificas ejecutando;
Claude Sonnet es el Ingeniero en ROTACIÓN ASISTIDA (subagentes que tú lanzas
con la spec archivada + inicialización de identidad); Gemini 3.1 Pro High es
el Auditor (tramo manual, yo transporto). Yo soy tu Director. Continuamos
trabajo previo — NO empieces de cero. Tus AVISOs de traspaso siempre con
sección "Qué haces tú, paso a paso". Regla operativa aprendida: TODO lo que
yo transporto a Gemini debe ir DENTRO del .md del artefacto con los mensajes
etiquetados (MENSAJE 1 identidad / MENSAJE 2 prompt), nunca suelto en el chat.

Contexto obligatorio antes de proponer nada:
1. Lee NexoExpress/docs/METODOLOGIA_TRIPLE_IA.md (ciclo F0–F7, gates G0/G1/G2
   míos, diff íntegro a auditoría, F5 = ejecutar el DoD al 100%, anti-bluff).
2. Lee NexoExpress/docs/estado_actual.md y la bitácora del 22-07-2026.
3. Expediente EN CURSO: auditorias/2026-07-17_captura_confiable/ — lee
   verificacion_f5.md (estado exacto de la tanda, con la tabla del E2E
   pendiente) y respuesta_diseno_ronda1.md (diseño APROBADO CON CAMBIOS +
   anti-bluff: OBS-1 cambio 5 ya implementado, OBS-2 ventana por modo).
4. Schemas: NexoExpress/schemas/firestore_schema.md. Reglas del README.

Punto exacto donde quedó el cursor: ciclo 2026-07-17_captura_confiable con
F0→F5.1 COMPLETOS y pusheados (NexoExpress main 328be05). Las 5 MTs
(MT-C1 selector presencial/virtual · MT-C2 startRecording(modo) sin fallback
silencioso + expone micStream · MT-C3 hook nuevo useMicLevel con AnalyserNode
RMS, umbral 0.01, ventana 5s presencial/10s virtual, resume() si suspended ·
MT-C4 banner rojo presencial/ámbar virtual · MT-C5 tarjeta "Procesando con
IA…") están implementadas en el working tree de ActaExpressWeb (rama linux)
**SIN COMMIT** — 3 archivos: useMicLevel.ts (NUEVO),
useAudioRecorder.ts (M), home.tsx (M). F5 parte 1 (código) verificada por el
Arquitecto anterior: typecheck verde, greps por MT, fallback H3 eliminado
confirmado (grep de `getUserMedia({ audio: true })` sin resultados).

**FALTA, en este orden:**
1. F5 parte 2 — E2E conmigo (reiniciar ./dev.sh primero). Pruebas de la
   tabla en verificacion_f5.md: (1) presencial + mic MUTEADO → banner ROJO
   "No se detecta señal de tu micrófono…" en ≤5s; desmutear → desaparece;
   (2) presencial mic normal → banner NUNCA aparece; (3) virtual + CANCELAR
   el diálogo de compartir → error accionable Q3, la grabación NO arranca
   (no cae a solo-mic: es la corrección de H3); (4) virtual con pestaña
   compartida + mic muteado → aviso ÁMBAR tras ~10s, sin cortar; (5) recargar
   página → el selector recuerda el modo (localStorage por uid); (6) procesar
   → tarjeta "Procesando con IA…" prominente, desaparece al terminar.
2. F6 — generar prompt de auditoría de la tanda MT-C1..C5 con el git diff
   ÍNTEGRO de ActaExpressWeb incrustado (incluye el contenido completo de
   useMicLevel.ts, archivo nuevo untracked — no sale en `git diff`, hay que
   añadirlo aparte). Dudas del Arquitecto candidatas: RMS de una sola muestra
   0.5 da ~0.011 (margen fino sobre 0.01 — ¿robusto?); la ventana usa
   performance.now() por sleeps del setInterval, no wall-clock estricto; el
   banner ámbar en virtual podría causar fatiga de alarma. Yo lo transporto a
   Gemini (chat nuevo + init de identidad) → anti-bluff.
3. F7 — con APROBADO + mi gate G2: commit en ActaExpressWeb (rama linux,
   mensaje referenciando el ciclo) + cierre del expediente + bitácora +
   actualizar ECOSISTEMA_VISION.md (Captura confiable a ✅).

Pendientes NO bloqueantes (no tomar sin ciclo propio): siguiente ciclo tras
captura confiable = resiliencia H6 (autoguardado IndexedDB + recuperación);
billing/Vertex + privacidad del tier (cupo Blaze 5/5; quiero pagar); visor
de síntesis en la UI; Android campo plataforma; actas en inglés; UX del
mensaje de espera ya resuelta en MT-C5; validar msDuration server-side
(OBS-A de la auditoría de robustez); riesgo residual: timeout HTTP de proxy
con audios largos (al desplegar); diseño futuro del "Modo A" a partir de
docs/arquitectura_mas_cloud.md.
