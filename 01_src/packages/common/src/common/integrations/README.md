Aquí podremos incluir paquetes comunes de integración.

Por ejemplo:
    librería compartida “AsanaClient” (no necesitas centralizar en un microservicio… todavía)

    Para las llamadas online del backend (por usuario con OAuth):

    Yo crearía un paquete común tipo common.integrations.asana con:

    AsanaClient (wrapper del SDK/HTTP)

    gestión de tokens (recibir access token ya emitido; refresco si aplica)

    errores tipados (403/429/etc.)

    funciones bien nombradas (get_task, update_task, list_projects…)

    Y el backend lo usa directamente.

    ✅ Ventajas:

    Menos hop/latencia (no metes un “gateway API” adicional).

    Menos piezas a desplegar en MVP.

    Sigue estando centralizado “en código” (una librería) aunque no “en runtime”.