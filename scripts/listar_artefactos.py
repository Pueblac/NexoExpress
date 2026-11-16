"""Lista los artefactos de un ciclo con su índice de secciones (kit coordinador v1.2).

Lo corre el Agente C al cerrar un ciclo y su salida es el insumo del Archivista, que así no
tiene que buscar los archivos ni sacar sus índices. Por cada archivo del ciclo da la ruta,
las líneas y, si es Markdown, sus cabeceras con número de línea. Para los demás archivos
(imágenes, binarios, carpetas de evidencia) da solo la ruta y el tamaño.

Dónde busca: en el directorio de cada rol de `coordinador.json` (`escribe_en`) y en el de
encargos del modo autónomo, todo archivo o carpeta cuyo nombre empiece por `<CICLO>_` o
`<CICLO>-`, más `consumo_<CICLO>.txt` en el directorio del coordinador. La convención es
que cada artefacto lleve delante el identificador corto de su ciclo o historia. Si el
proyecto guarda artefactos en otro sitio, añádalos con `--patron` (glob relativo a la raíz,
con `{h}` en lugar del ciclo).

Uso:
    python -I scripts/listar_artefactos.py <CICLO> [<archivo extra> ...] [--patron 'capturas/{h}_*'] > coordinacion/artefactos_<CICLO>.txt
"""
import argparse
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
TEXTO = {".md", ".txt", ".json", ".csv", ".tsv", ".py", ".r", ".sh", ".sql", ".do",
         ".diff", ".patch", ".yml", ".yaml", ".toml", ".cfg", ".ini", ".js", ".ts",
         ".html", ".tex"}

sys.stdout.reconfigure(encoding="utf-8")


def patrones_de_config() -> list[str]:
    try:
        cfg = json.loads((BASE / "coordinador.json").read_text(encoding="utf-8"))
    except Exception:
        cfg = {}
    dirs = []
    for r in (cfg.get("roles") or {}).values():
        d = (r.get("escribe_en") or "").strip()
        if d and not d.startswith("(") and d not in dirs:
            dirs.append(d)
    auto = cfg.get("modo_autonomo") or {}
    if auto.get("dir_encargos") and auto["dir_encargos"] not in dirs:
        dirs.append(auto["dir_encargos"])
    coord = ((cfg.get("roles") or {}).get("coordinador") or {}).get("escribe_en") or "coordinacion/"
    pats = []
    for d in dirs:
        d = d.rstrip("/") + "/"
        pats += [d + "{h}_*", d + "{h}-*"]
    pats.append(coord.rstrip("/") + "/consumo_{h}.txt")
    return pats


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("ciclo")
    ap.add_argument("extras", nargs="*", help="archivos extra (relativos a la raíz), p. ej. la ficha inicial")
    ap.add_argument("--patron", action="append", default=[], help="glob extra con {h}")
    a = ap.parse_args()
    h = a.ciclo
    rutas = [BASE / x for x in a.extras]
    for p in patrones_de_config() + a.patron:
        rutas += sorted(BASE.glob(p.format(h=h)))
    vistos = set()
    for r in rutas:
        if r in vistos or not r.exists():
            continue
        vistos.add(r)
        rel = r.relative_to(BASE).as_posix()
        if r.is_dir():
            n = sum(1 for f in r.rglob("*") if f.is_file())
            print(f"{rel}/  (carpeta, {n} archivos)")
            continue
        if r.suffix.lower() in TEXTO:
            lineas = r.read_text(encoding="utf-8", errors="replace").splitlines()
            print(f"{rel}  ({len(lineas)} líneas)")
            if r.suffix.lower() == ".md":
                for i, l in enumerate(lineas, 1):
                    if l.startswith("#"):
                        print(f"  {rel}:{i}  {l.strip()[:100]}")
        else:
            print(f"{rel}  ({r.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
