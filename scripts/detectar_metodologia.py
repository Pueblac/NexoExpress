"""Detecta una metodología de coordinación previa en un proyecto destino (kit coordinador v1.6).

Lo corre el instalador en el PASO 0, antes de copiar nada. Hace un inventario de las
señales de un sistema previo (una versión anterior de este kit u otra metodología), deduce
qué versión hay y propone, pieza por pieza, qué hacer:

  REEMPLAZAR  la pieza es del kit (o equivale a una del kit) y la versión nueva la sustituye;
              antes se respalda en una carpeta con fecha.
  MIGRAR      la pieza guarda datos o decisiones del proyecto (bitácora, fichas, órdenes,
              veredictos, actas, índices, roster, instrucciones del proyecto): se conserva y
              se adapta al formato nuevo, sin perder nada.
  RETIRAR     la pieza sobra o chocaría con el kit nuevo (material de tránsito, copias del
              kit anidadas, duplicados de herramientas);
              se respalda y se retira solo si el usuario lo confirma.

Desde v1.3 informa también del motor externo: en el destino, `.agents/` (agents y permisos),
`AGENTS.md` y `GEMINI.md`; en esta máquina, si agy está instalado, si existe su settings.json
global (o el de AGY_SETTINGS) y si tiene sección "permissions", y los restos de un lanzamiento
cortado (`settings.json.lanzar_agy`, `lanzar_agy.lock`). De la máquina solo informa.

NUNCA BORRA NI ESCRIBE NADA en el destino ni en la máquina: solo lee y escribe el informe en
la salida estándar. El informe lleva solo nombres de archivo, conteos y huellas cortas; no
copia el contenido de ningún archivo.

Uso:
    python -I scripts/detectar_metodologia.py <directorio destino> [--etiqueta "<nombre a mostrar>"] [--json]
    # exit 0 siempre que pudo leer el destino; exit 2 si el destino no existe
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KIT = Path(__file__).resolve().parents[1]
VERSION = "1.6.3"

# Huellas (sha256 de los primeros 16 hex, con los finales de línea normalizados a LF) de
# piezas de versiones anteriores del kit. Las de la versión actual se calculan del propio kit.
HUELLAS_ANTERIORES = {
    "b17a2489d900138b": ("emitir_arranque.py", "1.0–1.6.3 (sin cambios)"),
    "d0424ebb773fa3f6": ("validar_encuadre.py", "1.1"),
    "f69601802baf7095": ("detectar_metodologia.py", "1.3–1.3.1"),
    "5aac37c8ba8fe077": ("emitir_agy.py", "1.3–1.3.1"),
    "30402cec621d5fc7": ("encargar.sh", "1.3–1.3.1"),
    "99629305624f2e3b": ("lanzar_agy.py", "1.3–1.3.1"),
    "640db94b4ab325ed": ("proponer_tramos.py", "1.3–1.3.1"),
    "a20239d5963091b2": ("agy_roles.md", "1.3–1.3.1"),
    "f6dea2ac3a3e9266": ("arquitecto.md", "1.3–1.3.1"),
    "d65a1aba0908c259": ("herramienta_segura.py", "1.3–1.3.1"),
    # Piezas de la 1.3.2 que cambiaron en la 1.3.3 (sus huellas, de la rama v1.3.2):
    "49e4a0b837d5a1b0": ("emitir_agy.py", "1.3.2"),
    "0813799b887a4171": ("lanzar_agy.py", "1.3.2"),
    "39754c842945643f": ("proponer_tramos.py", "1.3.2"),
    "46a3914c347ae87e": ("detectar_metodologia.py", "1.3.2"),
    "7aeb6d221468f361": ("agy_roles.md", "1.3.2"),
    "7b2ec26f06fe3639": ("herramienta_segura.py", "1.3.2"),
    "2a0f00e64f723837": ("asist_encargo_asistente.md", "1.3.2"),
    "5bf9dd803dbfa6f0": ("asist_encargo_monitor.md", "1.3.2"),
    "b11d3eaa94211501": ("commit-msg", "1.1–1.6.3 (sin cambios)"),
    # Piezas de la 1.3.3 que cambiaron en la 1.4.0 (de anteriores/1.3.3/):
    "3a85714e69868fe4": ("actualizar_kit.py", "1.3.3"),
    "cf91143f00b156e1": ("detectar_metodologia.py", "1.3.3"),
    "521eb4752245f053": ("emitir_agy.py", "1.3.3"),
    "bbdb0e42ccd08966": ("lanzar_agy.py", "1.3.3"),
    "7e4e203445d2179e": ("encargar.sh", "1.3.3"),
    "c4cfe51424d75465": ("medir_consumo.py", "1.3.3"),
    "35a1d3438c3b714b": ("adenda_modo_autonomo.txt", "1.3.3"),
    "0febaf70d1a3a80e": ("adenda_modo_autonomo.txt", "1.3.3 (antes de la instrucción versión 2)"),
    "1fd9fb0417a5edf6": ("agy_roles.md", "1.3.3"),
    "7b2829e50f16d7fc": ("archivista.md", "1.3.3"),
    "cc519b76f65eaacc": ("arquitecto.md", "1.3.3"),
    "7098267ccf1d3a45": ("asist_encargo_monitor.md", "1.3.3"),
    "fb4ec6b6c177f719": ("asist_plan.md", "1.3.3"),
    "ca36fcad0bffaa24": ("guionista.md", "1.3.3"),
    "550adb77dcd7c1aa": ("ingeniero.md", "1.3.3"),
    "22f5f1ea9615aa17": ("modo_de_trabajo.md", "1.3.3 (instrucción versión 2)"),
    "ea9b54082c81450f": ("modo_de_trabajo.md", "1.3.3 (instrucción versión 1)"),
    "fb88d09fb5ba5441": ("verificador.md", "1.3.3"),
    # Piezas de la 1.4.0 que cambiaron en la 1.4.1 (de anteriores/1.4.0/):
    "d5f28b8f871cf521": ("detectar_metodologia.py", "1.4.0"),
    "eefe4f95241d14bd": ("actualizar_kit.py", "1.4.0"),
    "a5bd5aa158f5a2e1": ("guionista.md", "1.4.0"),
    "fbb248840e646c80": ("modo_de_trabajo.md", "1.4.0"),
    "fc3af2694f8eaf15": ("arquitecto.md", "1.4.0"),
    "7699202c2778ddac": ("ingeniero.md", "1.4.0"),
    "538eecf7f41e0415": ("adenda_modo_autonomo.txt", "1.4.0"),
    # Piezas de la 1.4.1 que cambiaron en la 1.4.2 (de anteriores/1.4.1/):
    "7e64ff1ad3f3eec6": ("detectar_metodologia.py", "1.4.1"),
    "ea71e7254746805e": ("actualizar_kit.py", "1.4.1"),
    "bc9b33cbe3a1591d": ("modo_de_trabajo.md", "1.4.1"),
    # Piezas de la 1.4.2 que cambiaron en la 1.5.0 (de anteriores/1.4.2/):
    "57c3105a0625f82b": ("emitir_agy.py", "1.4.0–1.4.2"),
    "8ac39ba23423912a": ("lanzar_agy.py", "1.4.0–1.4.2"),
    "e3c24785048d6acc": ("detectar_metodologia.py", "1.4.2"),
    "d923652ea2a79c28": ("actualizar_kit.py", "1.4.2"),
    "40b538e7932fc2b7": ("agy_roles.md", "1.4.0–1.4.2"),
    "4d9fea8b40be4d38": ("asist_encargo_asistente.md", "1.3.3–1.4.2"),
    "0b43fd0747758f59": ("asist_encargo_monitor.md", "1.4.0–1.4.2"),
    "51525b5f7f5f6e51": ("asist_plan.md", "1.4.0–1.4.2"),
    "187d1fc3ab7e4edf": ("arquitecto.md", "1.4.1–1.4.2"),
    "d1c139f94d78bfb5": ("ingeniero.md", "1.4.1–1.4.2"),
    "acad1d840246a311": ("verificador.md", "1.4.0–1.4.2"),
    "d08b6235bd9ee256": ("modo_de_trabajo.md", "1.4.2"),
    # Piezas de la 1.5.0 que cambiaron en la 1.6.0 (de anteriores/1.5.0/):
    "01bec1172c3cab8e": ("detectar_metodologia.py", "1.5.0"),
    "a258ecc87ae95c37": ("actualizar_kit.py", "1.5.0"),
    "33ed645ec5a5263f": ("adenda_modo_autonomo.txt", "1.5.0"),
    "425dee25acff10df": ("modo_de_trabajo.md", "1.5.0"),
    # Piezas de la 1.6.0 que cambiaron en la 1.6.1 (de anteriores/1.6.0/):
    "168fa138ea67084b": ("medir_consumo.py", "1.6.0"),
    "c65c4dcdbb903f3d": ("modo_de_trabajo.md", "1.6.0"),
    "464df694dbf15fac": ("actualizar_kit.py", "1.6.0"),
    "067cb5c3bc98bfcb": ("detectar_metodologia.py", "1.6.0"),
    # Piezas de la 1.6.1 que cambiaron en la 1.6.2 (de anteriores/1.6.1/):
    "955408389fd2f29a": ("emitir_agy.py", "1.6.1"),
    "1d5b611ef12f6077": ("actualizar_kit.py", "1.6.1"),
    "ba5f6aadf8884df6": ("detectar_metodologia.py", "1.6.1"),
    # Piezas de la 1.6.2 que cambiaron en la 1.6.3 (de anteriores/1.6.2/):
    "fef2466ca328f65a": ("actualizar_kit.py", "1.6.2"),
    "6de668a47bdbef1e": ("detectar_metodologia.py", "1.6.2"),
    "6b96f1c64439eb37": ("detectar_metodologia.py", "1.2–1.2.1"),
    "b5878125d820e2f1": ("detectar_metodologia.py", "1.2.2"),
    "d1fa5e51c4277f3b": ("proponer_tramos.py", "1.2–1.2.1"),
    "18c3084a41117a88": ("proponer_tramos.py", "1.2.2"),
    "e81a16b2442e4c2b": ("encargar.sh", "1.2–1.2.1"),
    "b4cdce934a904508": ("encargar.sh", "1.2.2"),
    "8cf62f847e65e17d": ("auditor.md", "1.2–1.2.2"),
    "eb4a2ca105a6630b": ("arquitecto.md", "1.0–1.1"),
    "551d60ac6f78184d": ("asesor.md", "1.0–1.1"),
    "8617f7e7cc7a809c": ("auditor.md", "1.0–1.1"),
    "3ba88a9020ecd6f6": ("guionista.md", "1.0–1.1"),
    "e1302d451cdb9d94": ("ingeniero.md", "1.0–1.1"),
    "dd0d33ab684ad624": ("verificador.md", "1.0–1.1"),
}
SCRIPTS_DEL_KIT = ["emitir_arranque.py", "validar_encuadre.py", "encargar.sh", "medir_consumo.py", "medir_asistentes.py",
                   "proponer_tramos.py", "reanclar_tramos.py", "listar_artefactos.py",
                   "archivar_bitacora.py", "comprobar_indice.py", "detectar_metodologia.py",
                   "lanzar_agy.py", "emitir_agy.py", "abrir_navegador.py",
                   "renderizar_informe.py", "verificar_informe.py"]
# Motor externo (v1.3): el settings.json global de agy y los restos de un lanzamiento cortado.
AGY_AJUSTES = Path.home() / ".gemini" / "antigravity-cli" / "settings.json"
DIRS_DE_ROL_HABITUALES = ["encuadres", "ingenieria/ordenes", "ingenieria/entregas",
                          "ingenieria/verificaciones", "indice", "agencia/respuestas",
                          "investigaciones", "diseno/fichas", "pruebas_manuales", "docs/asesorias"]
DOCS_HABITUALES = ["docs/metodologia.md", "docs/directriz_cadena_de_mando.md",
                   "docs/estado_actual.md", "docs/modo_de_trabajo.md"]
INSTRUCCIONES = ["CLAUDE.md", ".claude/CLAUDE.md", "AGENTS.md", "GEMINI.md", ".cursorrules",
                 ".github/copilot-instructions.md"]
IGNORAR = {".git", "node_modules", ".venv", "venv", "__pycache__", "build", "dist"}


def huella(p: Path) -> str:
    try:
        return hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest()[:16]
    except OSError:
        return "?"


def contar_lineas(p: Path) -> int:
    try:
        return p.read_bytes().count(b"\n")
    except OSError:
        return 0


def contar_archivos(d: Path) -> int:
    return sum(1 for f in d.rglob("*") if f.is_file() and not (set(f.relative_to(d).parts) & IGNORAR))


def buscar(raiz: Path, patron: str, prof: int = 3) -> list[Path]:
    """Busca por nombre (glob) hasta `prof` niveles, sin entrar en carpetas ignoradas."""
    hallados = []
    for p in raiz.rglob(patron):
        rel = p.relative_to(raiz)
        if len(rel.parts) > prof or set(rel.parts) & IGNORAR or rel.parts[0].startswith("respaldo_metodologia_"):
            continue
        hallados.append(p)
    return sorted(hallados)


class Informe:
    def __init__(self, raiz: Path):
        self.raiz = raiz
        self.piezas = []      # (grupo, ruta relativa, detalle, acción, motivo)
        self.versiones = []   # pistas de versión
        self.entorno = []     # (qué, estado) de esta máquina: motor externo; no son piezas del destino

    def rel(self, p: Path) -> str:
        return p.relative_to(self.raiz).as_posix() + ("/" if p.is_dir() else "")

    def add(self, grupo, p, detalle, accion, motivo):
        self.piezas.append((grupo, self.rel(p) if isinstance(p, Path) else p, detalle, accion, motivo))


def huellas_actuales() -> dict:
    h = {}
    for nombre in SCRIPTS_DEL_KIT:
        f = KIT / "scripts" / nombre
        if f.exists():
            h[huella(f)] = (nombre, VERSION)
    for f in sorted((KIT / "plantillas").glob("*")):
        h[huella(f)] = (f.name, VERSION)
    if (KIT / "hooks" / "commit-msg").exists():
        h[huella(KIT / "hooks" / "commit-msg")] = ("commit-msg", VERSION)
    return h


def version_de_pieza(p: Path, actuales: dict) -> str | None:
    hu = huella(p)
    if hu in HUELLAS_ANTERIORES and HUELLAS_ANTERIORES[hu][0] == p.name:
        return HUELLAS_ANTERIORES[hu][1]
    if hu in actuales and actuales[hu][0] == p.name:
        return actuales[hu][1]
    return None


def es_actual(v: str | None) -> bool:
    """True si la versión (o el extremo superior de un rango como «1.0–1.6.0») es 1.6.3 o posterior.

    Una pieza «1.6.2» no es actual: lo que cambió en 1.6.3 tiene huella nueva."""
    if not v:
        return False
    nums = re.findall(r"(\d+)\.(\d+)(?:\.(\d+))?", v)
    return bool(nums) and tuple(int(x or 0) for x in nums[-1]) >= (1, 6, 3)


def detectar(raiz: Path) -> Informe:
    inf = Informe(raiz)
    actuales = huellas_actuales()
    cfg_roles = {}
    dirs_plantillas = ["docs/prompts_arranque", "plantillas"]

    # 1. Configuración de la metodología
    configs = [p for p in buscar(raiz, "coordinador*.json", 2) if "kit_coordinador" not in p.relative_to(raiz).parts]
    for p in configs:
        try:
            cfg = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            inf.add("configuración", p, "no es JSON válido", "MIGRAR", "revisar a mano: no se pudo leer")
            continue
        roles = cfg.get("roles") or {}
        cfg_roles.update(roles)
        dp = ((cfg.get("proyecto") or {}).get("dir_plantillas") or "").strip("/")
        if dp and dp not in dirs_plantillas:
            dirs_plantillas.insert(0, dp)
        kv = cfg.get("kit_version")
        if kv:
            inf.versiones.append(f"`{inf.rel(p)}` declara kit_version {kv}")
        elif "modo_autonomo" in cfg or "archivista" in roles:
            inf.versiones.append(f"`{inf.rel(p)}` no declara kit_version pero tiene modo autónomo o Archivista: adaptación local posterior a 1.1")
        elif roles:
            asesor = (roles.get("asesor") or {}).get("escribe_en", "")
            inf.versiones.append(f"`{inf.rel(p)}` sin kit_version: "
                                 + ("1.0 (el Asesor tiene directorio)" if asesor and not asesor.startswith("(")
                                    else "1.1 o adaptación local de 1.1"))
        locales = sorted(set(roles) - {"coordinador", "asesor", "guionista", "validador", "arquitecto",
                                       "ingeniero", "verificador", "archivista", "auditor"})
        if p.name == "coordinador.example.json":
            inf.add("configuración", p, "ejemplo de configuración", "REEMPLAZAR", "lo trae el kit nuevo")
        else:
            inf.add("configuración", p,
                    f"{len(roles)} roles" + (f" ({len(locales)} locales: {', '.join(locales)})" if locales else "")
                    + f"; secciones: {', '.join(k for k in cfg if not k.startswith('_'))}",
                    "MIGRAR", "conservar roster, roles locales, directorios y reglas propias; añadir lo nuevo del kit "
                    "(kit_version, roles y secciones nuevas) sin pisar lo local")

    # 2. Plantillas de arranque
    for d in [raiz / x for x in dirs_plantillas]:
        if not d.is_dir():
            continue
        archivos = sorted(f for f in d.iterdir() if f.is_file())
        inf.add("plantillas", d, f"{len(archivos)} archivos", "REEMPLAZAR",
                "por las del kit nuevo, re-aplicando las adaptaciones locales listadas abajo")
        for f in archivos:
            v = version_de_pieza(f, actuales)
            if v:
                inf.add("plantillas", f, f"igual a la del kit {v}", "REEMPLAZAR",
                        "ya es la del kit nuevo: no hace falta tocarla" if es_actual(v) else "sin adaptaciones locales")
            elif f.name not in {x.name for x in (KIT / "plantillas").glob("*")}:
                inf.add("plantillas", f, f"{contar_lineas(f)} líneas; rol local (el kit no trae esta plantilla)",
                        "MIGRAR", "conservar, poniéndole al día las reglas comunes del kit nuevo")
            else:
                inf.add("plantillas", f, f"{contar_lineas(f)} líneas; adaptada localmente",
                        "REEMPLAZAR", "por la del kit nuevo, tras listar y re-aplicar sus cambios locales (diff)")

    # 3. Scripts y herramientas
    vistos = set()
    for nombre in SCRIPTS_DEL_KIT + ["validar_encuadre_*.py", "nuevo_encargo.py"]:
        for f in buscar(raiz, nombre, 3):
            if "kit_coordinador" in f.relative_to(raiz).parts or f in vistos:
                continue
            vistos.add(f)
            v = version_de_pieza(f, actuales)
            if f.name.startswith("validar_encuadre_"):
                inf.add("scripts", f, f"{contar_lineas(f)} líneas; validador hermano del dominio", "MIGRAR",
                        "conservar: son las pruebas del dominio; comprobar que valida el mapa_de_lectura")
            elif f.parent.name == "scripts":
                inf.add("scripts", f, f"kit {v}" if v else f"{contar_lineas(f)} líneas; distinto del kit",
                        "REEMPLAZAR", "ya es la del kit nuevo: no hace falta tocarlo" if es_actual(v) else
                        "por la versión del kit nuevo" + ("" if v else " (si tiene cambios locales, listarlos antes)"))
            else:
                inf.add("scripts", f, f"kit {v}" if v else f"{contar_lineas(f)} líneas; fuera de scripts/",
                        "RETIRAR", "duplicado de una herramienta que el kit trae en scripts/ (respaldar y "
                        "actualizar las referencias en la documentación local)")
            if v and f.name == "validar_encuadre.py":
                inf.versiones.append(f"`{inf.rel(f)}` es el validador del kit {v}")
    for d in [raiz / "herramientas"]:
        if d.is_dir():
            otros = sorted(x.name for x in d.iterdir() if x.name not in SCRIPTS_DEL_KIT)
            if otros:
                inf.add("scripts", d, f"{len(otros)} entradas propias del proyecto", "MIGRAR",
                        "conservar: no son del kit")

    # 4. Bitácora, decisiones y expediente
    for f in buscar(raiz, "bitacora*.md", 3):
        if "bitacora_archivo" in f.parts:
            continue
        texto = f.read_text(encoding="utf-8", errors="replace")
        dd = len(set(re.findall(r"DECISION_DELEGADA (DD-\d+)", texto)))
        inf.add("expediente", f, f"{contar_lineas(f)} líneas; {dd} decisiones delegadas escritas en este archivo", "MIGRAR",
                "conservar íntegra; si se cambia de formato, con archivar_bitacora.py (sin cambios, byte a byte)")
    for d in buscar(raiz, "bitacora_archivo", 3):
        if d.is_dir():
            inf.add("expediente", d, f"{contar_archivos(d)} archivos", "MIGRAR", "conservar íntegro")
    dirs_rol = {(r or {}).get("escribe_en", "").strip("/") for r in cfg_roles.values()}
    dirs_rol = {x for x in dirs_rol if x and not x.startswith("(")} | set(DIRS_DE_ROL_HABITUALES)
    for rel in sorted(dirs_rol):
        d = raiz / rel
        if d.is_dir():
            n = contar_archivos(d)
            extra = ""
            if (d / "mapa_vivo.json").exists() or (d / "memoria_guionista.md").exists():
                extra = "; incluye memoria del Guionista"
            if rel == "docs/asesorias":
                inf.add("expediente", d, f"{n} archivos", "MIGRAR",
                        "conservar como registro; desde v1.1 el Asesor no tiene directorio y no se le crea")
            else:
                inf.add("expediente", d, f"{n} archivos{extra}", "MIGRAR",
                        "conservar: artefactos del proyecto (fichas, órdenes, entregas, veredictos, actas, índices)")
    for rel in DOCS_HABITUALES:
        f = raiz / rel
        if f.exists():
            inf.add("documentos", f, f"{contar_lineas(f)} líneas", "MIGRAR",
                    "conservar las decisiones locales; poner al día lo que cambie con el kit nuevo")

    # 5. Modo autónomo y material de tránsito
    for f in buscar(raiz, "adenda_modo_autonomo*.txt", 3):
        if "kit_coordinador" in f.relative_to(raiz).parts:
            continue
        inf.add("modo autónomo", f, f"{contar_lineas(f)} líneas", "REEMPLAZAR",
                "por la adenda del kit nuevo, re-aplicando la sección del repositorio de trabajo")
    for d in buscar(raiz, "encargos", 3):
        if d.is_dir():
            inf.add("modo autónomo", d, f"{contar_archivos(d)} encargos archivados", "MIGRAR",
                    "conservar como expediente")
    for d in [raiz / "bloques"]:
        if d.is_dir():
            inf.add("tránsito", d, f"{contar_archivos(d)} bloques emitidos", "RETIRAR",
                    "material de tránsito (va en .gitignore); se regenera al emitir")
    for d in buscar(raiz, "kit_coordinador", 2) + buscar(raiz, "kit_exportable*", 2):
        if not d.is_dir():
            continue
        if d.resolve() == KIT:
            inf.add("kit en uso", d, f"la copia del kit con la que se instala ({contar_archivos(d)} archivos)",
                    "RETIRAR", "no es metodología previa; se retira al terminar si el Director no quiere conservarla")
            if (d / ".git").exists():
                inf.add("kit en uso", d / ".git", "repositorio git anidado dentro del proyecto", "RETIRAR",
                        "el kit se copia sin su `.git`: respaldar y retirar con el sí del Director")
        else:
            inf.add("tránsito", d, f"copia de un kit dentro del proyecto ({contar_archivos(d)} archivos)",
                    "RETIRAR", "una copia anidada confunde a git y al instalador; respaldar y retirar al terminar")

    # 6. Instrucciones del proyecto y configuración de la herramienta
    for rel in INSTRUCCIONES:
        f = raiz / rel
        if f.exists():
            if f.name in ("GEMINI.md", "AGENTS.md"):
                inf.add("instrucciones", f, f"{contar_lineas(f)} líneas", "MIGRAR",
                        "conservar lo que sea instrucción del proyecto; desde v1.3 lo que un rol necesita en el "
                        "motor externo va en `.agents/agents/<rol>.md` (lo genera emitir_agy.py), no aquí")
            else:
                inf.add("instrucciones", f, f"{contar_lineas(f)} líneas", "MIGRAR",
                        "conservar; añadir la referencia a la metodología sin sobrescribir lo del proyecto")
    for nombre in ("settings.json", "settings.local.json"):
        f = raiz / ".claude" / nombre
        if f.exists():
            try:
                s = json.loads(f.read_text(encoding="utf-8"))
                perm = s.get("permissions") or {}
                partes = [f"hooks: {len(s.get('hooks') or {})} eventos",
                          f"permisos allow/deny: {len(perm.get('allow') or [])}/{len(perm.get('deny') or [])}",
                          f"repositorios autorizados: {len(perm.get('additionalDirectories') or [])}",
                          f"caché de subagentes: {s.get('subagentPromptCacheTtl', 'por defecto')}"]
                det = "; ".join(partes)
            except Exception:
                det = "no es JSON válido"
            inf.add("herramienta", f, det, "MIGRAR",
                    "conservar permisos y repositorios autorizados (los lee el emisor); revisar hooks contra el kit")
    hook = raiz / ".git" / "hooks" / "commit-msg"
    if hook.exists():
        v = version_de_pieza(hook, actuales)
        texto = hook.read_text(encoding="utf-8", errors="replace")
        if v:
            det, acc, mot = f"hook del kit {v}", "REEMPLAZAR",                 "ya es el del kit nuevo: no hace falta tocarlo" if es_actual(v) else "por el hook del kit nuevo"
        elif "(?i)" in texto and "grep -E" in texto:
            det, acc, mot = "hook con `(?i)` dentro de `grep -E`: no bloquea nada", "REEMPLAZAR", \
                "por el hook corregido del kit"
        else:
            det, acc, mot = "hook propio", "MIGRAR", "conservar; ofrecer el del kit al usuario"
        inf.add("herramienta", hook, det, acc, mot)
    elif (raiz / ".git").is_dir():
        inf.add("herramienta", ".git/hooks/commit-msg", "no instalado", "REEMPLAZAR", "instalar el hook del kit")

    # 7. Motor externo (v1.3): definiciones y permisos de agy en el destino
    agentes = raiz / ".agents"
    if agentes.is_dir():
        for sub, patron in (("agents", "*.md"), ("permisos", "*.json")):
            d = agentes / sub
            if not d.is_dir():
                continue
            archivos = sorted(f for f in d.glob(patron) if f.is_file())
            generados = [f for f in archivos if "emitir_agy.py" in f.read_text(encoding="utf-8", errors="replace")]
            nombres = ", ".join(f.stem for f in archivos) or "ninguno"
            if archivos and len(generados) == len(archivos):
                inf.add("motor externo", d, f"{len(archivos)} ({nombres}); generados por emitir_agy.py", "REEMPLAZAR",
                        "se regeneran con scripts/emitir_agy.py desde coordinador.json")
            else:
                inf.add("motor externo", d, f"{len(archivos)} ({nombres}); {len(archivos) - len(generados)} escritos a mano",
                        "MIGRAR", "llevar sus reglas a motor, modelo_agy y comandos_agy del rol en coordinador.json y "
                        "regenerar con emitir_agy.py; el original queda en el respaldo")
        otros = sorted(x.name for x in agentes.iterdir() if x.name not in ("agents", "permisos"))
        if otros:
            inf.add("motor externo", agentes, f"{len(otros)} entradas más ({', '.join(otros)})", "MIGRAR",
                    "conservar: el kit solo usa agents/ y permisos/")
    inf.entorno = entorno_agy(raiz)
    return inf


def _ruta_confianza(s) -> str:
    s = str(s).strip().replace("\\", "/")
    if re.match(r"^/[a-zA-Z]/", s):
        s = s[1].upper() + ":" + s[2:]
    s = s.rstrip("/") or "/"
    return s.casefold() if os.name == "nt" else s


def entorno_agy(raiz: Path) -> list:
    """Estado del motor externo en ESTA máquina. Solo lee; no borra ni restaura nada."""
    e = []
    en_path = shutil.which("agy")
    exe = en_path
    if not exe and os.environ.get("LOCALAPPDATA"):
        for n in ("agy.exe", "agy"):
            if (Path(os.environ["LOCALAPPDATA"]) / "agy" / "bin" / n).exists():
                exe = n
                break
    e.append(("agy", ("instalado, en el PATH" if en_path else "instalado en %LOCALAPPDATA%/agy/bin, fuera del PATH "
                      "de esta terminal (abrir una nueva o usar AGY)") if exe else "no instalado"))
    ajustes = Path(os.environ["AGY_SETTINGS"]) if os.environ.get("AGY_SETTINGS") else AGY_AJUSTES
    nombre = "$AGY_SETTINGS" if os.environ.get("AGY_SETTINGS") else "~/.gemini/antigravity-cli/settings.json"
    if not ajustes.exists():
        estado = "no existe (falta autenticar agy una vez en interactivo)"
    else:
        try:
            s = json.loads(ajustes.read_text(encoding="utf-8"))
            perm = s.get("permissions") if isinstance(s, dict) else None
            estado = ("existe, sin sección permissions" if perm is None else
                      f"existe, con sección permissions (allow/deny: {len((perm or {}).get('allow') or [])}/"
                      f"{len((perm or {}).get('deny') or [])}); el lanzador la sustituye solo mientras corre un rol")
        except (OSError, json.JSONDecodeError):
            estado = "existe pero NO es JSON válido: agy ignora todas las reglas y deniega todo sin avisar"
    e.append((nombre, estado))
    ws = f"workspace {raiz.resolve().as_posix()}"
    try:
        lista = json.loads(ajustes.read_text(encoding="utf-8")).get("trustedWorkspaces")
        lista = [x.get("path") if isinstance(x, dict) else x for x in lista] if isinstance(lista, list) else []
        de_confianza = _ruta_confianza(raiz.resolve().as_posix()) in {_ruta_confianza(x) for x in lista if isinstance(x, str)}
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, AttributeError):
        de_confianza = None
    if de_confianza is None:
        e.append(("confianza de agy", f"no se pudo comprobar ({ws}): falta settings.json o no es JSON válido"))
    elif de_confianza:
        e.append(("confianza de agy", f"el {ws} está en trustedWorkspaces: agy carga sus roles"))
    else:
        e.append(("confianza de agy", f"el {ws} NO está en trustedWorkspaces: agy no carga sus roles ('unknown agent') "
                  "y el lanzador se detiene. Dale confianza tú: abre agy en interactivo dentro del workspace y acepta; "
                  "ni el detector ni el lanzador la añaden"))
    for resto, que in ((ajustes.with_name(ajustes.name + ".lanzar_agy"), "respaldo"),
                       (ajustes.with_name("lanzar_agy.lock"), "candado")):
        if resto.exists():
            e.append((resto.name, f"RESTO de un lanzamiento cortado ({que}). Si no hay otro corriendo: "
                                  "python -I scripts/lanzar_agy.py --restaurar. El detector no lo borra"))
    return e


def senales(inf: Informe) -> list:
    """Piezas que delatan una metodología previa: no cuentan el kit en uso ni un hook aún no instalado."""
    return [p for p in inf.piezas if p[0] != "kit en uso" and not (p[0] == "herramienta" and p[2] == "no instalado")]


def deducir(inf: Informe) -> str:
    if not senales(inf):
        return "sin metodología previa"
    if inf.versiones:
        return "; ".join(inf.versiones)
    grupos = {g for g, *_ in senales(inf)}
    if grupos <= {"instrucciones", "herramienta", "motor externo"}:
        return ("sin metodología de coordinación previa (solo instrucciones del proyecto o configuración de la "
                "herramienta, que se conservan)")
    return "metodología previa sin versión declarada (otra metodología o adaptación libre del kit)"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("destino")
    ap.add_argument("--etiqueta", help="nombre a mostrar en lugar del nombre real de la carpeta")
    ap.add_argument("--json", action="store_true", help="salida JSON en lugar de Markdown")
    a = ap.parse_args()
    raiz = Path(a.destino).resolve()
    if not raiz.is_dir():
        print(f"El destino no existe o no es una carpeta: {a.destino}")
        return 2
    inf = detectar(raiz)
    nombre = a.etiqueta or raiz.name
    version = deducir(inf)
    cuenta = {k: sum(1 for p in inf.piezas if p[3] == k) for k in ("REEMPLAZAR", "MIGRAR", "RETIRAR")}
    if a.json:
        json.dump({"destino": nombre, "fecha": date.today().isoformat(), "kit": VERSION, "version_deducida": version,
                   "cuenta": cuenta,
                   "piezas": [dict(zip(("grupo", "ruta", "detalle", "accion", "motivo"), p)) for p in inf.piezas],
                   "entorno": [dict(zip(("pieza", "estado"), x)) for x in inf.entorno]},
                  sys.stdout, ensure_ascii=False, indent=1)
        print()
        return 0
    print(f"# Detección de metodología previa — {nombre}")
    print()
    print(f"Detector del kit coordinador v{VERSION} · {date.today().isoformat()} · solo lectura: no se borró ni "
          "escribió nada en el destino.")
    print()
    print(f"**Versión deducida:** {version}")
    print()
    print(f"**Plan:** {cuenta['REEMPLAZAR']} a reemplazar · {cuenta['MIGRAR']} a migrar · "
          f"{cuenta['RETIRAR']} a retirar")
    print()
    print("**Motor externo en esta máquina** (solo se informa; no es parte del plan):")
    print()
    for pieza, estado in inf.entorno:
        print(f"- `{pieza}`: {estado}")
    print()
    if version.startswith("sin metodología"):
        if not inf.piezas:
            print("No hay piezas de un sistema previo: instalación limpia (el paso 0 termina aquí).")
            return 0
        print("Información, no un plan de migración: no hay piezas de otra metodología. Lo que se lista abajo "
              "(CLAUDE.md, .claude/, la copia del kit) es configuración del editor o el propio kit; la "
              "instalación es limpia y el paso 0 termina aquí.")
        print()
    print("| Grupo | Pieza | Qué hay | Acción | Por qué |")
    print("|---|---|---|---|---|")
    for g, r, d, acc, m in inf.piezas:
        print(f"| {g} | `{r}` | {d} | **{acc}** | {m} |")
    print()
    try:
        kv_local = json.loads((raiz / "coordinador.json").read_text(encoding="utf-8")).get("kit_version")
        kv_kit = json.loads((KIT / "coordinador.example.json").read_text(encoding="utf-8")).get("kit_version")
    except (OSError, ValueError):
        kv_local = kv_kit = None
    if (raiz / "coordinador.json").exists() and kv_local != kv_kit and any("kit" in v for v in inf.versiones):
        script = KIT / "scripts" / "actualizar_kit.py"
        rel = script.relative_to(raiz).as_posix() if raiz in script.parents else str(script)
        print(f"**Hay un kit anterior instalado.** Lo mecánico de la actualización lo hace `actualizar_kit.py`: "
              f"primero el plan (`python3 -I {rel} .`), y con el sí del Director "
              f"`--aplicar` (modo autónomo; `--modo manual` solo si el Director lo pide).")
        print()
    print("Antes de actuar: mostrar este informe al usuario, respaldar en una carpeta con fecha todo lo "
          "que se vaya a REEMPLAZAR o RETIRAR, y pedir su confirmación. Borrar o sobrescribir lo "
          "irrecuperable lo decide el usuario. Lo que se MIGRA conserva sus datos.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
