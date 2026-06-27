# Esquema Firestore — Contrato de Datos del Ecosistema Express

> **Mantenido por:** NexoExpress (Coordinador del Ecosistema)
> **Última modificación:** 26-06-2026
> **Regla:** Ningún proyecto puede crear una colección no documentada aquí.

---

## Colecciones Activas

### `users/{uid}`
**Quién escribe:** ActaExpressWeb, ActaExpress Android, BitácoraExpress
**Quién lee:** Todos los proyectos

```json
{
  "displayName": "string",
  "email": "string",
  "photoURL": "string",
  "subscriptionTier": "free | premium_monthly | premium_annual",
  "isPremium": false,
  "remainingCredits": 25000,
  "rolloverCredits": 0,
  "nextRefillDate": "timestamp",
  "createdAt": "timestamp",
  "meetingsUsed": 0,
  "preferences": {
    "trackingActivo": true,
    "horariosLaborales": [
      { "dia": "Lunes", "inicio": "09:00", "fin": "18:00" }
    ]
  }
}
```
> **Nota de Privacidad:** `preferences` permite al cliente de BitácoraExpress pausar la recolección automáticamente fuera del horario laboral, asegurando que los sitios privados del usuario no se suban a la base de datos.

---

### `actas/{actaId}`
**Quién escribe:** ActaExpressWeb, ActaExpress Android
**Quién lee:** ActaExpressWeb, ActaExpress Android, futuro sistema contextual

```json
{
  "ownerId": "uid",
  "ownerName": "string",
  "titulo": "string",
  "fecha": "string | null",
  "duracionMinutos": 45,
  "participantes": ["nombre1", "nombre2"],
  "resumen": "string",
  "puntosImportantes": ["string"],
  "acuerdos": ["string"],
  "pendientes": [
    { "tarea": "string", "responsable": "string | null", "fecha": "string | null" }
  ],
  "folderId": "string | null",
  "plataforma": "web | android",
  "createdAt": "timestamp",
  "updatedAt": "timestamp"
}
```
> ⚠️ `folderId` — pendiente de implementar (Fase 2)
> ✅ `plataforma` — campo implementado en Web.

---

### `sintesis/{actaId}` 
**Quién escribe:** ActaExpressWeb (✅ Implementado), ActaExpress Android (⏳ Pendiente)
**Quién lee:** Sistema contextual (Fase 3)
**Razón de separación:** Documentos grandes. No inflar la colección `actas/` que se lee frecuentemente.

```json
{
  "actaId": "string (referencia)",
  "ownerId": "uid",
  "transcripcion": "string (texto completo hablado)",
  "analisis_profundo": "string (análisis temático, tensiones, puntos no explícitos)",
  "preguntas_sin_resolver": ["string"],
  "temas_clave": ["string"],
  "contexto_previo": "string (relación con reuniones anteriores del mismo folder)",
  "createdAt": "timestamp"
}
```

---

### `folders/{folderId}` 
**Quién escribe:** ActaExpressWeb, ActaExpress Android (⏳ Fase 2)
**Quién lee:** Todos

```json
{
  "ownerId": "uid",
  "name": "string",
  "descripcion": "string | null",
  "ambito": "laboral | cotidiano | proyecto",
  "createdAt": "timestamp"
}
```

---

### `be_actividades/{actividadId}`
**Quién escribe:** BitácoraExpress
**Quién lee:** BitácoraExpress
**Estado actual:** 🟢 Migrado a Firestore (Activo).

```json
{
  "ownerId": "uid",
  "project_id": "string | null (referencia a be_proyectos o null si es huérfana)",
  "title": "string (título de la ventana)",
  "duration": 120,
  "time": "ISO 8601 string",
  "evidence_type": "file | text | null",
  "evidence_url": "string | null (ruta local o cloud al archivo)",
  "evidence_text": "string | null (texto plano pegado por el usuario)",
  "sistemaOperativo": "windows | linux | darwin"
}
```
> **Nota Arquitectónica:** El sistema RAG futuro **NO** debe leer esta colección debido al volumen masivo de registros. Solo debe leer `be_bitacoras/`.

---

### `be_proyectos/{proyectoId}`
**Quién escribe:** BitácoraExpress
**Quién lee:** BitácoraExpress
**Estado actual:** 🟢 Migrado a Firestore (Activo). Soporta proyectos virtuales sin carpeta.

```json
{
  "ownerId": "uid",
  "name": "string",
  "status": "active | archived",
  "fechaInicio": "YYYY-MM-DD | null",
  "fechaFin": "YYYY-MM-DD | null",
  "tags": ["string"],
  "folderPath": "string | null",
  "createdAt": "ISO 8601 string"
}
```
> **Nota de Contexto (Herencia):** Los campos `fechaInicio` y `fechaFin` permiten delimitar el contexto (ej. "ENA 2026" vs "ENA 2027"). Al cerrar un proyecto, su síntesis se empaqueta y puede ser heredada por el siguiente.

---

### `be_bitacoras/{fecha}`
**Quién escribe:** BitácoraExpress (generada por IA al final del día)
**Quién lee:** Sistema contextual (Fase 3)
**Estado actual:** ⚠️ Pendiente migración.

```json
{
  "ownerId": "uid",
  "fecha": "YYYY-MM-DD",
  "bitacora": "string (texto generado por IA)",
  "actividades": ["resumen de actividades del día"],
  "proyectosActivos": ["string"],
  "createdAt": "timestamp"
}
```

---

## 🧠 Viabilidad Técnica: Sistema de Inteligencia Contextual (Fase 3)

1. **Aislamiento de Cerebro (Privacidad):** Las actas y bitácoras son estrictamente personales (`ownerId`). Compartir un acta hacia afuera (PDF, Drive) es una acción de exportación explícita, no una mezcla de bases de datos internas. El RAG es un "Cerebro Aislado" por usuario.
2. **Capa Vectorial (RAG):** El sistema contextual usará Firestore Vector Search (añadiendo embeddings a `sintesis` y `be_bitacoras`) en lugar de leer texto crudo, lo cual disminuye costos e incrementa velocidad.

---

## Reglas de Seguridad Firestore (lineamientos)

- Todo documento debe tener `ownerId` = `uid` del usuario autenticado.
- Las reglas deben verificar `request.auth.uid == resource.data.ownerId`.
- El esquema asume **aislamiento total por usuario**. No existen lecturas compartidas a nivel de base de datos para preservar la privacidad de las actas y bitácoras.
