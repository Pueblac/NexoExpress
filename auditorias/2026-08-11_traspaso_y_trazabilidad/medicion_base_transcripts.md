# Medición base de transcripts — ground truth congelado (11-08-2026)

**Productor:** Arquitecto Macro (Opus 5) en F1, ciclo
`2026-08-11_traspaso_y_trazabilidad`.
**Propósito:** dejar por escrito, **antes de que el script exista**, los
números reales que `scripts/analizar_sesion_ia.py` deberá reproducir. Si el
script se escribiera primero y luego se "verificara" contra sí mismo, no se
estaría verificando nada (es el mismo vicio que la regla de oro §1 prohíbe:
nadie valida su propio trabajo). Congelando la medición hoy, el DoD de
MT-T2 pasa a ser falsable.

**Método:** lectura directa de los JSONL de transcript del cliente, sin
librerías, contando únicamente campos de metadatos. **No se leyó ni un solo
campo `content`.**

**Ruta leída:** `~/.claude/projects/-home-pueblac-AndroidStudioProjects-NexoExpress/`
(un archivo `{sessionId}.jsonl` por sesión, más
`{sessionId}/subagents/agent-*.jsonl` + `agent-*.meta.json` por cada
subagente lanzado desde esa sesión).

---

## 1. Campos que el transcript SÍ expone (verificado)

Por cada línea de tipo `assistant`:

| Campo | Ejemplo real | Sirve para |
|---|---|---|
| `message.model` | `claude-opus-5` | **Identificador REAL del modelo que respondió ese turno.** |
| `effort` | `high` / `null` | Nivel de esfuerzo registrado por el cliente. `null` en sesiones de versiones anteriores. |
| `message.usage.output_tokens` | `102` | Volumen de salida. |
| `message.usage.input_tokens` / `cache_read_input_tokens` / `cache_creation_input_tokens` | `2` / `13859` / `8411` | Volumen de entrada y **eficacia real del caching** de §7.1. |
| `timestamp`, `sessionId`, `gitBranch`, `cwd`, `version` | — | Correlación con el ciclo y la máquina. |
| `isSidechain` | `false` en todos | Marca de subagente en el hilo principal (ver §3: **no se usa**). |

Por cada subagente, `agent-*.meta.json`:

| Campo | Ejemplo real | Sirve para |
|---|---|---|
| `agentType` | `general-purpose`, `Explore`, `claude` | Qué clase de subagente se lanzó. |
| `description` | `MT-B1: Ingeniero Sonnet fix basurero lista` | **Rol declarado por el emisor** — contrastable con el modelo real. |
| `model` | `sonnet` (alias) o `null` (hereda del padre) | Modelo **pedido**; el real está en el JSONL del subagente. |
| `spawnDepth` | `1` | Profundidad de anidamiento. |

---

## 2. Salida literal de la medición (11-08-2026)

```
== MEDICION BASE DE TRANSCRIPTS ==
fecha: 2026-08-11
ruta : /home/pueblac/.claude/projects/-home-pueblac-AndroidStudioProjects-NexoExpress

--- HILO PRINCIPAL (por archivo de sesion) ---
01175772  turnos= 205  modelos={'claude-fable-5': 130, 'claude-opus-4-8': 75}  effort={'None': 205}  tokens={'out': 388384, 'in': 388, 'cache_read': 35163177, 'cache_create': 1613207}
0403aebe  turnos= 131  modelos={'claude-fable-5': 131}  effort={'high': 131}  tokens={'out': 292780, 'in': 251, 'cache_read': 12566215, 'cache_create': 913872}
6a1327bc  turnos= 433  modelos={'claude-fable-5': 433}  effort={'None': 433}  tokens={'out': 993884, 'in': 21031, 'cache_read': 115236129, 'cache_create': 14147843}
970c3ab4  turnos=  23  modelos={'claude-opus-5': 23}  effort={'high': 23}  tokens={'out': 27943, 'in': 45, 'cache_read': 1303135, 'cache_create': 153764}
a0b9d1eb  turnos= 154  modelos={'claude-opus-5': 75, 'claude-sonnet-5': 79}  effort={'high': 154}  tokens={'out': 368178, 'in': 296, 'cache_read': 22817945, 'cache_create': 2172817}
caf731aa  turnos= 530  modelos={'claude-fable-5': 512, 'claude-opus-5': 18}  effort={'high': 530}  tokens={'out': 906955, 'in': 1152, 'cache_read': 149376353, 'cache_create': 12597213}
f50ba75a  turnos=  30  modelos={'claude-sonnet-5': 30}  effort={'None': 30}  tokens={'out': 23501, 'in': 7768, 'cache_read': 1232035, 'cache_create': 55396}

--- SUBAGENTES (por sesion padre) ---
01175772  n_subagentes=5  alias_meta={'sonnet': 5}  agentType={'claude': 5}
          turnos=123  modelos_reales={'claude-sonnet-5': 123}  effort={'None': 123}
6a1327bc  n_subagentes=6  alias_meta={None: 6}  agentType={'general-purpose': 6}
          turnos=137  modelos_reales={'claude-sonnet-5': 137}  effort={'None': 137}
caf731aa  n_subagentes=16  alias_meta={'sonnet': 15, None: 1}  agentType={'general-purpose': 15, 'Explore': 1}
          turnos=535  modelos_reales={'claude-sonnet-5': 509, 'claude-opus-5': 26}  effort={'high': 535}
```

*(`970c3ab4` es la sesión que produce este documento; su cuenta seguirá
creciendo hasta que la sesión cierre. Todas las demás están cerradas y sus
números son estables.)*

---

## 3. Hallazgos — lo que estos números ya demuestran

**H-1. Una sesión NO equivale a un modelo.** Tres de siete sesiones
ejecutaron **dos modelos distintos en el mismo hilo**:

- `01175772`: 130 turnos de `claude-fable-5` + 75 de `claude-opus-4-8`.
- `a0b9d1eb`: 75 turnos de `claude-opus-5` + 79 de `claude-sonnet-5`.
- `caf731aa`: 512 turnos de `claude-fable-5` + 18 de `claude-opus-5`.

La metodología asume hoy que "sesión inicializada como rol X" ⇒ "modelo X
resolvió la tarea". Empíricamente eso **no se sostiene**: basta un `/model`
a mitad de sesión, o un arranque con el modelo equivocado, para que el
`MODELO` vinculante del AVISO (§5) quede desmentido sin que nadie se entere.
Ese es exactamente el riesgo que §10.7 declaró el 10-08 ("la separación pasa
a depender casi por completo de que cada sesión de Opus arranque realmente
en frío") y que hasta hoy **no tenía forma de comprobarse**.

**H-2. El `effort` registrado es `high` en TODAS las sesiones que lo
registran** — 530/530, 154/154, 131/131, 23/23. Incluye sesiones de trabajo
F0/F1 del Arquitecto, para las que §7.2 prescribe `low` o `medium`. Dos
lecturas posibles, y no se puede distinguir sin más datos: (a) el campo
refleja un ajuste de cliente distinto de la palanca que §7.2 tenía en mente;
(b) el ecosistema lleva semanas pagando razonamiento `high` en trabajo
rutinario. En cualquiera de los dos casos, **§7.2 se ha estado aplicando a
ciegas**. Este dato por sí solo justifica la directriz.

**H-3. El `effort` es `null` en sesiones anteriores** (205, 433 y 30 turnos).
El script **debe** reportar `no registrado` y jamás rellenar el hueco con el
valor declarado. Un campo inventado en un artefacto de trazabilidad es
peor que un campo ausente.

**H-4. La rotación asistida ya deja huella completa.** Los 27 subagentes de
tres sesiones registran `description` (rol declarado por el emisor: *"MT-B1:
Ingeniero Sonnet fix basurero lista"*), alias pedido y modelo real por turno.
En `caf731aa`, 15 subagentes pedidos como `sonnet` produjeron 509 turnos de
`claude-sonnet-5` — **coherencia confirmada**; los 26 turnos de
`claude-opus-5` corresponden al único subagente sin alias (`Explore`), que
hereda el modelo del padre. La Ruta A, por tanto, **no es una caja negra**:
es auditable a posteriori con el mismo material que el hilo principal.

**H-5. `isSidechain` es `false` en el 100% de las líneas.** Los turnos de
subagente **no** viven en el JSONL del padre, sino en
`{sessionId}/subagents/`. Un script que se apoyara en `isSidechain` para
contar subagentes reportaría **cero** y parecería correcto. Es la trampa más
obvia de esta implementación y queda declarada aquí antes de escribir el
código.

---

## 4. Límites de este material (declarados antes de usarlo)

Lo que el transcript **NO** puede demostrar, y que ningún script podrá
inventar:

1. **No prueba que la sesión arrancara en frío.** Registra qué modelo
   respondió, no qué contexto tenía. La inicialización de identidad (§6)
   sigue sin verificación mecánica.
2. **No prueba el rol.** `description` es lo que el emisor *dijo* que era.
   Un subagente mal etiquetado se registra mal etiquetado.
3. **No detecta filtrado de artefactos.** Si un emisor recorta lo que ve el
   receptor, el transcript lo registra como una conversación normal.
4. **Detecta contradicciones, no conformidad.** Puede afirmar *"esta orden
   se cerró con turnos de `claude-sonnet-5` aunque el AVISO declaraba Opus"*.
   No puede afirmar *"esta orden cumplió la metodología"*.

En términos de §4.3: es un **detector de humo, no un extintor** — avisa de
que algo no cuadra, no impide que ocurra ni apaga nada.

---

## 5. Riesgo de privacidad — el repo es PÚBLICO

`gh repo view` sobre `Pueblac/NexoExpress` devuelve
`"visibility":"PUBLIC"`. Todo lo que entre en `auditorias/` acaba en un
repositorio público de GitHub.

El transcript contiene **todo lo tecleado en la sesión**, incluidos nombres
de archivos `.env`, rutas de credenciales y prosa del Director. Por tanto
el script se diseña con **lista blanca fail-closed** (analogía: como un
extracto bancario, que enseña los importes pero nunca en qué se gastaron):
se enumeran uno a uno los campos permitidos y **todo lo demás se descarta
por defecto**. Una lista negra —"quita el contenido"— fallaría abierta el
día que aparezca un campo nuevo.

Además, publicar es **irreversible**: un commit se revierte, pero un dato
que ya estuvo en un repo público hay que darlo por difundido. Por eso el
orden de las micro-tareas no es negociable: **MT-T3 (filtro) cierra antes de
que ninguna salida del script se commitee** (MT-T5).

---

━━ AVISO DE TRASPASO ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CICLO      : 2026-08-11_traspaso_y_trazabilidad
FASE       : F1 — Diseño (evidencia de apoyo)
TURNO DE   : Arquitecto
MODELO     : Opus 5 (`effort: high` registrado; ver H-2)
ENTREGAR   : auditorias/2026-08-11_traspaso_y_trazabilidad/medicion_base_transcripts.md
ADJUNTOS   : Ninguno
DESTINO    : expediente del ciclo (documento de apoyo del diseño F1)
ACCIÓN     : conservar congelado; es el ground truth del DoD de MT-T2
OBSERVABLE : Ninguno en esta fase (la evidencia observable llega en MT-T1)
VUELVE A   : Arquitecto, que lo cita desde `diseno_f1.md`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
