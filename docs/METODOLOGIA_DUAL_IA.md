# Metodología Dual-IA — Ecosistema Express

> **Origen:** extrapolada del proyecto OPCG (jul-2026), donde este flujo cazó
> bugs reales que ninguna de las dos IAs habría detectado sola (un bypass por
> mutación referencial, un test falso-positivo y un claim impreciso del propio
> implementador). **Mantenido en:** NexoExpress.

---

## 1. Los Roles

| Rol | Quién | Responsabilidad |
|---|---|---|
| **Director / Auditor Técnico** | Pueblac (humano) | Define objetivos, transporta prompts entre IAs, da la aprobación FINAL. Nada se commitea sin su visto bueno. |
| **Ingeniero de Desarrollo** | Claude Code (Fable 5) | Diseña, implementa, corre las verificaciones, genera los prompts de auditoría y VALIDA las respuestas del auditor (anti-bluff). |
| **Auditor Externo** | Gemini 3.1 Pro High | Revisa diseño ANTES del código y audita el código DESPUÉS, bajo contrato adversarial (citas obligatorias, trazas, trampas). Siempre en conversación nueva. |
| **Innovador** | Skill `innovador` (la corre el Ingeniero u otra IA) | Detecta mejoras fuera del plan. Propone, nunca implementa. |
| **Depurador de Agentes** | Skill `depurador_agentes` (la invoca el Director) | Detecta bucles de error/alucinación en cualquier IA y prescribe la intervención. |

Regla de oro heredada de OPCG: **ninguna IA verifica su propio trabajo con
autoridad final**. El Ingeniero valida al Auditor (anti-bluff) y el Auditor
valida al Ingeniero (adversarial). El humano arbitra.

---

## 2. El Ciclo "Diseño Primero" (obligatorio para todo cambio no trivial)

```
1. DISEÑO      Ingeniero entrega prompt de revisión de DISEÑO → Director lo
               lleva a Gemini (conversación NUEVA, sin adjuntos: el contexto
               verificado va dentro del prompt).
2. VEREDICTO   Gemini responde. "APROBADO CON CAMBIOS" = implementar CON los
               cambios. "RECHAZADO" = rediseñar.
3. IMPLEMENTAR Ingeniero implementa FIEL al diseño aprobado. Corre TODAS las
               verificaciones (tests, la app real, scripts) + prueba A/B
               cuando aplique (el test debe FALLAR con el fix neutralizado).
4. AUDITORÍA   Ingeniero entrega prompt de auditoría de CÓDIGO (formato
               CLAIM → EVIDENCIA archivo:línea → TRAZA → VERDICTO), declara
               sus propias dudas, lista los archivos exactos a adjuntar.
5. ANTI-BLUFF  Director pega la respuesta → Ingeniero verifica CADA cita
               contra el código real (grep / ejecución). Sin citas o sin
               trazas = INVÁLIDA (frase de devolución, sin conversación).
               BUG confirmado → corregir → ronda NUEVA.
6. CIERRE      Con APROBADO de Gemini Y aprobación del Director: commit +
               push (mensaje referenciando el ciclo), bitácora y estado
               actualizados (skill documentador_sesion).
```

**Expedientes:** todo prompt, respuesta y validación se archiva en
`auditorias/{YYYY-MM-DD}_{tema}/` — es la memoria jurídica del ecosistema y
la referencia de dictámenes vigentes.

**Cambios triviales** (typo, texto de UI, doc): no requieren ciclo completo,
pero sí aprobación del Director antes de commit.

---

## 3. Planificación por Micro-Tareas (regla nueva, 05-07-2026)

Problema observado en OPCG: las tandas grandes producían sesiones de horas y
metas difíciles de cortar. Regla correctiva:

### Definición de micro-tarea
Una micro-tarea es la unidad mínima planificable y debe cumplir **todas**:
- **Un solo entregable verificable** (una función, un endpoint, un campo del
  schema, una vista, UN prompt de auditoría).
- **≤ 30–45 minutos** de trabajo del Ingeniero, estimados ANTES de empezar.
  Si al descomponer no puedes garantizarlo, sigue partiendo.
- **DoD explícito escrito ANTES de empezar**: qué comando/observación
  demuestra que está terminada (nunca "quedó mejor").
- **Deja el sistema commiteable**: al terminar, todo verde. Nada a medias
  entre micro-tareas.

### Cómo se planifica
1. Toda meta del roadmap se **descompone en micro-tareas ANTES de tocar
   código** (lo hace `roadmap_manager` o el Ingeniero en el paso de diseño).
2. La descomposición vive en `docs/estado_actual.md` como checklist:
   `[ ] MT-01 …`, `[ ] MT-02 …`, cada una con su DoD en una línea.
3. **Una sesión = 1 a 3 micro-ciclos completos** (micro-tarea + su paso del
   ciclo dual-IA). Es preferible cerrar 1 micro-tarea con expediente completo
   que dejar 3 abiertas.
4. Los pasos del ciclo dual-IA que dependen del Director (llevar prompts a
   Gemini) son **cortes de sesión naturales**: el Ingeniero deja el prompt
   listo y la sesión puede cerrarse ahí sin trabajo a medias.
5. Al retomar, el prompt de arranque (ver `PROMPT_ARRANQUE_SESION.md`)
   apunta a la micro-tarea exacta donde quedó el cursor.

### Agrupación para auditoría
Micro-tareas del mismo tema pueden compartir UN ciclo de auditoría (una
"tanda"), pero la tanda no debe superar ~5 micro-tareas — más allá de eso el
auditor pierde precisión y las rondas se alargan.

---

## 4. Reglas de evidencia (heredadas de OPCG, no negociables)

- Toda verificación afirma **estado final observable** (respuesta del
  endpoint, documento en Firestore, render real, assert de test), jamás
  "corrió sin errores" ni logs.
- **Prueba A/B** para todo test que proteja un fix: con el fix neutralizado,
  el test debe fallar. Un test que pasa igual es un bug del test.
- El Ingeniero **declara sus propias dudas** en cada prompt de auditoría:
  dirigen al auditor a donde menos certeza hay (precedente OPCG: así se
  confirmó un exploit real).
- Los reportes al Director incluyen el resultado REAL de lo corrido (salida
  literal), no un resumen de fe.
- **Schema centralizado**: cualquier cambio de datos pasa primero por
  `schemas/firestore_schema.md` (regla 2 del ecosistema) y su ciclo de diseño.

---

## 5. Mapa de skills en el ciclo

| Momento | Skill |
|---|---|
| Descomponer metas y priorizar | `roadmap_manager` |
| Pasos 1, 4 y 5 del ciclo | `auditor_externo` |
| Al cerrar sesión | `documentador_sesion` |
| Periódicamente / a demanda | `innovador` (propuestas fuera de plan) |
| Cuando una IA se comporta raro | `depurador_agentes` |
| Cambios de datos | `arquitecto_firebase` + ciclo de diseño |
| Paridad Web/Android | `auditor_paridad` |
