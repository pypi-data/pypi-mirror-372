"""
Beanie/PyMongo backend compiler.
"""

from typing import Any, Dict, Generic, List, Optional, Tuple, TypeVar, Union, get_args, get_origin

from beanie import Document
from beanie.odm.enums import SortDirection
from beanie.odm.queries.aggregation import AggregationQuery
from beanie.odm.queries.find import FindMany, FindQueryProjectionType
from pydantic import BaseModel, ConfigDict, create_model

from ..core.compiler_base import BaseQueryCompiler, QueryAdapter
from ..core.errors import CompilerError
from ..core.types import ASTNode, FieldCondition, FieldsNode, FilterAST, LogicalCondition, OrderNode
from ..operators.comparison import COMPARISON_OPERATORS
from ..operators.logical import LOGICAL_OPERATORS

# Type variable for Document subclasses
TDocument = TypeVar("TDocument", bound=Document)

# Type alias for Beanie query result tuple
BeanieQueryResult = tuple[
    Union[TDocument, FindMany[TDocument], AggregationQuery[TDocument]],
    Optional[type[FindQueryProjectionType]],
    Union[None, str, List[tuple[str, SortDirection]]],
]


# Type variable for Document subclasses
TDocument = TypeVar("TDocument", bound=Document)


class _ProjectionBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, extra="ignore")


class BeanieQueryAdapter(QueryAdapter):
    """Adapter for Beanie/PyMongo query objects."""

    def __init__(self):
        self.query: Dict[str, Any] = {}
        self.sort_spec: List[tuple] = []
        self.projection: Optional[Dict[str, int]] = None

    def add_where_condition(self, condition: Dict[str, Any]) -> "BeanieQueryAdapter":
        """Add a where condition to the query."""
        if not self.query:
            self.query = condition
        else:
            # Merge with existing query using $and
            if "$and" in self.query:
                self.query["$and"].append(condition)
            else:
                self.query = {"$and": [self.query, condition]}
        return self

    def add_sort(self, field: str, ascending: bool = True) -> "BeanieQueryAdapter":
        """Add sorting to the query."""
        direction = 1 if ascending else -1
        self.sort_spec.append((field, direction))
        return self

    def set_projection(self, fields: Dict[str, int]) -> "BeanieQueryAdapter":
        """Set field projection."""
        self.projection = fields
        return self

    def build(self) -> Dict[str, Any]:
        """Build the final query components."""
        result: Dict[str, Any] = {}

        if self.query:
            result["filter"] = self.query

        if self.sort_spec:
            result["sort"] = self.sort_spec

        if self.projection:
            result["projection"] = self.projection

        return result


class BeanieQueryCompiler(BaseQueryCompiler):
    """Query compiler for Beanie/PyMongo backend."""

    def __init__(self):
        super().__init__("beanie")
        self.adapter: Optional[BeanieQueryAdapter] = None

    def create_base_query(self) -> BeanieQueryAdapter:
        """Create the base query adapter for Beanie."""
        self.adapter = BeanieQueryAdapter()
        return self.adapter

    def apply_where(self, query: BeanieQueryAdapter, where_node: ASTNode) -> BeanieQueryAdapter:
        """Apply where conditions to the query."""
        condition = self.compile_condition(where_node)
        return query.add_where_condition(condition)

    def apply_order(self, query: BeanieQueryAdapter, order_nodes: List[OrderNode]) -> BeanieQueryAdapter:
        """Apply ordering to the query."""
        for order_node in order_nodes:
            query.add_sort(order_node.field, order_node.ascending)
        return query

    def apply_fields(self, query: BeanieQueryAdapter, fields_node: FieldsNode) -> BeanieQueryAdapter:
        """Apply field projection to the query."""
        return query.set_projection(fields_node.fields)

    def finalize_query(self, query: BeanieQueryAdapter) -> Dict[str, Any]:
        """Finalize the query and return MongoDB query components."""
        return query.build()

    def compile_field_condition(self, condition: FieldCondition) -> Dict[str, Any]:
        """Compile a field condition to MongoDB format."""
        handler = COMPARISON_OPERATORS.get(condition.operator)
        if not handler:
            raise CompilerError(f"Unsupported operator: {condition.operator}")

        return handler.compile(condition.field, condition.value, self.backend_name)

    def compile_logical_condition(self, condition: LogicalCondition) -> Dict[str, Any]:
        """Compile a logical condition to MongoDB format."""
        handler = LOGICAL_OPERATORS.get(condition.operator)
        if not handler:
            raise CompilerError(f"Unsupported logical operator: {condition.operator}")

        # Compile nested conditions
        compiled_conditions = [self.compile_condition(nested_condition) for nested_condition in condition.conditions]

        return handler.compile(compiled_conditions, self.backend_name)


class BeanieQueryEngine(Generic[TDocument]):
    """High-level query engine for Beanie models."""

    def __init__(self, model_class: type[TDocument]):
        """
        Initialize query engine for a Beanie model.

        Args:
            model_class: Beanie Document class
        """
        self.model_class = model_class
        self.compiler = BeanieQueryCompiler()

    def build_query(self, ast: FilterAST) -> BeanieQueryResult:
        """
        Build a Beanie query from FilterAST.

        Args:
            ast: FilterAST to compile

        Returns:
            Tuple containing:
            - query: Union[TDocument, FindMany[TDocument], AggregationQuery[TDocument]]
            - projection_model: Optional[type[DocumentProjectionType]]
            - sort: Union[None, str, list[tuple[str, SortDirection]]]
        """
        query_components = self.compiler.compile(ast)

        # Start with base find query
        query = self.model_class.find()

        # Apply filter
        if "filter" in query_components:
            query = self.model_class.find(query_components["filter"])

        # Apply sort
        sort_spec = None
        if "sort" in query_components:
            sort_spec = query_components["sort"]
            query = query.sort(sort_spec)

        # Handle projection - DON'T apply to query, return as separate parameter for apaginate
        projection_model = None
        projection_dict = None
        if "projection" in query_components:
            projection_dict = query_components["projection"]
            # Create a dynamic projection model for fastapi-pagination
            projection_model = self._create_projection_model(projection_dict)
            if projection_model:
                query = query.project(projection_model)

        return query, projection_model, sort_spec

    def _create_projection_model(self, projection_dict: Dict[str, int]) -> Optional[type[FindQueryProjectionType]]:
        """
        Crea un modelo Pydantic para usar con .project() en Beanie
        a partir de un dict de proyección con soporte dot-notation.

        Reglas:
          - Si hay al menos un '1' => modo INCLUSIÓN (los '0' se ignoran).
          - Si NO hay '1' => modo EXCLUSIÓN toplevel (incluye todos menos los '0' a primer nivel).
        """
        include_paths = [k for k, v in projection_dict.items() if v == 1]

        if include_paths:
            tree = self._paths_to_tree(include_paths)
        else:
            # Exclusión de primer nivel
            exclude_top = {k.split(".", 1)[0] for k, v in projection_dict.items() if v == 0}
            to_include = [k for k in getattr(self.model_class, "model_fields", {}).keys() if k not in exclude_top]
            if not to_include:
                return None
            tree = self._paths_to_tree(to_include)

        model_name = f"{getattr(self.model_class, '__name__', 'Unknown')}Projection"
        try:
            projection_model = self._build_model_from_tree(self.model_class, tree, model_name)
            return projection_model  # type: ignore[return-value]
        except Exception:
            # Fallback suave: si algo falla, no forzamos proyección
            return None

    @staticmethod
    def _paths_to_tree(paths: List[str]) -> Dict[str, Any]:
        """
        ["a", "b.c", "b.d.e"] ->
        {"a": True, "b": {"c": True, "d": {"e": True}}}
        """
        root: Dict[str, Any] = {}
        for p in paths:
            node = root
            parts = p.split(".")
            for i, part in enumerate(parts):
                last = i == len(parts) - 1
                if last:
                    node[part] = True
                else:
                    node = node.setdefault(part, {})
        return root

    @staticmethod
    def _unwrap_optional_union(tp: Any) -> Any:
        origin = get_origin(tp)
        if origin is Union:
            args = tuple(a for a in get_args(tp) if a is not type(None))  # noqa: E721
            if len(args) == 1:
                return args[0]
        return tp

    @staticmethod
    def _is_pyd_model(tp: Any) -> bool:
        try:
            return issubclass(tp, BaseModel)
        except TypeError:
            return False

    @staticmethod
    def _is_sequence_of_models(tp: Any) -> Tuple[bool, Any | None, Any | None]:
        """
        Detecta list/tuple/set[T] donde T es BaseModel.
        Retorna (True, elem_type, origin) si es colección de modelos.
        """
        origin = get_origin(tp)
        if origin in (list, tuple, set):
            args = get_args(tp)
            if not args:
                return (False, None, None)
            elem = args[0]
            elem = BeanieQueryEngine._unwrap_optional_union(elem)
            if BeanieQueryEngine._is_pyd_model(elem):
                return (True, elem, origin)
        return (False, None, None)

    @staticmethod
    def _optional(tp: Any) -> Any:
        # En Pydantic v2 basta con typing.Optional
        from typing import Optional as _Optional  # local para mypy/linters

        return _Optional[tp]  # type: ignore[valid-type]

    def _build_model_from_tree(
        self,
        model: type[BaseModel],
        tree: Dict[str, Any],
        model_name: str,
    ) -> type[BaseModel]:
        """
        Construye recursivamente un modelo Pydantic v2 con los campos incluidos en 'tree'.
        - Hojas -> Optional[T] = None
        - Nodos con subtree -> requiere submodelo Pydantic o colección de submodelos
        """
        field_defs: Dict[str, tuple[type, object]] = {}

        for name, subtree in tree.items():
            if name not in model.model_fields:
                raise KeyError(f"Campo '{name}' no existe en {model.__name__}")

            f_info = model.model_fields[name]
            f_type = f_info.annotation or Any
            f_type = self._unwrap_optional_union(f_type)

            if subtree is True:
                # Hoja: incluir tipo tal cual (o Any si desconocido), pero Optional
                field_defs[name] = (self._optional(f_type), None)
                continue

            # Nodo anidado
            if self._is_pyd_model(f_type):
                sub_model_name = f"{model_name}_{name.capitalize()}"
                sub_projection = self._build_model_from_tree(f_type, subtree, sub_model_name)
                field_defs[name] = (self._optional(sub_projection), None)
                continue

            is_seq, elem_type, origin = self._is_sequence_of_models(f_type)
            if is_seq and elem_type and origin:
                sub_model_name = f"{model_name}_{name.capitalize()}Item"
                sub_projection = self._build_model_from_tree(elem_type, subtree, sub_model_name)
                projected_coll = origin[sub_projection]  # list[Sub], tuple[Sub], set[Sub]
                field_defs[name] = (self._optional(projected_coll), None)
                continue

            # Si llegamos aquí con subtree != True, el campo no es submodelo ni colección de submodelos.
            # Para colecciones de tipos primitivos o dicts arbitrarios, no se puede seleccionar subcampos,
            # así que pedimos la hoja completa: trata el nodo como hoja.
            field_defs[name] = (self._optional(f_type), None)

        projection = create_model(
            model_name,
            __base__=_ProjectionBase,
            **field_defs,
        )  # type: ignore[return-value]
        return projection

    def execute_query(self, ast: FilterAST):
        """
        Execute query and return results.

        Args:
            ast: FilterAST to execute

        Returns:
            Query results
        """
        query, projection_model, sort_spec = self.build_query(ast)
        return query, projection_model, sort_spec


# Convenience function for creating MongoDB queries directly
def compile_to_mongodb(ast: FilterAST) -> Dict[str, Any]:
    """
    Compile FilterAST directly to MongoDB query components.

    Args:
        ast: FilterAST to compile

    Returns:
        Dict with 'filter', 'sort', and/or 'projection' keys
    """
    compiler = BeanieQueryCompiler()
    return compiler.compile(ast)
