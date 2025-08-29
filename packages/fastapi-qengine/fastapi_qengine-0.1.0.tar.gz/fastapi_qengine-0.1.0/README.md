# fastapi-qengine

[![PyPI version](https://badge.fury.io/py/fastapi-qengine.svg)](https://badge.fury.io/py/fastapi-qengine)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Un motor de consultas avanzado para FastAPI, inspirado en el poderoso sistema de filtros de Loopback 4. Diseñado inicialmente para Beanie/PyMongo, con planes de expansión a otros ORMs en el futuro.

`fastapi-qengine` te permite construir consultas complejas para tus modelos directamente desde la URL con una sintaxis flexible, ofreciendo una alternativa más potente y con menos configuración que `fastapi-filter`.

## Motivación

Mientras que librerías como `fastapi-filter` son excelentes, a menudo requieren una configuración detallada por cada modelo y campo. `fastapi-qengine` trae la flexibilidad del sistema de filtros de Loopback 4 al ecosistema de FastAPI, permitiendo a los clientes construir consultas complejas con operadores lógicos, selección de campos y ordenamiento desde la URL.

Este proyecto se enfoca únicamente en la **creación de la consulta**, delegando la paginación a librerías especializadas como [fastapi-pagination](https://github.com/uriyyo/fastapi-pagination).

## Características

- **Sintaxis de filtro flexible:** Soporte para JSON anidado en los parámetros de la URL y para JSON completo en formato string.
- **Operadores de consulta avanzados:** Soporte para operadores como `$gt`, `$gte`, `$in`, `$nin`, `$lt`, `$lte`, `$ne`, y más.
- **Combinaciones lógicas:** Soporte completo para consultas `$and` y `$or`.
- **Selección de campos (Proyección):** Elige qué campos devolver en los resultados con `fields`.
- **Ordenamiento dinámico:** Ordena los resultados con `order`.
- **Integración mínima:** Diseñado para funcionar con Beanie y FastAPI con una configuración mínima.
- **Enfocado en consultas:** No se encarga de la paginación, permitiendo la integración con librerías dedicadas.

## Instalación

```bash
pip install fastapi-qengine
pip install fastapi-pagination # Recomendado para la paginación
```

## Ejemplo Rápido

### 1. Define tu modelo Beanie

```python
# main.py
from beanie import Document
from pymongo import AsyncMongoClient

class Product(Document):
    name: str
    category: str
    price: float
    in_stock: bool

    class Settings:
        name = "products"

async def init_db():
    client = AsyncMongoClient("mongodb://localhost:27017")
    await Document.init_all(database=client.db_name, documents=[Product])
```

### 2. Crea tu endpoint de FastAPI

```python
# main.py
from fastapi import FastAPI, Depends
from fastapi_pagination import Page, add_pagination
from fastapi_pagination.ext.beanie import apaginate
from contextlib import asynccontextmanager

from fastapi_qengine import create_qe_dependency
from fastapi_qengine.backends.beanie import BeanieQueryEngine

app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)

# Engine explícito por backend
beanie_engine = BeanieQueryEngine(Product)
qe_dep = create_qe_dependency(beanie_engine)

@app.get("/products", response_model=Page[Product])
async def get_products(q = Depends(qe_dep)):
    # q es una tupla (query, projection_model, sort) lista para apaginate
    query, projection_model, sort = q
    return await apaginate(query, projection_model=projection_model, sort=sort)

add_pagination(app)
```

### 3. Realiza consultas desde la URL

`fastapi-qengine` soporta dos formatos para pasar el filtro, dándote flexibilidad según la complejidad de la consulta.

#### Formato 1: Parámetros de URL anidados (Ideal para consultas simples)

Para consultas directas o para usar desde un navegador, puedes usar la sintaxis de corchetes. Es más legible para filtros sencillos.

*   **Buscar productos con un precio mayor a 50:**
    `/products?filter[where][price][$gt]=50`

*   **Buscar productos en stock de la categoría "electronics":**
    `/products?filter[where][category]=electronics&filter[where][in_stock]=true`

*   **Buscar productos y ordenarlos por precio (descendente):**
    `/products?filter[where][in_stock]=true&filter[order]=-price`

#### Formato 2: Stringified JSON (Recomendado para consultas complejas)

Para consultas que involucran operadores lógicos como `$or`, `$and` o estructuras anidadas complejas, el formato de JSON como string es la mejor opción. Recuerda codificar el JSON para la URL.

*   **Buscar productos en la categoría "electronics" O que cuesten menos de 20:**
    *   **JSON Filter:** `{"where": {"$or": [{"category": "electronics"}, {"price": {"$lt": 20}}]}}`
    *   **URL Codificada:** `/products?filter=%7B%22where%22%3A%20%7B%22%24or%22%3A%20%5B%7B%22category%22%3A%20%22electronics%22%7D%2C%20%7B%22price%22%3A%20%7B%22%24lt%22%3A%2020%7D%7D%5D%7D%7D`

## Sintaxis de Filtro Soportada

El objeto `filter` acepta las siguientes claves, inspiradas en la especificación de Loopback.

### `where`

Un objeto que define las condiciones de búsqueda. Utiliza la sintaxis de operadores de PyMongo.

- `{"where": {"category": "books"}}`
- `{"where": {"price": {"$gte": 10, "$lte": 50}}}`
- `{"where": {"category": {"$in": ["electronics", "appliances"]}}}`
- `{"where": {"$and": [{"in_stock": true}, {"price": {"$lt": 100}}]}}`

### `order`

Una cadena de texto para ordenar los resultados. Usa el prefijo `-` para orden descendente.

- `{"order": "price"}` (ascendente)
- `{"order": "-price"}` (descendente)

### `fields`

Un objeto para especificar qué campos incluir (proyección).

- `{"fields": {"name": 1, "price": 1}}` (incluye solo `name` y `price`)

## Comparación con otras librerías

#### vs `fastapi-filter`

`fastapi-filter` es una librería excelente, pero requiere definir clases de filtro para cada modelo. `fastapi-qengine` adopta un enfoque diferente al permitir que el cliente construya la consulta completa en un solo objeto JSON (o vía parámetros anidados), reduciendo la configuración en el backend.

#### vs `fastapi-querybuilder`

`fastapi-qengine` comparte el objetivo de `fastapi-querybuilder` de facilitar la creación de consultas complejas. La principal diferencia es que `fastapi-qengine` está diseñado específicamente para Beanie en su versión inicial y sigue de cerca la especificación de filtros de Loopback 4, una solución probada y robusta en el ecosistema de Node.js.

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue o un pull request para discutir cualquier cambio.

### Desarrollo

Para contribuir al proyecto:

```bash
# Clonar el repositorio
git clone https://github.com/urielcuriel/fastapi-qengine.git
cd fastapi-qengine

# Instalar dependencias de desarrollo
uv pip install -e ".[dev]"

# Ejecutar tests
uv run pytest

# Ejecutar tests con cobertura
uv run pytest --cov=fastapi_qengine --cov-report=html
```

Ver [DEVELOPMENT.md](DEVELOPMENT.md) para más detalles sobre desarrollo y testing.

### Testing

El proyecto utiliza pytest para testing:

- **66 tests** cubriendo toda la funcionalidad
- **78% de cobertura** de código
- Tests unitarios, de integración y end-to-end
- Validación de seguridad y manejo de errores

```bash
# Ejecutar todos los tests
uv run pytest

# Tests específicos
uv run pytest tests/test_basic.py
uv run pytest -k "parser"

# Con cobertura detallada
uv run pytest --cov=fastapi_qengine --cov-report=html
```

## Licencia

Este proyecto está bajo la Licencia MIT.
