# SEGUNDO EXAMEN PARCIAL: APP. WEB Y MÓVIL

**Examen 2 - Sistemas 2**
**Docente:** MSc. Ing. Angélica Garzón Cuéllar

---

## Evolución de la Plataforma Inteligente de Atención de Emergencias Vehiculares

La aplicación desarrollada en la primera etapa deberá ser ampliada incorporando funcionalidades avanzadas que permitan convertirla en una plataforma más cercana a un producto real en producción.

El sistema base ya contemplaba app móvil, app web, backend FastAPI, PostgreSQL, IA, geolocalización, asignación de talleres, trazabilidad y notificaciones. En esta segunda fase, los estudiantes deberán extender esa solución con cuatro capacidades obligatorias.

---

## 1. Módulo de tiempo real (WebSockets + tracking)

**Objetivo:** Permitir que cliente, taller y sistema visualicen actualizaciones en vivo durante la atención de una emergencia.

**Funcionalidades mínimas:**

- Seguimiento en tiempo real del taller asignado.
- Actualización automática del estado del incidente.
- Notificación inmediata cuando:
  - un taller acepta,
  - un taller rechaza,
  - cambia el estado del servicio,
  - el auxilio está en camino,
  - el servicio fue atendido.

**Estados sugeridos:**

- pendiente
- buscando taller
- taller asignado
- en camino
- en atención
- finalizado
- cancelado

---

## 2. Modo offline y sincronización

**Objetivo:** Permitir que la app móvil pueda registrar emergencias incluso cuando el usuario no tenga conexión estable.

**Funcionalidades mínimas:**

- Guardar localmente una emergencia cuando no haya internet.
- Marcarla como "pendiente de sincronización".
- Sincronizar automáticamente cuando vuelva la conexión.
- Evitar duplicar incidentes.
- Mostrar al usuario si la emergencia fue enviada o sigue pendiente.
- Manejar errores de sincronización.

**Casos obligatorios:**

- El usuario registra emergencia sin internet.
- El usuario recupera conexión.
- El sistema sincroniza el incidente.
- El backend registra correctamente el caso.
- La app actualiza el estado local.
- Situación similar debe aplicar en la aplicación web basado en el enfoque de aplicaciones web progresivas.

---

### OTRAS FUNCIONALIDADES (WEB/MÓVIL)

- Obtener Cotizaciones del daño de vehículos en los talleres.
- Seleccionar un taller para realizar el servicio.
- Obtener el tiempo que tardará en ser reparado el vehículo.
- Efectuar los pagos, utilizar paralela de pagos.

> **CADA GRUPO TIENE QUE HACER SU APORTE PROPIO, CON NUEVAS FUNCIONALIDADES AL CASO DE ESTUDIO.**

---

## 3. Analítica operacional y KPIs

**Objetivo:** Agregar inteligencia operacional para administradores o responsables de la plataforma.

**Funcionalidades mínimas:** Panel web con indicadores como: Mostrarlo utilizando Dashboard para los talleres por tenant.

| KPI | Descripción |
| --- | --- |
| **Tiempo promedio de asignación** | Tiempo entre reporte y taller asignado |
| **Tiempo promedio de llegada** | Tiempo entre asignación y llegada |
| **Incidentes por tipo** | Batería, llanta, motor, choque, otros |
| **Talleres más eficientes** | Según tiempo de respuesta y finalización |
| **Zonas con más incidentes** | Según ubicación geográfica |
| **Casos cancelados** | Emergencias canceladas o no atendidas |
| **Nivel de cumplimiento SLA** | Servicios atendidos dentro del tiempo esperado |

**Requisito importante:** No basta con mostrar números fijos. Los KPIs deben salir de datos reales registrados en la base de datos.

---

## 4. Arquitectura multi-tenant SaaS

**Objetivo:** Preparar el sistema para que pueda ser usado por múltiples organizaciones, empresas o redes de talleres sin mezclar información.

**Funcionalidades mínimas:**

- Incorporar el concepto de tenant.
- Cada taller, usuario, incidente y métrica debe pertenecer a un tenant.
- Un usuario de un tenant no debe ver datos de otro tenant.
- El sistema debe permitir administrar múltiples redes de talleres.
- El backend debe filtrar la información según el tenant autenticado.

**Ejemplo:**

- Tenant A: Red de talleres "Auxilio Norte".
- Tenant B: Red de talleres "Mecánicos Express".
- Ambos usan la misma plataforma, pero sus datos están separados lógicamente.

---

## REGLA CLAVE

No se aceptará una funcionalidad aislada o decorativa. Cada módulo debe afectar realmente al flujo del sistema:

- tiempo real debe actualizar estados reales;
- offline debe guardar y sincronizar datos reales;
- KPIs deben calcularse desde la base de datos;
- multi-tenant debe aislar datos de verdad.

**FRASE OFICIAL DEL ENUNCIADO:**

> La segunda fase no consiste en crear un nuevo sistema, sino en evolucionar la plataforma existente hacia una solución profesional, escalable, trazable y orientada a operación real, incorporando capacidades de tiempo real, funcionamiento offline, analítica operacional y arquitectura SaaS multi-tenant.

---

## DOCUMENTO SEGUNDO PARCIAL

Continuación de ciclos PUDS-UML 2.5+: Ciclo # 4 y Ciclo # 5

**1) Perfil**

- 1.1 Introducción
- 1.2 Objetivo General
- 1.3 Objetivos Específicos
- 1.4 Descripción del problema
- 1.4 Alcance (la documentación estará organizada en dos partes).

**Parte I – Fundamentación Teórica** (revisar en libros o sitios en internet especializados en la temática)

**Parte II – Proceso de desarrollo**

- a) Seguir los pasos descritos por el PUDS para el desarrollo de la Aplicación.
- b) Generar los modelos pertinentes utilizando UML.
- 2.1) Flujo de Trabajo: Captura de Requisitos
- 2.2) Flujo de Trabajo: Análisis
- 2.3) Flujo de Trabajo: Diseño
- 2.4) Flujo de Trabajo: Implementación
- 2.5) Flujo de Trabajo: Pruebas

**Secciones Finales del Documento:**

- CONCLUSIÓN
- RECOMENDACIÓN
- BIBLIOGRAFÍA
- URL Y QR

---

## CRONOGRAMA DE PRESENTACIONES Y DEFENSA

| Evento | Fecha | Hora |
| --- | --- | --- |
| **SEGUNDO EXAMEN PARCIAL** | 19/MAYO/2026 al 09/06/2026 | — |
| **PRESENTACIÓN 1** | VIERNES 29/MAYO | 23:59 |
| **PRESENTACIÓN 2** | DOMINGO 07/JUNIO | 23:59 |
| **DEFENSA EXAMEN PARCIAL 2** | MARTES 09/06/2026 (TODOS) | — |

> *(Son obligatorias las 2 presentaciones)*
