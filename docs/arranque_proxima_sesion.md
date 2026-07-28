# Prompt de arranque — próxima sesión (generado el 28-07-2026, ciclo H6 CERRADO; probable arranque en WINDOWS con contexto CERO)

> Este prompt es AUTOCONTENIDO a propósito: la sesión nueva puede correr en
> una máquina Windows recién clonada, sin memoria previa de Claude Code.
> Todo el contexto histórico vive en los repos — este prompt dice dónde.
>
> ⚠️ CHECKLIST PREVIO DEL DIRECTOR (a mano, antes de abrir la sesión):
> 1. Instalar Git (con Git Bash), Node LTS y pnpm (`npm i -g pnpm`).
> 2. Clonar los repos hermanos en una misma carpeta de trabajo:
>    - https://github.com/Pueblac/NexoExpress.git (rama `main`)
>    - https://github.com/Pueblac/ActaExpressWeb.git (rama **`linux`** — sí,
>      se llama así aunque corras en Windows; es la rama de desarrollo)
> 3. Copiar el archivo **`.env`** a la raíz de ActaExpressWeb desde la
>    máquina Linux (está en `~/AndroidStudioProjects/ActaExpressWeb/.env`,
>    21 líneas con claves Firebase/Gemini). Está gitignoreado a propósito:
>    viaja por USB o gestor de contraseñas, NUNCA por repo ni chat.
> 4. Abrir la sesión de Claude Code (Fable 5) con el workspace en NexoExpress
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
   de metas; y las bitácoras `docs/bitacora_27_07_2026.md` y
   `docs/bitacora_28_07_2026.md` (últimas dos sesiones).
3. `NexoExpress/ECOSISTEMA_VISION.md` — roadmap por fases (fase 1 casi
   completa: robustez ✅, captura confiable ✅, resiliencia H6 ✅).
4. `NexoExpress/schemas/firestore_schema.md` — fuente de verdad de datos;
   ningún cambio de colecciones sin actualizarlo primero. Reglas del README.
5. Últimos expedientes como referencia de formato:
   `auditorias/2026-07-25_resiliencia_grabacion/` (17 archivos, ciclo
   CERRADO 28-07) y `auditorias/2026-07-17_captura_confiable/`.

Punto exacto donde quedó el cursor: **NO hay ciclo abierto.** El ciclo
2026-07-25_resiliencia_grabacion (H6: vault IndexedDB de chunks al vuelo +
tarjeta de recuperación tras crash) se CERRÓ el 28-07 con F0→F7 completo:
E2E de crash real → acta fiel, auditoría de Gemini APROBADO CON
OBSERVACIONES, anti-bluff válida, cero bugs de código, código en el commit
`2871a74` de ActaExpressWeb (rama linux, pusheado).

Tarea actual (en este orden):
0. **Verifica el SO real** (`uname` en Linux/Git Bash). **Si es Windows:**
   micro-ciclo de SETUP antes que nada, con G0 corto y DoD ejecutable:
   `pnpm install` en ActaExpressWeb; `.env` presente; `pnpm run typecheck`
   verde; levantar la app — OJO: `dev.sh` es bash y usa `fuser` (no existe
   en Windows): córrelo bajo Git Bash adaptándolo, o crea un script
   multiplataforma como MT del setup. DoD final: grabar 10 s en el
   navegador y obtener un acta real. Si algo del entorno te bloquea >2
   intentos, STOP y repórtamelo.
1. **Micro-ciclo "bug del basurero"** (primer candidato aprobado como
   siguiente paso; confírmalo conmigo en G0): en la lista de actas de
   `home.tsx`, el botón de borrar (Trash2, dentro de un `<Link>` de wouter)
   navega al detalle en vez de abrir el diálogo de borrado — hipótesis
   verificada por grep: el trigger hace `stopPropagation` pero falta
   `preventDefault` (zona `home.tsx:509` aprox. en `2871a74`); además el
   Director reporta que tampoco puede borrar desde la vista del acta
   (verificar `acta-detail`/ruta `/acta/:actaId`). Bug PREEXISTENTE
   (2 veces confirmado en E2E). Ciclo corto: F0/G0 → spec → Ingeniero →
   F5 con E2E de borrado real → F6 si el diff lo amerita → G2.
2. Después, el Director prioriza en G0: billing/Vertex (gobernanza,
   cupo Blaze 5/5, quiere pagar), "Continuar reunión" desde un acta
   (dirección de producto 27-07, requiere diseño), o visor de síntesis.

Pendientes NO bloqueantes (no los tomes sin ciclo propio — detalle en
estado_actual.md §Próximos Pasos): OOM base64 en recuperaciones muy largas
(D1 de la auditoría H6); aviso "audio parcial" tras quota (T3); recuperación
instantánea con marca pagehide (re-abre diseño auditado); Android campo
`plataforma`; actas en inglés; `msDuration` server-side; timeout de proxy al
desplegar; umbral RMS en sala callada y descarte del ámbar (captura
confiable); Modo A de la metodología.
