# Cotejo de desfase — paquete F2 (escrito bajo v2.6) contra metodología v3.0 VIGENTE

**Emitido por:** Coordinador · **Fecha:** 06-09-2026
**Destinatario:** Arquitecto (F1 r3), como insumo para reemitir el paquete de F2.
**Naturaleza:** cotejo factual con cita `archivo:línea`. No contiene decisiones de
diseño: qué se cambia y cómo lo decide el Arquitecto, y lo ratifica el Director.

**Motivo:** el diseño `diseno_f1.md` y el paquete `prompt_diseno_ronda1.md` se
escribieron el 11-08-2026 bajo la metodología **v2.6**. El 06-09-2026 el Director
adoptó la **v3.0**, que cambia el roster y el modo de operación. El Auditor trabaja
bajo contrato de citas verificables: si el paquete afirma cosas que la metodología
vigente ya no dice, está obligado a detenerse y declararlo incompleto. La auditoría
se gastaría sin producir veredicto.

---

## A. Desfases de HECHO en el paquete (CONTEXTO 1)

Afirmaciones del paquete que hoy son falsas contra el documento vigente.

| # | `prompt_diseno_ronda1.md` afirma | v3.0 vigente dice | Cita |
|---|---|---|---|
| A1 | «Roster desde el 10-08 (§10.7): **Arquitecto = Opus 5**» (línea 46) | Arquitecto = **Claude Fable 5.1** `high` | `docs/METODOLOGIA_TRIPLE_IA.md:39` |
| A2 | «Especificador = Opus 5 en Alta, **Sonnet 5 en Media/Baja**» (línea 46-47) | Especificador = **Opus 5**, fijo, sin bifurcación | `docs/METODOLOGIA_TRIPLE_IA.md:40` |
| A3 | «Verificador F5 = Opus 5 en Alta, **Haiku 4.5 en Media/Baja**» (línea 48) | Verificador = **Opus 5**, fijo | `docs/METODOLOGIA_TRIPLE_IA.md:42` |
| A4 | «**Sintetizador** (empaquetado F6) = Haiku 4.5» (línea 49) | El Sintetizador **no figura en el roster** de §1 ni en la tabla de §2 | `docs/METODOLOGIA_TRIPLE_IA.md:32-45`, `:133-141` |
| A5 | «Riesgo §10.7: **Opus ocupa tres de los cuatro nodos internos**» (líneas 52-55) | Con Fable en F0/F1, Opus ocupa **dos** (F3 y F5). El riesgo citado cambió de forma | `docs/METODOLOGIA_TRIPLE_IA.md:39-42` |
| A6 | «Modo de operación vigente (§6): **Modo M manual. El Director transporta cada artefacto a mano**» (líneas 57-59) | §6 pasó a ser «Modos de operación y **Emisión Determinista**». El transporte manual de prompts está **eliminado**: todo arranque lo genera `scripts/emitir_arranque.py` | `docs/METODOLOGIA_TRIPLE_IA.md:462`, `:466` |
| A7 | «**la rotación asistida de §6**» (concepto usado para definir Ruta A) | El término **«rotación asistida» ya no existe** en la metodología (`grep` sin resultados). Ruta A / Ruta B sí sobreviven, definidas en **§6.3** | `docs/METODOLOGIA_TRIPLE_IA.md:495-503` |

## B. Desfases de FONDO — tocan el contenido del diseño, no sólo el contexto

Aquí no basta actualizar una cita: cambia lo que el diseño propone.

**B1 — D1 quedó superada por §6.3.** El diseño decide que «**Ruta A NO entra en
esta tanda**» y que MT-T4 escriba su frontera «con Ruta A **NO habilitada**»
(`diseno_f1.md`, D1; `prompt_diseno_ronda1.md:233` punto C6). Pero la v3.0 vigente
**ya la habilita**: §6.3 dice que el Ingeniero «admite **Ruta A** (subagente
asistido lanzado por el Especificador) o Ruta B» (`docs/METODOLOGIA_TRIPLE_IA.md:499`).
El diseño propondría dejar apagado algo que la metodología vigente ya declaró
encendido. **Nota a favor del diseño:** §6.3 sí recoge la salvaguarda central
—«Verificador: sesión NUEVA en frío obligatoria por Ruta B. **NUNCA Ruta A**»
(`:500`)—, de modo que la arista de verificación quedó protegida; lo que falta
escrito es la frontera completa (Auditor y Asesor) que MT-T4 iba a producir.

**B2 — El cotejo de roster fechado (E1) necesita una tercera ventana.** El DoD de
MT-T2 está construido sobre **dos** ventanas: Fable legítimo hasta el 06-08 y Opus
desde el 10-08 (§10.7). La v3.0 **devuelve a Fable 5.1** al puesto de Arquitecto
desde el 06-09 (`docs/METODOLOGIA_TRIPLE_IA.md:39`). Son **tres** ventanas. Si la
tabla del script se queda en la sustitución del 10-08, marcará **DESVIACIÓN en toda
sesión futura del Arquitecto**, que es exactamente el modo de fallo que el propio
DoD quería evitar («un cotejo contra el roster de hoy llenaría de falsas alarmas
todo el histórico y quemaría el mecanismo en su estreno»). Los dos casos de prueba
existentes (`a0b9d1eb` → DESVIACIÓN, `caf731aa` → NO) siguen siendo válidos; falta
un tercero que cubra la reinstalación.

**B3 — El campo que MT-T5 quiere generar ya tiene un vecino mecánico.** El diseño
justifica el bloque `TRAZABILIDAD` en un mundo de transporte manual. La v3.0 ya
emite arranques por CLI y escribe bloques en `bloques/` (§6.1). No es contradicción,
pero el Arquitecto debería declarar si MT-T5 se integra con el emisor o queda al
margen, para que no nazcan dos mecanismos paralelos.

## C. Deuda interna de la propia v3.0 (no la arregla este ciclo, pero le llega)

La v3.0 **se contradice a sí misma** sobre quién ejecuta F5. Las tablas de §1 y §2
fijan **Verificador = Opus 5**, sin bifurcación por complejidad. Pero el cuerpo del
documento conserva texto de la v2.6 que asigna F5 en Media/Baja al **Sintetizador
Haiku**: `docs/METODOLOGIA_TRIPLE_IA.md:94-96`, `:162-167`, `:222-223`.

**Por qué importa a este ciclo:** las micro-tareas MT-T3, MT-T4 y MT-T5 son de
complejidad **Media**. La pregunta «¿quién firma su F5?» tiene hoy **dos respuestas
opuestas en el documento vigente**. No bloquea F2, pero bloqueará F5 si nadie lo
resuelve antes. Es una corrección de documentación que corresponde al Director.

---

## D. Qué NO está desfasado (sigue siendo válido tal cual)

Para que la reemisión no toque lo que no debe:

- El **triángulo de verificación** y la regla de oro: `docs/METODOLOGIA_TRIPLE_IA.md:90`.
- **§1.1 Asesor** y su separación de hilos respecto del Auditor: `:46`.
- **§2 matriz de complejidad** y §2.1 regla de escalada: `:129`, `:152`.
- **§3.1 Paradas de Observación** y §3.2 recalibración: `:255`, `:293`.
- **§7.2 calibración de `effort`**: `:548`.
- Toda la **evidencia empírica** de `medicion_base_transcripts.md`: son medidas
  sobre transcripts reales, independientes de qué metodología esté vigente.
- **MT-T1 y PO-1**: cerradas y validadas el 11-08, no se reabren.

---

## E. Alcance de este cotejo

Cubre `prompt_diseno_ronda1.md` (CONTEXTO 1) y los puntos de `diseno_f1.md` que
dependen del roster o del modo de operación. **No** se ha revisado línea a línea
el resto de `diseno_f1.md` (30.397 B); si el Arquitecto encuentra más desfases al
reemitir, se añaden aquí.
