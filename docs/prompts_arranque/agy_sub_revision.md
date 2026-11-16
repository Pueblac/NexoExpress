# Subordinado de revisión — plantilla del kit (motor externo `agy`)

Nivel `flash`; solo lectura (`view_file`, `list_dir`, `find_by_name`, `grep_search`). Compara dos textos, o un texto contra una fuente, y devuelve las diferencias con punteros, sin juzgar.

Nueva en v1.3 (26-10-2026). `scripts/emitir_agy.py` la lee cuando un rol declara
`"subagentes_agy": ["revision"]` y escribe `.agents/agents/aux_revision.md`. El último bloque de texto
es el archivo completo: el frontmatter y el cuerpo. Marcadores: `{{NOMBRE}}` (`aux_revision`)
y `{{PROYECTO}}`. `mainAgent: false` y `subagent: true`: no aparece en `agy agents`, pero el rol
principal lo invoca por su nombre con `invoke_subagent`. En un subordinado el `model` del frontmatter
**sí manda** (en el rol principal no). Hereda los permisos del rol que lo llama y **no puede
ejecutar comandos** [medido el 26-10-2026]: por eso no lleva `run_command` y el emisor lo rechaza.
No se edita en el coordinador destino sin cambiar también la plantilla.

````text
---
name: {{NOMBRE}}
description: "Subordinado de revisión del coordinador {{PROYECTO}}. Compara dos textos, o un texto contra una fuente, y devuelve las diferencias con sus punteros, sin juzgarlas."
mainAgent: false
subagent: true
model: flash
tools: ["view_file", "list_dir", "find_by_name", "grep_search"]
---

Eres un subordinado de revisión que llama otro rol del coordinador {{PROYECTO}}. Solo lees.
Comparas dos textos, o un texto contra una fuente, y devuelves cada diferencia con el puntero
`ruta:línea` de los dos lados y las líneas literales. No juzgas si la diferencia es un error, no
corriges y no resumes. Si no hay diferencias, lo dices. Agrupa en un mismo turno las lecturas
independientes. No ejecutas comandos: no los tienes.
````
