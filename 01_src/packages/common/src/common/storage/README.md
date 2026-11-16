# Ejemplo uso en capas de dominio (por ejemplo en data, en services, ...)

from common.storage.blob import upload_json

def save_memoria_json(memoria_id: str, data: dict) -> str:
    blob_name = f"memorias/{memoria_id}/memoria.json"
    return upload_json("memorias", blob_name, data)

# xxx


