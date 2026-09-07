# NexoExpress 🔗

**Coordinador del Ecosistema Express** — Repositorio central de documentación, esquemas y agentes IA del ecosistema de aplicaciones "Express" (ActaExpress y BitácoraExpress).

## 📦 Proyectos del Ecosistema

| Proyecto | Repo | Estado | % MVP | Rol en el Ecosistema |
|---|---|---|---|---|
| [ActaExpressWeb](https://github.com/Pueblac/ActaExpressWeb) | `ActaExpressWeb` | 🟢 Activo | ~82% | Captura formal (Reuniones) vía Web. Prototipo principal. |
| [BitacoraExpress](https://github.com/Pueblac/BitacoraExpress) | `BitacoraExpress` | 🟢 Activo | ~48% | Captura informal (Trabajo diario). Watcher Python multiplataforma. |
| ActaExpress Android | `ActaExpress` | 🟡 En pausa | ~60% | Captura formal (Reuniones) en terreno vía dispositivo móvil. |
| **NexoExpress** | `NexoExpress` | 🟢 Activo | 100% | Coordinador del ecosistema, fuente de verdad (schemas), memoria (bitácoras) e IA Agents. |
| NexoOrchestrator | `NexoOrchestrator` | 🟠 En construcción | — | **Plataforma, no producto.** Motor de orquestación y runner autónomo de agentes. Separado de NexoExpress el 09-08-2026. |

## 🧠 La Visión (El Sistema de Inteligencia Contextual)

El objetivo final del ecosistema no es solo tener aplicaciones aisladas, sino construir un **Sistema de Inteligencia Contextual (NotebookLM propio)** que una la información de todas ellas:
- **ActaExpress** documenta las decisiones formales y compromisos a través de actas y síntesis completas.
- **BitácoraExpress** cuantifica el esfuerzo real, contexto informal y herramientas usadas día a día sin fricción.

En el futuro, un Motor de Profundización (RAG) consumirá toda esta información desde Firebase para responder preguntas, preparar contexto antes de reuniones y asistir en tiempo real, cruzando lo que se acordó formalmente con lo que realmente se ha trabajado. (Ver [ECOSISTEMA_VISION.md](ECOSISTEMA_VISION.md) para la arquitectura completa).

## 🗂️ Estructura

```text
NexoExpress/
├── .agents/skills/            ← Agentes IA reutilizables
│   ├── auditor_externo/       ← Ciclo triple-IA: prompts de diseño/código para Gemini + validación anti-bluff
│   ├── auditor_paridad/       ← Audita brechas entre proyectos
│   ├── depurador_agentes/     ← Detecta bucles/alucinación en agentes IA y prescribe la intervención
│   ├── documentador_sesion/   ← Genera bitácoras de sesión
│   ├── innovador/             ← Propone mejoras fuera del plan (con evidencia; nunca implementa)
│   ├── arquitecto_firebase/   ← Define el schema Firestore
│   └── roadmap_manager/       ← Gestiona el roadmap global (descompone en micro-tareas)
├── docs/
│   ├── METODOLOGIA_TRIPLE_IA.md  ← Metodología v2.6 F0–F7: única del ecosistema (LEER PRIMERO)
│   ├── PROMPT_ARRANQUE_SESION.md ← Plantilla del primer mensaje de cada sesión
│   ├── estado_actual.md          ← Estado vivo, pendientes y checklist de micro-tareas
│   ├── ECOSISTEMA_VISION.md      ← Visión a futuro y arquitectura completa
│   └── bitacora_*.md             ← Bitácoras generadas en cada sesión
├── auditorias/                 ← Expedientes de ciclos IA ({fecha}_{tema}/: prompts, respuestas, specs, informes, validación)
├── schemas/
│   └── firestore_schema.md     ← Contrato de datos Firebase (fuente de verdad)
└── scratch/                    ← Scripts temporales y pruebas (ej. setups GitHub)
```

## 🔑 Reglas del Ecosistema

1. **Web primero**: ninguna feature se implementa en Android antes de ser probada y validada en Web.
2. **Schema centralizado**: ningún proyecto crea colecciones Firestore sin documentarlas primero en `schemas/firestore_schema.md`.
3. **Bitácora diaria**: cada sesión de desarrollo en el ecosistema genera su propia `docs/bitacora_DD_MM_YYYY.md` para mantener la trazabilidad.
4. **Prefijos y Trazabilidad**: BitacoraExpress usa `be_` en todas sus colecciones para evitar colisiones. Toda acta debe incluir el campo `plataforma` ("web" o "android").
5. **Metodología Triple-IA v3.0 — única y predominante del ecosistema** (ver `docs/METODOLOGIA_TRIPLE_IA.md`): Rigor físico en disco, arranques mecanizados por CLI (`scripts/emitir_arranque.py`) y roster unificado fijo (1 modelo y 1 esfuerzo por rol):
   - **Asesor Estratégico:** Gemini 3.8 Flash High (en Antigravity) traduce los gates al eje reversibilidad × impacto. No decide ni produce artefactos.
   - **Arquitecto Macro:** Claude Fable 5.1 High planifica F0, diseña F1 y predeclara la Parada de Observación (§3.1).
   - **Especificador Técnico:** Claude Opus 5 High redacta las specs F3 con glosa pedagógica inline (§4.3).
   - **Ingeniero:** Claude Sonnet 5 High implementa en F4 con evidencia literal no reformateada (`| tee`).
   - **Verificador Semántico:** Claude Opus 5 High ejecuta la compuerta empírica en F5 re-ejecutando DoDs en sesión en frío por Ruta B obligatoria.
   - **Auditor Externo:** Gemini 3.1 Pro High audita de forma adversarial el diseño (F2) y el código con su diff (F6) en conversación nueva cross-vendor.
   - **Guardrails obligatorios:** Sello de rol `[ROL · MODELO · turno N]` en toda respuesta, negaciones físicas por artefacto/ruta, nombrar regla violada antes de corregir, evidencia literal no reformateada (`| tee`) y hook git `commit-msg` anti-huellas.
   - **Paradas de Observación**: toda meta con UI o audio debe ser probada físicamente por el Director antes de gastar auditorías externas o commits.
6. **Micro-tareas**: toda meta se descompone en unidades de ≤30–45 min con DoD explícito antes de empezar; una sesión cierra 1–3 micro-ciclos completos.

## 🏗️ Firebase / Firestore Centralizado

Proyecto Firebase compartido: **`actaexpress`**

Colecciones activas:
- `users/{uid}` — Perfil y suscripción del usuario.
- `actas/{actaId}` — Actas de reuniones.
- `sintesis/{actaId}` — Transcripción extendida y análisis profundo.
- `be_proyectos/{id}` — Proyectos organizados de BitácoraExpress.
- `be_actividades/{id}` — Registros de ventana activa y duración.
- `be_bitacoras/{fecha}` — Resúmenes diarios generados por IA a partir del trabajo.

## 🤖 Cómo usar los Skills

Los skills están en la carpeta `.agents/skills/` y contienen instrucciones predefinidas para agentes IA (como Antigravity / Gemini). Al abrir cualquier proyecto del ecosistema o sesión de pair-programming con el agente, este detecta los skills disponibles para ayudarte a orquestar cambios arquitectónicos sin romper la paridad.

---
*Mantenido por: Pueblac · Última actualización: 06-09-2026 (metodología v3.0)*
