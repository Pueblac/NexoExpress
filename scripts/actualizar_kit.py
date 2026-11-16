"""Actualiza en sitio un coordinador que ya tiene instalada una versión anterior del kit (kit coordinador v1.6.0).

Lo corre el instalador en el PASO 0 cuando `detectar_metodologia.py` encuentra una versión
anterior del kit. Hace lo mecánico de la actualización y deja escrito lo que necesita criterio:

  · Cada pieza del kit (scripts, plantillas de rol, hook) se compara con la versión del kit
    desde la que se instaló, guardada en `anteriores/<versión>/`. Esa base permite separar lo
    que cambió el proyecto de lo que cambió el kit:
      NUEVO       la pieza no está en el proyecto: se copia.
      IGUAL       ya es la del kit nuevo: no se toca.
      REEMPLAZAR  el proyecto no la había cambiado: se sustituye por la nueva.
      FUSIONAR    los dos la cambiaron en sitios distintos: fusión a tres bandas
                  (`git merge-file`) sin conflictos; se escribe la fusión.
      REVISAR     los dos cambiaron lo mismo, o no hay base: la pieza del proyecto NO se toca
                  y la propuesta (con marcas <<<<<<< proyecto / >>>>>>> kit) queda en
                  `<respaldo>/propuestas/` para resolverla con el Director.
      OMITIR      plantilla de un rol que el proyecto no usa (lo quitó a propósito).
      CONSERVAR   pieza propia del proyecto (rol local, validador hermano, herramienta ya
                  rellenada): no se toca.
      NO APLICA   pieza del motor externo (v1.3) que el proyecto no usa: capas agy_*.md si
                  ningún rol declara "motor": "agy" ni el modo es "asistentes"; plantillas asist_*.md
                  (v1.3.2) si el modo no es "asistentes"; herramienta_segura.py si nadie la usa.
  · Piezas de la v1.3: `agy_capa.md`, `agy_roles.md` y `agy_sub_*.md` NO son plantillas de rol;
    se copian al directorio de plantillas solo si algún rol declara "motor": "agy". La
    `herramienta_segura.py` va a `scripts/` solo si un rol la usa en `comandos_agy`, y una ya
    rellenada no se sobrescribe nunca. `emitir_agy.py` y `lanzar_agy.py` se añaden como cualquier script.
  · Piezas de la v1.3.2 (modo «asistentes»): `asist_plan.md`, `asist_encargo_asistente.md` y
    `asist_encargo_monitor.md` son plantillas del modo, no de un rol: se copian al directorio de
    plantillas solo si `supervision.modo` es "asistentes". Una `herramienta_segura.py` ya rellenada no
    se toca, pero si no trae los subcomandos nuevos (`sello`, `sello-repo`, `mutar`, `poner`) el plan
    lo avisa en una nota con qué copiar del esqueleto del kit.
  · `coordinador.json` se fusiona clave por clave con la misma lógica: entra lo nuevo del kit
    (kit_version, roles y secciones nuevas, reglas nuevas), se actualiza lo que el proyecto no
    había cambiado, y lo que el proyecto cambió se conserva. Lo que choca se queda como está
    el proyecto y se lista para revisar. Los roles que el proyecto quitó no vuelven. De la 1.2
    a la 1.3 entran `supervision` (modo claude_completa por defecto), `motor` de cada rol, el
    guardrail `supervision_claude` y `kit_version`; la base es `anteriores/1.2/` (o `1.1/`).
    Desde la 1.4 el kit trae `supervision.modo = "asistentes"`: un proyecto que seguía en el
    `claude_completa` de fábrica pasa a `asistentes`, y el plan lo avisa en una nota; uno que eligió
    otro modo lo conserva, y el plan dice cómo pasarlo. Entran `modo_autonomo.topes_llamadas` y las
    etiquetas TOPE, MANUAL y SIN_ASISTENTES; `orientacion_llamadas_propias` queda como choque (el kit ya
    no la trae: la retira el Director).
  · `--modo autonomo` es el valor por defecto desde la 1.4: entran el rol `coordinador` y la sección
    `modo_autonomo`, y se copian la adenda y la instrucción del Director si faltan. `--modo manual`
    (solo si el Director lo pide para todo el proyecto) no los añade.
  · Un ciclo que empezó con una versión del kit termina con esa versión (v1.4.2,
    `modo_autonomo.cambio_de_version`). El ciclo más reciente es el del encargo con el commit más nuevo
    (o, sin commit, la fecha del archivo). Si no tiene todavía su ficha de cierre en la carpeta del
    Archivista (`ciclos/<ciclo>.md`, `historias/<ciclo>.md` u otra subcarpeta), el plan lo avisa con las
    rutas que buscó y `--aplicar` se niega (exit 3): se termina ese ciclo y después se actualiza. Dos
    excepciones, que quedan escritas en la nota de migración: `--ciclo-cerrado` (el Director confirma
    que el ciclo ya cerró y solo falta la ficha) y `--autoriza-director "<motivo>"` (el Director decide
    actualizar a mitad de ciclo, con el motivo).
  · Informes (v1.6): `estandar_documental.md` no es una plantilla de rol. Se copia a `informes.estandar`
    (por defecto `docs/estandar_documental.md`) si falta; si ya está, es del proyecto y no se pisa.
    `renderizar_informe.py` y `verificar_informe.py` entran como cualquier script: si el proyecto ya
    tenía un `renderizar_informe.py` propio, sale REVISAR. El plan avisa si falta la plantilla .docx y
    si la adenda o la instrucción del Director no traen todavía la regla de informes.
  · Renovar por contexto (v1.6.1): el plan avisa si la instrucción del Director no trae todavía la
    frase del punto 3 (contexto final de 150 k, RENOVAR en medir_consumo.py); la clave
    `modo_autonomo.reanudar_o_nuevo.renovar_por_contexto` entra con la fusión de coordinador.json.
  · Repositorio igual al workspace (v1.6.2): el plan avisa si los permisos de agy generados antes le niegan
    escribir a todo el repositorio, y pide regenerarlos con `emitir_agy.py`.
  · bloques/ en el .gitignore (v1.6.3): si el proyecto ya decidió sobre `bloques/` (una línea del .gitignore
    que lo menciona, regla, negación o comentario, o archivos de `bloques/` versionados), se respeta (CONSERVAR).

Sin `--aplicar` solo imprime el plan y no escribe nada. Con `--aplicar`, antes de escribir
respalda cada archivo que va a cambiar en `respaldo_metodologia_<fecha>/` (misma estructura
de rutas, con MANIFIESTO.sha256) y comprueba las copias por huella; si una no cuadra, no
escribe nada. Al terminar deja la nota de migración en `docs/migracion_kit_<versión>_<fecha>.md`.
NUNCA BORRA: lo que el kit ya no trae, o lo que conviene retirar, se informa y lo decide el
Director.

Uso:
    python3 -I kit_coordinador/scripts/actualizar_kit.py <destino>                      # plan
    python3 -I kit_coordinador/scripts/actualizar_kit.py <destino> --aplicar [--modo manual]
    # exit 0 = plan impreso o actualización hecha (las piezas REVISAR quedan listadas);
    # exit 1 = el respaldo no cuadró y no se escribió nada; exit 2 = destino sin kit instalado;
    # exit 3 = hay un ciclo en curso: no se escribió nada (se termina el ciclo primero)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KIT = Path(__file__).resolve().parents[1]
ANTERIORES = KIT / "anteriores"
EJEMPLO = json.loads((KIT / "coordinador.example.json").read_text(encoding="utf-8"))
VERSION = EJEMPLO.get("kit_version", "?")
DIR_PLANTILLAS_POR_DEFECTO = "docs/prompts_arranque"
SOLO_AUTONOMO = [("roles", "coordinador"), ("modo_autonomo",)]
SIEMPRE_LF = {".sh"}
CICLOS_DE_PRUEBA = {"HUMO", "PRUEBA", "VACIO"}
LOCALES_DEL_ROL = {"modelo", "orden"}
FALTA = object()


def v_tupla(v: str) -> tuple:
    return tuple(int(x) for x in re.findall(r"\d+", v)[:3])


def huella(b: bytes) -> str:
    return hashlib.sha256(b.replace(b"\r\n", b"\n")).hexdigest()


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def es_crlf(b: bytes) -> bool:
    return b"\r\n" in b


def a_lf(b: bytes) -> bytes:
    return b.replace(b"\r\n", b"\n")


def con_fin(b: bytes, crlf: bool) -> bytes:
    b = a_lf(b)
    return b.replace(b"\n", b"\r\n") if crlf else b


def fusion3(local: bytes, base: bytes, nuevo: bytes, etiqueta_base: str) -> tuple[bytes | None, int]:
    """Fusión a tres bandas con `git merge-file`. Devuelve (texto, n_conflictos); texto None si no hay git."""
    if not shutil.which("git"):
        return None, -1
    with tempfile.TemporaryDirectory() as td:
        rutas = []
        for nombre, b in (("proyecto", local), ("base", base), ("kit", nuevo)):
            p = Path(td) / nombre
            p.write_bytes(a_lf(b))
            rutas.append(str(p))
        r = subprocess.run(["git", "merge-file", "-p", "-L", "proyecto", "-L", etiqueta_base,
                            "-L", f"kit_{VERSION}", *rutas], capture_output=True)
    if r.returncode < 0:
        return None, -1
    return r.stdout, r.returncode


# ---------------------------------------------------------------- coordinador.json

def _insertar(orden: list, clave, nuevo_orden: list):
    """Inserta `clave` en `orden` justo después de la clave que la precede en `nuevo_orden`."""
    i = nuevo_orden.index(clave)
    for previa in reversed(nuevo_orden[:i]):
        if previa in orden:
            orden.insert(orden.index(previa) + 1, clave)
            return
    orden.insert(0, clave)


def _corto(v) -> str:
    s = json.dumps(v, ensure_ascii=False)
    return s if len(s) <= 90 else s[:87] + "…"


def fusionar_json(local, base, nuevo, ruta, cambios, choques):
    """Fusión a tres bandas de valores JSON. Devuelve el valor resultante (o FALTA si no queda)."""
    if local == nuevo:
        return local
    if local == base:                       # el proyecto no lo tocó: manda el kit
        etiqueta = "retirado" if nuevo is FALTA else ("añadido" if local is FALTA else "actualizado")
        if etiqueta == "retirado":         # NUNCA se borra en silencio: se informa
            choques.append((ruta, "el kit nuevo ya no trae esta clave; se conserva (decide el Director)",
                            local, nuevo))
            return local
        cambios.append((ruta, etiqueta, nuevo))
        return nuevo
    if nuevo == base:                       # el kit no lo cambió: manda el proyecto
        return local
    if len(ruta) == 3 and ruta[0] == "roles" and ruta[2] in LOCALES_DEL_ROL and local is not FALTA:
        return local                        # roster y orden de la cadena: siempre del proyecto
    if isinstance(local, dict) and isinstance(nuevo, dict) and isinstance(base, dict):
        orden = list(local)
        for k in nuevo:
            if k not in orden and k not in base:
                _insertar(orden, k, list(nuevo))
        out = {}
        for k in orden:
            r = fusionar_json(local.get(k, FALTA), base.get(k, FALTA), nuevo.get(k, FALTA),
                              ruta + [k], cambios, choques)
            if r is not FALTA:
                out[k] = r
        return out
    if local is FALTA:                      # el proyecto lo quitó y el kit lo cambió: sigue fuera
        choques.append((ruta, "el proyecto quitó esta clave y el kit la cambió; sigue fuera", local, nuevo))
        return FALTA
    choques.append((ruta, "el proyecto y el kit la cambiaron distinto; se conserva la del proyecto", local, nuevo))
    return local


def sangria(texto: str) -> int:
    for linea in texto.splitlines()[1:]:
        if linea.strip():
            return len(linea) - len(linea.lstrip(" ")) or 2
    return 2


# ---------------------------------------------------------------- plan

class Plan:
    def __init__(self, destino: Path, base_ver: str, modo: str | None):
        self.destino = destino
        self.base_ver = base_ver
        self.modo = modo
        self.filas = []        # (grupo, rel, accion, detalle)
        self.escrituras = {}   # rel -> (bytes, modo_ejecutable)
        self.propuestas = {}   # rel -> bytes
        self.dirs = []         # directorios a crear (rel)
        self.notas = []
        self.choques_cfg = []
        self.cambios_cfg = []
        self.ciclo = None          # lo que devuelve ciclo_en_curso()
        self.ciclo_abierto = None  # el mismo dict, solo si el ciclo más reciente no tiene ficha de cierre
        self.excepcion_ciclo = None  # texto de la excepción del Director, para la nota de migración

    def add(self, grupo, rel, accion, detalle, escribir: bytes | None = None, ejecutable=False, propuesta=None):
        self.filas.append((grupo, rel, accion, detalle))
        if escribir is not None:
            self.escrituras[rel] = (escribir, ejecutable)
        if propuesta is not None:
            self.propuestas[rel] = propuesta


def pieza(plan: Plan, grupo: str, rel: str, kit_p: Path, base_p: Path | None, ejecutable=False):
    """Decide qué hacer con una pieza del kit que corresponde a `rel` en el destino."""
    dst = plan.destino / rel
    nuevo = kit_p.read_bytes()
    lf = kit_p.suffix in SIEMPRE_LF or ejecutable
    if not dst.exists():
        plan.add(grupo, rel, "NUEVO", "no estaba en el proyecto", nuevo, ejecutable)
        return
    local = dst.read_bytes()
    crlf = es_crlf(local) and not lf
    if huella(local) == huella(nuevo):
        if ejecutable and not os.access(dst, os.X_OK):
            plan.add(grupo, rel, "REEMPLAZAR", "igual al del kit nuevo pero sin modo ejecutable", local, True)
        else:
            plan.add(grupo, rel, "IGUAL", f"ya es la del kit {VERSION}")
        return
    base = base_p.read_bytes() if base_p and base_p.exists() else None
    if base is not None and huella(local) == huella(base):
        plan.add(grupo, rel, "REEMPLAZAR", f"sin cambios locales sobre el kit {plan.base_ver}",
                 con_fin(nuevo, crlf), ejecutable)
        return
    if base is None:
        plan.add(grupo, rel, "REVISAR", "distinta del kit y sin base para fusionar: la propuesta es la del kit "
                 "nuevo entera; compárala con la del proyecto", propuesta=con_fin(nuevo, crlf))
        return
    texto, n = fusion3(local, base, nuevo, f"kit_{plan.base_ver}")
    if texto is None:
        plan.add(grupo, rel, "REVISAR", "adaptada localmente y sin git para fusionar: la propuesta es la del kit "
                 "nuevo entera", propuesta=con_fin(nuevo, crlf))
    elif n == 0:
        if huella(texto) == huella(local):
            plan.add(grupo, rel, "IGUAL", "adaptada localmente; el kit no cambió esta pieza: se conserva")
        else:
            plan.add(grupo, rel, "FUSIONAR", "adaptada localmente; fusión a tres bandas sin conflictos",
                     con_fin(texto, crlf), ejecutable)
    else:
        plan.add(grupo, rel, "REVISAR", f"adaptada localmente; {n} conflicto(s) en la fusión: la del proyecto "
                 "no se toca", propuesta=con_fin(texto, crlf))


def es_plantilla_agy(stem: str) -> bool:
    return stem in ("agy_capa", "agy_roles") or stem.startswith("agy_sub_")


def es_plantilla_informes(stem: str) -> bool:
    """El estándar documental (v1.6) no es plantilla de rol: va a `informes.estandar`."""
    return stem == "estandar_documental"


def es_plantilla_asistentes(stem: str) -> bool:
    """Plantillas del modo «asistentes» (v1.3.2): plan, encargo del asistente y encargo del monitor."""
    return stem.startswith("asist_")


SUBCOMANDOS_NUEVOS = ("sello", "sello-repo", "mutar", "poner")   # herramienta_segura.py, v1.3.2


def buscar(raiz: Path, patron: str, prof: int, excluir: set) -> list[Path]:
    out = []
    for p in raiz.rglob(patron):
        rel = p.relative_to(raiz).parts
        if len(rel) <= prof and not (set(rel) & excluir) and not rel[0].startswith("respaldo_metodologia_"):
            out.append(p)
    return sorted(out)


def fechas_de_commit(destino: Path, carpeta: Path) -> dict[str, float]:
    """Fecha del último commit de cada archivo de `carpeta` (ruta relativa al proyecto -> segundos). Vacío sin git."""
    if not shutil.which("git") or not (destino / ".git").exists():
        return {}
    r = subprocess.run(["git", "-C", str(destino), "-c", "core.quotepath=off", "log", "--format=@%ct", "--name-only",
                        "--", carpeta.relative_to(destino).as_posix()],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    fechas, t = {}, None
    for linea in r.stdout.splitlines():
        if linea.startswith("@"):
            t = float(linea[1:])
        elif linea.strip() and t is not None:
            fechas.setdefault(linea.strip(), t)     # git log va del más nuevo al más viejo: el primero manda
    return fechas


def ciclo_en_curso(destino: Path, cfg: dict) -> dict | None:
    """El ciclo del encargo más reciente y si tiene la ficha de cierre del Archivista (v1.4.2); None si no hay cómo saberlo.

    Un ciclo que empezó con una versión del kit termina con esa versión: la nueva se integra entre ciclos. Solo se
    mira el ciclo más reciente, para que los ciclos viejos que nunca se archivaron no cuenten. «Más reciente» es por
    la fecha del último commit del encargo; un encargo sin commit (aún no versionado) cuenta por la fecha del archivo.
    La ficha se busca en la carpeta real del Archivista (su `escribe_en`): en `ciclos/<ciclo>.md`,
    `historias/<ciclo>.md` o cualquier otra subcarpeta directa. Sin directorio de encargos o sin Archivista no hay
    cómo saberlo, y no se avisa.

    Devuelve {"ciclo", "n" (encargos del ciclo), "criterio", "buscadas" (rutas), "ficha" (ruta hallada o None)}."""
    auto = cfg.get("modo_autonomo") or {}
    roles = {r: c for r, c in (cfg.get("roles") or {}).items() if not r.startswith("_")}
    d_enc = destino / (auto.get("dir_encargos") or "coordinacion/encargos/").strip("/")
    if not d_enc.is_dir() or "archivista" not in roles:
        return None
    nombres = sorted(roles, key=len, reverse=True)
    patron = re.compile(r"^(.+?)_(?:" + "|".join(map(re.escape, nombres)) + r")(?:_[^/]*)?\.txt$")
    commits = fechas_de_commit(destino, d_enc)
    encargos = []
    for f in d_enc.glob("*.txt"):
        m = patron.match(f.name)
        if m and m.group(1).upper() not in CICLOS_DE_PRUEBA:
            t = commits.get(f.relative_to(destino).as_posix())
            encargos.append((t if t is not None else f.stat().st_mtime, t is not None, m.group(1)))
    if not encargos:
        return None
    _, por_commit, ciclo = max(encargos)
    d_indice = destino / ((roles.get("archivista") or {}).get("escribe_en") or "indice/").strip("/")
    sub = ["ciclos", "historias"] + sorted(p.name for p in (d_indice.iterdir() if d_indice.is_dir() else [])
                                           if p.is_dir() and p.name not in ("ciclos", "historias"))
    buscadas = [d_indice / s / f"{ciclo}.md" for s in sub]
    ficha = next((p for p in buscadas if p.exists()), None)
    rel = lambda p: p.relative_to(destino).as_posix()
    return {"ciclo": ciclo, "n": sum(1 for *_, c in encargos if c == ciclo),
            "criterio": "la fecha del commit del encargo" if por_commit else "la fecha del archivo, porque el encargo no tiene commit",
            "buscadas": [rel(p) for p in buscadas], "ficha": rel(ficha) if ficha else None}


def construir(destino: Path, modo: str | None) -> Plan:
    cfg_p = destino / "coordinador.json"
    texto_cfg = cfg_p.read_text(encoding="utf-8")
    local_cfg = json.loads(texto_cfg)
    kv = local_cfg.get("kit_version")
    versiones = sorted((d.name for d in ANTERIORES.iterdir() if d.is_dir()), key=v_tupla)
    if kv == VERSION:                       # ya actualizado: la base es este mismo kit (re-correrlo no duplica)
        base_ver, base_dir = VERSION, KIT
    else:
        # la base es la mayor versión publicada que no pase de la instalada (1.2.3 -> 1.2); sin kit_version (el campo
        # nació en la 1.2), la más antigua
        previas = [v for v in versiones if v_tupla(v) < v_tupla(VERSION)]
        hasta_kv = [v for v in previas if kv and v_tupla(v) <= v_tupla(kv)]
        base_ver = kv if kv in versiones else (hasta_kv or previas[:1])[-1] if kv else previas[0]
        base_dir = ANTERIORES / base_ver
    plan = Plan(destino, base_ver, modo)
    if kv and v_tupla(kv) > v_tupla(VERSION):
        raise SystemExit(f"El proyecto declara kit_version {kv}, más nueva que este kit ({VERSION}). No hago nada.")

    # 1. coordinador.json
    base_cfg = json.loads((base_dir / "coordinador.example.json").read_text(encoding="utf-8"))
    nuevo_cfg = json.loads(json.dumps(EJEMPLO))
    if modo == "manual":
        for ruta in SOLO_AUTONOMO:
            d = nuevo_cfg
            for k in ruta[:-1]:
                d = d.get(k, {})
            cont = local_cfg
            for k in ruta[:-1]:
                cont = cont.get(k, {})
            if ruta[-1] not in cont:
                d.pop(ruta[-1], None)
    cambios, choques = [], []
    fusion = fusionar_json(local_cfg, base_cfg, nuevo_cfg, [], cambios, choques)
    if "kit_version" in fusion and fusion["kit_version"] != VERSION:
        fusion["kit_version"] = VERSION
        cambios.append((["kit_version"], "actualizado", VERSION))
    plan.cambios_cfg, plan.choques_cfg = cambios, choques
    modo_local = (local_cfg.get("supervision") or {}).get("modo", "claude_completa")
    modo_final = (fusion.get("supervision") or {}).get("modo", "claude_completa")
    modo_kit = (EJEMPLO.get("supervision") or {}).get("modo")
    if modo_final != modo_local:
        plan.notas.append(f"`supervision.modo` pasa de `{modo_local}` a `{modo_final}`: es el modo que instala el kit "
                          f"{VERSION} (Gemini como asistente de los roles de Claude, vigilado por monitores de Claude). "
                          "Necesita agy instalado, con sesión y el workspace de confianza: si el proyecto aún no lo "
                          "tiene, deja `claude_completa` en coordinador.json y anótalo como pendiente en la nota.")
    elif modo_kit and modo_final != modo_kit and modo_final != "solo_coordinador":
        plan.notas.append(f"`supervision.modo` del proyecto es `{modo_final}` y se conserva. El kit {VERSION} instala "
                          f"`{modo_kit}`: para pasarlo, cámbialo en coordinador.json y vuelve a correr este script "
                          "(copia las plantillas del modo) y `scripts/emitir_agy.py`.")
    crlf = "\r\n" in texto_cfg
    salida = json.dumps(fusion, ensure_ascii=False, indent=sangria(texto_cfg)) + "\n"
    salida_b = con_fin(salida.encode("utf-8"), crlf)
    if fusion == local_cfg:
        plan.add("configuración", "coordinador.json", "IGUAL", "nada nuevo del kit que añadir")
    else:
        det = f"{len(cambios)} cambio(s) del kit" + (f"; {len(choques)} choque(s) a revisar (se conserva lo del "
                                                    "proyecto)" if choques else "")
        plan.add("configuración", "coordinador.json", "FUSIONAR", det, salida_b)
    roles = set((fusion.get("roles") or {}))

    # 2. scripts
    for f in sorted((KIT / "scripts").iterdir()):
        if f.is_file() and f.suffix in (".py", ".sh"):
            pieza(plan, "scripts", f"scripts/{f.name}", f, base_dir / "scripts" / f.name)
    if (destino / "scripts").is_dir():
        for f in sorted((destino / "scripts").glob("validar_encuadre_*.py")):
            plan.add("scripts", f"scripts/{f.name}", "CONSERVAR",
                     "validador hermano del dominio: comprueba que valide el mapa_de_lectura")

    # 3. plantillas de rol
    dir_pl = (fusion.get("proyecto") or {}).get("dir_plantillas") or DIR_PLANTILLAS_POR_DEFECTO
    dir_pl = dir_pl.strip("/")
    todas_md = {f.stem: f for f in (KIT / "plantillas").glob("*.md")
                if f.stem != "modo_de_trabajo" and not es_plantilla_informes(f.stem)}
    kit_pl = {k: f for k, f in todas_md.items() if not es_plantilla_agy(k) and not es_plantilla_asistentes(k)}
    for rol, f in sorted(kit_pl.items()):
        rel = f"{dir_pl}/{f.name}"
        if rol not in roles:
            plan.add("plantillas", rel, "OMITIR", "el proyecto no usa este rol (no está en coordinador.json)")
        else:
            pieza(plan, "plantillas", rel, f, base_dir / "plantillas" / f.name)
    # Capas del motor externo (v1.3): no son plantillas de rol. Se copian solo si algún rol declara motor agy.
    roles_agy = sorted(r for r, c in (fusion.get("roles") or {}).items() if isinstance(c, dict) and c.get("motor") == "agy")
    roles_agy += sorted(n for n in (fusion.get("roles_adhoc_agy") or {}) if not n.startswith("_"))
    modo_asist = (fusion.get("supervision") or {}).get("modo") == "asistentes"
    for k, f in sorted(todas_md.items()):
        if not (es_plantilla_agy(k) or es_plantilla_asistentes(k)):
            continue
        rel = f"{dir_pl}/{f.name}"
        if es_plantilla_asistentes(k):
            if modo_asist:
                pieza(plan, "modo asistentes", rel, f, base_dir / "plantillas" / f.name)
            else:
                plan.add("modo asistentes", rel, "NO APLICA", "supervision.modo no es \"asistentes\"; se copia cuando "
                         "el Director lo active (ver MOTOR_EXTERNO.md §10)")
        elif roles_agy or modo_asist:
            pieza(plan, "motor externo", rel, f, base_dir / "plantillas" / f.name)
        else:
            plan.add("motor externo", rel, "NO APLICA", "ningún rol declara \"motor\": \"agy\" y el modo no es "
                     "\"asistentes\"; se copia cuando alguno lo declare (ver MOTOR_EXTERNO.md)")
    herr_rel, herr_kit = "scripts/herramienta_segura.py", KIT / "plantillas" / "herramienta_segura.py"
    if herr_kit.exists():
        herr_dst = destino / herr_rel
        usa = "herramienta_segura" in json.dumps([fusion.get("roles") or {}, fusion.get("roles_adhoc_agy") or {}] + (
            [(fusion.get("supervision") or {}).get("asistentes") or {}] if modo_asist else []), ensure_ascii=False)
        if herr_dst.exists():
            if huella(herr_dst.read_bytes()) == huella(herr_kit.read_bytes()):
                plan.add("motor externo", herr_rel, "IGUAL", "es el esqueleto sin rellenar; sigue pendiente rellenarlo")
            elif (base_dir / "plantillas" / "herramienta_segura.py").exists() and huella(herr_dst.read_bytes()) == huella(
                    (base_dir / "plantillas" / "herramienta_segura.py").read_bytes()):
                plan.add("motor externo", herr_rel, "REEMPLAZAR", f"es el esqueleto sin rellenar del kit {plan.base_ver}: "
                         "pasa al nuevo (con sello, sello-repo, mutar y poner); sigue pendiente rellenarlo",
                         herr_kit.read_bytes())
            else:
                plan.add("motor externo", herr_rel, "CONSERVAR", "herramienta del proyecto, ya rellenada: no se "
                         "sobrescribe nunca")
                faltan = [s for s in SUBCOMANDOS_NUEVOS
                          if f"\"{s}\"" not in herr_dst.read_text(encoding="utf-8", errors="replace")]
                if faltan:
                    plan.notas.append(f"`{herr_rel}` no trae los subcomandos de la v1.3.2 ({', '.join(faltan)}): para "
                                      "que el Verificador inyecte mutantes y dé sellos por la herramienta segura, "
                                      "cópialos del esqueleto `plantillas/herramienta_segura.py` del kit "
                                      "(`cmd_sello`, `cmd_sello_repo`, `cmd_mutar`, `cmd_poner` y su entrada en "
                                      "COMANDOS) y amplía el regex de `comandos_agy`. No se sobrescribe sola.")
        elif usa:
            plan.add("motor externo", herr_rel, "NUEVO", "esqueleto de la herramienta segura que un rol usa en "
                     "comandos_agy; RELLENAR su configuración antes de lanzar", herr_kit.read_bytes())
        else:
            plan.add("motor externo", herr_rel, "NO APLICA", "ningún rol la usa en comandos_agy; la plantilla "
                     "queda en el kit")
    if (destino / dir_pl).is_dir():
        for f in sorted((destino / dir_pl).glob("*.md")):
            if (f.stem not in kit_pl and f.stem != "modo_de_trabajo" and not es_plantilla_agy(f.stem)
                    and not es_plantilla_asistentes(f.stem) and not es_plantilla_informes(f.stem)):
                plan.add("plantillas", f"{dir_pl}/{f.name}", "CONSERVAR",
                         "rol local: ponle al día a mano las reglas comunes del kit nuevo (mapa de lectura, "
                         "consumo, evidencia con comando delante)")

    # 3b. informes (v1.6): el estándar documental y lo que falta para renderizar
    inf = fusion.get("informes") or {}
    est_kit = KIT / "plantillas" / "estandar_documental.md"
    est_rel = (inf.get("estandar") or "docs/estandar_documental.md").strip("/")
    if est_kit.exists():
        if (destino / est_rel).exists():
            pieza_base = base_dir / "plantillas" / "estandar_documental.md"
            if huella((destino / est_rel).read_bytes()) == huella(est_kit.read_bytes()):
                plan.add("informes", est_rel, "IGUAL", f"ya es la del kit {VERSION}")
            elif pieza_base.exists():
                pieza(plan, "informes", est_rel, est_kit, pieza_base)
            else:
                plan.add("informes", est_rel, "CONSERVAR", "estándar documental del proyecto: compáralo con "
                         "`plantillas/estandar_documental.md` del kit (reglas D1 a D4 y el procedimiento)")
        else:
            plan.add("informes", est_rel, "NUEVO", "estándar documental: completar sus marcadores `>>>` con el "
                     "Director", est_kit.read_bytes())
    pl_docx = inf.get("plantilla_docx") or "docs/plantilla.docx"
    if not (destino / pl_docx).exists():
        otras = [p.relative_to(destino).as_posix() for p in buscar(destino, "*.dotx", 3, {".git", "kit_coordinador"})]
        plan.notas.append(f"Informes (v1.6): no está la plantilla .docx en `{pl_docx}`. Pídesela al Director y ponla "
                          "ahí, o ajusta `informes.plantilla_docx`; mientras falte, `renderizar_informe.py` se detiene "
                          "(STOP). Para informes sin plantilla, quita esa clave de `informes`."
                          + (f" Hay plantillas de Word en el proyecto: {', '.join(otras[:3])}." if otras else ""))
    propio = destino / "scripts" / "renderizar_informe.py"
    if propio.exists() and "verificar_informe.py" not in propio.read_text(encoding="utf-8", errors="replace"):
        plan.notas.append("Informes (v1.6): el proyecto ya tenía su `scripts/renderizar_informe.py`. El del kit lee lo "
                          "mismo desde `coordinador.json` (sección `informes`): antes de reemplazarlo, declara ahí sus "
                          "rutas y marcadores propios y comprueba que el cuerpo del .docx sale igual con los dos.")

    # 4. hook
    if (destino / ".git").is_dir():
        hook_rel = ".git/hooks/commit-msg"
        hook_p = destino / hook_rel
        if hook_p.exists() and huella(hook_p.read_bytes()) != huella((KIT / "hooks" / "commit-msg").read_bytes()):
            t = hook_p.read_text(encoding="utf-8", errors="replace")
            if "(?i)" in t and "grep" in t:
                plan.add("herramienta", hook_rel, "REEMPLAZAR", "hook viejo con `(?i)` en grep: no bloqueaba nada",
                         (KIT / "hooks" / "commit-msg").read_bytes(), True)
            else:
                pieza(plan, "herramienta", hook_rel, KIT / "hooks" / "commit-msg",
                      base_dir / "hooks" / "commit-msg", ejecutable=True)
        else:
            pieza(plan, "herramienta", hook_rel, KIT / "hooks" / "commit-msg", None, ejecutable=True)
    else:
        plan.notas.append("El proyecto no es un repositorio git: no hay hook que instalar (decláralo como límite).")

    # 5. .gitignore
    gi = destino / ".gitignore"
    texto_gi = gi.read_text(encoding="utf-8", errors="replace") if gi.exists() else ""
    # v1.6.3: si el proyecto ya decidió sobre bloques/ (una línea que lo menciona, aunque sea un comentario o una
    # negación, o archivos de bloques/ versionados), se respeta y no se escribe nada.
    lineas_bloques = [l.strip() for l in texto_gi.splitlines() if "bloques" in l.lower()]
    versionados_bloques = 0
    if not lineas_bloques and shutil.which("git") and (destino / ".git").exists():
        r = subprocess.run(["git", "-C", str(destino), "ls-files", "bloques"], capture_output=True, text=True)
        versionados_bloques = len(r.stdout.splitlines()) if r.returncode == 0 else 0
    if any(l.rstrip("/") == "bloques" for l in lineas_bloques):
        plan.add("herramienta", ".gitignore", "IGUAL", "ya ignora bloques/")
    elif lineas_bloques or versionados_bloques:
        senal = (f"{len(lineas_bloques)} línea(s) del .gitignore lo mencionan" if lineas_bloques
                 else f"{versionados_bloques} archivo(s) de bloques/ versionados")
        plan.add("herramienta", ".gitignore", "CONSERVAR",
                 f"el proyecto decide sobre bloques/ ({senal}): se respeta, no se añade bloques/")
    else:
        nuevo_gi = texto_gi + ("" if texto_gi.endswith("\n") or not texto_gi else "\n") + "bloques/\n"
        plan.add("herramienta", ".gitignore", "FUSIONAR" if gi.exists() else "NUEVO",
                 "añade bloques/ (material de tránsito)", nuevo_gi.encode("utf-8"))

    # 5b. capturas de los asistentes (v1.4.1): se propone como nota, nunca se escribe sola
    if not any(l.strip() == "asistentes/**/*.png" for l in texto_gi.splitlines()):
        plan.notas.append("Recomendación (v1.4.1, con el sí del Director): añadir al .gitignore "
                          "`asistentes/**/*.png`, `!asistentes/**/lamina*/**` y `!asistentes/**/contacto_*.png`; "
                          "las capturas de los asistentes pesaron cientos de MB por historia. No lo escribo solo.")

    # 5c. asistente navegador (v1.5): la actividad A-navegacion entra con la fusión de coordinador.json
    if modo_asist:
        plan.notas.append("v1.5, asistente navegador (A-navegacion): tras aplicar, regenera los asistentes con "
                          "`scripts/emitir_agy.py`. Prueba de humo: `scripts/abrir_navegador.py abrir`, un encargo "
                          "A-navegacion de prueba con `scripts/lanzar_agy.py asist_navegacion`, `abrir_navegador.py leer` "
                          "y `abrir_navegador.py cerrar` (MOTOR_EXTERNO.md §11). Si el proyecto usa sitios con inicio de "
                          "sesión, el Director entra una vez a mano en el perfil del kit, que es de la máquina: "
                          "`scripts/abrir_navegador.py sesion --url <URL>`.")

    # 5d. repositorio que coincide con el workspace (v1.6.2): los permisos generados antes le negaban escribir a todo rol
    try:
        repos_ws = (json.loads((destino / ".claude" / "settings.json").read_text(encoding="utf-8"))
                    .get("permissions") or {}).get("additionalDirectories") or []
    except (OSError, ValueError):
        repos_ws = []
    ws_norm = destino.resolve().as_posix().rstrip("/")
    iguales = [i for i, r in enumerate(repos_ws, 1)
               if (Path(r) if Path(r).is_absolute() else destino / r).resolve().as_posix().rstrip("/") == ws_norm]
    viejos = [f.name for f in sorted((destino / ".agents" / "permisos").glob("*.json"))
              if any(f"write_file({{REPO_{i}}})" in f.read_text(encoding="utf-8", errors="replace") for i in iguales)]
    if viejos:
        plan.notas.append(f"v1.6.2: el repositorio de trabajo es el mismo workspace y {len(viejos)} permiso(s) de agy "
                          f"({', '.join(viejos[:4])}{'…' if len(viejos) > 4 else ''}) todavía le niegan escribir a todo el "
                          "repositorio, también en la carpeta de salida del rol. Tras aplicar, regenéralos con "
                          "`scripts/emitir_agy.py` y repite la prueba de humo.")

    # 6. modo autónomo
    auto = fusion.get("modo_autonomo") or {}
    if modo == "autonomo" or (modo is None and auto):
        excluir = {".git", "node_modules", "kit_coordinador", "__pycache__", "build", "dist", ".venv", "venv"}
        for clave, origen in (("adenda", KIT / "plantillas" / "adenda_modo_autonomo.txt"),
                              ("instruccion_del_director", KIT / "plantillas" / "modo_de_trabajo.md")):
            rel = (auto.get(clave) or "").strip("/")
            if not rel:
                continue
            if (destino / rel).exists():
                plan.add("modo autónomo", rel, "CONSERVAR", "ya existe: es del proyecto (la instrucción la firma el "
                         "Director); compárala con la del kit si hace falta")
                texto = (destino / rel).read_text(encoding="utf-8", errors="replace")
                if clave == "adenda" and "LÍMITES DE ESTE ENCARGO" not in texto:
                    plan.notas.append(f"`{rel}` es anterior a la 1.4: añádele a mano los puntos 10 (tope de llamadas, "
                                      "no de contexto) y 11 (asistentes Gemini) de `plantillas/adenda_modo_autonomo.txt`, "
                                      "y cambia en el punto 7 «si tu contexto ya pasa de unos 200 k» por «si ya vas por "
                                      "dos tercios de tu tope de llamadas». No se sobrescribe: su punto 3 es del proyecto.")
                if clave == "instruccion_del_director" and "medir_asistentes" not in texto:
                    plan.notas.append(f"`{rel}` es anterior a la versión 3 de la instrucción (kit 1.4): propón al "
                                      "Director los puntos 1, 3 y 9 de `plantillas/modo_de_trabajo.md` (asistentes "
                                      "obligatorios y MANUAL, llamadas y medir_asistentes en la compuerta, traspaso en "
                                      "cada cierre). La instrucción la adapta y la firma el Director: no la edites tú.")
                if clave == "adenda" and "verificar_informe" not in texto:
                    plan.notas.append(f"`{rel}` no trae la regla de informes (kit 1.6): añádele a mano el punto 12 de "
                                      "`plantillas/adenda_modo_autonomo.txt` (borrador, renderizar_informe.py y "
                                      "verificar_informe.py hasta CONFORME; las dos rutas en la entrega).")
                if clave == "instruccion_del_director" and "renderizar_informe" not in texto:
                    plan.notas.append(f"`{rel}` no trae la regla de informes (kit 1.6): propón al Director el punto 11 "
                                      "de `plantillas/modo_de_trabajo.md` (todo informe que pide se entrega en .md y en "
                                      ".docx con la plantilla del proyecto, sin pedirlo). La firma él: no la edites tú.")
                if clave == "instruccion_del_director" and "renovar_por_contexto" not in texto:
                    plan.notas.append(f"`{rel}` no trae la renovación por contexto (kit 1.6.1): propón al Director "
                                      "la frase nueva del punto 3 de `plantillas/modo_de_trabajo.md` (si el contexto "
                                      "final de un rol llegó a 150 k, RENOVAR en medir_consumo.py, su siguiente turno va "
                                      "en un agente nuevo con su nota de reanudación). La firma él: no la edites tú.")
                if clave == "instruccion_del_director" and "subagente de navegador de Antigravity" in texto:
                    plan.notas.append(f"`{rel}` todavía manda el navegador a MANUAL (anterior al kit 1.5): propón al "
                                      "Director el punto 1 nuevo de `plantillas/modo_de_trabajo.md` (lo que se lee o "
                                      "navega en un sitio web lo hace el asistente navegador; MANUAL solo para inicio "
                                      "de sesión, segundo factor o captcha). La firma él: no la edites tú.")
            else:
                plan.add("modo autónomo", rel, "NUEVO", "copiada del kit; completar sus marcadores `>>>`",
                         origen.read_bytes())
        for clave, patron, es_dir in (("dir_encargos", "encargos", True), ("bitacora", "bitacora*.md", False)):
            rel = (auto.get(clave) or "").strip("/")
            if not rel or (destino / rel).exists():
                continue
            otros = [p.relative_to(destino).as_posix() for p in buscar(destino, patron, 3, excluir)
                     if p.is_dir() == es_dir]
            if otros:
                lista = ", ".join(otros[:3]) + (f" y {len(otros) - 3} más" if len(otros) > 3 else "")
                plan.add("modo autónomo", rel, "REVISAR", f"el proyecto ya tiene {lista}: ajusta "
                         f"`modo_autonomo.{clave}` en coordinador.json en lugar de crear otro")
            elif es_dir:
                plan.add("modo autónomo", rel + "/", "NUEVO", "directorio de encargos")
                plan.dirs.append(rel)
            else:
                plan.add("modo autónomo", rel, "NUEVO", "bitácora vacía con su cabecera",
                         b"# Bitacora del Coordinador\n\nDecisiones delegadas, compuertas y cierres de ciclo.\n\n---\n")
        plan.notas.append("Modo autónomo: conviene `\"subagentPromptCacheTtl\": \"1h\"` en `.claude/settings.json` "
                          "(se propone al Director; este script no toca la configuración de la herramienta).")

    # 6b. ciclo en curso (v1.4.2): la versión nueva entra entre ciclos, nunca a mitad de uno
    plan.ciclo = ciclo_en_curso(destino, local_cfg)
    if plan.ciclo and plan.ciclo["ficha"]:
        plan.notas.append(f"Ciclo más reciente: `{plan.ciclo['ciclo']}` (por {plan.ciclo['criterio']}), cerrado: su ficha "
                          f"de cierre es `{plan.ciclo['ficha']}`.")
    elif plan.ciclo:
        plan.ciclo_abierto = c = plan.ciclo
        plan.notas.insert(0, f"**ANTES DE APLICAR: el ciclo `{c['ciclo']}` parece en curso** ({c['n']} encargo(s); el más "
                             f"reciente por {c['criterio']}). Busqué su ficha de cierre en "
                             f"{', '.join(f'`{b}`' for b in c['buscadas'])} y no está. Un ciclo que empezó con una versión "
                             "de la metodología termina con esa versión: el Agente C lo cierra (compuerta, commit, cierre "
                             "de memoria, traspaso, Archivista) y después se actualiza. `--aplicar` se niega mientras "
                             "tanto. Excepciones del Director, que quedan en la nota: `--ciclo-cerrado` (ya cerró y solo "
                             "falta la ficha) o `--autoriza-director \"<motivo>\"` (actualizar a mitad de ciclo).")

    # 7. la copia del kit dentro del proyecto
    kit_local = destino / "kit_coordinador"
    if (kit_local / ".git").exists():
        plan.notas.append("`kit_coordinador/.git` existe: es un repositorio anidado dentro del proyecto. "
                          "Retíralo (con el sí del Director): el kit se copia sin su `.git`.")
    if shutil.which("git") and (destino / ".git").is_dir():
        r = subprocess.run(["git", "-C", str(destino), "ls-files", "kit_coordinador"], capture_output=True, text=True)
        if r.stdout.strip():
            plan.notas.append(f"`kit_coordinador/` está versionado en el repositorio del proyecto "
                              f"({len(r.stdout.splitlines())} archivos). Decide el Director si sigue así o se "
                              "retira del índice.")
    return plan


# ---------------------------------------------------------------- salida y aplicación

def imprimir(plan: Plan, kv_local):
    cuenta = {}
    for _, _, acc, _ in plan.filas:
        cuenta[acc] = cuenta.get(acc, 0) + 1
    print(f"# Actualización del kit — {plan.destino.name}")
    print()
    print(f"De **{kv_local or 'sin kit_version'}** (base de fusión: kit {plan.base_ver}) a **{VERSION}** · "
          f"modo: {plan.modo or 'sin elegir (se muestra lo del modo autónomo)'} · "
          + " · ".join(f"{n} {a}" for a, n in sorted(cuenta.items())))
    print()
    print("| Grupo | Pieza | Acción | Detalle |")
    print("|---|---|---|---|")
    for g, r, a, d in plan.filas:
        print(f"| {g} | `{r}` | **{a}** | {d} |")
    if plan.cambios_cfg:
        print()
        print("**coordinador.json — lo que entra del kit:**")
        for ruta, etq, v in plan.cambios_cfg:
            nombre = '.'.join(map(str, ruta)) or "(el archivo entero: el proyecto no lo había cambiado)"
            print(f"- `{nombre}` {etq}" + ("" if isinstance(v, dict) else f": {_corto(v)}"))
    if plan.choques_cfg:
        print()
        print("**coordinador.json — choques (se conserva lo del proyecto; revisar con el Director):**")
        for ruta, motivo, l, n in plan.choques_cfg:
            print(f"- `{'.'.join(map(str, ruta))}`: {motivo}. Kit: {_corto(n) if n is not FALTA else '(no la trae)'}")
    if plan.notas:
        print()
        for n in plan.notas:
            print(f"- {n}")


def carpeta_libre(base: Path) -> Path:
    p, i = base, 2
    while p.exists():
        p = base.with_name(f"{base.stem}_{i}{base.suffix}") if base.suffix == ".md" else base.with_name(f"{base.name}_{i}")
        i += 1
    return p


def nota_migracion(plan: Plan, kv_local, respaldo: Path, hoy: str) -> str:
    rel_resp = respaldo.relative_to(plan.destino).as_posix()
    lineas = [f"# Migración del kit coordinador a {VERSION} — {hoy}", "",
              f"Generada por `scripts/actualizar_kit.py`. Versión anterior: {kv_local or 'sin kit_version'} "
              f"(base de fusión: kit {plan.base_ver}). Modo: {plan.modo}.", "",
              f"**Respaldo:** `{rel_resp}/` (misma estructura de rutas, con `MANIFIESTO.sha256`).", "",
              "| Grupo | Pieza | Acción | Detalle |", "|---|---|---|---|"]
    lineas += [f"| {g} | `{r}` | {a} | {d} |" for g, r, a, d in plan.filas]
    revisar = [r for _, r, a, _ in plan.filas if a == "REVISAR"]
    if revisar or plan.choques_cfg:
        lineas += ["", "## Pendiente de revisar con el Director", ""]
        for r in revisar:
            if r in plan.propuestas:
                lineas.append(f"- `{r}`: propuesta en `{rel_resp}/propuestas/{r}`. Resolver cada bloque "
                              "`<<<<<<< proyecto` / `=======` / `>>>>>>> kit_…` y copiarla sobre la pieza.")
            else:
                lineas.append(f"- `{r}`: ver el detalle de la tabla.")
        for ruta, motivo, l, n in plan.choques_cfg:
            lineas.append(f"- `coordinador.json` → `{'.'.join(map(str, ruta))}`: {motivo}. Proyecto: {_corto(l)} · "
                          f"kit: {_corto(n) if n is not FALTA else '(no la trae)'}")
    fusionadas = [r for _, r, a, _ in plan.filas if a == "FUSIONAR"]
    if fusionadas:
        lineas += ["", "## Fusionadas sin conflictos (leerlas una vez)", ""]
        lineas += [f"- `{r}` (la versión anterior está en el respaldo)" for r in fusionadas]
    if plan.excepcion_ciclo:
        c = plan.ciclo_abierto
        lineas += ["", "## Ciclo en curso: excepción del Director", "",
                   f"- Ciclo `{c['ciclo']}`, {c['n']} encargo(s); el más reciente por {c['criterio']}.",
                   f"- Ficha de cierre buscada en {', '.join(f'`{b}`' for b in c['buscadas'])}: no está.",
                   f"- {plan.excepcion_ciclo}",
                   "- La regla (`modo_autonomo.cambio_de_version`) dice que un ciclo termina con la versión con que "
                   "empezó; esta actualización se aplicó como excepción."]
    if plan.notas:
        lineas += ["", "## Notas", ""] + [f"- {n}" for n in plan.notas]
    return "\n".join(lineas) + "\n"


def aplicar(plan: Plan, kv_local, hoy: str) -> int:
    d = plan.destino
    # una propuesta idéntica a la de una pasada anterior no se vuelve a escribir (la segunda pasada no escribe nada)
    for rel in list(plan.propuestas):
        if any(q.read_bytes() == plan.propuestas[rel] for q in d.glob(f"respaldo_metodologia_*/propuestas/{rel}")):
            del plan.propuestas[rel]
    if not plan.escrituras and not plan.propuestas and not plan.dirs:
        n_rev = sum(1 for *_, a, _ in plan.filas if a == "REVISAR") + len(plan.choques_cfg)
        print()
        print("APLICADO: 0 archivo(s) escritos · sin respaldo ni nota (nada que escribir).")
        print(f"PENDIENTE: {n_rev} punto(s) a revisar con el Director (ver la nota anterior)." if n_rev
              else "PENDIENTE: nada.")
        return 0
    respaldo = carpeta_libre(d / f"respaldo_metodologia_{hoy}")
    a_respaldar = [rel for rel in plan.escrituras if (d / rel).exists()]
    # 1. Respaldo verificado por huella antes de escribir nada.
    manifiesto = []
    for rel in a_respaldar:
        orig = (d / rel).read_bytes()
        copia = respaldo / rel
        copia.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(d / rel, copia)
        if sha(copia.read_bytes()) != sha(orig):
            print(f"El respaldo de {rel} no cuadra por huella. No escribo nada en el proyecto.")
            return 1
        manifiesto.append(f"{sha(orig)}  {rel}")
    respaldo.mkdir(parents=True, exist_ok=True)
    (respaldo / "MANIFIESTO.sha256").write_bytes(("\n".join(manifiesto) + "\n").encode("utf-8"))
    for rel, b in plan.propuestas.items():
        p = respaldo / "propuestas" / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b)
    # 2. Escrituras, cada una con temporal y renombrado.
    for rel, (b, ejecutable) in plan.escrituras.items():
        p = d / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_name(p.name + ".tmp_kit")
        tmp.write_bytes(b)
        if ejecutable:
            tmp.chmod(0o755)
        elif p.exists():
            shutil.copymode(p, tmp)
        tmp.replace(p)
    for rel in plan.dirs:
        (d / rel).mkdir(parents=True, exist_ok=True)
    # 3. Nota de migración.
    nota = carpeta_libre(d / "docs" / f"migracion_kit_{VERSION}_{hoy}.md")
    nota.parent.mkdir(parents=True, exist_ok=True)
    nota.write_text(nota_migracion(plan, kv_local, respaldo, hoy), encoding="utf-8")
    n_rev = sum(1 for *_, a, _ in plan.filas if a == "REVISAR") + len(plan.choques_cfg)
    print()
    print(f"APLICADO: {len(plan.escrituras)} archivo(s) escritos · respaldo en {respaldo.relative_to(d)}/ "
          f"({len(a_respaldar)} archivo(s), huellas OK) · nota en {nota.relative_to(d)}")
    print(f"PENDIENTE: {n_rev} punto(s) a revisar con el Director (en la nota)." if n_rev else "PENDIENTE: nada.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("destino", nargs="?", default=".")
    ap.add_argument("--aplicar", action="store_true", help="escribe (sin esto solo imprime el plan)")
    ap.add_argument("--modo", choices=("autonomo", "manual"), default="autonomo",
                    help="autonomo (por defecto desde la 1.4) o manual (solo si el Director lo pide)")
    ap.add_argument("--fecha", help="AAAA-MM-DD para el respaldo y la nota; por defecto, hoy")
    ap.add_argument("--ciclo-cerrado", action="store_true",
                    help="el Director confirma que no hay un ciclo en curso aunque falte su ficha de cierre")
    ap.add_argument("--autoriza-director", metavar="MOTIVO",
                    help="el Director autoriza actualizar a mitad de un ciclo; el motivo queda en la nota de migración")
    a = ap.parse_args()
    destino = Path(a.destino).resolve()
    if not (destino / "coordinador.json").exists():
        print(f"No hay coordinador.json en {destino}: no hay un kit instalado que actualizar. "
              "Siga la instalación normal (PROMPT_INSTALACION.md, pasos 1 a 5).")
        return 2
    if destino == KIT:
        print("El destino es el propio kit. Indique la carpeta del proyecto.")
        return 2
    kv_local = json.loads((destino / "coordinador.json").read_text(encoding="utf-8")).get("kit_version")
    plan = construir(destino, a.modo)
    imprimir(plan, kv_local)
    if not a.aplicar:
        print()
        print("Solo plan: no se escribió nada. Para aplicarlo, con el sí del Director: "
              "--aplicar (modo autónomo; --modo manual solo si el Director lo pide)")
        return 0
    motivo = (a.autoriza_director or "").strip()
    if a.autoriza_director is not None and len(motivo) < 15:
        print("--autoriza-director necesita el motivo del Director, de al menos 15 caracteres. No se escribió nada.")
        return 2
    if plan.ciclo_abierto and (plan.escrituras or plan.dirs):
        if motivo:
            plan.excepcion_ciclo = f"Autorizado por el Director (`--autoriza-director`) el {a.fecha or date.today().isoformat()}: {motivo}"
        elif a.ciclo_cerrado:
            plan.excepcion_ciclo = ("El Director confirmó (`--ciclo-cerrado`) que el ciclo ya está cerrado y solo falta su "
                                    "ficha de cierre.")
        else:
            print()
            print(f"STOP: el ciclo `{plan.ciclo_abierto['ciclo']}` parece en curso: busqué su ficha de cierre en "
                  f"{', '.join(plan.ciclo_abierto['buscadas'])} y no está. No se escribió nada. Termina ese ciclo con la "
                  "versión con que empezó y actualiza después. Excepciones del Director: --ciclo-cerrado o "
                  "--autoriza-director \"<motivo>\".")
            return 3
    return aplicar(plan, kv_local, a.fecha or date.today().isoformat())


if __name__ == "__main__":
    raise SystemExit(main())
