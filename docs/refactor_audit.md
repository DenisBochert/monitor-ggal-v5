# Auditoria inicial v369

Fecha: 2026-05-15.

## Base tomada

- Origen: `C:\Proyectos\Bolson\monitor_galicia_tiempo_real_v369.py`.
- Copia de trabajo: `monitor.py`.
- Snapshot original: `legacy/monitor_galicia_tiempo_real_v369.py`.

## Datos encontrados

- `C:\Proyectos\Bolson\data\monitor_galicia.sqlite3`: 57 KB, copiado a `data/`.
- `C:\Proyectos\Bolson\salida_monitor\historial_GGAL.sqlite`: ~1.18 GB, no copiado.
- `C:\Proyectos\Bolson\salida_monitor\monitor_galicia.log`: ~49 MB, no copiado.
- Datos recientes copiados a `salida_monitor/`: `marketdata_GGAL_latest.json`, `ui_state_GGAL.json`, cache y tickers del 2026-05-15.

## Bugs y riesgos visibles

1. La cabecera decia `Script v339.0` y `VERSION_SCRIPT` decia `362.0` aunque el archivo base es v369. La copia de trabajo ya quedó en `369.0`.
2. La documentacion interna seguia mencionando comandos `monitor_galicia_tiempo_real_v45.py` y requirements viejos. La copia de trabajo ya apunta a `monitor.py` y `requirements.txt`.
3. `main()` solo cierra conexiones en `finally` si `STOP_EVENT.is_set()`. Si la UI termina sin activar ese flag, el cierre queda delegado a otras rutas; revisar en el refactor de ciclo de vida.
4. Hay muchos `except Exception` silenciosos o casi silenciosos. Esto oculta fallas en UI, persistencia, importacion de historicos y cierre de recursos.
5. El archivo de credenciales real esta en `C:\Proyectos\Contras\contras.py`. Por decision del proyecto, esta base mantiene la busqueda original de `contras.py` y no migra a `.env`/`credentials.enc`.

## Cuellos de botella probables

1. `MonitorGaliciaUI` tiene unas 20.898 lineas y concentra estado, graficos, tablas, backtests y persistencia. Es el principal punto de riesgo para lentitud y bugs.
2. `MonitorGaliciaUI.__init__` tiene ~1.078 lineas. Conviene separar inicializacion de estado, widgets, datos historicos y timers.
3. `_cargar_estado_ui_guardado` tiene ~863 lineas. Carga y normaliza demasiadas preferencias en una sola pasada; es buen candidato para tests y funciones puras.
4. `SheetTableAdapter._sheet_set_data` reconstruye matrices y listas varias veces por refresco. En tablas grandes esto genera CPU y memoria innecesarias.
5. `_refrescar_ui` compara matrices completas (`data != self._current_data`) y puede ejecutarse seguido por `root.after`. En vivo, esta comparacion O(filas * columnas) puede ser una fuente directa de lentitud.
6. El historico principal en SQLite ya supera 1 GB. Las consultas intradia/backtest deben revisarse con `EXPLAIN QUERY PLAN` antes de agregar mas calculos sobre la UI.

## Primer orden recomendado de refactor

1. Congelar comportamiento con pruebas pequeñas para funciones puras: clasificacion, normalizacion, Black-Scholes, IV, relaciones y carga de estado UI.
2. Extraer constantes/configuracion y modelos (`InstrumentoClasificado`, `EstadoMercado`) a modulos propios.
3. Separar acceso SQLite de la UI y medir consultas principales con el historico grande.
4. Optimizar refresco de tablas para actualizar solo cuando cambia la secuencia de market data o un hash liviano de filas visibles.
5. Separar la UI por vistas: comparador, relaciones, intradia, backtest y cierre.

## Cambio aplicado: vista compacta

- Se eliminaron las pestañas principales separadas `Calls`, `Puts`, `Acciones` y `Futuros`.
- Se agrego la pestaña `Compacta`.
- `Compacta` carga una tabla superior con acciones/futuros y una tabla de opciones unificada por strike.
- La seleccion de una fila compacta actualiza internamente el call y put elegidos para mantener continuidad con selectores existentes.

## Cambio aplicado: Ratios

- Se quito la pestaña principal `Matriz bases` del notebook.
- Se agrego la pestaña `Ratios`.
- `Ratios` incluye vista cuadro, vista cadena expandible, selector Call/Put, base central, salto 1-4 y umbrales editables para colores.
