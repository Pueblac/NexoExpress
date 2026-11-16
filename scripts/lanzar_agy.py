"""Lanza un rol del kit en el motor externo `agy` con permisos mínimos (kit coordinador v1.5).

`agy` es la CLI de Antigravity (ver `MOTOR_EXTERNO.md`). Guarda los permisos en un único
archivo global (~/.gemini/antigravity-cli/settings.json; no hay archivo por proyecto). Por eso
este script, mientras corre el rol, escribe en ese archivo los permisos del rol
(`.agents/permisos/<rol>.json` más la carpeta de salida) y al terminar lo deja exactamente como
estaba, byte a byte y comprobado, también si agy falla o se agota el tope. Nunca usa
`--dangerously-skip-permissions`: está prohibido. Un candado, creado de forma atómica (O_EXCL),
impide dos lanzamientos a la vez, porque los permisos de uno pisarían los del otro.

Mientras corre el rol, ese archivo vale para TODO agy en la máquina: no se usa agy en otra ventana
hasta que termine, y el candado serializa los lanzamientos de todos los proyectos. Si el archivo
cambia de CONTENIDO durante la corrida (agy u otra sesión), esa versión se guarda en
`settings.json.durante_<sello>` junto al original, se avisa con las claves cambiadas (línea WARN) y se
restaura el original. Se compara el JSON ya leído, no los bytes: agy reescribe el archivo escapando & | < >
como u0026, u003c y u003e y eso no es un cambio (v1.3.2).

Guarda el registro completo (stream-json) y un resumen: estado, acciones denegadas, comandos
corridos, herramientas que fallaron y el consumo, con una línea en las mismas columnas que
`medir_consumo.py` para comparar con los roles de Claude. En modo sin intervención, un permiso
que falta corta la ejecución entera y agy sale con 0: el resumen lo marca como CORTADA.

KIT COORDINADOR — no hay rutas absolutas. El workspace sale de la ubicación del script y los
repositorios, de `.claude/settings.json` (permissions.additionalDirectories), como en
`emitir_arranque.py`. Marcadores de `.agents/permisos/<rol>.json`:
    {WS}                    la raíz del workspace
    {REPO_1}, {REPO_2}, …   los repositorios de additionalDirectories, en su orden
Compatibilidad (v1.3.2): el formato anterior de otros coordinadores usa {REPO} y {JUEGO}; con UN solo
repositorio se leen como {REPO_1} y el lanzador lo avisa; con varios, STOP (no adivina cuál).
Todos se escriben con letra de unidad y barras `/` en Windows (agy no casa la regla sin la
letra). Dentro de `command(regex:…)` el valor va escapado, para que un `.` de la ruta no
case cualquier carácter.

Intérprete: los ejemplos usan python3 -I; en Windows suele ser python. El script imprime el que usa.

Uso:
    python3 -I scripts/lanzar_agy.py <rol> <encargo.txt> --salida <carpeta relativa al workspace>
        [--modelo <id>] [--tope 30] [--registro <carpeta>] [--conversacion <id> [--nota <texto o ruta>]]
        [--escritura <ruta> ...] [--plan <plan.md>]
    python3 -I scripts/lanzar_agy.py --restaurar
    --modelo   por defecto, `modelo_agy` del rol en coordinador.json.
    --escritura  repetible: permiso de escritura extra SOLO para este lanzamiento (por ejemplo, los
               «Archivos autorizados» de la orden que cumple el Ingeniero). La ruta tiene que estar
               dentro del workspace o de un repositorio de trabajo, nunca bajo .git, .agents ni .claude,
               y no dentro de una carpeta que los permisos del rol protegen (las de otros roles, scripts/,
               las plantillas). Dentro de un repositorio de trabajo, el lanzador retira solo para esa
               corrida la negativa a escribir en el repositorio entero y deja permitidas únicamente las
               rutas dadas. Se imprimen en el resumen.
    --nota     con --conversacion: el mensaje con el que se sigue (texto, o la ruta de un archivo de
               texto de hasta 4000 caracteres), en lugar del mensaje fijo.
    --tope     en minutos: va a `--print-timeout` de agy y, con 2 minutos más, al proceso.
    --conversacion  sigue una ejecución anterior (por ejemplo, una CORTADA) con un mensaje corto
               en lugar del arranque.
    --plan     solo asistentes (rol con "asistente": true): para un modelo Argon, el plan de actividades que
               lleva la línea «Justificación Argon: <por qué>». Un asistente solo corre en modelos gemini-*.
    --restaurar  deja settings.json como estaba si un lanzamiento se cortó sin restaurarlo
               (lo avisa `detectar_metodologia.py`). Solo si no hay otro lanzamiento corriendo.

Antes de nada comprueba que el workspace esté en "trustedWorkspaces" del settings.json de agy
[medido]: si no, agy no carga ningún rol y el lanzamiento falla con «unknown agent». Si no
está, STOP. La confianza la da el usuario abriendo `agy` en interactivo dentro del workspace y
aceptando; el lanzador nunca la añade.

Variables de entorno:
    AGY           ejecutable de agy. Si no está, `agy` del PATH; si no, %LOCALAPPDATA%/agy/bin.
                  Si apunta a un .py (un agy falso para probar), se corre con este intérprete.
    AGY_SETTINGS  ruta del settings.json de agy (por defecto ~/.gemini/antigravity-cli/settings.json).
                  Sirve para probar sin tocar el real.

Cuota: si el resultado es ERROR (o no hay resultado) y el error o el stderr nombran quota,
RESOURCE_EXHAUSTED, 429 o rate limit, sale con el código 4 «CUOTA». El aviso dice qué hacer (mirar
/usage en una sesión interactiva, esperar la renovación de 5 h o bajar a un modelo flash). NUNCA
activa créditos de pago: es un gasto que decide el usuario.

Salida: exit 0 si el rol terminó; 3 si quedó CORTADA, TIMEOUT, sin resultado o con un comando SIN_EVIDENCIA
(un paso DONE sin la salida de la herramienta: no se da por corrido); 4 si es CUOTA; 1 en
un STOP (nada se lanzó) o si settings.json no quedó igual (restaurarlo desde el respaldo antes de
seguir). El coordinador no se lanza nunca en agy. Si settings.json cambió durante la corrida el exit
no cambia: sigue el del rol, y se añade una línea WARN.
La primera línea del resumen dice `EXIT_DEL_LANZADOR=N`: ese es el que cuenta (el `exit` de agy solo dice que el
proceso terminó, y con CORTADA o SIN_EVIDENCIA el estado se imprime como «NO VALE (agy dijo …)», no como éxito).

Asistente navegador (v1.5, actividad con "navegador": true): se lanza SIN `--agent`, con el agente por defecto de agy,
porque un rol de `.agents/agents/` no puede invocar el subagente `browser` (ni con `tools`, ni sin él, ni con otras
claves: medido el 09-11-2026, `MOTOR_EXTERNO.md` §11). Su definición (`.agents/agents/<rol>.md`, sin el frontmatter) va al
principio del mensaje, y los permisos son los de siempre, con todos los comandos negados. Antes de nada exige el Chrome
del kit abierto (`abrir_navegador.py abrir`: el puerto responde y existe `DevToolsActivePort`); si no, STOP. El
agente por defecto tiene herramientas que el rol no debe usar (buscar en la web, leer URL sin el navegador, generar
imágenes, programar tareas, otros subagentes): cada uso sale como FUERA_DE_ALCANCE y el lanzamiento no vale (exit 3).
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]     # convención: scripts/ cuelga de la raíz
PY = os.path.basename(sys.executable) or "python3"   # el intérprete en uso: en Linux suele ser solo python3
AJUSTES = Path(os.environ.get("AGY_SETTINGS") or Path.home() / ".gemini" / "antigravity-cli" / "settings.json")
RESPALDO = AJUSTES.with_name(AJUSTES.name + ".lanzar_agy")
CANDADO = AJUSTES.with_name("lanzar_agy.lock")
PROHIBIDAS = ("write_file({WS}/.git", "write_file({WS}/.agents", "write_file({WS}/.claude")
CARPETAS_VEDADAS = (".git", ".agents", ".claude")
CUOTA = re.compile(r"quota|RESOURCE_EXHAUSTED|\b429\b|rate[ _-]?limit", re.I)
TOPE_NOTA = 4000
FALTA = object()
# Asistente navegador (v1.5): lo que usa el agente por defecto de agy y el rol no debe. La lista es de lo que NO vale
# (el registro de agy crece entre versiones): leer, escribir en su carpeta, esperar e invocar `browser` sí valen.
FUERA_NAVEGADOR = {"run_command", "send_command_input", "search_web", "read_url_content", "generate_image", "schedule",
                   "run_workflow", "define_subagent", "notebook_edit", "notebook_execution", "delete_knowledge",
                   "search_marketplace", "list_plugin_accounts", "manage_inbox", "ask_question", "ask_permission",
                   "ask_custom_permission", "call_mcp_tool"}

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def posix(p) -> str:
    """Ruta absoluta con letra de unidad y `/`. En Windows acepta también /c/... de Git Bash."""
    s = str(p)
    if os.name == "nt" and re.match(r"^/[a-zA-Z]/", s):
        s = s[1].upper() + ":" + s[2:]
    q = Path(s)
    if not q.is_absolute():
        q = BASE / q
    return q.resolve().as_posix()


def repositorios() -> list:
    f = BASE / ".claude" / "settings.json"
    try:
        dirs = (json.loads(f.read_text(encoding="utf-8")).get("permissions") or {}).get("additionalDirectories") or []
    except (OSError, json.JSONDecodeError) as e:
        sys.exit(f"STOP: no se pudo leer {f}: {e}")
    return [posix(d) for d in dirs]


def norm_ruta(s) -> str:
    """Ruta comparable: barras `/`, sin barra final, letra de unidad como en Windows y, ahí, sin mayúsculas."""
    s = str(s).strip().replace("\\", "/")
    if re.match(r"^/[a-zA-Z]/", s):
        s = s[1].upper() + ":" + s[2:]
    s = s.rstrip("/") or "/"
    return s.casefold() if os.name == "nt" else s


def es_de_confianza(ajustes) -> bool:
    lista = ajustes.get("trustedWorkspaces") if isinstance(ajustes, dict) else None
    if not isinstance(lista, list):
        return False
    rutas = [x.get("path") if isinstance(x, dict) else x for x in lista]
    return norm_ruta(BASE.resolve().as_posix()) in {norm_ruta(x) for x in rutas if isinstance(x, str)}


def escapar(s: str) -> str:
    """Escapa solo lo que tiene sentido en una regex; no toca espacios ni `/` (motores estrictos)."""
    return re.sub(r"([\\.^$|?*+()\[\]{}])", r"\\\1", s)


def marcadores() -> dict:
    m = {"WS": BASE.resolve().as_posix()}
    for i, r in enumerate(repositorios(), 1):
        m[f"REPO_{i}"] = r
    return m


ANTIGUOS = ("REPO", "JUEGO")      # marcadores del formato anterior de otros coordinadores


def traducir_antiguos(regla: str, m: dict, avisados: set) -> str:
    """{REPO} y {JUEGO} (formato anterior) se leen como {REPO_1} si hay un solo repositorio; con varios, STOP."""
    for a in ANTIGUOS:
        if "{" + a + "}" not in regla:
            continue
        repos = [k for k in m if k.startswith("REPO_")]
        if len(repos) != 1:
            sys.exit(f"STOP: la regla {regla!r} usa {{{a}}} (formato anterior) y hay {len(repos)} repositorios en "
                     ".claude/settings.json: no adivino cuál. Usa {REPO_1}, {REPO_2}… o regenera los permisos con "
                     "scripts/emitir_agy.py.")
        if a not in avisados:
            avisados.add(a)
            print(f"[aviso] los permisos usan {{{a}}} (formato anterior): se lee como {{REPO_1}} = {m['REPO_1']}. "
                  "Regenera los permisos con scripts/emitir_agy.py para quitar este aviso.")
        regla = regla.replace("{" + a + "}", "{REPO_1}")
    return regla


def validar_regex(bruta: str, resuelta: str, origen: str):
    """Una regex mal escrita en `command(regex:…)` hace que agy deniegue todos los comandos sin avisar [medido]
    y que el lanzador diera por buena una orden que no corrió. Antes de lanzar se comprueba que compile (la regla ya
    con los marcadores resueltos) y que no lleve una barra invertida doble delante de un especial (la bruta)."""
    pref = "command(regex:"
    if not resuelta.startswith(pref):
        return
    rx = resuelta[len(pref):-1] if resuelta.endswith(")") else resuelta[len(pref):]
    try:
        re.compile(rx)
    except re.error as e:
        sys.exit(f"STOP: {origen}: la regex {rx!r} no compila ({e}). Agy la trataría como «nada casa» y denegaría "
                 "todos los comandos sin avisar.")
    doble = re.search(r"\\\\[.()\[\]{}|?*+^$nsdwNSDW]", bruta)
    if doble:
        sys.exit(f"STOP: {origen}: la regex {bruta!r} lleva una barra invertida doble ({doble.group(0)!r}) delante de "
                 "un carácter especial: tras leer el JSON casa una barra literal y el comando nunca casaría. En el "
                 "JSON se escribe `\\\\.` para obtener la regex `\\.`.")


def sustituir(regla: str, m: dict, avisados: set | None = None) -> str:
    es_regex = regla.startswith("command(regex:")
    regla = traducir_antiguos(regla, m, avisados if avisados is not None else set())
    for k, v in m.items():
        regla = regla.replace("{" + k + "}", escapar(v) if es_regex else v)
    resto = re.findall(r"\{(WS|REPO_\d+)\}", regla)
    if resto:
        sys.exit(f"STOP: la regla {regla!r} usa {{{resto[0]}}}, que no existe (¿falta un repositorio en "
                 ".claude/settings.json?).")
    return regla


def config_del_rol(rol: str) -> dict:
    """El rol de `coordinador.json` (roles); si no está ahí es un rol ad hoc o un asistente, y su definición
    (`_rol`) la dejó `emitir_agy.py` en `.agents/permisos/<rol>.json`."""
    f = BASE / "coordinador.json"
    if not f.exists():
        print(f"[aviso] no hay {f.name}: no se comprueba el motor ni la carpeta del rol")
        return {}
    r = ((json.loads(f.read_text(encoding="utf-8")).get("roles") or {}).get(rol))
    if r:
        return r
    p = BASE / ".agents" / "permisos" / f"{rol}.json"
    try:
        return (json.loads(p.read_text(encoding="utf-8")).get("_rol")) or {}
    except (OSError, json.JSONDecodeError):
        return {}


def escrituras_extra(pedidas: list, m: dict) -> list:
    """Rutas de --escritura validadas: (ruta, raíz que la contiene, es_repositorio)."""
    ws = BASE.resolve()
    repos = [Path(v) for k, v in m.items() if k.startswith("REPO_")]
    salida = []
    for x in pedidas:
        q = Path(posix(x))
        raiz = ws if q.is_relative_to(ws) else next((r for r in repos if q.is_relative_to(r)), None)
        if raiz is None:
            sys.exit(f"STOP: --escritura {x!r} cae fuera del workspace y de los repositorios de trabajo.")
        partes = q.relative_to(raiz).parts
        if q == raiz or any(d in partes for d in CARPETAS_VEDADAS):
            sys.exit(f"STOP: --escritura {x!r}: ni la raíz entera ni nada bajo {', '.join(CARPETAS_VEDADAS)} "
                     "se autoriza a un rol.")
        salida.append((q.as_posix(), raiz, raiz != ws))
    return salida


def permisos_del_rol(rol: str, salida: Path, m: dict, extra: list | None = None) -> dict:
    f = BASE / ".agents" / "permisos" / f"{rol}.json"
    p = json.loads(f.read_text(encoding="utf-8"))
    for r in p.get("allow", []):
        if any(r.startswith(x) for x in PROHIBIDAS):
            sys.exit(f"STOP: {f.name} permite {r}; ningún rol escribe en .git, .agents ni .claude.")
    avisados: set = set()
    allow, deny = [], []
    for lista, destino in ((p.get("allow", []), allow), (p.get("deny", []), deny)):
        for r in lista:
            resuelta = sustituir(r, m, avisados)
            validar_regex(traducir_antiguos(r, m, avisados), resuelta, f.name)
            destino.append(resuelta)
    allow.append(f"write_file({salida.as_posix()})")
    for ruta, raiz, es_repo in extra or []:
        q = Path(ruta)
        if es_repo:
            # La negativa a escribir en el repositorio entero taparía el permiso (deny gana): se retira solo
            # esa; sin regla, agy no deja escribir en -p, así que solo quedan permitidas las rutas dadas.
            deny = [d for d in deny if d != f"write_file({raiz.as_posix()})"]
        else:
            for d in deny:
                if d.startswith("write_file(") and q.is_relative_to(Path(d[len("write_file("):-1])):
                    sys.exit(f"STOP: --escritura {ruta!r} cae en una carpeta que los permisos del rol protegen ({d}).")
        allow.append(f"write_file({ruta})")
    return {"allow": allow, "deny": deny}


def ejecutable_agy() -> list:
    ruta = os.environ.get("AGY")
    if not ruta:
        ruta = shutil.which("agy")
    if not ruta and os.environ.get("LOCALAPPDATA"):
        for nombre in ("agy.exe", "agy"):
            c = Path(os.environ["LOCALAPPDATA"]) / "agy" / "bin" / nombre
            if c.exists():
                ruta = str(c)
                break
    if not ruta or not Path(ruta).exists() and not shutil.which(ruta):
        sys.exit("STOP: no se encuentra agy (variable AGY, PATH o %LOCALAPPDATA%/agy/bin). "
                 "Ver MOTOR_EXTERNO.md §1.")
    return [sys.executable, "-I", ruta] if ruta.endswith(".py") else [ruta]


SALIDA_DE_COMANDO = re.compile(r"^\s*Command exited with code (-?\d+)", re.I)
RECHAZO = re.compile(r"permission check failed|user denied|auto-denied|permission denied", re.I)


def resumir(registro: Path):
    """Pasos del registro. Un comando cuenta como corrido (`DONE exit=N`) solo si el paso trae la salida de la
    herramienta («Command exited with code N»): un DONE sin ella, o con un rechazo de permiso, se lista como
    SIN_EVIDENCIA y el lanzamiento no se da por bueno (v1.3.2, hallazgo 3 del piloto)."""
    pasos, comandos, errores, resultado, cortes = 0, [], [], None, []
    for linea in registro.open(encoding="utf-8", errors="replace"):
        try:
            e = json.loads(linea)
        except json.JSONDecodeError:
            if "auto-denied" in linea:
                cortes.append(linea.strip()[:200])
            continue
        if not isinstance(e, dict):
            continue
        s = e.get("step_update") or {}
        if s.get("step_type") == "tool" and s.get("state") in ("DONE", "ERROR"):
            pasos += 1
            ti = s.get("tool_info") or {}
            if ti.get("name") == "run_command":
                orden = (ti.get("parameters") or {}).get("CommandLine", "")[:160]
                salida = str(ti.get("output") or s.get("output") or "")
                m_salida = SALIDA_DE_COMANDO.match(salida)
                if s["state"] == "DONE" and m_salida and not RECHAZO.search(salida[:400]):
                    comandos.append(f"DONE exit={m_salida.group(1)} {orden}")
                elif s["state"] == "DONE":
                    comandos.append(f"SIN_EVIDENCIA {orden}")
                else:
                    comandos.append(f"{s['state']} {orden}")
            if s["state"] == "ERROR":
                errores.append(f"{ti.get('name')}: {((ti.get('error') or {}).get('message') or '')[:160]}")
        if e.get("event") == "result":
            resultado = e.get("result") or {}
    return pasos, comandos, errores, resultado, cortes


def fuera_de_alcance(registro: Path) -> list:
    """Asistente navegador: herramientas fuera de su alcance y subagentes que no son `browser`, en el orden en que se
    pidieron (también las que agy rechazó: pedirlas ya es salirse del encargo)."""
    fuera = []
    for linea in registro.open(encoding="utf-8", errors="replace"):
        try:
            e = json.loads(linea)
        except json.JSONDecodeError:
            continue
        s = (e.get("step_update") or {}) if isinstance(e, dict) else {}
        if s.get("state") not in ("DONE", "ERROR"):
            continue
        nombre = s.get("tool_name") or ""
        if nombre in FUERA_NAVEGADOR:
            fuera.append(nombre)
        elif nombre == "invoke_subagent":
            for sub in (s.get("subagent_info") or {}).get("subagents") or [
                    (s.get("tool_info") or {}).get("parameters") or {}]:
                tipo = sub.get("type_name") or sub.get("TypeName")
                if tipo and tipo != "browser":
                    fuera.append(f"invoke_subagent({tipo})")
    return fuera


def navegador_listo() -> str | None:
    """None si el Chrome del kit está abierto (puerto y DevToolsActivePort); si no, el motivo."""
    try:
        cfg = json.loads((BASE / "coordinador.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        cfg = {}
    nav = ((cfg.get("supervision") or {}).get("asistentes") or {}).get("navegador") or {}
    puerto = int(nav.get("puerto") or 9222)
    try:
        import urllib.request
        with urllib.request.urlopen(f"http://127.0.0.1:{puerto}/json/version", timeout=3) as r:
            r.read()
    except OSError:
        return f"el puerto {puerto} no responde"
    if os.name == "nt":
        dtap = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local") / "Google" / "Chrome" / "User Data"
    elif sys.platform == "darwin":
        dtap = Path.home() / "Library" / "Application Support" / "Google" / "Chrome"
    else:
        dtap = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config") / "google-chrome"
    if not (dtap / "DevToolsActivePort").exists():
        return f"no existe {dtap / 'DevToolsActivePort'} (sin él el subagente no se conecta)"
    return None


def cambios_externos(escrito: bytes, sello: str):
    """Si settings.json ya no es lo que escribió el lanzador (agy u otra sesión lo tocó durante la corrida), guarda
    esa versión en settings.json.durante_<sello> y devuelve (ruta, claves cambiadas); si no cambió, None."""
    try:
        actual = AJUSTES.read_bytes()
    except OSError:
        return (f"(el archivo ya no existía)", ["(archivo borrado)"])
    if actual == escrito:
        return None
    try:
        # agy reescribe el JSON escapando & | < > (\u0026…): la misma información con otros bytes no es un cambio
        if json.loads(actual.decode("utf-8")) == json.loads(escrito.decode("utf-8")):
            return None
    except (UnicodeDecodeError, json.JSONDecodeError):
        pass
    guardado = AJUSTES.with_name(f"{AJUSTES.name}.durante_{sello}")
    n = 1
    while guardado.exists():
        n += 1
        guardado = AJUSTES.with_name(f"{AJUSTES.name}.durante_{sello}_{n}")
    guardado.write_bytes(actual)
    try:
        antes, ahora = json.loads(escrito.decode("utf-8")), json.loads(actual.decode("utf-8"))
        claves = sorted(k for k in set(antes) | set(ahora) if antes.get(k, FALTA) != ahora.get(k, FALTA))
    except (UnicodeDecodeError, json.JSONDecodeError, AttributeError):
        claves = ["(ya no es JSON válido)"]
    return (guardado.name, claves or ["(contenido distinto)"])


def restaurar() -> int:
    if RESPALDO.exists():
        shutil.copyfile(RESPALDO, AJUSTES)
        RESPALDO.unlink()
        print(f"settings.json restaurado desde {RESPALDO.name}")
    else:
        print("no había respaldo pendiente")
    if CANDADO.exists():
        CANDADO.unlink()
        print(f"candado retirado: {CANDADO}")
    return 0


def main() -> int:
    a = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    a.add_argument("rol", nargs="?")
    a.add_argument("encargo", nargs="?")
    a.add_argument("--salida")
    a.add_argument("--modelo")
    a.add_argument("--tope", type=int, default=30)
    a.add_argument("--registro")
    a.add_argument("--conversacion")
    a.add_argument("--nota")
    a.add_argument("--escritura", action="append", default=[])
    a.add_argument("--plan", help="plan de actividades (solo asistentes): hace falta para usar un modelo Argon")
    a.add_argument("--restaurar", action="store_true")
    o = a.parse_args()
    if o.restaurar:
        return restaurar()
    if not (o.rol and o.encargo and o.salida):
        a.error("hacen falta <rol>, <encargo> y --salida")

    # 1. Comprobaciones, todas antes de tocar nada.
    if o.rol == "coordinador":
        sys.exit("STOP: el coordinador no corre nunca en agy (guardrail supervision_claude).")
    if o.nota and not o.conversacion:
        sys.exit("STOP: --nota solo vale con --conversacion (es el mensaje con el que se sigue).")
    nota = None
    if o.nota:
        cand = Path(o.nota)
        try:
            archivo = cand if cand.is_file() else (BASE / cand if (BASE / cand).is_file() else None)
        except OSError:                       # un texto largo no es una ruta
            archivo = None
        nota = (archivo.read_text(encoding="utf-8") if archivo else o.nota).strip()
        if not nota or len(nota) > TOPE_NOTA:
            sys.exit(f"STOP: la nota está vacía o pasa de {TOPE_NOTA} caracteres: una nota es corta.")
    cfg = config_del_rol(o.rol)
    if cfg and cfg.get("motor", "claude") != "agy":
        sys.exit(f"STOP: el rol {o.rol!r} declara motor {cfg.get('motor', 'claude')!r} en coordinador.json.")
    modelo = o.modelo or cfg.get("modelo_agy")
    if not modelo:
        sys.exit("STOP: falta el modelo (--modelo o modelo_agy del rol).")
    if cfg.get("asistente"):
        # Modo «asistentes» (v1.3.2): Flash por defecto; Argon solo si el plan lo justifica por escrito; nunca la bolsa
        # «Claude and GPT» de agy para trabajo de rutina.
        if not modelo.lower().startswith("gemini-"):
            sys.exit(f"STOP: el asistente {o.rol!r} no corre en {modelo!r}: los asistentes usan modelos Gemini "
                     "(la bolsa «Claude and GPT» de agy no se gasta en trabajo de rutina).")
        if "argon" in modelo.lower():
            plan = Path(o.plan) if o.plan else None
            plan = (plan if plan.is_absolute() else BASE / plan) if plan else None
            if not plan or not plan.is_file() or not re.search(r"^\W*Justificaci[oó]n Argon\W*:\s*.{15,}", plan.read_text(
                    encoding="utf-8", errors="replace"), re.M | re.I):
                sys.exit(f"STOP: el modelo {modelo!r} es de la bolsa chica (Argon): un asistente solo lo usa si el plan "
                         "de actividades lo justifica por escrito. Pasa --plan <plan.md> con una línea "
                         "«Justificación Argon: <por qué>».")
    for f in (BASE / ".agents" / "agents" / f"{o.rol}.md", BASE / ".agents" / "permisos" / f"{o.rol}.json"):
        if not f.exists():
            sys.exit(f"STOP: falta {f.relative_to(BASE).as_posix()}; se genera con scripts/emitir_agy.py {o.rol}.")
    navegador = bool(cfg.get("navegador"))
    if navegador:
        motivo = navegador_listo()
        if motivo:
            sys.exit(f"STOP: el asistente navegador necesita el Chrome del kit abierto ({motivo}). Ábrelo con "
                     f"{PY} -I scripts/abrir_navegador.py abrir, y ciérralo al terminar con "
                     f"{PY} -I scripts/abrir_navegador.py cerrar.")
    salida = (BASE / o.salida).resolve()
    rel = salida.relative_to(BASE.resolve()).as_posix() if salida.is_relative_to(BASE.resolve()) else None
    if rel is None or rel == "." or rel.split("/")[0] in (".git", ".agents", ".claude"):
        sys.exit(f"STOP: la salida {o.salida!r} tiene que ser una carpeta del workspace fuera de .git, .agents y .claude.")
    propia = (cfg.get("escribe_en") or "").strip("/")
    if propia and not propia.startswith("(") and not (rel + "/").startswith(propia + "/"):
        sys.exit(f"STOP: la salida {rel!r} no está dentro de {propia!r}, la carpeta del rol.")
    encargo = Path(o.encargo) if Path(o.encargo).is_absolute() else BASE / o.encargo
    encargo = encargo.resolve()
    if not encargo.is_file():
        sys.exit(f"STOP: el encargo no existe: {encargo}")
    if not encargo.is_relative_to(BASE.resolve()):
        sys.exit("STOP: el encargo tiene que estar dentro del workspace: agy no lee fuera sin permiso.")
    if not AJUSTES.exists():
        sys.exit(f"STOP: no existe {AJUSTES}. Autentícate una vez en interactivo (MOTOR_EXTERNO.md §1).")
    try:
        confiable = es_de_confianza(json.loads(AJUSTES.read_text(encoding="utf-8")))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        confiable = None        # un settings.json inválido se rechaza más abajo, con su propio STOP
    if confiable is False:
        sys.exit(f"STOP: el workspace {BASE.resolve().as_posix()} no es de confianza para agy (no está en "
                 f"\"trustedWorkspaces\" de {AJUSTES}). Sin eso agy no carga los roles y responde «unknown agent». "
                 "Dale confianza tú: abre `agy` en modo interactivo dentro de esa carpeta y acepta. "
                 "El lanzador nunca la añade por su cuenta: es una decisión tuya.")
    orden_agy = ejecutable_agy()
    m = marcadores()
    extra = escrituras_extra(o.escritura, m)
    permisos = permisos_del_rol(o.rol, salida, m, extra)

    # El candado se crea de forma atómica (O_EXCL) justo antes de tocar nada: de dos lanzamientos casi
    # simultáneos entra uno y el otro recibe FileExistsError, que es el STOP de siempre. Hasta tenerlo no se
    # restaura ni se respalda nada: un respaldo ajeno puede ser el de otro lanzamiento en curso.
    sello = time.strftime("%Y%m%d-%H%M%S")
    try:
        fd = os.open(CANDADO, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        sys.exit(f"STOP: hay otro lanzamiento en curso o uno que no terminó ({CANDADO}). Si no hay ninguno "
                 f"corriendo: {PY} -I scripts/lanzar_agy.py --restaurar")
    with os.fdopen(fd, "w", encoding="utf-8") as c:
        c.write(sello)
    try:
        if RESPALDO.exists():  # un lanzamiento anterior se cortó sin restaurar
            print(f"[aviso] había un respaldo sin restaurar ({RESPALDO.name}): se restaura antes de seguir")
            shutil.copyfile(RESPALDO, AJUSTES)
            RESPALDO.unlink()
        original = AJUSTES.read_bytes()
        try:
            ajustes = json.loads(original.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            sys.exit(f"STOP: {AJUSTES} no es JSON válido ({e}); no se toca.")
        salida.mkdir(parents=True, exist_ok=True)
        dir_reg = Path(o.registro).resolve() if o.registro else salida
        dir_reg.mkdir(parents=True, exist_ok=True)
        registro, n = dir_reg / f"agy_{o.rol}_{sello}.ndjson", 1
        while registro.exists():            # dos lanzamientos en el mismo segundo no se pisan el registro
            n += 1
            registro = dir_reg / f"agy_{o.rol}_{sello}_{n}.ndjson"
        if o.conversacion and nota:
            mensaje = nota
        elif o.conversacion:
            mensaje = ("Tu ejecución anterior se cortó porque pediste una acción no permitida. Sigue tu "
                       "encargo desde donde ibas, sin repetir lo ya hecho, y usa solo lo que permite tu "
                       "definición de rol.")
        else:
            mensaje = (f"Eres un agente arrancado en frío. Tu arranque completo está en {encargo.as_posix()}. "
                       f"Léelo íntegro y cúmplelo, incluida la ADENDA final. Tu carpeta de salida es "
                       f"{salida.as_posix()}.")
            if navegador:
                # Sin --agent, agy no carga la definición del rol: va delante del mensaje, sin el frontmatter.
                definicion = (BASE / ".agents" / "agents" / f"{o.rol}.md").read_text(encoding="utf-8")
                definicion = re.sub(r"\A---\n.*?\n---\n", "", definicion, count=1, flags=re.S).strip()
                mensaje = f"{definicion}\n\n---\n\n{mensaje}"
    except BaseException:
        CANDADO.unlink(missing_ok=True)
        raise

    # 2. Permisos del rol solo mientras corre; restauración pase lo que pase.
    salida_agy, segundos = "-", 0.0
    escrito, externo = None, None       # lo que escribió el lanzador; y, si cambió durante la corrida, (archivo, claves)
    try:
        shutil.copyfile(AJUSTES, RESPALDO)
        ajustes["permissions"] = permisos
        texto = json.dumps(ajustes, ensure_ascii=False, indent=2)   # nunca a mano: un JSON inválido deniega todo
        json.loads(texto)
        escrito = texto.encode("utf-8")
        AJUSTES.write_bytes(escrito)
        orden = orden_agy + ["-p", mensaje] + ([] if navegador else ["--agent", o.rol]) + [
            "--model", modelo, "--output-format", "stream-json", "--print-timeout", f"{o.tope}m"]
        for r in m:
            if r.startswith("REPO_"):
                orden += ["--add-dir", m[r]]
        if o.conversacion:
            orden += ["--conversation", o.conversacion]
        inicio = time.time()
        with registro.open("w", encoding="utf-8") as f:
            try:
                r = subprocess.run(orden, cwd=BASE, stdout=f, stderr=subprocess.STDOUT,
                                   timeout=o.tope * 60 + 120)
                salida_agy = r.returncode
            except subprocess.TimeoutExpired:
                salida_agy = "TIMEOUT"
        segundos = time.time() - inicio
    finally:
        if escrito is not None:
            externo = cambios_externos(escrito, sello)
        if RESPALDO.exists():
            shutil.copyfile(RESPALDO, AJUSTES)
            RESPALDO.unlink()
        CANDADO.unlink(missing_ok=True)

    # 3. Resumen.
    pasos, comandos, errores, res, cortes = resumir(registro)
    estado = (res.get("status") or "?") if res is not None else "SIN_RESULTADO"
    denegadas = (res or {}).get("denied_actions") or []
    cortada = bool(cortes or denegadas)
    sin_evidencia = [c for c in comandos if c.startswith("SIN_EVIDENCIA")]
    fuera = fuera_de_alcance(registro) if navegador else []
    cuota = False
    if res is None or str(res.get("status", "")).upper() == "ERROR":
        crudo = [l for l in registro.read_text(encoding="utf-8", errors="replace").splitlines()
                 if not l.lstrip().startswith("{")]
        texto_error = " ".join(crudo + errores + [json.dumps((res or {}).get("error"), ensure_ascii=False)])
        cuota = bool(CUOTA.search(texto_error))
    igual = AJUSTES.read_bytes() == original
    # El exit que cuenta es el del LANZADOR (el de agy solo dice que el proceso terminó): se calcula antes del
    # resumen para imprimirlo en la primera línea [hallazgo 2 de las pruebas de la v1.3.2].
    if not igual:
        salida_lanzador = 1
    elif cuota:
        salida_lanzador = 4
    else:
        salida_lanzador = 3 if (cortada or sin_evidencia or fuera or res is None or salida_agy == "TIMEOUT") else 0
    if cortada or sin_evidencia or fuera or salida_agy == "TIMEOUT":
        # «SUCCESS» de agy junto a un corte no es un éxito: no se imprime con ese aspecto.
        estado = f"NO VALE (agy dijo {estado})"
    if cortada:
        estado += " · CORTADA (permiso denegado)"
    if sin_evidencia:
        estado += f" · SIN_EVIDENCIA ({len(sin_evidencia)} comando(s) sin la salida de la herramienta)"
    if fuera:
        estado += f" · FUERA_DE_ALCANCE ({', '.join(dict.fromkeys(fuera))})"
    if salida_agy == "TIMEOUT":
        estado += " · TIMEOUT"
    print(f"rol={o.rol} modelo={modelo} EXIT_DEL_LANZADOR={salida_lanzador} (0 = valido; el exit de agy = {salida_agy} "
          f"no cuenta) estado={estado} segundos={segundos:.0f}")
    print(f"conversacion={(res or {}).get('conversation_id', '-')} registro={registro}")
    print("escritura extra: " + (", ".join(e[0] for e in extra) if extra else "ninguna"))
    print("marcadores: " + " ".join(f"{{{k}}}={v}" for k, v in m.items()))
    print(f"herramientas={pasos} comandos={len(comandos)}")
    for c in comandos:
        print(f"  {c}")
    for e in errores:
        print(f"  ERROR {e}")
    for d in denegadas + cortes:
        d = d if isinstance(d, str) else json.dumps(d, ensure_ascii=False)
        print(f"  DENEGADA {d[:200]}")
    if res is not None:
        u = res.get("usage") or {}
        g = {k: u.get(k, 0) or 0 for k in ("input_tokens", "cache_read_tokens", "output_tokens",
                                            "thinking_tokens", "total_tokens")}
        print("consumo: entrada={input_tokens:,} cache_leida={cache_read_tokens:,} salida={output_tokens:,} "
              "razonamiento={thinking_tokens:,} total={total_tokens:,}".format(**g))
        # Mismas columnas que medir_consumo.py (MOTOR_EXTERNO.md §5). «llamadas» son aquí las
        # herramientas: agy no informa las llamadas al modelo, y el contexto final tampoco.
        print(f"{'agente':<22}{'modelo':<20}{'llamadas':>9}{'entrada nueva':>15}{'relectura':>13}{'salida':>10}{'contexto final':>16}")
        print(f"{('agy:' + o.rol)[:21]:<22}{modelo[:19]:<20}{pasos:>9}{g['input_tokens']:>15,}"
              f"{g['cache_read_tokens']:>13,}{g['output_tokens']:>10,}{'-':>16}")
        print("respuesta:")
        print((res.get("response") or "")[:3000])
    if cuota:
        print("CUOTA: el motor externo agotó la cuota o limitó el ritmo (quota, RESOURCE_EXHAUSTED, 429 o rate limit).")
        print("  Qué hacer: (1) mira /usage en una sesión interactiva de agy; (2) espera la renovación de la "
              "ventana de 5 h; (3) o baja a un modelo flash con --modelo.")
        print("  NO se activan créditos de pago: es un gasto que decide el usuario, no el coordinador.")
        if (res or {}).get("conversation_id"):
            print(f"  Para seguir después: --conversacion {res['conversation_id']} --nota <mensaje corto>")
    if externo:
        print(f"WARN: settings.json cambió durante la corrida (claves: {', '.join(externo[1])}). Esa versión quedó en "
              f"{externo[0]}; el archivo se restauró al original, sin esos cambios. Revísala e incorpora a mano lo "
              "que sea tuyo (un token, trustedWorkspaces, preferencias).")
    print(f"settings.json restaurado: {igual}" + (f" (con cambios externos guardados en {externo[0]})" if externo else ""))
    if not igual:
        print(f"STOP: settings.json no quedó como estaba; compáralo con {RESPALDO.name} si existe.")
        return 1
    return salida_lanzador


if __name__ == "__main__":
    raise SystemExit(main())
