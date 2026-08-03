# Expediente 2026-07-30_selector_microfono — Verificación F5 del Arquitecto (tanda MT-M1..M5)

**Fecha:** 30-07-2026 · **Modo:** rotación asistida (5 subagentes Sonnet secuenciales, working tree encadenado). Informes en `informe_mtM1.md` … `informe_mtM5.md`.
**Decisión del Director (30-07):** ciclo completo en Linux; el **E2E del caso real (Stereo Mix en el PC Windows del trabajo) queda como DEUDA para mañana** — registrada abajo.

## DoD re-EJECUTADO por el Arquitecto (no leído de los informes)

1. **`git status --short`** → exactamente 4 paths: `useAudioRecorder.ts` (M, +158), `home.tsx` (M, +52), `micDevices.ts` (?? 27 líneas), `useMicDevices.ts` (?? 30 líneas). Coincide con los 5 informes. ✅
2. **`pnpm run typecheck`** re-ejecutado → 4 paquetes `Done`, EXIT=0. ✅
3. **Lectura del diff COMPLETO del recorder** (el archivo crítico) contra el diseño congelado:
   - Enrutamiento presencial con salvaguarda T1-arranque: `running`-check y **fallback declarado** al camino directo con `routingDisabledRef` + warn (fiel a D-B).
   - **Cambio 1 del dictamen:** `attachStateWatch` (onstatechange→resume) aplicado en presencial Y en el ctx de `mixAudioStreams` (extensión a virtual, como se congeló). ✅
   - **Cambio 2:** cerrojo `isSwappingRef` (rechazo del concurrente) + época con stop del "perdedor tardío" + chequeo del estado real del recorder. ✅
   - Orden del swap: connect-nuevo → disconnect-viejo → stop-viejos; CERO referencias a MediaRecorder/vault dentro del swap; `setMicStream(crudo)` re-arma el detector. ✅
   - **Q2:** el preferido inválido deja notice y NO borra la clave (comentario y ausencia de removeItem verificados). `getMicWithPreference` con exact→catch→default; catch externo pre-existente de mic denegado INTACTO. ✅
   - `mixAudioStreams` ampliado (micSource/dest/micPreferredFailed) conservando su try/catch de última capa (semántica "system" intacta). ✅
4. **home.tsx** por grep: `useMicDevices(isRecording && micSilent)` (:108 — lista solo con banner activo, G0-c), toast del `micFallbackNotice` (:112-115), CTA `cta-cambiar-mic` (:387) con `mic-option-*` (:397), `handleSwapMic` con toasts ok/error (:233). Sin ocultamiento optimista del banner. ✅
5. **MT-M5:** checklist adversarial 10/10 PASA, cero fixes; 2 observaciones no bloqueantes declaradas (época parcialmente redundante con el cerrojo — correcto; swap virtual sin-mic inalcanzable por el gating del banner — coincide con Q4 fuera de alcance). Contraste informes-vs-realidad: sin discrepancias. ✅

**Veredicto F5 parte 1 (código): las 5 MTs FIELES al diseño congelado en G1** (D-A..D-E + cambios 1-2 + recomendaciones Q1-Q4). Typecheck verde, 4 archivos, sin dependencias nuevas.

## F5 parte 2 — E2E en LINUX (con el Director)

Nota: en Linux, la entrada "Monitor of…" de PulseAudio es el análogo perfecto del Stereo Mix de Windows (un "micrófono" que no capta tu voz).

| # | Prueba | Resultado esperado |
|---|---|---|
| 1 | Grabar presencial hablando normal | Banner NUNCA aparece; acta fiel (regresión del enrutamiento: la señal pasa por Web Audio y el acta sale igual que siempre) |
| 2 | Grabar presencial con mic MUTEADO en el SO | Banner rojo ≤5 s con el CTA **"Cambiar micrófono"** visible; al abrirlo, lista de dispositivos con nombres amigables |
| 3 | Desde el CTA, elegir OTRA entrada (p. ej. "Monitor of…" con música sonando, o desmutear y re-elegir el mic) | Toast "Micrófono cambiado…"; **la grabación NO se corta**; cuando la nueva entrada da señal, el banner se apaga SOLO; el acta final contiene el audio de ambos tramos |
| 4 | Parar, grabar de NUEVO hablando al mic físico (con el "Monitor" persistido como preferido) | El banner debería aparecer ≤5 s (prueba de que el preferido persistió y se aplicó al iniciar) → cambiar de vuelta al mic real desde el CTA |
| 5 | Recargar y grabar otra vez normal | Toast "Micrófono" solo si el preferido no está disponible (fallback declarado); si está, graba con él sin avisos |
| 6 | Doble click rápido en dos mics del CTA | Segundo intento rechazado con toast "Ya hay un cambio de micrófono en curso" (cerrojo T5) |

## E2E Linux RONDA 1 (30-07) — resultados y F3′

**Reporte del Director con capturas:**
- **P1 ✅ (la crítica):** grabación presencial normal por el enrutamiento Web Audio → acta fiel, banner nunca aparece. El rediseño del corazón de la captura NO degradó nada.
- **P2 ✅ con cambios de producto:** banner rojo con CTA "Cambiar micrófono" y lista funcionando (captura). Dirección del Director: (a) la lista debe ser un **cuadro superpuesto** tipo diálogo de borrado, no dropdown; (b) los labels del navegador no son intuitivos → **nombres amigables**.
- **P3/P4 — limitación de plataforma DOCUMENTADA (no bug):** cambiar de dispositivo no puede des-mutear un mic silenciado en el SO, y "Predeterminado" sigue el ruteo del SO (Linux/PulseAudio pisa la selección al enchufar auriculares). Dirección del Director: nota explicativa en la UI.
- **P5:** graba con lo disponible (aceptado).
- **P6:** no testeable con dropdown (se cerraba al clickear fuera) → el modal la hace testeable.

**F3′ ejecutado (30-07): MT-M7 + MT-M6** (specs+informes en el expediente):
- MT-M7: `friendlyMicName` en micDevices.ts — traducción heurística con el caso Stereo Mix/Monitor marcado como "Audio del sistema (no capta tu voz)" (¡el anti-Stereo-Mix explícito!), auriculares/USB/Bluetooth/interno; label original conservado en `detail`.
- MT-M6: el CTA abre un **modal** (`dialog-selector-mic`, patrón del diálogo de borrado) con opciones por nombre amigable + detalle, **nota del SO** (`nota-so-mic`), cierre solo en swap exitoso (fallo → modal abierto para reintentar; el cerrojo T5 ahora es observable con dos clicks), y el ícono del botón de grabar subido un paso (h-12→h-14, declarado).
- **Verificado por el Arquitecto ejecutando:** typecheck EXIT=0, greps de los marcadores nuevos, `DropdownMenu` eliminado por completo de home.tsx, traductor con el orden de patrones del contrato.

**E2E Linux ronda 2 (30-07, parcial):** P2 re-probada ✅ — el Director aprueba el modal ("así quería que saliera"), el texto del banner y los labels ("excelentes"); captura archivada. Ícono del botón: el paso h-12→h-14 de MT-M6 resultó imperceptible → **ajuste menor del Arquitecto en F5 (declarado): h-14→h-16** (64 px, mitad del botón de 128 px), precedente de ajustes menores sin reabrir F3.

**Ícono del botón — CAUSA RAÍZ encontrada (30-07, tras 2 intentos fallidos):** la base del componente `Button` de shadcn fuerza `[&_svg]:size-4` a todo svg hijo (`components/ui/button.tsx:8`) — NINGÚN cambio de className en el `<Mic>` puede verse. **Fix de una línea pendiente (decisión del Director: "veámoslo después"):** `className="!h-16 !w-16 text-white"` en el `<Mic>` del botón de grabar (o `[&_svg]:!size-16` en ese Button). Los h-14/h-16 ya aplicados quedan inertes pero inocuos.

**Pendiente para cerrar F5-Linux:** fix del ícono (1 línea, arriba) + P6 (doble click en dos opciones del modal → toast "Ya hay un cambio de micrófono en curso").

## DEUDA REGISTRADA — E2E Windows (mañana)

En el PC del trabajo (caso real que motivó el ciclo): poner "Stereo Mix (Realtek)" como mic default de Chrome → grabar presencial → banner rojo → CTA → elegir "Micrófono (Realtek(R) Audio)" → señal → acta fiel SIN tocar chrome://settings. Además verifica T4 bi-máquina: el preferido persistido en Linux no existe en Windows → toast de fallback declarado y grabación normal. **El ciclo NO cierra G2 hasta saldar esta deuda.**

Tras el E2E Linux → F6 (auditoría con diff íntegro) puede correr en paralelo a la deuda; G2 al final.
