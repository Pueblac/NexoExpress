# Prompt de arranque — próxima sesión (generado el 23-07-2026, ciclo captura confiable CERRADO)

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
2. Lee NexoExpress/docs/estado_actual.md y la bitácora del 23-07-2026.
3. Contexto del ciclo candidato: hallazgo H6 descrito en estado_actual.md
   (cursor histórico del 13-07: autoguardado de chunks en IndexedDB +
   recuperación al reabrir, Fase 1 recomendada; transcripción incremental NO
   recomendada como parche; streaming Live API = Fase 3).
4. Schemas: NexoExpress/schemas/firestore_schema.md. Reglas del README.

Punto exacto donde quedó el cursor: **ciclo 2026-07-17_captura_confiable
CERRADO el 23-07** (F0→F7 completo): E2E 6/6 con el Director, auditoría
Gemini r1 APROBADO CON OBSERVACIONES, anti-bluff VÁLIDA con el único BUG
alegado (T5 carrera de auth) REFUTADO con evidencia (ProtectedRoute + E2E
prueba 5), G2 concedido, commit `35580f0` en ActaExpressWeb (rama linux).
Expediente completo (16 archivos) en auditorias/2026-07-17_captura_confiable/.
**NO hay ciclo abierto.**

Tarea actual: abrir **F0 del ciclo "Resiliencia de grabación" (H6)** —
autoguardado IndexedDB + recuperación al reabrir la pestaña, para que un
crash/cierre de pestaña durante una reunión larga no pierda el audio ya
grabado. F0 = propuesta de meta con micro-tareas y DoD por MT para mi gate
G0; considerar el análisis previo del 13-07 (Fase 1: chunks a IndexedDB +
oferta de recuperación al reabrir; NO streaming). Si en G0 decido otra
prioridad (p. ej. billing/Vertex o visor de síntesis), esa decisión manda.

Micro-tareas de esta sesión: se definen en F0/G0 (no hay checklist vigente).

Pendientes NO bloqueantes (no los tomes sin ciclo propio): billing/Vertex +
privacidad del tier (cupo Blaze 5/5; quiero pagar); visor de síntesis en la
UI; Android campo plataforma; actas en inglés; validar msDuration
server-side (OBS-A robustez); timeout HTTP de proxy con audios largos (al
desplegar); backlog del ciclo captura confiable: D1 umbral RMS en sala
callada (falso positivo presencial posible; calibración/0.005 candidatos),
D3 botón de descarte del aviso ámbar (fatiga de alarma), useEffect
defensivo de persistencia del selector; diseño futuro del "Modo A" a partir
de docs/arquitectura_mas_cloud.md.
