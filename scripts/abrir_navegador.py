"""Chrome dedicado para el asistente navegador (A-navegacion) del kit coordinador (v1.5).

Lo usa el monitor de Claude de una actividad A-navegacion, nunca el asistente: abre Chrome con el puerto de
depuración en un PERFIL DEDICADO del kit (no el del usuario), lanza al asistente con `lanzar_agy.py` y al
terminar lo cierra. El asistente Gemini en agy usa su subagente `browser` (Chrome DevTools MCP), que se conecta
a este Chrome [medido el 09-11-2026, agy 1.5.3, Chrome 131, Windows: `MOTOR_EXTERNO.md` §11].

Perfil dedicado: uno por máquina, compartido por los coordinadores, y se conserva entre corridas para que las
sesiones que el Director abre a mano (JupyterHub, GitLab, tableros) sigan abiertas. Por eso existe `sesion`:
abre ese mismo perfil SIN puerto de depuración para que el Director inicie sesión (es el caso MANUAL del
navegador: inicio de sesión, segundo factor, captcha). El perfil del usuario (la opción A de la nota del
Director) no está en el kit: el script se niega a usar el directorio de Chrome del usuario.

`abrir` escribe `DevToolsActivePort` en el directorio de Chrome del usuario (es donde lo busca el subagente) con
respaldo, y `cerrar` lo deja como estaba; también si `abrir` falla a mitad. Toda espera lleva tope y TIMEOUT.

Subcomandos:
    abrir   [--url URL] [--tope 30]   Chrome dedicado con el puerto; exit 0 LISTO, 3 TIMEOUT, 2 STOP
    cerrar  [--tope 15]               cierra ese Chrome y restaura DevToolsActivePort; exit 0 CERRADO
    estado                            si está abierto, sus pestañas (título y URL)
    leer    --url URL [--selector CSS] [--max 3000] [--tope 30]
                                      el monitor vuelve a medir: abre la URL en una pestaña nueva, espera la
                                      carga y devuelve título, URL final y texto (del selector o del body), y
                                      cierra la pestaña. Solo lee: no hace clic ni escribe.
    sesion  [--url URL]               el perfil dedicado SIN puerto, para que el Director inicie sesión a mano

Configuración opcional en coordinador.json, `supervision.asistentes.navegador`:
    "perfil": carpeta del perfil dedicado (por defecto <datos locales>/kit_coordinador/chrome_navegador)
    "chrome": ruta del ejecutable (por defecto se busca), "puerto": 9222

KIT COORDINADOR — no hay rutas absolutas: el workspace sale de la ubicación del script.
"""
import argparse
import base64
import json
import os
import platform
import shutil
import socket
import struct
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = Path(__file__).resolve().parents[1]
SISTEMA = platform.system()
BANDERAS = ["--no-first-run", "--no-default-browser-check", "--disable-features=Translate",
            "--disable-sync", "--password-store=basic"]
# Sin traducción: en la prueba del 09-11 Chrome tradujo example.com al castellano y el DOM dejó de ser el del
# servidor. Sin sincronización ni gestor de contraseñas del sistema: el perfil es del kit, no de una cuenta.


def datos_locales() -> Path:
    if SISTEMA == "Windows":
        return Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
    if SISTEMA == "Darwin":
        return Path.home() / "Library" / "Application Support"
    return Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share")


def chrome_del_usuario() -> Path:
    """Directorio de datos del Chrome del usuario: ahí busca el subagente `DevToolsActivePort`."""
    if SISTEMA == "Windows":
        return datos_locales() / "Google" / "Chrome" / "User Data"
    if SISTEMA == "Darwin":
        return datos_locales() / "Google" / "Chrome"
    return Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config") / "google-chrome"


def config() -> dict:
    f = BASE / "coordinador.json"
    try:
        cfg = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
    except (OSError, json.JSONDecodeError) as e:
        sys.exit(f"STOP: coordinador.json ilegible: {e}")
    return ((cfg.get("supervision") or {}).get("asistentes") or {}).get("navegador") or {}


def ejecutable(c: dict) -> str:
    if c.get("chrome"):
        return c["chrome"]
    candidatos = []
    if SISTEMA == "Windows":
        for v in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA"):
            if os.environ.get(v):
                candidatos.append(Path(os.environ[v]) / "Google" / "Chrome" / "Application" / "chrome.exe")
    elif SISTEMA == "Darwin":
        candidatos.append(Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"))
    for c_ in candidatos:
        if c_.exists():
            return str(c_)
    for n in ("google-chrome", "google-chrome-stable", "chromium", "chrome"):
        if shutil.which(n):
            return shutil.which(n)
    sys.exit("STOP: no encuentro Chrome; declara supervision.asistentes.navegador.chrome en coordinador.json.")


def rutas(c: dict) -> dict:
    perfil = Path(os.path.expandvars(os.path.expanduser(c.get("perfil") or
                                                         datos_locales() / "kit_coordinador" / "chrome_navegador")))
    if perfil.resolve() == chrome_del_usuario().resolve() or chrome_del_usuario().resolve() in perfil.resolve().parents:
        sys.exit("STOP: el perfil del asistente no puede ser el Chrome del usuario (opción A, fuera del kit).")
    estado_dir = perfil.parent
    return {"perfil": perfil, "estado": estado_dir / "navegador_estado.json",
            "respaldo": estado_dir / "DevToolsActivePort.respaldo",
            "dtap": chrome_del_usuario() / "DevToolsActivePort", "puerto": int(c.get("puerto") or 9222)}


def http(puerto: int, ruta: str, metodo: str = "GET", tope: float = 2):
    r = urllib.request.Request(f"http://127.0.0.1:{puerto}{ruta}", method=metodo)
    with urllib.request.urlopen(r, timeout=tope) as resp:
        cuerpo = resp.read().decode("utf-8", "replace")
    try:
        return json.loads(cuerpo)
    except json.JSONDecodeError:
        return cuerpo


def version(puerto: int):
    try:
        return http(puerto, "/json/version")
    except OSError:
        return None


# --- WebSocket mínimo (RFC 6455) para el protocolo de DevTools, sin dependencias -----------------------------

class Cdp:
    def __init__(self, url_ws: str, tope: float):
        u = urllib.parse.urlparse(url_ws)
        self.s = socket.create_connection((u.hostname, u.port), timeout=tope)
        clave = base64.b64encode(os.urandom(16)).decode()
        self.s.sendall((f"GET {u.path} HTTP/1.1\r\nHost: {u.hostname}:{u.port}\r\nUpgrade: websocket\r\n"
                        f"Connection: Upgrade\r\nSec-WebSocket-Key: {clave}\r\nSec-WebSocket-Version: 13\r\n\r\n").encode())
        cabecera = b""
        while b"\r\n\r\n" not in cabecera:
            trozo = self.s.recv(1024)
            if not trozo:
                raise OSError("DevTools cerró la conexión en el saludo")
            cabecera += trozo
        primera = cabecera.split(b"\r\n", 1)[0]
        if b" 101 " not in primera:
            raise OSError("DevTools rechazó el WebSocket: " + primera.decode(errors="replace"))
        self.resto, self.n = cabecera.split(b"\r\n\r\n", 1)[1], 0

    def _leer(self, k: int) -> bytes:
        while len(self.resto) < k:
            trozo = self.s.recv(65536)
            if not trozo:
                raise OSError("DevTools cerró la conexión")
            self.resto += trozo
        dato, self.resto = self.resto[:k], self.resto[k:]
        return dato

    def _mensaje(self) -> str:
        partes = []
        while True:
            b1, b2 = self._leer(2)
            largo = b2 & 0x7F
            if largo == 126:
                largo = struct.unpack(">H", self._leer(2))[0]
            elif largo == 127:
                largo = struct.unpack(">Q", self._leer(8))[0]
            datos = self._leer(largo)
            op = b1 & 0x0F
            if op == 0x8:
                raise OSError("DevTools cerró la conexión")
            if op in (0x9, 0xA):
                continue
            partes.append(datos)
            if b1 & 0x80:
                return b"".join(partes).decode("utf-8", "replace")

    def llamar(self, metodo: str, params: dict | None = None) -> dict:
        self.n += 1
        carga = json.dumps({"id": self.n, "method": metodo, "params": params or {}}).encode()
        mascara = os.urandom(4)
        cab = bytes([0x81])
        if len(carga) < 126:
            cab += bytes([0x80 | len(carga)])
        elif len(carga) < 65536:
            cab += bytes([0x80 | 126]) + struct.pack(">H", len(carga))
        else:
            cab += bytes([0x80 | 127]) + struct.pack(">Q", len(carga))
        self.s.sendall(cab + mascara + bytes(c ^ mascara[i % 4] for i, c in enumerate(carga)))
        while True:
            m = json.loads(self._mensaje())
            if m.get("id") == self.n:
                if "error" in m:
                    raise OSError(f"{metodo}: {m['error'].get('message')}")
                return m.get("result") or {}

    def cerrar(self):
        try:
            self.s.close()
        except OSError:
            pass


# --- Subcomandos ----------------------------------------------------------------------------------------------

def lanzar(exe: str, args: list) -> int:
    opciones = {"stdin": subprocess.DEVNULL, "stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL,
                "close_fds": True}
    if SISTEMA == "Windows":
        opciones["creationflags"] = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        opciones["start_new_session"] = True
    return subprocess.Popen([exe, *args], **opciones).pid


def restaurar_dtap(r: dict, escrito: str | None) -> str:
    """Deja DevToolsActivePort del usuario como estaba antes de `abrir`."""
    if r["respaldo"].exists():
        shutil.copyfile(r["respaldo"], r["dtap"])
        r["respaldo"].unlink()
        return "restaurado desde su respaldo"
    if r["dtap"].exists():
        if escrito is None or r["dtap"].read_text(encoding="ascii", errors="replace") == escrito:
            r["dtap"].unlink()
            return "retirado (no existía antes)"
        return "NO se tocó: cambió durante la corrida (lo escribió otro Chrome)"
    return "no estaba"


def abrir(o, c: dict) -> int:
    r = rutas(c)
    if version(r["puerto"]):
        print(f"STOP: el puerto {r['puerto']} ya responde. Si es un navegador del kit que quedó abierto, "
              "`python -I scripts/abrir_navegador.py cerrar`; si es otro programa, cambia `puerto`.")
        return 2
    if r["estado"].exists():
        print(f"STOP: quedó un estado de una corrida anterior ({r['estado']}); corre `cerrar` primero.")
        return 2
    r["perfil"].mkdir(parents=True, exist_ok=True)
    pid = lanzar(ejecutable(c), [f"--remote-debugging-port={r['puerto']}", f"--user-data-dir={r['perfil']}",
                                 *BANDERAS, "--new-window", o.url or "about:blank"])
    estado = {"pid": pid, "puerto": r["puerto"], "perfil": str(r["perfil"]), "workspace": str(BASE),
              "abierto": time.strftime("%Y-%m-%d %H:%M:%S"), "dtap_escrito": None}
    r["estado"].write_text(json.dumps(estado, ensure_ascii=False, indent=1), encoding="utf-8")
    limite, v = time.monotonic() + o.tope, None
    while time.monotonic() < limite and not (v := version(r["puerto"])):
        time.sleep(0.5)
    if not v:
        print(f"TIMEOUT: Chrome no abrió el puerto {r['puerto']} en {o.tope} s; lo cierro.")
        cerrar(argparse.Namespace(tope=10), c, silencioso=True)
        return 3
    ruta_ws = urllib.parse.urlparse(v["webSocketDebuggerUrl"]).path
    escrito = f"{r['puerto']}\n{ruta_ws}"
    if r["dtap"].exists():
        shutil.copyfile(r["dtap"], r["respaldo"])
    r["dtap"].parent.mkdir(parents=True, exist_ok=True)
    r["dtap"].write_text(escrito, encoding="ascii", newline="")
    estado["dtap_escrito"] = escrito
    r["estado"].write_text(json.dumps(estado, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"LISTO: {v.get('Browser')} en el puerto {r['puerto']}, perfil {r['perfil']}. "
          f"Al terminar: python -I scripts/abrir_navegador.py cerrar")
    return 0


def matar(pid: int):
    if SISTEMA == "Windows":
        subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True)
    else:
        try:
            os.killpg(pid, 9)
        except OSError:
            pass


def cerrar(o, c: dict, silencioso: bool = False) -> int:
    r = rutas(c)
    estado = json.loads(r["estado"].read_text(encoding="utf-8")) if r["estado"].exists() else {}
    puerto = estado.get("puerto", r["puerto"])
    v = version(puerto)
    if v and estado:
        try:
            cdp = Cdp(v["webSocketDebuggerUrl"], 5)
            try:
                cdp.llamar("Browser.close")
            except OSError:
                pass
            cdp.cerrar()
        except OSError:
            pass
        limite = time.monotonic() + o.tope
        while time.monotonic() < limite and version(puerto):
            time.sleep(0.5)
    elif v and not estado:
        print(f"STOP: el puerto {puerto} responde pero no hay estado del kit: no es un navegador del kit, no lo cierro.")
        return 2
    if estado.get("pid") and (version(puerto) or not v):
        matar(estado["pid"])
    sigue = version(puerto)
    dtap = restaurar_dtap(r, estado.get("dtap_escrito"))
    if r["estado"].exists():
        r["estado"].unlink()
    if not silencioso:
        print(("FALLA: el puerto sigue respondiendo; " if sigue else "CERRADO: ") + f"DevToolsActivePort {dtap}.")
    return 1 if sigue else 0


def estado_cmd(o, c: dict) -> int:
    r = rutas(c)
    v = version(r["puerto"])
    print(f"perfil: {r['perfil']}\nestado del kit: {'sí' if r['estado'].exists() else 'no'}\n"
          f"puerto {r['puerto']}: {v.get('Browser') if v else 'no responde'}")
    if v:
        for p in http(r["puerto"], "/json/list"):
            if p.get("type") == "page":
                print(f"  - {p.get('title')} | {p.get('url')}")
    return 0


def leer(o, c: dict) -> int:
    r = rutas(c)
    if not version(r["puerto"]):
        print("STOP: el navegador del kit no está abierto (`abrir` primero).")
        return 2
    destino = http(r["puerto"], "/json/new?" + urllib.parse.quote(o.url, safe=":/?&=#%"), "PUT", 10)
    cdp = None
    try:
        cdp = Cdp(destino["webSocketDebuggerUrl"], o.tope)
        limite, listo = time.monotonic() + o.tope, False
        while time.monotonic() < limite:
            res = cdp.llamar("Runtime.evaluate", {"expression": "document.readyState", "returnByValue": True})
            if (res.get("result") or {}).get("value") == "complete":
                listo = True
                break
            time.sleep(0.5)
        sel = json.dumps(o.selector) if o.selector else "null"
        expr = (f"(() => {{ const s = {sel}; const n = s ? document.querySelector(s) : document.body; "
                f"return JSON.stringify({{titulo: document.title, url: location.href, "
                f"encontrado: !!n, texto: n ? n.innerText.slice(0, {o.max}) : null}}); }})()")
        res = cdp.llamar("Runtime.evaluate", {"expression": expr, "returnByValue": True})
        dato = json.loads((res.get("result") or {}).get("value") or "{}")
        dato["carga_completa"] = listo
        print(json.dumps(dato, ensure_ascii=False, indent=1))
        return 0 if listo and dato.get("encontrado") else 1
    finally:
        if cdp:
            cdp.cerrar()
        try:
            http(r["puerto"], f"/json/close/{destino['id']}")
        except OSError:
            pass


def sesion(o, c: dict) -> int:
    r = rutas(c)
    if version(r["puerto"]) or r["estado"].exists():
        print("STOP: el perfil está abierto para un asistente; espera a que termine (`estado`).")
        return 2
    r["perfil"].mkdir(parents=True, exist_ok=True)
    lanzar(ejecutable(c), [f"--user-data-dir={r['perfil']}", *BANDERAS, "--new-window", o.url or "about:blank"])
    print(f"Abierto el perfil dedicado {r['perfil']} sin puerto de depuración. Inicia sesión y cierra la ventana "
          "cuando termines: las sesiones quedan para los asistentes.")
    return 0


def main() -> int:
    a = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = a.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("abrir"); p.add_argument("--url"); p.add_argument("--tope", type=float, default=30)
    p = sub.add_parser("cerrar"); p.add_argument("--tope", type=float, default=15)
    sub.add_parser("estado")
    p = sub.add_parser("leer"); p.add_argument("--url", required=True); p.add_argument("--selector")
    p.add_argument("--max", type=int, default=3000); p.add_argument("--tope", type=float, default=30)
    p = sub.add_parser("sesion"); p.add_argument("--url")
    o = a.parse_args()
    c = config()
    return {"abrir": abrir, "cerrar": cerrar, "estado": estado_cmd, "leer": leer, "sesion": sesion}[o.cmd](o, c)


if __name__ == "__main__":
    sys.exit(main())
