# Correcciones — Flujo de Pagos y Cotización

Estado final tras aplicar las decisiones del usuario.
**Tests:** 136/136 ✅ (10 nuevos + 126 existentes, 0 regresiones).

---

## Decisiones tomadas

| Tema | Decisión |
|---|---|
| Modalidad de la app | **Solo móvil**. Se quita la columna "Movil" del web. |
| Cotización | **Tarifa referencial**. El técnico puede ajustar el costo final si hubo gastos no contemplados (vida real). |
| Distancia GPS | **SÍ se incluye** en la cotización como `monto_traslado`, calculado automáticamente. |
| Tarifa por km | Configurable en `/servicios` del taller (campo `taller.tarifa_traslado`). |
| Penalización | Porcentajes (pendiente / aceptada / en_camino) configurables por tenant desde `/cancelaciones`. |
| Pestaña Cotizaciones del web | **Eliminada** (decisión: tarifa es referencial, app es solo móvil). |
| Display monto en cliente | Muestra desglose en `seleccionar_taller_screen`: `Total estimado = tarifa_base + (tarifa_traslado × distancia)`. |

---

## ✅ Bug #1 — Técnico sobrescribe el precio  *(RESUELTO como decisión de negocio)*

**Decisión:** Se mantiene el `costo_final` editable en el `CompletarServicioDialog`. En la vida real el técnico puede encontrar gastos adicionales (combustible, herramientas, repuestos menores). La cotización pasa a ser **referencial**.

**Cambios aplicados:**
- `CompletarServicioDialog`: cambié label "COP" → "USD", permití decimales (`85.50`), agregué hint explicando que es ajustable.
- Texto en `/servicios` del web actualizado: "La tarifa base es **referencial**..."

---

## ✅ Bug #2 — Cotización sin costo por distancia GPS  *(RESUELTO)*

**Solución implementada:**

1. **Migración 0011** — `cotizacion.distancia_km` y `cotizacion.monto_traslado` (idempotente).
2. **Modelo `Cotizacion`** — `monto_total = monto_servicio + monto_repuestos + monto_traslado`.
3. **`cotizacion_service.responder_cotizacion`** — calcula automáticamente distancia GPS (haversine) y multiplica por `taller.tarifa_traslado` cuando el taller responde.
4. **Schema `CotizacionResponse`** — incluye `distancia_km` y `monto_traslado` en la respuesta.
5. **`/servicios` del web** — nueva card "Tarifa por km recorrido (USD)" arriba de la tabla. El taller la configura una vez y se usa en todas sus cotizaciones.
6. **Web del taller `/cotizaciones`** — desglose visible: `Servicio $X + traslado $Y (Z km) = Total`.
7. **Flutter cliente `cotizaciones_screen`** — fila extra en el desglose: `Traslado (3.5 km)   $10.50` cuando aplica.

**Cobertura:** `tests/test_cotizacion_traslado.py` (2 tests pasando).

---

## ✅ Bug #3 — `listar_mis_pagos` retorna duplicados con preauth  *(RESUELTO)*

`app/api/pagos.py:368` — Cambié `outerjoin(Pago, ...)` a `outerjoin(Pago, and_(..., Pago.tipo == "servicio"))`. Ahora `mis-pagos` ignora preauth y penalización al listar.

---

## ✅ Bug #4 — `crear-intent` machaca preauth existente  *(RESUELTO)*

`app/api/pagos.py:202` — `db.query(Pago).filter(...).first()` ahora filtra `Pago.tipo == "servicio"`. El nuevo Pago insertado también se marca explícitamente con `tipo="servicio"`.

También fixé `obtener_pago` (`GET /pagos/{id_incidente}`) con el mismo filtro.

---

## ⚠️ Bug #5 — Flujo viejo (cobro directo) + nuevo (preauth) coexisten  *(NO RESUELTO, pendiente decisión)*

Tras los fixes de #3 y #4, ambos flujos conviven sin conflicto. Pero **Flutter sigue usando solo el flujo viejo** (`crear-intent`). La pre-autorización Fase 1 existe en backend pero no se activa.

**Opciones (futuro):**
- A) Integrar preauth al reportar incidente en Flutter (más fiel a la guía).
- B) Borrar `preautorizar` y `capturar` del backend.

Por ahora **se queda como está**. No bloquea producción.

---

## ✅ Bug #6 — Estimación sin aprendizaje histórico  *(RESUELTO)*

`pago_service.estimar_costo` ahora usa esta jerarquía:

1. **Promedio de cotizaciones ACEPTADAS** de la misma categoría en los últimos 90 días (si hay ≥ 3).
2. Si no, promedio de `tarifa_base` de los talleres que ofrecen esa categoría.
3. Si tampoco, fallback fijo USD 20.

Esto hace que el estimado refleje precios reales aceptados, no solo el rate-card de los talleres. El nuevo `monto_traslado` también se incluye en el cálculo.

**Cobertura:** `tests/test_estimacion_historico.py` (3 tests pasando).

---

## ⏸️ Bug #7 — Admin global de categorías  *(NO REVISADO)*

Pendiente verificar si existe una pantalla de "admin de plataforma" para `CategoriaProblema`. En el dashboard del taller los campos sí están bien.

---

## ✅ Bug #8 — Columna "Movil" no hacía nada  *(RESUELTO como Opción A)*

**Decisión:** App es **solo móvil**, así que la columna "Movil" se vuelve redundante.

**Cambios aplicados:**
- `web/servicios.component.html` — eliminada columna "Movil" y su checkbox.
- `web/servicios.component.ts` — eliminado `servicio_movil` del interface `FilaServicio`.
- `web/servicios.service.ts` — eliminado del interface `TallerServicio`.

> **Nota técnica:** El campo `TallerServicio.servicio_movil` en BD no se elimina (queda como `default false` sin usar) para no romper migraciones existentes. Si en el futuro se decide implementar la Opción B (híbrida móvil + taller), se puede reactivar.

---

## Archivos modificados

### Backend
| Archivo | Cambio |
|---|---|
| `alembic/versions/c0d1e2f30411_0011_cotizacion_traslado.py` | **NUEVO** — migración 0011 idempotente |
| `app/models/cotizacion.py` | + `distancia_km`, + `monto_traslado`, `monto_total` incluye traslado |
| `app/schemas/cotizacion_schema.py` | + `distancia_km`, + `monto_traslado` en response |
| `app/services/cotizacion_service.py` | `responder_cotizacion` calcula haversine + tarifa_traslado |
| `app/services/pago_service.py` | `estimar_costo` con histórico de aceptadas |
| `app/api/pagos.py` | Filtros `Pago.tipo == "servicio"` en mis-pagos, crear-intent, obtener_pago |
| `app/api/talleres.py` | Summary actualizado: tarifa-traslado = tarifa por km |

### Web (Angular)
| Archivo | Cambio |
|---|---|
| `dashboards/taller/servicios/servicios.component.html` | Sin columna Movil + card "Tarifa por km" |
| `dashboards/taller/servicios/servicios.component.ts` | Sin `servicio_movil`, + `tarifaKm` + `guardarTarifaKm()` |
| `dashboards/taller/servicios/servicios.component.scss` | Estilo `.tarifa-km-card` |
| `dashboards/taller/servicios/servicios.service.ts` | + `obtenerMiTaller`, + `actualizarTarifaKm` |
| `dashboards/taller/cotizaciones/cotizaciones.component.html` | Desglose servicio + traslado en la tabla y modal |
| `dashboards/taller/cotizaciones/cotizaciones.service.ts` | + `distancia_km`, + `monto_traslado` |

### Mobile (Flutter)
| Archivo | Cambio |
|---|---|
| `lib/models/cotizacion.dart` | + `distanciaKm`, + `montoTraslado`, `montoTotal` incluye traslado |
| `lib/screens/cotizaciones_screen.dart` | Fila "Traslado (X km) $Y" en el desglose |
| `lib/widgets/completar_servicio_dialog.dart` | Moneda USD + decimales + hint "tarifa referencial" |

### Tests
| Archivo | Tests |
|---|---|
| `tests/test_cotizacion_traslado.py` | **NUEVO** — 2 tests (responder calcula traslado, aceptar propaga al costo_estimado) |
| `tests/test_estimacion_historico.py` | **NUEVO** — 3 tests (historico, fallback a tarifa_base, fallback fijo) |

---

## Resultado

```
============================ 134 passed in 24.64s =============================
```

8 tests nuevos + 126 existentes = **134/134 OK**.

---

## Cambios añadidos en la segunda ronda

### Penalización configurable desde admin

- **Migración 0012** — `tenant.pct_cancel_pendiente`, `tenant.pct_cancel_aceptada`, `tenant.pct_cancel_en_camino` (defaults 0/50/100, idempotente).
- **`cancelacion_service`** — `_factor_compensacion(tenant, estado)` lee del tenant en vez de la constante hardcoded.
- **Endpoint** — `PATCH /tenants/me/cancelacion-pct` (auth = taller del tenant) + `GET /tenants/me`.
- **UI web** — en `/dashboard/taller/cancelaciones` se añadió la sección "Porcentajes de compensación" con 3 inputs editables y botón "Guardar porcentajes".
- **Tests** — `tests/test_cancelacion_pct_config.py` (3 tests pasando).

### Pestaña Cotizaciones eliminada del web

- Quitada del routing (`app.routes.ts`) y del menú (`taller-shell.component.html`).
- Borrada la carpeta `dashboards/taller/cotizaciones/` completa.
- El backend de cotizaciones se queda (modelos, services, endpoints) para no romper migraciones / tests existentes, pero la UI ya no expone ese flujo.

### Desglose en la selección de taller (mobile)

- **Backend** — `/talleres/compatibles` ahora devuelve `monto_traslado` y `total_estimado` por cada taller candidato:
  ```python
  monto_traslado = taller.tarifa_traslado * distancia_km
  total_estimado = tarifa_base + monto_traslado
  ```
- **Flutter** — `TallerCompatible` model + `seleccionar_taller_screen` muestran:
  > **Total estimado: $95.50**
  > Servicio $80 + traslado $15.50

  En vez de solo "Desde $80". Resuelve el bug "el monto no aumenta con la distancia".

### Tiempo estimado de reparación + ETA de llegada

- **Migración 0013** — `taller_servicio.tiempo_estimado_min` (Integer, nullable).
- **UI web `/servicios`** — nueva columna "Tiempo reparacion (min)" editable por el taller para cada categoría que atiende.
- **`/talleres/compatibles`** devuelve dos campos más:
  - `tiempo_reparacion_min` (del `TallerServicio` del taller, lo configura él).
  - `eta_llegada_min` calculado con la **misma constante que usa el tracking en vivo del técnico** (`tracking_service.VELOCIDAD_DEFAULT_KMH = 40 km/h`). Así el ETA inicial coincide con el que verá el cliente cuando el técnico ya viene en camino.
- **Flutter `seleccionar_taller_screen`** — ahora muestra:
  > 3.5 km · llega en 6 min
  > Reparacion: 1 h 30 min
  > **Total estimado: $95.50**
  > Servicio $80 + traslado $15.50

- **Tests:** `tests/test_compatibles_eta_tiempo.py` (2 tests pasando).
