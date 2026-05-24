# Pendientes de Implementación — Segundo Parcial

Basado en comparación del código actual vs. requisitos del PDF.

---

## 1. Tiempo estimado de reparación ❌ (0%)

**Qué pide el PDF:** "Obtener el tiempo que tardará en ser reparado el vehículo"

**Qué falta:**
- Campo `tiempo_estimado_min` en modelo `Cotizacion` o `Asignacion`
- El taller lo llena al responder la cotización
- Endpoint que devuelva ese tiempo al cliente
- Mostrar en la app/web junto con el estado del incidente

**Sugerencia de implementación:**
1. Agregar `tiempo_estimado_min: int | None` a `Cotizacion` (el taller lo incluye al responder)
2. Al aceptar cotización y crear `Asignacion`, copiar el campo allí también
3. Exponer en `GET /incidentes/{id}` dentro del resumen de la asignación activa
4. En el frontend mostrar como "Tiempo estimado: X horas Y minutos"

**Archivos a tocar:**
- `app/models/cotizacion.py` — agregar campo
- `app/schemas/cotizacion_schema.py` — agregar al schema de respuesta del taller
- `app/services/cotizacion_service.py` — pasar el campo al crear Asignacion
- `alembic/` — nueva migración

---

## 2. KPIs faltantes ⚠️ (parcial)

El endpoint `GET /tenants/me/kpis` existe pero le faltan 3 de 7 KPIs del PDF.

### 2a. Casos cancelados ❌

**Qué falta:**
- Contar incidentes con estado `cancelado` en el rango de fechas
- Incluirlo en `KpiResumen`

**Sugerencia:**
```python
# en kpi_service.py — agregar función:
def incidentes_cancelados(db, desde, hasta, id_tenant) -> int:
    return db.query(func.count(Incidente.id_incidente)).filter(
        Incidente.id_tenant == id_tenant,
        Incidente.estado == "cancelado",
        Incidente.created_at.between(desde, hasta)
    ).scalar()
```

**Archivos a tocar:**
- `app/services/kpi_service.py`
- `app/schemas/kpi_schema.py` — agregar campo `casos_cancelados: int`
- `app/api/kpis.py` — llamar la nueva función

### 2b. Zonas con más incidentes ❌

**Qué falta:**
- Agrupar incidentes por zona geográfica (aproximar con redondeo de lat/lng)
- Devolver lista de zonas con conteo

**Sugerencia (sin PostGIS, solo SQL puro):**
```python
# Redondear lat/lng a 2 decimales = zonas de ~1km²
def zonas_mas_incidentes(db, desde, hasta, id_tenant, limite=10):
    return db.query(
        func.round(UbicacionIncidente.latitud, 2).label("lat"),
        func.round(UbicacionIncidente.longitud, 2).label("lng"),
        func.count().label("total")
    ).join(Incidente).filter(
        Incidente.id_tenant == id_tenant,
        Incidente.created_at.between(desde, hasta)
    ).group_by("lat", "lng").order_by(desc("total")).limit(limite).all()
```

**Archivos a tocar:**
- `app/services/kpi_service.py`
- `app/schemas/kpi_schema.py` — nuevo schema `ZonaKpi(lat, lng, total)`
- `app/api/kpis.py`

### 2c. Nivel de cumplimiento SLA ❌

**Qué falta:**
- Definir umbral SLA (ej: servicio atendido en ≤ 60 minutos desde reporte)
- Calcular % de incidentes que cumplieron ese umbral

**Sugerencia:**
```python
SLA_MINUTOS = 60  # configurable por tenant en el futuro

def cumplimiento_sla(db, desde, hasta, id_tenant) -> float:
    # total finalizados en el período
    # de esos, cuántos tuvieron (fecha_fin - created_at) <= SLA_MINUTOS
    # retorna porcentaje 0-100
```

Usar `HistorialEstadoAsignacion` para sacar timestamps exactos de cada transición.

**Archivos a tocar:**
- `app/services/kpi_service.py`
- `app/schemas/kpi_schema.py` — agregar `sla_cumplimiento_pct: float`
- `app/api/kpis.py`

---

## 3. Offline — Idempotencia en creación de incidentes ⚠️

**Qué pide el PDF:** "Evitar duplicar incidentes" al sincronizar desde modo offline.

**Problema actual:** Si la app offline guarda un incidente y al volver la conexión lo envía 2 veces, el backend crea 2 registros.

**Sugerencia:**
1. El cliente (móvil/web) genera un `idempotency_key` (UUID v4) al crear el incidente localmente
2. El backend recibe ese key en el body o header
3. Si ya existe un incidente con ese key del mismo usuario → devuelve el existente (200), no crea uno nuevo (201)

**Implementación:**
- Agregar campo `idempotency_key: str | None` (unique) a `Incidente`
- En `POST /incidentes`, antes de insertar, buscar si ya existe ese key para ese usuario
- Si existe → return el incidente existente con status 200
- Si no → crear normalmente con status 201

**Archivos a tocar:**
- `app/models/incidente.py` — agregar campo + unique constraint
- `app/api/incidentes.py` — lógica de deduplicación
- `alembic/` — nueva migración

---

## 4. Aporte Propio — Mejoras al módulo de Pagos 🔵

Basado en la sugerencia recibida. Se recomiendan las Fases 1 y 2 como realistas para el examen.

### Fase 1 — Pre-autorización con catálogo IA

**Qué hace:** Al crear el incidente, la IA estima un costo referencial desde el catálogo de tarifas. Ese monto sirve como pre-autorización para validar que el cliente puede pagar antes de enviar al técnico.

**Sugerencia:**
- Nuevo campo `monto_preautorizacion` en `Incidente`
- Al crear incidente, llamar al servicio de IA que devuelve estimado según categoría
- Crear un `PaymentIntent` de Stripe en estado `manual_capture` (no cobra, solo reserva)
- Si el cliente no tiene fondos → no se busca taller, se notifica
- Al finalizar servicio → capturar el PaymentIntent real con el monto final

**Archivos a tocar:**
- `app/models/incidente.py`
- `app/services/ia_service.py` (o donde esté la IA)
- `app/api/pagos.py` — lógica de pre-auth y captura final
- `alembic/`

### Fase 2 — Adendas / demasías (ampliación de presupuesto)

**Qué hace:** Si el mecánico encuentra daños ocultos, registra una ampliación. El incidente se congela en estado `en_espera_aprobacion`. El cliente aprueba o rechaza digitalmente para continuar.

**Sugerencia:**
- Nuevo modelo `Adenda` con campos: `id_asignacion`, `monto_adicional`, `descripcion`, `estado` (pendiente/aprobada/rechazada), `created_at`
- Nuevo estado de asignación: `en_espera_aprobacion`
- Endpoints:
  - `POST /asignaciones/{id}/adenda` — técnico registra la ampliación
  - `POST /asignaciones/{id}/adenda/responder` — cliente aprueba o rechaza
- Al crear adenda → WebSocket notifica al cliente inmediatamente
- Si cliente rechaza → asignación pasa a `cancelada` con motivo

**Archivos a tocar:**
- `app/models/transaccional.py` — nuevo modelo `Adenda`
- `app/api/asignaciones.py` — nuevos endpoints
- `app/services/notify_service.py` — notificación WebSocket al cliente
- `alembic/`

### Fase 3 — Penalización por cancelación en trayecto (solo la parte GPS, no el seguro)

**Qué hace:** Si el cliente cancela cuando el técnico ya está en camino, se cobra una tarifa fija de penalización.

**Sugerencia:**
- Al cancelar incidente, verificar si la asignación está en estado `en_camino`
- Si sí → calcular penalización (tarifa fija, ej: $5)
- Crear `Pago` de tipo `penalizacion` y procesarlo con Stripe
- Notificar al cliente el cobro antes de confirmar la cancelación

**Nota:** La parte de seguros/facturación corporativa mensual NO se recomienda implementar — requeriría integración con API de aseguradora real.

**Archivos a tocar:**
- `app/api/incidentes.py` — lógica al cancelar
- `app/api/pagos.py` — nuevo tipo de pago `penalizacion`
- `app/models/transaccional.py` — agregar tipo al enum de pagos

---

## Resumen de archivos por tocar

| Archivo | Cambios |
|---|---|
| `app/models/cotizacion.py` | + `tiempo_estimado_min` |
| `app/models/incidente.py` | + `idempotency_key`, + `monto_preautorizacion` |
| `app/models/transaccional.py` | + modelo `Adenda`, + tipo `penalizacion` en Pago |
| `app/services/kpi_service.py` | + cancelados, + zonas, + SLA |
| `app/schemas/kpi_schema.py` | + nuevos campos KPI |
| `app/api/kpis.py` | + llamadas a nuevas funciones |
| `app/api/incidentes.py` | + idempotencia, + penalización al cancelar |
| `app/api/asignaciones.py` | + endpoints de adenda |
| `app/api/pagos.py` | + pre-auth, + captura final, + penalización |
| `app/services/notify_service.py` | + notificación adenda al cliente |
| `alembic/` | migraciones para cada modelo nuevo |

---

## Orden sugerido de implementación

1. **KPIs faltantes** — impacto alto, cambios pequeños, todo en `kpi_service.py`
2. **Tiempo estimado de reparación** — campo simple, gran visibilidad en el examen
3. **Idempotencia offline** — campo + lógica en un endpoint
4. **Adendas (Fase 2 pagos)** — nuevo flujo completo, más complejo
5. **Pre-autorización IA (Fase 1 pagos)** — depende de cómo esté el servicio IA
6. **Penalización cancelación (Fase 3 pagos)** — ajuste al flujo de cancelación
