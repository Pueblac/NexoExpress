### 1. Verificación de Claims

| Claim | Análisis | Veredicto |
| :--- | :--- | :--- |
| **C1** | **ANÁLISIS**: El contexto verifica que presencial hoy usa `getUserMedia({ audio: { echoCancellation: false, noiseSuppression: false, autoGainControl: true } })` (`useAudioRecorder.ts:162-167`) y va al MediaRecorder (`:224`). D-B mantiene estas exactas constraints en el track fuente y conecta a `createMediaStreamDestination()`. Este pipeline idéntico ya funciona y se usa en captura virtual (`mixAudioStreams`, `:95-120`). Ya que la sesión guarda el `mimeType` del recorder y el MediaRecorder procesa este mismo `dest.stream` sin fallas comprobadas en virtual, el archivo y la calidad del track raíz se preservan. | **SÓLIDO** |
| **C2** | **ANÁLISIS**: El contexto es claro: "MediaRecorder NO tolera cambiar los tracks". D-B instruye que "el MediaRecorder graba `dest.stream`". D-C estipula un "orden connect-nuevo → disconnect-viejo" sobre el AudioContext, aislando al recorder. Al no alterarse jamás el track inmutable del `dest.stream`, la escritura de "chunks de 1 s a IndexedDB" bajo la misma sesión en el Vault H6 fluye ininterrumpidamente. | **SÓLIDO** |
| **C3** | **ANÁLISIS**: El detector depende de `useMicLevel.ts`, donde "su useEffect depende de `[active, micStream]` → si micStream CAMBIA de instancia, se destruye el AnalyserNode viejo y se crea uno sobre el nuevo". D-C inyecta la nueva instancia ejecutando explícitamente `setMicStream(newMicStream)`. El re-arme orgánico del useEffect está garantizado por el contexto sin requerir código extra. | **SÓLIDO** |
| **C4** | **ANÁLISIS**: El contexto ordena que "la grabación JAMÁS se sacrifica por el enrutamiento". D-E dispone un "fallback DECLARADO... continuar con default" si falla el exact/preferido. D-C decreta que ante un swap fallido "la grabación SIGUE con el mic anterior intacto". D-B tiene un timeout corto y fallback si no llega a `running`. Los fallos listados están mitigados en inicio y swap. | **SÓLIDO** (Para los fallos iniciales listados; la resiliencia en vuelo asíncrono falla ante T1). |
| **C5** | **ANÁLISIS**: Contexto: "Restricción... 100% frontend". D-A confina los datos a `localStorage` con la convención actual (`actaexpress:micDeviceId:${uid}`). D-C declara sobre virtual en mode system: "el swap queda fuera de alcance", evitando intervenir en flujos sin micrófono que no activan el banner (`home.tsx:~505`). Cero alteraciones de Backend o flujos subyacentes. | **SÓLIDO** |

### 2. Respuestas a Preguntas de Diseño

- **Q1:** **AudioContext NUEVO por grabación (reutilizando `audioCtxRef` y la limpieza existente).**
  *Justificación:* El patrón de limpieza y gestión de ciclo de vida atado a la grabación ya existe y es seguro (`cleanupStreams:147-151`). Un contexto compartido de larga vida introduce altos riesgos con las Autoplay Policies (que dictan que un contexto suspendido exige interacción reciente de usuario para hacer `resume`). Crear el contexto en la misma pila de llamadas del inicio presencial hereda la interacción del usuario directamente y previene contextos zombies.

- **Q2:** **Avisar y MANTENER la clave.**
  *Justificación:* Un fallo en un micrófono preferido suele ser un estado transitorio (por ejemplo, los audífonos Bluetooth no se conectaron hoy a tiempo, o el micrófono USB no está en la mochila). Si se purga la persistencia, se castiga al usuario forzándolo a reconfigurarla mañana. Avisar que se usará el predeterminado y conservar la clave es resiliente y prioriza la conveniencia a largo plazo.

- **Q3:** **Re-arme natural (`lastLoudAt` → ahora) del useEffect sin lógica extra.**
  *Justificación:* Según el contexto de `useMicLevel`, el reseteo ocurre naturalmente cuando el `micStream` cambia de instancia. Dada la ventana de gracia de 5 segundos en presencial antes de que se dispare el trigger destructivo rojo, el breve hueco de cientos de milisegundos del `getUserMedia` es silenciosamente absorbido por el inicio del nuevo `AnalyserNode`. Añadir lógicas extras de bloqueo (debounce en UI) es añadir complejidad muerta.

- **Q4:** **Fuera de alcance.**
  *Justificación:* El banner H4 ámbar no se renderiza sin un fallo de volumen comprobado (`isRecording && micSilent`), y el detector H4 no opera si no existe un `micStream`. Añadir un CTA para iniciar hardware "de la nada" obligaría a diseñar nueva UI externa al banner H4 o alterar la semántica pasiva del modo `"system"`.

### 3. Demostración Anti-aprobación-automática (Trampas)

- **T1 (Silencio por AudioContext suspendido): APLICA.**
  D-B tiene una salvaguarda de timeout exclusiva para el ARRANQUE. Sin embargo, si durante la grabación el sistema operativo o un evento de hardware obliga al AudioContext a transicionar asíncronamente al estado `suspended` (ej. al desconectar un USB agresivamente), el recorder captará solo silencio. Como el diseño carece de recuperación en vuelo para el estado del contexto, el acta se corrompe en silencio. *Requiere mitigación.*
- **T2 (Hueco de audio en el swap): No aplica.**
  La espera asíncrona por segundos de `getUserMedia` ocurre con el micrófono viejo aún conectado al destination enviando audio. La transición topológica (`connect-nuevo` → `disconnect-viejo`) es síncrona en el event loop. No habrá solapamiento perceptible ni hueco perjudicial.
- **T3 (Desenchufe del mic activo a mitad de grabación): No aplica.**
  Si un micro muere espontáneamente y pasa a estado `ended`, su nodo deja de emitir audio al `dest.stream`, generando silencio ininterrumpido en la grabación. Tras 5 segundos, el detector orgánico detectará `micSilent`, activará el banner rojo, y el flujo normal de `swapMicrophone` rescatará la situación.
- **T4 (Preferido fantasma de otra máquina): No aplica.**
  D-E protege explícitamente obligando a verificar que el ID "existe y está en la lista" (derivada de `enumerateDevices` en local) antes de pedirlo. Si evadiera el filtro, D-E prevé un "fallback DECLARADO" al predeterminado, preservando la grabación.
- **T5 (Doble swap rápido): APLICA.**
  D-C no gestiona concurrencia. Si el usuario pulsa Mic A y de inmediato Mic B, hay dos promesas de `getUserMedia` en vuelo. Si resuelven y los cierres acceden a las referencias viejas de manera inestable, el micrófono más rápido en cargar podría quedar permanentemente como una fuente huérfana en el mix Web Audio (sin `disconnect` ni `stop`), doblando la entrada del audio, consumiendo RAM y dejando hardware cautivo. *Requiere mitigación.*

### 4. Cambios obligatorios

1. **Recuperación activa de AudioContext (Mitigación T1):** En D-B, durante el modo presencial, se debe registrar un listener para el evento `statechange` en el `AudioContext`. Si el estado transiciona a `suspended` (o similar) mientras la grabación sigue activa, el sistema debe intentar inyectar un `audioCtx.resume()` automáticamente, logeando el evento.
2. **Cerrojo de transaccionalidad en Swap (Mitigación T5):** En D-C, `swapMicrophone` debe incorporar un mecanismo de concurrencia. Si se ejecuta un nuevo intento de swap mientras hay uno previo asíncrono en vuelo (`isSwappingRef.current = true`), el código debe rechazar agresivamente el intento concurrente, o bien llevar un token de cancelación que fuerce la destrucción (stop) inmediata del stream "perdedor" si este llega a resolver tarde.

### 5. Veredicto global

**APROBADO CON CAMBIOS**
