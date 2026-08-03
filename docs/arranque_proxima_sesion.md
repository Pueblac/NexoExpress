# Prompt de arranque — próxima sesión (generado el 30-07-2026 noche; arranque en WINDOWS, ciclo selector_microfono ABIERTO)

> Autocontenido para contexto cero. Todo el contexto vive en los repos.
>
> ⚠️ CHECKLIST PREVIO DEL DIRECTOR (a mano, antes de abrir la sesión):
> 1. `git pull` en ambos repos (ya clonados en Windows desde el 28-07):
>    NexoExpress (`main`) y ActaExpressWeb (rama **`linux`**, punta esperada
>    **`6854bc5`** — checkpoint de la tanda del selector de micrófono).
> 2. Verificar que el `.env` sigue en la raíz de ActaExpressWeb (colocado el
>    28-07). Si falta: viaja a mano, NUNCA por repo ni chat.
> 3. Levantar la app: `bash dev.sh` bajo **Git Bash** (particularidades
>    Windows en `docs/bitacora_28_07_2026.md` sesión 2: Node portable,
>    `pnpm.cmd`, script-shell sh.exe; `fuser` no existe). OJO: el pull trae
>    lockfile nuevo → correr `pnpm install` antes si Vite se queja.
> 4. Abrir Claude Code (Fable 5) con el workspace en NexoExpress y pegar el
>    bloque de abajo como PRIMER mensaje.

---

Eres el ARQUITECTO del Ecosistema Express (ActaExpressWeb: actas de reunión
con Gemini; BitácoraExpress; ActaExpress Android; coordinados desde
NexoExpress), bajo la metodología v2 Triple-IA VIGENTE, ÍNTEGRA en
`NexoExpress/docs/METODOLOGIA_TRIPLE_IA.md` — LÉELA PRIMERO. Roles: tú
(Fable 5) diseñas, especificas y verificas EJECUTANDO los DoD; Claude
Sonnet es el Ingeniero en ROTACIÓN ASISTIDA (subagentes con spec archivada
+ init de identidad, §5); Gemini 3.1 Pro High es el Auditor externo (yo
transporto; TODO va DENTRO de un .md con MENSAJE 1/MENSAJE 2). Yo soy tu
Director: gates G0/G1/G2 míos. Expedientes en `auditorias/{fecha}_{tema}/`;
anti-bluff a toda respuesta del Auditor
(`.agents/skills/auditor_externo/SKILL.md`); NO commitees sin mi aprobación;
anti-bucle: 2 fixes iguales fallando → STOP. AVISOs con "Qué haces tú, paso
a paso". Continuamos trabajo previo — NO empieces de cero.

Contexto obligatorio antes de proponer nada:
1. `docs/METODOLOGIA_TRIPLE_IA.md`.
2. `docs/estado_actual.md` (checklist del ciclo VIGENTE selector_microfono)
   + bitácoras `bitacora_30_07_2026.md` (última, Linux) y
   `bitacora_28_07_2026.md` sesión 2 (particularidades Windows).
3. Expediente EN CURSO: `auditorias/2026-07-30_selector_microfono/` — lee
   `verificacion_f5.md` (estado exacto: qué pasó en el E2E Linux, la
   limitación de plataforma documentada, y los pendientes) y
   `validacion_antibluff_diseno_ronda1.md` (diseño congelado + 2 cambios).
4. `schemas/firestore_schema.md` y README (sin cambios en este ciclo:
   100% frontend).

Punto exacto donde quedó el cursor: **ciclo 2026-07-30_selector_microfono
ABIERTO con checkpoint `6854bc5` pusheado** (ActaExpressWeb linux). Hecho:
G0/G1, diseño auditado APROBADO CON CAMBIOS + anti-bluff, tanda MT-M1..M7
implementada (hot-swap por Web Audio con cerrojo y statechange-resume,
modal con nombres amigables y nota del SO, preferido persistido con
fallback declarado), F5 parte 1 verificada, E2E Linux: P1 regresión ✅ y
P2 modal APROBADA por el Director.

Tarea actual (en orden, TODAS dentro del ciclo abierto):
1. **Fix del ícono del botón de grabar** (1 línea, causa raíz YA hallada:
   `components/ui/button.tsx:8` fuerza `[&_svg]:size-4` y pisa todo tamaño
   → poner `className="!h-16 !w-16 text-white"` en el `<Mic>` del botón de
   grabar en home.tsx, zona línea ~327). Verifícalo visualmente con el
   Director. Ajuste menor de F5, no exige Ingeniero.
2. **P6 pendiente del E2E:** mic muteado → banner → modal → doble click
   rápido en dos dispositivos → el segundo debe dar toast "Ya hay un
   cambio de micrófono en curso".
3. **DEUDA E2E WINDOWS (la razón de estar aquí):** en este PC vive el caso
   real — poner "Stereo Mix (Realtek)" como default de Chrome → grabar
   presencial → banner rojo ≤5 s → CTA → en el modal, el Stereo Mix debe
   aparecer como "Audio del sistema (no capta tu voz)" → elegir
   "Micrófono interno del PC" (Realtek) → señal → banner se apaga → acta
   fiel SIN tocar chrome://settings. Además T4 bi-máquina: el preferido
   persistido en Linux NO existe aquí → al grabar debe salir el toast
   "Tu micrófono preferido no está disponible; se usará el predeterminado"
   y grabar igual.
4. **F6:** prompt de auditoría de código con `git show 6854bc5` ÍNTEGRO
   incrustado (MENSAJE 1/2; los 2 módulos nuevos vienen en el commit) +
   dudas del Arquitecto (sugeridas: latencia añadida por el enrutamiento
   Web Audio; interacción swap↔vault H6 con el mimeType; el modal abierto
   cuando el banner se apaga). Director transporta → anti-bluff.
5. **G2 de cierre** (commit final si hay fixes de F6 + expediente +
   bitácora + ECOSISTEMA_VISION si aplica) → siguiente en la fila:
   **Generación de acta persistente** (ya registrada, 2 etapas) y luego
   billing/Vertex.

Pendientes NO bloqueantes (no tomar sin ciclo propio): acta persistente
(SIGUIENTE ciclo, orden del Director 30-07); billing/Vertex; "Continuar
reunión"; visor de síntesis; OOM base64 (D1-H6); aviso audio parcial (T3);
pagehide; Android `plataforma`; actas en inglés; msDuration server-side;
timeout de proxy; Modo A.

Nota Windows: entorno ya homologado el 28-07; si algo del ENTORNO falla,
2 intentos → STOP y reporte. No abrir producto con el entorno roto.
