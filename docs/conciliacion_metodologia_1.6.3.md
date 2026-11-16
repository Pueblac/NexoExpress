# Conciliación de la metodología (kit coordinador 1.6.3) — NexoExpress

Rama `metodologia-kit-1.6.3`, creada el 16-11-2026 desde `main` (`e81efcd`). Contiene **solo** las actualizaciones de la metodología que en este PC quedaron sin commit (las de las versiones 1.3.1 a 1.6.3, según el proyecto), en el estado exacto del árbol de trabajo. La rama de trabajo y sus cambios sin commit no se tocaron.

## Cómo comparar y conciliar desde otro PC

```
git fetch origin
git diff --stat main...origin/metodologia-kit-1.6.3      # qué trae la rama
git diff main...origin/metodologia-kit-1.6.3 -- coordinador.json   # una pieza en detalle
git switch main && git merge origin/metodologia-kit-1.6.3   # conciliar (o cherry-pick del commit)
```

**En el PC donde se hizo la actualización** esos mismos cambios están sin commit: un `merge` se negará a sobrescribirlos. Como son idénticos, basta commitearlos en la rama de trabajo agregando por nombre los archivos de la lista de abajo, o guardarlos (`git stash -u`) y fusionar la rama.

## Incluido en la rama (41 archivos)

- `.gitignore`
- `coordinacion/adenda_modo_autonomo.txt`
- `coordinacion/bitacora.md`
- `coordinador.json`
- `docs/estandar_documental.md`
- `docs/migracion_kit_1.6.3_2026-11-14.md`
- `docs/modo_de_trabajo.md`
- `docs/prompts_arranque/agy_capa.md`
- `docs/prompts_arranque/agy_roles.md`
- `docs/prompts_arranque/agy_sub_lectura.md`
- `docs/prompts_arranque/agy_sub_redaccion.md`
- `docs/prompts_arranque/agy_sub_revision.md`
- `docs/prompts_arranque/archivista.md`
- `docs/prompts_arranque/arquitecto.md`
- `docs/prompts_arranque/asesor.md`
- `docs/prompts_arranque/asist_capa_navegador.md`
- `docs/prompts_arranque/asist_encargo_asistente.md`
- `docs/prompts_arranque/asist_encargo_monitor.md`
- `docs/prompts_arranque/asist_plan.md`
- `docs/prompts_arranque/auditor.md`
- `docs/prompts_arranque/especificador.md`
- `docs/prompts_arranque/ingeniero.md`
- `docs/prompts_arranque/verificador.md`
- `scripts/abrir_navegador.py`
- `scripts/actualizar_kit.py`
- `scripts/archivar_bitacora.py`
- `scripts/comprobar_indice.py`
- `scripts/detectar_metodologia.py`
- `scripts/emitir_agy.py`
- `scripts/emitir_arranque.py`
- `scripts/encargar.sh`
- `scripts/herramienta_segura.py`
- `scripts/lanzar_agy.py`
- `scripts/listar_artefactos.py`
- `scripts/medir_asistentes.py`
- `scripts/medir_consumo.py`
- `scripts/proponer_tramos.py`
- `scripts/reanclar_tramos.py`
- `scripts/renderizar_informe.py`
- `scripts/validar_encuadre.py`
- `scripts/verificar_informe.py`

## Fuera de la rama, a propósito (9 archivos sin commit)

- Sin cambios en `kit_coordinador/` versionados.
- **Trabajo propio del proyecto** (no es de la actualización; queda en la rama de trabajo):
  - `auditorias/2026-08-11_traspaso_y_trazabilidad/diseno_f1.md`
  - `auditorias/2026-08-11_traspaso_y_trazabilidad/evidencia_r4.md`
  - `auditorias/2026-08-11_traspaso_y_trazabilidad/fe_de_erratas_f2_ronda1.md`
  - `auditorias/2026-08-11_traspaso_y_trazabilidad/insumo_f1r4.md`
  - `auditorias/2026-08-11_traspaso_y_trazabilidad/prompt_diseno_ronda2.md`
  - `auditorias/2026-08-11_traspaso_y_trazabilidad/respuesta_diseno_ronda2.md`
  - `auditorias/2026-08-11_traspaso_y_trazabilidad/validacion_antibluff_ronda1.md`
  - `docs/estado_actual.md`
  - `scratch/prompt_opus_mejoras.md`

- Respaldos `respaldo_metodologia_*`, la copia `kit_coordinador/` sin versionar, `asistentes/` y los encargos de prueba quedan fuera de git por diseño.

