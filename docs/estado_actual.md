# Estado Actual — NexoExpress (Coordinador del Ecosistema)

**Estado Global del Ecosistema:** 🟢 VERDE
**Última Actualización:** 09-07-2026
**Metodología vigente:** v2 Triple-IA (`docs/METODOLOGIA_TRIPLE_IA.md`, adoptada 09-07-2026)

---

## ✅ Checklist de Micro-Tareas Vigente

**Meta (PILOTO v2 — CERRADA 13-07-2026):** [ActaExpressWeb] MT-04: toggle "Análisis profundo" → `generarSintesis: true`. **Primer ciclo de código completo bajo la metodología v2**: F0→F7 con 2 rondas de diseño + 1 de código; auditoría final de Gemini **APROBADO** ("listo para merge"), anti-bluff VÁLIDA; persistencia confirmada; commits `0e35253` (ActaExpressWeb linux) y `05d0539` (NexoExpress).
**Expediente:** `auditorias/2026-07-09_mt04_toggle_sintesis/` (15 archivos)
**Hallazgo de F0:** `openapi.yaml` ya declara `generarSintesis` (línea 218, ciclo anterior), pero los clientes generados (`lib/api-client-react`, `lib/api-zod`) NO lo incluyen — la regeneración es prerrequisito del toggle.

- [x] **MT-04a** — Regenerar los clientes API desde `lib/api-spec/openapi.yaml` (alcance ampliado en `spec_mt04a_r2.md`: sincronización completa con el yaml vigente — incluye drift aprobado `plataforma`/`updatedAt`/`ActaPlataforma` del ciclo 07-07). — **DoD cumplido y re-ejecutado en F5 (09-07-2026):** grep devuelve el campo en ambos paquetes; typecheck EXIT=0; mapeo hunk→yaml 1:1. El Ingeniero aplicó DETENTE por la regla de diff limpio (funcionó según diseño); duda resuelta en F3' sin trabajo nuevo. Cambios sin commit en el working tree (F7 pendiente).
- [x] **MT-04b** — Toggle "Análisis profundo" en `home.tsx` (rotación asistida: subagente Sonnet; F5 código verificada por el Arquitecto). — **DoD cumplido (13-07-2026):** E2E real con guion como ground truth — toggle ON → `sintesis/g1oWHvziNoalE9ESxepg` con transcripción FIEL (capturó hasta un lapsus del hablante que no estaba en el guion) y diarización correcta; OFF → sin síntesis; multi-grabación sin B1; acta ~10s, síntesis +10s. Evidencia literal en `evidencia_mt04.md`. *(Confirmación visual de persistencia tras reload: pendiente, respaldada por código.)*

**Cursor:** **CICLO CERRADO (13-07):** auditoría de código APROBADO + anti-bluff válida + persistencia confirmada + commits pusheados. **Siguiente: retro del piloto + `roadmap_manager`** — el Director prioriza entre los ciclos candidatos: "captura confiable" (H3+H4), "robustez del pipeline" (H1+H2+H5), "resiliencia de grabación" (H6), billing/Vertex (pendientes #3/#4). Contexto histórico: E2E del 11-07 **verificó la plomería del flag** (ON → `sintesis/` poblada por el mismo request; OFF → sin síntesis; multi-grabación OK) — evidencia con logs literales y lecturas Firestore en `evidencia_mt04.md`. **Pendiente:** pruebas restantes del Director (persistencia tras reload + prueba de pestaña con audio) → F6 (auditoría tanda MT-04a+b) → F7. **Hallazgos del piloto (ciclos propios, NO tomar sin F0):** H1 doble alucinación de Gemini sobre audio casi mudo (10.5KB/42s) que bypasea la heurística anti-silencio; H2 thinking devora el presupuesto de síntesis (62.912 de 65.536 tokens, latencia 4 min, riesgo MAX_TOKENS en reuniones reales — fix candidato: `thinkingBudget: 0`); H3 captura Linux solo da audio de sistema por pestaña + **dirección de producto del Director (12-07): selector explícito "Reunión virtual" (pestaña+mic) / "Reunión presencial – sonido ambiente" (mic directo, sin diálogo)**; sin avisos a terceros — requisito del Director satisfecho; **H4** detector de señal de micrófono en cliente (aviso "tu micrófono está apagado" vía AnalyserNode — UX del Director; causa raíz de los silencios CONFIRMADA: mic apagado en el SO). H3+H4 candidatos a ciclo conjunto "captura confiable"; **H5** espera y audios largos: timeout duro de 40s en `waitForFileActive` (rompería con audios de ~1h), procesamiento atado a la pestaña (cerrarla pierde el acta), y UX de expectativa ("puede tardar, sigue en otra pestaña") + síntesis invisible al terminar. **12-07 tarde: PRIMERA ACTA FIEL E2E** (modo rápido, mic presencial) — pipeline verificado con audio real; **H6** resiliencia de grabación (13-07): autoguardado de chunks en IndexedDB + recuperación al reabrir (Fase 1 recomendada); transcripción incremental NO recomendada como parche (streaming Live API = Fase 3); aclarado que el timeout de File API no es cola del tier gratuito — Vertex/tier pagado se justifica por privacidad y rate limits (depende de billing, pendientes #3/#4).

---

## 📁 Meta anterior (CERRADA 09-07-2026)

**Meta (CERRADA 09-07-2026, commit `b23dff7` pusheado):** [NexoExpress] Diseñar y adoptar la METODOLOGÍA v2 (Triple-IA): Fable 5 Arquitecto / Claude Sonnet Ingeniero / Gemini 3.1 Pro High Auditor.
**Expediente:** `auditorias/2026-07-08_metodologia_v2/`

- [x] **MT-01** — Borrador de `docs/METODOLOGIA_TRIPLE_IA.md` (roles, fases F0–F7, artefactos de traspaso spec/informe, AVISO estándar, gates humanos G0–G2, evaluación Modo M vs Modo A, excepciones y plan de adopción). — **DoD cumplido (08-07-2026):** doc completo + prompt de revisión archivado en `auditorias/2026-07-08_metodologia_v2/prompt_diseno_ronda1.md` y entregado al Director.
- [x] **Veredicto ronda 1 (08-07-2026): APROBADO CON CAMBIOS** — respuesta archivada en `respuesta_diseno_ronda1.md` con validación anti-bluff anexada (VÁLIDA; 1 observación: la premisa de C4 sobre incapacidad de ejecución del Arquitecto era incorrecta por omisión del prompt, cambio 3 incorporado con precisión). Los 5 cambios + Q1/Q3/D4 incorporados al borrador.
- [x] **Gate de adopción (09-07-2026):** el Director aprobó adoptar la v2 ("continuemos con el plan"). `METODOLOGIA_TRIPLE_IA.md` marcada VIGENTE; `METODOLOGIA_DUAL_IA.md` marcada HISTÓRICA/fallback.
- [x] **MT-02 (BLOQUEANTE antes del piloto, dictamen r1 cambio 5)** — Actualizados al ciclo v2: `PROMPT_ARRANQUE_SESION.md` (plantilla de Arquitecto), skills `auditor_externo` (diff íntegro F6, init de identidad, dudas del Ingeniero, F5 previo) y `roadmap_manager` (F0/G0), README (regla 5, árbol, fecha), skill `innovador` (colateral detectado por grep) y `arranque_proxima_sesion.md` regenerado para el piloto. — **DoD cumplido (09-07-2026):** `grep -rni "dual"` sobre los documentos operativos devuelve únicamente la línea intencional del README que marca la v1 como "histórica — fallback operativo (v2 §7)"; cero referencias operativas huérfanas.

*(Cursor histórico: G2 concedido el 09-07-2026; ciclo commiteado y pusheado — `b23dff7` — con bitácora `bitacora_09_07_2026.md`.)*

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

- **Metodología v2 Triple-IA adoptada (09-07):** ciclo F0–F7 con Fable Arquitecto / Sonnet Ingeniero / Gemini Auditor; auto-auditada por Gemini (APROBADO CON CAMBIOS r1, 5 cambios incorporados) y commiteada (`b23dff7`). v1 queda como fallback. Piloto: MT-04.
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
