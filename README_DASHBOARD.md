# Guía Detallada: Consola de Administración y Métricas de ALTOQ

Este documento sirve como manual explicativo y técnico para comprender el funcionamiento, origen de datos e indicadores clave de rendimiento (KPIs) expuestos en la **Consola de Métricas** del administrador del marketplace ALTOQ.

---

## 📌 Tabla de Contenidos
1. [Introducción General](#1-introducción-general)
2. [Indicadores Clave de Rendimiento (KPI Cards)](#2-indicadores-clave-de-rendimiento-kpi-cards)
3. [Barra de Filtros y Herramientas](#3-barra-de-filtros-y-herramientas)
4. [Gráficos de Líneas Temporales (SVG Nativo)](#4-gráficos-de-líneas-temporales-svg-nativo)
5. [Ranking de Tiendas (Leaderboard Top 5)](#5-ranking-de-tiendas-leaderboard-top-5)
6. [Métricas de Tráfico y Adopción (Embudo de IA)](#6-métricas-de-tráfico-y-adopción-embudo-de-ia)
7. [Ficha Técnica: Base de Datos y Seguridad](#7-ficha-técnica-base-de-datos-y-seguridad)

---

## 1. Introducción General

La **Consola de Métricas** es un panel de control corporativo diseñado exclusivamente para el Super Administrador de ALTOQ. Su objetivo es brindar visibilidad en tiempo real sobre la salud comercial del negocio, la actividad del usuario y, principalmente, medir el impacto comercial y la adopción de las herramientas de inteligencia artificial de las tiendas del ecosistema.

Toda la información responde dinámicamente al **filtro de fecha seleccionado**, permitiendo realizar auditorías históricas precisas y analizar tendencias de crecimiento.

---

## 2. Indicadores Clave de Rendimiento (KPI Cards)

Ubicados en la parte superior del panel, muestran resúmenes consolidados de las cuatro variables operativas críticas del marketplace.

```
┌────────────────────────┐  ┌────────────────────────┐  ┌────────────────────────┐  ┌────────────────────────┐
│  VENTAS DE PLATAFORMA  │  │   PEDIDOS COMPLETADOS  │  │    USUARIOS ACTIVOS    │  │  TIENDAS REGISTRADAS   │
│       S/ 12,450.00     │  │           245          │  │          1,050         │  │           84           │
└────────────────────────┘  └────────────────────────┘  └────────────────────────┘  └────────────────────────┘
```

### A. Ventas de Plataforma
* **Qué representa:** El monto neto total en Soles (S/.) transaccionado por los clientes en la plataforma durante el período seleccionado.
* **Origen de datos:** Tabla `orders` de la base de datos MySQL.
* **Cálculo técnico:** Suma agregada del campo `total_amount` de todas las órdenes cuyo estado es `completed` (completadas) y cuya fecha de creación (`created_at`) se encuentra dentro del rango de tiempo filtrado.
* **Utilidad:** Mide el volumen económico total del marketplace (GTV - Gross Transaction Value).

### B. Pedidos Completados
* **Qué representa:** La cantidad total de pedidos que fueron finalizados y entregados con éxito en la plataforma.
* **Origen de datos:** Tabla `orders`.
* **Cálculo técnico:** Conteo físico (`COUNT`) de los registros en la tabla `orders` filtrados por el estado `status = 'completed'` dentro del rango de fechas.
* **Utilidad:** Mide la frecuencia de compra y el ritmo de envíos validados en el marketplace.

### C. Usuarios Activos
* **Qué representa:** El volumen total de cuentas de usuarios creadas en la plataforma.
* **Origen de datos:** Tabla `users`.
* **Cálculo técnico:** Conteo físico de registros en la tabla `users` creados en el rango. Adicionalmente, desglosa cuántos de estos tienen asignado el rol de comprador (`buyer`) y cuántos el de vendedor (`seller`).
* **Utilidad:** Permite ver el ritmo de adquisición de nuevos usuarios en la plataforma.

### D. Tiendas Registradas
* **Qué representa:** El volumen total de tiendas de vendedores creadas dentro del ecosistema de ALTOQ.
* **Origen de datos:** Tabla `stores`.
* **Cálculo técnico:** Conteo físico de registros en la tabla `stores`. Desglosa el estado operativo de las tiendas en tres categorías:
  * **Activas:** Tiendas aprobadas por el administrador que están vendiendo al público.
  * **Pendientes:** Nuevas tiendas en espera de ser evaluadas y aprobadas por el administrador.
  * **Suspendidas:** Tiendas desactivadas temporal o permanentemente debido a infracciones.
* **Utilidad:** Ayuda a controlar la oferta del marketplace y a identificar solicitudes de aprobación pendientes.

---

## 3. Barra de Filtros y Herramientas

Ubicada en la esquina superior derecha, permite gestionar el período de tiempo de las consultas y descargar la data cruda.

### A. Selector de Períodos (Presets)
Permite alternar de forma rápida entre filtros temporales estandarizados:
* **Últimos 7 días / Últimos 30 días:** Muestra la tendencia de la última semana o mes.
* **Este mes:** Filtra dinámicamente desde el día 1 del mes en curso hasta la fecha de hoy.
* **Mes anterior:** Calcula el primer y último día del mes calendario anterior.
* **Rango personalizado:** Abre dinámicamente los campos de calendario.

### B. Calendario de Rango Personalizado
* Habilita dos campos de fecha (`Desde` y `Hasta`). 
* Cuenta con una validación de seguridad de **máximo 365 días** por consulta. Esto previene que una consulta masiva (ej. 5 años diarios) colapse el servidor MySQL o ralentice la carga del navegador.

### C. Botón "Exportar" (Descarga de Excel)
* **Qué hace:** Descarga un reporte diario detallado en formato CSV compatible de forma nativa con Microsoft Excel en español.
* **Detalle técnico de compatibilidad:** El archivo incluye un **BOM UTF-8** (Byte Order Mark) y utiliza el **punto y coma (;) como delimitador**. Esto garantiza que al hacer doble clic en el archivo descargado en Windows, Excel interprete correctamente las columnas y caracteres del idioma español (acentos, letra ñ y símbolo de moneda) sin mostrar pantallas de importación confusas.

---

## 4. Gráficos de Líneas Temporales (SVG Nativo)

Los dos gráficos principales se dibujan utilizando tecnología vectorizada **SVG nativa calculada en Angular (TypeScript)**. No requieren dependencias externas de Canvas o ChartJS, logrando una velocidad de renderizado óptima y capacidad responsiva móvil.

```
                 RENDIMIENTO FINANCIERO (Ingresos y Órdenes)
  S/ 10k ┬                                      ╭╮ (Punto Hover: Muestra Tooltip)
         │                                     ╭╯╰╮
   S/ 5k ┼                 ╭╮                 ╭╯  ╰╮
         │               ╭─╯╰───────────────╮╭╯    ╰──────────
     S/ 0┴───────●───────╯──────────────────╰●────────────────
               01/07   03/07              05/07              08/07
```

### Gráfico A: Rendimiento Financiero
* **Línea Azul (Ingresos):** Curva continua que representa la facturación monetaria acumulada de cada día.
* **Línea Verde Discontinua (Órdenes):** Representa la cantidad física de pedidos procesados por día.
* **Interpretación:** Permite evaluar visualmente si los ingresos altos se deben a muchas compras pequeñas o a pocas compras de alto valor.

### Gráfico B: Interacción y Tracción
* **Línea Azul (Sesiones Chat):** Registra el volumen de conversaciones abiertas por día. Mide el uso de los asistentes conversacionales inteligentes de ALTOQ.
* **Línea Morada (Nuevos Usuarios):** Registra cuántas cuentas nuevas se registran cada día.
* **Interpretación:** Mide la viralidad y uso del software. Permite observar si los días de mayor registro de usuarios coinciden con un incremento en las sesiones de chat con la IA.

### Funcionalidad de Tooltips (Al pasar el mouse)
Al colocar el cursor encima de cualquier nodo (círculo) del gráfico, Angular calcula la posición relativa del cursor y despliega un cuadro emergente flotante con:
* La fecha exacta en formato amigable (ej. `05 Jul 2026`).
* Los valores exactos numéricos y monetarios correspondientes a ese día.

---

## 5. Ranking de Tiendas (Leaderboard Top 5)

Una tabla dinámica que expone el rendimiento comercial individual de las tiendas vendedoras más exitosas en la plataforma.

* **Estructura de Columnas:**
  * **Pos:** Posición ordinal (del #1 al #5) calculada de mayor a menor facturación.
  * **Tienda:** Nombre comercial del comercio.
  * **Dueño:** Muestra el nombre del vendedor responsable y su dirección de correo electrónico institucional debajo.
  * **Visitas:** Volumen de tráfico o visualizaciones que ha tenido la tienda.
  * **Órdenes:** Cantidad de pedidos con éxito despachados por esa tienda.
  * **Ventas (S/):** El dinero neto total generado por las ventas de la tienda.
  * **Estado:** Etiqueta colorida que resalta si la tienda está Activa, Pendiente o Suspendida.
* **Cálculo técnico:** El backend realiza un `LEFT JOIN` entre la tabla `stores` y la tabla `store_metrics` para consolidar y agrupar las sumatorias diarias de cada tienda antes de ordenar el resultado de forma descendente.

---

## 6. Métricas de Tráfico y Adopción (Embudo de IA)

Esta sección de barras de progreso ayuda al administrador a comprender la conversión de los usuarios mediante la interacción con los chatbots inteligentes (IA) de las tiendas.

```
┌────────────────────────────────────────────────────────────────┐
│  TRÁFICO Y ADOPCIÓN                                            │
│                                                                │
│  Total Visitas [████████████████████████████████████]   15,000  │
│  Sesiones Chat [██████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░]    3,000  │
│  └─ Tasa de interacción: 20.0% de los visitantes abren un chat │
│                                                                │
│  Uso de Plantillas [██████████████████████░░░░░░░░░] 750 veces │
│                                                                │
│  Conversión de la Plataforma:                             8.5% │
└────────────────────────────────────────────────────────────────┘
```

### A. Total Visitas
* Mide cuántas veces se han visualizado los escaparates de los vendedores en el rango de fechas.

### B. Sesiones de Chat IA
* Mide cuántos hilos de conversación han sido abiertos con los asistentes virtuales.

### C. Tasa de Interacción
* **Fórmula:** $\text{Tasa de Interacción} = \left( \frac{\text{Sesiones de Chat IA}}{\text{Total Visitas}} \right) \times 100$
* **Significado:** Indica la curiosidad o necesidad de soporte del cliente. Si es del 20%, significa que 2 de cada 10 visitantes deciden usar el bot de IA.

### D. Uso de Plantillas
* Mide cuántas veces los vendedores utilizaron la herramienta de creación de prompts/plantillas provista en su panel para personalizar y optimizar sus asistentes.

### E. Conversión de la Plataforma (Indicador de Éxito)
* **Fórmula:** $\text{Conversión} = \left( \frac{\text{Pedidos Completados}}{\text{Sesiones de Chat IA}} \right) \times 100$
* **Significado:** Es el KPI de efectividad comercial de la IA. Si la conversión es del 8.5%, significa que de cada 100 conversaciones asistidas por el chatbot inteligente, 8.5 usuarios terminan confirmando un pedido real en el marketplace.

---

## 7. Ficha Técnica: Base de Datos y Seguridad

Para fines de documentación técnica y académica del proyecto, se detallan los pilares de la integración:

1. **Protocolo de Seguridad (JWT):**
   Cualquier llamada a las APIs de métricas (`/api/admin/metrics/*`) debe adjuntar en las cabeceras HTTP un token de autorización Bearer válido (`Authorization: Bearer <TOKEN>`). El backend descodifica el token y valida que la propiedad `type` sea estrictamente `"admin"`. Si un cliente o vendedor común intenta acceder, el sistema lo rechaza automáticamente con un código HTTP `401 Unauthorized` ("Admin authentication required").

2. **CORS Middleware:**
   FastAPI tiene configurado el middleware de CORS para permitir solicitudes exclusivamente del origen autorizado del cliente (`http://localhost:4200` en desarrollo), previniendo vulnerabilidades de secuestro de peticiones en navegadores.

3. **Autorecarga del Servidor:**
   El archivo de arranque `run.py` está configurado con `reload=True` en su enrutamiento de Uvicorn, lo que asegura que cualquier cambio en caliente en los controladores de analíticas se despliegue de manera inmediata sin necesidad de apagar el servidor de desarrollo.
