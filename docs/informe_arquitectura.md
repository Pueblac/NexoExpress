# Informe de Arquitectura — Suite Express (Cloud & Local)

## 1. Visión Global
El Ecosistema Express ha madurado hacia una arquitectura de 3 capas claramente delimitadas, donde Firestore actúa como la única fuente de verdad y puente de comunicación:
- **Capa 1 (Recolección):** ActaExpressWeb, ActaExpress Android, BitácoraExpress. Su foco es la baja fricción en la captura y el respeto a la privacidad mediante filtros locales (horarios laborales).
- **Capa 2 (Inteligencia / RAG):** El "Cerebro Aislado" que asimila las síntesis formales y los resúmenes de bitácora mediante búsquedas semánticas.
- **Capa 3 (Reportería):** Visualización analítica del esfuerzo y uso de tiempo, sin necesidad de inferencia profunda.

## 2. Hallazgos y Desafíos Técnicos (Cloud)

### A. Escalabilidad y Costos (RAG vs Firestore)
El modelo conceptual inicial sugería que la IA leería múltiples documentos completos (como toda la colección `sintesis`) al vuelo. **Riesgo:** Hacer esto para cada prompt destrozará los límites de la capa gratuita de Firestore (50k lecturas/día) y añadirá latencia inaceptable al Asistente.
**Mitigación Obligatoria:** Implementar **Firestore Vector Search**. El cliente solo pedirá los *Top-K* documentos más similares a la pregunta.

### B. Latencia de Ingesta (El Pipeline de Embeddings)
El cliente frontend/local no debe calcular embeddings matemáticos. Se recomienda delegar esto a Cloud Functions: cuando se crea una síntesis, un trigger `onDocumentCreated` llama a Vertex AI y guarda el vector. Esto desahoga al cliente pero introduce una latencia asíncrona de 1-2 segundos. El cliente debe estar preparado para no mostrar resultados del asistente si el vector aún no existe.

### C. Ciclo de Vida y "Amnesia Controlada"
Si un proyecto "ENA 2026" termina, y la IA lee esos datos en "ENA 2028", se generarán contradicciones ("Alucinación de Vigencia"). 
**Propuesta Arquitectónica:** Cuando un proyecto de `be_proyectos` marque `status: archived` y pase su `fechaFin`, se debe invocar a Gemini para generar un "Documento de Traspaso" súper-sintetizado. Los vectores de "ENA 2026" se excluyen de la búsqueda diaria (se filtran en la query), y solo se vectoriza el Documento de Traspaso.

### D. Seguridad e Inmutabilidad
Las reglas de Firestore garantizan aislamiento por `ownerId`. No obstante, `be_actividades` es una colección volátil y propensa a inflar la base de datos velozmente. Debe diseñarse una Cloud Function de limpieza (TTL) que purgue `be_actividades` de más de 30 días, ya que el contexto útil reside permanentemente en `be_bitacoras/`.

## 3. Propuesta de Flujos a Diagramar
Solicito al `diseñador_flujos` que diagrame lo siguiente:
1. **Arquitectura Global:** La separación entre las 3 Capas y el bus de Firebase.
2. **Flujo de Datos RAG:** La secuencia asíncrona desde que se guarda un acta hasta que el cliente hace una búsqueda semántica.
