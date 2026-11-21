# Recorrido de EntregaHub

Escenario ficticio: agencia Estudio Faro; cliente Café Aurora; proyecto Identidad visual. Otro cliente: Estudio Nube, sin acceso a ese proyecto.

| Paso | Actor | Acción | Resultado previsto |
|---|---|---|---|
| 1 | Administrador | Crea cuentas/cliente/proyecto y asigna participantes | Colaborador y cliente autorizados sobre el proyecto |
| 2 | Colaborador | Crea entregable Propuesta de logotipo y sube V1 | Versión borrador con PDF privado, invisible al cliente |
| 3 | Colaborador | Envía V1 a revisión | Cliente puede consultar, descargar, comentar y decidir |
| 4 | Cliente | Comenta y solicita cambios | V1 conserva comentarios y decisión |
| 5 | Colaborador | Publica V2 y la envía a revisión | V1 permanece intacta; nueva revisión propia |
| 6 | Cliente | Aprueba V2 | V2 aprobada e inmutable, con responsable y fecha |
| 7 | Participante autorizado | Consulta historial | Versiones y decisiones identificables |

Acceder a la URL desde Estudio Nube no entrega datos ni bytes del proyecto. La UI React adapta acciones al rol, pero DRF debe autorizar toda operación.

