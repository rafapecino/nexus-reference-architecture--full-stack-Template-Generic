# AGENTS.md  
### Guía de colaboración para contribuidores humanos y asistentes de IA

Este documento define cómo colaborar correctamente en el repositorio, independientemente de si se usan herramientas de IA, editores inteligentes o trabajo manual.  
Su objetivo es garantizar **coherencia, calidad, trazabilidad y estabilidad arquitectónica** en la solución.

---

# 1. Principios generales

Todas las contribuciones deben respetar estos principios:

1. **Documentación y comentarios en español**, salvo que la librería, API o estándar requiera inglés.  
2. Utiliza descripciones claras en commits, issues y PRs: resume el **qué** y el **por qué**.  
3. Respeta siempre **Clean Architecture**:  
   - separación de capas clara,  
   - reglas de negocio aisladas,  
   - dependencias hacia adentro,  
   - no mezclar infraestructura con dominio.  
4. Mantén siempre que sea posible **soluciones idempotentes**, especialmente en pipelines, workers y pasos de procesamiento.  
5. Sigue un enfoque **type-first**: modelos, esquemas y tipos bien definidos antes de implementar.  
6. Sigue las convenciones de formato del proyecto:  
   - **ruff/black** en Python,  
   - **eslint/prettier** en frontend.  
7. Evita introducir cambios amplios sin justificación técnica sólida.  
8. Antes de finalizar un cambio, **verifica su impacto en la documentación** (docs/\*, requisitos, README, arquitectura, dominio, UX) y actualízala en la misma PR.

---

# 2. Reglas específicas para contribuciones

## 2.1 Documentación

- La documentación debe escribirse en español, salvo ejemplos o referencias externas.  
- Todo nuevo documento o sección debe enlazarse desde el README o el índice correspondiente.  
- Si un cambio modifica comportamiento, contratos o estructuras de datos, la documentación debe actualizarse **en la misma PR**.

---

## 2.2 Estilo de código

### Python

- Utilizar **ruff** y **black** para formateo.  
- Usar **type hints** exhaustivos.  
- No envolver importaciones en `try/except`.  
- Mantener la separación por capas:
  - `routers/`  
  - `schemas/`  
  - `services/`  
  - `repositories/`  
  - `domain/` (si existe)  
  - `workers/` o `steps/`  

### JavaScript / TypeScript

- Usar **eslint** y **prettier**.  
- Preferir **TypeScript** estricto.  
- Evitar `any` salvo casos justificados.  
- No introducir lógica de negocio en componentes de presentación.

---

# 3. Pull Requests

Toda PR debe incluir:

## 3.1 Resumen claro

- Qué se ha cambiado.  
- Por qué era necesario.  
- Qué impacto tiene (dominio, datos, pipeline, UX, API).  

## 3.2 Checklist recomendado

- [ ] Código formateado.  
- [ ] Tests nuevos o actualizados si aplica.  
- [ ] Documentación revisada/actualizada.  
- [ ] No se rompen APIs públicas o se ha versionado adecuadamente.  
- [ ] Se ha comprobado el impacto en pipelines y estructuras de datos.  

## 3.3 Limitaciones

- No introducir paquetes nuevos sin justificarlo claramente.  
- No mezclar en la misma PR:  
  - cambios de infra + cambios de dominio,  
  - cambios funcionales no relacionados.  
- No introducir refactors masivos sin motivo técnico explícito.

---

# 4. Buenas prácticas para colaboradores y asistentes IA

1. Revisa primero la arquitectura y el dominio antes de escribir código nuevo.  
2. No dupliques funciones: busca código existente antes de crear nuevas piezas.  
3. No elimines logs ni campos de trazabilidad sin analizar su impacto.  
4. No modificar configuraciones de seguridad sin consenso del equipo.  
5. No asumir estructuras de datos: revisa siempre los modelos reales.

Si un cambio afecta a:
- la base de datos,  
- blobs JSON,  
- pipelines,  
- contratos API,  

debe explicarse explícitamente en la PR.

---

# 5. Cambios en datos, pipelines y modelos

1. Verificar el esquema actual antes de modificar datos.  
2. Si se añade un nuevo campo:  
   - actualizar modelos y esquemas,  
   - ajustar steps o workers que lo usan,  
   - actualizar documentación,  
   - valorar versionado (`schema_version`).  
3. Mantener la idempotencia de los pasos del pipeline.  
4. Documentar claramente input/output de cada step.

---

# 6. Cambios en frontend

1. Mantener TS estricto y convenciones del proyecto.  
2. Usar componentes reutilizables y desacoplados.  
3. Encapsular accesos a API en módulos de servicios.  
4. No romper contratos backend sin coordinación.  

---

# 7. Cambios en backend y orquestador

1. Mantener modularidad y SRP (Single Responsibility Principle).  
2. Los steps del orquestador deben:  
   - registrar acciones,  
   - manejar errores explícitamente,  
   - evitar efectos secundarios no controlados.  
3. No acoplar dominio con infraestructura.

---

# 8. Uso de IA (genérico)

Estas reglas aplican independientemente de si usas ChatGPT, Claude, Cursor, Copilot, etc.

- La IA debe respetar estrictamente este documento.  
- No generar código sin revisar el contexto real del repo.  
- Si la herramienta no tiene una información, debe pedir aclaración o actuar conservadoramente.  
- Toda contribución generada por IA debe ser revisada por un humano.  

---

# 9. Anti-patrones (prohibido)

- Duplicar lógica existente.  
- Reducir validaciones o seguridad “para simplificar”.  
- Modificar la estructura de blobs sin justificarlo.  
- Crear pasos del pipeline sin documentar su entrada/salida.  
- Mezclar múltiples responsabilidades en un mismo archivo.  
- Introducir dependencias sin motivo.  
- Ocultar errores de importación con `try/except`.  
- Refactors grandes no solicitados.  

---

# 10. Mensaje final

> Este repositorio prioriza la **estabilidad**, la **observabilidad**, la **coherencia arquitectónica** y la **idempotencia**.  
> Toda contribución —humana o asistida por IA— debe mantener estos principios.  
> En caso de duda, pregunta, documenta o propone antes de hacer un cambio arriesgado.

---

# 11. Reglas operativas para agentes (obligatorio)

Esta sección define un flujo mínimo para que asistentes IA no omitan validaciones.

## 11.1 Secuencia obligatoria antes de cerrar un cambio

1. Entender alcance y capas afectadas (dominio, datos, API, worker, frontend).  
2. Implementar el cambio mínimo necesario (sin refactors masivos no solicitados).  
3. Ejecutar validaciones técnicas locales según aplique.  
4. Verificar impacto en contratos, migraciones y documentación.  
5. Reportar resultado final indicando qué se validó y qué quedó pendiente.

## 11.2 Validaciones técnicas mínimas

Para Python, ejecutar como mínimo:

- `ruff check` en los archivos modificados.  
- tests relevantes del área impactada (`pytest` selectivo o completo según alcance).  
- si hubo cambios de modelos SQLAlchemy: revisar autogenerado Alembic y coherencia de `upgrade`/`downgrade`.

Si una validación no puede ejecutarse, se debe informar explícitamente el motivo en la respuesta final.

## 11.3 Reglas específicas de modelos ORM

Aplican a `01_src/packages/data/src/data/models/**`:

- Clases ORM en `PascalCase`.  
- `__tablename__`, atributos y módulos en `snake_case`.  
- `relationship()` apuntando al nombre real de clase (`PascalCase`).  
- `ForeignKey` apuntando a tabla/columna real, no a nombre de clase.  
- Registrar modelos en `data/models/__init__.py`.

## 11.4 Criterios de bloqueo

Un agente no debe dar por finalizado un cambio si ocurre alguno de estos casos:

- errores de lint o tests en el código tocado;  
- migración generada no revisada cuando hubo cambios en modelos;  
- documentación desactualizada ante cambios de comportamiento o contrato;  
- impacto potencial en seguridad sin explicitarlo.

## 11.5 Formato mínimo de cierre en PR/respuesta

Todo cierre debe incluir:

1. Qué se cambió.  
2. Qué se validó (comandos concretos).  
3. Riesgos residuales o pendientes.
