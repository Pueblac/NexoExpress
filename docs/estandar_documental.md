# Estándar documental — informes para el Director (plantilla del kit, v1.6)

> Se instala en la ruta de `informes.estandar` de `coordinador.json` (por defecto
> `docs/estandar_documental.md`). Lo propio del proyecto va en los marcadores `>>>`; el resto es del kit.
> Sale del Coordinador de Indicadores I+D 2026, donde así se hicieron su memoria técnica, sus minutas y sus
> reportes de calidad (allí, «Estándar Documental R1-R4»).

## Qué es un informe

Un informe es lo que el Director pide como tal: «necesitamos un informe de…», una minuta, un reporte, una
memoria, una respuesta a otro equipo. Va a personas fuera de la cadena de roles. No lo es lo que los roles
producen para trabajar (encargos, fichas, órdenes, entregas, veredictos, bitácora): eso sigue solo en Markdown.

Todo informe se entrega en **dos archivos**: el borrador `.md`, que es la fuente y lo que se verifica, y el
`.docx` renderizado con la plantilla del proyecto. Nadie tiene que pedir el `.docx`: va siempre.

>>> Plantilla del proyecto: `informes.plantilla_docx` (portada, encabezado, pie, estilos). Marcadores que
llena el renderizador: `informes.marcadores`. Quién firma los informes: …

## Cómo se hace (siempre igual)

1. **Encargo.** El Agente C se lo encarga al rol que tiene las fuentes (el que leyó o midió lo que el informe
   cuenta), con el nombre del archivo y el título. En modo manual, el bloque `COPIAR` lo dice igual.
2. **Borrador** en `informes.dir_borradores/<nombre>.md`, con las reglas D1 a D4 de abajo.
3. **Antes de renderizar:** `python -I scripts/verificar_informe.py <borrador> --solo-borrador`. Si dice
   NO CONFORME, se corrige el borrador.
4. **Renderizar:** `python -I scripts/renderizar_informe.py <borrador> --titulo "<título>" [--salida <nombre>.docx]`.
   El `.docx` queda en `informes.dir_informes/` con la huella del borrador en sus propiedades.
5. **Verificar:** `python -I scripts/verificar_informe.py <borrador> [--salida <nombre>.docx]` hasta CONFORME.
6. **Entrega:** la ruta del `.md`, la del `.docx`, la tabla de fuentes de D2 y la salida literal del paso 5.
7. **Compuerta del Agente C:** vuelve a correr el paso 5 y recalcula una muestra de las cifras contra su
   fuente. El `.docx` no se edita a mano: si algo cambia, se cambia el borrador y se vuelve a renderizar.

## Reglas

**D1 — Sin huella.** El informe no nombra herramientas de asistencia (modelos, asistentes, motores, `prompt`,
«agente», «IA») ni el método interno (roles de la cadena con mayúscula, «Agente C», órdenes de ingeniería,
encargos, fichas de encuadre, códigos de ciclo). El trabajo se describe en voz institucional: «se revisó», «se
midió», «revisiones de arquitectura, ingeniería y verificación». `verificar_informe.py` lo mide con la lista
de `informes.huella` y con control positivo. Director y Coordinador son cargos y sí se nombran.

>>> Códigos internos de este proyecto que tampoco salen (van en `informes.huella.metodo_extra`), y palabras
que aquí son legítimas (`informes.huella.permitidos`): …

**D2 — Ninguna cifra de memoria.** Toda cifra sale de un registro verificado del proyecto o se recalcula contra
los datos o el código reales. La entrega trae una tabla de fuentes: cifra, dónde está o con qué comando se
obtuvo, y su salida.

**D3 — Redacción para dos lectores.** Cada sección abre con uno o dos párrafos que entiende una jefatura sin
contexto técnico; el cuerpo mantiene el rigor (fórmulas, tablas, rutas en `código`). Todo término técnico se
define la primera vez. Las advertencias metodológicas van en cita (`>`). Tablas para lo enumerable; prosa para
la narrativa. Voz impersonal, sin primera persona ni nombres de personas.

**D4 — Solo el Markdown que el renderizador entiende.** Títulos `#` a `####` (sin `**` ni `` ` `` dentro),
**negrita**, *cursiva*, `código`, listas, tablas, bloques de código, citas, líneas divisorias e imágenes PNG en
línea propia (`![pie](ruta relativa al borrador)`). **Cada viñeta, ítem numerado o cita va en una sola línea
física**: si se parte, la segunda línea sale como párrafo aparte. Nada de enlaces, notas al pie, HTML ni
diagramas embebidos (Mermaid y similares): salen literales. Un diagrama se renderiza antes a PNG.

## Quitar la huella sin cambiar los hechos

Cuando `verificar_informe.py` marca D1:

- **Herramientas:** la frase se reescribe diciendo qué se hizo y con qué criterio, sin decir con qué. «El
  agente revisó las fórmulas» → «Se revisaron las fórmulas». Si el párrafo entero trata de la herramienta, se
  quita.
- **Método:** el código o el rol se cambian por la acción y, si el porqué lo necesita, la fecha. «Corrección de
  la orden 15» → «corrección del 17-07-2026».
- **Redundancias** (de paso): muletillas («cabe destacar que», «a nivel de»), adverbios de énfasis
  («claramente», «totalmente»), la misma idea dicha dos veces.
- **No se toca:** cifras, fechas, nombres de indicadores, fuentes legales ni decisiones. No se inventa texto
  para rellenar lo que se quitó.

Un documento cuyo tema **son** las herramientas (un reporte de costos de asistentes, por ejemplo) es interno:
no va a `informes.dir_borradores` ni se renderiza con la plantilla del proyecto.

## La plantilla `.docx`

La pone el Director una vez, en `informes.plantilla_docx`. El renderizador la abre y escribe el informe
después de lo que ya tiene (portada incluida). Para que salga bien:

- los marcadores de la portada (`[Nombre_Informe]`, `[dd-mm-yy]`, …) están declarados en `informes.marcadores`;
  los que el proyecto agregue (`[Unidad]`, por ejemplo) también, con su valor;
- tiene los estilos `Heading 1` a `Heading 4` y `Table Grid`; si no trae `List Bullet` o `List Number`, la
  viñeta sale como «• » y el número se escribe tal cual;
- su título en Propiedades se reemplaza por el del informe; el resto de las propiedades (autor, empresa) queda
  como venga en la plantilla.

Sin plantilla declarada, el informe sale en un documento en blanco y el renderizador lo avisa.

## Límites

- Hace falta `python-docx` (`python -m pip install python-docx`).
- No actualiza un índice de contenidos de la plantilla: se actualiza al abrir el documento en Word.
- No trae renderizador de diagramas: el del proyecto de origen manda el texto del diagrama a un servicio web
  externo, y eso solo con el sí del Director para ese proyecto.
- Que el texto no tenga huella lo mide `verificar_informe.py`; que diga la verdad lo mide D2 en la compuerta.
