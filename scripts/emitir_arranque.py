"""Emite el bloque COPIAR de arranque en frío de un rol. Config-driven, portable.

KIT COORDINADOR — este script no sabe nada de ningún proyecto. Todo lo que
necesita sale de dos archivos del coordinador donde se instale:

  · `coordinador.json`      → qué roles existen, con qué modelo, qué producen
  · `.claude/settings.json` → los repositorios de trabajo autorizados

y de la ubicación del propio script, que da la raíz del workspace. **Por eso se
adapta solo al proyecto destino: no hay una sola ruta absoluta en el código ni
en las plantillas.** Si alguna vez tiene que editar este archivo para instalarlo
en otro coordinador, algo se hizo mal — lo que se edita es la configuración.

POR QUÉ EXISTE: un modelo al que se le dijo "actúa como asesor" en el turno 1 lo
ha olvidado en el turno 30, y nadie lo nota hasta que produce el artefacto
equivocado. La respuesta no es recordárselo: es que cada conversación arranque
en frío con su rol declarado por escrito, y que emitirlo cueste un comando.

Uso:
    python scripts/emitir_arranque.py --lista
    python scripts/emitir_arranque.py <rol> ["<tarea>"] [--insumo <ruta>]
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE = Path(__file__).resolve().parents[1]     # convención: scripts/ cuelga de la raíz
CONFIG = BASE / "coordinador.json"
DIR_PLANTILLAS_POR_DEFECTO = "docs/prompts_arranque"
DIR_BLOQUES = "bloques"


def cargar_config() -> dict:
    if not CONFIG.exists():
        raise SystemExit(
            f"Falta {CONFIG}.\n"
            "Copie `coordinador.example.json` del kit a la raíz como "
            "`coordinador.json` y complételo. Sin él no hay metodología que "
            "aplicar: el kit no trae roles por defecto a propósito.")
    try:
        return json.loads(CONFIG.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise SystemExit(f"{CONFIG} no es JSON válido (línea {e.lineno}): {e.msg}")


CFG = cargar_config()
ROLES = {k: v for k, v in (CFG.get("roles") or {}).items()
         if v.get("plantilla")}          # el validador es un script, no se arranca


def repos_autorizados() -> list[Path]:
    """Única fuente de verdad de los repositorios de trabajo: los settings.

    Leerlos de aquí y de ningún otro sitio es lo que hace que el prompt siga al
    día solo cuando cambia el alcance del proyecto.
    """
    cfg_path = BASE / ".claude" / "settings.json"
    try:
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise SystemExit(f"No se pudo leer {cfg_path}: {e}")
    dirs = (cfg.get("permissions") or {}).get("additionalDirectories") or []
    if not dirs:
        raise SystemExit(
            "`permissions.additionalDirectories` está vacío: no hay "
            "repositorios de trabajo que declarar. El prompt no se emite; un "
            "rol que no sabe dónde puede leer, lee donde no debe.")
    return [Path(d) for d in dirs]


def cuerpo_de_la_plantilla(texto: str, ruta: Path) -> str:
    """Extrae el prompt de entre las cercas ````text.

    La plantilla es documentación con el prompt dentro; lo que se emite es solo
    el prompt. Sin el marcador se aborta en vez de mandar el documento entero:
    un prompt con sus notas de diseño pegadas contamina al receptor.
    """
    m = re.search(r"^````text\n(.*?)^````$", texto, re.S | re.M)
    if not m:
        raise SystemExit(f"No se encontró el bloque ````text en {ruta}. "
                         "No se emite un prompt a medias.")
    return m.group(1).rstrip("\n")


def resolver_insumo(valor: str) -> str:
    """El insumo viaja como RUTA ABSOLUTA, no volcado dentro del prompt.

    Volcar el contenido congelaría una copia; el receptor debe leer el archivo
    vivo. Se comprueba que exista: despachar hacia un archivo inexistente es la
    forma más barata de fabricar una alucinación.
    """
    p = Path(valor)
    if not p.is_absolute():
        p = (BASE / p).resolve()
    if not p.exists():
        raise SystemExit(f"El insumo no existe en disco: {p}\n"
                         "No se despacha a un rol hacia un archivo que no está.")
    return str(p)


def modelo_de(r: dict) -> str:
    """El sello lleva el modelo que de verdad corre: en un rol con motor agy, `modelo_agy`."""
    if r.get("motor") == "agy":
        return f"{r.get('modelo_agy') or '?'} (agy)"
    return r.get("modelo", "")


def cadena_de_mando() -> str:
    """El orden de los mandatos, renderizado desde la configuración."""
    en_linea = sorted((r for r in (CFG.get("roles") or {}).values()
                       if r.get("en_la_linea")),
                      key=lambda r: r.get("orden", 99))
    return " → ".join(r.get("artefacto", "?") for r in en_linea)


def ganchos(rol: str) -> None:
    """Hooks declarados en config: scripts que deben correr antes de emitir."""
    for cmd in (CFG.get("roles", {}).get(rol, {}).get("antes_de_emitir") or []):
        try:
            subprocess.run([sys.executable, str(BASE / cmd)],
                           capture_output=True, timeout=120)
        except Exception as e:                      # nunca bloquea la emisión
            print(f"[aviso] no se pudo ejecutar el gancho {cmd}: {e}",
                  file=sys.stderr)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("rol", nargs="?", help="Rol a arrancar. Ver --lista.")
    ap.add_argument("tarea", nargs="?", help="Enunciado de la tarea.")
    ap.add_argument("--insumo", metavar="RUTA", help="Artefacto de entrada.")
    ap.add_argument("--tarea-desde", metavar="ARCHIVO")
    ap.add_argument("--fecha", help="AAAA-MM-DD; por defecto, hoy.")
    ap.add_argument("--lista", action="store_true",
                    help="Muestra la cadena de mando y los roles; termina.")
    args = ap.parse_args()

    if args.lista or not args.rol:
        print(f"{CFG.get('proyecto', {}).get('nombre', '(sin nombre)')}")
        print(f"Cadena de mando: {cadena_de_mando()}\n")
        for nombre, r in sorted(ROLES.items(), key=lambda x: x[1].get("orden", 99)):
            linea = "" if r.get("en_la_linea") else "  (fuera de la línea)"
            print(f"  {nombre:<12} {modelo_de(r) or '?'}{linea}")
            print(f"  {'':<12} produce {r.get('artefacto', '?')} → "
                  f"{r.get('escribe_en', '?')}")
            print(f"  {'':<12} ruta de traspaso {r.get('ruta_traspaso', '?')} · "
                  f"tarea {r.get('tarea', '?')} · insumo {r.get('insumo', '?')}\n")
        return 0 if args.lista else 2

    rol = args.rol.strip().lower()
    if rol not in ROLES:
        raise SystemExit(f"Rol desconocido: {rol!r}. Válidos: "
                         + ", ".join(sorted(ROLES)) + ". Use --lista.")
    cfg = ROLES[rol]

    tarea = (Path(args.tarea_desde).read_text(encoding="utf-8").strip()
             if args.tarea_desde else (args.tarea or "").strip())
    if not tarea:
        if cfg.get("tarea") == "obligatoria":
            raise SystemExit(
                f"El rol {rol!r} no se arranca sin enunciado de tarea. "
                "Un rol despachado en blanco inventa su encargo.")
        tarea = "(el Director la indicará en su siguiente mensaje)"

    if args.insumo:
        insumo = resolver_insumo(args.insumo)
    elif cfg.get("insumo") == "obligatorio":
        raise SystemExit(
            f"El rol {rol!r} exige --insumo: no decide sobre premisas que "
            "nadie midió.")
    else:
        insumo = "(ninguno)"

    ganchos(rol)
    repos = repos_autorizados()
    proy = CFG.get("proyecto", {})
    valores = {
        "PROYECTO": proy.get("nombre", ""),
        "DOMINIO": proy.get("dominio", ""),
        "WORKSPACE_PATH": str(BASE),
        "REPOS_AUTORIZADOS": "\n".join(f"   - `{r}`" for r in repos),
        "RAIZ_INSUMOS": str(repos[0].parent),
        "MODELO": modelo_de(cfg),
        "ARTEFACTO": cfg.get("artefacto", ""),
        "DIR_ARTEFACTO": str(BASE / cfg.get("escribe_en", "")),
        "CADENA_DE_MANDO": cadena_de_mando(),
        "DOC_METODOLOGIA": str(BASE / proy.get("documento_metodologia", "")),
        "DOC_ESTADO": str(BASE / proy.get("documento_estado", "")),
        "DOC_CADENA_MANDO": str(BASE / proy.get("documento_cadena_mando", "")),
        "FECHA": args.fecha or date.today().isoformat(),
        "TAREA": tarea,
        "INSUMO": insumo,
    }
    # Cualquier rol puede citar el directorio de otro sin que nadie lo cablee.
    for n, r in (CFG.get("roles") or {}).items():
        valores[f"DIR_{n.upper()}"] = str(BASE / r.get("escribe_en", ""))

    dir_plant = BASE / (proy.get("dir_plantillas") or DIR_PLANTILLAS_POR_DEFECTO)
    plantilla = dir_plant / cfg["plantilla"]
    if not plantilla.exists():
        raise SystemExit(f"Falta la plantilla del rol {rol!r}: {plantilla}")

    bloque = cuerpo_de_la_plantilla(
        plantilla.read_text(encoding="utf-8"), plantilla)
    for k, v in valores.items():
        bloque = bloque.replace("{{" + k + "}}", v)

    pendientes = sorted(set(re.findall(r"\{\{(\w+)\}\}", bloque)))
    if pendientes:
        raise SystemExit("Placeholders sin resolver: " + ", ".join(pendientes)
                         + ". No se emite un prompt con huecos.")

    destino = BASE / DIR_BLOQUES / f"bloque_{rol}.txt"
    destino.parent.mkdir(exist_ok=True)
    destino.write_text(bloque + "\n", encoding="utf-8")

    print(bloque)
    print()
    print(f"[arranque {rol} · {modelo_de(cfg) or '?'} · {valores['FECHA']} · "
          f"{len(repos)} repositorio(s) · su artefacto va a "
          f"{cfg.get('escribe_en', '?')}]", file=sys.stderr)
    print(f"[bloque escrito en {destino} — ábralo, Ctrl+A, Ctrl+C]",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
