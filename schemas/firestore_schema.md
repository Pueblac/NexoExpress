# Esquema Firestore — Contrato de Datos del Ecosistema Express

> **Mantenido por:** NexoExpress (Coordinador del Ecosistema)
> **Última modificación:** 24-06-2026
> **Regla:** Ningún proyecto puede crear una colección no documentada aquí.

---

## Colecciones Activas

### `users/{uid}`
**Quién escribe:** ActaExpressWeb, ActaExpress Android
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
  "meetingsUsed": 0
}
```

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
> ⚠️ `plataforma` — campo nuevo, permite saber el origen del acta

---

### `sintesis/{actaId}` ← PENDIENTE (Fase 1)
**Quién escribe:** ActaExpressWeb, ActaExpress Android
**Quién lee:** Sistema contextual (Fase 3)
**Razón de separación:** Documentos grandes. No inflar la colección `actas/` que se lee frecuentemente.

```json
{
  "actaId": "string (referencia)",
  "transcripcion": "string (texto completo hablado)",
  "analisis_profundo": "string (análisis temático, tensiones, puntos no explícitos)",
  "preguntas_sin_resolver": ["string"],
  "temas_clave": ["string"],
  "contexto_previo": "string (relación con reuniones anteriores del mismo folder)",
  "createdAt": "timestamp"
}
```

---

### `folders/{folderId}` ← PENDIENTE (Fase 2)
**Quién escribe:** ActaExpressWeb, ActaExpress Android
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

### `be_actividades/{actividadId}` ← BitácoraExpress (PENDIENTE migración)
**Quién escribe:** BitácoraExpress
**Quién lee:** BitácoraExpress, sistema contextual (Fase 3)
**Estado actual:** SQLite local. Pendiente migración a Firestore.

```json
{
  "ownerId": "uid",
  "proyectoId": "string | null",
  "ventanaTitulo": "string",
  "duracionSegundos": 120,
  "evidenciaUrl": "string | null",
  "sistemaOperativo": "windows | linux | darwin",
  "timestamp": "timestamp"
}
```

---

### `be_proyectos/{proyectoId}` ← BitácoraExpress (PENDIENTE migración)
**Quién escribe:** BitácoraExpress
**Quién lee:** BitácoraExpress

```json
{
  "ownerId": "uid",
  "name": "string",
  "status": "active | archived",
  "folderPath": "string | null",
  "createdAt": "timestamp"
}
```

---

### `be_bitacoras/{fecha}` ← BitácoraExpress (PENDIENTE)
**Quién escribe:** BitácoraExpress (generada por Gemini al final del día)
**Quién lee:** Sistema contextual (Fase 3)

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

## Colecciones Futuras (Fase 3)

| Colección | Propósito |
|---|---|
| `contextos/{uid}` | Índice de ámbitos para el sistema de inteligencia contextual |
| `docs_subidos/{docId}` | Documentos subidos manualmente (PPTs, actas externas, etc.) |

---

## Reglas de Seguridad Firestore (lineamientos)

- Todo documento debe tener `ownerId` = `uid` del usuario autenticado.
- Las reglas deben verificar `request.auth.uid == resource.data.ownerId`.
- Colecciones de BitácoraExpress (`be_*`) son privadas — solo el propietario puede leer/escribir.
- `actas/` puede ser compartida en el futuro (campo `sharedWith: [uid]`), diseñar pensando en eso.
