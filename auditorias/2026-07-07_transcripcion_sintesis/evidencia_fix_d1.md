# Evidencia del fix D1 (truncado por bytes) — ronda 2 (07-07-2026)

## A/B del helper real (compilado de src/lib/truncate.ts con esbuild):
```
PASS — texto corto queda intacto
PASS — CJK: bytes del resultado ≤ 800000 (2828584 bytes de entrada → 799998)
PASS — CJK: bajo el límite real de Firestore
PASS — CJK: termina con el sufijo
PASS — CJK: sin U+FFFD residual
PASS — A/B: la lógica vieja DEBE fallar el límite de bytes (vieja produce 2200056 bytes > 1048576)

RESULTADO: TODOS LOS CHECKS PASAN
```

## Regresión E2E con el fix integrado (audio real, generarSintesis:true):
```
HTTP:201 tiempo:13.96s — actaId: ASlzr3ZXteAdAfNL9QYA
sintesis OK — campos: [actaId, analisis_profundo, contexto_previo, createdAt, ownerId, preguntas_sin_resolver, temas_clave, transcripcion]
transcripcion: 492 chars (contenido fiel al audio; ver sintesis_v4.json de la sesión)
Datos de prueba eliminados tras la captura (DELETE 200/200, usuario Auth borrado).
```
