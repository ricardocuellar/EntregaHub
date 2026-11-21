# EntregaHub — permisos preparados

Referencia: SPEC.md. Política de referencia propuesta; pendiente de revisión humana. Tres roles, uno por cuenta. Usuarios activos; autoría y acceso derivados desde sesión. Nunca confiar en botones ocultos como autorización.

| Acción | Administrador | Colaborador | Cliente |
|---|---|---|---|
| Crear cuentas/clientes/proyectos | Sí, global agencia | No | No |
| Asignar participantes | Sí; cliente debe coincidir con organización | No | No |
| Consultar proyecto | Todos | Solo asignados | Solo asignados y de su organización |
| Crear entregable/publicar versión | Sí | En proyectos asignados | No |
| Consultar versión borrador | Sí | En proyecto asignado | No |
| Enviar borrador a revisión | Sí | En proyecto asignado | No |
| Consultar/descargar versión enviada a revisión | Sí | En proyecto asignado | En proyecto asignado y organización correcta |
| Comentar borrador | Sí | En proyecto asignado | No |
| Comentar en revisión/cambios solicitados | Sí | En proyecto asignado | En proyecto asignado |
| Comentar versión aprobada | No | No | No |
| Solicitar cambios/aprobar | No en nombre del cliente | No | Versión en revisión, proyecto asignado |
| Consultar historial | Global | En proyecto asignado | Solo versiones visibles de proyecto asignado |
| Editar archivo publicado/decisión aceptada | No | No | No |
| Borrar versiones/comentarios/decisiones | No en interfaces del curso | No | No |

Administrador puede crear otro usuario, pero no atribuirle decisiones usando un campo de autor en el formulario. Desactivar una cuenta conserva historial. Una asignación revocada impide nuevas solicitudes; no elimina archivos ya descargados. Detalles de respuesta HTTP se fijan en contratos DRF sin revelar objetos ajenos.

El cliente ve versiones que salieron del estado borrador, incluido historial de cambios/aprobadas. No exponer comentarios o eventos de borrador mediante el historial o sus endpoints. Campos de formulario que referencian objetos requieren la misma autorización que una consulta directa.
