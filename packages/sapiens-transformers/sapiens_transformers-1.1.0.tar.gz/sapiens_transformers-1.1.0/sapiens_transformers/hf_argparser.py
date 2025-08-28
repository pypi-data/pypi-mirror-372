"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import Any, Callable, Dict, Iterable, List, Literal, NewType, Optional, Tuple, Union, get_type_hints
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser, ArgumentTypeError
from inspect import isclass
from pathlib import Path
from copy import copy
from enum import Enum
import dataclasses
import types
import json
import yaml
import sys
import os
DataClass = NewType("DataClass", Any)
DataClassType = NewType("DataClassType", Any)
def string_to_bool(v):
    if isinstance(v, bool): return v
    if v.lower() in ("yes", "true", "t", "y", "1"): return True
    elif v.lower() in ("no", "false", "f", "n", "0"): return False
    else: raise ArgumentTypeError(f"Truthy value expected: got {v} but expected one of yes/no, true/false, t/f, y/n, 1/0 (case insensitive).")
def make_choice_type_function(choices: list) -> Callable[[str], Any]:
    str_to_choice = {str(choice): choice for choice in choices}
    return lambda arg: str_to_choice.get(arg, arg)
def HfArg(*, aliases: Union[str, List[str]] = None, help: str = None, default: Any = dataclasses.MISSING, default_factory: Callable[[], Any] = dataclasses.MISSING, metadata: dict = None, **kwargs) -> dataclasses.Field:
    if metadata is None: metadata = {}
    if aliases is not None: metadata["aliases"] = aliases
    if help is not None: metadata["help"] = help
    return dataclasses.field(metadata=metadata, default=default, default_factory=default_factory, **kwargs)
class HfArgumentParser(ArgumentParser):
    dataclass_types: Iterable[DataClassType]
    def __init__(self, dataclass_types: Union[DataClassType, Iterable[DataClassType]], **kwargs):
        if "formatter_class" not in kwargs: kwargs["formatter_class"] = ArgumentDefaultsHelpFormatter
        super().__init__(**kwargs)
        if dataclasses.is_dataclass(dataclass_types): dataclass_types = [dataclass_types]
        self.dataclass_types = list(dataclass_types)
        for dtype in self.dataclass_types: self._add_dataclass_arguments(dtype)
    @staticmethod
    def _parse_dataclass_field(parser: ArgumentParser, field: dataclasses.Field):
        field_name = f"--{field.name}"
        kwargs = field.metadata.copy()
        if isinstance(field.type, str): raise RuntimeError("Unresolved type detected, which should have been done with the help of `typing.get_type_hints` method by default")
        aliases = kwargs.pop("aliases", [])
        if isinstance(aliases, str): aliases = [aliases]
        origin_type = getattr(field.type, "__origin__", field.type)
        if origin_type is Union or (hasattr(types, "UnionType") and isinstance(origin_type, types.UnionType)):
            if str not in field.type.__args__ and (len(field.type.__args__) != 2 or type(None) not in field.type.__args__): raise ValueError(f"Only `Union[X, NoneType]` (i.e., `Optional[X]`) is allowed for `Union` because the argument parser only supports one type per argument. Problem encountered in field '{field.name}'.")
            if type(None) not in field.type.__args__:
                field.type = field.type.__args__[0] if field.type.__args__[1] is str else field.type.__args__[1]
                origin_type = getattr(field.type, "__origin__", field.type)
            elif bool not in field.type.__args__:
                field.type = (field.type.__args__[0] if isinstance(None, field.type.__args__[1]) else field.type.__args__[1])
                origin_type = getattr(field.type, "__origin__", field.type)
        bool_kwargs = {}
        if origin_type is Literal or (isinstance(field.type, type) and issubclass(field.type, Enum)):
            if origin_type is Literal: kwargs["choices"] = field.type.__args__
            else: kwargs["choices"] = [x.value for x in field.type]
            kwargs["type"] = make_choice_type_function(kwargs["choices"])
            if field.default is not dataclasses.MISSING: kwargs["default"] = field.default
            else: kwargs["required"] = True
        elif field.type is bool or field.type == Optional[bool]:
            bool_kwargs = copy(kwargs)
            kwargs["type"] = string_to_bool
            if field.type is bool or (field.default is not None and field.default is not dataclasses.MISSING):
                default = False if field.default is dataclasses.MISSING else field.default
                kwargs["default"] = default
                kwargs["nargs"] = "?"
                kwargs["const"] = True
        elif isclass(origin_type) and issubclass(origin_type, list):
            kwargs["type"] = field.type.__args__[0]
            kwargs["nargs"] = "+"
            if field.default_factory is not dataclasses.MISSING: kwargs["default"] = field.default_factory()
            elif field.default is dataclasses.MISSING: kwargs["required"] = True
        else:
            kwargs["type"] = field.type
            if field.default is not dataclasses.MISSING: kwargs["default"] = field.default
            elif field.default_factory is not dataclasses.MISSING: kwargs["default"] = field.default_factory()
            else: kwargs["required"] = True
        parser.add_argument(field_name, *aliases, **kwargs)
        if field.default is True and (field.type is bool or field.type == Optional[bool]):
            bool_kwargs["default"] = False
            parser.add_argument(f"--no_{field.name}", action="store_false", dest=field.name, **bool_kwargs)
    def _add_dataclass_arguments(self, dtype: DataClassType):
        if hasattr(dtype, "_argument_group_name"): parser = self.add_argument_group(dtype._argument_group_name)
        else: parser = self
        try: type_hints: Dict[str, type] = get_type_hints(dtype)
        except NameError: raise RuntimeError(f"Type resolution failed for {dtype}. Try declaring the class in global scope or removing line of `from __future__ import annotations` which opts in Postponed Evaluation of Annotations (PEP 563)")
        except TypeError as ex:
            if sys.version_info[:2] < (3, 10) and "unsupported operand type(s) for |" in str(ex):
                python_version = ".".join(map(str, sys.version_info[:3]))
                raise RuntimeError(f"Type resolution failed for {dtype} on Python {python_version}. Try removing line of `from __future__ import annotations` which opts in union types as `X | Y` (PEP 604) via Postponed Evaluation of Annotations (PEP 563). To support Python versions that lower than 3.10, you need to use `typing.Union[X, Y]` instead of `X | Y` and `typing.Optional[X]` instead of `X | None`.") from ex
            raise
        for field in dataclasses.fields(dtype):
            if not field.init: continue
            field.type = type_hints[field.name]
            self._parse_dataclass_field(parser, field)
    def parse_args_into_dataclasses(self, args=None, return_remaining_strings=False, look_for_args_file=True, args_filename=None, args_file_flag=None) -> Tuple[DataClass, ...]:
        if args_file_flag or args_filename or (look_for_args_file and len(sys.argv)):
            args_files = []
            if args_filename: args_files.append(Path(args_filename))
            elif look_for_args_file and len(sys.argv): args_files.append(Path(sys.argv[0]).with_suffix(".args"))
            if args_file_flag:
                args_file_parser = ArgumentParser()
                args_file_parser.add_argument(args_file_flag, type=str, action="append")
                cfg, args = args_file_parser.parse_known_args(args=args)
                cmd_args_file_paths = vars(cfg).get(args_file_flag.lstrip("-"), None)
                if cmd_args_file_paths: args_files.extend([Path(p) for p in cmd_args_file_paths])
            file_args = []
            for args_file in args_files:
                if args_file.exists(): file_args += args_file.read_text().split()
            args = file_args + args if args is not None else file_args + sys.argv[1:]
        namespace, remaining_args = self.parse_known_args(args=args)
        outputs = []
        for dtype in self.dataclass_types:
            keys = {f.name for f in dataclasses.fields(dtype) if f.init}
            inputs = {k: v for k, v in vars(namespace).items() if k in keys}
            for k in keys: delattr(namespace, k)
            obj = dtype(**inputs)
            outputs.append(obj)
        if len(namespace.__dict__) > 0: outputs.append(namespace)
        if return_remaining_strings: return (*outputs, remaining_args)
        else:
            if remaining_args: raise ValueError(f"Some specified arguments are not used by the HfArgumentParser: {remaining_args}")
            return (*outputs,)
    def parse_dict(self, args: Dict[str, Any], allow_extra_keys: bool = False) -> Tuple[DataClass, ...]:
        unused_keys = set(args.keys())
        outputs = []
        for dtype in self.dataclass_types:
            keys = {f.name for f in dataclasses.fields(dtype) if f.init}
            inputs = {k: v for k, v in args.items() if k in keys}
            unused_keys.difference_update(inputs.keys())
            obj = dtype(**inputs)
            outputs.append(obj)
        if not allow_extra_keys and unused_keys: raise ValueError(f"Some keys are not used by the HfArgumentParser: {sorted(unused_keys)}")
        return tuple(outputs)
    def parse_json_file(self, json_file: Union[str, os.PathLike], allow_extra_keys: bool = False) -> Tuple[DataClass, ...]:
        with open(Path(json_file), encoding="utf-8") as open_json_file: data = json.loads(open_json_file.read())
        outputs = self.parse_dict(data, allow_extra_keys=allow_extra_keys)
        return tuple(outputs)
    def parse_yaml_file(self, yaml_file: Union[str, os.PathLike], allow_extra_keys: bool = False) -> Tuple[DataClass, ...]:
        outputs = self.parse_dict(yaml.safe_load(Path(yaml_file).read_text()), allow_extra_keys=allow_extra_keys)
        return tuple(outputs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
