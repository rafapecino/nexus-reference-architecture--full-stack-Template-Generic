"""
Ejemplo de script de seed usando el modelo Item genérico.

Uso:
    .venv/Scripts/python.exe 03_data/seed_example.py
"""

import sys
from pathlib import Path

# Añadir raíz al path para importar paquetes del workspace
root = Path(__file__).parents[1]
sys.path.insert(0, str(root / "01_src" / "packages" / "data" / "src"))
sys.path.insert(0, str(root / "01_src" / "packages" / "common" / "src"))

from data.database import SessionLocal
from data.models.item import Item


def seed():
    db = SessionLocal()
    try:
        items = [
            Item(name="Item de ejemplo 1", description="Descripción del primer item"),
            Item(name="Item de ejemplo 2", description="Descripción del segundo item"),
            Item(name="Item de ejemplo 3", description=None),
        ]
        db.add_all(items)
        db.commit()
        print(f"Insertados {len(items)} items.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
