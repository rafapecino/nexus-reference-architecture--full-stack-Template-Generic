# Estructura de carpetas del proyecto

Este documento explica para qué sirve cada carpeta del repositorio, en lenguaje sencillo.

---

## La idea general

El repositorio está organizado en carpetas numeradas. Los números no son casuales: indican el **tipo de contenido** y ayudan a que cualquier persona del equipo (desarrollador, analista, responsable de infraestructura) encuentre lo que busca sin tener que conocer toda la arquitectura del proyecto.

```
repo/
├─ 00_governance/
├─ 01_src/
├─ 02_artifacts/
├─ 03_data/
├─ 04_gitops_manifests/
├─ 05_notebooks/
├─ 06_architecture/
├─ 07_tests/
├─ 08_monitoring/
├─ 09_configs/
└─ 10_docs/
```

---

## Carpeta por carpeta

### `00_governance/` — Cómo gestionamos el proyecto

Aquí viven los documentos que explican **cómo trabajamos**, no qué construimos.

- `RUNBOOK.md` → Qué hacer si algo falla en producción (paso a paso).
- `SLA_DEFINITION.md` → Compromisos de disponibilidad y tiempos de respuesta.
- `CHANGE_LOG.md` → Qué ha cambiado y cuándo.
- `LESSONS_LEARNED.md` → Qué salió mal, qué salió bien y qué haríamos distinto.
- `CONTRIBUTING.md` → Cómo contribuir al proyecto: ramas, pull requests, convenciones.

> Si entras al proyecto nuevo y quieres entender las reglas del juego, empieza aquí.

---

### `01_src/` — El código fuente

Todo el código que hace funcionar el sistema. Es la carpeta más importante.

```
01_src/
├─ api/          → El backend (API REST con FastAPI)
├─ worker/       → Proceso que ejecuta tareas en segundo plano
├─ worker-xxx/   → Plantilla para crear nuevos workers
├─ front/        → El frontend (Next.js / React)
└─ packages/
   ├─ data/      → Conexión con la base de datos
   ├─ contracts/ → Definición de los datos que se intercambian entre servicios
   ├─ common/    → Utilidades que usan todos los servicios (logs, auth, config...)
   └─ ai/        → Esqueleto del agente de inteligencia artificial (LangGraph)
```

**¿Por qué hay una carpeta `packages`?**
Porque `api`, `worker` y `front` comparten código. En lugar de copiar ese código en cada sitio, se extrae a paquetes reutilizables. Así, si cambias algo en `common`, el cambio llega a todos los servicios automáticamente.

---

### `02_artifacts/` — Artefactos de IA

Lo que le "dices" al modelo de inteligencia artificial: prompts, instrucciones de rol, configuraciones de temperatura y tokens, plantillas de mensajes.

> Importante: aquí va el **contenido** que consume la IA, no el código que la ejecuta. El código está en `01_src/packages/ai/`.

---

### `03_data/` — Datos del proyecto

```
03_data/
├─ evaluation/        → Conjuntos de prueba para medir la calidad del sistema
└─ source_documents/  → Documentos fuente que alimentan el sistema
```

Separar los datos del código evita que el repositorio se llene de ficheros pesados mezclados con el código fuente, y facilita reemplazar los datos por entorno (desarrollo, producción, etc.).

---

### `04_gitops_manifests/` — Infraestructura y despliegue

```
04_gitops_manifests/
├─ iac/        → Código de infraestructura (Terraform, Bicep, ARM...)
└─ pipelines/  → Plantillas de CI/CD reutilizables
```

Aquí se define **dónde y cómo se despliega** el sistema. Es la diferencia entre "qué hace el sistema" (código en `01_src`) y "dónde vive el sistema" (infraestructura aquí).

---

### `05_notebooks/` — Experimentos y análisis

Jupyter Notebooks para explorar datos, probar prompts, evaluar modelos o hacer análisis puntuales. Están separados del código de producción para que no interfieran con los tests ni con los imports del proyecto.

> Piensa en esta carpeta como el "borrador" del equipo de datos e IA.

---

### `06_architecture/` — Decisiones de arquitectura

Diagramas y documentos que explican **por qué el sistema está construido como está**. Incluye diagramas de flujo, diagramas C4 y registros de decisiones arquitectónicas (ADRs).

> Si te preguntas "¿por qué se hizo así?", la respuesta suele estar aquí.

---

### `07_tests/` — Tests globales

Tests que afectan a varios módulos a la vez o que no encajan dentro de un único paquete. Cada paquete también tiene sus propios tests internos, pero los tests que cruzan fronteras viven aquí.

```
07_tests/
└─ unit/
   ├─ api/
   ├─ common/
   └─ worker/
```

---

### `08_monitoring/` — Observabilidad

Configuraciones de logging estructurado, métricas y alertas. Separado del código de negocio para que el equipo de operaciones pueda ajustarlo sin tocar la lógica de la aplicación.

---

### `09_configs/` — Plantillas de configuración

**Solo plantillas, nunca valores reales.**

Contiene ejemplos de las variables de entorno que necesita el proyecto (nombres de variables, sin contraseñas ni claves). Sirve para que un desarrollador nuevo sepa exactamente qué tiene que configurar para arrancar el proyecto.

> Los valores reales van en ficheros `.env` locales que nunca se suben al repositorio.

---

### `10_docs/` — Documentación técnica

```
10_docs/
├─ architecture.md       → Visión general de la arquitectura
├─ base-starter.md       → Guía de inicio del monorepo
├─ coding-guidelines.md  → Convenciones de código
├─ mixins.md             → Cómo usar los mixins de base de datos
├─ examples/
│  └─ item-slice.md      → Ejemplo completo de una funcionalidad de punta a punta
├─ projects/             → Documentación específica por proyecto o iniciativa
└─ tools/                → Guías de herramientas internas
```

La documentación técnica centralizada. Si quieres entender cómo funciona algo concreto del sistema, empieza aquí.

---

## Resumen en una frase por carpeta

| Carpeta | En una frase |
|---|---|
| `00_governance` | Cómo trabajamos como equipo |
| `01_src` | El código que hace funcionar el sistema |
| `02_artifacts` | Lo que le decimos a la IA (prompts, configs) |
| `03_data` | Los datos con los que trabaja el sistema |
| `04_gitops_manifests` | Cómo y dónde se despliega el sistema |
| `05_notebooks` | Experimentos y análisis exploratorio |
| `06_architecture` | Por qué el sistema está construido así |
| `07_tests` | Pruebas automatizadas globales |
| `08_monitoring` | Cómo observamos el sistema en producción |
| `09_configs` | Plantillas de variables de entorno |
| `10_docs` | Documentación técnica del proyecto |
