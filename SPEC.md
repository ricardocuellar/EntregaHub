# EntregaHub — especificación funcional del proyecto

## Propósito y recorrido
Portal para una agencia que organiza proyectos, coordina colaboradores y comparte entregables privados con clientes. Administrador crea cliente/proyecto y asigna usuarios → colaborador publica V1 y la envía a revisión → cliente comenta/solicita cambios → colaborador publica V2 → cliente aprueba V2 → historial conserva ambas versiones y sus decisiones.

La IA genera gran parte de la implementación. El producto no requiere una API de IA para funcionar.

## Alcance
Tres roles: administrador, colaborador y cliente. Todas las interfaces del producto en React/TypeScript; backend Django REST Framework. Cuentas creadas por administrador, sin registro público ni recuperación por correo. Un rol por cuenta. Colaboradores y clientes acceden por asignación explícita a proyecto; una cuenta cliente pertenece a la organización del proyecto. Administrador gestiona toda la agencia, sin aprobar en nombre del cliente. PERMISOS.md es la referencia detallada.

Cliente: nombre. Proyecto: cliente, título y descripción. Entregable: proyecto, título, descripción y fecha objetivo. Versión: entregable, número, PDF, autor, fecha y estado. Comentario: versión, autor, texto y fecha. Decisión: versión, usuario cliente, resultado, fecha y referencia de solicitud. Asignaciones: proyecto/usuario con unicidad.

Nombres/títulos de 1–150 caracteres; descripciones opcionales hasta 2000; comentarios de 1–2000; validar tras quitar espacios externos. Fecha objetivo obligatoria, fecha válida; no convertirla automáticamente en vencimiento de acceso. Cada nueva versión recibe número único creciente dentro del entregable. No sobrescribir archivos de versiones ya publicadas.

PDF obligatorio, extensión .pdf sin distinguir mayúsculas, máximo inclusivo 10 MiB (10 485 760 bytes), no vacío y estructura legible; rechazar PDF malformado o cifrado no inspeccionable. Biblioteca y versión se validan con el prototipo. Esto no equivale a análisis antivirus. Descargar como adjunto, sin vista previa ni ruta pública alternativa.

## Revisión, comentarios e historial
ESTADOS.md define transiciones y política de decisiones. Una versión aprobada no se modifica. Una nueva versión no hereda aprobación. Los comentarios y decisiones no se trasladan entre versiones. Cada acción relevante del recorrido identifica actor/fecha/versión en historial del entregable; no se construye auditoría genérica de cada campo.

Comentarios publicados sin edición/eliminación en el flujo del proyecto; aclaraciones como comentario nuevo en estados permitidos. Autor y pertenencia se derivan del servidor, no de campos del navegador. Proteger borrado/reasignación de clientes/proyectos/entregables que contengan versiones o historial. Desactivar cuentas sin borrar su autoría. Descargar un archivo no implica revocación de copias ya obtenidas.

Portal: acceso, resumen/pendientes, proyectos, detalle de proyecto, entregable con versiones y detalle de versión con archivo, comentarios y decisiones. Pantallas y acciones según rol; backend siempre autoriza. Listados básicos paginados de 20 elementos y orden estable. Componentes visuales preparados, interfaz adaptable y mensajes/estados vacíos. No buscador/filtros avanzados en esta entrega.

## Tecnología y operación
backend/: Python, Django, DRF; frontend/: React, TypeScript, Vite. PostgreSQL, Docker Compose, servidor WSGI y proxy Caddy/HTTPS. Mismo origen en producción para frontend y /api; proxy /api durante desarrollo. Sesión en cookie HttpOnly y CSRF efectivo en escrituras, login y logout. No guardar credenciales de sesión en localStorage. Versiones de dependencias y comandos se fijan y ejecutan con el starter, no por memoria.

Persistencia tras reinicio, respaldo y restauración de base y archivos en entorno separado, instrucciones de instalación/uso/actualización y límites de reversión. Recursos y datos ficticios; sin secretos versionados. Prototipo completo comprobado antes de cerrar grabación definitiva.

## Diez criterios esenciales de aceptación
- CA01: administrador crea cuentas y asignaciones válidas; login funciona; logout/desactivación impiden nuevas operaciones protegidas; escrituras/login/logout aplican CSRF y cookies apropiadas.
- CA02: colaborador y cliente solo consultan o actúan en proyectos asignados; usuario cliente coincide con organización del proyecto. Identificadores directos, formularios, listados y paginación no permiten acceder a otro proyecto. Cliente no obtiene acceso a todos los proyectos por pertenecer a la organización.
- CA03: administrador asigna personas y colaborador autorizado crea entregable con valores válidos; al consultar de nuevo se conservan campos/relaciones. Entradas inválidas o actores sin permiso se rechazan sin cambios.
- CA04: PDF válido al límite se acepta; vacío, mayor, extensión inválida o estructura no inspeccionable se rechaza sin versión utilizable ni exposición pública. Versiones reciben números únicos; cargas concurrentes no duplican el número.
- CA05: autorizado descarga bytes correctos de una versión visible; ajeno o sin sesión no obtiene bytes por ninguna ruta alternativa. Un cliente no ve borradores.
- CA06: comentarios conservan versión, autor y fecha; texto inválido o versión/rol/estado no permitido se rechaza. Autor enviado por navegador no suplanta identidad. Publicar V2 no reasigna comentarios de V1.
- CA07: el flujo borrador → en revisión → cambios solicitados → nueva versión → en revisión → aprobada se completa según permisos. V1 conserva archivo y decisión; V2 tiene revisión propia. No se decide sobre una versión que no esté en revisión.
- CA08: archivo/decisión de versión aprobada no cambian; reintento idéntico no duplica decisiones/eventos; solicitudes contradictorias concurrentes no quedan ambas aceptadas. Historial identifica actor, momento y versión. ESTADOS.md concreta resultados esperados.
- CA09: recorrido completo en React con DRF funciona por HTTPS; resumen, historial, paginación y navegación móvil reflejan datos autorizados. Reiniciar servicios conserva datos y archivos relacionados.
- CA10: respaldo se restaura en entorno separado y se comparan relaciones/archivos; README reproduce arranque, uso y operación. Una actualización se verifica con procedimiento y límites de reversión documentados. No declarar una restauración probada por existir un archivo de respaldo.

## Exclusiones
SaaS multiagencia, pagos/suscripciones, firma electrónica, edición colaborativa, anotaciones sobre imágenes, procesamiento de video, app nativa, notificaciones, IA dentro del producto y aprobaciones configurables por etapas. La aprobación del portal no es firma electrónica.

## Registro de revisión humana
Detalles de índices, endpoints y bibliotecas se concretan al implementar, sin cambiar el comportamiento acordado.
