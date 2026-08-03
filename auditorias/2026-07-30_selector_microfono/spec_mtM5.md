# Spec MT-M5 — Endurecimiento adversarial del selector de micrófono (cierre de tanda)

**Ciclo:** 2026-07-30_selector_microfono · F4 · **Rol:** Ingeniero (Sonnet, rotación asistida)
**Diseño aprobado:** r1 + G1 (30-07). Esta MT cierra la tanda: audita ADVERSARIALMENTE MT-M1..M4 contra el diseño congelado (incluidos los 2 cambios del dictamen), corrige huecos con fixes mínimos y deja evidencia A/B.
**Repo:** `/home/pueblac/AndroidStudioProjects/ActaExpressWeb`, rama `linux`. Working tree esperado: `?? lib/micDevices.ts`, `?? hooks/useMicDevices.ts`, `M hooks/useAudioRecorder.ts`, `M pages/home.tsx`. Puedes tocar ESOS CUATRO archivos, nada más.

## Checklist adversarial (TODAS; veredicto PASA con cita archivo:línea o FALLA+fix con A/B)
1. **Regla de oro:** ningún camino del selector (preferido inválido, exact fallido, swap fallido, ctx no-running, doble swap, API ausente) corta ni impide una grabación. Lista TODOS los `getUserMedia`/vault-like calls nuevos y su manejo de error.
2. **T1 arranque:** ctx que no llega a `running` → fallback directo declarado (`routingDisabledRef`), swap responde "no disponible", grabación idéntica a la de antes del ciclo.
3. **T1 en vuelo (cambio 1):** `onstatechange` → `resume()` presente en el contexto de grabación de AMBOS modos (presencial y el de `mixAudioStreams`). Cita las dos líneas.
4. **T5 (cambio 2):** cerrojo `isSwappingRef` + época: doble click en dos mics → segundo rechazado; perdedor tardío → tracks detenidos sin conectar. Traza ambos.
5. **Orden del swap:** connect-nuevo → disconnect-viejo → stop-viejos, y CERO referencias al MediaRecorder/vault dentro del swap (grep).
6. **Detector re-armado:** tras swap, `setMicStream(newMic)` con el stream CRUDO (no el dest.stream) → `useMicLevel` dep `[active, micStream]` re-crea el analyser. Cita.
7. **Persistencia:** el swap exitoso persiste (`setPreferredMic`); el fallido NO; el preferido inválido al iniciar NO borra la clave (Q2). Citas.
8. **Fugas:** al parar (stopRecording→cleanupStreams): tracks viejos y nuevos detenidos, sources/dest en null, ctx cerrado; y `useMicDevices` sin listener cuando el banner se apaga.
9. **Virtual `"system"`:** sin mic → banner no aparece → CTA inalcanzable; swap con `destRef` presente pero `micSourceRef` null: ¿el swap virtual conecta un mic NUEVO donde antes no había? (Q4 dijo FUERA DE ALCANCE: si el código lo permitiera accidentalmente, es desviación — el guard correcto es que sin banner no hay CTA; verifica si hace falta guard extra en `swapMicrophone` y decláralo).
10. **Sin regresiones de los ciclos previos:** grep de que el vault H6 (createSession/appendChunk) y el guard de captura confiable (texto Q3, sin fallback silencioso virtual) siguen intactos.

## Contrato de fixes
FALLA → fix MÍNIMO en los 4 archivos de la tanda, declarado con traza A/B. Si un fix exigiera cambiar diseño congelado (firmas, política Q2, cerrojo) → DETENTE y decláralo.

## Restricciones
Solo los 4 archivos de la tanda. Sin dependencias nuevas. No commit. NO añadir features.

## DoD (salida literal al informe)
1. `pnpm run typecheck` → exit 0.
2. Tabla checklist 1–10 con veredictos y citas.
3. `git diff --stat` de la tanda completa + diff literal de los fixes propios (o "checklist 10/10 PASA, cero cambios").

## Protocolo de dudas
Ambigüedad fix-mínimo vs diseño: si cabe sin tocar firmas/políticas, hazlo y decláralo; si no, DETENTE.

## Informe: `informe_mtM5.md` — formato estándar (incluye la tabla).
