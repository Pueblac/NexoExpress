# Ecosistema Express — Visión y Arquitectura Global

> **Mantenido en:** `NexoExpress` (Coordinador del Ecosistema)
> **Última actualización:** 26/06/2026

---

## 🗺️ La Arquitectura de 3 Capas

A medida que el ecosistema evoluciona, se hace evidente que necesitamos separar las responsabilidades. El ecosistema se divide conceptualmente en tres grandes capas:

### Capa 1: Recolección de Información (Los "Sensores")
Aplicaciones cuyo único propósito es capturar información sin fricción y guardarla estructurada en Firestore.
- **ActaExpressWeb:** Captura de reuniones formales en PC.
- **ActaExpress Android:** Captura de reuniones formales en terreno.
- **BitácoraExpress:** Captura del trabajo diario, esfuerzo y herramientas en background, respetando la privacidad (horarios configurables, detección pausada).

### Capa 2: Análisis de Información (El "Cerebro")
Servicios que procesan, vectorizan y conectan la información recolectada. (Proyectos separados de las apps de recolección).
- **Motor RAG / Inteligencia Contextual:** Transforma las actas (colección `sintesis`) y los resúmenes diarios (`be_bitacoras`) en vectores para responder consultas.
- **Gestión del Conocimiento Histórico:** Entiende el ciclo de vida de los proyectos. Si un proyecto como "ENA 2026" termina, su aprendizaje se sintetiza y se pasa a "ENA 2027", evitando que la IA se contradiga con decisiones obsoletas del pasado.

### Capa 3: Reportería (El "Espejo Analítico")
- Dashboards y métricas semanales que analizan el esfuerzo vs. resultados. Esta capa no busca razonamiento profundo de IA, sino cruce de datos numéricos y reportes ejecutivos consolidados a partir de `be_proyectos` y `be_actividades`.

---

## 📱 Las Tres Herramientas de Recolección (Capa 1)

### 1. ActaExpress (Android)
- **Estado:** MVP core funcionando en dispositivo real (~60%)
- **Entrada:** Micrófono del celular
- **Procesamiento:** Gemini 2.5 Flash
- **Salida:** Acta en Firestore (`actas/` con `plataforma: "android"`)

### 2. ActaExpressWeb
- **Estado:** Principal prototipo del ecosistema (~82%)
- **Entrada:** Micrófono del sistema O captura de pestaña (YouTube, Teams)
- **Procesamiento:** Gemini 2.5 Flash vía API Server
- **Salida:** Acta + `sintesis/` + Export DOCX/TXT

### 3. BitácoraExpress (Desktop - Python)
- **Estado:** Activo en Linux/Windows (~48%), migrando SQLite a Firestore
- **Entrada:** Watcher en background captura título de la ventana activa, filtrado por configuración de privacidad del usuario (horarios laborales, modo off).
- **Procesamiento:** FastAPI backend agrupa tiempos por proyecto; Gemini resume el día.
- **Salida:** `be_actividades/` y `be_bitacoras/` en Firestore

---

## ❓ Decisiones Clave de Diseño y Privacidad

### 1. Aislamiento Total (Cerebro Aislado)
Las actas y bitácoras son estrictamente personales en la base de datos. Si deseas compartir un acta, la exportas (PDF, DOCX) y la envías por Drive o correo. La base de datos y el motor RAG nunca mezclarán información de múltiples usuarios, garantizando la privacidad absoluta de tu contexto.

### 2. Privacidad y el Límite Personal/Laboral
Para evitar que BitácoraExpress capture información confidencial fuera del trabajo, la herramienta integrará configuraciones de **horario laboral** y un botón de **pausa manual**. El usuario acepta que, dentro del horario activo, se registrarán las cabeceras, confiando en el modelo de "Cerebro Aislado" donde solo él tiene acceso a sus datos.

### 3. El Ciclo de Vida del Contexto (Proyectos)
El contexto no es infinito. Se agrupa en **Proyectos** (`be_proyectos`) con inicio y fin (ej. anualmente). Esto evita la "contaminación" histórica de decisiones y permite trasladar aprendizajes ordenados de una iteración a otra sin confundir a la IA.

---

## 🗓️ Roadmap Global por Fases

### Fase 1 — Paridad básica y Estabilización (Actual)
✅ **[ActaExpressWeb]**: Implementar colección `sintesis/` y `plataforma: "web"`.
⚠️ **[BitácoraExpress]**: Finalizar migración local (SQLite) a Firebase (`be_proyectos/`, `be_actividades/`).
✅ **[NexoExpress & BitácoraExpress]**: Push a GitHub de los repos locales completado con éxito.
⏳ **[ActaExpressWeb]**: Enriquecer el prompt para incluir la transcripción completa (mejora la síntesis).
⏳ **[ActaExpress Android]**: Añadir campo `plataforma: "android"` y lograr paridad de exportación y síntesis.

### Fase 2 — Organización e Integración (Capa 1)
⏳ **Privacidad Frontend**: Agregar interfaz de configuración de horarios y botón de pausa a BitácoraExpress.
⏳ **Carpetas/Proyectos**: Implementar la organización y ciclo de vida en ambas apps ActaExpress.
⏳ **Asignación de Actas**: Vincular un acta a un `be_proyectos/{id}`.

### Fase 3 — Inteligencia (Capa 2) y Reportería (Capa 3)
⏳ **Capa Vectorial**: Implementar Firestore Vector Search para `sintesis` y `be_bitacoras`.
⏳ **Motor de profundización**: RAG aislado para conversar con tu propio contexto.
⏳ **Capa de Reportería Semanal**: Dashboard de analítica del esfuerzo (separado de la IA profunda).

---

> **Última revisión:** 26-06-2026
> **Regla de NexoExpress:** La versión Web es el prototipo. Toda feature se construye primero en Web. El schema unificado en `schemas/` es la única fuente de verdad.
