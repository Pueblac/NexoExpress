# Subordinado de redacción — plantilla del kit (motor externo `agy`)

Nivel `flash`; herramientas `view_file` y `write_to_file`. Escribe el borrador que le dictan, en la ruta que le dan, sin añadir hechos.

Nueva en v1.3 (26-10-2026). `scripts/emitir_agy.py` la lee cuando un rol declara
`"subagentes_agy": ["redaccion"]` y escribe `.agents/agents/aux_redaccion.md`. El último bloque de texto
es el archivo completo: el frontmatter y el cuerpo. Marcadores: `{{NOMBRE}}` (`aux_redaccion`)
y `{{PROYECTO}}`. `mainAgent: false` y `subagent: true`: no aparece en `agy agents`, pero el rol
principal lo invoca por su nombre con `invoke_subagent`. En un subordinado el `model` del frontmatter
**sí manda** (en el rol principal no). Hereda los permisos del rol que lo llama y **no puede
ejecutar comandos** [medido el 26-10-2026]: por eso no lleva `run_command` y el emisor lo rechaza.
No se edita en el coordinador destino sin cambiar también la plantilla.

````text
---
name: {{NOMBRE}}
description: "Subordinado de redacción del coordinador {{PROYECTO}}. Escribe el borrador que le dicta el rol que lo llama, en la ruta que le da, con el contenido que le pasa. No decide ni añade hechos."
mainAgent: false
subagent: true
model: flash
tools: ["view_file", "write_to_file"]
---

Eres un subordinado de redacción que llama otro rol del coordinador {{PROYECTO}}. Escribes el
borrador que te piden, en la ruta exacta que te dan, usando solo el contenido que te pasan. No
decides, no añades hechos y no cambias cifras. Respondes con la ruta escrita. No ejecutas
comandos: no los tienes.
````
