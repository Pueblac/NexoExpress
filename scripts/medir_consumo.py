"""Consumo de tokens y llamadas de los agentes de una sesión de Claude Code (kit coordinador v1.6.1).

Lee los registros de los subagentes (~/.claude/projects/<proyecto>/<sesión>/subagents/
agent-<id>.jsonl) y, para cada agente pedido y sus auxiliares (los que lanzó, de forma
recursiva), suma por llamada al modelo: entrada nueva (entrada + escritura de caché),
relectura de caché y salida. Informa también el contexto final, que NO es consumo
(es la cifra que la sesión muestra como «tokens del agente»). Lo que cuesta es la suma de
las llamadas: cada llamada relee todo el contexto, así que un agente con muchas llamadas y
contexto grande consume mucho aunque su contexto final parezca moderado.

Desde v1.4 la cuenta que manda es la de LLAMADAS, contra el tope de cada rol
(`modo_autonomo.topes_llamadas` de coordinador.json): un agente no sabe medir sus tokens, y
también cuenta mal sus llamadas, así que la cifra buena es la de este registro. Si el agentId
se escribe `<agentId>=<rol>`, su fila lleva el tope de ese rol y, si lo pasó, SOBRE TOPE; los
agentes hijos llevan el tope `auxiliar`. Sin `=<rol>`, la fila no lleva tope.

Desde v1.6.1 también se renueva por CONTEXTO: si el contexto final de un agente llega a
`modo_autonomo.reanudar_o_nuevo.renovar_por_contexto` (150 k por defecto; con `null` no se
aplica), su fila lleva RENOVAR y su siguiente turno va en un agente nuevo con su «Nota de
reanudación», aunque no haya llegado a su tope de llamadas: lo que ocurra primero. Medido por
el Director: un Arquitecto que se deja seguir hasta 200 k termina en 250 k y pierde eficiencia.

El directorio de subagentes está en ~/.claude/projects/<carpeta del workspace>/<id de
la sesión>/subagents/. Los agentId son los que devuelve la herramienta Agent.

Uso:
    python -I scripts/medir_consumo.py <dir_subagents> <agentId>[=<rol>] [<agentId>[=<rol>] ...]
    # exit 0 siempre que pudo leer; exit 2 si faltan argumentos
"""
import collections
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HIJO =re.compile(r"agentId: (a[0-9a-f]{16})")
BASE = Path(__file__).resolve().parents[1]
UMBRAL_POR_DEFECTO = 150_000


def leer(f: Path):
    usos, orden, hijos, modelo = {}, [], set(), None
    for linea in f.open(encoding="utf-8", errors="replace"):
        try:
            e = json.loads(linea)
        except json.JSONDecodeError:
            continue
        m = e.get("message") or {}
        if e.get("type") == "assistant" and isinstance(m, dict) and m.get("usage"):
            mid = m.get("id")
            if mid not in usos:
                orden.append(mid)
            usos[mid] = m["usage"]          # el último registro del mensaje trae el uso final
            modelo = m.get("model", modelo)
        if e.get("type") == "user":
            hijos.update(HIJO.findall(linea))
    t = collections.Counter()
    for u in usos.values():
        for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens"):
            t[k] += u.get(k, 0) or 0
    final = usos[orden[-1]] if orden else {}
    ctx = sum(final.get(k, 0) or 0 for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
    return modelo, len(orden), t, ctx, hijos


def topes() -> dict:
    """`modo_autonomo.topes_llamadas` de coordinador.json; vacío si no hay configuración."""
    try:
        cfg = json.loads((BASE / "coordinador.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    t = (cfg.get("modo_autonomo") or {}).get("topes_llamadas") or {}
    return {k: v for k, v in t.items() if not k.startswith("_") and isinstance(v, int)}


def umbral_contexto():
    """`modo_autonomo.reanudar_o_nuevo.renovar_por_contexto`; 150 k si la clave falta, None si vale null."""
    try:
        cfg = json.loads((BASE / "coordinador.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return UMBRAL_POR_DEFECTO
    r = (cfg.get("modo_autonomo") or {}).get("reanudar_o_nuevo") or {}
    if "renovar_por_contexto" not in r:
        return UMBRAL_POR_DEFECTO
    v = r["renovar_por_contexto"]
    return v if isinstance(v, int) and v > 0 else None


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    base = Path(sys.argv[1])
    tope_de = topes()
    umbral = umbral_contexto()
    pendientes = []
    for arg in sys.argv[2:]:
        a, _, rol = arg.partition("=")
        pendientes.append((a, 0, rol or None))
    vistos, total, sobre, renovar = set(), collections.Counter(), [], []
    print(f"{'agente':<22}{'modelo':<20}{'llamadas':>9}{'tope':>6}{'entrada nueva':>15}{'relectura':>13}{'salida':>10}"
          f"{'contexto final':>16}")
    while pendientes:
        a, nivel, rol = pendientes.pop(0)
        if a in vistos:
            continue
        vistos.add(a)
        f = base / f"agent-{a}.jsonl"
        if not f.exists():
            print(f"{'  ' * nivel}{a}: sin registro")
            continue
        modelo, n, t, ctx, hijos = leer(f)
        nueva = t["input_tokens"] + t["cache_creation_input_tokens"]
        total["nueva"] += nueva
        total["relectura"] += t["cache_read_input_tokens"]
        total["salida"] += t["output_tokens"]
        tope = tope_de.get(rol) if rol else (tope_de.get("auxiliar") if nivel else None)
        marca = ""
        if tope is not None and n > tope:
            marca = "  SOBRE TOPE"
            sobre.append(f"{a} ({rol or 'auxiliar'}): {n} llamadas, tope {tope}")
        if umbral is not None and ctx >= umbral:
            marca += "  RENOVAR"
            renovar.append(f"{a} ({rol or 'auxiliar'}): contexto final {ctx:,}, umbral {umbral:,}")
        print(f"{'  ' * nivel + a:<22}{(modelo or '')[:19]:<20}{n:>9}{(tope if tope is not None else '-'):>6}"
              f"{nueva:>15,}{t['cache_read_input_tokens']:>13,}{t['output_tokens']:>10,}{ctx:>16,}{marca}")
        pendientes = [(h, nivel + 1, None) for h in sorted(hijos - vistos)] + pendientes
    print(f"{'TOTAL':<42}{'':>9}{'':>6}{total['nueva']:>15,}{total['relectura']:>13,}{total['salida']:>10,}")
    for s in sobre:
        print(f"SOBRE TOPE {s}: el siguiente turno de ese rol va en un agente nuevo con su Nota de reanudación")
    for s in renovar:
        print(f"RENOVAR {s}: el siguiente turno de ese rol va en un agente nuevo con su Nota de reanudación")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
