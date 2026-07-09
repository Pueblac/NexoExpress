# Estado Actual — NexoExpress (Coordinador del Ecosistema)

**Estado Global del Ecosistema:** 🟢 VERDE
**Última Actualización:** 09-07-2026
**Metodología vigente:** v2 Triple-IA (`docs/METODOLOGIA_TRIPLE_IA.md`, adoptada 09-07-2026)

---

## ✅ Checklist de Micro-Tareas Vigente

**Meta (EN CURSO, 08-07-2026):** [NexoExpress] Diseñar y adoptar la METODOLOGÍA v2 (Triple-IA): Fable 5 Arquitecto / Claude Sonnet Ingeniero / Gemini 3.1 Pro High Auditor.
**Expediente:** `auditorias/2026-07-08_metodologia_v2/`

- [x] **MT-01** — Borrador de `docs/METODOLOGIA_TRIPLE_IA.md` (roles, fases F0–F7, artefactos de traspaso spec/informe, AVISO estándar, gates humanos G0–G2, evaluación Modo M vs Modo A, excepciones y plan de adopción). — **DoD cumplido (08-07-2026):** doc completo + prompt de revisión archivado en `auditorias/2026-07-08_metodologia_v2/prompt_diseno_ronda1.md` y entregado al Director.
- [x] **Veredicto ronda 1 (08-07-2026): APROBADO CON CAMBIOS** — respuesta archivada en `respuesta_diseno_ronda1.md` con validación anti-bluff anexada (VÁLIDA; 1 observación: la premisa de C4 sobre incapacidad de ejecución del Arquitecto era incorrecta por omisión del prompt, cambio 3 incorporado con precisión). Los 5 cambios + Q1/Q3/D4 incorporados al borrador.
- [x] **Gate de adopción (09-07-2026):** el Director aprobó adoptar la v2 ("continuemos con el plan"). `METODOLOGIA_TRIPLE_IA.md` marcada VIGENTE; `METODOLOGIA_DUAL_IA.md` marcada HISTÓRICA/fallback.
- [x] **MT-02 (BLOQUEANTE antes del piloto, dictamen r1 cambio 5)** — Actualizados al ciclo v2: `PROMPT_ARRANQUE_SESION.md` (plantilla de Arquitecto), skills `auditor_externo` (diff íntegro F6, init de identidad, dudas del Ingeniero, F5 previo) y `roadmap_manager` (F0/G0), README (regla 5, árbol, fecha), skill `innovador` (colateral detectado por grep) y `arranque_proxima_sesion.md` regenerado para el piloto. — **DoD cumplido (09-07-2026):** `grep -rni "dual"` sobre los documentos operativos devuelve únicamente la línea intencional del README que marca la v1 como "histórica — fallback operativo (v2 §7)"; cero referencias operativas huérfanas.

**Cursor:** ciclo `2026-07-08_metodologia_v2` completo (diseño → veredicto r1 APROBADO CON CAMBIOS → cambios incorporados → adopción → MT-02). **Esperando GATE G2: aprobación explícita del Director para commit + push** (mensaje referenciando el ciclo) y generación de bitácora. Tras el cierre: piloto MT-04 en Modo M — arranca en F0 y necesita tu decisión de UX del toggle.

---

## 📁 Meta anterior (CERRADA 07-07-2026)

**Meta (CERRADA 07-07-2026):** [ActaExpressWeb] Enriquecer el prompt de Gemini para incluir transcripción completa y poblar `sintesis/` con contenido real.
**Expediente:** `auditorias/2026-07-07_transcripcion_sintesis/` — ciclo dual-IA completo: diseño APROBADO CON CAMBIOS (r1), código APROBADO CON OBSERVACIONES + BUG D1 corregido (r1), fix APROBADO (r2). Commiteado y pusheado con aprobación del Director.

- [x] **MT-01** — Diseño del enriquecimiento + prompt de revisión de DISEÑO para Gemini 3.1 Pro High, archivado en el expediente. — **DoD cumplido (07-07-2026):** existe `auditorias/2026-07-07_transcripcion_sintesis/prompt_diseno_ronda1.md` y fue entregado al Director.
- [x] **MT-02** — Implementar el diseño aprobado en ronda 1 (ver `respuesta_diseno_ronda1.md`, dictamen §3): dos llamadas (acta síncrona intacta + síntesis en background text/plain 65536 tokens reutilizando el `fileUri`), sin reintento MAX_TOKENS, purga anti-derrame, truncado 800k, flag `generarSintesis` (default false), logging de `usageMetadata`. — **DoD cumplido (07-07-2026):** E2E real con audio sintetizado → `sintesis/HwewR3jTMUdopfVzqCVN` con transcripción de 494 chars y `actas/{id}` con solo sus 13 campos; evidencia literal en `evidencia_mt02.md`. **Colaterales resueltos:** reglas Firestore no cubrían `sintesis/` (desplegado fix con aprobación del Director) y bug 400 en `firestoreSet` (updateMask con comas) corregido.
- [x] **MT-03** — Prompt de auditoría de CÓDIGO (claims, trazas, trampas, dudas, adjuntos exactos) archivado en el expediente. — **DoD cumplido (07-07-2026):** existe `prompt_auditoria_ronda1.md` y fue entregado al Director.
- [ ] **MT-04** — Frontend Web: enviar `generarSintesis: true` desde la UI (toggle u opción al grabar, decisión de UX del Director). — **DoD:** request real del frontend con el flag y síntesis generada end-to-end. *(No bloqueante para MT-02/MT-03.)*

*(Cursor histórico: ciclo cerrado el 07-07-2026. MT-04 pendiente — reservada como piloto de la metodología v2.)*

---

## 🗺️ Estado por Proyecto

| Proyecto | Estado | % MVP | Prioridad ahora |
|---|---|---|---|
| ActaExpressWeb | 🟢 Activo | ~82% | Enriquecer prompt Gemini con transcripción |
| ActaExpress Android | 🟡 En pausa | ~60% | Paridad con Web (campo `plataforma`) |
| BitácoraExpress | 🟢 Activo en Linux | 100% (MVP) | MVP Completado, mantenimiento |
| NexoExpress | 🟢 Activo | 100% | Orquestación, RAG Docs y Mantenimiento |

---

## 📌 Hitos Recientes del Ecosistema

- **Transcripción + análisis profundo funcionando (07-07):** ActaExpressWeb puebla `sintesis/` en background con flag `generarSintesis`; verificado E2E contra Firestore real. Primer ciclo dual-IA completo (expediente `2026-07-07_transcripcion_sintesis`): cazó 3 defectos reales (reglas Firestore sin `sintesis/`, 400 en `firestoreSet`, truncado chars vs bytes).
- **Reglas Firestore actualizadas (07-07):** bloque owner-based para `sintesis/` desplegado (ruleset `3dc59963`). Regla operativa nueva: colección en el schema ⇒ verificar reglas desplegadas antes de estrenarla.
- **Entorno GCP verificado (07-07):** config gcloud `actaexpress`; billing OFF (suficiente por ahora; Blaze exige desvincular otro proyecto — cupo 5/5); Gemini API en `gen-lang-client-0046942155` tier gratuito (decisión de gobernanza pendiente).
- **Integración con GitHub exitosa:** Repositorios conectados y subidos correctamente usando PAT.
- **Configuración de Firebase en Backend:** El SDK de Admin de Firebase ya está configurado en BitácoraExpress (`keys/`).
- **BitácoraExpress MVP Completado:** Interfaz de conciliación con evidencia, agrupación masiva de saltos de ventana, borrado y creación de proyectos virtuales, todo conectado a Firebase.
- **Frontend Modularizado:** Refactorización arquitectónica de BitácoraExpress para separar CSS y JS de la vista HTML (`index.html`).
- **Pipeline Documental Automatizado:** Script en Python que renderiza flujos de Mermaid a PNG y los empaqueta en `.docx` con timestamp.
- **Privacidad y Vectorización:** Se decidió delegar la privacidad al cliente (horarios laborales) para que Firestore sea un "Cerebro Aislado".

---

## 🚀 Próximos 5 Pasos Globales (priorizados)

1. **[ActaExpressWeb] MT-04:** frontend envía `generarSintesis: true` (toggle de UX a decidir por el Director).
2. **[ActaExpress Android]** Añadir campo `plataforma: "android"` al guardar actas y lograr paridad de exportación.
3. **[NexoExpress]** Costos de Cloud Functions/Vertex AI para vectorización + decisión de billing (cupo 5/5, hay que desvincular un proyecto).
4. **[Gobernanza]** Tier de Gemini API: gratuito (datos usables por Google) vs pagado — afecta privacidad del audio de reuniones.
5. **[ActaExpressWeb]** Observación: actas de reuniones en inglés salen en español pese al prompt (ciclo propio si se prioriza).

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
