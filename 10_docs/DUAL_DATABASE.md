# Arquitectura de doble base de datos

## Concepto

El sistema gestiona dos bases de datos PostgreSQL con responsabilidades distintas:

| | Primary | Secondary |
|---|---|---|
| **Propósito** | Datos operacionales / primarios del proyecto | Datos de referencia / integración externa |
| **Cuándo se escribe** | Escritura frecuente durante la operación normal | Escritura controlada, normalmente desde procesos de integración |
| **Permanencia** | Ciclo de vida definido por el proyecto | Permanente |
| **Prefijo env vars** | `POSTGRES_*` | `SECONDARY_POSTGRES_*` |

---

## Variables de entorno

Definidas en `.env`, `.env.example` y `.env.test`:

```ini
# Primary (base de datos primaria)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=your_work_db
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_secure_password

# Secondary (base de datos secundaria)
SECONDARY_POSTGRES_HOST=localhost
SECONDARY_POSTGRES_PORT=5432
SECONDARY_POSTGRES_DB=your_secondary_db
SECONDARY_POSTGRES_USER=your_postgres_user
SECONDARY_POSTGRES_PASSWORD=your_secure_password
```

---

## Configuración (`settings.py`)

`DatabaseSettings.from_env(prefix)` acepta un prefijo para leer el conjunto
de variables correspondiente. `Settings` expone los dos campos:

```python
class Settings(BaseModel):
    app: AppSettings
    db_work:      DatabaseSettings  # Primary  — base de datos primaria
    db_secondary: DatabaseSettings  # Secondary — base de datos secundaria

# get_settings() los instancia con su prefijo
db_work      = DatabaseSettings.from_env(prefix="POSTGRES")
db_secondary = DatabaseSettings.from_env(prefix="SECONDARY_POSTGRES")
```

---

## Motores y sesiones (`database.py`)

Cada base de datos tiene su propio bloque de objetos SQLAlchemy:

| Concepto | Primary | Secondary |
|---|---|---|
| Motor SQLAlchemy | `engine` | `engine_secondary` |
| Fábrica de sesiones | `SessionLocal` | `SessionSecondary` |
| Base para modelos ORM | `Base` | `BaseSecondary` |
| Dependencia FastAPI | `get_db()` | `get_secondary_db()` |
| Context manager scripts | `session_scope()` | `secondary_session_scope()` |

---

## Regla de uso

| Si el modelo pertenece a... | Hereda de | Sesión en el router |
|---|---|---|
| Primary | `Base` | `Depends(get_db)` |
| Secondary | `BaseSecondary` | `Depends(get_secondary_db)` |

---

## Ejemplos de uso en routers

`Ejemplo: POST /items/` usa `get_db` y escribe en la Primary:

```python
# interfaces/routers/item.py
@router.post("/items/", response_model=ItemRead, status_code=201)
def create_item(body: ItemCreate, db: Session = Depends(get_db)):
    return ItemService(db).create_item(body)
```

`Ejemplo: POST /records/` usa `get_secondary_db` y escribe en la Secondary:

```python
# interfaces/routers/record.py
@router.post("/records/", response_model=RecordRead, status_code=201)
def create_record(body: RecordCreate, db: Session = Depends(get_secondary_db)):
    return RecordService(db).create_item(body)
```

---

## Cómo añadir un nuevo modelo

### Primary — modelo en `data/models/postgres/`

**1. Crear el modelo** heredando de `Base`:

```python
# data/models/postgres/my_model.py
from data.database import Base

class MyModel(Base):
    __tablename__ = "work_my_models"
    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name        = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    status      = Column(String(50), default="pending")
```

**2. Registrarlo** en `data/models/postgres/__init__.py`:

```python
from .my_model import MyModel
```

**3. Crear el router** usando `get_db`:

```python
# interfaces/routers/my_model.py
@router.post("/my-models/", response_model=MyModelRead, status_code=201)
def create_my_model(body: MyModelCreate, db: Session = Depends(get_db)):
    return MyModelService(db).create_item(body)
```

### Secondary — modelo en `data/models/secondary/`

**1. Crear el modelo** heredando de `BaseSecondary`:

```python
# data/models/secondary/my_record.py
from data.models.secondary.base import BaseSecondary

class MyRecord(BaseSecondary):
    __tablename__ = "secondary_my_records"
    id    = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name  = Column(String(100), nullable=False)
```

**2. Registrarlo** en `data/models/secondary/__init__.py`:

```python
from .my_record import MyRecord
```

**3. Crear el router** usando `get_secondary_db`:

```python
@router.post("/records/", response_model=MyRecordRead, status_code=201)
def create_record(body: MyRecordCreate, db: Session = Depends(get_secondary_db)):
    return MyRecordService(db).create_item(body)
```

**4. Generar y aplicar la migración** (ver sección Alembic):

```bash
alembic revision --autogenerate -m "add work_my_models"
alembic upgrade head
```

---

## Migraciones Alembic

Dos configuraciones independientes, cada una con su carpeta de versiones:

```
01_src/packages/data/
├── alembic_secondary.ini    → Secondary  (settings.db_secondary.url + BaseSecondary.metadata)
├── alembic.ini              → Primary            (settings.db_work.url   + Base.metadata)
├── migrations_secondary/    → versiones del Secondary
│   ├── env.py
│   └── versions/
└── migrations/              → versiones de la Primary
    ├── env.py
    └── versions/
```

Comandos (desde `01_src/packages/data/`):

```bash
# Primary
alembic upgrade head
alembic revision --autogenerate -m "descripcion"

# Secondary
alembic -c alembic_secondary.ini upgrade head
alembic -c alembic_secondary.ini revision --autogenerate -m "descripcion"
```
