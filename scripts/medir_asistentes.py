"""Uso de los asistentes Gemini por los roles de un ciclo (kit coordinador v1.4).

Lo corre el Agente C al cerrar cada ciclo, con `supervision.modo = "asistentes"`. Por cada rol de
`supervision.asistentes.roles` que trabajó en el ciclo (tiene encargo `<dir_encargos>/<ciclo>_<rol>*.txt`
o un plan del ciclo), mide en disco, sin preguntarle al rol:

  · si escribió su Plan de actividades del ciclo (`*plan_actividades*.md` en su `escribe_en`, con
    «ciclo <ciclo>» en la cabecera; formato en `plantillas/asist_plan.md`);
  · cuántas actividades planeó y cuántas se lanzaron de verdad: registros `agy_*.ndjson` en
    `<carpeta_salida>/<ciclo>_<id>/` y la primera línea de su `VEREDICTO.md`;
  · los tokens que gastó Gemini (`total_tokens` del resultado de cada registro);
  · la tabla «Cobertura»: cada tipo de actividad del catálogo (`supervision.asistentes.actividades`)
    con sus actividades o con «Sin asistente: <motivo>».

Imprime una línea INVESTIGAR por cada cosa que no cuadra: rol sin plan, actividad planeada sin
lanzamiento o sin veredicto, tipo del catálogo sin fila en Cobertura o sin motivo. El Agente C
averigua el porqué de cada una y lo anota en la bitácora con SIN_ASISTENTES. Lo que diga el rol
de sí mismo no cuenta: cuenta lo que hay en disco.

KIT COORDINADOR — no hay rutas absolutas: el workspace sale de la ubicación del script.

Uso:
    python -I scripts/medir_asistentes.py <ciclo> [--json]
    # exit 0 = nada que investigar (o el modo no es asistentes); exit 1 = hay líneas INVESTIGAR;
    # exit 2 = uso incorrecto o coordinador.json ilegible
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = Path(__file__).resolve().parents[1]
FILA = re.compile(r"^\|(.+)\|\s*$")
SEPARADOR = re.compile(r"^\|[\s:|-]+\|\s*$")
VEREDICTO = re.compile(r"VEREDICTO\s+\S+\s+\([^)]*\):\s*(ACEPTADO|RECHAZADO|ESCALAR|CUOTA)")
MOTIVO_MIN = 15          # como la «Justificación Argon:» del lanzador: menos que esto no explica nada


def sin_tilde(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower().strip()


def tabla(texto: str, titulo: str) -> list[list[str]]:
    """Filas (sin cabecera ni separador) de la primera tabla bajo `## <titulo>`."""
    filas, dentro, cabecera = [], False, False
    for linea in texto.splitlines():
        if linea.startswith("## "):
            if dentro:
                break
            dentro = sin_tilde(linea[3:]).startswith(sin_tilde(titulo))
            cabecera = False
            continue
        if not dentro:
            continue
        m = FILA.match(linea.strip())
        if not m:
            if filas:
                break
            continue
        if SEPARADOR.match(linea.strip()):
            continue
        if not cabecera:
            cabecera = True
            continue
        filas.append([c.strip() for c in m.group(1).split("|")])
    return filas


def planes_del_ciclo(dir_rol: Path, ciclo: str) -> list[Path]:
    if not dir_rol.is_dir():
        return []
    patron = re.compile(r"ciclo\s+" + re.escape(ciclo) + r"(?![\w.-])", re.IGNORECASE)
    out = []
    for p in sorted(dir_rol.rglob("*plan_actividades*.md")):
        cabeza = "\n".join(p.read_text(encoding="utf-8", errors="replace").splitlines()[:5])
        if patron.search(cabeza):
            out.append(p)
    return out


def tokens(registro: Path) -> int:
    total = 0
    for linea in registro.open(encoding="utf-8", errors="replace"):
        try:
            e = json.loads(linea)
        except json.JSONDecodeError:
            continue
        if isinstance(e, dict) and e.get("event") == "result":
            total = ((e.get("result") or {}).get("usage") or {}).get("total_tokens", 0) or 0
    return total


def medir_rol(rol: str, cfg: dict, ciclo: str, catalogo: list[str], carpeta: Path, encargos: Path) -> dict:
    escribe_en = ((cfg.get("roles") or {}).get(rol) or {}).get("escribe_en") or ""
    planes = planes_del_ciclo(BASE / escribe_en.strip("/"), ciclo) if escribe_en else []
    encargo = sorted(encargos.glob(f"{ciclo}_{rol}*.txt")) if encargos.is_dir() else []
    r = {"rol": rol, "trabajo": bool(encargo or planes), "planes": [p.relative_to(BASE).as_posix() for p in planes],
         "actividades": [], "cobertura": {}, "investigar": []}
    if not r["trabajo"]:
        return r
    if not planes:
        r["investigar"].append(f"{rol}: trabajó en el ciclo {ciclo} y no hay Plan de actividades del ciclo en "
                               f"{escribe_en or '(rol sin escribe_en)'}")
        return r
    vistos = set()
    for plan in planes:
        texto = plan.read_text(encoding="utf-8", errors="replace")
        for f in tabla(texto, "Actividades"):
            if len(f) < 2 or not f[0] or f[0].startswith("<") or f[0] in vistos:
                continue
            vistos.add(f[0])
            d = carpeta / f"{ciclo}_{f[0]}"
            registros = sorted(d.glob("agy_*.ndjson")) if d.is_dir() else []
            ver = "-"
            if (d / "VEREDICTO.md").exists():
                m = VEREDICTO.search((d / "VEREDICTO.md").read_text(encoding="utf-8", errors="replace"))
                ver = m.group(1) if m else "ILEGIBLE"
            a = {"id": f[0], "tipo": f[1], "lanzamientos": len(registros),
                 "tokens_gemini": sum(tokens(x) for x in registros), "veredicto": ver}
            r["actividades"].append(a)
            if not registros:
                r["investigar"].append(f"{rol}: la actividad {f[0]} ({f[1]}) está en el plan y no tiene ningún "
                                       f"lanzamiento en {d.relative_to(BASE).as_posix()}/")
            elif ver == "-":
                r["investigar"].append(f"{rol}: la actividad {f[0]} se lanzó {len(registros)} vez(es) y no tiene "
                                       "VEREDICTO.md del monitor")
        for f in tabla(texto, "Cobertura"):
            if len(f) >= 3 and f[0] and not f[0].startswith("<"):
                r["cobertura"][sin_tilde(f[0])] = (f[1], f[2])
    tipos_con_actividad = {sin_tilde(a["tipo"]) for a in r["actividades"] if a["lanzamientos"]}
    for tipo in catalogo:
        t = sin_tilde(tipo)
        delegado, motivo = r["cobertura"].get(t, ("", ""))
        motivo = re.sub(r"^sin asistente:\s*", "", motivo, flags=re.IGNORECASE)
        if t in tipos_con_actividad or re.search(r"\w", delegado):
            continue                        # lanzada, o planeada sin lanzar (ya va su línea por actividad)
        if t not in r["cobertura"]:
            r["investigar"].append(f"{rol}: {tipo} sin actividad lanzada y sin fila en «Cobertura»")
        elif len(motivo) < MOTIVO_MIN or motivo.startswith("<"):
            r["investigar"].append(f"{rol}: {tipo} sin actividad lanzada y sin motivo en «Cobertura» "
                                   f"(se leyó: {motivo or 'vacío'!r})")
    return r


def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--json"]
    if len(args) != 1:
        print(__doc__)
        return 2
    ciclo = args[0]
    try:
        cfg = json.loads((BASE / "coordinador.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"No se pudo leer {BASE / 'coordinador.json'}: {e}")
        return 2
    sup = cfg.get("supervision") or {}
    if sup.get("modo") != "asistentes":
        print(f"supervision.modo = {sup.get('modo', 'claude_completa')!r}: no aplica (solo mide el modo asistentes).")
        return 0
    asist = sup.get("asistentes") or {}
    roles = [r for r in asist.get("roles") or ["arquitecto"] if not r.startswith("_")]
    catalogo = [k for k in (asist.get("actividades") or {}) if not k.startswith("_")]
    carpeta = BASE / (asist.get("carpeta_salida") or "asistentes/").strip("/")
    encargos = BASE / ((cfg.get("modo_autonomo") or {}).get("dir_encargos") or "coordinacion/encargos/").strip("/")
    resultado = [medir_rol(r, cfg, ciclo, catalogo, carpeta, encargos) for r in roles]
    duenos = {}
    for r in resultado:
        for a in r["actividades"]:
            duenos.setdefault(a["id"], []).append(r["rol"])
    for ident, quienes in sorted(duenos.items()):
        if len(quienes) > 1:
            resultado[roles.index(quienes[0])]["investigar"].append(
                f"el id {ident} está en los planes de {', '.join(quienes)}: comparten {ciclo}_{ident}/ y la medida "
                "no se puede atribuir (los ids llevan el prefijo del rol)")

    if "--json" in sys.argv[1:]:
        print(json.dumps({"ciclo": ciclo, "roles": resultado}, ensure_ascii=False, indent=2))
    else:
        print(f"Uso de asistentes · ciclo {ciclo} · catálogo: {', '.join(catalogo)}")
        print(f"{'rol':<14}{'plan':<6}{'actividades':>12}{'lanzadas':>10}{'lanzamientos':>14}{'aceptadas':>11}"
              f"{'cuota':>7}{'tokens Gemini':>15}")
        for r in resultado:
            if not r["trabajo"]:
                print(f"{r['rol']:<14}(no trabajó en este ciclo)")
                continue
            act = r["actividades"]
            print(f"{r['rol']:<14}{('sí' if r['planes'] else 'NO'):<6}{len(act):>12}"
                  f"{sum(1 for a in act if a['lanzamientos']):>10}{sum(a['lanzamientos'] for a in act):>14}"
                  f"{sum(1 for a in act if a['veredicto'] == 'ACEPTADO'):>11}"
                  f"{sum(1 for a in act if a['veredicto'] == 'CUOTA'):>7}{sum(a['tokens_gemini'] for a in act):>15,}")
            for tipo, (delegado, motivo) in sorted(r["cobertura"].items()):
                motivo = re.sub(r"^sin asistente:\s*", "", motivo, flags=re.IGNORECASE)
                if len(motivo) >= MOTIVO_MIN and not motivo.startswith("<"):
                    print(f"  sin asistente · {tipo}: {motivo[:150]}")
        investigar = [i for r in resultado for i in r["investigar"]]
        for i in investigar:
            print(f"INVESTIGAR {i}")
        if not investigar:
            print("Nada que investigar: cada rol que trabajó tiene plan, sus actividades se lanzaron y lo no "
                  "delegado lleva motivo.")
    return 1 if any(r["investigar"] for r in resultado) else 0


if __name__ == "__main__":
    raise SystemExit(main())
