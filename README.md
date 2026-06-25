# NexoExpress 🔗

**Coordinador del Ecosistema Express** — Repositorio central de documentación, esquemas y agentes del ecosistema de apps Express.

## 📦 Proyectos del Ecosistema

| Proyecto | Repo | Estado | % MVP |
|---|---|---|---|
| [ActaExpressWeb](https://github.com/Pueblac/ActaExpressWeb) | `ActaExpressWeb` | 🟢 Activo | ~82% |
| [BitacoraExpress](https://github.com/Pueblac/BitacoraExpress) | `BitacoraExpress` | 🟢 Activo | ~48% |
| ActaExpress Android | `ActaExpress` | 🟡 En pausa | ~60% |

## 🗂️ Estructura

```
NexoExpress/
├── .agents/skills/          ← Agentes IA reutilizables
│   ├── auditor_paridad/     ← Audita brechas entre proyectos
│   ├── documentador_sesion/ ← Genera bitácoras de sesión
│   ├── arquitecto_firebase/ ← Define el schema Firestore
│   └── roadmap_manager/     ← Gestiona el roadmap global
├── docs/
│   ├── estado_actual.md     ← Estado vivo del ecosistema
│   ├── ECOSISTEMA_VISION.md ← Visión y roadmap completo
│   └── bitacora_*.md        ← Bitácoras de sesión
└── schemas/
    └── firestore_schema.md  ← Contrato de datos Firebase (fuente de verdad)
```

## 🔑 Reglas del Ecosistema

1. **Web primero**: ninguna feature se implementa en Android antes que en Web.
2. **Schema centralizado**: ningún proyecto crea colecciones Firestore sin documentarlas en `schemas/firestore_schema.md`.
3. **Bitácora diaria**: cada sesión de desarrollo genera su `docs/bitacora_DD_MM_YYYY.md`.
4. **Prefijos de colección**: BitacoraExpress usa `be_` en todas sus colecciones Firestore.

## 🏗️ Firebase / Firestore

Proyecto Firebase compartido: **`actaexpress`**

Colecciones activas:
- `users/{uid}` — Perfil y suscripción
- `actas/{actaId}` — Actas generadas (con `plataforma: "web" | "android"`)
- `sintesis/{actaId}` — Síntesis extendida separada del acta
- `be_proyectos/{id}` — Proyectos de BitacoraExpress
- `be_actividades/{id}` — Actividades trackeadas
- `be_bitacoras/{fecha}` — Bitácoras generadas por IA

## 🤖 Cómo usar los Skills

Los skills están en `.agents/skills/` y son instrucciones para agentes IA (Antigravity/Gemini).
Al abrir cualquier proyecto del ecosistema, el agente detecta los skills disponibles.

---

*Mantenido por: Pueblac · Última actualización: 25-06-2026*
