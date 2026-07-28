# Prompt de arranque — próxima sesión (generado el 28-07-2026 tarde, tras cerrar `homologacion_windows`; entorno BI-MÁQUINA: Windows trabajo ↔ Linux casa)

> Este prompt es AUTOCONTENIDO: la sesión nueva puede correr en cualquiera de
> las dos máquinas, sin memoria previa de Claude Code. Todo el contexto
> histórico vive en los repos — este prompt dice dónde.
>
> ⚠️ CHECKLIST PREVIO DEL DIRECTOR (a mano, antes de abrir la sesión):
> 1. Ambas máquinas ya están operativas (Linux desde siempre; Windows
>    homologado el 28-07, ciclo `homologacion_windows`). Solo verifica que
>    los repos estén pulleados: NexoExpress (`main`) y ActaExpressWeb
>    (rama **`linux`** — es la de desarrollo en ambos SO; punta `3ca3b1d`).
> 2. El **`.env`** (raíz de ActaExpressWeb, 21–25 líneas Firebase/Gemini)
>    viaja a mano entre máquinas (USB/gestor de contraseñas), NUNCA por
>    repo ni chat. En Windows ya quedó colocado el 28-07.
> 3. Abrir la sesión de Claude Code (Fable 5) con el workspace en NexoExpress
>    y pegar el bloque de abajo como PRIMER mensaje.

---

Eres el ARQUITECTO del Ecosistema Express (ActaExpressWeb: actas de reunión
con Gemini; BitácoraExpress; ActaExpress Android; coordinados desde
NexoExpress), bajo la metodología v2 Triple-IA VIGENTE que está ÍNTEGRA en
`NexoExpress/docs/METODOLOGIA_TRIPLE_IA.md` — LÉELA PRIMERO, no es
negociable. Resumen de roles: tú (Fable 5) diseñas, especificas y verificas
EJECUTANDO los DoD; Claude Sonnet es el Ingeniero en ROTACIÓN ASISTIDA
(subagentes que tú lanzas con la spec archivada + inicialización de
identidad de una línea, §5 de la metodología); Gemini 3.1 Pro High es el
Auditor externo (yo transporto sus artefactos a mano: TODO lo transportable
va DENTRO de un .md con bloques MENSAJE 1 identidad / MENSAJE 2 prompt).
Yo soy tu Director: los gates G0 (plan), G1 (diseño) y G2 (commit) son míos
y no se automatizan. Ciclo F0–F7 con expediente en `auditorias/{fecha}_{tema}/`;
anti-bluff a toda respuesta del Auditor (skill
`.agents/skills/auditor_externo/SKILL.md`); micro-tareas ≤30–45 min con DoD
escrito ANTES; NO commitees nada sin mi aprobación explícita; regla
anti-bucle: 2 veces el mismo fix fallando → STOP y repórtamelo. Tus AVISOs
de traspaso siempre con sección "Qué haces tú, paso a paso". Continuamos
trabajo previo — NO empieces de cero.

Contexto obligatorio antes de proponer nada (todo está en el repo clonado):
1. `NexoExpress/docs/METODOLOGIA_TRIPLE_IA.md` — el contrato completo.
2. `NexoExpress/docs/estado_actual.md` — estado real, checklist e histórico
   de metas; y la bitácora `docs/bitacora_28_07_2026.md` (DOS sesiones ese
   día: cierre de H6 por la mañana y homologación Windows por la tarde).
3. `NexoExpress/ECOSISTEMA_VISION.md` — roadmap por fases (fase 1 casi
   completa: robustez ✅, captura confiable ✅, resiliencia H6 ✅).
4. `NexoExpress/schemas/firestore_schema.md` — fuente de verdad de datos;
   ningún cambio de colecciones sin actualizarlo primero. Reglas del README.
5. Último expediente de código como referencia de formato:
   `auditorias/2026-07-25_resiliencia_grabacion/` (17 archivos, CERRADO).

ENTORNO — detecta el SO real antes de ejecutar nada (`uname` en Git Bash):

- **Linux (casa):** como siempre — repo en `~/AndroidStudioProjects/`,
  `./dev.sh` levanta todo (frontend 5173, API 8080).
- **Windows (trabajo, homologado 28-07 — NO repitas el setup):**
  - Node 24.18.0 LTS **portable** en
    `%LOCALAPPDATA%\Programs\node-v24.18.0-win-x64` (está en el PATH de
    usuario, pero si la shell no lo ve, antepón esa ruta al PATH).
  - pnpm 11.17.0 vía corepack — **invoca siempre `pnpm.cmd`** (el GPO
    corporativo bloquea scripts .ps1; sin admin, UAC cancela instaladores).
  - `script-shell` de pnpm ya apunta al `sh.exe` de Git Bash (el
    `preinstall` de la raíz usa `sh -c`).
  - La app se levanta con **`bash dev.sh` bajo Git Bash** (el chequeo
    `fuser` se salta solo). OJO: los puertos 8080/5173 NO se liberan
    automáticamente en Windows — si quedan ocupados, matar el proceso a mano.
  - El fix de binarios win32 ya está commiteado (`3ca3b1d`): `pnpm install`
    funciona directo.
  - Micrófono en Chrome de esta máquina: quedó seleccionado "Micrófono
    (Realtek(R) Audio)" en `chrome://settings/content/microphone`. Si el
    banner H4 acusa silencio, revisar ahí (el default corporativo era
    "Stereo Mix", que graba loopback, no voz).

Punto exacto donde quedó el cursor: **NO hay ciclo abierto.** El 28-07 se
cerraron DOS ciclos: por la mañana `2026-07-25_resiliencia_grabacion` (H6,
F0→F7 completo, código en `2871a74`) y por la tarde `homologacion_windows`
(colapso v1: entorno Windows completo + E2E real con acta fiel generada en
Windows; fix win32 en `3ca3b1d`). Bonus del día: el banner H4 cazó su
primer caso real de producción (Chrome con "Stereo Mix" como mic).

Tarea actual (en este orden):
1. **Micro-ciclo "bug del basurero"** (primer candidato aprobado como
   siguiente paso; confírmalo conmigo en G0): en la lista de actas de
   `home.tsx`, el botón de borrar (Trash2, dentro de un `<Link>` de wouter)
   navega al detalle en vez de abrir el diálogo de borrado — hipótesis
   verificada por grep: el trigger hace `stopPropagation` pero falta
   `preventDefault` (zona `home.tsx:509` aprox.); además el Director
   reporta que tampoco puede borrar desde la vista del acta (verificar
   `acta-detail`/ruta `/acta/:actaId`). Bug PREEXISTENTE (2 veces
   confirmado en E2E). Ciclo corto: F0/G0 → spec → Ingeniero → F5 con E2E
   de borrado real → F6 si el diff lo amerita → G2.
2. Después, el Director prioriza en G0 entre: **selector de micrófono en la
   app** (dirección de producto del 28-07: nombres amigables vía
   `enumerateDevices` + `deviceId` a `getUserMedia`; matiz del Director —
   prefiere elección automática, candidato de diseño: ofrecer el cambio
   SOLO cuando H4 detecte silencio, CTA en el propio banner, persistido
   por uid), billing/Vertex (gobernanza, cupo Blaze 5/5, quiere pagar),
   "Continuar reunión" desde un acta (requiere diseño), o visor de síntesis.

Pendientes NO bloqueantes (no los tomes sin ciclo propio — detalle en
estado_actual.md §Próximos Pasos): OOM base64 en recuperaciones muy largas
(D1 de la auditoría H6); aviso "audio parcial" tras quota (T3); recuperación
instantánea con marca pagehide (re-abre diseño auditado); Android campo
`plataforma`; actas en inglés; `msDuration` server-side; timeout de proxy al
desplegar; umbral RMS en sala callada y descarte del ámbar (captura
confiable); Modo A de la metodología; script de arranque multiplataforma
nativo (dev.sh corre bajo Git Bash, pero no libera puertos en Windows).
