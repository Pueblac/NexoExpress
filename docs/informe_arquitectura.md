# Informe Arquitectónico y Cloud — Ecosistema Express

**Fecha:** 27-06-2026
**Analista:** Arquitecto de Ecosistema y Software
**Proyectos Analizados:** ActaExpressWeb, BitácoraExpress, NexoExpress

---

## 1. Visión End-to-End del Ciclo de Vida de los Datos
El ecosistema actualmente captura información desde la máquina local (BitácoraExpress) y aplicaciones front-end (ActaExpress). 
El flujo crítico es: **Captura Local -> API Local / Cliente Web -> Google Cloud Firestore -> Modelos LLM (Gemini) -> Base de Conocimiento (Vector Search)**.

## 2. Hallazgos y Desafíos Estructurales

### 2.1. Escalabilidad y Costos de Lectura (Firestore)
- **Riesgo:** BitácoraExpress inserta cientos de micro-registros diarios en la colección `be_actividades` (saltos de ventana rápidos). Si el futuro motor RAG o la IA leen directamente esta colección para consultar contexto histórico, los costos operativos (Facturación por Document Reads en GCP) crecerán drásticamente de forma insostenible.
- **Solución Evaluada:** La arquitectura dictada en el esquema actual estipula que la IA **solo** debe leer `be_bitacoras/` (un documento resumen por día) en lugar de la data cruda. Este límite arquitectónico es vital y está diseñado correctamente.

### 2.2. Aislamiento, Seguridad y Admin SDK
- **Riesgo:** Actualmente, las aplicaciones locales (como BitácoraExpress) se comunican con Firestore usando credenciales de **Firebase Admin SDK**. Esto significa que el backend local tiene acceso de superusuario a la base de datos, saltándose las *Firestore Security Rules*.
- **Solución a Futuro:** Para uso exclusivamente personal (MVP) en un PC seguro, esto es aceptable. Sin embargo, si la suite Express se distribuye a otros usuarios, se debe migrar al SDK Cliente (Firebase Auth) para que los tokens de sesión restrinjan estrictamente la lectura a `request.auth.uid == resource.data.ownerId`.

### 2.3. Cuello de Botella: Vectorización y Triggers (Fase 3)
- **Desafío:** La promesa del ecosistema es un "Cerebro Aislado" (RAG). Para ello, cada acta y bitácora debe ser transformada a vectores numéricos (Embeddings).
- **Riesgo Operacional:** Si la vectorización se hace sincrónicamente (esperando a que Gemini devuelva el vector antes de que el usuario vea el "Guardado con éxito"), la latencia frustrará al usuario.
- **Recomendación:** Usar **Firebase Cloud Functions** (Background Triggers). Cuando un documento se escribe en Firestore, un evento `onDocumentCreated` debe disparar asíncronamente el llamado a Vertex AI para calcular el embedding, sin bloquear la interfaz del usuario.

## 3. Propuestas de Mejora Concretas (Arquitectura)

1. **Garbage Collection (Recolección de Basura):** Los registros crudos en `be_actividades` pierden su valor principal una vez que el Agente IA genera el resumen diario en `be_bitacoras`. Propongo diseñar una política de expiración (TTL en Firestore o un Cron Job de GCP) que purgue las actividades huérfanas de más de 30 días para ahorrar cuota de almacenamiento gratuito.
2. **Consolidación de Evidencias de Texto:** Actualmente, las evidencias largas en texto se guardan crudas. Si se almacenan muchas actas pesadas directamente en el documento de Firestore, podríamos golpear el límite de 1MB por documento. Se debe vigilar este límite en `ActaExpressWeb`.

## 4. Requerimientos para `@/disenador_flujos`
Basado en este análisis de arquitectura Cloud, se solicita al Diseñador de Flujos que genere **dos diagramas Mermaid**:
1. **Flujo de Vectorización Asíncrona:** Un diagrama que ilustre cómo un Acta/Bitácora llega a Firestore -> dispara una Cloud Function -> consulta a Vertex AI (Text Embeddings) -> y guarda el vector de vuelta en Firestore.
2. **Ciclo de Vida de la Data Local a Cloud:** Mostrando el filtro de privacidad local (horarios), el viaje al backend, la consolidación, y la purga a los 30 días (Garbage Collection).
