# Migración del kit coordinador a 1.6.3 — 2026-11-14

Generada por `scripts/actualizar_kit.py`. Versión anterior: sin kit_version (base de fusión: kit 1.1). Modo: autonomo.

**Respaldo:** `respaldo_metodologia_2026-11-14/` (misma estructura de rutas, con `MANIFIESTO.sha256`).

| Grupo | Pieza | Acción | Detalle |
|---|---|---|---|
| configuración | `coordinador.json` | FUSIONAR | 19 cambio(s) del kit; 2 choque(s) a revisar (se conserva lo del proyecto) |
| scripts | `scripts/abrir_navegador.py` | NUEVO | no estaba en el proyecto |
| scripts | `scripts/actualizar_kit.py` | NUEVO | no estaba en el proyecto |
| scripts | `scripts/archivar_bitacora.py` | NUEVO | no estaba en el proyecto |
| scripts | `scripts/comprobar_indice.py` | NUEVO | no estaba en el proyecto |
| scripts | `scripts/detectar_metodologia.py` | NUEVO | no estaba en el proyecto |
| scripts | `scripts/emitir_agy.py` | NUEVO | no estaba en el proyecto |
| scripts | `scripts/emitir_arranque.py` | REEMPLAZAR | sin cambios locales sobre el kit 1.1 |
| scripts | `scripts/encargar.sh` | NUEVO | no estaba en el proyecto |
| scripts | `scripts/lanzar_agy.py` | NUEVO | no estaba en el proyecto |
| scripts | `scripts/listar_artefactos.py` | NUEVO | no estaba en el proyecto |
| scripts | `scripts/medir_asistentes.py` | NUEVO | no estaba en el proyecto |
| scripts | `scripts/medir_consumo.py` | NUEVO | no estaba en el proyecto |
| scripts | `scripts/proponer_tramos.py` | NUEVO | no estaba en el proyecto |
| scripts | `scripts/reanclar_tramos.py` | NUEVO | no estaba en el proyecto |
| scripts | `scripts/renderizar_informe.py` | NUEVO | no estaba en el proyecto |
| scripts | `scripts/validar_encuadre.py` | NUEVO | no estaba en el proyecto |
| scripts | `scripts/verificar_informe.py` | NUEVO | no estaba en el proyecto |
| plantillas | `docs/prompts_arranque/archivista.md` | NUEVO | no estaba en el proyecto |
| plantillas | `docs/prompts_arranque/arquitecto.md` | REVISAR | adaptada localmente; 2 conflicto(s) en la fusión: la del proyecto no se toca |
| plantillas | `docs/prompts_arranque/asesor.md` | REVISAR | adaptada localmente; 2 conflicto(s) en la fusión: la del proyecto no se toca |
| plantillas | `docs/prompts_arranque/auditor.md` | REVISAR | adaptada localmente; 2 conflicto(s) en la fusión: la del proyecto no se toca |
| plantillas | `docs/prompts_arranque/guionista.md` | OMITIR | el proyecto no usa este rol (no está en coordinador.json) |
| plantillas | `docs/prompts_arranque/ingeniero.md` | REVISAR | adaptada localmente; 3 conflicto(s) en la fusión: la del proyecto no se toca |
| plantillas | `docs/prompts_arranque/verificador.md` | REVISAR | adaptada localmente; 3 conflicto(s) en la fusión: la del proyecto no se toca |
| motor externo | `docs/prompts_arranque/agy_capa.md` | NUEVO | no estaba en el proyecto |
| motor externo | `docs/prompts_arranque/agy_roles.md` | NUEVO | no estaba en el proyecto |
| motor externo | `docs/prompts_arranque/agy_sub_lectura.md` | NUEVO | no estaba en el proyecto |
| motor externo | `docs/prompts_arranque/agy_sub_redaccion.md` | NUEVO | no estaba en el proyecto |
| motor externo | `docs/prompts_arranque/agy_sub_revision.md` | NUEVO | no estaba en el proyecto |
| modo asistentes | `docs/prompts_arranque/asist_capa_navegador.md` | NUEVO | no estaba en el proyecto |
| modo asistentes | `docs/prompts_arranque/asist_encargo_asistente.md` | NUEVO | no estaba en el proyecto |
| modo asistentes | `docs/prompts_arranque/asist_encargo_monitor.md` | NUEVO | no estaba en el proyecto |
| modo asistentes | `docs/prompts_arranque/asist_plan.md` | NUEVO | no estaba en el proyecto |
| motor externo | `scripts/herramienta_segura.py` | NUEVO | esqueleto de la herramienta segura que un rol usa en comandos_agy; RELLENAR su configuración antes de lanzar |
| plantillas | `docs/prompts_arranque/especificador.md` | CONSERVAR | rol local: ponle al día a mano las reglas comunes del kit nuevo (mapa de lectura, consumo, evidencia con comando delante) |
| informes | `docs/estandar_documental.md` | NUEVO | estándar documental: completar sus marcadores `>>>` con el Director |
| herramienta | `.git/hooks/commit-msg` | IGUAL | ya es la del kit 1.6.3 |
| herramienta | `.gitignore` | IGUAL | ya ignora bloques/ |
| modo autónomo | `coordinacion/adenda_modo_autonomo.txt` | NUEVO | copiada del kit; completar sus marcadores `>>>` |
| modo autónomo | `docs/modo_de_trabajo.md` | NUEVO | copiada del kit; completar sus marcadores `>>>` |
| modo autónomo | `coordinacion/encargos/` | NUEVO | directorio de encargos |
| modo autónomo | `coordinacion/bitacora.md` | REVISAR | el proyecto ya tiene docs/bitacora_04_08_2026.md, docs/bitacora_06_08_2026.md, docs/bitacora_07_07_2026.md y 14 más: ajusta `modo_autonomo.bitacora` en coordinador.json en lugar de crear otro |

## Pendiente de revisar con el Director

- `docs/prompts_arranque/arquitecto.md`: propuesta en `respaldo_metodologia_2026-11-14/propuestas/docs/prompts_arranque/arquitecto.md`. Resolver cada bloque `<<<<<<< proyecto` / `=======` / `>>>>>>> kit_…` y copiarla sobre la pieza.
- `docs/prompts_arranque/asesor.md`: propuesta en `respaldo_metodologia_2026-11-14/propuestas/docs/prompts_arranque/asesor.md`. Resolver cada bloque `<<<<<<< proyecto` / `=======` / `>>>>>>> kit_…` y copiarla sobre la pieza.
- `docs/prompts_arranque/auditor.md`: propuesta en `respaldo_metodologia_2026-11-14/propuestas/docs/prompts_arranque/auditor.md`. Resolver cada bloque `<<<<<<< proyecto` / `=======` / `>>>>>>> kit_…` y copiarla sobre la pieza.
- `docs/prompts_arranque/ingeniero.md`: propuesta en `respaldo_metodologia_2026-11-14/propuestas/docs/prompts_arranque/ingeniero.md`. Resolver cada bloque `<<<<<<< proyecto` / `=======` / `>>>>>>> kit_…` y copiarla sobre la pieza.
- `docs/prompts_arranque/verificador.md`: propuesta en `respaldo_metodologia_2026-11-14/propuestas/docs/prompts_arranque/verificador.md`. Resolver cada bloque `<<<<<<< proyecto` / `=======` / `>>>>>>> kit_…` y copiarla sobre la pieza.
- `coordinacion/bitacora.md`: ver el detalle de la tabla.
- `coordinador.json` → `reglas_duras.nada_se_commitea_sin_aprobacion`: el proyecto y el kit la cambiaron distinto; se conserva la del proyecto. Proyecto: "El Director aprueba todo commit." · kit: "El director aprueba todo commit. En modo autónomo (v1.2) los commits locales los hace …
- `coordinador.json` → `no_exportable.roster_de_modelos`: el proyecto y el kit la cambiaron distinto; se conserva la del proyecto. Proyecto: "Asignaciones locales únicas: Asesor=Gemini 3.8 Flash High, Arquitecto=Claude Fable 5.1… · kit: "Las asignaciones rol→modelo, y desde v1.3 rol→motor, son locales. Heredarlas produce d…

## Fusionadas sin conflictos (leerlas una vez)

- `coordinador.json` (la versión anterior está en el respaldo)

## Notas

- `supervision.modo` pasa de `claude_completa` a `asistentes`: es el modo que instala el kit 1.6.3 (Gemini como asistente de los roles de Claude, vigilado por monitores de Claude). Necesita agy instalado, con sesión y el workspace de confianza: si el proyecto aún no lo tiene, deja `claude_completa` en coordinador.json y anótalo como pendiente en la nota.
- Informes (v1.6): no está la plantilla .docx en `docs/plantilla.docx`. Pídesela al Director y ponla ahí, o ajusta `informes.plantilla_docx`; mientras falte, `renderizar_informe.py` se detiene (STOP). Para informes sin plantilla, quita esa clave de `informes`.
- Recomendación (v1.4.1, con el sí del Director): añadir al .gitignore `asistentes/**/*.png`, `!asistentes/**/lamina*/**` y `!asistentes/**/contacto_*.png`; las capturas de los asistentes pesaron cientos de MB por historia. No lo escribo solo.
- v1.5, asistente navegador (A-navegacion): tras aplicar, regenera los asistentes con `scripts/emitir_agy.py`. Prueba de humo: `scripts/abrir_navegador.py abrir`, un encargo A-navegacion de prueba con `scripts/lanzar_agy.py asist_navegacion`, `abrir_navegador.py leer` y `abrir_navegador.py cerrar` (MOTOR_EXTERNO.md §11). Si el proyecto usa sitios con inicio de sesión, el Director entra una vez a mano en el perfil del kit, que es de la máquina: `scripts/abrir_navegador.py sesion --url <URL>`.
- Modo autónomo: conviene `"subagentPromptCacheTtl": "1h"` en `.claude/settings.json` (se propone al Director; este script no toca la configuración de la herramienta).

## Ciclo en curso: excepción del Director

El plan no detectó un ciclo en curso (no hay encargos del modo autónomo), pero hay trabajo de la ronda 2 de la
auditoría de diseño sin commit (`auditorias/2026-08-11_traspaso_y_trazabilidad/`: `diseno_f1.md`, `evidencia_r4.md`,
`fe_de_erratas_f2_ronda1.md`, `insumo_f1r4.md`, `prompt_diseno_ronda2.md`, `respuesta_diseno_ronda2.md`,
`validacion_antibluff_ronda1.md`; y `docs/estado_actual.md`). El Director autorizó actualizar igual:
`--autoriza-director "Actualizar a la 1.6.3 con trabajo de la ronda 2 sin commit, por decision del Director del 14-11-2026"`.
Esos documentos no se tocaron.

## Resolución

Actualización hecha el 14-11-2026 desde el kit `kit_coordinador` (rama `main`, 1.6.3), con sus scripts.
Versión de partida: sin `kit_version` (instalado con la 1.1; base de fusión 1.1). Versión de llegada: 1.6.3.

**Lo aplicado.** `actualizar_kit.py --aplicar` escribió 32 archivos (31 NUEVO, `scripts/emitir_arranque.py`
REEMPLAZAR y `coordinador.json` FUSIONAR). Después, a mano: las 5 plantillas REVISAR, el rol local, la adenda
(punto 3), `coordinacion/bitacora.md`, dos claves de `coordinador.json`, la copia del kit y el `.gitignore`.
Antes de tocar las plantillas vivas se respaldaron en `respaldo_metodologia_2026-11-14/docs/prompts_arranque/`
(6 archivos, con su línea en `MANIFIESTO.sha256`; `sha256sum -c` da OK en los 9).

**Decisiones del Director aplicadas (14-11-2026).**
- Modo autónomo (el del kit).
- Supervisión: **`claude_completa` provisional**. El plan la pasaba a `asistentes`, pero el workspace no está en
  `trustedWorkspaces` de agy (línea «confianza de agy» del detector). Límite de la instalación: pasa a `asistentes`
  cuando el Director dé la confianza abriendo `agy` en el proyecto; entonces se cambia `supervision.modo`, se vuelve a
  correr `actualizar_kit.py --aplicar` (copia las plantillas `agy_*`/`asist_*`, que ahora salen NO APLICA) y
  `scripts/emitir_agy.py`, y se hacen las pruebas de humo (asistente y asistente navegador).
- Informes: `.md` y `.docx` **sin plantilla**: se quitó `informes.plantilla_docx` (el `.docx` sale en un documento en
  blanco, con aviso). Las rutas quedan las del kit: `docs/borradores/` y `docs/informes/` (esta última ya existía).

**REVISAR y choques.**
- `docs/prompts_arranque/arquitecto.md` (2 conflictos): cabecera del proyecto + las líneas «Nuevo en v1.2/v1.4» del
  kit. «Lo que NO haces — por artefacto y rol» del proyecto, con lo que agrega el kit («No decides lo que excede tu
  alcance», el encuadre no es evidencia, el modelo real en el sello, commits del Agente C en modo autónomo). Reglas
  duras: quedan las 17 del kit con su número (otras piezas las citan por número); donde decían lo mismo (DoD con
  comando, evidencia literal, vector mitigado, anti-bucle, duda) queda la redacción del proyecto; la regla local sin
  equivalente, **Paradas de Observación**, va al final como regla 18. El título de la sección junta los dos: «Reglas
  duras al diseñar, planificar y escribir la orden».
- `asesor.md` (2): queda «traducción pedagógica y recomendación con opciones» del proyecto. La línea «Se archiva en:
  {{DIR_ARTEFACTO}}» se cambió por la del kit («No se archiva en ninguna parte»): con el `escribe_en` del propio
  proyecto («(ninguno — …)») se emitía como una ruta inexistente; lo mismo dice la nota `_escribe_en_nota` del
  proyecto. Entra la regla del kit «No escribes ningún archivo» y se conserva la del proyecto sobre los cuatro
  directorios.
- `auditor.md` (2): se conserva el auditor **cross-vendor en Gemini** del proyecto; entra del kit de dónde sale la
  independencia (contexto frío, material sanitizado, cambio de modelo) y «sin el razonamiento de quien hizo el
  trabajo». No entra la nota del kit sobre la regla v1.2 «solo roles Claude», que este proyecto nunca tuvo.
- `ingeniero.md` (3): cabecera del proyecto (Ruta A desde el Especificador) + línea «Nuevo en v1.2». «Lo que NO haces»
  del proyecto (las 5 reglas, con su redacción) más las del kit (no eliges la medición, mediciones con condiciones,
  no tocas archivos no nombrados, ejecución en copia, duda reabre la orden). La regla del kit «No escribes en
  {{DIR_ARQUITECTO}}» se adaptó a «No escribes órdenes ni especificaciones … aunque compartáis {{DIR_ARQUITECTO}}»,
  porque aquí todos los roles escriben en `auditorias/`. Entran completas «Tu consumo y tus auxiliares» y «Modo
  asistentes». Reglas duras: las 6 del kit con su número; nueva la 5 (finales de línea); la 6 junta el aviso de
  traspaso del proyecto (Parada de Observación, comandos para el Verificador) con lo del kit.
- `verificador.md` (3): cabecera del proyecto + línea «Nuevo en v1.2». «Comprueba metódicamente» del proyecto con lo
  que agrega el kit (cifras que reproducen, comando delante, alcance del diff y finales de línea, todas las pruebas
  en copia, el documento no cambió en silencio). Entran completas «Tus auxiliares» (reglas 1 a 11) y «Modo
  asistentes». «Lo que NO haces — por artefacto y ruta física» queda la del proyecto, con el añadido del kit sobre el
  árbol de trabajo temporal. «Dónde escribes»: la del proyecto, con la evidencia en adjuntos y la re-verificación
  fechada del kit.
- Reglas locales en negrita, antes → después: arquitecto 11 → 39, asesor 8 → 9, auditor 6 → 6, ingeniero 9 → 27,
  verificador 8 → 24. No falta ninguna (comprobado texto por texto; en dos, «No commiteas sin aprobación…», solo se
  añadió el paréntesis del modo autónomo). Sin marcas `<<<<<<<`; todas siguen en LF.
- `coordinacion/bitacora.md` (REVISAR): se creó nueva, con cabecera cerrada por `---` y el índice de decisiones
  delegadas vacío. Las 17 bitácoras por fecha de `docs/` no se tocaron ni se movieron. `modo_autonomo.bitacora` queda
  en `coordinacion/bitacora.md`.
- Rol local `especificador.md` (CONSERVAR): tarea intacta; se le agregaron las reglas 5 a 9 (evidencia con el comando
  delante, ejecución en copia, finales de línea, tope de llamadas, lectura por índice) y el paréntesis de los commits
  en modo autónomo.
- Choques de `coordinador.json`: `reglas_duras.nada_se_commitea_sin_aprobacion` y `no_exportable.roster_de_modelos`
  quedan los del proyecto. Comparación aplanada de `git show HEAD:coordinador.json` con el nuevo: 94 claves antes,
  227 después, ninguna perdida y ninguna cambiada.
- Encargos: el proyecto no tenía directorio de encargos; queda el del kit, `coordinacion/encargos/`.
- Adenda (NUEVA, copiada del kit): su punto 3 se completó con lo que el proyecto documenta (repositorios de
  `.claude/settings.json`, rama `linux` de ActaExpressWeb y `main` del coordinador, `.env` de ActaExpressWeb). La rama
  de BitacoraExpress y ActaExpress no está documentada: el punto 3 dice que la da la orden.
- `docs/modo_de_trabajo.md` (NUEVA, copiada del kit): queda para que el Director complete sus marcadores `>>>` y la
  firme.
- Copia del kit `kit_coordinador/` (1.2, no versionada): sus 39 archivos están en el historial del kit; se respaldó
  en `respaldo_metodologia_2026-11-14/kit_coordinador_anterior_1.2.tar` (línea en el manifiesto) y se reemplazó por
  `git archive main` del kit 1.6.3. `.gitignore`: se agregaron `kit_coordinador/` y `respaldo_metodologia_*/`.

**Comprobación final** (evidencia en la carpeta de trabajo de la actualización, fuera del proyecto):
- detector: «`coordinador.json` declara kit_version 1.6.3»;
- segunda pasada de `--aplicar`: «APLICADO: 0 archivo(s) escritos»;
- `emitir_arranque.py <rol>`, en una copia: exit 0 en los 7 roles con arranque (asesor, arquitecto, especificador,
  ingeniero, verificador, archivista, auditor), sin `{{…}}` sin reemplazar. `coordinador` no tiene arranque (es el
  Agente C);
- `medir_asistentes.py VACIO`: exit 0 («no aplica» en `claude_completa`);
- `encargar.sh PRUEBA arquitecto …`, en la copia: termina en «LÍMITES DE ESTE ENCARGO» con tope 25 (borrado);
- `verificar_informe.py docs/borradores/PRUEBA_informe.md --solo-borrador`, en la copia: control positivo OK y
  `RESULTADO: CONFORME` (borrado).

**Pendiente del Director.**
- Dar la confianza del workspace en agy (abriendo `agy` en el proyecto) y, con eso, pasar a `asistentes` (ver arriba).
- Decir los sitios con inicio de sesión que usarán los asistentes (`scripts/abrir_navegador.py sesion --url <URL>`).
- Informes: si quiere plantilla `.docx`, ponerla y declarar `informes.plantilla_docx` y sus marcadores; los códigos
  internos que no deben salir en un informe (`informes.huella.metodo_extra`; candidatos que ya usa el proyecto:
  `MT-…`, `PO-…`, `BUG-…`, `OBS-…`, `DD-…`); completar los `>>>` de `docs/estandar_documental.md`.
- Completar y firmar `docs/modo_de_trabajo.md` (sus marcadores `>>>`).
- Topes de llamadas para los roles que el kit no trae: `especificador` (recomendado 25, como el Arquitecto), `asesor`
  y `auditor` (`modo_autonomo.topes_llamadas`). Hoy sus encargos no llevan tope propio.
- `scripts/generar_informe.py` (propio, genera el informe de arquitectura con python-docx y mermaid.ink): el kit no lo
  conoce y no se tocó. Recomendación: pasar sus informes al flujo de `renderizar_informe.py` cuando haya plantilla.
- `.agents/skills/` (9 skills propias): no son roles de agy del kit; se conservan sin tocar.
- Recomendaciones del plan: `.gitignore` de capturas de asistentes (`asistentes/**/*.png` y sus dos excepciones) y
  `"subagentPromptCacheTtl": "1h"` en `.claude/settings.json` (no se tocó).
- Commit de la actualización: no se hizo.

**No verificado.**
- El `.docx`: `python-docx` no está en el `python3` del sistema; el renderizado no se probó. El `.venv` del proyecto
  trae python-docx 1.1.2 en su `site-packages`, pero con `.venv/bin/python -I` el renderizador también dijo
  «STOP: falta python-docx».
- agy y el asistente navegador: sin pruebas de humo (falta la confianza del workspace).
- El arranque emitido de cada rol se comprobó por exit 0 y sin marcadores; no se leyó completo.
