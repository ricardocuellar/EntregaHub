# EntregaHub — estados y decisiones preparados

Referencia: SPEC.md y PERMISOS.md. Políticas de referencia propuestas para simplificar el flujo; deben revisarse humanamente antes de implementar. No son resultados de una prueba ejecutada.

## Estados por versión

| Estado | Significado | Próxima acción permitida |
|---|---|---|
| borrador | PDF ya publicado para el equipo, todavía oculto al cliente | Administrador/colaborador autorizado envía a revisión |
| en_revision | Cliente autorizado puede comentar y decidir | Cliente solicita cambios o aprueba |
| cambios_solicitados | Revisión terminada con petición de corrección | Equipo comenta y prepara una versión nueva |
| aprobada | Cliente aceptó ese archivo | Solo consulta/descarga/historial; no edición ni nuevos comentarios |

Transiciones de la misma versión: borrador → en_revision; en_revision → cambios_solicitados; en_revision → aprobada. Sin reapertura, reversión de decisión ni edición del archivo. Un error requiere nueva versión; la anterior conserva su estado y decisión.

Puede crearse V2 cuando la versión anterior está en cambios_solicitados o aprobada. No crear otra mientras haya borrador o revisión abierta del mismo entregable. Cada versión inicia en borrador y necesita su envío a revisión. Los números no se reutilizan ni duplican, incluso con cargas simultáneas. Si una carga falla, no se promete numeración sin huecos: se requiere identidad única y orden creciente.

## Varias cuentas cliente

Cualquier usuario cliente activo asignado al proyecto puede decidir sobre la versión en revisión. Una sola decisión final por revisión/versión: no unanimidad ni cadena de aprobadores. Gana la primera decisión válida aceptada de forma atómica; una posterior incompatible se rechaza y no cambia el estado. El backend vuelve a comprobar estado y permisos al aceptar la operación.

## Reintentos

La interfaz identifica cada intento lógico de decisión con una clave de solicitud y la reutiliza si reintenta. El backend la relaciona con usuario, versión y acción. Reintentar la misma clave y contenido devuelve la decisión ya aceptada sin crear otra ni otro evento de negocio. Misma clave con contenido diferente se rechaza. Una solicitud con otra clave sobre una revisión ya terminada se rechaza sin cambiar la decisión, aunque solicite la misma acción. Los registros técnicos de solicitudes pueden repetirse; no son decisiones duplicadas.

Dos solicitudes concurrentes con claves distintas y acciones incompatibles no pueden terminar ambas aceptadas. La implementación y pruebas deben usar transacciones/restricciones adecuadas, no confiar en deshabilitar el botón.

## Historial y conservación

Conservar archivos, comentarios y decisiones por versión con actor y fecha del servidor. Un evento de decisión aceptada se registra una vez. Publicar otra versión crea un registro nuevo; no altera la aprobación anterior. No hacer público un borrador a través del historial. No construir una auditoría de cada campo del sistema.
