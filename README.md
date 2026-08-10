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
5. **Metodología Triple-IA v2.6 — única y predominante del ecosistema** (ver `docs/METODOLOGIA_TRIPLE_IA.md`): Fable 5 (Arquitecto Macro, effort low/medium) planifica F0, diseña F1 y **predeclara la Parada de Observación**; Sonnet 5 (Especificador, effort high) redacta las specs en F3 con **glosa pedagógica inline**; el Ingeniero de F4 es Sonnet 5 o Haiku 4.5 según la matriz de complejidad (Alta/Media/Baja); la verificación F5 la ejecuta Sonnet 5 (effort high) en Alta —juicio semántico— y Haiku 4.5 (Sintetizador) en Media/Baja; Haiku empaqueta la auditoría en toda complejidad; Gemini revisa el diseño ANTES y audita el código DESPUÉS (Ronda 1 de F6 SIEMPRE con 3.1 Pro High; Flash solo rondas 2+ de fixes o complejidad Baja), con validación anti-bluff de cada respuesta y el `git diff` íntegro como material de auditoría. El Director cuenta con un **Asesor Estratégico** (Gemini 3.6 Flash en Antigravity) que le traduce los gates a lenguaje ordinario y reduce cada decisión al eje **reversibilidad × impacto de negocio**: explica, pero **no decide**. Todo cambio no trivial recorre el ciclo F0–F7; nada se commitea sin aprobación del Director (gate G2).
   - **Paradas de Observación**: toda meta con UI, datos o indicadores predeclara en F0 qué podrá **ver y tocar** el Director y cuándo (por defecto al cerrar F5, antes de gastar la auditoría). Infraestructura pura puede eximirse, pero la exención se declara y se ratifica en G0 — por omisión no pasa el gate.
   - **Recalibración dinámica (G0′)**: si en F4/F5 se descubre que el prototipo o el indicador estaban mal especificados, se DETIENE y se pide recalibración formal al Director. Cambiar la evidencia sobre la marcha es deriva de alcance e invalida la entrega.
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
*Mantenido por: Pueblac · Última actualización: 09-08-2026 (metodología v2.6)*
