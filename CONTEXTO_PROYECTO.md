# Monitor GGAL — Contexto del Proyecto

> Referencia para continuar la conversación en un nuevo chat.
> Archivo de trabajo: `C:\Proyectos\Refactor monitor V5\monitor.py` (~29 300 líneas)
> Backup estable: `monitor_stable.py` (misma carpeta)

---

## Qué hace el programa

Monitor integral de opciones sobre GGAL (Grupo Financiero Galicia) en tiempo real. En una sola aplicación de escritorio Tkinter concentra:

- Descarga y caché local de instrumentos (opciones, acciones, futuros) vía pyRofex REST.
- Conexión WebSocket para recibir bid / ask / last en tiempo real (reconexión automática).
- Cálculo de volatilidad implícita, griegas (delta, theta, vega) y GEX por strike.
- Persistencia en SQLite (~1 GB, **no tocar**) y snapshots JSON por minuto.
- Interfaz con múltiples pestañas, refresco adaptativo (120 ms en mercado abierto, 1 200 ms fuera).
- Soporte offline: usa instrumentos y cierres del día anterior si la API no responde.

---

## Cómo se conecta

### Credenciales — `contras.py`
Debe existir en la misma carpeta que `monitor.py`:

```python
usuario = "TU_USUARIO"
contra  = "TU_PASSWORD"
cuenta  = "TU_CUENTA"
entorno = "REMARKET"   # o "LIVE"
```

### Flujo de arranque
1. `pyRofex.initialize(...)` con las credenciales de `contras.py`.
2. Descarga `get_detailed_instruments()` → filtra por aliases de GGAL (`GGAL`, `GFG`, `GALICIA`, …).
3. Abre WebSocket con `pyRofex.init_websocket_connection(...)` y suscribe los tickers activos.
4. El handler WS escribe en un buffer thread-safe; el loop de UI lo consume.
5. Thread `AnalyticsWorker` calcula IV y griegas en paralelo sin bloquear la UI.
6. Reconexión automática en segundo plano si el WS cae.

### Ejecución
```bash
python monitor.py                        # GGAL por defecto
python monitor.py --subyacente GGAL
python monitor.py --salida ./mi_salida   # directorio de persistencia
```

---

## Persistencia local

| Archivo | Contenido |
|---|---|
| `historial_GGAL.sqlite` | Snapshots por minuto + cierres diarios (~1 GB, **nunca borrar**) |
| `ui_state_GGAL.json` | Estado de la UI (vencimiento activo, splits, columnas) |
| `ui_distribution_GGAL.json` | Anchos de columnas persistidos por el usuario |
| `instrumentos_*.json` | Caché diaria de instrumentos descargados |
| `cierre_*.json` | Cierres diarios automáticos (17:05 hs) |

---

## Vistas (pestañas)

### 1. Compacta
Vista unificada que reemplaza las antiguas pestañas Calls, Puts, Acciones y Futuros.
- Tabla superior: precio spot de GGAL CI / 24hs y futuros vigentes.
- Tabla inferior: opciones por strike, con columnas bid / ask / last / IV / delta / theta / GEX.
- Solo muestra strikes con actividad (bid, ask o last no nulos).
- Selector de vencimiento compartido con el resto de la app.
- Clic en una fila selecciona el par call/put para las otras vistas.

### 2. Tabla relaciones
Compara dos bases (call o put) elegidas por el usuario.
- Columnas: last A, last B, ratio A/B, A+B, Δ(A+B), A−B, Δ(A−B), Δ(−A+2B), ask A − bid B.
- Implementada con `SheetTableAdapter` (wrapper de `tksheet`) para coloreo por celda.
- Soporta múltiples subvistas (slots), reordenado de columnas por drag, Ctrl+clic para seleccionar columnas y clic derecho para graficarlas en popup flotante.
- Modo ratio: muestra el cociente de precios normalizado.
- Guarda anchos de columna configurados por el usuario.

### 3. Tabla rel. intradía
Igual que Tabla relaciones pero con datos históricos intradía del SQLite.
- Selector de fecha + intervalo (1 min a 1 hora, o "solo cambios").
- Base A y Base B elegibles independientemente.
- Popup con gráfico histórico del ratio seleccionado.

### 4. Backtest cobertura
Simula reversión a la media sobre dos bases con tamaño de posición cubierto.
- Misma señal que Tabla rel. intradía, pero calcula PnL con lotes cubiertos.
- Parámetros: día, bases A y B, umbral de entrada/salida, tamaño.
- Muestra equity curve y métricas de la estrategia.

### 5. Cadena *(nueva, esta sesión)*
Vista tipo "cadena de opciones" centrada en el ATM, con ratios de pendiente entre strikes.
- Columnas: `PUT | P-N … P-1 | STRIKE | C+1 … C+N | CALL`
- Los encabezados incluyen el valor real del strike entre paréntesis, e.g. `C+1 (7.800)`.
- Número de bases configurable con un Spinbox (1–8).
- Botones `‹` / `›` para desplazar el rango de strikes visible.
- **Fórmula de ratio call:** `(call(K) − call(K+n)) / (K+n − K) × 100`
- **Fórmula de ratio put:** `(put(K) − put(K−n)) / (K − K−n) × 100`
- Coloreo por celda según nivel del ratio (verde bajo → rojo alto).
- La fila ATM se resalta con fondo azul y texto dorado.
- Precios en columnas PUT/CALL: `last` → `bid` → `ask` → `ref` (primer valor disponible).
- Actualiza en vivo (120 ms en mercado abierto).

---

## Stack técnico

| Componente | Uso |
|---|---|
| `pyRofex` | Conexión REST + WebSocket a ByMA/ROFEX |
| `tkinter` + `ttk` | GUI principal |
| `tksheet` v7.6.0 | Grillas con coloreo por celda (`TksheetWidget = Sheet`) |
| `SQLite` | Persistencia histórica |
| `threading` | WS, analytics worker, reconexión automática |
| `scipy` / `math` | IV por bisección, griegas Black-Scholes |

### Notas de tksheet
- Font requiere 3-tuple: `("Consolas", 14, "normal")` — 2-tuple crashea.
- `sheet.headers(lista, redraw=False)` — actualiza cabeceras sin resetear posiciones.
- `sheet.set_sheet_data(data, reset_col_positions=bool, redraw=False)` — resetear solo cuando cambia el número de columnas.
- `sheet.highlight_cells(row=r, column=c, bg=bg, fg=fg, redraw=False)` — coloreo por celda.
- `sheet.column_width(i, width=w)` — ancho por índice.

---

## Estado del refactor (sesiones anteriores)

Cambios ya aplicados sobre el original (`monitor-e8dae4c9.py`, 28 925 líneas):

- Eliminadas pestañas: Smile VI, Comparador 2 bases, Registro spread, Registro ratio invertido, Comparador intradía, Ratios.
- Loop de refresco limpiado (ramas muertas removidas).
- Event handlers de sub-notebooks eliminados neutralizados con `hasattr`.
- Floor de tab-switch reducido de 250 ms a 120 ms.
- Query SQLite duplicada al arranque eliminada.
- Mapas de hidratación de pestañas actualizados.
- `_precio_subyacente_actual` cacheado en el objeto.
- Vista Cadena creada de cero (`_crear_vista_cadena`, `_refrescar_cadena`, `_cadena_navegar`, `_color_cadena_celda`, `_cadena_tono_atm`).

---

## Pendientes / ideas a continuar

- **Columnas Cadena auto-ancho**: las columnas deberían adaptarse al contenido del texto más largo visible (actualmente tienen anchos fijos: PUT/CALL 115 px, bases 100 px, STRIKE 90 px).
- Revisar si conviene agregar una fila resumen/totales en Cadena.
- Posible mejora: resaltar filas con ratio extremo (> umbral configurable).
- El Backtest cobertura aún no fue tocado en este refactor — candidato a mejora.

---

## Archivos clave

```
C:\Proyectos\Refactor monitor V5\
├── monitor.py              ← archivo de trabajo principal
├── monitor_stable.py       ← backup de la última versión estable
├── contras.py              ← credenciales (no subir a git)
├── legacy\
│   └── monitor_galicia_tiempo_real_v369.py   ← referencia histórica
└── salida\
    ├── historial_GGAL.sqlite   ← ~1 GB, NUNCA borrar
    └── ...
```
