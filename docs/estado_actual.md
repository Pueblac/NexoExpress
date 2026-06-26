# Estado Actual — NexoExpress (Coordinador del Ecosistema)

**Estado Global del Ecosistema:** 🟢 VERDE
**Última Actualización:** 26-06-2026

---

## 🗺️ Estado por Proyecto

| Proyecto | Estado | % MVP | Prioridad ahora |
|---|---|---|---|
| ActaExpressWeb | 🟢 Activo | ~82% | Enriquecer prompt Gemini con transcripción |
| ActaExpress Android | 🟡 En pausa | ~60% | Paridad con Web (campo `plataforma`) |
| BitácoraExpress | 🟢 Activo en Linux | ~48% | Completar migración a Firebase (Python local) |
| NexoExpress | 🟢 Activo | 100% | Orquestación, RAG Docs y Mantenimiento |

---

## 📌 Hitos Recientes del Ecosistema

- **Integración con GitHub exitosa:** Repositorios conectados y subidos correctamente usando PAT.
- **Configuración de Firebase en Backend:** El SDK de Admin de Firebase ya está configurado en BitácoraExpress (`keys/`).
- **Pipeline Documental Automatizado:** Script en Python que renderiza flujos de Mermaid a PNG y los empaqueta en `.docx` con timestamp.
- **Definición de 3 Capas:** El ecosistema separa formalmente la Recolección (Apps), el Análisis (RAG Vectorial) y la Reportería.
- **Privacidad y Vectorización:** Se decidió no usar texto crudo para RAG por costos (se usará Vector Search) y se delegó la privacidad al cliente (horarios laborales) para que Firestore sea un "Cerebro Aislado".
- **Skills creados:** `arquitecto_ecosistema` y `disenador_flujos` añadidos a los 4 originales.

---

## 🚀 Próximos 5 Pasos Globales (priorizados)

1. **[BitácoraExpress]** Migrar escritura SQLite → Firebase Firestore (`be_proyectos/`, `be_actividades/`) usando el `GOOGLE_APPLICATION_CREDENTIALS`.
2. **[ActaExpressWeb]** Enriquecer el prompt para incluir transcripción completa en la respuesta de Gemini, mejorando la `sintesis/`.
3. **[BitácoraExpress]** Implementar frontend o configuración para establecer horario laboral y botón de pausa.
4. **[ActaExpress Android]** Añadir campo `plataforma: "android"` al guardar actas y lograr paridad de exportación.
5. **[NexoExpress]** Investigar costos de Cloud Functions para la futura vectorización con Vertex AI.

---

## 🔧 Skills Disponibles

| Skill | Propósito |
|---|---|
| `auditor_paridad` | Revisa brechas funcionales entre proyectos. |
| `documentador_sesion` | Genera bitácora y actualiza el estado (memoria a corto plazo). |
| `arquitecto_firebase` | Define/modifica el esquema Firestore (`schemas/`). |
| `roadmap_manager` | Compara avance vs `ECOSISTEMA_VISION.md` y prioriza tareas. |
| `arquitecto_ecosistema` | Analiza viabilidad cloud, privacidad y arquitectura end-to-end. |
| `disenador_flujos` | Traduce análisis arquitectónico a Mermaid (`docs/flujos/`). |

---

## 🖥️ Cómo Levantar BitácoraExpress

```bash
# Desde el directorio del proyecto
python3 start.py               # producción local
python3 start.py --reload      # desarrollo (hot-reload)
```
La app queda disponible en `http://127.0.0.1:8001`

---

## 📁 Estructura del Workspace

```
NexoExpress/
├── .agents/skills/             ← 6 Agentes IA configurados
├── docs/
│   ├── estado_actual.md        ← este archivo
│   ├── ECOSISTEMA_VISION.md    ← arquitectura y roadmap
│   ├── informe_arquitectura.md ← análisis profundo
│   ├── flujos/                 ← diagramas en .mmd y .png
│   ├── informes/               ← reportes generados en .docx
│   └── bitacora_*.md           ← logs de sesión
├── schemas/
│   └── firestore_schema.md     ← contrato de datos Firebase
├── scripts/
│   └── generar_informe.py      ← pipeline de documentación
└── scratch/                    ← scripts temporales
```
