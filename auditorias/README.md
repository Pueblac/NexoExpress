# Expedientes de auditoría dual-IA

Cada ciclo (skill `auditor_externo`) crea una carpeta `{YYYY-MM-DD}_{tema}/`
con archivos numerados por ronda (nomenclatura heredada de OPCG, 07-07-2026):

- `prompt_diseno_rondaN.md` — prompt de revisión de diseño entregado a Gemini.
- `prompt_auditoria_rondaN.md` — prompt de auditoría de código de la ronda N.
- `respuesta_diseno_rondaN.md` / `respuesta_auditoria_rondaN.md` — respuesta
  literal de Gemini + la **validación anti-bluff** del Ingeniero (citas
  verificadas contra el código real) y el dictamen final. Cada ronda nueva
  incrementa N.

**Flujo de una sola escritura (07-07-2026):** cada prompt instruye a Gemini
para que entregue su respuesta como un único documento markdown listo para
archivar. El Director lo guarda tal cual como `respuesta_{fase}_rondaN.md`
en el expediente y avisa al Ingeniero (sin pegarlo en el chat); el Ingeniero
lo lee del disco y le ANEXA su validación anti-bluff y el dictamen.

Estos expedientes son la memoria jurídica del ecosistema: los dictámenes
vigentes se citan por carpeta y fecha. Precedente del formato: repo
`OPCG_Coordinator/scripts/auditorias/` (jul-2026).
