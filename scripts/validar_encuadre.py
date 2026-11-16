"""Valida una ficha de encuadre contra el disco. Esqueleto genérico del kit (v1.2).

KIT COORDINADOR — el eslabón 2 de la cadena: un script determinista que mide lo
que el Guionista declaró, ANTES de que el Arquitecto decida sobre ello. Que no
sea un modelo es el punto entero: un script no puede compartir el punto ciego
del modelo que escribió la ficha, porque no razona.

POR QUÉ VIAJA CON EL KIT (cambio de postura, v1.1): la v1.0 declaraba el
validador completo como no-exportable, confiando en que cada coordinador lo
escribiría "por acumulación" desde su primera ficha real. En la primera
instalación real, tras DIEZ fichas reales, seguía sin existir: "por acumulación"
sin fecha ni dueño resultó significar "nunca", y el Arquitecto quedó midiendo a
mano la misma ficha sobre la que después decidía. Este esqueleto implementa lo
que SÍ es genérico y deja al dominio únicamente lo que le corresponde: qué
archivos, qué llaves y qué columnas declara cada ficha.

QUÉ AÑADE v1.2 (traído de un coordinador cuyo dominio no era tabular):
  · dos pruebas que sirven a cualquier dominio, también sin tablas:
    `archivo_existe` (la única que admite declarar una AUSENCIA) y
    `ocurrencias_en_archivo` (cuenta OCURRENCIAS, no líneas: la lección del
    `grep -c`);
  · la validación del `mapa_de_lectura`: cada tramo debe existir, caber en su
    archivo y contener su ancla literal. El mapa es la frontera del Arquitecto
    (ver `MODO_AUTONOMO.md`), así que un tramo que no cuadra tumba la ficha
    igual que una afirmación falsa;
  · una ficha que no es JSON sale como FICHA INVÁLIDA con exit=1, no con traza;
  · pandas solo se carga si alguna afirmación es tabular.
Un dominio con otras pruebas (escenas, configuraciones, comandos) escribe un
HERMANO local de este script que conserve el contrato, la salida
declarado-vs-medido, el mapa y el fail-closed; este archivo no se edita.

CONTRATO DE LA FICHA (lo que este script exige para poder medir):

    {
      "sello_repo": "<commit del repositorio medido; opcional, lo usa reanclar_tramos.py>",
      "insumos": [ {"id": "a", "ruta": "carpeta/archivo.ext", "hoja": null},
                   {"id": "s", "ruta": "src/limpieza.py"} ],
      "afirmaciones_verificables": [
        {"id": 1, "prueba": "existencia_y_conteo",      "insumo": "a",
         "filas": 17009, "columnas": 12},
        {"id": 2, "prueba": "unicidad_y_cardinalidad",  "insumo": "a",
         "llave": ["col1", "col2"], "duplicados": 0},
        {"id": 3, "prueba": "dominio_de_columna",       "insumo": "a",
         "columna": "estado", "n_distintos": 5, "conteos": {"120": 41}},
        {"id": 4, "prueba": "columnas_vs_contrato",     "insumo": "a",
         "columnas": ["col1", "col2", "col3"]},
        {"id": 5, "prueba": "archivo_existe",
         "ruta": "salidas/tabla_final.csv", "existe": false},
        {"id": 6, "prueba": "ocurrencias_en_archivo",   "insumo": "s",
         "patron": "def normalizar_folio", "ocurrencias": 1}
      ],
      "mapa_de_lectura": [
        {"tema": "normalización de folios", "archivo": "src/limpieza.py",
         "desde": 40, "hasta": 62, "ancla": "def normalizar_folio"}
      ]
    }

Una afirmación que no calce en los seis tipos no va como afirmación: va en
`notas` de la ficha, y este script la ignora. Un insumo declarado que no exista
en disco hace fallar la ficha ENTERA: despachar una orden sobre premisas que
apuntan a archivos fantasma es la forma más barata de fabricar una alucinación.

Uso:
    python scripts/validar_encuadre.py <ficha.json> --raiz <dir> [--raiz <dir2>]
    # exit 0 = todas las afirmaciones y tramos cuadran; exit 1 = alguno falla (fail-closed)

La salida es el diff analítico declarado-vs-medido, afirmación por afirmación.
Se pega TAL CUAL en el expediente (`... | tee salida_validacion.txt`).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TABULARES = ("existencia_y_conteo", "unicidad_y_cardinalidad",
             "dominio_de_columna", "columnas_vs_contrato")
DE_TEXTO = ("ocurrencias_en_archivo",)
SIN_INSUMO = ("archivo_existe",)
PRUEBAS = TABULARES + DE_TEXTO + SIN_INSUMO


def leer_tabla(ruta: Path, hoja=None):
    """Carga el insumo con pandas. Separador por extensión; .tab/.tsv = tabulador."""
    try:
        import pandas as pd
    except ImportError:
        raise SystemExit("Falta pandas: la ficha trae pruebas tabulares y el "
                         "validador no puede medir tablas sin leerlas. "
                         "Instálelo en el entorno del coordinador.")
    ext = ruta.suffix.lower()
    if ext in (".xlsx", ".xls"):
        return pd.read_excel(ruta, sheet_name=hoja or 0)
    if ext == ".parquet":
        return pd.read_parquet(ruta)
    if ext == ".json":
        return pd.read_json(ruta)
    sep = "\t" if ext in (".tab", ".tsv", ".txt") else ","
    return pd.read_csv(ruta, sep=sep, dtype=str, keep_default_na=True,
                       low_memory=False)


def resolver_insumo(ruta_decl: str, raices: list[Path]) -> Path | None:
    """Busca la ruta declarada bajo cada raíz autorizada, en orden."""
    if not ruta_decl:
        return None
    p = Path(ruta_decl)
    if p.is_absolute():
        return p if p.exists() else None
    for raiz in raices:
        cand = (raiz / p)
        if cand.exists():
            return cand
    return None


def medir_sin_tabla(af: dict, ruta: Path | None, raices: list[Path]) -> tuple[bool, str]:
    """Pruebas que no necesitan pandas."""
    prueba = af.get("prueba")
    if prueba == "archivo_existe":
        if not af.get("ruta") or not isinstance(af.get("ruta"), str) or not isinstance(af.get("existe"), bool):
            return False, ("la prueba exige `ruta` (texto) y `existe` (true/false): "
                           f"ruta={af.get('ruta')!r} · existe={af.get('existe')!r}")
        medido = resolver_insumo(af["ruta"], raices) is not None
        ok = af["existe"] == medido
        return ok, (f"ruta={af.get('ruta')!r} · declarado existe={af.get('existe')} · "
                    f"medido existe={medido}")
    if prueba == "ocurrencias_en_archivo":
        patron = af.get("patron")
        if not patron:
            return False, "falta `patron`"
        medido = ruta.read_text(encoding="utf-8", errors="replace").count(patron)
        return af.get("ocurrencias") == medido, (
            f"patron={patron!r} · declarado ocurrencias={af.get('ocurrencias')} · "
            f"medido ocurrencias={medido}")
    raise ValueError(prueba)


def medir(af: dict, df) -> tuple[bool, str]:
    """Ejecuta UNA afirmación tabular contra el DataFrame. Sin criterio propio:
    lo declarado se compara con lo medido y se reporta la cifra, cuadre o no."""
    prueba = af.get("prueba")

    if prueba == "existencia_y_conteo":
        filas, cols = len(df), len(df.columns)
        ok = (af.get("filas") in (None, filas)) and (af.get("columnas") in (None, cols))
        return ok, (f"declarado filas={af.get('filas')} columnas={af.get('columnas')} · "
                    f"medido filas={filas} columnas={cols}")

    if prueba == "unicidad_y_cardinalidad":
        llave = af.get("llave") or []
        llave = [llave] if isinstance(llave, str) else list(llave)
        faltan = [c for c in llave if c not in df.columns]
        if faltan:
            return False, f"la llave declarada no existe en el insumo: {faltan}"
        dup = int(df.duplicated(subset=llave).sum())
        ok = af.get("duplicados") in (None, dup)
        return ok, (f"llave={llave} · declarado duplicados={af.get('duplicados')} · "
                    f"medido duplicados={dup} sobre {len(df)} filas")

    if prueba == "dominio_de_columna":
        col = af.get("columna")
        if col not in df.columns:
            return False, f"la columna declarada no existe: {col!r}"
        vc = df[col].value_counts(dropna=True)
        nd = int(vc.size)
        ok = af.get("n_distintos") in (None, nd)
        detalle = [f"declarado n_distintos={af.get('n_distintos')} · medido n_distintos={nd}"]
        for valor, esperado in (af.get("conteos") or {}).items():
            medido = int(vc.get(valor, vc.get(str(valor), 0)))
            cuadra = (esperado == medido)
            ok = ok and cuadra
            detalle.append(f"conteo[{valor!r}] declarado={esperado} medido={medido}")
        return ok, " · ".join(detalle)

    if prueba == "columnas_vs_contrato":
        declaradas = list(af.get("columnas") or [])
        presentes = list(df.columns)
        faltan = [c for c in declaradas if c not in presentes]
        sobran = [c for c in presentes if c not in declaradas]
        ok = not faltan and (not sobran or af.get("permite_extras", False))
        return ok, (f"declaradas={len(declaradas)} presentes={len(presentes)} · "
                    f"faltan={faltan or 0} · extras={sobran or 0}")

    raise ValueError(prueba)


def validar_mapa(mapa: list, raices: list[Path]) -> int:
    """Cada tramo debe existir, caber en su archivo y contener su ancla literal."""
    fallas = 0
    for n, tr in enumerate(mapa, 1):
        tr = tr if isinstance(tr, dict) else {}
        p = resolver_insumo(tr.get("archivo", ""), raices)
        desde, hasta, ancla = tr.get("desde"), tr.get("hasta"), tr.get("ancla", "")
        if not p or not p.is_file():
            ok, detalle = False, f"{tr.get('archivo')!r}: archivo no existe"
        elif not (isinstance(desde, int) and isinstance(hasta, int) and 1 <= desde <= hasta):
            ok, detalle = False, f"tramo inválido {desde}..{hasta}"
        else:
            lineas = p.read_text(encoding="utf-8", errors="replace").splitlines()
            texto = "\n".join(lineas[desde - 1:hasta])
            presente = bool(ancla) and ancla in texto
            ok = hasta <= len(lineas) and presente
            detalle = (f"{tr.get('archivo')}:{desde}-{hasta} de {len(lineas)} líneas, "
                       f"ancla {'presente' if presente else 'AUSENTE'}")
        fallas += 0 if ok else 1
        print(f"  [mapa {n}] {'OK   ' if ok else 'FALLA'} · {tr.get('tema', '')} · {detalle}")
    if mapa:
        print(f"MAPA DE LECTURA: {len(mapa) - fallas}/{len(mapa)} tramos cuadran")
    return fallas


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("ficha", help="Ruta a la ficha de encuadre (.json)")
    ap.add_argument("--raiz", action="append", required=True, metavar="DIR",
                    help="Raíz bajo la que resolver rutas relativas de insumos "
                         "(repetible; en el coordinador salen de "
                         "`.claude/settings.json`)")
    args = ap.parse_args()

    raices = [Path(r) for r in args.raiz]
    ficha_p = Path(args.ficha)
    if not ficha_p.exists():
        raise SystemExit(f"La ficha no existe: {ficha_p}")
    try:
        ficha = json.loads(ficha_p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"RESULTADO: FICHA INVÁLIDA — no es JSON (línea {e.lineno}): {e.msg}")
        return 1

    insumos_decl = {i.get("id"): i for i in (ficha.get("insumos") or [])
                    if isinstance(i, dict)}
    afirmaciones = ficha.get("afirmaciones_verificables") or []
    print(f"== validar_encuadre · {ficha_p.name} · {len(insumos_decl)} insumos "
          f"declarados · {len(afirmaciones)} afirmaciones ==")

    # 1) Todo insumo declarado debe existir; uno ausente tumba la ficha entera.
    rutas, ausentes = {}, []
    for iid, ins in insumos_decl.items():
        p = resolver_insumo(ins.get("ruta", ""), raices)
        (rutas.__setitem__(iid, p) if p else ausentes.append((iid, ins.get("ruta"))))
        print(f"  insumo {iid}: {ins.get('ruta')} -> {p if p else 'NO EXISTE'}")
    if ausentes:
        print(f"RESULTADO: FICHA INVÁLIDA — {len(ausentes)} insumo(s) declarados "
              f"no existen en disco: {ausentes}")
        return 1

    # 2) Diff analítico declarado-vs-medido, afirmación por afirmación.
    fallas = 0
    cache = {}
    for af in afirmaciones:
        prueba, iid = af.get("prueba"), af.get("insumo")
        if prueba not in PRUEBAS:
            ok, detalle = False, (
                f"tipo de prueba desconocido: {prueba!r}. Los tipos admitidos son "
                + ", ".join(PRUEBAS) + ". No se inventan tipos nuevos: lo que no "
                "calce va en `notas` de la ficha.")
        elif prueba not in SIN_INSUMO and iid not in rutas:
            ok, detalle = False, f"afirmación apunta a insumo inexistente en la ficha: {iid!r}"
        else:
            try:
                if prueba in TABULARES:
                    if iid not in cache:
                        cache[iid] = leer_tabla(rutas[iid], insumos_decl[iid].get("hoja"))
                    ok, detalle = medir(af, cache[iid])
                else:
                    ok, detalle = medir_sin_tabla(af, rutas.get(iid), raices)
            except SystemExit:
                raise
            except Exception as e:        # una medición que revienta no cuadra
                ok, detalle = False, f"error al medir: {e}"
        fallas += (0 if ok else 1)
        print(f"  [{af.get('id')}] {'OK   ' if ok else 'FALLA'} · {prueba} · {detalle}")

    # 3) Mapa de lectura (v1.2): la frontera de lectura del Arquitecto.
    mapa = ficha.get("mapa_de_lectura") or []
    fallas_mapa = validar_mapa(mapa, raices)

    total = len(afirmaciones)
    malas = fallas + fallas_mapa
    print(f"RESULTADO: {total - fallas}/{total} afirmaciones cuadran"
          + (f" · mapa {len(mapa) - fallas_mapa}/{len(mapa)}" if mapa else "")
          + ("" if not malas else f" · {malas} FALLA(S) — la ficha vuelve al "
             "Guionista (máximo 3 intentos; el diff de arriba es su insumo)"))
    return 0 if malas == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
