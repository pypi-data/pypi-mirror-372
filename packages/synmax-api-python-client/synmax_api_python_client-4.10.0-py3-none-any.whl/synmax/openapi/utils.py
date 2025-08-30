import inspect
from pydantic import BaseModel, create_model, Extra
from typing import Any, Dict, Optional, Type, Union, Literal
from datetime import date


def change_signature(func, signature: inspect.Signature):
    """
    Wraps a func in a new one with a different signature

    :param func: function to wrap
    :param signature: signature to assign
    """
    def wrapped(*args, **kwargs):
        bound_arguments = inspect.signature(func).bind(*args, **kwargs)
        bound_arguments.apply_defaults()
        return func(*bound_arguments.args, **bound_arguments.kwargs)
    sig = inspect.signature(func)
    new_params = [
            inspect.Parameter(
                name,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                annotation=signature.get(name)
                )
            for name in signature
            ]
    new_signature = sig.replace(parameters=new_params)
    wrapped.__signature__ = new_signature
    return wrapped


def get_annotation(models: list[BaseModel]) -> str:
    params = []
    for model in models:
        if model is None:
            continue
        fields = model.model_fields
        for fname, field in fields.items():

            annotation = repr(field.annotation)
            if hasattr(field.annotation, "__name__"):
                annotation = field.annotation.__name__
            if hasattr(field.annotation, "__origin__"):
                annotation = str(field.annotation).replace("typing.","")
            default = " = ..." if field.is_required() is False else ""
            params.append(f"{fname}: {annotation}{default}")
    return ",".join(["self"] + params)


def get_param_model(parameters: list, operation_id: str) -> Optional[Type[BaseModel]]:
    param_fields = {}
    for param in parameters:
        name = param["name"]
        schema = param.get("schema", {"type": "string"})
        required = param.get("required", False)
        param_fields[name] = (map_openapi_type(schema, name), ... if required else None)
    return create_model(f"{operation_id}Params", **param_fields) if param_fields else None


def get_body_model(request_body: dict, operation_id: str) -> Optional[Type[BaseModel]]:
    body_fields = {}
    body_extra = Extra.allow
    if request_body:
        content = request_body.get("content", {}).get("application/json", {})
        schema = content.get("schema", {"type": "object", "properties": {}})
        required_fields = schema.get("required", [])
        for key, value in schema.get("properties", {}).items():
            is_required = key in required_fields
            body_fields[key] = (map_openapi_type(value, key), ... if is_required else None)
        if schema.get("additionalProperties") is False:
            body_extra = Extra.forbid
    return create_model(f"{operation_id}Body", **body_fields, __config__=type("Config", (), {"extra": body_extra})) if body_fields else None


def map_openapi_type(schema: Dict[str, Any], name: str) -> Type:
    type_map = {
        "string": str,
        "integer": int,
        "boolean": bool,
        "number": float,
        "array": list,
        "object": dict
    }

    if "enum" in schema:
        return Literal[tuple(schema["enum"])]

    if "anyOf" in schema:
        types = [map_openapi_type(sub_schema, name) for sub_schema in schema["anyOf"]]
        return Union[tuple(types)]

    if schema.get("type") == "array":
        items_schema = schema.get("items", {})
        item_type = map_openapi_type(items_schema, name)
        return list[item_type]

    if schema.get("type") == "string" and schema.get("format") == "date":
        return date

    return type_map.get(schema.get("type"), Any)

