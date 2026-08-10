# Estado Actual — NexoExpress (Coordinador del Ecosistema)

**Estado Global del Ecosistema:** 🟢 VERDE
**Última Actualización:** 09-08-2026
**Metodología vigente:** **Triple-IA v2.6** (`docs/METODOLOGIA_TRIPLE_IA.md`, adoptada 09-08-2026 — única metodología del ecosistema, sin fallbacks; conserva íntegra la maquinaria de v2/v2.5 y añade Asesor del Director §1.1, Glosa Pedagógica Inline §4.3, Paradas de Observación §3.1 y Recalibración Dinámica G0′ §3.2)

---

## ✅ Meta vigente (CERRADA 09-08-2026): Adopción de la Metodología v2.6 + separación de NexoOrchestrator

**Meta (CERRADA 09-08-2026 — commit `8b55ed1` en NexoExpress main; G2 concedido por el Director):** adoptar la **v2.6** como metodología ÚNICA del ecosistema y **separar la plataforma del producto**.

Lo adoptado en v2.6, todo apuntando al mismo problema —que el Director pueda decidir de verdad en los gates sin leer el código—:
- **Asesor Estratégico del Director** (Gemini 3.6 Flash en Antigravity): traduce lo que se aprueba. NO decide, NO vota, NO produce artefactos del expediente y **NUNCA comparte conversación con el Auditor** (ambos son Gemini; si conviven en un hilo, la auditoría adversarial queda contaminada).
- **Glosa Pedagógica Inline**: analogía en lenguaje ordinario donde aparece el término, y toda decisión pedida al Director formulada en el eje **reversibilidad × impacto de negocio**.
- **Paradas de Observación**: toda meta con UI, datos o indicadores predeclara en F0 qué verá el Director, cuándo, cómo lo comprueba solo y **qué la haría fallida**. Infraestructura pura puede eximirse, pero la exención se declara y se ratifica en G0 — por omisión no pasa el gate.
- **Recalibración Dinámica (Mini-Gate G0′)**: si en F4/F5 la evidencia predeclarada no se sostiene, se DETIENE y se pide permiso. Solo toca la evidencia, **nunca el alcance**.

**Separación de repositorios (09-08):** la infraestructura del orquestador autónomo se movió a **`NexoOrchestrator`** (repo propio, rama `main`): 20 archivos verificados por hash SHA-256 uno a uno antes de borrar el origen. **NexoExpress vuelve a ser solo el coordinador de las aplicaciones del producto.**

**Evidencia empírica que motivó la v2.6** — el ciclo `2026-08-06_docker_orchestrator` (MT-D2, núcleo de ejecución del orquestador; expediente hoy en NexoOrchestrator) recorrió **6 rondas de corrección y 6 de verificación** más una auditoría externa que devolvió **RECHAZADO**, encontrando defectos reales cada vez. Dos lecciones: (a) **ningún defecto serio lo encontró quien escribió el código**, y varios fueron fallos de diseño del Arquitecto —incluida una **retractación firmada** sobre un vector declarado cerrado sin estarlo—; (b) el Director atravesó seis rondas **sin nada que ver**, aprobando sobre artefactos que no podía verificar. Detalle en `bitacora_09_08_2026.md`.

**Cursor: CICLO CERRADO (09-08).** **Siguiente: G0 del próximo ciclo — PRIMER ciclo bajo v2.6** (el G0 debe traer clasificación de complejidad por MT **y Parada de Observación predeclarada o exención ratificada**).

**Pendientes del ciclo del orquestador (en NexoOrchestrator, no bloquean a NexoExpress):** (1) F5 sobre la ronda F4⁶ de MT-D2 — corrección aplicada y verificada por el Arquitecto, **falta verificación independiente**; (2) ronda 2 de F6 con el paquete regenerado, que debe presentar la neutralización de hooks **como mitigación con su ataque residual descrito**; (3) regresión abierta por la mudanza —el workspace por defecto se deducía de la ubicación del archivo y ahora apunta a todos los proyectos del disco— documentada en `NexoOrchestrator/MIGRACION.md`, mitigable declarando `NEXO_WORKSPACE_ROOTS`, corrección pendiente a fallo cerrado: **primera micro-tarea del repo nuevo**.

Fila del Director sin tocar: acta persistente → página de Configuración (tuerca) → billing/Vertex.

---

## 📁 Meta anterior (CERRADA 06-08-2026): Transición a la Metodología v2.5 Optimizada

**Meta (CERRADA 06-08-2026 — NexoExpress main, refactor documental por vía directa ordenada por el Director; feedback del Arquitecto → 2 ajustes → G2 concedido el mismo día):** adoptar la **v2.5 Optimizada** como metodología ÚNICA del ecosistema: roles por modelo/parámetros (Fable F0/F1 effort low-medium; Sonnet effort high F3 y F5-Alta; Sonnet/Haiku F4; Haiku Sintetizador F5 Media/Baja + empaquetado F6; Gemini F2/F6 con Ronda 1 SIEMPRE Pro High), matriz de complejidad Alta/Media/Baja clasificada en F0 y ratificada en G0, estrategia de tokens (caching + effort), regla de escalada §2.1, y **eliminación física de `METODOLOGIA_DUAL_IA.md` sin fallback** (el viejo "colapso v1" pasa a ser la "vía rápida v2.5"). Verificación: cero referencias operativas huérfanas a v1/dual (las menciones históricas en bitácoras/expedientes/metas cerradas se conservan como memoria jurídica). Detalle en `bitacora_06_08_2026.md`.

**Cursor: CICLO CERRADO (06-08).** **Siguiente: G0 del próximo ciclo — PRIMER ciclo bajo v2.5** (el G0 debe traer clasificación de complejidad por MT). Fila del Director: acta persistente → página de Configuración (tuerca) → billing/Vertex.

---

## 📁 Meta anterior (CERRADA 04-08-2026)

**Meta (CERRADA 04-08-2026 — código en `6854bc5` + `f6b6158`, ActaExpressWeb linux, pusheados):** [ActaExpressWeb] **Selector de micrófono** (CTA en el banner H4): cuando el detector avise silencio, cambiar de micrófono desde el propio banner **sin cortar la grabación** (hot-swap vía enrutamiento Web Audio del presencial — MediaRecorder graba un `MediaStreamDestination` estable), con la elección persistida como default futuro por uid. 100% frontend; sin cambios de schema/openapi/server. Orden de la fila fijado por el Director (30-07): selector → acta persistente → billing. E2E final: mañana en el PC Windows del caso real (Stereo Mix).
**Expediente:** `auditorias/2026-07-30_selector_microfono/`

**Decisiones de producto del GATE G0 (30-07):** (a) **hot-swap sin cortar** la grabación; (b) la elección **persiste como default futuro** por uid; (c) **CTA solo en el banner** — el default sigue siendo automático, la app solo interviene al detectar silencio.

- [x] **MT-M1** — Hook `useMicDevices`: enumerateDevices post-permiso + devicechange + persistencia `actaexpress:micDeviceId:${uid}` con validación. — DoD: typecheck + A/B de 3 estados.
- [x] **MT-M2** — Enrutamiento Web Audio presencial + `swapMicrophone(deviceId)` (connect-nuevo→disconnect-viejo, salvaguarda anti-suspended con fallback declarado al camino directo). — DoD: A/B + grabación continua durante swap.
- [x] **MT-M3** — CTA "Cambiar micrófono" dentro del banner H4 (lista con labels, sin ocultamiento optimista). — DoD E2E: mutear→banner→cambiar→señal→banner fuera sin cortar.
- [x] **MT-M4** — Mic persistido al iniciar (`{exact}` con fallback DECLARADO a default). — DoD: A/B válido/inválido/ausente.
- [x] **MT-M5** — Endurecimiento: desenchufe en vivo, doble swap, deviceId de otra máquina (bi-máquina), permiso. — DoD: checklist adversarial.

**Cursor (ACTUALIZADO 30-07 noche, checkpoint para migrar a Windows):** G0 → F1 → F2 (APROBADO CON CAMBIOS ×2 + anti-bluff) → **G1 (delegado)** → F3 (5 specs) → **F4 COMPLETA (5 Sonnet, checklist MT-M5 10/10, cero fixes)** → F5 parte 1 verificada por el Arquitecto → **E2E Linux r1: P1 regresión del enrutamiento ✅ (acta fiel), P2 ✅ con dirección de producto** → **F3′ (MT-M6 modal superpuesto + nota del SO + MT-M7 nombres amigables con Stereo Mix marcado "Audio del sistema") → E2E r2 parcial: P2 APROBADA por el Director** ("así quería que saliera"; labels "excelentes"). Limitación de plataforma DOCUMENTADA (P3/P4, no bug): el swap no des-mutea un mic silenciado en el SO y "Predeterminado" sigue el ruteo del SO → nota en el modal. **CHECKPOINT `6854bc5` pusheado en ActaExpressWeb (linux) — CICLO ABIERTO.** → **AVANCE 04-08 (sesión Windows): F5 CERRADA COMPLETA** — fix del ícono aplicado (`!h-16 !w-16`, working tree) y confirmado "excelente"; **DEUDA E2E WINDOWS SALDADA:** caso real Stereo Mix resuelto por la app (banner → modal con "Audio del sistema (no capta tu voz)" → cambio al Realtek → banner apagado, grabación 01:05→02:24 con DOS swaps vivos, acta fiel) SIN tocar chrome://settings; T4 toast de fallback capturado; MT-M4 camino válido probado por irreproducibilidad (el preferido vence al default malo); cerrojo P6: rechazo no observable en pantalla (ventana corta), respaldado por código y dirigido a T-b de la auditoría. **F6 RONDA 1 COMPLETA (04-08): APROBADO CON OBSERVACIONES + anti-bluff VÁLIDA con 1 refutación** — C1..C6 confirmados 6/6; de los 3 BUGs alegados: **BUG 1 CONFIRMADO** (fuga de AudioContext en el camino de fallo del enrutamiento presencial — trampa T-a plantada por el Arquitecto, Media-Alta), **BUG 2 CONFIRMADO** (modal huérfano con "No se encontraron micrófonos" al apagarse el banner, Baja/UX), **BUG 3 REFUTADO con evidencia** (`useMicLevel.ts:32`: con micStream null jamás hay micSilent → CTA inalcanzable; el Auditor extrapoló sobre un archivo fuera del diff — mismo patrón que el T5 de captura confiable). D1 observación de monitoreo; D2/D3/D4 cerradas. **FIXES A/B IMPLEMENTADOS (04-08, colapso v1 autorizado por el Director):** Fix A `routingCtx` visible por el catch + `close()` en fallo (useAudioRecorder.ts); Fix B `useEffect` que cierra el modal cuando el banner deja de aplicar (home.tsx). Typecheck EXIT 0. **F6 RONDA 2 COMPLETA (04-08): APROBADO limpio + anti-bluff VÁLIDA** — CF-A/CF-B/CF-C confirmados 3/3; TF-1 resuelta con mecanismo (cierre del modal idempotente, sin carrera; comportamiento de diseño: el modal es extensión táctica del banner). **Cero bugs pendientes. F6 CERRADA en 2 rondas. → CICLO CERRADO (04-08): G2 concedido → commit `f6b6158` pusheado en ActaExpressWeb (linux) + expediente cerrado (19 archivos) + bitácora `bitacora_04_08_2026.md` + arranque regenerado para LINUX.** Séptimo ciclo v2 completo; primer E2E bi-máquina del ecosistema. **Siguiente: G0 del próximo ciclo — en la fila (orden del Director 30-07): acta persistente → página de Configuración (tuerca) → billing/Vertex.** Nuevas direcciones de producto registradas (backlog, ciclos propios): página de CONFIGURACIÓN (tuerca: tema claro/oscuro, selector de mic siempre accesible, cuenta/uso) que absorbe la iteración 2 del selector (probe "Recomendado" + dedupe de entradas virtuales). Detalle en `verificacion_f5.md`.

**Cursor histórico:** G0 (30-07) → F1 (expediente + prompt de diseño) → **F2 COMPLETA (30-07): veredicto de Gemini APROBADO CON CAMBIOS (2) + anti-bluff VÁLIDA** — 2 trampas APLICAN legítimas: T1 suspensión del AudioContext EN VUELO (mi salvaguarda solo cubría el arranque) → cambio 1: listener `statechange` + resume automático (extendido por el Arquitecto a AMBOS modos, virtual ya sufría el riesgo); T5 doble swap concurrente → cambio 2: cerrojo `isSwappingRef` + token de época que detiene al "perdedor". Recomendaciones Q adoptadas: contexto nuevo por grabación, avisar-y-MANTENER la clave del preferido inválido, re-arme natural del detector, upgrade desde "system" fuera de alcance. **Siguiente: G1 del Director → F3 (specs MT-M1..M5) → F4 (rotación Sonnet) → F5 (E2E mañana en el PC Windows del caso real).**

---

## 📁 Meta anterior (CERRADA 29-07-2026)

**Meta (CERRADA 29-07-2026 — commit `74e3d32` en ActaExpressWeb linux, pusheado):** [ActaExpressWeb] **Bug del basurero** (preexistente, confirmado 2 veces en E2E): borrado funcional desde la lista Y desde la vista de detalle.
**Expediente:** `auditorias/2026-07-29_bug_basurero/` (6 archivos: 3 specs incl. r2, 3 informes + verificación F5)

- [x] **MT-B1 (r2)** — Basurero de la lista: diálogo **controlado por estado** (`deleteDialogActaId`), botón fuera del `AlertDialogTrigger`, cierre explícito en `handleDelete`. — **DoD CUMPLIDO AL 100% (29-07):** E2E con capturas: diálogo en primer plano SIN navegar, borrado permanente. *Lección del ciclo: la spec r1 (`preventDefault` en el Trigger) fue un BUG de diseño del Arquitecto cazado en F5 contra el código instalado de Radix (`composeEventHandlers` salta handlers internos si `defaultPrevented` — el botón habría quedado muerto); F3′ → r2.*
- [x] **MT-B2** — Botón **Eliminar** en la vista de detalle (no existía): confirmación, borrado, invalidación de la lista, toast y retorno a `/`. — **DoD CUMPLIDO AL 100% (29-07):** E2E con captura: borrado permanente desde el detalle.

**Cursor: CICLO CERRADO (29-07).** G0 (ambas MTs) → F3/F3′ → F4 (3 subagentes Sonnet) → F5 (código + E2E 5/5) → **F6 DIFERIDO por decisión del Director en G2** (diff pequeño de patrón ya auditado; la verificación contra Radix se hizo en F5) → G2 + commit `74e3d32`. **Siguiente: G0 del próximo ciclo — candidato recomendado por el Arquitecto: selector de micrófono (CTA en el banner H4).**

---

## 📁 Meta anterior (CERRADA 28-07-2026)

**Meta (CERRADA 28-07-2026 — fix win32 en `3ca3b1d`, ActaExpressWeb linux, pusheado; G0 colapso v1 + G2 concedidos el mismo día):** [Ecosistema/ActaExpressWeb] **Homologación Windows** (micro-ciclo de setup, prerrequisito de TODO ciclo de código en esta máquina — arranque_proxima_sesion.md tarea 0, ampliada por el Director: homologar el entorno y PROBAR en Windows antes de tocar producto): rama `linux` checkouteada, dependencias instaladas, credenciales colocadas donde el código las lee, typecheck verde, app levantada con arranque multiplataforma y un E2E real (grabar ~10 s → acta fiel) como prueba final. **Modo propuesto: colapso v1 (el Arquitecto ejecuta — son tareas de entorno, no de producto) [pendiente de autorización en G0].** Contexto verificado: ActaExpressWeb local está en `main`; la rama de desarrollo `linux` existe en el remoto y `2871a74` ya está fetcheado; los `.env` transportados a mano están en `artifacts/acta-express/.env`, `artifacts/api-server/.env` y un archivo `env` en la raíz (ubicación por confirmar en MT-W2).

- [x] **MT-W1 — Sincronizar código.** — **DoD CUMPLIDO (28-07):** rama `linux` checkouteada al día (`## linux...origin/linux`, punta `2871a74`); `pnpm install` EXIT 0. Prerrequisitos resueltos en el camino: Node 24.18.0 LTS **portable** en `%LOCALAPPDATA%\Programs\node-v24.18.0-win-x64` (winget canceló por UAC sin admin) + PATH de usuario; pnpm 11.17.0 vía corepack (**usar `pnpm.cmd`**: el GPO del trabajo bloquea scripts .ps1); `pnpm config set script-shell` → `sh.exe` de Git Bash (el `preinstall` de la raíz usa `sh -c`, Linux-ismo que revienta con cmd.exe).
- [x] **MT-W2 — Credenciales.** — **DoD CUMPLIDO (28-07):** el archivo `env` transportado se renombró a **`.env` en la raíz** (es lo que `source`a `dev.sh`; 25 líneas, claves VITE_* + servidor verificadas solo por nombre); `.gitignore` de `linux` cubre `.env` a todo nivel → `git status` no lista ningún `.env`; los `artifacts/*/.env` del Director quedan como espejo inofensivo (Vite los lee de su propio root). Arranque sin variable faltante.
- [x] **MT-W3 — Typecheck en Windows.** — **DoD CUMPLIDO (28-07):** `pnpm run typecheck` EXIT 0 — libs + 4 paquetes (`acta-express`, `api-server`, `mockup-sandbox`, `scripts`) todos Done, primera vez en Windows.
- [x] **MT-W4 — Arranque multiplataforma.** — **DoD CUMPLIDO (28-07):** app levantada en Windows — API 8080 viva (404 en `/` esperado, log `Server listening`) y frontend **HTTP 200 en 5173**. Dos hallazgos de homologación: (1) `dev.sh` corre TAL CUAL bajo Git Bash — el chequeo `fuser` se salta en silencio (limitación aceptada: en Windows no libera puertos ocupados automáticamente); (2) **causa raíz del primer fallo de Vite:** `pnpm-workspace.yaml` excluía TODOS los binarios nativos no-linux ("replit uses linux-x64 only") → fix mínimo: quitadas 4 exclusiones `win32-x64` (esbuild, lightningcss, tailwind-oxide, rollup-msvc). **Working tree de ActaExpressWeb con `pnpm-workspace.yaml` + `pnpm-lock.yaml` modificados SIN commit → paquete del G2 de este micro-ciclo.**
- [x] **MT-W5 — E2E Windows (con el Director).** — **DoD CUMPLIDO (28-07, 18:41):** acta real "Discusión sobre el funcionamiento de una máquina" (1 min, 2 participantes) generada end-to-end en Windows, resumen y puntos fieles a lo hablado; evidencia por capturas del Director. Incidencia diagnosticada en el camino y RESUELTA manual: Chrome tenía "Stereo Mix (Realtek)" como micrófono → silencio → **primer caso real de producción cazado por el banner H4** (funcionó exactamente como se diseñó); cambiado a "Micrófono (Realtek(R) Audio)" en `chrome://settings/content/microphone`. Derivó la dirección de producto "selector de micrófono en la app" (backlog, ciclo propio).

**CICLO CERRADO (28-07 tarde): G2 concedido → commit `3ca3b1d` pusheado en ActaExpressWeb (`linux`) + bitácora sesión 2 + este estado + arranque regenerado, pusheados en NexoExpress.** El ecosistema ahora es **bi-máquina**: Windows (trabajo) ↔ Linux (casa); el `.env` viaja a mano; en Windows la app se levanta con `bash dev.sh` bajo Git Bash (ver bitácora 28-07 sesión 2 para las particularidades del entorno). **Siguiente: micro-ciclo del bug del basurero (primer candidato) o el ciclo que el Director priorice en G0** (en la fila también: selector de micrófono, billing/Vertex, "Continuar reunión").

*Regla anti-bucle vigente: 2 intentos del mismo fix de entorno fallando → STOP y reporte al Director. Tras cerrar este micro-ciclo, el cursor pasa al micro-ciclo del bug del basurero (confirmación en su propio G0).*

---

**Meta (CERRADA 28-07-2026 — código en `2871a74`, ActaExpressWeb linux, pusheado):** [ActaExpressWeb] **Resiliencia de grabación** (hallazgo H6, Fase 1): que un crash o cierre de pestaña a mitad de una reunión larga NO pierda el audio ya grabado — persistencia de los chunks de 1 s en IndexedDB al vuelo + oferta de recuperación al reabrir. 100% frontend; la grabación JAMÁS falla por culpa del vault. **Quinto ciclo v2 completo (cuarto de código): F0→F7 con 1 ronda de diseño + 1 de auditoría, ambas con anti-bluff; primer F3′ disparado por E2E (MT-H6e) y primer checkpoint commiteado a mitad de ciclo por orden del Director.**
**Expediente:** `auditorias/2026-07-25_resiliencia_grabacion/` (17 archivos)

**Decisiones de producto del GATE G0 (25-07):** (a) recuperación **OFRECIDA** (tarjeta Recuperar/Descartar), nunca automática; (b) máximo **1** sesión huérfana conservada (la última); (c) H6 confirmado como ciclo — billing/Vertex pospuesto.

- [x] **MT-H6a** — Módulo `recordingVault.ts` (227 líneas): wrapper IndexedDB con heartbeat, silo por uid, `purgeStaleKeepNewest` que jamás toca sesiones vivas, transacciones atómicas. — **DoD CUMPLIDO AL 100% (28-07):** typecheck verde, A/B del ciclo de vida, E2E real.
- [x] **MT-H6b** — Escritura al vuelo en `useAudioRecorder`: `createSession` con mimeType real + `appendChunk` fire-and-forget; fallo del vault degrada sin cortar; PROHIBIDO borrar desde el recorder (grep sin resultados). — **DoD CUMPLIDO AL 100% (28-07):** E2E: la recuperación de la prueba 1 demuestra la persistencia al vuelo.
- [x] **MT-H6c** — Recuperación en `home.tsx`: tarjeta Recuperar/Descartar, re-check heartbeat (T2×T5), `msDuration` por timestamps, borrado solo en acta-OK/descarte/422 (conserva en red/5xx). — **DoD CUMPLIDO AL 100% (28-07):** E2E: **cierre real de pestaña grabando → tarjeta automática → acta FIEL al guion**; descarte definitivo; caso feliz sin rastro.
- [x] **MT-H6d** — Endurecimiento adversarial: checklist 8/8 PASA, cero fixes necesarios (todas las llamadas al vault con catch, silo verificado, doble-borrado benigno). — **DoD cumplido (25-07).**
- [x] **MT-H6e** — (F3′ tras E2E r1) Re-chequeo periódico de huérfanas cada 10 s con apagado al detectar. — **DoD CUMPLIDO AL 100% (28-07):** E2E r2: tarjeta aparece SOLA a ~20 s de reabrir sin navegar; multi-pestaña sin falso positivo.

**Cursor:** G0 (25-07) → F1 → F2 (APROBADO CON CAMBIOS ×5 + anti-bluff VÁLIDA) → **G1 CONCEDIDO (25-07)** → F3 (4 specs congeladas) → **F4 COMPLETA (25-07): 4 subagentes Sonnet secuenciales, cero desviaciones, cero dudas, checklist adversarial de MT-H6d 8/8** (incidencia: pausa por modo Plan a mitad de MT-H6b, reanudada con aprobación del Director sin impacto) → **F5 parte 1 (código) VERIFICADA por el Arquitecto** (`verificacion_f5.md`: typecheck verde re-ejecutado, greps por MT, lectura de los bloques críticos — purga que ignora vivas, re-check T2×T5, ruta imperativa anti-T4 — contraste informes-vs-realidad sin discrepancias). **E2E ronda 1 (27-07): núcleo VALIDADO** (recuperación tras cierre real → acta fiel; Descartar OK) **+ 1 BUG corregido en F3′ (MT-H6e:** la tarjeta no aparecía sin remontar Home; ahora re-chequeo cada 10 s, aparición sola en ~30-40 s**)** + 2 hallazgos nuevos al backlog (bug preexistente del basurero; feature "Continuar reunión"). **Checkpoint commiteado y pusheado por orden del Director (27-07): `2871a74` en ActaExpressWeb linux (MT-H6a..e, 381 inserciones).** **E2E ronda 2 (28-07): 4/4 PASA → F5 CERRADA** (tarjeta automática a ~20 s de reabrir, acta recuperada FIEL al guion, descarte definitivo, caso feliz limpio, multi-pestaña sin falso positivo; ver `verificacion_f5.md`). **F6 EN CURSO: `prompt_auditoria_ronda1.md` generado** (`git show 2871a74` incrustado byte a byte verificado, C1..C6, Q1..Q4, T1..T5, dudas D1..D4 del Arquitecto — memoria en recuperaciones largas, carrera poll-descarte, purgas concurrentes, timing; formato MENSAJE 1/2). **F6 COMPLETA (28-07): APROBADO CON OBSERVACIONES + anti-bluff VÁLIDA** — cero bugs de código (el único "BUG", C3, fue imprecisión del enunciado del claim, reconocida por el propio Auditor). **CICLO CERRADO (28-07): G2 de cierre concedido** → expediente cerrado (17 archivos) + bitácora + ECOSISTEMA_VISION.md (Resiliencia H6 ✅). Backlog alimentado: OOM base64 en recuperaciones muy largas (D1), aviso de "audio parcial" tras quota (T3), bucle de tarjeta si el descarte falla (D2, aceptado), recuperación casi instantánea con marca pagehide. **Siguiente: micro-ciclo del bug del basurero (primer candidato) o el ciclo que el Director priorice en G0; si la sesión es en WINDOWS, antes va el micro-ciclo de setup (ver `arranque_proxima_sesion.md`).**

---

## 📁 Meta anterior (CERRADA 23-07-2026)

**Meta (CERRADA 23-07-2026 — commit `35580f0` en ActaExpressWeb linux):** [ActaExpressWeb] **Captura confiable** (hallazgos H3+H4): el usuario elige EXPLÍCITAMENTE el tipo de reunión (sin diálogos sorpresa ni degradación silenciosa de la fuente de audio) y se entera de un micrófono muerto EN LOS PRIMEROS SEGUNDOS de la grabación, no al final. 100% frontend; sin cambios de schema, openapi ni reglas; el guard 422 del server queda como última defensa. **Cuarto ciclo v2 completo (tercero de código): F0→F7 en 1 ronda de diseño + 1 de auditoría, ambas con anti-bluff; E2E 6/6 con el Director.**
**Expediente:** `auditorias/2026-07-17_captura_confiable/` (16 archivos)

- [x] **MT-C1** — Selector de tipo de reunión (RadioGroup, default presencial, persistido por uid, deshabilitado en grabación/proceso). — **DoD CUMPLIDO AL 100% (23-07):** typecheck verde, 11 marcadores, **E2E real: persistencia tras reload confirmada en ambos sentidos (prueba 5).**
- [x] **MT-C2** — `startRecording(modo)`: presencial → `getUserMedia` directo (EC/NS off, AGC on); virtual → pestaña+mic **sin fallback silencioso** (cancela→error Q3, no arranca); expone `micStream`. — **DoD CUMPLIDO AL 100% (23-07):** fallback `getUserMedia({audio:true})` ELIMINADO (grep sin resultados), **E2E real: cancelar el diálogo → error Q3 con timer en 00:00, la grabación NO arrancó (prueba 3 — corrección de H3 verificada con captura).**
- [x] **MT-C3** — Hook nuevo `useMicLevel.ts` (H4): `AnalyserNode` sobre mic crudo, RMS, umbral 0.01, ventana 5s presencial/10s virtual, `resume()` si suspended (trampa T1), no acumula silencio hasta `running`. — **DoD CUMPLIDO AL 100% (23-07):** **E2E real: mic muteado detectado en presencial (banner a ≤10s de grabación, prueba 1) y en virtual (~12s, prueba 4); regresión hablando normal sin falso positivo (prueba 2).**
- [x] **MT-C4** — Banner H4 (`banner-mic-muerto`): rojo destructivo presencial / ámbar pasivo virtual (cambio 3), solo con `isRecording && micSilent`, nunca corta. — **DoD CUMPLIDO AL 100% (23-07):** **E2E real con capturas: rojo con texto exacto en presencial, desaparece al desmutear; ámbar pasivo en virtual sin cortar la grabación.**
- [x] **MT-C5** — Tarjeta de procesamiento prominente (`card-procesando`, Loader2, conserva `text-espera`). — **DoD CUMPLIDO AL 100% (23-07):** **render real confirmado por captura durante el procesamiento (prueba 6); acta fiel a la noticia grabada; desaparece al terminar.**

**Decisiones de producto del GATE G0 (17-07):** (a) modo por defecto = **presencial** (recomendación del Arquitecto adoptada: no interrumpe con diálogos y es el caso probado E2E); (b) **MT-C5 INCLUIDA** en la tanda (5/5); (c) el aviso H4 **solo avisa, nunca corta** la grabación.

**Cursor:** G0 → F1 → F2 (APROBADO CON CAMBIOS + anti-bluff) → G1 (ventana 5s/10s) → F3 (5 specs) → **F4 COMPLETA (22-07)** → **F5 COMPLETA (23-07): parte 1 código + parte 2 E2E real con el Director — las 6 pruebas PASADAS con capturas** (banner rojo con mic muteado y desaparición al desmutear; regresión sin banner; virtual cancelado→error Q3 sin arrancar, H3 corregido; ámbar ~10s en virtual; persistencia tras reload; tarjeta "Procesando con IA…" + acta fiel; ver `verificacion_f5.md`) → **F6 EN CURSO: `prompt_auditoria_ronda1.md` generado** (diff íntegro verificado byte a byte + `useMicLevel.ts` completo incrustado, C1..C6, Q1..Q4, T1..T5, dudas D1..D4 del Arquitecto; formato MENSAJE 1/MENSAJE 2). Working tree de ActaExpressWeb con la tanda SIN commit (3 archivos) → **F6 COMPLETA (23-07): respuesta de Gemini archivada (`respuesta_auditoria_ronda1.md`, APROBADO CON OBSERVACIONES) + anti-bluff del Arquitecto VÁLIDA (`validacion_antibluff_ronda1.md`)** — Q1 carácter a carácter, citas sin código inexistente, y el único "BUG" (T5, carrera de auth pisando la persistencia) **REFUTADO con evidencia**: `Home` solo se monta vía `ProtectedRoute` con `user` resuelto (App.tsx:33-47) + E2E prueba 5 lo contradice empíricamente; cero bugs confirmados → **CICLO CERRADO (23-07): G2 concedido → commit `35580f0` en ActaExpressWeb (linux) + expediente cerrado + bitácora + ECOSISTEMA_VISION.md (Captura confiable ✅).** Backlog alimentado por este ciclo (NO tomar sin ciclo propio): D1 umbral RMS en sala callada (posible falso positivo presencial; calibración/0.005 candidatos), D3 botón de descarte del aviso ámbar (fatiga de alarma), useEffect defensivo de persistencia si algún día `Home` se montara sin guard. **Siguiente: F0 del ciclo "Resiliencia de grabación" (H6: autoguardado IndexedDB + recuperación) — pendiente de G0 del Director.**

**Parámetros finales del diseño (F3):** `modoReunion: "presencial"|"virtual"` default presencial, persistido `actaexpress:modoReunion:${uid}` + ref espejo · presencial = `getUserMedia({audio:{echoCancellation:false,noiseSuppression:false,autoGainControl:true}})` directo · virtual = display+mix, SIN fallback silencioso (null→setError con texto Q3, no arranca; display OK + mic falla→mode "system") · hook `useMicLevel(micStream,isRecording,modo)`: AnalyserNode fftSize 2048, muestreo ~200ms, RMS, `MIC_RMS_THRESHOLD=0.01`, ventana `MIC_SILENT_WINDOW_PRESENCIAL_MS=5000`/`MIC_SILENT_WINDOW_VIRTUAL_MS=10000`, `resume()` si suspended + no contar hasta `running`, salida inmediata a false con señal · banner rojo presencial / ámbar pasivo virtual (`data-testid="banner-mic-muerto"`) · MT-C5 tarjeta de procesamiento prominente (conserva `text-espera`). Texto Q3: *"No se capturó audio. Al compartir, asegúrate de seleccionar 'Pestaña de Chrome' y tener activa la casilla 'Compartir audio de la pestaña'."*

---

## 📁 Meta anterior (CERRADA 17-07-2026)

**Meta (CERRADA 17-07-2026 — commit `c382c4c` en ActaExpressWeb linux, pusheado):** [ActaExpressWeb] **Robustez del pipeline** (hallazgos H1+H2+H5 del piloto): que una reunión real larga o un audio defectuoso NUNCA produzcan acta confabulada, síntesis truncada ni fallo por timeout. **Tercer ciclo v2 completo (segundo de código): F0→F7 en 1 ronda de diseño + 1 de auditoría, ambas con anti-bluff; rotación asistida consolidada.**
**Expediente:** `auditorias/2026-07-14_robustez_pipeline/` (15 archivos)

- [x] **MT-R1** — Guard 422 de audio casi mudo (`audioGuard.ts` + handler; umbral **300 B/s** por dictamen, env-configurable, piso 5s). — **DoD CUMPLIDO AL 100% (17-07):** A/B de 5 casos re-ejecutado por el Arquitecto + typecheck verde + **E2E real: mic muteado 31,9s → 254 B/s → 422 en 292 ms, cero llamadas a Gemini, toast correcto, sin acta.**
- [x] **MT-R2** — Centinelas anti-confabulación en ambos prompts (texto Q3 literal) + `looksEmpty` reconciliada (título exacto + keyword "no se detectó" — cierra OBS-1, hueco demostrado por A/B viejo=false/nuevo=true). — **DoD código cumplido (17-07).**
- [x] **MT-R3** — `thinkingConfig: { thinkingBudget: 4096 }` SOLO en la síntesis (acta intacta, verificado). — **DoD CUMPLIDO AL 100% (17-07):** **E2E real: síntesis con `thoughtsTokenCount: 1145` ≤ 4096 (baseline pre-fix: 62.912), `finishReason: STOP`, acta fiel al guión.**
- [x] **MT-R4** — `calcularMaxWaitMs` (clamp 40s → +msDuration/10 → techo 600s) + `waitForFileActive(fileName, msDuration)`. — **DoD cumplido (17-07):** A/B de 5 valores re-ejecutado (30min→220s, 1h→400s, 2h→techo) + neutralizado.
- [x] **MT-R5** — Mensaje "Esto puede tardar unos minutos — no cierres esta pestaña" bajo el estado, solo con `isPending` (`data-testid="text-espera"`). — **DoD CUMPLIDO AL 100% (17-07):** **render real confirmado por captura del Director durante el procesamiento; desmonta al resolver.** *Mejora UX registrada fuera de tanda: mensaje más prominente + indicador visual de "pensando".*

**Cursor:** **CICLO CERRADO (17-07):** F5 completa (código + E2E real), F6 auditoría de Gemini **APROBADO** con anti-bluff VÁLIDA, **G2 concedido** → commit `c382c4c` pusheado en ActaExpressWeb (linux) + expediente y bitácora cerrados. **Siguiente: F0 del ciclo "Captura confiable" (H3 selector virtual/presencial + H4 detector de micrófono muerto)** — H4 re-pedido por el Director en F5.2 (el 422 llega al final; el aviso debe llegar AL INICIO de la grabación). Backlog alimentado por este ciclo: UX del mensaje de espera más prominente; validar `msDuration` server-side (OBS-A); visor de síntesis; riesgo residual de proxy al desplegar.

---

## 📁 Meta anterior (CERRADA 13-07-2026)

**Meta (PILOTO v2 — CERRADA 13-07-2026):** [ActaExpressWeb] MT-04: toggle "Análisis profundo" → `generarSintesis: true`. **Primer ciclo de código completo bajo la metodología v2**: F0→F7 con 2 rondas de diseño + 1 de código; auditoría final de Gemini **APROBADO** ("listo para merge"), anti-bluff VÁLIDA; persistencia confirmada; commits `0e35253` (ActaExpressWeb linux) y `05d0539` (NexoExpress).
**Expediente:** `auditorias/2026-07-09_mt04_toggle_sintesis/` (15 archivos)
**Hallazgo de F0:** `openapi.yaml` ya declara `generarSintesis` (línea 218, ciclo anterior), pero los clientes generados (`lib/api-client-react`, `lib/api-zod`) NO lo incluyen — la regeneración es prerrequisito del toggle.

- [x] **MT-04a** — Regenerar los clientes API desde `lib/api-spec/openapi.yaml` (alcance ampliado en `spec_mt04a_r2.md`: sincronización completa con el yaml vigente — incluye drift aprobado `plataforma`/`updatedAt`/`ActaPlataforma` del ciclo 07-07). — **DoD cumplido y re-ejecutado en F5 (09-07-2026):** grep devuelve el campo en ambos paquetes; typecheck EXIT=0; mapeo hunk→yaml 1:1. El Ingeniero aplicó DETENTE por la regla de diff limpio (funcionó según diseño); duda resuelta en F3' sin trabajo nuevo. Cambios sin commit en el working tree (F7 pendiente).
- [x] **MT-04b** — Toggle "Análisis profundo" en `home.tsx` (rotación asistida: subagente Sonnet; F5 código verificada por el Arquitecto). — **DoD cumplido (13-07-2026):** E2E real con guion como ground truth — toggle ON → `sintesis/g1oWHvziNoalE9ESxepg` con transcripción FIEL (capturó hasta un lapsus del hablante que no estaba en el guion) y diarización correcta; OFF → sin síntesis; multi-grabación sin B1; acta ~10s, síntesis +10s. Evidencia literal en `evidencia_mt04.md`. *(Confirmación visual de persistencia tras reload: pendiente, respaldada por código.)*

**Cursor:** **CICLO CERRADO (13-07):** auditoría de código APROBADO + anti-bluff válida + persistencia confirmada + commits pusheados. **Siguiente: retro del piloto + `roadmap_manager`** — el Director prioriza entre los ciclos candidatos: "captura confiable" (H3+H4), "robustez del pipeline" (H1+H2+H5), "resiliencia de grabación" (H6), billing/Vertex (pendientes #3/#4). Contexto histórico: E2E del 11-07 **verificó la plomería del flag** (ON → `sintesis/` poblada por el mismo request; OFF → sin síntesis; multi-grabación OK) — evidencia con logs literales y lecturas Firestore en `evidencia_mt04.md`. **Pendiente:** pruebas restantes del Director (persistencia tras reload + prueba de pestaña con audio) → F6 (auditoría tanda MT-04a+b) → F7. **Hallazgos del piloto (ciclos propios, NO tomar sin F0):** H1 doble alucinación de Gemini sobre audio casi mudo (10.5KB/42s) que bypasea la heurística anti-silencio; H2 thinking devora el presupuesto de síntesis (62.912 de 65.536 tokens, latencia 4 min, riesgo MAX_TOKENS en reuniones reales — fix candidato: `thinkingBudget: 0`); H3 captura Linux solo da audio de sistema por pestaña + **dirección de producto del Director (12-07): selector explícito "Reunión virtual" (pestaña+mic) / "Reunión presencial – sonido ambiente" (mic directo, sin diálogo)**; sin avisos a terceros — requisito del Director satisfecho; **H4** detector de señal de micrófono en cliente (aviso "tu micrófono está apagado" vía AnalyserNode — UX del Director; causa raíz de los silencios CONFIRMADA: mic apagado en el SO). H3+H4 candidatos a ciclo conjunto "captura confiable"; **H5** espera y audios largos: timeout duro de 40s en `waitForFileActive` (rompería con audios de ~1h), procesamiento atado a la pestaña (cerrarla pierde el acta), y UX de expectativa ("puede tardar, sigue en otra pestaña") + síntesis invisible al terminar. **12-07 tarde: PRIMERA ACTA FIEL E2E** (modo rápido, mic presencial) — pipeline verificado con audio real; **H6** resiliencia de grabación (13-07): autoguardado de chunks en IndexedDB + recuperación al reabrir (Fase 1 recomendada); transcripción incremental NO recomendada como parche (streaming Live API = Fase 3); aclarado que el timeout de File API no es cola del tier gratuito — Vertex/tier pagado se justifica por privacidad y rate limits (depende de billing, pendientes #3/#4).

---

## 📁 Meta anterior (CERRADA 09-07-2026)

**Meta (CERRADA 09-07-2026, commit `b23dff7` pusheado):** [NexoExpress] Diseñar y adoptar la METODOLOGÍA v2 (Triple-IA): Fable 5 Arquitecto / Claude Sonnet Ingeniero / Gemini 3.1 Pro High Auditor.
**Expediente:** `auditorias/2026-07-08_metodologia_v2/`

- [x] **MT-01** — Borrador de `docs/METODOLOGIA_TRIPLE_IA.md` (roles, fases F0–F7, artefactos de traspaso spec/informe, AVISO estándar, gates humanos G0–G2, evaluación Modo M vs Modo A, excepciones y plan de adopción). — **DoD cumplido (08-07-2026):** doc completo + prompt de revisión archivado en `auditorias/2026-07-08_metodologia_v2/prompt_diseno_ronda1.md` y entregado al Director.
- [x] **Veredicto ronda 1 (08-07-2026): APROBADO CON CAMBIOS** — respuesta archivada en `respuesta_diseno_ronda1.md` con validación anti-bluff anexada (VÁLIDA; 1 observación: la premisa de C4 sobre incapacidad de ejecución del Arquitecto era incorrecta por omisión del prompt, cambio 3 incorporado con precisión). Los 5 cambios + Q1/Q3/D4 incorporados al borrador.
- [x] **Gate de adopción (09-07-2026):** el Director aprobó adoptar la v2 ("continuemos con el plan"). `METODOLOGIA_TRIPLE_IA.md` marcada VIGENTE; `METODOLOGIA_DUAL_IA.md` marcada HISTÓRICA/fallback.
- [x] **MT-02 (BLOQUEANTE antes del piloto, dictamen r1 cambio 5)** — Actualizados al ciclo v2: `PROMPT_ARRANQUE_SESION.md` (plantilla de Arquitecto), skills `auditor_externo` (diff íntegro F6, init de identidad, dudas del Ingeniero, F5 previo) y `roadmap_manager` (F0/G0), README (regla 5, árbol, fecha), skill `innovador` (colateral detectado por grep) y `arranque_proxima_sesion.md` regenerado para el piloto. — **DoD cumplido (09-07-2026):** `grep -rni "dual"` sobre los documentos operativos devuelve únicamente la línea intencional del README que marca la v1 como "histórica — fallback operativo (v2 §7)"; cero referencias operativas huérfanas.

*(Cursor histórico: G2 concedido el 09-07-2026; ciclo commiteado y pusheado — `b23dff7` — con bitácora `bitacora_09_07_2026.md`.)*

---

## 📁 Meta anterior (CERRADA 07-07-2026)

**Meta (CERRADA 07-07-2026):** [ActaExpressWeb] Enriquecer el prompt de Gemini para incluir transcripción completa y poblar `sintesis/` con contenido real.
**Expediente:** `auditorias/2026-07-07_transcripcion_sintesis/` — ciclo dual-IA completo: diseño APROBADO CON CAMBIOS (r1), código APROBADO CON OBSERVACIONES + BUG D1 corregido (r1), fix APROBADO (r2). Commiteado y pusheado con aprobación del Director.

- [x] **MT-01** — Diseño del enriquecimiento + prompt de revisión de DISEÑO para Gemini 3.1 Pro High, archivado en el expediente. — **DoD cumplido (07-07-2026):** existe `auditorias/2026-07-07_transcripcion_sintesis/prompt_diseno_ronda1.md` y fue entregado al Director.
- [x] **MT-02** — Implementar el diseño aprobado en ronda 1 (ver `respuesta_diseno_ronda1.md`, dictamen §3): dos llamadas (acta síncrona intacta + síntesis en background text/plain 65536 tokens reutilizando el `fileUri`), sin reintento MAX_TOKENS, purga anti-derrame, truncado 800k, flag `generarSintesis` (default false), logging de `usageMetadata`. — **DoD cumplido (07-07-2026):** E2E real con audio sintetizado → `sintesis/HwewR3jTMUdopfVzqCVN` con transcripción de 494 chars y `actas/{id}` con solo sus 13 campos; evidencia literal en `evidencia_mt02.md`. **Colaterales resueltos:** reglas Firestore no cubrían `sintesis/` (desplegado fix con aprobación del Director) y bug 400 en `firestoreSet` (updateMask con comas) corregido.
- [x] **MT-03** — Prompt de auditoría de CÓDIGO (claims, trazas, trampas, dudas, adjuntos exactos) archivado en el expediente. — **DoD cumplido (07-07-2026):** existe `prompt_auditoria_ronda1.md` y fue entregado al Director.
- [ ] **MT-04** — Frontend Web: enviar `generarSintesis: true` desde la UI (toggle u opción al grabar, decisión de UX del Director). — **DoD:** request real del frontend con el flag y síntesis generada end-to-end. *(No bloqueante para MT-02/MT-03.)*

*(Cursor histórico: ciclo cerrado el 07-07-2026. MT-04 pendiente — reservada como piloto de la metodología v2.)*

---

## 🗺️ Estado por Proyecto

| Proyecto | Estado | % MVP | Prioridad ahora |
|---|---|---|---|
| ActaExpressWeb | 🟢 Activo | ~93% | Próximo G0 bajo v2.5 (fila: acta persistente → Configuración → billing) |
| ActaExpress Android | 🟡 En pausa | ~60% | Paridad con Web (campo `plataforma`) |
| BitácoraExpress | 🟢 Activo en Linux | 100% (MVP) | MVP Completado, mantenimiento |
| NexoExpress | 🟢 Activo | 100% | Orquestación, RAG Docs y Mantenimiento |

---

## 📌 Hitos Recientes del Ecosistema

- **Metodología v2.5 Optimizada adoptada (06-08):** roles por modelo/`effort` (Fable macro F0/F1; Sonnet specs F3 + F5-Alta; Sonnet/Haiku F4; Haiku Sintetizador; Gemini con F6-r1 siempre Pro High), matriz de complejidad, optimización de tokens y **legacy Dual-IA eliminada sin fallback** — metodología única del ecosistema. Ajustes del Director en G2: F5-Alta a Sonnet effort high (juicio semántico) y Flash solo en rondas 2+/Baja.
- **Resiliencia de grabación cerrada (28-07):** vault IndexedDB que persiste los chunks de 1 s al vuelo + tarjeta de recuperación tras crash/cierre de pestaña (heartbeat 30 s, poll 10 s, silo por uid, borrado solo en acta-OK/descarte/422). E2E en 2 rondas con cierre REAL de pestaña → acta fiel; auditoría APROBADO CON OBSERVACIONES con anti-bluff válida y cero bugs de código (`2871a74` en ActaExpressWeb linux; expediente `2026-07-25_resiliencia_grabacion`, 17 archivos). Primer F3′ disparado por E2E (MT-H6e).
- **Captura confiable cerrada (23-07):** selector explícito presencial/virtual persistido por uid, fin del fallback silencioso de fuente de audio (H3), detector de micrófono muerto con banner por severidad en los primeros 5–10 s (H4) y tarjeta prominente de procesamiento. Ciclo v2 completo con E2E 6/6 y auditoría APROBADO CON OBSERVACIONES cuyo único BUG alegado (T5) fue refutado con evidencia por el Arquitecto (`35580f0` en ActaExpressWeb linux; expediente `2026-07-17_captura_confiable`, 16 archivos).
- **Robustez del pipeline cerrada (17-07):** guard 422 pre-gasto (300 B/s), centinelas anti-confabulación en ambos prompts + `looksEmpty` reconciliada, thinkingBudget 4096 en síntesis (thoughts reales: 1145 vs 62.912), timeout File API proporcional y mensaje de espera. Ciclo v2 completo con E2E real y auditoría APROBADO (`c382c4c` en ActaExpressWeb linux; expediente `2026-07-14_robustez_pipeline`, 15 archivos).
- **Metodología v2 Triple-IA adoptada (09-07):** ciclo F0–F7 con Fable Arquitecto / Sonnet Ingeniero / Gemini Auditor; auto-auditada por Gemini (APROBADO CON CAMBIOS r1, 5 cambios incorporados) y commiteada (`b23dff7`). v1 queda como fallback. Piloto: MT-04.
- **Transcripción + análisis profundo funcionando (07-07):** ActaExpressWeb puebla `sintesis/` en background con flag `generarSintesis`; verificado E2E contra Firestore real. Primer ciclo dual-IA completo (expediente `2026-07-07_transcripcion_sintesis`): cazó 3 defectos reales (reglas Firestore sin `sintesis/`, 400 en `firestoreSet`, truncado chars vs bytes).
- **Reglas Firestore actualizadas (07-07):** bloque owner-based para `sintesis/` desplegado (ruleset `3dc59963`). Regla operativa nueva: colección en el schema ⇒ verificar reglas desplegadas antes de estrenarla.
- **Entorno GCP verificado (07-07):** config gcloud `actaexpress`; billing OFF (suficiente por ahora; Blaze exige desvincular otro proyecto — cupo 5/5); Gemini API en `gen-lang-client-0046942155` tier gratuito (decisión de gobernanza pendiente).
- **Integración con GitHub exitosa:** Repositorios conectados y subidos correctamente usando PAT.
- **Configuración de Firebase en Backend:** El SDK de Admin de Firebase ya está configurado en BitácoraExpress (`keys/`).
- **BitácoraExpress MVP Completado:** Interfaz de conciliación con evidencia, agrupación masiva de saltos de ventana, borrado y creación de proyectos virtuales, todo conectado a Firebase.
- **Frontend Modularizado:** Refactorización arquitectónica de BitácoraExpress para separar CSS y JS de la vista HTML (`index.html`).
- **Pipeline Documental Automatizado:** Script en Python que renderiza flujos de Mermaid a PNG y los empaqueta en `.docx` con timestamp.
- **Privacidad y Vectorización:** Se decidió delegar la privacidad al cliente (horarios laborales) para que Firestore sea un "Cerebro Aislado".

---

## 🚀 Próximos 5 Pasos Globales (actualizado 06-08 tras adoptar la v2.5)

1. ~~[Si la sesión es en WINDOWS] Micro-ciclo de setup del entorno~~ ✅ **CERRADO 28-07** (`3ca3b1d`): entorno Windows homologado y probado E2E; particularidades en bitácora 28-07 sesión 2.
2. ~~[ActaExpressWeb] Micro-ciclo bug del basurero~~ ✅ **CERRADO 29-07** (`74e3d32`): borrado funcional en lista (diálogo controlado, sin navegación espuria) y detalle (botón nuevo); E2E 5/5. **El siguiente ciclo se decide en G0 — candidato recomendado: selector de micrófono (punto 4).**
3. **[ActaExpressWeb] Generación de acta PERSISTENTE (dirección de producto del Director, 29-07):** que el procesamiento sobreviva al cierre del sitio y no bloquee la app. **Etapa 1 (fácil, frontend):** desacoplar grabación de procesamiento — poder grabar otra reunión mientras la anterior se genera, con aviso no bloqueante. **Etapa 2 (ciclo estándar, toca server+openapi+schema):** el server crea el acta INMEDIATAMENTE con `estado: "generando"` (visible en la lista), completa en background, y correlación de IDs con el vault H6 para evitar el duplicado detectado por el Arquitecto (hoy, cerrar durante el procesamiento deja la sesión en el vault Y el server probablemente termina igual → reprocesar duplicaría). Sinergia: resuelve de paso el riesgo de timeout de proxy al desplegar. Orden vs selector de micrófono: a decidir en G0 (recomendación del Arquitecto: selector primero por tamaño/dolor diario).
4. **[Backlog]** ~~Selector de micrófono en la app~~ → **en ciclo (2026-07-30, ABIERTO — ver checklist vigente)**; **[NUEVO 04-08] Página de CONFIGURACIÓN (la "tuerca") — dirección de producto del Director, Windows y Linux:** panel de ajustes en el frontend con (a) **Tema** claro/oscuro; (b) **Audio**: selector de micrófono SIEMPRE accesible — para cambiar el preferido persistido sin esperar a que el banner H4 detecte silencio (hallazgo del E2E: el preferido protege tan bien que ya no hay camino de UI para cambiarlo voluntariamente); (c) tipo de cuenta y uso, entre otros. **Absorbe la "iteración 2 del selector"** (nacida del E2E Windows 04-08: 3 opciones-trampa de 4 por entradas virtuales duplicadas del SO y labels no obvios → sondear dispositivos en la ventana de detección y marcar "**Recomendado**" a los que SÍ captan señal + dedupe de entradas virtuales; candidato técnico: probe RMS ~0,5 s por dispositivo, permiso ya concedido). "Puede hacerse después" (Director) — ciclo propio con G0. **"Continuar reunión"** desde un acta (anexar audio tras un corte — dirección de producto del Director, ciclo propio); visor de síntesis en la UI; Android campo `plataforma`; actas en inglés; `msDuration` server-side; timeout de proxy al desplegar; **de captura confiable:** umbral RMS sala callada, descarte del ámbar, useEffect defensivo; **de resiliencia H6:** OOM base64 en recuperaciones muy largas (D1), aviso "audio parcial" tras quota (T3), recuperación casi instantánea con marca pagehide (cambia el diseño auditado).
5. **[Metodología]** ~~Transición a v2.5~~ ✅ **CERRADA 06-08** (metodología única, legacy eliminado). Queda: retro del PRIMER ciclo v2.5 (¿matriz clasificó bien? ¿F5-Haiku sostiene en Media/Baja? ¿ahorro medible?) y diseño del "Modo A" partiendo de `docs/arquitectura_mas_cloud.md` (cuando el Director lo priorice).

---

## 🔧 Skills Disponibles

| Skill | Propósito |
|---|---|
| `auditor_paridad` | Revisa brechas funcionales entre proyectos. |
| `documentador_sesion` | Genera bitácora y actualiza el estado (memoria a corto plazo). |
| `arquitecto_firebase` | Define/modifica el esquema Firestore (`schemas/`). |
| `roadmap_manager` | Compara avance vs `ECOSISTEMA_VISION.md` y prioriza tareas. |
| `arquitecto_ecosistema` | Analiza viabilidad cloud, privacidad y arquitectura end-to-end. |
| `disenador_flujos` | Traduce análisis arquitectónico a Mermaid (`docs/flujos/`). |

---

## 🖥️ Cómo Levantar BitácoraExpress

```bash
# Desde el directorio del proyecto
python3 start.py               # producción local
python3 start.py --reload      # desarrollo (hot-reload)
```
La app queda disponible en `http://127.0.0.1:8001`

---

## 📁 Estructura del Workspace

```
NexoExpress/
├── .agents/skills/             ← 6 Agentes IA configurados
├── docs/
│   ├── estado_actual.md        ← este archivo
│   ├── ECOSISTEMA_VISION.md    ← arquitectura y roadmap
│   ├── informe_arquitectura.md ← análisis profundo
│   ├── flujos/                 ← diagramas en .mmd y .png
│   ├── informes/               ← reportes generados en .docx
│   └── bitacora_*.md           ← logs de sesión
├── schemas/
│   └── firestore_schema.md     ← contrato de datos Firebase
├── scripts/
│   └── generar_informe.py      ← pipeline de documentación
└── scratch/                    ← scripts temporales
```
