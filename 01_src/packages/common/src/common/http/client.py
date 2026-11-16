# Para no repetir clientes HTTP.
# Esto evita que cada API/worker haga su propio “requests.get” mal configurado.

import httpx


async def get(url: str, **kwargs):
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, **kwargs)
        resp.raise_for_status()
        return resp.json()
