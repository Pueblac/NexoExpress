# Ecosistema ActaExpress — Visión y Arquitectura Global

> **Mantenido en:** `Coordinador_ActaExpress` (workspace auditor)
> **Última actualización:** 24/06/2026
> **Propósito de este workspace:** Auditar paridad de funcionalidades entre proyectos, definir la arquitectura compartida y trazar el roadmap del ecosistema completo.

---

## 🗺️ El Ecosistema Completo

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        ECOSISTEMA ACTAEXPRESS                           │
│                                                                         │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐  │
│  │  ActaExpress     │    │  ActaExpressWeb   │    │ BurócrataExpress │  │
│  │  (Android)       │    │  (Web / Chrome)   │    │  (Desktop)       │  │
│  │                  │    │                  │    │                  │  │
│  │ • Graba mic      │    │ • Graba mic      │    │ • Cada 10 seg    │  │
│  │   del celular    │    │ • Graba pestaña  │    │   envía titular  │  │
│  │ • Gemini 2.5     │    │   (YouTube/Teams)│    │   de lo que hago │  │
│  │ • Acta→Firestore │    │ • Gemini 2.5    │    │ • Agrupa por     │  │
│  │ • Capacitor      │    │ • Acta→Firestore │    │   tareas/día    │  │
│  │                  │    │ • Export DOCX/TXT│    │ • Sube docs al   │  │
│  └────────┬─────────┘    └────────┬─────────┘    │   final del día  │  │
│           │                       │              └────────┬─────────┘  │
│           └───────────────────────┴──────────────────────┘             │
│                                   │                                     │
│                    ┌──────────────▼──────────────┐                     │
│                    │      FIREBASE (compartido)   │                     │
│                    │                             │                     │
│                    │  • Firestore: actas/        │                     │
│                    │  • Firestore: sintesis/     │  ← nuevo            │
│                    │  • Firestore: bitacoras/    │  ← BurócrataExpress │
│                    │  • Auth: Google Sign-In     │                     │
│                    │  • Storage: audios (opt.)   │                     │
│                    └──────────────┬──────────────┘                     │
│                                   │                                     │
│                    ┌──────────────▼──────────────┐                     │
│                    │   SISTEMA DE INTELIGENCIA   │  ← FASE FUTURA      │
│                    │   CONTEXTUAL (NotebookLM    │                     │
│                    │   propio)                   │                     │
│                    └─────────────────────────────┘                     │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📱 Las Tres Aplicaciones Actuales

### 1. ActaExpress (Android)
- **Estado:** MVP core funcionando en dispositivo real (~Fase 4)
- **Entrada:** Micrófono del celular (capacitor-voice-recorder)
- **Procesamiento:** Gemini 2.5 Flash (llamada directa desde cliente)
- **Salida:** Acta estructurada en Firestore
- **Pendiente:** Síntesis extendida, carpetas/proyectos, copiloto en tiempo real

### 2. ActaExpressWeb
- **Estado:** ~78% MVP (más avanzada que Android)
- **Entrada:** Micrófono del sistema O captura de pestaña (YouTube, Teams)
- **Procesamiento:** Gemini 2.5 Flash vía API Server (Express en puerto 8080)
- **Salida:** Acta en Firestore + Export DOCX/TXT
- **Pendiente:** Export PDF, compartir acta, deploy

### 3. BurócrataExpress
- **Estado:** Definido en concepto, desarrollo pendiente
- **Entrada:** Texto automático cada 10 segundos (lo que hago en el PC)
- **Procesamiento:** Agrupación por tareas/contexto del día
- **Salida:** Bitácora diaria en Firestore
- **Extra:** Al final del día, el usuario sube documentos adicionales (actas, PPTs, etc.)

---

## ❓ Respuestas a las preguntas clave

### 4. ¿Es posible guardar una síntesis más larga además del acta?

**Sí, y es muy recomendable.** La propuesta: una colección separada `sintesis/`:

```json
sintesis/{actaId}
{
  "actaId": "referencia al acta",
  "transcripcion": "texto completo de lo hablado",
  "analisis_profundo": "análisis temático, tensiones, no dichos",
  "contexto_previo": "qué pasó en reuniones anteriores del tema",
  "preguntas_sin_resolver": ["¿Cuándo entrega Pedro?", "..."],
  "temas_clave": ["string"],
  "createdAt": "timestamp"
}
```

**¿Por qué colección separada?** Para no inflar `actas/` que se lee frecuentemente, y consultar la síntesis solo cuando se necesita profundizar.

### 5. ¿Por qué es importante tener más información?

La información extendida sirve para:
- **Modificar actas** con fundamento (no solo el resumen)
- **Ampliar un tema** específico sin re-escuchar el audio
- **Alimentar el sistema de inteligencia contextual** (fase futura)
- **Detectar contradicciones** entre reuniones del mismo proyecto

### 6. BurócrataExpress — ¿Cómo encaja?

Es el **tercer canal de captura de contexto**, el más granular. Mientras las actas capturan reuniones formales:

```
BurócrataExpress captura → trabajo informal, decisiones pequeñas,
                            navegación web, código escrito, contexto
                            cotidiano que nunca queda en un acta
```

Flujo de datos:
```
Cada 10 seg → texto → buffer acumulado
     ↓
Cada N minutos → IA agrupa en "tarea actual"
     ↓
bitacoras/{uid}/{fecha} en Firestore
     ↓ (fin del día)
El usuario sube docs adicionales → enriquece el contexto del día
```

---

## 🧠 El Sistema de Inteligencia Contextual (Fase Futura)

Esta es la pieza que une todo. Funciona como un **NotebookLM propio** pero con tus datos.

### Arquitectura conceptual

```
FUENTES DE CONTEXTO:
  actas/          → reuniones formales (ActaExpress Web + Android)
  sintesis/       → análisis profundo de cada reunión
  bitacoras/      → trabajo cotidiano (BurócrataExpress)
  docs_subidos/   → PPTs, textos, etc. subidos manualmente
         │
         ▼
  ÍNDICE DE ÁMBITOS:
  { laboral: [...actaIds, ...bitacoraIds],
    cotidiano: [...],
    "proyecto-X": [...] }
         │
         ▼
  MOTOR DE PROFUNDIZACIÓN:
  • El usuario elige ámbito
  • Se cargan los documentos relevantes como contexto
  • Gemini 2.5 Flash (1M tokens) procesa todo en una sola llamada
  • El usuario puede preguntar, explorar, tomar decisiones
         │
         ▼
  ASISTENTE EN TIEMPO REAL (durante reuniones):
  • Carga el contexto del ámbito activo
  • Escucha la reunión en curso (streaming)
  • Sugiere preguntas relevantes
  • Detecta compromisos no cumplidos del pasado
  • Genera respuestas posibles a preguntas que te hagan
```

### ¿Qué preguntas puede responder en tiempo real?
- *"¿Qué puedo preguntar ahora dado este contexto?"*
- *"¿Qué respuesta tengo a este problema según lo que ya sé?"*
- *"¿Qué ideas puedo aportar en este momento?"*
- *"¿Esto contradice algún acuerdo previo?"*

---

## 📊 Paridad de funcionalidades (tabla de auditoría)

| Funcionalidad | ActaExpressWeb | ActaExpress Android | Prioridad |
|---|---|---|---|
| Grabación de audio | ✅ mic + pestaña | ✅ mic celular | — |
| Procesamiento Gemini | ✅ | ✅ | — |
| Acta estructurada → Firestore | ✅ | ✅ | — |
| Export DOCX/TXT | ✅ | ❌ | 🔴 Alta |
| Export PDF | ⏳ pendiente | ❌ | 🟡 Media |
| Síntesis extendida guardada | ❌ | ❌ | 🔴 Alta (nuevo) |
| Transcripción completa guardada | ❌ | ❌ | 🟡 Media (nuevo) |
| Carpetas/Proyectos | ❌ | ❌ | 🟡 Media |
| Chat con historial | ❌ | ❌ | 🟢 Futura |
| Copiloto tiempo real | ❌ | ❌ | 🟢 Futura |

---

## 🗓️ Roadmap por fases

### Fase 1 — Paridad básica (próximas semanas)
1. **Síntesis extendida**: agregar colección `sintesis/` y guardarla al procesar acta en ambas apps
2. **Export en Android**: implementar share/export equivalente a la versión web
3. **Unificar modelo de datos Firestore**: mismo esquema en ambas apps

### Fase 2 — Organización y profundización
1. **Carpetas/Proyectos** en ambas apps (ya en ROADMAP_FUTURO.md de Android)
2. **BurócrataExpress** MVP básico (web app)
3. **Chat con historial** dentro de cada carpeta (NotebookLM básico)

### Fase 3 — Inteligencia contextual
1. **Índice de ámbitos** (laboral / cotidiano / proyecto)
2. **Motor de profundización** con Gemini como núcleo
3. **Asistente en tiempo real** durante reuniones (el más complejo)

---

## 🔧 Decisiones de arquitectura abiertas

| Decisión | Opciones | Recomendación |
|---|---|---|
| ¿Dónde vive el motor de inteligencia contextual? | Cloud Function / servidor propio / cliente | Cloud Function (escalable, sin CORS) |
| ¿Síntesis en colección separada o campo en `actas`? | Campo adicional / colección `sintesis/` | Colección separada |
| ¿BurócrataExpress es web o desktop? | Web app / Electron / extensión Chrome | Web app primero, luego extensión Chrome |
| ¿Cómo se define el "ámbito"? | Tags manuales / clasificación IA / carpetas | Carpetas + IA para sugerencias |

---

> **Regla del coordinador:** La versión Web es el prototipo. Toda feature nueva se construye primero en Web y luego se porta a Android. Este documento se actualiza al iniciar cada sesión de trabajo importante.
