"""Renderiza un informe: borrador Markdown (+ imágenes PNG) → .docx sobre la plantilla del proyecto (kit coordinador v1.6.0).

Lo usa el rol al que el Agente C le encarga un informe que pidió el Director. El borrador `.md` es la fuente
y lo que se verifica; el `.docx` se genera desde él y no se edita a mano. Después se corre
`scripts/verificar_informe.py <borrador>`.

Todo sale de la sección `informes` de `coordinador.json` (si falta, valen los valores por defecto):

  · `dir_borradores` (docs/borradores) y `dir_informes` (docs/informes);
  · `plantilla_docx` (docs/plantilla.docx): el .docx del proyecto con su portada, encabezado, pie y estilos.
    Declarada y ausente → STOP (exit 2). Sin declarar y ausente → documento en blanco, con AVISO;
  · `marcadores`: texto de la plantilla → valor. El valor puede llevar {titulo}, {fecha} (dd-mm-aaaa) y
    {mes_anio} («Noviembre 2026»). Se reemplazan en el cuerpo, las tablas, los encabezados y los pies.

Markdown que entiende (estándar documental, regla D4 de `plantillas/estandar_documental.md`): títulos #…####,
**negrita**, *cursiva* y `código` en línea, listas con viñetas y numeradas (cada ítem en UNA línea física),
tablas, bloques de código, citas (`>`, una línea física), líneas divisorias e imágenes en línea propia
(`![pie](ruta relativa al borrador)`). Lo demás (enlaces, notas al pie, HTML, Mermaid) sale literal: el
renderizador lo avisa y `verificar_informe.py` lo marca FALLA.

El .docx lleva la huella del borrador en sus propiedades (identificador `sha256:<16>`): así se comprueba que
viene del borrador vigente.

Origen: `scripts/renderizar_informe.py` del Coordinador de Indicadores I+D 2026, que lo usó en todos sus
informes. La lectura del Markdown es la misma; con la misma plantilla y los mismos marcadores, el cuerpo del
documento sale idéntico.

KIT COORDINADOR — no hay rutas absolutas: el workspace sale de la ubicación del script.

Uso:
    python -I scripts/renderizar_informe.py docs/borradores/x.md
    python -I scripts/renderizar_informe.py docs/borradores/x.md --titulo "Informe X" --salida Informe_X.docx
    python -I scripts/renderizar_informe.py docs/borradores/x.md --marcador "[Unidad]=Departamento Y"
    # exit 0 = generado; 1 = generado con avisos que lo dejan incompleto (imagen que falta);
    # 2 = no se generó (uso, configuración, plantilla declarada que no existe, falta python-docx)
"""

import argparse
import datetime
import hashlib
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = Path(__file__).resolve().parents[1]

POR_DEFECTO = {
    "dir_borradores": "docs/borradores",
    "dir_informes": "docs/informes",
    "plantilla_docx": "docs/plantilla.docx",
    "marcadores": {
        "[Nombre_Informe]": "{titulo}", "{Nombre_Informe}": "{titulo}",
        "[dd-mm-yy]": "{fecha}", "{dd-mm-yy}": "{fecha}",
        "[Fecha]": "{fecha}", "{Fecha}": "{fecha}",
        "[MesAnio]": "{mes_anio}", "{MesAnio}": "{mes_anio}",
    },
}

MESES = ("Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
         "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre")

try:
    from docx import Document
    from docx.shared import Inches, Pt
except ImportError:          # el aviso se da en main(): verificar_informe.py importa este módulo
    Document = None

ANCHO_MAX_IMAGEN = Inches(6) if Document else None
IMAGEN_FALTANTE = "[Imagen no encontrada: "


# ---------------------------------------------------------------- configuración

class ErrorDeConfiguracion(Exception):
    """coordinador.json ilegible: el script sale con 2."""


def cargar_config():
    """Sección `informes` de coordinador.json con los valores por defecto. Devuelve (cfg, declarada)."""
    ruta = BASE / "coordinador.json"
    cfg_total = {}
    if ruta.exists():
        try:
            cfg_total = json.loads(ruta.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            raise ErrorDeConfiguracion(f"STOP: no se pudo leer {ruta}: {e}")
    sec = cfg_total.get("informes") or {}
    cfg = dict(POR_DEFECTO)
    cfg["marcadores"] = dict(POR_DEFECTO["marcadores"])
    for k, v in sec.items():
        if k.startswith("_"):
            continue
        if k == "marcadores" and isinstance(v, dict):
            cfg["marcadores"] = {mk: mv for mk, mv in v.items() if not mk.startswith("_")}
        else:
            cfg[k] = v
    cfg["_huella_cfg"] = sec.get("huella") or {}
    cfg["_roles"] = [r for r in (cfg_total.get("roles") or {}) if not r.startswith("_")]
    return cfg, "plantilla_docx" in sec


def ruta_del_proyecto(rel):
    p = Path(rel)
    return p if p.is_absolute() else BASE / p


def huella_borrador(ruta_md):
    return "sha256:" + hashlib.sha256(ruta_md.read_bytes()).hexdigest()[:16]


def valores_marcadores(marcadores, titulo, hoy, extra):
    fecha = hoy.strftime("%d-%m-%Y")
    mes_anio = f"{MESES[hoy.month - 1]} {hoy.year}"
    valores = {}
    for clave, plantilla in marcadores.items():
        valores[clave] = (str(plantilla).replace("{titulo}", titulo).replace("{fecha}", fecha)
                          .replace("{mes_anio}", mes_anio))
    valores.update(extra)
    return valores


# ---------------------------------------------------------------- plantilla

def parrafos_de_plantilla(doc):
    """Párrafos del cuerpo, de las tablas del cuerpo y de encabezados y pies de cada sección."""
    def de_tablas(tablas):
        for tabla in tablas:
            for fila in tabla.rows:
                for celda in fila.cells:
                    yield from celda.paragraphs
    yield from doc.paragraphs
    yield from de_tablas(doc.tables)
    vistos = set()
    for s in doc.sections:
        for parte in (s.header, s.footer, s.first_page_header, s.first_page_footer,
                      s.even_page_header, s.even_page_footer):
            if parte.is_linked_to_previous or id(parte._element) in vistos:
                continue
            vistos.add(id(parte._element))
            yield from parte.paragraphs
            yield from de_tablas(parte.tables)


def reemplazar_placeholders(doc, valores):
    """Reemplaza los marcadores en la plantilla (primero run a run; si uno quedó partido entre runs, en el párrafo)."""
    for p in parrafos_de_plantilla(doc):
        for clave, valor in valores.items():
            if clave in p.text:
                for run in p.runs:
                    if clave in run.text:
                        run.text = run.text.replace(clave, valor)
                if clave in p.text:
                    p.text = p.text.replace(clave, valor)


# ---------------------------------------------------------------- Markdown → Word (igual que en el origen)

def agregar_texto_con_formato(parrafo, texto):
    """Convierte **negrita**, *cursiva* y `código` inline en runs de Word."""
    patron = re.compile(r"(\*\*.+?\*\*|\*.+?\*|`.+?`)")
    for trozo in patron.split(texto):
        if not trozo:
            continue
        if trozo.startswith("**") and trozo.endswith("**"):
            parrafo.add_run(trozo[2:-2]).bold = True
        elif trozo.startswith("*") and trozo.endswith("*"):
            parrafo.add_run(trozo[1:-1]).italic = True
        elif trozo.startswith("`") and trozo.endswith("`"):
            run = parrafo.add_run(trozo[1:-1])
            run.font.name = "Consolas"
            run.font.size = Pt(9)
        else:
            parrafo.add_run(trozo)


def insertar_imagen(doc, ruta_imagen, alt, faltantes, como_se_escribio):
    if ruta_imagen.exists():
        doc.add_picture(str(ruta_imagen), width=ANCHO_MAX_IMAGEN)
        if alt:
            pie = doc.add_paragraph()
            pie.alignment = 1  # centrado
            run = pie.add_run(alt)
            run.italic = True
            run.font.size = Pt(9)
    else:
        faltantes.append(str(ruta_imagen))
        p = doc.add_paragraph()
        run = p.add_run(f"{IMAGEN_FALTANTE}{como_se_escribio}]")     # la ruta del borrador, no la de la máquina
        run.italic = True


def insertar_tabla(doc, filas_md):
    filas = []
    for linea in filas_md:
        celdas = [c.strip() for c in linea.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-{3,}:?", c) for c in celdas):     # fila separadora |---|---|
            continue
        filas.append(celdas)
    if not filas:
        return
    n_cols = max(len(f) for f in filas)
    tabla = doc.add_table(rows=len(filas), cols=n_cols)
    try:
        tabla.style = "Table Grid"
    except (KeyError, ValueError):
        pass                                                       # plantilla sin ese estilo: tabla sin bordes
    for i, fila in enumerate(filas):
        for j, celda in enumerate(fila):
            parrafo = tabla.rows[i].cells[j].paragraphs[0]
            agregar_texto_con_formato(parrafo, celda)
            if i == 0:
                for run in parrafo.runs:
                    run.bold = True


def insertar_bloque_codigo(doc, lineas):
    for linea in lineas:
        p = doc.add_paragraph()
        run = p.add_run(linea if linea else " ")
        run.font.name = "Consolas"
        run.font.size = Pt(9)
        p.paragraph_format.space_after = Pt(0)


INICIO_DE_BLOQUE = re.compile(r"(#{1,4}\s|[-*+]\s|\d+[.)]\s|\||```|!\[|>)")


def renderizar_markdown(doc, ruta_md, faltantes):
    lineas = ruta_md.read_text(encoding="utf-8").splitlines()
    i = 0
    while i < len(lineas):
        limpia = lineas[i].strip()

        if not limpia:
            i += 1
            continue

        if limpia.startswith("```"):
            bloque = []
            i += 1
            while i < len(lineas) and not lineas[i].strip().startswith("```"):
                bloque.append(lineas[i])
                i += 1
            insertar_bloque_codigo(doc, bloque)
            i += 1
            continue

        if limpia.startswith("|"):
            filas_md = []
            while i < len(lineas) and lineas[i].strip().startswith("|"):
                filas_md.append(lineas[i])
                i += 1
            insertar_tabla(doc, filas_md)
            continue

        m_img = re.fullmatch(r"!\[(.*?)\]\((.+?)\)", limpia)
        if m_img:
            alt, ruta_rel = m_img.group(1), m_img.group(2)
            insertar_imagen(doc, (ruta_md.parent / ruta_rel).resolve(), alt, faltantes, ruta_rel)
            i += 1
            continue

        m_titulo = re.match(r"(#{1,4})\s+(.*)", limpia)
        if m_titulo:
            doc.add_heading(m_titulo.group(2).strip(), level=len(m_titulo.group(1)))
            i += 1
            continue

        if re.fullmatch(r"[-*_]{3,}", limpia):
            i += 1
            continue

        m_vineta = re.match(r"[-*+]\s+(.*)", limpia)
        m_numerada = re.match(r"(\d+[.)])\s+(.*)", limpia)
        if m_vineta or m_numerada:
            estilo = "List Bullet" if m_vineta else "List Number"
            contenido = m_vineta.group(1) if m_vineta else m_numerada.group(2)
            try:
                p = doc.add_paragraph(style=estilo)
            except KeyError:
                # Plantilla sin el estilo: la viñeta se escribe «• » y el número se conserva tal cual
                # (el renderizador de origen lo perdía: «1. Algo» salía «Algo»).
                p = doc.add_paragraph()
                contenido = ("• " if m_vineta else f"{m_numerada.group(1)} ") + contenido
            agregar_texto_con_formato(p, contenido)
            i += 1
            continue

        if limpia.startswith(">"):
            p = doc.add_paragraph()
            agregar_texto_con_formato(p, limpia.lstrip("> ").strip())
            for run in p.runs:
                run.italic = True
            i += 1
            continue

        parrafo_lineas = [limpia]                                  # párrafo normal: une líneas contiguas
        while (i + 1 < len(lineas) and lineas[i + 1].strip()
               and not INICIO_DE_BLOQUE.match(lineas[i + 1].strip())
               and not re.fullmatch(r"[-*_]{3,}", lineas[i + 1].strip())):
            i += 1
            parrafo_lineas.append(lineas[i].strip())
        p = doc.add_paragraph()
        agregar_texto_con_formato(p, " ".join(parrafo_lineas))
        i += 1


# ---------------------------------------------------------------- lo que el renderizador no entiende

ENLACE = re.compile(r"(?<!!)\[[^\]]+\]\([^)]+\)")
NOTA_AL_PIE = re.compile(r"\[\^[^\]]+\]")
HTML = re.compile(r"</?[a-zA-Z][a-zA-Z0-9]*(\s[^<>]*)?/?>")


def revisar_markdown(lineas):
    """Lo que saldría mal en el .docx. Devuelve una lista de (línea, qué). Lo usa también verificar_informe.py."""
    hallazgos = []
    en_codigo = False
    previa = ""          # tipo de la línea anterior con texto: "item", "cita" u otro
    for n, linea in enumerate(lineas, 1):
        limpia = linea.strip()
        if limpia.startswith("```"):
            if not en_codigo and limpia[3:].strip().lower() in ("mermaid", "plantuml", "dot"):
                hallazgos.append((n, f"diagrama embebido ({limpia[3:].strip()}): saldrá como código; renderízalo a PNG"))
            en_codigo = not en_codigo
            previa = ""
            continue
        if en_codigo:
            continue
        if not limpia:
            previa = ""
            continue
        es_item = bool(re.match(r"([-*+]|\d+[.)])\s+", limpia))
        es_cita = limpia.startswith(">")
        if previa in ("item", "cita") and not INICIO_DE_BLOQUE.match(limpia) \
                and not re.fullmatch(r"[-*_]{3,}", limpia):
            hallazgos.append((n, f"{'viñeta' if previa == 'item' else 'cita'} partida en más de una línea física: "
                                 "esta línea saldrá como párrafo aparte"))
        if ENLACE.search(limpia):
            hallazgos.append((n, "enlace Markdown: saldrá literal ([texto](url)); escribe el texto sin enlace"))
        if NOTA_AL_PIE.search(limpia):
            hallazgos.append((n, "nota al pie: no se procesa"))
        if HTML.search(limpia) and not limpia.startswith("|"):
            hallazgos.append((n, "HTML crudo: saldrá literal"))
        if re.match(r"#{5,}\s", limpia):
            hallazgos.append((n, "título de nivel 5 o más: saldrá como párrafo con los #"))
        elif re.match(r"#{1,4}\s.*(\*|`)", limpia):
            hallazgos.append((n, "título con ** , * o ` : en un título salen literales"))
        previa = "item" if es_item else ("cita" if es_cita else "")
    return hallazgos


# ---------------------------------------------------------------- principal

def main(argv=None):
    ap = argparse.ArgumentParser(description="Renderiza un borrador Markdown a .docx con la plantilla del proyecto.")
    ap.add_argument("markdown", help="borrador .md (relativo a la raíz del coordinador o absoluto)")
    ap.add_argument("--titulo", help="título para los marcadores (por defecto, el nombre del archivo)")
    ap.add_argument("--salida", help="nombre del .docx (por defecto, el del .md); va a informes.dir_informes")
    ap.add_argument("--marcador", action="append", default=[], metavar="CLAVE=VALOR",
                    help="valor de un marcador para este informe (se puede repetir)")
    args = ap.parse_args(argv)

    if Document is None:
        print("STOP: falta python-docx. Instálalo con: python -m pip install python-docx")
        return 2

    try:
        cfg, declarada = cargar_config()
    except ErrorDeConfiguracion as e:
        print(e)
        return 2
    ruta_md = ruta_del_proyecto(args.markdown)
    if not ruta_md.exists():
        print(f"STOP: no se encontró el borrador: {ruta_md}")
        return 2

    extra = {}
    for m in args.marcador:
        if "=" not in m:
            print(f"STOP: --marcador espera CLAVE=VALOR, recibió {m!r}")
            return 2
        k, v = m.split("=", 1)
        extra[k] = v

    avisos = []
    plantilla = ruta_del_proyecto(cfg["plantilla_docx"]) if cfg.get("plantilla_docx") else None
    if plantilla and plantilla.exists():
        doc = Document(str(plantilla))
    elif plantilla and declarada:
        print(f"STOP: informes.plantilla_docx declara {plantilla} y no existe. Ponla ahí o corrige la ruta.")
        return 2
    else:
        doc = Document()
        doc.core_properties.author = ""                  # el documento en blanco trae «python-docx» como autor
        doc.core_properties.comments = ""                # y «generated by python-docx» como comentario
        avisos.append("sin plantilla del proyecto: documento en blanco (declara informes.plantilla_docx)")

    titulo = args.titulo or ruta_md.stem.replace("_", " ").title()
    doc.core_properties.title = titulo                   # si no, queda el título que traía la plantilla
    reemplazar_placeholders(doc, valores_marcadores(cfg["marcadores"], titulo, datetime.date.today(), extra))

    lineas = ruta_md.read_text(encoding="utf-8").splitlines()
    for n, que in revisar_markdown(lineas):
        avisos.append(f"línea {n}: {que}")

    faltantes = []
    renderizar_markdown(doc, ruta_md, faltantes)
    sello = huella_borrador(ruta_md)
    doc.core_properties.identifier = sello

    dir_informes = ruta_del_proyecto(cfg["dir_informes"])
    dir_informes.mkdir(parents=True, exist_ok=True)
    ruta_salida = dir_informes / (args.salida or f"{ruta_md.stem}.docx")
    doc.save(str(ruta_salida))

    print(f"Informe generado: {ruta_salida}")
    print(f"Borrador: {ruta_md} ({sello})")
    print(f"Plantilla: {plantilla if plantilla and plantilla.exists() else '(ninguna)'}")
    for r in faltantes:
        avisos.append(f"imagen que no existe: {r}")
    for a in avisos:
        print(f"AVISO: {a}")
    print(f"Siguiente paso: python -I scripts/verificar_informe.py {args.markdown}"
          + (f" --salida {args.salida}" if args.salida else ""))
    return 1 if faltantes else 0


if __name__ == "__main__":
    sys.exit(main())
