#!/bin/sh
# Compone el encargo de un rol en modo autónomo: bloque emitido + adenda (kit coordinador v1.4).
# Uso: sh scripts/encargar.sh <ciclo> <rol> "<tarea>" [--insumo <ruta>]
# Deja el encargo en <dir_encargos>/<ciclo>_<rol>.txt e imprime la ruta.
# Rutas: `modo_autonomo.adenda` y `modo_autonomo.dir_encargos` de coordinador.json
# (por defecto coordinacion/adenda_modo_autonomo.txt y coordinacion/encargos/).
#
# El Agente C lanza después al rol como subagente en frío, con el modelo del roster y este
# mensaje mínimo (nada más: todo lo demás está en el encargo):
#   Eres un agente arrancado en frío. Tu arranque completo está en <ruta del encargo>.
#   Léelo íntegro y cúmplelo, incluida la ADENDA final. Nombra tu artefacto <nombre>.
# Si el rol tiene "motor": "agy", la última línea (en stderr) dice cómo lanzarlo con
# scripts/lanzar_agy.py (ver MOTOR_EXTERNO.md).
set -e
BASE="$(cd "$(dirname "$0")/.." && pwd)"
# Intérprete: $PYTHON si está definido; si no, python3 y después python (en Linux suele existir solo python3).
# Se prueba que corra: en Windows, `python3` puede ser el acceso directo de la tienda, que existe y no corre.
if [ -n "$PYTHON" ]; then PY="$PYTHON"
elif python3 -c "" >/dev/null 2>&1; then PY=python3
elif python -c "" >/dev/null 2>&1; then PY=python
else echo "No hay intérprete de Python: instala python3 o define PYTHON=<ruta>" >&2; exit 127; fi
if [ $# -lt 2 ]; then
  echo "Uso: sh scripts/encargar.sh <ciclo> <rol> \"<tarea>\" [--insumo <ruta>]" >&2
  exit 2
fi
ciclo="$1"; rol="$2"; shift 2
leer() {
  "$PY" -I -c "import json,sys; d=json.load(open(sys.argv[1],encoding='utf-8')); print((d.get('modo_autonomo') or {}).get(sys.argv[2]) or sys.argv[3])" \
    "$BASE/coordinador.json" "$1" "$2"
}
adenda="$BASE/$(leer adenda coordinacion/adenda_modo_autonomo.txt)"
encargos="$BASE/$(leer dir_encargos coordinacion/encargos/)"
[ -f "$adenda" ] || { echo "Falta la adenda: $adenda" >&2; exit 1; }
"$PY" "$BASE/scripts/emitir_arranque.py" "$rol" "$@" > /dev/null
mkdir -p "$encargos"
destino="${encargos%/}/${ciclo}_${rol}.txt"
cat "$BASE/bloques/bloque_${rol}.txt" "$adenda" > "$destino"
# v1.4: al final, los límites del encargo que salen de coordinador.json: el tope de llamadas del rol
# (modo_autonomo.topes_llamadas) y, si el rol está en supervision.asistentes.roles con el modo asistentes,
# la obligación del Plan de actividades con su tabla «Cobertura».
"$PY" -I - "$BASE/coordinador.json" "$rol" "$ciclo" >> "$destino" <<'PYEOF'
import json, sys
sys.stdout.reconfigure(encoding="utf-8", newline="\n")
cfg = json.load(open(sys.argv[1], encoding="utf-8"))
rol, ciclo = sys.argv[2], sys.argv[3]
topes = (cfg.get("modo_autonomo") or {}).get("topes_llamadas") or {}
sup = cfg.get("supervision") or {}
asist = sup.get("asistentes") or {}
r = (cfg.get("roles") or {}).get(rol) or {}
lineas = []
if isinstance(topes.get(rol), int):
    t = topes[rol]
    lineas.append(f"- **Tope de llamadas propias: {t}.** Cuenta cada llamada de herramienta, también las de lectura. "
                  "Tu cuenta se queda corta (medido: un Ingeniero dijo «unas 25» y el registro tenía 64): escribe tu "
                  f"«Nota de reanudación» cuando creas ir por unas {t * 2 // 3} y, al llegar a {t}, termina con "
                  "`TOPE: <n> llamadas · <ruta de la nota>`. Quien coordina cuenta tus llamadas en el registro "
                  "(`scripts/medir_consumo.py`), no en lo que digas.")
if isinstance(topes.get("auxiliar"), int):
    lineas.append(f"- **Auxiliares y monitores que lances: tope de {topes['auxiliar']} llamadas cada uno.** "
                  "Escríbeselo en su encargo, con la misma regla de la nota.")
if sup.get("modo") == "asistentes" and rol in (asist.get("roles") or []):
    tipos = ", ".join(k for k in (asist.get("actividades") or {}) if not k.startswith("_"))
    dir_pl = ((cfg.get("proyecto") or {}).get("dir_plantillas") or "docs/prompts_arranque").strip("/")
    lineas.append(f"- **Modo asistentes, obligatorio para este rol.** Antes de tu artefacto escribe tu Plan de "
                  f"actividades del ciclo {ciclo} en {r.get('escribe_en', 'tu directorio')} (plantilla "
                  f"`{dir_pl}/asist_plan.md`, con «ciclo {ciclo}» en la cabecera). Su tabla «Cobertura» lleva una "
                  f"fila por tipo ({tipos}): las actividades que delegas, o «Sin asistente: <motivo concreto>». Lo "
                  "mecánico va primero a un asistente Gemini con su monitor de Claude; un auxiliar de Claude solo para "
                  "lo que el catálogo no cubre o lo que quedó en CUOTA. Al cerrar el ciclo, el Agente C mide en disco "
                  f"qué se lanzó (`scripts/medir_asistentes.py {ciclo}`) e investiga cada tipo sin actividad y sin motivo.")
if lineas:
    print("\n# LÍMITES DE ESTE ENCARGO (los escribe scripts/encargar.sh desde coordinador.json)\n")
    print("\n".join(lineas))
PYEOF
echo "$destino"
# v1.3: un rol con motor agy no se lanza como subagente sino con el lanzador; el sello del
# bloque ya lleva su modelo_agy. La línea va a stderr para no romper a quien lee la ruta.
motor="$("$PY" -I -c "import json,sys; r=(json.load(open(sys.argv[1],encoding='utf-8')).get('roles') or {}).get(sys.argv[2]) or {}; print(r.get('motor') or 'claude', (r.get('escribe_en') or '').strip('/'), sep='|')" "$BASE/coordinador.json" "$rol")"
case "$motor" in
  agy\|*) echo "Motor agy: $PY -I scripts/lanzar_agy.py $rol ${destino#"$BASE"/} --salida ${motor#agy|}/<carpeta>" >&2 ;;
esac
