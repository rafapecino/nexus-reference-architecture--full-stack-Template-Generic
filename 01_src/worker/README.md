# Worker base

Instalacion (entorno local):
- `pip install -r requirements.txt`
- Los paquetes compartidos (`contracts`, `data`, `common`) se instalan en editable via los path relativos definidos en `requirements.txt`.

Ejecucion:
- Usa `worker.main.bootstrap()` para inicializar logging y conectar el trigger que corresponda.
