"""Genera la definición y los permisos de agy de cada rol con motor agy (kit coordinador v1.5).

Para cada rol de `coordinador.json` con "motor": "agy" escribe:

  · `.agents/agents/<rol>.md`     frontmatter de agy (name, description, model, tools) y, de
                                  cuerpo, la capa de homologación (`agy_capa.md` del
                                  directorio de plantillas, con sus marcadores resueltos);
  · `.agents/permisos/<rol>.json` las reglas allow y deny que `lanzar_agy.py` pone en el
                                  settings.json de agy solo mientras corre el rol.

El `model` del frontmatter solo puede ser flash, pro o inherit (con otro valor agy descarta el
rol sin avisar): sale de `modelo_agy_definicion` o se deduce de `modelo_agy`, y el modelo
exacto lo fija `lanzar_agy.py` con --model.

Los permisos quedan con marcadores ({WS}, {REPO_1}, …) y los resuelve el lanzador; la capa
lleva las rutas reales, porque la lee el rol. Si cambian los repositorios de
`.claude/settings.json`, se vuelve a correr. Los archivos generados no se editan a mano.

Comprueba antes el guardrail `supervision_claude`, según `supervision.modo` de coordinador.json:
  · claude_completa (por defecto): el coordinador y el Verificador corren en Claude, y cada rol
    en agy declara en `supervision_agy` quién mide su artefacto (un validador del workspace o
    "verificador");
  · solo_coordinador: solo el coordinador corre en Claude. El Verificador puede ir en agy, con
    un modelo_agy distinto del de cada rol que revisa, y `supervision_agy` puede ser también
    "coordinador" (su compuerta). Esa compuerta es obligatoria tras cada rol.
  · asistentes (v1.3.2): como claude_completa para los roles de la cadena, y además genera los ASISTENTES de
    `supervision.asistentes.actividades` (un rol agy por actividad: asist_lectura, asist_prototipo, asist_medicion,
    asist_borrador, asist_revision). Un asistente es Gemini en agy, lo lanza y lo vigila un monitor de Claude
    (`supervision_agy`: "monitor"), corre en un modelo gemini-* y escribe solo en `carpeta_salida`.
    Una actividad con "navegador": true (A-navegacion, v1.5) es el asistente navegador: no ejecuta comandos (se le
    niegan todos), su capa sale de `asist_capa_navegador.md` y no de `agy_capa.md`, y `lanzar_agy.py` lo lanza con el
    agente por defecto de agy, el único que puede invocar el subagente `browser` [medido el 09-11-2026, MOTOR_EXTERNO.md §11].
El Asesor no tiene artefacto y no pasa a agy en ningún modo. Si algo falla, no escribe nada.

Roles ad hoc (v1.3.2): `roles_adhoc_agy` en coordinador.json declara roles con la misma forma que un rol de `roles`
(motor agy, modelo_agy, escribe_en, comandos_agy, supervision_agy…) que no pertenecen a la cadena —un auxiliar de
medición, un verificador de prueba—; se generan y se lanzan como cualquier otro. La definición de cada rol
generado (`_rol`) queda en su archivo de permisos, de donde la lee `lanzar_agy.py` si el rol no está en `roles`.

Subagentes: un rol en agy puede declarar "subagentes_agy": ["lectura", "redaccion", "revision"]. Por cada
tipo se escribe `.agents/agents/aux_<tipo>.md` (desde `agy_sub_<tipo>.md`, con `mainAgent: false`,
`subagent: true`, su nivel y solo las herramientas de su tipo) y al rol se le añaden `invoke_subagent`,
`manage_subagents` y la sección `auxiliares` de `agy_roles.md`. Un subagente no puede ejecutar comandos
[medido el 26-10-2026]: se rechaza el tipo «medicion» y todo subagente con `run_command`. Lo que ejecuta
sigue por pasadas (`MOTOR_EXTERNO.md` §9).
Al cuerpo de cada rol se le añaden las secciones `todos` y `<rol>` de `agy_roles.md`.

Intérprete: los ejemplos usan python3 -I; en Windows suele ser python. El script imprime el que usa.

Uso:
    python3 -I scripts/emitir_agy.py [<rol> ...] [--terminal powershell|sh] [--comprobar]
    sin <rol>: todos los roles con motor agy, los de roles_adhoc_agy y, con modo asistentes, los asistentes.
    --comprobar: valida y no escribe.
    --terminal: la de la máquina donde corre agy (por defecto, PowerShell en Windows y sh en el resto).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

PY = os.path.basename(sys.executable) or "python3"   # el intérprete en uso: en Linux suele ser solo python3

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE = Path(__file__).resolve().parents[1]     # convención: scripts/ cuelga de la raíz
DIR_PLANTILLAS_POR_DEFECTO = "docs/prompts_arranque"
# Nombres del registro de herramientas de agy. `command_status` y `finish` salen en la lista
# del init pero hacen fallar el arranque con `unknown component` (MOTOR_EXTERNO.md §3).
REGISTRO = ["view_file", "list_dir", "find_by_name", "grep_search", "run_command",
            "write_to_file", "replace_file_content", "multi_replace_file_content"]
ROMPEN = {"command_status", "finish"}
MODOS = ("claude_completa", "solo_coordinador", "asistentes")
MONITORES = ("haiku", "sonnet", "opus")   # modelos de Claude que pueden monitorizar a un asistente
SIEMPRE_CLAUDE = {"coordinador": "el coordinador corre siempre en Claude"}
SOLO_EN_CLAUDE_COMPLETA = {"verificador": "el Verificador de un trabajo hecho en agy corre en Claude "
                                          "(solo supervision.modo = solo_coordinador lo admite en agy)"}
NUNCA_AGY = {"asesor": "el Asesor no produce artefactos: su conversación la tiene el Director con quien quiera"}
NO_RECOMENDADOS = {"arquitecto": "decide", "ingeniero": "ejecuta y toca el producto",
                   "asesor": "no produce artefactos", "auditor": "audita: su independencia es la gracia"}
# Cada palabra vale solo como palabra suelta (subcomando o argumento, entre espacios, separadores o extremos): así
# `git merge x` se niega y `vm1_merge_test` pasa [medido en las pruebas de la v1.3.2, hallazgo 1].
PELIGROSOS = (r"command(regex:.*(^|[ ;&|(])(push|commit|reset|checkout|rebase|merge|clean|Remove-Item)([ ;&|)]|$).*"
              r"|.*(^|[ ;&|(])(rm -|--output).*)")
# Una petición de ayuda (`--help`, `-h`, `-?`, `/?`) no está en los comandos permitidos y, como todo comando que
# falta, cortaría la ejecución entera [medido, hallazgo 5 de las pruebas de la v1.3.2]. Una regla `deny` explícita no
# corta: el rol recibe el error y sigue (MOTOR_EXTERNO.md §3). Por eso se niega la ayuda de forma explícita.
AYUDA = r"command(regex:.*(^|[ ;&|(])(--help|-h|-[?]|/[?])([ ;&|)]|$).*)"
TERMINALES = {
    "powershell": "- La terminal es **PowerShell**. No hay `sed`, `grep`, `cat`, `head` ni `wc`.",
    "sh": "- La terminal es `sh`. Aun así, lee y busca con las herramientas de abajo, no con "
          "`sed`, `grep` ni `cat`: solo corren tus comandos permitidos.",
}
MODELOS_DEFINICION = ("flash", "pro", "inherit")   # lo único que agy carga en el frontmatter [medido]
HERRAMIENTAS_SUB = ["invoke_subagent", "manage_subagents"]
SUBAGENTES = {   # tipo -> plantilla y línea que lee el rol que lo invoca
    "lectura": ("agy_sub_lectura.md", "devuelve líneas literales con su puntero `ruta:línea`; no resume ni interpreta (nivel flash_lite)"),
    "redaccion": ("agy_sub_redaccion.md", "escribe el borrador que le dictas, en la ruta que le das, sin añadir hechos (nivel flash)"),
    "revision": ("agy_sub_revision.md", "compara dos textos, o un texto contra una fuente, y devuelve las diferencias con punteros, sin juzgar (nivel flash)"),
}
SUB_RECHAZADOS = {"medicion": "los subagentes no pueden ejecutar comandos (permission check failed for unsandboxed, "
                              "medido el 26-10-2026): una medición va por pasadas, con el «Pedido de auxiliar»"}
MARCA = "Generado por scripts/emitir_agy.py desde coordinador.json (kit coordinador v1.5). No se edita a mano: se regenera."
NIEGA_TODO = "command(regex:.*)"   # el asistente navegador no corre comandos: un deny explícito no corta [medido 09-11-2026]


def modo_de(cfg: dict) -> str:
    m = (cfg.get("supervision") or {}).get("modo", "claude_completa")
    if m not in MODOS:
        raise SystemExit(f"supervision.modo {m!r} no vale: {' o '.join(MODOS)}.")
    return m


def prohibidos(roles: dict, modo: str) -> dict:
    """Roles que no pueden declarar motor agy en este modo, con su razón."""
    p = {**SIEMPRE_CLAUDE, **NUNCA_AGY}
    if modo != "solo_coordinador":      # claude_completa y asistentes: el Verificador corre en Claude
        p.update(SOLO_EN_CLAUDE_COMPLETA)
    return p


def leer_json(p: Path) -> dict:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise SystemExit(f"No se pudo leer {p}: {e}")


def repositorios() -> list[str]:
    dirs = (leer_json(BASE / ".claude" / "settings.json").get("permissions") or {}).get("additionalDirectories") or []
    if not dirs:
        raise SystemExit("`permissions.additionalDirectories` está vacío: un rol que no sabe dónde puede "
                         "leer, lee donde no debe.")
    salida = []
    for d in dirs:
        s = str(d)
        if os.name == "nt" and re.match(r"^/[a-zA-Z]/", s):
            s = s[1].upper() + ":" + s[2:]
        q = Path(s) if Path(s).is_absolute() else BASE / s
        salida.append(q.resolve().as_posix())
    return salida


def mismo_camino(s: str) -> str:
    """Ruta comparable: barras `/`, sin barra final y, en Windows, sin mayúsculas."""
    s = str(s).replace("\\", "/").rstrip("/") or "/"
    return s.casefold() if os.name == "nt" else s


def carpeta(r: dict) -> str | None:
    d = (r.get("escribe_en") or "").strip().strip("/")
    return None if not d or d.startswith("(") or d in ("—", "-") else d


def comprobar(nombre: str, r: dict, roles: dict, modo: str = "claude_completa") -> list[str]:
    """Lista de fallos del rol; vacía si se puede generar."""
    f = []
    if nombre in prohibidos(roles, modo):
        return [f"{nombre}: {prohibidos(roles, modo)[nombre]} (guardrail supervision_claude, modo {modo})"]
    if not carpeta(r):
        f.append(f"{nombre}: no tiene carpeta propia (escribe_en); un rol sin artefacto no pasa a agy")
    if not r.get("modelo_agy"):
        f.append(f"{nombre}: falta modelo_agy")
    if r.get("modelo_agy_definicion") and not modelo_definicion(r):
        f.append(f"{nombre}: modelo_agy_definicion {r['modelo_agy_definicion']!r} no vale; agy descarta en silencio "
                 f"el rol con otro valor que {', '.join(MODELOS_DEFINICION)}")
    cmds = r.get("comandos_agy")
    if r.get("navegador"):
        if cmds:
            f.append(f"{nombre}: el asistente navegador no ejecuta comandos; deja comandos_agy vacío")
        if not r.get("asistente"):
            f.append(f"{nombre}: «navegador» solo vale en una actividad de supervision.asistentes")
        cmds = []
    elif not isinstance(cmds, list) or not cmds:
        f.append(f"{nombre}: comandos_agy vacío; un rol sin comandos no corre ni su validador")
    for c in cmds or []:
        rx = c.get("regex") if isinstance(c, dict) else c
        if not isinstance(rx, str) or not (rx.startswith("^") and rx.endswith("$")):
            f.append(f"{nombre}: comando sin anclar (^…$): {rx!r}")
            continue
        if "dangerously" in rx:
            f.append(f"{nombre}: --dangerously-skip-permissions está prohibido")
        try:
            re.compile(re.sub(r"\{(WS|REPO_\d+)\}", "X", rx))
        except re.error as e:
            f.append(f"{nombre}: regex inválida {rx!r}: {e}")
        doble = re.search(r"\\\\[.()\[\]{}|?*+^$nsdwNSDW]", rx)
        if doble:
            f.append(f"{nombre}: la regex {rx!r} lleva una barra invertida doble ({doble.group(0)!r}) delante de un "
                     "carácter especial: tras leer el JSON casaría una barra literal y el comando nunca casaría")
    if r.get("asistente"):
        if not str(r.get("modelo_agy") or "").lower().startswith("gemini-"):
            f.append(f"{nombre}: un asistente corre en un modelo gemini-*, no en {r.get('modelo_agy')!r} (la bolsa "
                     "«Claude and GPT» de agy no se gasta en trabajo de rutina)")
        if r.get("monitor") not in MONITORES:
            f.append(f"{nombre}: falta el modelo del monitor de Claude (monitor: {', '.join(MONITORES)})")
    sup = r.get("supervision_agy")
    if not sup:
        f.append(f"{nombre}: falta supervision_agy (un validador del workspace, \"verificador\", \"monitor\" en un "
                 "asistente o, en solo_coordinador, \"coordinador\")")
    elif sup == "monitor":
        if not (r.get("asistente") and modo == "asistentes"):
            f.append(f"{nombre}: supervision_agy \"monitor\" solo vale en un asistente con supervision.modo = asistentes")
    elif sup == "coordinador":
        if modo != "solo_coordinador" and not r.get("adhoc"):     # un rol ad hoc lo mide quien lo lanza
            f.append(f"{nombre}: supervision_agy \"coordinador\" solo vale con supervision.modo = solo_coordinador "
                     "(o en un rol de roles_adhoc_agy)")
    elif sup == "verificador":
        v = roles.get("verificador")
        if nombre == "verificador":
            f.append("verificador: no puede ser su propio supervisor (supervision_agy \"verificador\")")
        elif not v:
            f.append(f"{nombre}: supervision_agy es el Verificador, y no hay uno")
        elif v.get("motor", "claude") == "claude":
            pass
        elif modo != "solo_coordinador":
            f.append(f"{nombre}: supervision_agy es el Verificador, y no hay uno en Claude")
        elif v.get("modelo_agy") and v.get("modelo_agy") == r.get("modelo_agy"):
            f.append(f"{nombre}: el Verificador en agy usa el mismo modelo_agy ({v['modelo_agy']}) que el rol "
                     "que revisa; en solo_coordinador tiene que ser un nivel distinto")
    elif not (BASE / sup).is_file():
        f.append(f"{nombre}: el validador de supervision_agy no existe: {sup}")
    f += [f"{nombre}: {t}" for t in subagentes_de(r)[1]]
    h = r.get("herramientas_agy") or REGISTRO
    if set(h) & ROMPEN:
        f.append(f"{nombre}: herramientas que rompen el arranque de agy: {', '.join(sorted(set(h) & ROMPEN))}")
    if set(h) - set(REGISTRO) - ROMPEN - set(HERRAMIENTAS_SUB):
        f.append(f"{nombre}: herramientas fuera del registro de agy: "
                 f"{', '.join(sorted(set(h) - set(REGISTRO) - set(HERRAMIENTAS_SUB)))}")
    return f


def subagentes_de(r: dict) -> tuple[list, list]:
    """Subagentes que declara el rol: ([(tipo, herramientas o None)], fallos).

    Cada elemento de `subagentes_agy` es un tipo (cadena) o {"tipo": …, "herramientas": […]}."""
    decl, fallos, vistos = r.get("subagentes_agy") or [], [], set()
    if not isinstance(decl, list):
        return [], ["subagentes_agy tiene que ser una lista de tipos"]
    salida = []
    for d in decl:
        tipo = d.get("tipo") if isinstance(d, dict) else d
        herr = d.get("herramientas") if isinstance(d, dict) else None
        if tipo in SUB_RECHAZADOS:
            fallos.append(f"subagente {tipo!r} rechazado: {SUB_RECHAZADOS[tipo]}")
        elif tipo not in SUBAGENTES:
            fallos.append(f"subagente {tipo!r} desconocido; valen {', '.join(SUBAGENTES)}")
        elif tipo in vistos:
            fallos.append(f"subagente {tipo!r} repetido")
        elif herr is not None and (not isinstance(herr, list) or "run_command" in herr
                                   or set(herr) - set(REGISTRO)):
            fallos.append(f"subagente {tipo!r}: herramientas {herr!r} no valen; run_command está prohibido "
                          "(los subagentes no ejecutan comandos) y el resto sale del registro de agy")
        else:
            salida.append((tipo, herr))
        vistos.add(tipo)
    return salida, fallos


def modelo_definicion(r: dict) -> str:
    """Valor de `model` en el frontmatter: solo flash, pro o inherit; cualquier otro, agy descarta el rol en silencio.

    Con modelo_agy_definicion, ese valor (y no otro). Sin él, se deduce de modelo_agy:
    «flash» da flash; «pro» o «argon» dan pro; el resto, inherit. El modelo exacto lo fija
    lanzar_agy.py con --model."""
    d = r.get("modelo_agy_definicion")
    if d:
        return d if d in MODELOS_DEFINICION else ""
    m = str(r.get("modelo_agy") or "").lower()
    if "flash" in m:
        return "flash"
    if "pro" in m or "argon" in m:
        return "pro"
    return "inherit"


def asistentes_de(cfg: dict, modo: str) -> tuple[dict, list]:
    """Roles-asistente que declara `supervision.asistentes.actividades` (solo con modo = asistentes).

    Devuelve ({nombre del rol: definición como la de un rol de la cadena}, fallos). Cada actividad (A-lectura,
    A-prototipo…) es un rol agy que escribe solo en `carpeta_salida`, corre en un modelo gemini-* y lo vigila un
    monitor de Claude (`monitor`). Con otro modo la sección se ignora: está en el ejemplo para quien la active."""
    a = (cfg.get("supervision") or {}).get("asistentes") or {}
    if modo != "asistentes" or not a:
        return {}, []
    salida, fallos = {}, []
    carpeta_salida = a.get("carpeta_salida") or "asistentes/"
    for act, d in (a.get("actividades") or {}).items():
        if not isinstance(d, dict):
            fallos.append(f"asistentes.actividades.{act}: tiene que ser un objeto")
            continue
        nombre = d.get("rol") or "asist_" + re.sub(r"[^a-z0-9]+", "_", act.lower().replace("a-", "", 1)).strip("_")
        if not re.fullmatch(r"[a-z][a-z0-9_]*", nombre):
            fallos.append(f"asistentes.actividades.{act}: el rol {nombre!r} no es un nombre válido (a-z, 0-9 y _)")
            continue
        rol = {
            "motor": "agy", "asistente": True, "actividad": act,
            "modelo_agy": d.get("asistente"), "modelo_agy_definicion": d.get("modelo_agy_definicion"),
            "monitor": d.get("monitor"), "comandos_agy": d.get("comandos_agy") or ([] if d.get("navegador") else None),
            "navegador": True if d.get("navegador") else None,
            "herramientas_agy": d.get("herramientas_agy"), "tope_llamadas_agy": d.get("tope_llamadas_agy", 60),
            "supervision_agy": "monitor", "escribe_en": carpeta_salida,
            "artefacto": f"resultado de {act} (orienta; no es un hecho hasta que el monitor lo vuelve a medir)",
        }
        salida[nombre] = {k: v for k, v in rol.items() if v is not None}
    return salida, fallos


def adhoc_de(cfg: dict) -> dict:
    """Roles ad hoc de `roles_adhoc_agy`: la forma de un rol de `roles`, fuera de la cadena (hallazgo 5 del piloto)."""
    adhoc = cfg.get("roles_adhoc_agy") or {}
    return {n: {**r, "motor": "agy", "adhoc": True}
            for n, r in adhoc.items() if isinstance(r, dict) and not n.startswith("_")}


def permisos(nombre: str, r: dict, roles: dict, repos: list[str], dir_plant: str) -> dict:
    propia = carpeta(r)
    n_repos = len(repos)
    allow = [f"read_file({{REPO_{i}}})" for i in range(1, n_repos + 1)]
    allow += [f"command(regex:{c['regex'] if isinstance(c, dict) else c})" for c in r.get("comandos_agy") or []]
    # v1.6.2: un repositorio que coincide con el workspace no lleva la negativa general de escritura. Taparía la carpeta
    # de salida del rol (deny gana sobre allow) y el rol no podría escribir nada. Quedan las negativas de .git, .agents,
    # .claude, scripts/, las plantillas y las carpetas de los otros roles, y en `-p` nada se escribe sin regla [medido].
    ws = mismo_camino(BASE.resolve().as_posix())
    deny = [f"write_file({{REPO_{i}}})" for i, repo in enumerate(repos, 1) if mismo_camino(repo) != ws]
    deny += [f"write_file({{WS}}/{d})" for d in (".git", ".agents", ".claude", "scripts", dir_plant.strip("/"))]
    for otro, ro in sorted(roles.items()):
        d = carpeta(ro)
        # La propia, y toda carpeta que la contenga, no se niegan: deny gana sobre allow.
        if otro == nombre or not d or (propia + "/").startswith(d + "/"):
            continue
        regla = f"write_file({{WS}}/{d})"
        if regla not in deny:
            deny.append(regla)
    deny += [NIEGA_TODO] if r.get("navegador") else [PELIGROSOS, AYUDA]
    return {"_nota": f"Permisos del rol {nombre} en agy. {MARCA} Los aplica scripts/lanzar_agy.py solo "
                     "mientras corre el rol, con {WS} = workspace y {REPO_n} = repositorios de "
                     ".claude/settings.json en su orden; la carpeta de salida (--salida) se añade sola.",
            "_rol": {"motor": "agy", "modelo_agy": r.get("modelo_agy"), "escribe_en": r.get("escribe_en"),
                     "asistente": bool(r.get("asistente")), "actividad": r.get("actividad"),
                     "monitor": r.get("monitor"), **({"navegador": True} if r.get("navegador") else {})},
            "allow": allow, "deny": deny}


def cuerpo_capa(dir_plant: Path, nombre: str = "agy_capa.md") -> str:
    p = dir_plant / nombre
    if not p.exists():
        raise SystemExit(f"Falta la plantilla {p} (cópiela de plantillas/{nombre} del kit).")
    m = re.search(r"^````text\n(.*?)^````$", p.read_text(encoding="utf-8"), re.S | re.M)
    if not m:
        raise SystemExit(f"No se encontró el bloque ````text en {p}.")
    return m.group(1).rstrip("\n")


def supervisor(sup: str, verificador_agy: bool) -> str:
    """Quién mide el artefacto, en la frase que lee el rol."""
    if sup == "monitor":
        return ("un monitor de Claude, que vuelve a medir una muestra contra las fuentes antes de aceptarte; lo "
                "tuyo orienta y no es un hecho hasta que él (o el Arquitecto) lo vuelva a medir")
    if sup == "coordinador":
        return "la compuerta del coordinador (corre tus validadores y vuelve a medir una muestra contra las fuentes)"
    if sup == "verificador":
        if verificador_agy:
            return "un Verificador con un nivel de modelo distinto del tuyo, que solo ve tu entregable y las fuentes"
        return "un Verificador en Claude"
    return f"el validador determinista `{sup}`"


def secciones_roles(dir_plant: Path) -> dict:
    """Secciones `## <rol>` de agy_roles.md (cada una, un bloque ````text); la de `todos` va a todos los roles."""
    p = dir_plant / "agy_roles.md"
    if not p.exists():
        print(f"[aviso] no hay {p}: los roles salen solo con la capa general (cópiela de plantillas/agy_roles.md del kit)",
              file=sys.stderr)
        return {}
    patron = r"^## (\w+)\n+````text\n(.*?)^````$"
    return {m.group(1): m.group(2).rstrip("\n")
            for m in re.finditer(patron, p.read_text(encoding="utf-8"), re.S | re.M)}


def definicion(nombre: str, r: dict, proyecto: str, repos: list[str], capa: str, terminal: str,
               extra: dict | None = None, verificador_agy: bool = False) -> str:
    subs = [t for t, _ in subagentes_de(r)[0]]
    if subs and not (extra or {}).get("auxiliares"):
        raise SystemExit(f"{nombre}: declara subagentes y falta la sección `auxiliares` en agy_roles.md "
                         "(cópiela de plantillas/agy_roles.md del kit).")
    capa = "\n\n".join([capa] + [s for s in ((extra or {}).get("todos"),
                                            (extra or {}).get("asistente") if r.get("asistente") else None,
                                            (extra or {}).get(nombre),
                                            (extra or {}).get("auxiliares") if subs else None) if s])
    rutas = {"WS": BASE.resolve().as_posix(), **{f"REPO_{i}": v for i, v in enumerate(repos, 1)}}

    def real(s: str) -> str:
        for k, v in rutas.items():
            s = s.replace("{" + k + "}", v)
        return s

    formas = [real(c.get("forma") or c["regex"]) if isinstance(c, dict) else real(c) for c in r.get("comandos_agy") or []]
    sup = r["supervision_agy"]
    valores = {
        "ROL": nombre,
        "ACTIVIDAD": str(r.get("actividad") or "-"),
        "PROYECTO": proyecto,
        "DIR_ARTEFACTO": carpeta(r) + "/",
        "REPOS": "\n".join(f"- `{v}`" for v in repos),
        "TERMINAL": TERMINALES[terminal],
        "COMANDOS": "\n".join(f"- `{x}`" for x in formas) or "- ninguno",
        "TOPE_LLAMADAS": str(r.get("tope_llamadas_agy") or 60),
        "SUPERVISION": supervisor(sup, verificador_agy),
        "SUBAGENTES_CAPA": ("Subagentes: solo los de tu sección «Tus auxiliares»." if subs
                            else "No tienes subagentes."),
        "SUBAGENTES_TODOS": ("Tu único subagente es `browser`: navega dentro de tu turno y no ejecuta comandos."
                             if r.get("navegador") else
                             "Tus subagentes leen y redactan dentro de tu turno; ninguno ejecuta comandos."
                             if subs else "No tienes subagentes."),
        "AUXILIARES": "\n".join(f"- `aux_{t}`: {SUBAGENTES[t][1]}." for t in subs),
    }
    for k, v in valores.items():
        capa = capa.replace("{{" + k + "}}", v)
    pendientes = sorted(set(re.findall(r"\{\{(\w+)\}\}", capa)))
    if pendientes:
        raise SystemExit("Marcadores sin resolver en la capa: " + ", ".join(pendientes))
    descripcion = (f"Rol {nombre} del coordinador {proyecto}: produce {r.get('artefacto', '?')} en "
                   f"{carpeta(r)}/. Lo lanza scripts/lanzar_agy.py; solo lee los repositorios de trabajo.")
    herramientas = list(r.get("herramientas_agy") or REGISTRO)
    if r.get("navegador"):      # informativo: agy no carga este frontmatter (el lanzador no usa --agent con él)
        herramientas = ["view_file", "list_dir", "write_to_file"]
    if subs:
        herramientas += [h for h in HERRAMIENTAS_SUB if h not in herramientas]
    cabecera = ["---",
                f"name: {nombre}",
                f"description: {json.dumps(descripcion, ensure_ascii=False)}",
                "mainAgent: true",
                "subagent: false",
                f"model: {modelo_definicion(r)}",
                f"tools: {json.dumps(herramientas)}",
                "---", "", ""]
    return "\n".join(cabecera) + capa + f"\n\n<!-- {MARCA} -->\n"


def definicion_sub(tipo: str, herr: list | None, proyecto: str, dir_plant: Path) -> str:
    """`.agents/agents/aux_<tipo>.md` desde la plantilla `agy_sub_<tipo>.md` (su último bloque de texto)."""
    p = dir_plant / SUBAGENTES[tipo][0]
    if not p.exists():
        raise SystemExit(f"Falta la plantilla {p} (cópiela de plantillas/{SUBAGENTES[tipo][0]} del kit).")
    bloques = re.findall(r"^````text\n(.*?)^````$", p.read_text(encoding="utf-8"), re.S | re.M)
    if not bloques:
        raise SystemExit(f"No se encontró el bloque de texto en {p}.")
    t = bloques[-1].replace("{{NOMBRE}}", f"aux_{tipo}").replace("{{PROYECTO}}", (proyecto or "?").replace(chr(34), chr(39))).rstrip("\n")
    if herr is not None:
        t = re.sub(r"^tools: .*$", lambda _: "tools: " + json.dumps(herr), t, count=1, flags=re.M)
    m = re.search(r"^tools: (\[.*\])$", t, re.M)
    tools = json.loads(m.group(1)) if m else []
    if not m or "run_command" in tools or set(tools) - set(REGISTRO):
        raise SystemExit(f"aux_{tipo}: sus herramientas no valen (sin `tools:`, con run_command o fuera del "
                         "registro): los subagentes no ejecutan comandos.")
    for clave in ("mainAgent: false", "subagent: true"):
        if clave not in t:
            raise SystemExit(f"aux_{tipo}: la plantilla {p.name} tiene que llevar `{clave}`.")
    return t + f"\n\n<!-- {MARCA} -->\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("roles", nargs="*")
    ap.add_argument("--terminal", choices=sorted(TERMINALES),
                    default="powershell" if os.name == "nt" else "sh")
    ap.add_argument("--comprobar", action="store_true")
    a = ap.parse_args()

    cfg_path = BASE / "coordinador.json"
    if not cfg_path.exists():
        raise SystemExit(f"Falta {cfg_path}. Copie coordinador.example.json del kit y complételo.")
    cfg = leer_json(cfg_path)
    roles = cfg.get("roles") or {}
    modo = modo_de(cfg)
    vetados = prohibidos(roles, modo)
    fallos = [f"{n}: {vetados[n]} (guardrail supervision_claude, modo {modo})"
              for n in vetados if (roles.get(n) or {}).get("motor", "claude") != "claude"]
    adhoc = adhoc_de(cfg)
    asist, fallos_asist = asistentes_de(cfg, modo)
    fallos += fallos_asist
    fallos += [f"{n}: el nombre ya es un rol de la cadena; un rol ad hoc o un asistente no lo reemplaza"
               for n in list(adhoc) + list(asist) if n in roles]
    fallos += [f"{n}: el nombre está en roles_adhoc_agy y es también un asistente" for n in adhoc if n in asist]
    fallos += [f"{n}: {vetados[n]} (un rol ad hoc no lo reemplaza)" for n in adhoc if n in vetados]
    cadena = {**roles, **adhoc}                      # roles con carpeta propia: las demás carpetas se les niegan
    todos = {**cadena, **asist}                      # lo que se puede generar
    pedidos = [x.strip().lower() for x in a.roles] or (
        [n for n, r in roles.items() if r.get("motor") == "agy"] + list(adhoc) + list(asist))
    for n in pedidos:
        if n not in todos:
            fallos.append(f"{n}: no existe en coordinador.json (ni en roles_adhoc_agy ni entre los asistentes)")
        elif todos[n].get("motor", "claude") != "agy":
            fallos.append(f"{n}: declara motor {todos[n].get('motor', 'claude')!r}, no agy")
        else:
            fallos += [x for x in comprobar(n, todos[n], roles, modo) if x not in fallos]
    if fallos:
        print("No se genera nada:", file=sys.stderr)
        for x in fallos:
            print(f"  - {x}", file=sys.stderr)
        return 1
    if not pedidos:
        print("Ningún rol declara motor agy: no hay nada que generar.")
        return 0
    for n in pedidos:
        if modo != "solo_coordinador" and n in NO_RECOMENDADOS and not (todos.get(n) or {}).get("asistente"):
            print(f"[aviso] {n} en agy no se recomienda: {NO_RECOMENDADOS[n]} (MOTOR_EXTERNO.md §6)", file=sys.stderr)

    repos = repositorios()
    dir_plant_rel = (cfg.get("proyecto") or {}).get("dir_plantillas") or DIR_PLANTILLAS_POR_DEFECTO
    capa = cuerpo_capa(BASE / dir_plant_rel)
    capa_nav = (cuerpo_capa(BASE / dir_plant_rel, "asist_capa_navegador.md")
                if any(todos[n].get("navegador") for n in pedidos) else "")
    proyecto = (cfg.get("proyecto") or {}).get("nombre", "")
    extra = secciones_roles(BASE / dir_plant_rel)
    verificador_agy = (roles.get("verificador") or {}).get("motor", "claude") == "agy"
    print(f"[modo de supervisión: {modo}]")
    salidas = []
    for n in pedidos:
        r = todos[n]
        salidas.append((BASE / ".agents" / "agents" / f"{n}.md",
                        definicion(n, r, proyecto, repos, capa_nav if r.get("navegador") else capa, a.terminal, extra,
                                   verificador_agy)))
        salidas.append((BASE / ".agents" / "permisos" / f"{n}.json",
                        json.dumps(permisos(n, r, cadena, repos, dir_plant_rel), ensure_ascii=False, indent=2) + "\n"))
    subs_out: dict = {}
    for n in pedidos:
        for tipo, herr in subagentes_de(todos[n])[0]:
            texto = definicion_sub(tipo, herr, proyecto, BASE / dir_plant_rel)
            if tipo in subs_out and subs_out[tipo][1] != texto:
                raise SystemExit(f"aux_{tipo}: los roles que lo declaran lo piden con herramientas distintas; "
                                 "se escribe un solo archivo por tipo.")
            subs_out[tipo] = (BASE / ".agents" / "agents" / f"aux_{tipo}.md", texto)
    salidas += list(subs_out.values())
    for destino, texto in salidas:
        if a.comprobar:
            print(f"[comprobado] {destino.relative_to(BASE).as_posix()} ({texto.count(chr(10))} líneas)")
            continue
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes(texto.encode("utf-8"))
        print(f"[escrito] {destino.relative_to(BASE).as_posix()} ({texto.count(chr(10))} líneas)")
    for n in pedidos:
        if todos[n].get("subagentes_agy"):
            print(f"[{n} · subagentes · {', '.join('aux_' + t for t, _ in subagentes_de(todos[n])[0])}] "
                  "invocables por nombre; no aparecen en `agy agents` (MOTOR_EXTERNO.md §9)")
        if todos[n].get("navegador"):
            print(f"[{n} · asistente navegador de {todos[n]['actividad']} · {todos[n]['modelo_agy']} · monitor "
                  f"{todos[n]['monitor']}] el monitor abre Chrome con {PY} -I scripts/abrir_navegador.py abrir, lo lanza con "
                  f"{PY} -I scripts/lanzar_agy.py {n} <encargo> --salida {carpeta(todos[n])}/<ciclo>_<id> y lo cierra con "
                  f"{PY} -I scripts/abrir_navegador.py cerrar (MOTOR_EXTERNO.md §11)")
            continue
        if todos[n].get("asistente"):
            print(f"[{n} · asistente de {todos[n]['actividad']} · {todos[n]['modelo_agy']} · monitor {todos[n]['monitor']}] "
                  "lo lanza el monitor de Claude con: "
                  f"{PY} -I scripts/lanzar_agy.py {n} <encargo> --salida {carpeta(todos[n])}/<ciclo>_<id> "
                  "(plantillas asist_*.md del kit)")
            continue
        print(f"[{n} · agy · {todos[n]['modelo_agy']}] encargo con: sh scripts/encargar.sh <ciclo> {n} \"<tarea>\"; "
              f"lanzamiento con: {PY} -I scripts/lanzar_agy.py {n} <encargo> --salida {carpeta(todos[n])}/<carpeta>")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
