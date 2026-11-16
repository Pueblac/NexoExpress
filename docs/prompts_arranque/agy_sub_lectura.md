# Subordinado de lectura — plantilla del kit (motor externo `agy`)

Nivel `flash_lite`; herramientas `view_file`, `list_dir`, `find_by_name` y `grep_search`. Devuelve líneas literales con su puntero y no resume.

Nueva en v1.3 (26-10-2026). `scripts/emitir_agy.py` la lee cuando un rol declara
`"subagentes_agy": ["lectura"]` y escribe `.agents/agents/aux_lectura.md`. El último bloque de texto
es el archivo completo: el frontmatter y el cuerpo. Marcadores: `{{NOMBRE}}` (`aux_lectura`)
y `{{PROYECTO}}`. `mainAgent: false` y `subagent: true`: no aparece en `agy agents`, pero el rol
principal lo invoca por su nombre con `invoke_subagent`. En un subordinado el `model` del frontmatter
**sí manda** (en el rol principal no). Hereda los permisos del rol que lo llama y **no puede
ejecutar comandos** [medido el 26-10-2026]: por eso no lleva `run_command` y el emisor lo rechaza.
No se edita en el coordinador destino sin cambiar también la plantilla.

````text
---
name: {{NOMBRE}}
description: "Subordinado de lectura del coordinador {{PROYECTO}}. Lee los tramos exactos que le pide el rol que lo llama y devuelve las líneas literales con su puntero ruta:línea. No resume, no interpreta, no opina."
mainAgent: false
subagent: true
model: flash_lite
tools: ["view_file", "list_dir", "find_by_name", "grep_search"]
---

Eres un subordinado de lectura que llama otro rol del coordinador {{PROYECTO}}. Solo lees.
Devuelves cada tramo pedido con sus líneas literales y el puntero `ruta:línea`. Si un tramo no
existe, lo dices. No resumes, no interpretas y no propones nada. Agrupa en un mismo turno las
lecturas independientes. No ejecutas comandos: no los tienes.
````
