"""
FastAPI dependency helpers for query engine.

New explicit backend pattern:
- You construct a backend engine (e.g., BeanieQueryEngine(Product)).
- Use create_qe_dependency(engine) to produce a FastAPI dependency that parses,
  validates and compiles request filters into the backend-specific query.
"""

from typing import Any, Dict, Optional, Union

from fastapi import HTTPException, Query, Request

from .core.ast import ASTBuilder
from .core.config import QEngineConfig, default_config
from .core.errors import QEngineError
from .core.normalizer import FilterNormalizer
from .core.optimizer import ASTOptimizer
from .core.parser import FilterParser
from .core.types import FilterAST, SecurityPolicy
from .core.validator import FilterValidator


def _build_pipeline(config: Optional[QEngineConfig] = None, security_policy: Optional[SecurityPolicy] = None):
    """Inicializa y devuelve todos los componentes del pipeline de procesamiento."""
    cfg = config or default_config
    policy = security_policy or cfg.security_policy
    parser = FilterParser(cfg.parser)
    normalizer = FilterNormalizer()
    validator = FilterValidator(cfg.validator, policy)
    ast_builder = ASTBuilder()
    optimizer = ASTOptimizer(cfg.optimizer)
    return cfg, parser, normalizer, validator, ast_builder, optimizer


def process_filter_to_ast(
    filter_input: Union[str, Dict[str, Any]],
    config: Optional[QEngineConfig] = None,
    security_policy: Optional[SecurityPolicy] = None,
) -> FilterAST:
    """Procesa la entrada a través de parse -> normalize -> validate -> build AST -> optimize."""
    _, parser, normalizer, validator, ast_builder, optimizer = _build_pipeline(config, security_policy)

    parsed_input = parser.parse(filter_input)
    normalized_input = normalizer.normalize(parsed_input)
    validator.validate_filter_input(normalized_input)
    ast = ast_builder.build(normalized_input)
    optimized_ast = optimizer.optimize(ast)
    return optimized_ast


def _execute_query_on_engine(engine: Any, ast: FilterAST) -> Any:
    """Ejecuta el AST en el motor de backend proporcionado."""
    if hasattr(engine, "build_query"):
        return engine.build_query(ast)
    if hasattr(engine, "compile"):
        return engine.compile(ast)
    # Este error es para el desarrollador, por lo que un 500 es apropiado.
    raise HTTPException(
        status_code=500, detail="El motor proporcionado no es válido: debe tener un método 'build_query' o 'compile'."
    )


def _get_filter_input_from_request(request: Request, filter_param: Optional[str]) -> Union[str, Dict[str, Any], None]:
    """Extrae la entrada del filtro del parámetro 'filter' o de los query params."""
    if filter_param is not None:
        return filter_param

    # Extrae parámetros que comienzan con "filter[" para filtros anidados.
    query_params = dict(request.query_params)
    filter_params = {k: v for k, v in query_params.items() if k.startswith("filter[")}
    return filter_params if filter_params else None


def _handle_processing_error(e: Exception, debug: bool) -> None:
    """Centraliza el manejo de errores, convirtiendo excepciones en respuestas HTTP."""
    if isinstance(e, QEngineError):
        # Errores de validación o parseo del usuario.
        raise HTTPException(status_code=400, detail=str(e))

    # Errores inesperados del servidor.
    if debug:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {e}")

    raise HTTPException(status_code=400, detail="La especificación del filtro no es válida.")


# --- Función principal simplificada ---


def create_qe_dependency(
    engine: Any,
    *,
    config: Optional[QEngineConfig] = None,
    security_policy: Optional[SecurityPolicy] = None,
):
    """
    Crea una dependencia de FastAPI usando una instancia explícita del motor de backend.

    La dependencia se encarga de:
    1. Extraer los filtros de la petición.
    2. Procesarlos para generar un AST (Abstract Syntax Tree).
    3. Ejecutar el AST en el motor para construir la consulta final.
    4. Manejar los errores de forma centralizada.
    """
    # Se obtiene la configuración una sola vez al crear la dependencia.
    cfg = config or default_config

    def dependency(
        request: Request,
        filter_param: Optional[str] = Query(None, alias="filter", description="Filtro en formato JSON o anidado"),
    ) -> Any:
        try:
            filter_input = _get_filter_input_from_request(request, filter_param)

            if not filter_input:
                # Si no hay filtro, se ejecuta una consulta vacía.
                return _execute_query_on_engine(engine, FilterAST())

            # La lógica de procesamiento se delega a la función existente.
            ast = process_filter_to_ast(filter_input, config=cfg, security_policy=security_policy)

            return _execute_query_on_engine(engine, ast)

        except Exception as e:
            # La lógica de manejo de errores también se delega.
            _handle_processing_error(e, debug=cfg.debug)

    return dependency
