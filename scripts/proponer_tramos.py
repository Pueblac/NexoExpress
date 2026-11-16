"""Propone tramos candidatos para el mapa_de_lectura del Guionista (kit coordinador v1.3.3).

El Guionista da temas con un archivo (o glob) y un patrón. El script busca cada patrón y
propone tramos de 3 a 40 líneas con su ancla literal (la línea que casó, sin espacios a
los lados). Si la línea abre un bloque (una función, un método, una clase), el tramo llega
hasta el bloque siguiente, con el tope de 40 líneas. El Guionista elige y recorta. El
script no decide qué entra en el mapa, y el validador sigue siendo quien comprueba.

Qué cuenta como «abre un bloque» lo dice una expresión regular. La de fábrica reconoce
definiciones habituales (Python `def`/`class`, R `<- function`, JavaScript `function`,
Go/GDScript `func`, SQL `CREATE ...`, Stata `program define`, encabezados Markdown, solo en archivos .md). Para
otro lenguaje, pásela con `--bloque` o por tema con la clave "bloque".

Uso:
    python -I scripts/proponer_tramos.py --raiz <raíz del repositorio> temas.json > candidatos.json
    temas.json: [{"tema": "limpieza de folios", "archivo": "src/limpieza.py", "patron": "def normalizar_folio"}, ...]
    Opcional por tema: "antes" (líneas antes, 2 por defecto), "despues" (12), "max" (5 coincidencias),
    "bloque" (regex propia del tema), "regex" (true si el patrón es una expresión regular).

El "patron" es TEXTO LITERAL por defecto (desde v1.3): se busca tal cual, con paréntesis, llaves
y puntos incluidos. Dos pilotos fallaron con patrones que llevaban paréntesis y llaves, cuando el
patrón se leía como expresión regular. Quien quiera una expresión la marca con "regex": true en ese tema.
"""
import argparse
import json
import re
import sys
from pathlib import Path

TOPE = 40
FORMATO = ('Formato exacto: [{"tema": "...", "archivo": "ruta o glob", "patron": "texto"}, ...]; opcionales: '
           '"antes", "despues", "max", "bloque", "regex" (true o false).')
BLOQUE_POR_DEFECTO = (
    r"^\s*(?:async\s+)?def\s"                       # Python
    r"|^\s*class\s"                                 # Python, JavaScript y otros
    r"|^\s*(?:static\s+)?func\s"                    # Go, GDScript, Swift
    r"|^\s*(?:export\s+)?(?:async\s+)?function\s"   # JavaScript, PHP
    r"|^\s*[\w.]+\s*<-\s*function\s*\("             # R
    r"|^\s*program\s+define\s"                      # Stata
    r"|^\s*(?:CREATE|create)\s"                     # SQL
)
BLOQUE_MARKDOWN = r"|^#{1,6}\s"                      # encabezados: solo para archivos .md

sys.stdout.reconfigure(encoding="utf-8")


def tramo(lineas, i, antes, despues, bloque):
    desde = max(1, i + 1 - antes)
    if bloque.match(lineas[i]):
        fin = i + 1
        while fin < len(lineas) and not bloque.match(lineas[fin]) and fin - desde + 1 < TOPE:
            fin += 1
        hasta = fin  # 1-based: última línea antes del bloque siguiente
    else:
        hasta = i + 1 + despues
    hasta = min(len(lineas), hasta, desde + TOPE - 1)
    if hasta - desde + 1 < 3:
        hasta = min(len(lineas), desde + 2)
    return desde, hasta


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--raiz", required=True)
    ap.add_argument("--bloque", default=BLOQUE_POR_DEFECTO,
                    help="regex de inicio de bloque (por defecto, varias sintaxis habituales)")
    ap.add_argument("temas")
    a = ap.parse_args()
    raiz = Path(a.raiz)
    try:
        temas = json.loads(Path(a.temas).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        sys.exit(f"{a.temas}: no se puede leer como JSON ({e}). {FORMATO}")
    if not isinstance(temas, list) or not all(isinstance(t, dict) for t in temas):
        sys.exit(f"{a.temas}: tiene que ser una LISTA de temas (objetos). {FORMATO}")
    salida = []
    for t in temas:
        faltan = [k for k in ("tema", "archivo", "patron") if not isinstance(t.get(k), str) or not t[k]]
        if faltan:
            sys.exit(f"tema {t.get('tema')!r}: falta {' y '.join(repr(k) for k in faltan)} (texto, sin cambiar el nombre "
                     f"de la clave); claves recibidas: {sorted(t)}. {FORMATO}")
        if not isinstance(t.get("regex", False), bool):
            sys.exit(f"tema {t.get('tema')!r}: \"regex\" debe ser true o false, no {t['regex']!r}")
        patron = re.compile(t["patron"] if t.get("regex") else re.escape(t["patron"]))
        propia = t.get("bloque")          # una regex explícita (del tema o de --bloque) se respeta tal cual
        explicita = propia is not None or a.bloque != BLOQUE_POR_DEFECTO
        base = propia if propia is not None else a.bloque
        existentes = 0
        archivos = sorted(raiz.glob(t["archivo"])) or [raiz / t["archivo"]]
        hallados = 0
        for f in archivos:
            if not f.is_file():
                salida.append({"tema": t["tema"], "archivo": t["archivo"], "sin_coincidencias": "no existe"})
                continue
            existentes += 1
            bloque = re.compile(base + (BLOQUE_MARKDOWN if f.suffix.lower() == ".md" and not explicita else ""))
            lineas = f.read_text(encoding="utf-8", errors="replace").splitlines()
            for i, l in enumerate(lineas):
                if patron.search(l) and hallados < t.get("max", 5):
                    desde, hasta = tramo(lineas, i, t.get("antes", 2), t.get("despues", 12), bloque)
                    salida.append({"tema": t["tema"], "archivo": f.relative_to(raiz).as_posix(),
                                   "desde": desde, "hasta": hasta, "ancla": l.strip()})
                    hallados += 1
        if hallados == 0 and existentes > 0:   # si nada existe ya se informó «no existe»
            salida.append({"tema": t["tema"], "archivo": t["archivo"], "sin_coincidencias": t["patron"]})
    json.dump(salida, sys.stdout, ensure_ascii=False, indent=1)
    print()


if __name__ == "__main__":
    main()
