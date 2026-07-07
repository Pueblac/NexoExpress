# Respuesta de auditoría de código — Ronda 2 (Gemini 3.1 Pro High)

**Expediente:** 2026-07-07_transcripcion_sintesis
**Recibida:** 07-07-2026 (transportada por el Director, pegada en chat)
**Alcance:** fix del BUG D1 (truncado por bytes) + no-regresión
**Veredicto del auditor:** APROBADO

---

## 1. Respuesta literal del auditor

> Nota de transporte: en la respuesta pegada, el carácter U+FFFD (�) del regex se perdió al copiar del chat (aparece como `/+$/`). El archivo real contiene `/�+$/`. Verificado como artefacto de transporte, no como cita falsa.

C1 → EVIDENCIA (truncate.ts:5-9): if (Buffer.byteLength(texto, "utf8") <= maxBytes) return texto; const presupuesto = maxBytes - Buffer.byteLength(sufijo, "utf8"); const corte = Buffer.from(texto, "utf8").subarray(0, presupuesto).toString("utf8"); return corte.replace(/�+$/, "") + sufijo; → TRAZA: (a) Si ya cabe, el if temprano retorna el texto intacto sin sufijo. (b) Para texto multibyte masivo, presupuesto recorta a exactamente maxBytes menos los bytes reales del sufijo. (c) Si el corte secciona un carácter multibyte por la mitad, toString("utf8") sustituye ese byte inválido final por U+FFFD, el cual el regex elimina limpiamente. Como eliminar el U+FFFD quita 3 bytes y no agrega nada, byteLength(corte_limpio) siempre es <= presupuesto. Al sumar el sufijo, el resultado total siempre será <= maxBytes. → VEREDICTO: CONFIRMADO.

C2 → EVIDENCIA (actas.ts:10, actas.ts:71-72, actas.ts:201): import { truncarPorBytes } from "../lib/truncate.js";, const SINTESIS_MAX_BYTES = 800_000;, const transcripcion = truncarPorBytes(parsed.transcripcion, SINTESIS_MAX_BYTES, SINTESIS_TRUNC_SUFFIX); → TRAZA: Toda referencia antigua a SINTESIS_MAX_CHARS y el antiguo .slice() han sido erradicados del archivo. La lógica de fondo depende enteramente de la nueva constante explícitamente anotada como BYTES y la llamada al nuevo helper de utilidades. → VEREDICTO: CONFIRMADO.

C3 → EVIDENCIA (evidencia_fix_d1.md:6, evidencia_fix_d1.md:10): PASS — CJK: bytes del resultado ≤ 800000 (2828584 bytes de entrada → 799998), PASS — A/B: la lógica vieja DEBE fallar el límite de bytes (vieja produce 2200056 bytes > 1048576) → TRAZA: La ejecución experimental demuestra que la entrada masiva produce salida de 799,998 bytes, lo cual es estrictamente menor o igual al límite propuesto de 800,000. Además, certifica que la lógica antigua en caracteres provocaba silenciosamente un output de 2,200,056 bytes (violando el límite duro de Firestore, materializando la trampa T3 que se predecía). → VEREDICTO: CONFIRMADO.

C4 → EVIDENCIA (evidencia_fix_d1.md:17-19): HTTP:201 tiempo:13.96s — actaId: ASlzr3ZXteAdAfNL9QYA... transcripcion: 492 chars (contenido fiel al audio... → TRAZA: Transcripción corta de 492 caracteres cumple con la primera línea temprana de truncarPorBytes que esquiva el truncado y la adición del sufijo. El JSON del endpoint se inyecta en Firestore sin fallos colaterales introducidos por el Buffer de Node, y la latencia HTTP se mantiene inafectada por la operación en background. → VEREDICTO: CONFIRMADO.

Dudas declaradas por el implementador

D1: Riesgo de maxBytes < byteLength(sufijo). Postura: OBSERVACIÓN. Dado que SINTESIS_MAX_BYTES está rígidamente fijado en la constante probada de 800_000 (inmensamente mayor que los ~57 bytes del sufijo), el riesgo en este dominio es estrictamente teórico. Se aconseja añadir a futuro un if (maxBytes < Buffer.byteLength(sufijo)) throw new Error(...) en el helper para blindarlo contra re-usos imprudentes por otros desarrolladores, pero no amerita detener este despliegue.

D2: El regex elimina U+FFFD legítimos en el límite de corte. Postura: OBSERVACIÓN. El carácter de reemplazo (U+FFFD) se usaría legítimamente en transcripciones con errores de codec previos o si el usuario hablara sobre el carácter. Perderlo al final exacto de un corte de 800KB es trivial, estadísticamente irrisorio y puramente estético.

Preguntas de control (Q1-Q3)

Q1: Cuerpo completo de truncarPorBytes:

```typescript
4: export function truncarPorBytes(texto: string, maxBytes: number, sufijo: string): string {
5:   if (Buffer.byteLength(texto, "utf8") <= maxBytes) return texto;
6:   const presupuesto = maxBytes - Buffer.byteLength(sufijo, "utf8");
7:   const corte = Buffer.from(texto, "utf8").subarray(0, presupuesto).toString("utf8");
8:   // cortar en medio de un carácter multibyte deja U+FFFD al final del decode
9:   return corte.replace(/�+$/, "") + sufijo;
10: }
```

Q2: Traza truncarPorBytes("ñ".repeat(10), 12, "!"): Entrada: 10 veces "ñ" (2 bytes UTF-8 cada una = 20 bytes). maxBytes: 12. sufijo: "!" (1 byte). Línea 5: 20 <= 12 es Falso. Línea 6: presupuesto = 12 - 1 = 11 bytes. Línea 7: subarray(0, 11) extrae 11 bytes: 5 "ñ" (10 bytes) + el byte 0xC3 huérfano de la sexta "ñ", que toString("utf8") convierte en U+FFFD. corte = "ñññññ�". Línea 9: se borra el U+FFFD y se concatena "!", resultado exacto "ñññññ!". ByteLength final: 10 + 1 = 11 bytes (<= 12).

Q3: Se invoca en la línea 201: const transcripcion = truncarPorBytes(parsed.transcripcion, SINTESIS_MAX_BYTES, SINTESIS_TRUNC_SUFFIX);. El valor retornado se asume en la constante local transcripcion, la cual se empaqueta en sintesisData (línea 205) antes de ejecutar firestoreSet.

Anti-aprobación-automática (Trampas y refutaciones)

T1 (sufijo multibyte): No aplica. La línea 6 usa Buffer.byteLength(sufijo, "utf8") — peso binario real, no sufijo.length. T2 (entrada vacía/corta): No aplica. La condición de escape de la línea 5 retorna temprano sin operaciones de índice negativas. T3 (test sobre copia): La línea 3 de evidencia_fix_d1.md expone "A/B del helper real (compilado de src/lib/truncate.ts con esbuild)" — se probó la función real compilada, no un clon.

Veredicto Global: APROBADO

---

## 2. Validación anti-bluff del Ingeniero (07-07-2026)

| Verificación | Método | Resultado |
|---|---|---|
| Q1 (truncate.ts:4-10 textual) | `sed -n '4,10p'` | Coincidencia exacta, línea por línea. ✅ |
| actas.ts:10 / 71-72 / 201 / 205 | `sed` | Coinciden textuales. ✅ |
| C2: cero referencias a SINTESIS_MAX_CHARS | `grep -c` | 0 ocurrencias. ✅ |
| **Q2: traza simbólica vs ejecución REAL** | helper compilado ejecutado con esos valores | Resultado real: `"ñññññ!"`, byteLength 11 — **idéntico a la traza del auditor**. ✅ |
| T2: entrada vacía | ejecución real | `""` retornado sin lanzar. ✅ |
| evidencia_fix_d1.md:6 y :10 | `sed` | Coinciden. ✅ |
| Regex citado como `/+$/` | inspección del archivo real | U+FFFD perdido al pegar en chat; el archivo tiene `/�+$/`. Artefacto de transporte, NO cita falsa. ✅ |

**Resultado: auditoría VÁLIDA.**

## 3. Dictamen final del ciclo

**APROBADO en ronda 2 + aprobación explícita del Director (07-07-2026) = CICLO CERRADO.**

- BUG D1 corregido y verificado con A/B sobre el código real compilado.
- D1-r2 (guard de maxBytes < sufijo): observación aceptada; se adopta como mejora sugerida NO bloqueante para un ciclo futuro.
- D2-r2: observación sin acción.
- Autorización de cierre: commit + push de ActaExpressWeb y NexoExpress, bitácora y estado actualizados (documentador_sesion).
