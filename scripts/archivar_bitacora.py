"""Archiva entradas cerradas de la bitácora y regenera su índice de decisiones delegadas.

Kit coordinador v1.2. Lo corre el Agente C al cerrar un ciclo (la bitácora es suya).
Mueve SIN CAMBIOS las entradas que van desde el final del índice hasta justo antes de la
cabecera `--desde` al directorio de archivo (`<dir_bitacora_archivo>/<nombre>.md`), y
reescribe el índice de DD (todas las
DECISION_DELEGADA de los archivos archivados y de la activa, con archivo y línea).
Comprueba que lo movido + lo que queda reproduce byte a byte el cuerpo anterior; si no,
no escribe nada.

Rutas: `modo_autonomo.bitacora` y `modo_autonomo.dir_bitacora_archivo` de
`coordinador.json` (por defecto `coordinacion/bitacora.md` y `coordinacion/bitacora_archivo/`).
Supuestos sobre la bitácora: una cabecera de documento cerrada por una línea `---`, entradas
que empiezan por `## `, y las decisiones escritas como `DECISION_DELEGADA DD-NN — título`.

Uso:
    python -I scripts/archivar_bitacora.py --desde "## <cabecera de la primera entrada que se queda>" --nombre 2026-10-24_ciclo3
"""
import argparse
import json
import sys
import hashlib
import re
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
try:
    _AUTO = json.loads((BASE / "coordinador.json").read_text(encoding="utf-8")).get("modo_autonomo") or {}
except Exception:
    _AUTO = {}
REL_ACTIVA = _AUTO.get("bitacora", "coordinacion/bitacora.md")
REL_ARCHIVO = _AUTO.get("dir_bitacora_archivo", "coordinacion/bitacora_archivo/").rstrip("/")
ACTIVA = BASE / REL_ACTIVA
ARCHIVO = BASE / REL_ARCHIVO
CAB_INDICE = b"## \xc3\x8dndice de decisiones delegadas"   # «## Índice de decisiones delegadas»
CAB_ARCHIVO = b"# Bitacora del Coordinador - archivo (sin cambios)"
DD = re.compile(r"DECISION_DELEGADA (DD-\d+)[^—]*—\s*([^*]+)")


sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def partir(b: bytes):
    lineas = b.split(b"\n")
    cab_fin = next((i for i, l in enumerate(lineas) if l.strip() == b"---"), None)
    if cab_fin is None:
        raise SystemExit("La bitácora no tiene la línea `---` que cierra la cabecera del documento. No escribo nada.")
    cab_fin += 1
    i0 = next((i for i, l in enumerate(lineas) if l.startswith(CAB_INDICE)), None)
    if i0 is None:
        return lineas[:cab_fin], lineas[cab_fin:]
    i1 = next((i for i in range(i0, len(lineas)) if lineas[i].strip() == b"---"), None)
    if i1 is None:
        raise SystemExit("El índice de decisiones delegadas no termina en una línea `---`. No escribo nada.")
    return lineas[:cab_fin], lineas[i1 + 1:]


def indice(fuentes, nl: bytes):
    filas = []
    for ruta, lineas, desplaz in fuentes:
        for n, l in enumerate(lineas, 1):
            m = DD.search(l.decode("utf-8", "replace"))
            if m:
                filas.append((int(m.group(1)[3:]), m.group(1), m.group(2).strip()[:70], ruta, n + desplaz))
    filas.sort()
    out = ["## Índice de decisiones delegadas (DD) — generado por scripts/archivar_bitacora.py", "",
           f"Las entradas cerradas están **archivadas sin cambios** en `{REL_ARCHIVO}/`.",
           "Cada DD con su archivo y línea:", ""]
    out += [f"- **{dd}** — {t} → `{r}:{n}`" for _, dd, t, r, n in filas]
    out += ["", "---", ""]
    return [s.encode("utf-8") + (b"\r" if nl == b"\r\n" else b"") for s in out], len(filas)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--desde", required=True, help="cabecera exacta (## ...) de la primera entrada que se queda")
    ap.add_argument("--nombre", required=True, help="nombre del archivo de archivo, sin .md")
    a = ap.parse_args()
    b = ACTIVA.read_bytes()
    nl = b"\r\n" if b"\r\n" in b else b"\n"
    cab, cuerpo = partir(b)
    corte = next((i for i, l in enumerate(cuerpo) if l.rstrip(b"\r").decode("utf-8") == a.desde), None)
    if corte is None:
        raise SystemExit(f"No encuentro la cabecera: {a.desde!r}. No escribo nada.")
    movido, queda = cuerpo[:corte], cuerpo[corte:]
    if not any(l.startswith(b"## ") for l in movido):
        raise SystemExit("Lo que se movería no contiene ninguna entrada `## `: no hay nada que archivar "
                         "(¿se repitió el mismo --desde?). No escribo nada.")
    destino = ARCHIVO / f"{a.nombre}.md"
    if destino.exists():
        raise SystemExit(f"Ya existe {destino}. No escribo nada.")
    # 1. Todo se construye en memoria.
    pie = (b"\r" if nl == b"\r\n" else b"")
    arch = b"\n".join([CAB_ARCHIVO + pie, pie] + movido) + b"\n"
    fuentes = []
    for f in sorted(ARCHIVO.glob("*.md")) if ARCHIVO.is_dir() else []:
        fuentes.append((f"{REL_ARCHIVO}/{f.name}", f.read_bytes().split(b"\n"), 0))
    fuentes.append((f"{REL_ARCHIVO}/{destino.name}", arch.split(b"\n"), 0))
    tmp, _ = indice(fuentes + [(REL_ACTIVA, queda, 0)], nl)
    desplaz = len(cab) + len(tmp)
    idx, n = indice(fuentes + [(REL_ACTIVA, queda, desplaz)], nl)
    nueva = b"\n".join(cab + idx + queda)
    # 2. Se verifica la reconstrucción con los bytes que se van a escribir.
    lin_nueva = nueva.split(b"\n")
    rec = arch.split(b"\n")[2:-1] + lin_nueva[len(cab) + len(idx):]
    ok = b"\n".join(rec) == b"\n".join(cuerpo) and lin_nueva[:len(cab)] == cab
    if not ok:
        raise SystemExit("La reconstrucción (archivo + activa) no reproduce el cuerpo anterior. No escribo nada.")
    # 3. Solo entonces se escribe, con temporales y renombrado.
    ARCHIVO.mkdir(parents=True, exist_ok=True)
    t_arch = destino.with_name(destino.name + ".tmp")
    t_act = ACTIVA.with_name(ACTIVA.name + ".tmp")
    t_arch.write_bytes(arch)
    t_act.write_bytes(nueva)
    t_arch.replace(destino)
    t_act.replace(ACTIVA)
    print(f"movidas {len(movido)} líneas a {destino.name}; activa {len(lin_nueva)} líneas; "
          f"DD indexadas {n}; reconstrucción OK; sha cuerpo {hashlib.sha256(b''.join(cuerpo)).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
