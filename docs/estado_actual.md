# Estado Actual — NexoExpress (Coordinador del Ecosistema)

**Estado Global del Ecosistema:** 🟢 VERDE
**Última Actualización:** 25-06-2026

---

## 🗺️ Estado por Proyecto

| Proyecto | Estado | % MVP | Prioridad ahora |
|---|---|---|---|
| ActaExpressWeb | 🟢 Activo | ~82% | Enriquecer prompt Gemini con transcripción |
| ActaExpress Android | 🟡 En pausa | ~60% | Paridad con Web (campo `plataforma`) |
| BitácoraExpress | 🟢 Activo en Linux | ~48% | Migración Firebase + Push a GitHub |

---

## 📌 Hitos Recientes del Ecosistema

- **NexoExpress creado** — El coordinador tiene identidad propia con skills, esquema Firestore y documentación.
- **BitácoraExpress integrado** — Clonado, renombrado, cross-platform (Linux + Windows), levantado en `127.0.0.1:8001`.
- **Esquema Firestore unificado** — `schemas/firestore_schema.md` define el contrato de datos para todos los proyectos.
- **4 skills creados** — `auditor_paridad`, `documentador_sesion`, `arquitecto_firebase`, `roadmap_manager`.
- **Path cross-platform resuelto** — `BitácoraExpress` ya no tiene hardcoded `C:\Users\...`. Usa `PROJECT_BASE_DIR` en `.env`.
- **`start.py` creado** — Arranque limpio de BitácoraExpress en Linux: `python3 start.py`.
- **Campo `plataforma: "web"` activo** — ActaExpressWeb ya lo guarda en cada acta nueva.
- **Colección `sintesis/` implementada** — ActaExpressWeb guarda síntesis tras procesar cada audio.
- **`firestoreSet` añadido** — `firebaseAdmin.ts` ahora soporta escritura con ID específico.

---

## 🚀 Próximos 5 Pasos Globales (priorizados)

1. **[BitácoraExpress]** Migrar SQLite → Firebase Firestore (`be_proyectos/`, `be_actividades/`) ← requiere `GCP_PROJECT_ID` real
2. **[BitácoraExpress]** Push a GitHub rama `desarrollo` (necesita PAT configurado)
3. **[NexoExpress]** Crear repo en GitHub para el coordinador
4. **[ActaExpressWeb]** Enriquecer `ACTA_PROMPT` para incluir transcripción completa → mejora síntesis
5. **[ActaExpress Android]** Añadir campo `plataforma: "android"` al guardar actas

---

## 🔧 Skills Disponibles

| Skill | Propósito | Cuándo usarlo |
|---|---|---|
| `auditor_paridad` | Revisa brechas entre proyectos | Al inicio de cada sesión |
| `documentador_sesion` | Genera bitácora y actualiza estado | Al cerrar cada sesión |
| `arquitecto_firebase` | Define/modifica esquema Firestore | Antes de crear colecciones nuevas |
| `roadmap_manager` | Actualiza y prioriza el roadmap | Cuando hay cambios de prioridad |

---

## 🖥️ Cómo Levantar BitácoraExpress

```bash
# Desde el directorio del proyecto
python3 start.py               # producción local
python3 start.py --reload      # desarrollo (hot-reload)
python3 start.py --port 8002   # en otro puerto
```

La app queda disponible en `http://127.0.0.1:8001`

---

## 📁 Estructura del Workspace

```
Coordinador_ActaExpress/  (NexoExpress)
├── .agents/skills/
│   ├── auditor_paridad/
│   ├── documentador_sesion/
│   ├── arquitecto_firebase/
│   └── roadmap_manager/
├── docs/
│   ├── estado_actual.md        ← este archivo
│   ├── ECOSISTEMA_VISION.md    ← visión y roadmap completo
│   ├── bitacora_24_06_2026.md  ← sesión fundacional
│   └── bitacora_25_06_2026.md  ← sesión de hoy
└── schemas/
    └── firestore_schema.md     ← contrato de datos Firebase
```
