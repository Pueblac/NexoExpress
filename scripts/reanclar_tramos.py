"""Re-ancla los tramos movidos de un mapa_de_lectura (kit coordinador v1.2).

Cuando el repositorio de trabajo cambia, los tramos de un encuadre o del mapa vivo se corren de línea. Para
cada tramo cuya ancla ya no cae dentro de su rango, el script lee el archivo en el commit
del sello (`sello_repo`) para saber en qué línea del tramo estaba el ancla, busca el ancla
en el archivo actual y propone el rango nuevo con la misma longitud y la misma posición
relativa del ancla. Si el ancla aparece varias veces, elige la más cercana al rango viejo.
Si el ancla desapareció, lo declara y no propone nada. Tampoco toca las afirmaciones: sus
cifras son mediciones, y las vuelve a medir el Guionista. El validador sigue siendo quien
comprueba.

Uso:
    python -I scripts/reanclar_tramos.py <encuadre.json> --raiz <raíz del repositorio> [--escribir <salida.json>]
    Sin --escribir solo informa. Con --escribir guarda una copia del encuadre con los rangos
    re-anclados (el sello no cambia: lo actualiza el Guionista al validar).
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")


def lineas_en_sello(raiz: Path, sello: str, archivo: str):
    r = subprocess.run(["git", "-C", str(raiz), "show", f"{sello}:./{archivo}"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.stdout.splitlines() if r.returncode == 0 else None


def reanclar(tr: dict, raiz: Path, sello: str, cache: dict):
    archivo, desde, hasta, ancla = tr["archivo"], tr["desde"], tr["hasta"], tr.get("ancla", "")
    if archivo not in cache:
        p = raiz / archivo
        cache[archivo] = p.read_text(encoding="utf-8", errors="replace").splitlines() if p.exists() else None
    actual = cache[archivo]
    if actual is None:
        return "ARCHIVO AUSENTE", None
    if ancla and hasta <= len(actual) and any(ancla in l for l in actual[desde - 1:hasta]):
        return "OK", None
    usos = [i + 1 for i, l in enumerate(actual) if ancla and ancla in l]
    if not usos:
        return "ANCLA AUSENTE (el código desapareció o cambió el texto del ancla)", None
    viejo = lineas_en_sello(raiz, sello, archivo)
    offset = 0
    if viejo:
        dentro = [i for i in range(desde - 1, min(hasta, len(viejo))) if ancla in viejo[i]]
        if dentro:
            offset = dentro[0] - (desde - 1)
    linea = min(usos, key=lambda n: abs((n - offset) - desde))
    largo = hasta - desde
    nuevo_desde = max(1, linea - offset)
    nuevo_hasta = min(len(actual), nuevo_desde + largo)
    aviso = "" if len(usos) == 1 else f" (ancla en {len(usos)} sitios; elegida la más cercana)"
    return f"MOVIDO {desde}-{hasta} → {nuevo_desde}-{nuevo_hasta}{aviso}", (nuevo_desde, nuevo_hasta)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("encuadre")
    ap.add_argument("--raiz", required=True)
    ap.add_argument("--escribir")
    a = ap.parse_args()
    raiz = Path(a.raiz)
    datos = json.loads(Path(a.encuadre).read_text(encoding="utf-8"))
    sello = datos.get("sello_repo", "HEAD")
    cache, cuenta = {}, {"OK": 0, "MOVIDO": 0, "SIN": 0}
    for n, tr in enumerate(datos.get("mapa_de_lectura", []), 1):
        estado, rango = reanclar(tr, raiz, sello, cache)
        if rango:
            tr["desde"], tr["hasta"] = rango
            cuenta["MOVIDO"] += 1
        elif estado == "OK":
            cuenta["OK"] += 1
            continue
        else:
            cuenta["SIN"] += 1
        print(f"[mapa {n}] {estado} · {tr['archivo']} · {tr.get('tema', '')}")
    print(f"RESUMEN: {cuenta['OK']} en su sitio · {cuenta['MOVIDO']} re-anclados · "
          f"{cuenta['SIN']} sin propuesta (sello {sello})")
    if a.escribir:
        Path(a.escribir).write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"escrito: {a.escribir}")


if __name__ == "__main__":
    main()
