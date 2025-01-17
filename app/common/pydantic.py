"""Utility functions for pydantic models """
from typing import Type

from pydantic import BaseModel, model_serializer


def filter_fields(cls, data):
    return {field: getattr(data, field) for field in cls.__fields__.keys() if hasattr(data, field)}

class ResponseTemplate(BaseModel):
    status_code: int
    description: str
    model: Type[BaseModel]
    example: BaseModel

    @model_serializer
    def ser_model(self):
        return {
            self.status_code: {
                "model": self.model,
                "description": self.description,
                "content": {
                    "application/json": {
                        "example": self.example.model_dump()
                    }
                }
            }
        }
