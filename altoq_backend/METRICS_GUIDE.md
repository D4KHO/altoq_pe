# Guía del Módulo de Métricas del Emprendedor

## Descripción
El módulo de métricas permite a los emprendedores ver el desempeño de su tienda a través de diferentes indicadores clave: visitas, ventas, ingresos, sesiones de chat, uso de templates, y más.

## Modelo de Datos

### StoreMetric
- `store_id`: ID de la tienda
- `date`: Fecha del registro (un registro por día por tienda)
- `visits`: Número de visitas a la tienda ese día
- `products_published`: Productos activos en el catálogo
- `orders_delivered`: Pedidos con código de entrega validado
- `revenue`: Monto total generado ese día (S/)
- `chat_sessions`: Chats de pedidos iniciados
- `template_usage`: Veces que se usó el flujo de templates
- `new_users`: Compradores nuevos que interactuaron
- `avg_rating`: Promedio de calificaciones acumulado
- `created_at`: Fecha de creación del registro
- `updated_at`: Fecha de última actualización

## Endpoints API

### 1. Dashboard Resumen
**GET** `/api/seller/metrics/dashboard`

Obtiene el resumen general del dashboard para la tienda del usuario actual.

**Respuesta:**
```json
{
  "store_id": 1,
  "total_visits": 1500,
  "total_products": 25,
  "total_orders_delivered": 45,
  "total_revenue": 3450.50,
  "total_chat_sessions": 120,
  "average_rating": 4.5,
  "today_visits": 25,
  "today_orders": 3,
  "today_revenue": 230.00,
  "weekly_growth": 15.5
}
```

### 2. Métricas por Período
**GET** `/api/seller/metrics/?period=daily&days=30`

Obtiene las métricas para un período específico.

**Parámetros:**
- `period`: "daily", "weekly", o "monthly"
- `days`: Número de días a retroceder (1-365)

**Respuesta:**
```json
[
  {
    "id": 1,
    "store_id": 1,
    "date": "2026-06-10",
    "visits": 25,
    "products_published": 25,
    "orders_delivered": 3,
    "revenue": 230.00,
    "chat_sessions": 8,
    "template_usage": 2,
    "new_users": 5,
    "avg_rating": 4.5,
    "created_at": "2026-06-10T00:00:00",
    "updated_at": "2026-06-10T12:30:00"
  }
]
```

### 3. Métricas por Fecha Específica
**GET** `/api/seller/metrics/date/{metric_date}`

Obtiene las métricas de una fecha específica.

**Parámetros:**
- `metric_date`: Fecha en formato YYYY-MM-DD

### 4. Registrar Visita
**POST** `/api/seller/metrics/visit`

Registra una visita a la tienda del usuario actual.

**Respuesta:**
```json
{
  "message": "Visita registrada exitosamente",
  "date": "2026-06-10",
  "total_visits": 26
}
```

### 5. Actualizar Métricas Manualmente
**POST** `/api/seller/metrics/refresh`

Actualiza manualmente las métricas de la tienda (productos publicados y rating promedio).

**Respuesta:**
```json
{
  "message": "Métricas actualizadas exitosamente",
  "products_published": 25,
  "average_rating": 4.5
}
```

### 6. Resumen por Rango de Fechas
**GET** `/api/seller/metrics/summary?start_date=2026-06-01&end_date=2026-06-10`

Obtiene un resumen de métricas para un rango de fechas específico.

**Parámetros:**
- `start_date`: Fecha de inicio (YYYY-MM-DD)
- `end_date`: Fecha de fin (YYYY-MM-DD)

**Respuesta:**
```json
{
  "period": {
    "start_date": "2026-06-01",
    "end_date": "2026-06-10",
    "days": 10
  },
  "totals": {
    "visits": 250,
    "orders_delivered": 30,
    "revenue": 2300.00,
    "chat_sessions": 80,
    "template_usage": 15,
    "new_customers": 45
  },
  "averages": {
    "daily_visits": 25.0,
    "daily_orders": 3.0,
    "daily_revenue": 230.0
  }
}
```

### 7. Comparación de Períodos
**GET** `/api/seller/metrics/comparison?period1_days=7&period2_days=7`

Compara métricas entre dos períodos para identificar tendencias.

**Parámetros:**
- `period1_days`: Días del período 1 (reciente)
- `period2_days`: Días del período 2 (anterior)

**Respuesta:**
```json
{
  "period1": {
    "start_date": "2026-06-03",
    "end_date": "2026-06-10",
    "days": 7,
    "visits": 175,
    "orders": 21,
    "revenue": 1610.00
  },
  "period2": {
    "start_date": "2026-05-27",
    "end_date": "2026-06-02",
    "days": 7,
    "visits": 150,
    "orders": 18,
    "revenue": 1350.00
  },
  "changes": {
    "visits_percent": 16.67,
    "orders_percent": 16.67,
    "revenue_percent": 19.26
  }
}
```

## Funciones de Utilidad

El módulo incluye funciones automáticas para actualizar métricas cuando ocurren eventos:

### `increment_visits(db, store_id, increment=1)`
Incrementa el contador de visitas para una tienda en la fecha actual.

### `increment_chat_sessions(db, store_id, increment=1)`
Incrementa el contador de sesiones de chat para una tienda en la fecha actual.

### `increment_template_usage(db, store_id, increment=1)`
Incrementa el contador de uso de templates para una tienda en la fecha actual.

### `record_order_delivery(db, store_id, order_amount)`
Registra una entrega de pedido para una tienda en la fecha actual.

### `record_new_customer(db, store_id)`
Registra un nuevo cliente para una tienda en la fecha actual.

### `update_products_published(db, store_id)`
Actualiza el contador de productos publicados para una tienda en la fecha actual.

### `update_average_rating(db, store_id)`
Actualiza el rating promedio de una tienda en la fecha actual.

## Integración con Otros Módulos

Para integrar el cálculo automático de métricas en otros módulos:

### En el módulo de Chat (chat.py)
```python
from ..utils.metrics import increment_chat_sessions

# Al iniciar un nuevo chat
increment_chat_sessions(db, store_id)
```

### En el módulo de Delivery (delivery.py)
```python
from ..utils.metrics import record_order_delivery

# Al validar un código de entrega
record_order_delivery(db, store_id, order.total_amount)
```

### En el módulo de Templates (templates.py)
```python
from ..utils.metrics import increment_template_usage

# Al usar un template para publicar un producto
increment_template_usage(db, store_id)
```

### En el módulo de Productos (products.py)
```python
from ..utils.metrics import update_products_published, update_average_rating

# Al crear, editar o eliminar un producto
update_products_published(db, store_id)
update_average_rating(db, store_id)
```

## Ejemplo de Uso

```python
# Ejemplo: Registrar una visita cuando alguien ve la tienda
POST /api/seller/metrics/visit

# Ejemplo: Ver el dashboard
GET /api/seller/metrics/dashboard

# Ejemplo: Ver métricas de los últimos 30 días
GET /api/seller/metrics/?period=daily&days=30

# Ejemplo: Comparar esta semana con la semana anterior
GET /api/seller/metrics/comparison?period1_days=7&period2_days=7
```

## Notas Importantes

1. **Un registro por día**: El sistema crea automáticamente un registro de métricas por día por tienda. Si no existe, lo crea al primer evento del día.

2. **Actualización automática**: Las métricas se actualizan automáticamente cuando ocurren eventos relevantes (visitas, ventas, chats, etc.).

3. **Conversión de tipos**: Los valores monetarios (revenue) se almacenan como `Numeric` en la base de datos pero se retornan como `float` en la API para facilitar el uso en el frontend.

4. **Cálculo de crecimiento**: El crecimiento semanal se calcula comparando los ingresos de la semana actual con la semana anterior.

5. **Rating promedio**: El rating promedio se calcula basándose en el promedio de ratings de todos los productos de la tienda.

## Pruebas

Para probar el módulo de métricas:

1. Asegúrate de tener una tienda creada
2. Usa el endpoint `/api/seller/metrics/visit` para registrar visitas
3. Usa el endpoint `/api/seller/metrics/dashboard` para ver el resumen
4. Usa el endpoint `/api/seller/metrics/refresh` para actualizar métricas manualmente
