from __future__ import annotations
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import argparse
from typing import List, Literal, Union, Any, Type, TypeVar
from pydantic import BaseModel
def _get_base_type(annotation: Type[Any]) -> Type[Any]:
    if getattr(annotation, "__origin__", None) is Literal:
        assert hasattr(annotation, "__args__") and len(annotation.__args__) >= 1
        return type(annotation.__args__[0])
    elif getattr(annotation, "__origin__", None) is Union:
        assert hasattr(annotation, "__args__") and len(annotation.__args__) >= 1
        non_optional_args: List[Type[Any]] = [arg for arg in annotation.__args__ if arg is not type(None)]
        if non_optional_args: return _get_base_type(non_optional_args[0])
    elif (getattr(annotation, "__origin__", None) is list or getattr(annotation, "__origin__", None) is List):
        assert hasattr(annotation, "__args__") and len(annotation.__args__) >= 1
        return _get_base_type(annotation.__args__[0])
    return annotation
def _contains_list_type(annotation: Type[Any] | None) -> bool:
    origin = getattr(annotation, "__origin__", None)
    if origin is list or origin is List: return True
    elif origin in (Literal, Union): return any(_contains_list_type(arg) for arg in annotation.__args__)
    else: return False
def _parse_bool_arg(arg: str | bytes | bool) -> bool:
    if isinstance(arg, bytes): arg = arg.decode("utf-8")
    true_values = {"1", "on", "t", "true", "y", "yes"}
    false_values = {"0", "off", "f", "false", "n", "no"}
    arg_str = str(arg).lower().strip()
    if arg_str in true_values: return True
    elif arg_str in false_values: return False
    else: raise ValueError(f"Invalid boolean argument: {arg}")
def add_args_from_model(parser: argparse.ArgumentParser, model: Type[BaseModel]):
    for name, field in model.model_fields.items():
        description = field.description
        if field.default and description and not field.is_required(): description += f" (default: {field.default})"
        base_type = (_get_base_type(field.annotation) if field.annotation is not None else str)
        list_type = _contains_list_type(field.annotation)
        if base_type is not bool: parser.add_argument(f"--{name}", dest=name, nargs="*" if list_type else None, type=base_type, help=description)
        if base_type is bool: parser.add_argument(f"--{name}", dest=name, type=_parse_bool_arg, help=f"{description}")
T = TypeVar("T", bound=Type[BaseModel])
def parse_model_from_args(model: T, args: argparse.Namespace) -> T: return model(**{k: v for k, v in vars(args).items() if v is not None and k in model.model_fields})
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
