"""Herramienta segura de un rol en el motor externo (esqueleto del kit coordinador, v1.3.3).

REGLA: al rol se le da una HERRAMIENTA, no una consola. Un rol en agy que necesita ejecutar algo del
proyecto (pruebas, mediciones, copias) lo hace por este script, y es lo único que ese comando de
`comandos_agy` le permite correr. Así la seguridad va DENTRO del script y no depende de que el
rol obedezca, y el rol hace menos turnos: una llamada = varias acciones.

Copie este archivo a `scripts/` del coordinador destino, rellene la sección CONFIGURACIÓN (marcada
con «RELLENAR») y añada a `comandos_agy` del rol una regla anclada, por ejemplo:
    {"regex": "^python3? -I scripts/herramienta_segura\\.py (copiar|clonar|correr|diff) [A-Za-z0-9_./ -]*$",
     "forma": "python -I scripts/herramienta_segura.py <copiar|clonar|correr|diff> <argumentos>"}

Qué da el esqueleto:
- Subcomandos fijos (`copiar`, `clonar`, `correr`, `diff`, y desde la v1.3.2 `sello`, `sello-repo`, `mutar` y
  `poner`); nada fuera de ellos corre.
- Nombres validados con [A-Za-z0-9_-]: no hay rutas ni opciones en un nombre.
- Todas las rutas encerradas en CARPETA; lo que se sale, se rechaza.
- Un tope de tiempo en cada proceso que se lanza (y escribe TIMEOUT si se cumple).
- Una línea de resultado por acción, corta, para que el rol lea poco y el coordinador lea menos.
- Una comprobación «antes y después» (`huella` / `vigilar`) de lo que NO debe cambiar —los datos
  reales del usuario, el repositorio de trabajo—, que el proyecto rellena. Si cambia, STOP.

Desde la v1.3.2 (hallazgo 4 del piloto VM1): el Verificador no necesita escribir fuera de su carpeta para inyectar
mutantes ni calcular sellos. `mutar` cambia un texto exacto DENTRO de una copia (la copia se tira, el repositorio no
se toca); `sello` da el sha256 y los finales de línea de un archivo de una copia; `sello-repo` da el `git ls-files
--eol` y el sha256 de un archivo del repositorio de trabajo (solo lectura); `poner` copia a una copia un archivo
que el asistente escribió en su carpeta de salida (la única vía por la que el código de un prototipo entra a la copia).

Uso:
    python -I scripts/herramienta_segura.py copiar <commit> <nombre>
    python -I scripts/herramienta_segura.py clonar <origen> <nombre>
    python -I scripts/herramienta_segura.py correr <copia> <prueba> [<prueba> ...] [--tope 240]
    python -I scripts/herramienta_segura.py diff <copia_a> <copia_b> <ruta>
    python -I scripts/herramienta_segura.py sello <copia> <ruta>
    python -I scripts/herramienta_segura.py sello-repo <ruta>
    python -I scripts/herramienta_segura.py mutar <copia> <ruta> <desde> <hasta>
    python -I scripts/herramienta_segura.py poner <copia> <ruta> <fuente>
    <ruta> es relativa a la copia (en `sello-repo`, al repositorio). <fuente> es relativa al workspace y tiene que
    estar en CARPETA_FUENTES. Las salidas completas quedan en CARPETA/salidas/.
Salida: exit 0 si la acción se hizo; 2 si se rechazó una entrada; 3 si cambió lo vigilado (STOP).

AISLAR LOS DATOS DEL USUARIO (v1.3.3, hallazgo 3 de las pruebas de la v1.3.2). Una copia que se corre tiene que
escribir en SU lugar, nunca en el del usuario real. Cada motor guarda sus datos en un sitio que sale de algo del
proyecto, así que `preparar_copia()` cambia ese algo en la copia (`copiar` y `clonar` la llaman; `mutar` y `poner`
se niegan a tocar el archivo donde está):
- Godot (se detecta por `project.godot`): los datos van a user:// = `%APPDATA%/Godot/app_userdata/<config/name>`.
  La copia recibe otro `config/name` y se importa (`--import`) ANTES de correr nada, o la primera corrida
  importaría y escribiría. Rellene `COMANDO_IMPORTAR` con `{godot}` y fije la variable de entorno GODOT, o
  `huella()` verá la carpeta real de datos cuando ya sea tarde.
- Otros motores, qué mirar: Unity (`productName`/`companyName` en ProjectSettings → `persistentDataPath`), Unreal
  (`ProjectName`/carpeta `Saved`), Python/Node/Java (variables de entorno HOME, XDG_*, APPDATA, o la ruta de la
  base de datos o del `.env`: pásalas a una carpeta de la copia en `ENTORNO_COPIA`), una base de datos real
  (otra URL en la copia). Regla: busque dónde escribe la aplicación fuera de su carpeta, cámbielo en la copia, y
  ponga en `huella()` lo que quedó fuera para que cualquier fuga sea STOP.
"""
import difflib
import hashlib
import io
import os
import re
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ---------------------------------------------------------------- CONFIGURACIÓN (RELLENAR)
# Repositorio de trabajo del que se sacan las copias (solo se LEE: `git archive`).
REPO = None                      # RELLENAR: ruta absoluta con `/`, p. ej. "C:/proyectos/mi_repo"
# Carpeta donde viven las copias y las salidas. Dentro del workspace del coordinador, para que el rol
# pueda leer las salidas; la crea la herramienta. Nada se escribe fuera de ella.
CARPETA = (Path(__file__).resolve().parents[1] / "trabajo_herramienta").resolve()
# De dónde puede salir un archivo para `poner`: la carpeta de salida de los asistentes (nada más).
CARPETA_FUENTES = (Path(__file__).resolve().parents[1] / "asistentes").resolve()
# Subcarpeta del repositorio que se copia (None = todo el repositorio).
SUBCARPETA = None                # RELLENAR si el proyecto vive en una subcarpeta
# Comando de una prueba, con {copia} (ruta de la copia) y {prueba} (nombre validado). Una lista, sin shell.
COMANDO_PRUEBA = None            # RELLENAR: p. ej. ["python", "-I", "{copia}/tests/{prueba}.py"]
# Dónde está cada prueba dentro de la copia, para comprobar que existe antes de correrla.
ARCHIVO_PRUEBA = "tests/{prueba}"            # RELLENAR si cambia la convención (se le añade la extensión)
EXTENSION_PRUEBA = ".py"                     # RELLENAR
# Patrón que marca la primera línea relevante de la salida de una prueba (si no aparece, «pasa»).
BUSCA = re.compile(r"ERROR|FAIL|FALLO|Traceback")
# Importación previa de la copia (el motor genera su caché una vez, antes de las pruebas). None = no hace falta.
# Godot: ["{godot}", "--headless", "--path", "{copia}", "--import"]  (y {godot} también en COMANDO_PRUEBA).
COMANDO_IMPORTAR = None          # RELLENAR si el motor lo necesita
# Variables de entorno que se fijan en cada proceso que corre en la copia: {copia} es su ruta. Para motores que
# guardan datos según HOME, APPDATA, etc., p. ej. {"APPDATA": "{copia}/_datos"}.
ENTORNO_COPIA = {}
TOPE_MAXIMO = 600                # segundos: ningún --tope pasa de esto
TOPE_POR_DEFECTO = 240

NOMBRE = re.compile(r"^[A-Za-z0-9_-]+$")
COMMIT = re.compile(r"^[A-Za-z0-9_./-]+$")


def huella():
    """«Antes y después»: una huella de lo que esta herramienta NO debe cambiar. RELLENAR.

    Devuelve un valor comparable con `==`. Ejemplo para una carpeta de datos del usuario: el número
    de archivos y la fecha del más reciente. Mientras no se rellene, la herramienta se niega a
    correr: una herramienta sin esta vigilancia no es segura."""
    raise NotImplementedError


def godot_exe():
    """El ejecutable de Godot: variable de entorno GODOT (en Windows, también la del usuario)."""
    g = os.environ.get("GODOT", "")
    if not g and os.name == "nt":
        try:
            g = subprocess.run(["powershell.exe", "-NoProfile", "-Command",
                                "[Environment]::GetEnvironmentVariable('GODOT','User')"],
                               capture_output=True, text=True, timeout=30).stdout.strip()
        except (OSError, subprocess.TimeoutExpired):
            g = ""
    if not g or not Path(g).is_file():
        salir("GODOT NO ENCONTRADO: fije la variable de entorno GODOT con la ruta del ejecutable", 2)
    return g


def sustituir_orden(plantilla, copia_ruta, prueba=""):
    godot = godot_exe() if any("{godot}" in x for x in plantilla) else ""
    return [x.format(copia=copia_ruta, prueba=prueba, godot=godot) for x in plantilla]


def entorno_copia(copia_ruta):
    env = dict(os.environ)
    for k, v in ENTORNO_COPIA.items():
        env[k] = v.format(copia=copia_ruta)
    return env


def preparar_copia(dest: Path, nombre: str):
    """Aísla la copia de los datos reales del usuario. Godot: otro config/name + importación previa."""
    pg = dest / "project.godot"
    if pg.is_file():
        t = pg.read_text(encoding="utf-8")
        nuevo, n = re.subn(r'(?m)^config/name="([^"]*)"', lambda m: f'config/name="{m.group(1)} AUX-{nombre}"', t, count=1)
        if n != 1:
            shutil.rmtree(dest, ignore_errors=True)
            salir("STOP: no se pudo cambiar config/name en project.godot; copia descartada", 3)
        pg.write_text(nuevo, encoding="utf-8", newline="")
        print(f"aislada: config/name cambiado en {nombre}")
        if not COMANDO_IMPORTAR:
            shutil.rmtree(dest, ignore_errors=True)
            salir("STOP: proyecto Godot sin COMANDO_IMPORTAR: la primera corrida importaría y escribiría; copia descartada", 3)
    if COMANDO_IMPORTAR:
        antes = huella()
        try:
            r = subprocess.run(sustituir_orden(COMANDO_IMPORTAR, dest.as_posix()), capture_output=True,
                               timeout=TOPE_MAXIMO, cwd=dest, env=entorno_copia(dest.as_posix()))
            print(f"importación exit={r.returncode}")
        except subprocess.TimeoutExpired:
            print("importación TIMEOUT")
        vigilar(antes)


def salir(msg, codigo=2):
    print(msg)
    sys.exit(codigo)


def nombre_ok(n):
    if not NOMBRE.match(n):
        salir(f"NOMBRE NO VALIDO: {n!r} (solo A-Z a-z 0-9 _ -)")
    return n


def en_carpeta(p: Path) -> Path:
    p = p.resolve()
    if CARPETA != p and CARPETA not in p.parents:
        salir(f"RUTA FUERA DE LA CARPETA: {p}")
    return p


def copia(n: str) -> Path:
    p = en_carpeta(CARPETA / nombre_ok(n))
    if not p.is_dir():
        salir(f"NO EXISTE LA COPIA: {n}")
    return p


def comprobar_configuracion():
    faltan = [k for k, v in (("REPO", REPO), ("COMANDO_PRUEBA", COMANDO_PRUEBA)) if not v]
    if faltan:
        salir("SIN CONFIGURAR: falta " + ", ".join(faltan) + " en la herramienta (ver CONFIGURACIÓN)", 2)
    try:
        huella()
    except NotImplementedError:
        salir("SIN CONFIGURAR: falta rellenar huella() (lo que no debe cambiar)", 2)


def vigilar(antes):
    ahora = huella()
    if ahora != antes:
        salir(f"STOP: cambió lo vigilado: antes={antes} ahora={ahora}", 3)


def cmd_copiar(a):
    if len(a) != 2:
        salir("uso: copiar <commit> <nombre>")
    commit, n = a
    if not COMMIT.match(commit) or commit.startswith("-"):
        salir(f"COMMIT NO VALIDO: {commit!r}")
    dest = en_carpeta(CARPETA / nombre_ok(n))
    if dest.exists():
        salir(f"YA EXISTE: {n}")
    dest.mkdir(parents=True)
    orden = ["git", "-C", REPO, "archive", "--format=tar", commit] + ([SUBCARPETA] if SUBCARPETA else [])
    try:
        p = subprocess.run(orden, capture_output=True, timeout=TOPE_POR_DEFECTO)
    except subprocess.TimeoutExpired:
        shutil.rmtree(dest, ignore_errors=True)
        salir("TIMEOUT: git archive pasó del tope", 2)
    if p.returncode != 0:
        shutil.rmtree(dest, ignore_errors=True)
        salir("git archive falló: " + p.stderr.decode(errors="replace")[:200])
    with tarfile.open(fileobj=io.BytesIO(p.stdout)) as tf:
        for m in tf.getmembers():
            partes = Path(m.name).parts
            if SUBCARPETA:
                if len(partes) < 2 or partes[0] != SUBCARPETA:
                    continue
                partes = partes[1:]
            if ".." in partes or not partes:
                continue
            objetivo = en_carpeta(dest / Path(*partes))
            if m.isdir():
                objetivo.mkdir(parents=True, exist_ok=True)
            elif m.isfile():
                objetivo.parent.mkdir(parents=True, exist_ok=True)
                objetivo.write_bytes(tf.extractfile(m).read())
    preparar_copia(dest, n)
    print(f"copia {n} lista en {dest.as_posix()} (commit {commit})")


def cmd_clonar(a):
    if len(a) != 2:
        salir("uso: clonar <origen> <nombre>")
    o, n = a
    src = copia(o)
    dest = en_carpeta(CARPETA / nombre_ok(n))
    if dest.exists():
        salir(f"YA EXISTE: {n}")
    shutil.copytree(src, dest)
    preparar_copia(dest, n)
    print(f"copia {n} clonada de {o} en {dest.as_posix()}")


def cmd_correr(a):
    tope = TOPE_POR_DEFECTO
    if "--tope" in a:
        i = a.index("--tope")
        try:
            tope = min(int(a[i + 1]), TOPE_MAXIMO)
        except (IndexError, ValueError):
            salir("--tope necesita un entero")
        a = a[:i] + a[i + 2:]
    if len(a) < 2:
        salir("uso: correr <copia> <prueba> [<prueba> ...] [--tope 240]")
    c = copia(a[0])
    (CARPETA / "salidas").mkdir(parents=True, exist_ok=True)
    for t in a[1:]:
        nombre_ok(t)
        if not (c / (ARCHIVO_PRUEBA.format(prueba=t) + EXTENSION_PRUEBA)).is_file():
            print(f"{a[0]} {t}: NO EXISTE")
            continue
        antes = huella()
        orden = sustituir_orden(COMANDO_PRUEBA, c.as_posix(), t)
        try:
            r = subprocess.run(orden, capture_output=True, timeout=tope, cwd=c, env=entorno_copia(c.as_posix()))
            texto = (r.stdout + r.stderr).decode("utf-8", errors="replace")
            estado = str(r.returncode)
        except subprocess.TimeoutExpired as e:
            texto = ((e.stdout or b"") + (e.stderr or b"")).decode("utf-8", errors="replace")
            estado = "TIMEOUT"
        (CARPETA / "salidas" / f"{a[0]}_{t}.txt").write_text(texto, encoding="utf-8")
        vigilar(antes)
        linea = next((l.strip() for l in texto.splitlines() if BUSCA.search(l)), "pasa")
        print(f"{a[0]} {t}: exit={estado} | {linea[:300]}")      # UNA línea por acción


def cmd_diff(a):
    if len(a) != 3:
        salir("uso: diff <copia_a> <copia_b> <ruta>")
    ca, cb = copia(a[0]), copia(a[1])
    ra = a[2].replace("\\", "/")
    if ra.startswith("/") or ".." in ra.split("/") or ":" in ra:
        salir(f"RUTA NO VALIDA: {ra}")
    fa, fb = en_carpeta(ca / ra), en_carpeta(cb / ra)
    la = fa.read_text(encoding="utf-8").splitlines(keepends=True) if fa.is_file() else []
    lb = fb.read_text(encoding="utf-8").splitlines(keepends=True) if fb.is_file() else []
    d = "".join(difflib.unified_diff(la, lb, f"{a[0]}/{ra}", f"{a[1]}/{ra}"))
    (CARPETA / "salidas").mkdir(parents=True, exist_ok=True)
    (CARPETA / "salidas" / f"{a[0]}_{a[1]}_{ra.replace('/', '_')}.diff").write_text(d, encoding="utf-8")
    print(d if d else "(sin diferencias)")


def ruta_en(base: Path, ruta: str) -> Path:
    r = ruta.replace("\\", "/")
    if r.startswith("/") or ".." in r.split("/") or ":" in r or not r:
        salir(f"RUTA NO VALIDA: {ruta}")
    return en_carpeta(base / r) if base == CARPETA or CARPETA in base.parents else (base / r).resolve()


def _sello(b: bytes) -> str:
    crlf = b.count(bytes([13, 10]))
    lf_solo = b.count(bytes([10])) - crlf
    fin = "crlf" if crlf and not lf_solo else "lf" if lf_solo and not crlf else "mixto" if crlf else "sin-saltos"
    return f"sha256={hashlib.sha256(b).hexdigest()} bytes={len(b)} CR={b.count(bytes([13]))} LF={b.count(bytes([10]))} eol={fin}"


def cmd_sello(a):
    if len(a) != 2:
        salir("uso: sello <copia> <ruta>")
    f = ruta_en(copia(a[0]), a[1])
    if not f.is_file():
        salir(f"NO EXISTE: {a[0]}/{a[1]}")
    print(f"{a[0]}/{a[1]}: {_sello(f.read_bytes())}")


def cmd_sello_repo(a):
    if len(a) != 1:
        salir("uso: sello-repo <ruta>")
    r = a[0].replace("\\", "/")
    if r.startswith("/") or ".." in r.split("/") or ":" in r or r.startswith("-"):
        salir(f"RUTA NO VALIDA: {a[0]}")
    f = (Path(REPO) / r).resolve()
    if Path(REPO).resolve() not in f.parents or not f.is_file():
        salir(f"NO EXISTE EN EL REPOSITORIO: {r}")
    try:
        p = subprocess.run(["git", "-C", REPO, "ls-files", "--eol", "--", r], capture_output=True, timeout=60)
        eol = p.stdout.decode(errors="replace").strip() or "(no está en el índice)"
    except subprocess.TimeoutExpired:
        eol = "TIMEOUT"
    print(f"repo/{r}: {_sello(f.read_bytes())} | git ls-files --eol: {eol}")


def cmd_mutar(a):
    if len(a) != 4:
        salir("uso: mutar <copia> <ruta> <desde> <hasta>")
    c, ruta, desde, hasta = a
    f = ruta_en(copia(c), ruta)
    if f.name == "project.godot":
        salir("RECHAZADO: project.godot lleva el aislamiento de la copia (config/name); no se muta")
    if not f.is_file():
        salir(f"NO EXISTE: {c}/{ruta}")
    if not desde or desde == hasta:
        salir("MUTANTE NO VALIDO: <desde> vacío o igual a <hasta>")
    b, d, h = f.read_bytes(), desde.encode("utf-8"), hasta.encode("utf-8")
    n = b.count(d)
    if n != 1:
        salir(f"MUTANTE RECHAZADO: <desde> aparece {n} veces en {c}/{ruta}; tiene que aparecer exactamente una")
    linea = b[:b.index(d)].count(bytes([10])) + 1
    f.write_bytes(b.replace(d, h))          # solo en la copia, y conserva los finales de línea del resto
    print(f"{c}/{ruta}: mutado en la línea {linea} | {_sello(f.read_bytes())}")


def cmd_poner(a):
    if len(a) != 3:
        salir("uso: poner <copia> <ruta> <fuente>")
    c, ruta, fuente = a
    dest = ruta_en(copia(c), ruta)
    if dest.name == "project.godot":
        salir("RECHAZADO: project.godot lleva el aislamiento de la copia (config/name); no se pone")
    src = (CARPETA_FUENTES.parent / fuente.replace("\\", "/")).resolve()
    if CARPETA_FUENTES not in src.parents or not src.is_file():
        salir(f"FUENTE NO VALIDA: {fuente} (tiene que ser un archivo bajo {CARPETA_FUENTES.name}/)")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(src.read_bytes())
    print(f"{c}/{ruta}: puesto desde {fuente} | {_sello(dest.read_bytes())}")


COMANDOS = {"copiar": cmd_copiar, "clonar": cmd_clonar, "correr": cmd_correr, "diff": cmd_diff,
            "sello": cmd_sello, "sello-repo": cmd_sello_repo, "mutar": cmd_mutar, "poner": cmd_poner}


def main(argv):
    if not argv or argv[0] not in COMANDOS:
        salir(__doc__.split("Uso:")[1].split("Salida:")[0].rstrip() if "Uso:" in __doc__ else "uso: ver el encabezado")
    comprobar_configuracion()
    CARPETA.mkdir(parents=True, exist_ok=True)
    COMANDOS[argv[0]](argv[1:])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
