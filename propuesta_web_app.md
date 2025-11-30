**Propuesta de Desarrollo Aplicativo Web para la gestión y operación de la Sostenibilidad Caracol-WERO**

**Módulo RESPEL**

Preparado por: Sebastián Pérez Cuadros

Fecha: 11 de noviembre de 2025

# Introducción

Esta propuesta presenta el diseño y desarrollo de un aplicativo web integral para la gestión y operación de la sostenibilidad ambiental, con un conjunto de modulos iniciales enfocados en el manejo de RESPEL y su aprovechamiento. El sistema permitirá gestionar de manera estratégica todo el ecosistema de proveedores, flujos operativos, trazabilidad documental y métricas de impacto ambiental.

La plataforma centraliza la operación completa de sostenibilidad: desde el registro y validación de actores externos (proveedores especializados), pasando por la planificación y ejecución de actividades de recolección y aprovechamiento, hasta la generación de indicadores consolidados que demuestren el compromiso y cumplimiento ambiental de la organización ante autoridades reguladoras y partes interesadas.

Objetivo estratégico: Construir una base tecnológica robusta que soporte la toma de decisiones en sostenibilidad, garantice cumplimiento normativo y facilite la demostración de resultados ambientales cuantificables.

# Autenticación y Control de Acceso

El sistema contará con autenticación de usuario. Se implementarán roles de acceso diferenciados:

- Administrador / Gestor interno de Wero
- Usuario / Crear solicitudes de recolección
- Operador / Completar solicitudes con toda la información de cierre
- Aprobador / Registro proveedores y responsable de validar solicitudes
- Auditor / Autoridad ambiental

Cada rol verá únicamente las funciones y paneles que le corresponden. Se añadirán controles de expiración de sesión mínima.

# Módulos Funcionales

Los módulos principales se numeran y relacionan con los archivos actuales del repositorio y futuros componentes:

1. Módulo de Ingreso de Proveedores
	- Registro de proveedores con datos básicos (identificación, contacto, tipo de material, permisos vigentes).
	- Gestión documental: subida de certificados (archivo PDF/JPG/PNG).

2. Módulo de Creación de Solicitudes
	- Formulario para generar solicitudes de recolección indicando: proveedor, tipo de material, estimado de cantidad, fecha tentativa, observaciones.
	- Asignación automática de consecutivo interno.
	- Validaciones: campos obligatorios completos.
	- Registro en base de datos interna. 

3. Módulo de Aprobación de Solicitudes
	- Bandeja de solicitudes en estado "Pendiente" con filtros (fecha, proveedor, material).
	- Acciones: aprobar / rechazar.
	- Historial de cambios de estado con marca temporal y usuario.
	- Notificación interna.

4. Módulo de Completar Solicitud
	- Disponible solo para solicitudes aprobadas.
	- Campos adicionales al cerrar el ciclo:
	  * Cantidad recolectada (peso o volumen - selector de unidad).
	  * Evidencia fotográfica (múltiples imágenes).
	  * Certificado de recolección (PDF).
	  * Certificado de transformación y/o aprovechamiento (PDF).
	- Cambio de estado a "Completada" y bloqueo de edición salvo por rol Administrador.

5. Módulo de Autoridad Ambiental
	- Panel consolidado de:
	  * Conteo de solicitudes por estado (pendiente, aprobada, completada, rechazada).
	  * Lista rápida de últimas completadas con acceso a documentos.
	  * Indicadores agregados (total kg/volumen recolectado por periodo, top proveedores, materiales más gestionados).
	  * Verificación documental: porcentajes de proveedores con certificados vigentes.
	- Exportación de paquete comprimido con carpeta de soportes por rango de fechas.
	- Búsqueda por número de solicitud o proveedor para atención inmediata en visita.

# Beneficios Esperados

- Gestión integral de sostenibilidad: Visibilidad completa del ciclo de vida de residuos peligrosos desde la generación hasta su aprovechamiento final.
- Cumplimiento normativo garantizado: Trazabilidad documental completa que respalda el cumplimiento de regulaciones ambientales.
- Medición de impacto ambiental: Consolidación de métricas cuantificables (kg recolectados, materiales aprovechados, certificaciones obtenidas).
- Preparación para auditorías: Respuesta inmediata ante visitas de autoridad ambiental con acceso centralizado a toda la documentación.
- Fortalecimiento de la cadena de valor sostenible: Control y verificación continua de proveedores y sus certificaciones.
- Transparencia y rendición de cuentas: Capacidad de generar reportes de sostenibilidad con datos verificables.

# Plan de Trabajo Acelerado

Se plantea un cronograma intensivo dada la fecha objetivo para contar con un aplicativo funcional.

| Semana | Fechas (aprox) | Objetivo Principal |
| ------ | -------------- | ------------------ |
| Semana 1 | 11 - 17 nov | Ajustes de autenticación, estructura de datos base, CRUD proveedores (Módulo 1). |
| Semana 2 | 18 - 24 nov | Formulario creación solicitudes (Módulo 2) + consecutivos + almacenamiento. |
| Semana 3 | 25 nov - 1 dic | Bandeja aprobación (Módulo 3) + flujo de estados + registro histórico. |
| Semana 4 | 2 - 8 dic | Pantalla completar solicitud (estructura y definición de campos) + carga de archivos. |
| Semana 5 | 9 - 14 dic | Dashboard autoridad ambiental (visualizaciones básicas, exportación ZIP) + Módulos 1-3 operativos, módulos 4 y 5 en versión inicial funcional (alpha). |
| Post-Alpha | 15 dic en adelante | Endurecimiento, optimización persistencia, refinamiento UI/UX y métricas avanzadas. |

Reuniones de seguimiento: 2 por semana (inicio y cierre). Retroalimentación rápida para asegurar alineación continua.

# Acompañamiento y Compromiso

Durante el ciclo acelerado se garantizan:
- Reuniones de avance semanales (mínimo 2).
- Entregas incrementales demostrables en entorno de prueba.
- Soporte post-entrega inicial (2 semanas) para estabilización y correcciones menores.

El enfoque colaborativo permitirá ajustar prioridades si emergen requisitos adicionales sin comprometer la fecha de primer entregable.

# Conclusión

La plataforma propuesta constituye una solución estratégica para la gestión operativa de la sostenibilidad ambiental, posicionando a la organización como referente en el manejo responsable de residuos peligrosos. Más allá de un simple sistema de solicitudes, esta herramienta se convierte en el centro de operaciones de sostenibilidad, integrando personas, procesos y documentación en un ecosistema digital cohesivo.

La base tecnológica permitirá no solo alcanzar el cumplimiento normativo, sino demostrar de manera cuantificable el impacto positivo de las iniciativas ambientales. El diseño modular garantiza escalabilidad para incorporar futuros módulos (gestión de otros tipos de residuos, economía circular, indicadores GRI, etc.).

Con el primer entregable funcional antes del 15 de diciembre, la organización estará preparada para operar su estrategia de sostenibilidad con trazabilidad, control y visibilidad total.

# Tabla Resumen de Módulos

| Módulo | Funciones Clave | Beneficios |
| ------ | --------------- | ---------- |
| 1. Proveedores | Alta/edición, estado, documentos | Control vigencia y base ordenada |
| 2. Creación Solicitudes | Formulario, consecutivo, validaciones | Ingreso estructurado y rápido |
| 3. Aprobación | Revisión, aprobar/rechazar, historial | Trazabilidad y control de flujo |
| 4. Completar Solicitud | Carga de evidencias y certificados | Cierre documental completo |
| 5. Dashboard Autoridad | KPIs, descarga zip, búsqueda | Respuesta ágil ante visitas |

# Propuesta Económica

| Ítem | Descripción | Tiempo | Valor |
| ---- | ----------- | ------ | ----- |
| 1 | Desarrollo e implementación del producto | Hasta 15 dic (≈5 semanas) | 10'000'000 COP |


Estructura de pagos propuesta:
- 30% al inicio (arranque y setup técnico)
- 40% al presentar producto minimo viable funcional previo al 15 de diciembre
- 30% al finalizar fase de estabilización

* Valor incluye impuestos aplicables y soporte básico post-entrega inicial.
