from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class SchemaBase(BaseModel):
    """Atributos em snake_case no Python e em camelCase no JSON, como no contrato.

    Ex.: copias_disponiveis no código sai como "copiasDisponiveis" na API.
    from_attributes permite devolver direto um objeto das tabelas (app/models).
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        validate_by_name=True,
        validate_by_alias=True,
        from_attributes=True,
    )
