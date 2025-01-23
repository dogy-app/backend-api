import re

from pydantic import BaseModel


# Convert Capital Case to snake_case
def to_snake_case(name: str) -> str:
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()

def flatten_list_to_entries(input_model: BaseModel, mapping: dict, output_model:
                            BaseModel) -> None:
    for key, value in input_model:
        if key in mapping:
            model_class, param_name = mapping[key]
            attr_list = [model_class(**{param_name: val}) for val in value]
            setattr(output_model, key, attr_list)
