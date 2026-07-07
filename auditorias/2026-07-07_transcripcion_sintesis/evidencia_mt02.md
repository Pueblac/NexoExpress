# Evidencia E2E — MT-02 (07-07-2026)

Audio sintetizado (ffmpeg flite, 2 voces, 29.3s) → POST /api/actas/process con generarSintesis:true, usuario de prueba mt02-e2e-test (idToken real acuñado con la service account).

## Respuesta 201 (10.7s, solo acta):
```json
{"id":"HwewR3jTMUdopfVzqCVN","titulo":"Reunión de Planificación Semanal del Proyecto Nexo","fecha":null,"duracionMinutos":1,"participantes":["John","Maria"],"resumen":"La reunión semanal de planificación del proyecto Nexo se centró en la decisión de la fecha de lanzamiento. Se acordó que el lanzamiento será el viernes 10 de julio, con la funcionalidad de transcripción lista para pruebas.","puntosImportantes":["Decisión de la fecha de lanzamiento del proyecto Nexo","La funcionalidad de transcripción está lista para pruebas"],"acuerdos":["La fecha de lanzamiento del proyecto Nexo será el viernes 10 de julio"],"pendientes":[{"tarea":"Preparar la lista de verificación de despliegue","responsable":"Maria","fecha":"Antes del jueves"}],"ownerId":"mt02-e2e-test","plataforma":"web","audioStoragePath":null,"createdAt":"2026-07-07T12:27:30.772Z","updatedAt":"2026-07-07T12:27:30.772Z"}
```

## Documento sintesis/HwewR3jTMUdopfVzqCVN (GET literal Firestore REST):
```json
{
    "name": "projects/actaexpress/databases/(default)/documents/sintesis/HwewR3jTMUdopfVzqCVN",
    "fields": {
        "actaId": {
            "stringValue": "HwewR3jTMUdopfVzqCVN"
        },
        "contexto_previo": {
            "stringValue": ""
        },
        "ownerId": {
            "stringValue": "mt02-e2e-test"
        },
        "preguntas_sin_resolver": {
            "arrayValue": {
                "values": [
                    {
                        "stringValue": "\u00bfCu\u00e1l es el alcance completo del proyecto Nexo y qu\u00e9 otras funcionalidades, adem\u00e1s de la de transcripci\u00f3n, son cr\u00edticas para este lanzamiento?"
                    },
                    {
                        "stringValue": "\u00bfExisten otros factores o dependencias que podr\u00edan afectar la fecha de lanzamiento del 10 de julio, adem\u00e1s de la funcionalidad de transcripci\u00f3n?"
                    },
                    {
                        "stringValue": "\u00bfQu\u00e9 implicaciones tiene la fecha l\u00edmite del jueves para la \"deployment checklist\" y qu\u00e9 recursos se necesitan para completarla a tiempo?"
                    },
                    {
                        "stringValue": "\u00bfQui\u00e9n es el responsable de la ejecuci\u00f3n del despliegue una vez que la checklist est\u00e9 preparada?"
                    }
                ]
            }
        },
        "analisis_profundo": {
            "stringValue": "La reuni\u00f3n es extremadamente concisa y eficiente, lo que sugiere una cultura de trabajo muy directa y orientada a resultados. No hay rodeos ni discusiones prolongadas. La propuesta de Mar\u00eda para la fecha de lanzamiento (10 de julio) es aceptada de inmediato por John, lo que indica una fuerte alineaci\u00f3n previa o un alto nivel de confianza en el criterio de Mar\u00eda. La justificaci\u00f3n de Mar\u00eda para la fecha de lanzamiento, \"The transcription feature is ready for testing\", es un punto clave que valida la decisi\u00f3n y muestra que la fecha se basa en el progreso de una funcionalidad espec\u00edfica. La asignaci\u00f3n de la tarea de la \"deployment checklist\" a Mar\u00eda con una fecha l\u00edmite clara (\"before Thursday\") demuestra una delegaci\u00f3n de tareas efectiva y un seguimiento inmediato de las decisiones tomadas. La reuni\u00f3n concluye abruptamente una vez que se ha tomado la decisi\u00f3n principal y se ha asignado la siguiente acci\u00f3n, lo que refuerza la eficiencia y el enfoque en la acci\u00f3n. No se perciben tensiones ni desacuerdos, lo que apunta a un equipo cohesionado y bien coordinado."
        },
        "transcripcion": {
            "stringValue": "John: Good morning team. This is the weekly planning meeting for the Nexo project. Today we must decide the release date.\nMaria: Thanks John. I reviewed the backlog and I propose we release on Friday, July 10th. The transcription feature is ready for testing.\nJohn: Agreed. Then we decide the release is Friday, July 10th. Maria will prepare the deployment checklist before Thursday.\nMaria: Perfect. I take the pending task, deployment checklist by Thursday. Meeting closed. Thank you everyone."
        },
        "createdAt": {
            "stringValue": "2026-07-07T12:27:38.268Z"
        },
        "temas_clave": {
            "arrayValue": {
                "values": [
                    {
                        "stringValue": "Planificaci\u00f3n de lanzamiento del proyecto Nexo"
                    },
                    {
                        "stringValue": "Decisi\u00f3n de fecha de lanzamiento (10 de julio)"
                    },
                    {
                        "stringValue": "Preparaci\u00f3n de la funcionalidad de transcripci\u00f3n"
                    },
                    {
                        "stringValue": "Preparaci\u00f3n de la lista de verificaci\u00f3n de despliegue"
                    },
                    {
                        "stringValue": "Asignaci\u00f3n de tareas y plazos"
                    }
                ]
            }
        }
    },
    "createTime": "2026-07-07T12:27:38.346436Z",
    "updateTime": "2026-07-07T12:27:38.346436Z"
}
```

## Hallazgos colaterales corregidos en esta MT:
1. Reglas Firestore desplegadas NO cubrían sintesis/ (403 silencioso; trampa T3 confirmada en producción). Se desplegó ruleset 3dc59963-f465-4106-bb13-8929bad36c92 con aprobación del Director (ver firestore_rules_desplegadas.rules).
2. Bug latente en firestoreSet (firebaseAdmin.ts): updateMask.fieldPaths con comas → 400 INVALID_ARGUMENT reproducido con curl; corregido a parámetro repetido. A/B literal: con comas = 'Invalid property path "actaId,ownerId"'; sin mask/reparado = documento creado.
