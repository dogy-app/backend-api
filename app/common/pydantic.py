"""Utility functions for pydantic models """

def filter_fields(cls, data):
    return {field: getattr(data, field) for field in cls.__fields__.keys() if hasattr(data, field)}
