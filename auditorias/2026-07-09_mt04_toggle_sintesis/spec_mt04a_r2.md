# Spec MT-04a — ronda 2 (F3', resolución de la duda del informe_mt04a)

**Ciclo:** 2026-07-09_mt04_toggle_sintesis · **Emitida por:** Arquitecto, 09-07-2026
**Naturaleza:** resolución de duda (protocolo §6 de spec_mt04a). **No requiere trabajo nuevo del Ingeniero** — el entregable de F4 queda ACEPTADO tal como está; esta spec amplía el alcance y responde las 3 preguntas del informe. Se archiva como registro del expediente.

## Respuestas del Arquitecto (verificadas contra el repo, no de memoria)

**P1 — ¿El drift es contrato aprobado o trabajo ajeno mezclado?**
Contrato APROBADO. Verificado: `git log -- lib/api-spec/openapi.yaml` muestra que el último cambio del yaml es `6811f56` — el commit del ciclo `2026-07-07_transcripcion_sintesis` (cerrado, auditado y pusheado). Ese ciclo añadió al yaml `generarSintesis`, `plataforma` (enum `web`/`android`, regla 4 del ecosistema) y `updatedAt`; el backend desplegado escribe `plataforma: "web"` y `updatedAt` desde entonces (evidencia CTX-3 del expediente anterior). El drift existe porque nadie regeneró clientes tras ese commit — la misma causa raíz por la que faltaba `generarSintesis`. No hay trabajo en curso de otra rama.

**P2 — ¿Mismo diff/commit o separar en dos?**
UN solo diff/commit (cuando el Director autorice F7). Razones: (a) el diff es producto atómico de un único comando reproducible (`codegen`); partirlo exigiría staging parcial de archivos generados — artesanal, frágil y contrario a "no editar generated a mano"; (b) la trazabilidad la da el expediente, no la partición del commit; (c) el mensaje de commit declarará la sincronización completa.

**P3 — ¿Cómo aislar generarSintesis?**
No se aísla. La pregunta queda sin objeto al aceptarse el drift (P1).

## Alcance ampliado de MT-04a (vinculante)

> MT-04a pasa de "exponer `generarSintesis`" a **"sincronizar los clientes generados con el `openapi.yaml` vigente"** (que incluye `generarSintesis`, `plataforma`, `updatedAt`, `ActaPlataforma`).

Verificación F5 del Arquitecto (ejecutada, no leída — ver anexo en `informe_mt04a.md`): todos los hunks del diff mapean 1:1 a líneas del yaml vigente; `ActaPlataforma` = enum `["web","android"]` del yaml (líneas 192-194); typecheck del workspace EXIT=0 re-ejecutado por el Arquitecto. Los campos nuevos de `Acta` son opcionales → cambio aditivo, sin ruptura de consumidores.

## Estado resultante

- **MT-04a: CERRADA en F5** (entregable aceptado con alcance ampliado; working tree de ActaExpressWeb conserva los cambios sin commit, como debe).
- La regla de diff limpio de la spec original FUNCIONÓ según diseño: detectó el drift, lo detuvo y lo subió a decisión. La ampliación quedará visible íntegra en el `git diff` que irá al Auditor en F6.
- **Nota para la retro del piloto:** caso nuevo para la metodología — "duda resuelta sin trabajo nuevo": la spec r2 puede cerrar el turno del Ingeniero sin transporte cuando el entregable de F4 ya satisface el contrato ampliado.

━━ AVISO DE TRASPASO ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CICLO      : 2026-07-09_mt04_toggle_sintesis
FASE       : F3' cerrada → F5 MT-04a cerrada → F3→F4 de MT-04b
TURNO DE   : Director
ENTREGAR   : spec_mt04b.md (ya archivada en el expediente)
ADJUNTOS   : Ninguno
DESTINO    : Sesión NUEVA de Claude Sonnet sobre ActaExpressWeb
             (inicialización de identidad primero, ver AVISO de la spec)
ACCIÓN     : Que el Ingeniero implemente MT-04b sobre el working tree
             actual (que ya contiene MT-04a sin commit — declarado en
             el DoD 1 de la spec)
VUELVE A   : Arquitecto, con informe_mt04b.md → F5
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
