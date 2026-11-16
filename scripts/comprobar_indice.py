"""Comprueba los punteros `ruta:línea` del índice del proyecto y del índice de la bitácora.

Kit coordinador v1.2. En la bitácora (el archivo que se llame como `modo_autonomo.bitacora`
de `coordinador.json`) solo se miran las filas del índice de DD. Cada puntero entre comillas
invertidas con forma `ruta:N` (ruta relativa al coordinador o a un repositorio de trabajo
autorizado en `.claude/settings.json`, o absoluta) debe apuntar a un archivo existente con
al menos N líneas. Si la línea del índice nombra una DD (DD-NN), la línea apuntada debe
contenerla. Fail-closed: exit=1 si falla alguno.

Uso:
    python -I scripts/comprobar_indice.py coordinacion/bitacora.md indice/INDICE.md indice/historias/*.md
"""
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
try:
    import json as _json
    RAICES = [BASE] + [Path(r) for r in _json.loads((BASE / ".claude" / "settings.json").read_text(encoding="utf-8"))
                       .get("permissions", {}).get("additionalDirectories", [])]
except Exception:
    RAICES = [BASE]
try:
    NOMBRE_BITACORA = Path((_json.loads((BASE / "coordinador.json").read_text(encoding="utf-8"))
                            .get("modo_autonomo") or {}).get("bitacora", "bitacora.md")).name
except Exception:
    NOMBRE_BITACORA = "bitacora.md"
PUNTERO = re.compile(r"`([^`\s]+?):(\d+)`")
DD = re.compile(r"\bDD-\d+\b")


sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main() -> int:
    total = malos = 0
    for arg in sys.argv[1:]:
        f = Path(arg) if Path(arg).is_absolute() else BASE / arg
        solo_indice = f.name == NOMBRE_BITACORA   # en la bitácora solo cuentan las filas del índice de DD
        for n, linea in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if solo_indice and not linea.startswith("- **DD-"):
                continue
            for ruta, num in PUNTERO.findall(linea):
                total += 1
                p = Path(ruta) if Path(ruta).is_absolute() else next((r / ruta for r in RAICES if (r / ruta).exists()), BASE / ruta)
                num = int(num)
                if not p.exists():
                    malos += 1
                    print(f"FALLA {arg}:{n} → {ruta}:{num} (no existe)")
                    continue
                lineas = p.read_text(encoding="utf-8", errors="replace").splitlines()
                if num > len(lineas):
                    malos += 1
                    print(f"FALLA {arg}:{n} → {ruta}:{num} (tiene {len(lineas)} líneas)")
                    continue
                dd = DD.search(linea)
                if dd and dd.group(0) not in lineas[num - 1]:
                    malos += 1
                    print(f"FALLA {arg}:{n} → {ruta}:{num} (no contiene {dd.group(0)})")
    print(f"PUNTEROS: {total - malos}/{total} correctos")
    return 0 if malos == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
