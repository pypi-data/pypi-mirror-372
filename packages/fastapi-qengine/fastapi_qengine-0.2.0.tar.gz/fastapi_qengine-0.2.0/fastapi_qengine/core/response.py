from typing import Optional, Type

from pydantic import BaseModel, create_model


def create_response_model(model: Type[BaseModel]) -> Type[BaseModel]:
    """
    Creates a new Pydantic model with all fields from the original model
    made optional.

    This is for projection compatibility.
    """
    optional_fields = {name: (Optional[field.annotation], None) for name, field in model.model_fields.items()}
    optional_model_name = f"Optional{model.__name__}"

    # Se crea un modelo completamente nuevo que no hereda del base
    # para evitar conflictos de validadores o configuraciones.
    return create_model(optional_model_name, **optional_fields)  # type: ignore
