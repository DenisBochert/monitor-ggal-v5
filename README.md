# Refactor V3 Monitor Galicia

Base nueva creada desde `C:\Proyectos\Bolson\monitor_galicia_tiempo_real_v369.py`.

## Estructura

- `monitor.py`: copia de trabajo basada en v369.
- `legacy/monitor_galicia_tiempo_real_v369.py`: snapshot sin tocar para comparar.
- `data/monitor_galicia.sqlite3`: base chica encontrada en `C:\Proyectos\Bolson\data`.
- `salida_monitor/`: datos mínimos recientes para arrancar en modo offline.
- `requirements.txt`: freeze del virtualenv anterior, sin el editable viejo.
- `.venv/`: virtualenv local nuevo para este proyecto.
- `docs/refactor_audit.md`: primer inventario de bugs/riesgos/lentitud.

## Arranque

```powershell
.\.venv\Scripts\python.exe monitor.py --offline --salida .\salida_monitor
```

Para ejecución online, mantener el mecanismo original del monitor: usar `contras.py` desde la carpeta de contraseñas original.

El script busca credenciales como el programa original:

- `contras.py` en esta carpeta.
- `..\contras\contras.py` respecto de esta carpeta.
- `C:\Proyectos\Contras\contras.py`, equivalente a la carpeta raiz usada por el monitor original.
- módulo `contras` disponible en `sys.path`.

## Datos pesados no copiados

El archivo `C:\Proyectos\Bolson\salida_monitor\historial_GGAL.sqlite` pesa aproximadamente 1.18 GB y fue copiado a `salida_monitor/` junto con sus archivos `-wal` y `-shm`.

## Cambios de interfaz en esta base

Las pestañas separadas `Calls`, `Puts`, `Acciones` y `Futuros` fueron reemplazadas por `Compacta`.

La vista `Compacta` muestra arriba Galicia CI/24 hs y futuros disponibles, y debajo una tabla unificada por strike con calls a la izquierda, strike al centro y puts a la derecha.

La pestaña `Matriz bases` fue reemplazada por `Ratios`. `Ratios` permite alternar entre vista cuadro y vista cadena, elegir Call/Put, definir una base central, seleccionar saltos entre bases y editar los umbrales de color.
