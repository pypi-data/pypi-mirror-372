"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import inspect
import tempfile
import warnings
from collections import OrderedDict, UserDict
from collections.abc import MutableMapping
from contextlib import ExitStack, contextmanager
from dataclasses import fields, is_dataclass
from enum import Enum
from functools import partial, wraps
from typing import Any, ContextManager, Iterable, List, Optional, Tuple, TypedDict
import numpy as np
from packaging import version
from .import_utils import (get_torch_version, is_flax_available, is_mlx_available, is_tf_available, is_torch_available, is_torch_fx_proxy)
class cached_property(property):
    def __get__(self, obj, objtype=None):
        if obj is None: return self
        if self.fget is None: raise AttributeError("unreadable attribute")
        attr = "__cached_" + self.fget.__name__
        cached = getattr(obj, attr, None)
        if cached is None:
            cached = self.fget(obj)
            setattr(obj, attr, cached)
        return cached
def strtobool(val):
    val = val.lower()
    if val in {"y", "yes", "t", "true", "on", "1"}: return 1
    if val in {"n", "no", "f", "false", "off", "0"}: return 0
    raise ValueError(f"invalid truth value {val!r}")
def infer_framework_from_repr(x):
    representation = str(type(x))
    if representation.startswith("<class 'torch."): return "pt"
    elif representation.startswith("<class 'tensorflow."): return "tf"
    elif representation.startswith("<class 'jax"): return "jax"
    elif representation.startswith("<class 'numpy."): return "np"
    elif representation.startswith("<class 'mlx."): return "mlx"
def _get_frameworks_and_test_func(x):
    framework_to_test = {"pt": is_torch_tensor, "tf": is_tf_tensor, "jax": is_jax_tensor, "np": is_numpy_array, "mlx": is_mlx_array}
    preferred_framework = infer_framework_from_repr(x)
    frameworks = [] if preferred_framework is None else [preferred_framework]
    if preferred_framework != "np": frameworks.append("np")
    frameworks.extend([f for f in framework_to_test if f not in [preferred_framework, "np"]])
    return {f: framework_to_test[f] for f in frameworks}
def is_tensor(x):
    framework_to_test_func = _get_frameworks_and_test_func(x)
    for test_func in framework_to_test_func.values():
        if test_func(x): return True
    if is_torch_fx_proxy(x): return True
    if is_flax_available():
        from jax.core import Tracer
        if isinstance(x, Tracer): return True
    return False
def _is_numpy(x): return isinstance(x, np.ndarray)
def is_numpy_array(x): return _is_numpy(x)
def _is_torch(x):
    import torch
    return isinstance(x, torch.Tensor)
def is_torch_tensor(x): return False if not is_torch_available() else _is_torch(x)
def _is_torch_device(x):
    import torch
    return isinstance(x, torch.device)
def is_torch_device(x): return False if not is_torch_available() else _is_torch_device(x)
def _is_torch_dtype(x):
    import torch
    if isinstance(x, str):
        if hasattr(torch, x): x = getattr(torch, x)
        else: return False
    return isinstance(x, torch.dtype)
def is_torch_dtype(x): return False if not is_torch_available() else _is_torch_dtype(x)
def _is_tensorflow(x):
    import tensorflow as tf
    return isinstance(x, tf.Tensor)
def is_tf_tensor(x): return False if not is_tf_available() else _is_tensorflow(x)
def _is_tf_symbolic_tensor(x):
    import tensorflow as tf
    if hasattr(tf, "is_symbolic_tensor"): return tf.is_symbolic_tensor(x)
    return isinstance(x, tf.Tensor)
def is_tf_symbolic_tensor(x): return False if not is_tf_available() else _is_tf_symbolic_tensor(x)
def _is_jax(x):
    import jax.numpy as jnp
    return isinstance(x, jnp.ndarray)
def is_jax_tensor(x): return False if not is_flax_available() else _is_jax(x)
def _is_mlx(x):
    import mlx.core as mx
    return isinstance(x, mx.array)
def is_mlx_array(x): return False if not is_mlx_available() else _is_mlx(x)
def to_py_obj(obj):
    framework_to_py_obj = {"pt": lambda obj: obj.detach().cpu().tolist(), "tf": lambda obj: obj.numpy().tolist(), "jax": lambda obj: np.asarray(obj).tolist(), "np": lambda obj: obj.tolist()}
    if isinstance(obj, (dict, UserDict)): return {k: to_py_obj(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)): return [to_py_obj(o) for o in obj]
    framework_to_test_func = _get_frameworks_and_test_func(obj)
    for framework, test_func in framework_to_test_func.items():
        if test_func(obj): return framework_to_py_obj[framework](obj)
    if isinstance(obj, np.number): return obj.tolist()
    else: return obj
def to_numpy(obj):
    framework_to_numpy = {"pt": lambda obj: obj.detach().cpu().numpy(), "tf": lambda obj: obj.numpy(), "jax": lambda obj: np.asarray(obj), "np": lambda obj: obj}
    if isinstance(obj, (dict, UserDict)): return {k: to_numpy(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)): return np.array(obj)
    framework_to_test_func = _get_frameworks_and_test_func(obj)
    for framework, test_func in framework_to_test_func.items():
        if test_func(obj): return framework_to_numpy[framework](obj)
    return obj
class ModelOutput(OrderedDict):
    def __init_subclass__(cls) -> None:
        if is_torch_available():
            if version.parse(get_torch_version()) >= version.parse("2.2"): _torch_pytree.register_pytree_node(cls, _model_output_flatten, partial(_model_output_unflatten, output_type=cls), serialized_type_name=f"{cls.__module__}.{cls.__name__}")
            else: _torch_pytree._register_pytree_node(cls, _model_output_flatten, partial(_model_output_unflatten, output_type=cls))
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        is_modeloutput_subclass = self.__class__ != ModelOutput
        if is_modeloutput_subclass and not is_dataclass(self): raise TypeError(f"{self.__module__}.{self.__class__.__name__} is not a dataclasss. This is a subclass of ModelOutput and so must use the @dataclass decorator.")
    def __post_init__(self):
        class_fields = fields(self)
        if not len(class_fields): raise ValueError(f"{self.__class__.__name__} has no fields.")
        if not all(field.default is None for field in class_fields[1:]): raise ValueError(f"{self.__class__.__name__} should not have more than one required field.")
        first_field = getattr(self, class_fields[0].name)
        other_fields_are_none = all(getattr(self, field.name) is None for field in class_fields[1:])
        if other_fields_are_none and not is_tensor(first_field):
            if isinstance(first_field, dict):
                iterator = first_field.items()
                first_field_iterator = True
            else:
                try:
                    iterator = iter(first_field)
                    first_field_iterator = True
                except TypeError: first_field_iterator = False
            if first_field_iterator:
                for idx, element in enumerate(iterator):
                    if (not isinstance(element, (list, tuple)) or not len(element) == 2 or not isinstance(element[0], str)):
                        if idx == 0: self[class_fields[0].name] = first_field
                        else: raise ValueError(f"Cannot set key/value for {element}. It needs to be a tuple (key, value).")
                        break
                    setattr(self, element[0], element[1])
                    if element[1] is not None: self[element[0]] = element[1]
            elif first_field is not None: self[class_fields[0].name] = first_field
        else:
            for field in class_fields:
                v = getattr(self, field.name)
                if v is not None: self[field.name] = v
    def __delitem__(self, *args, **kwargs): raise Exception(f"You cannot use ``__delitem__`` on a {self.__class__.__name__} instance.")
    def setdefault(self, *args, **kwargs): raise Exception(f"You cannot use ``setdefault`` on a {self.__class__.__name__} instance.")
    def pop(self, *args, **kwargs): raise Exception(f"You cannot use ``pop`` on a {self.__class__.__name__} instance.")
    def update(self, *args, **kwargs): raise Exception(f"You cannot use ``update`` on a {self.__class__.__name__} instance.")
    def __getitem__(self, k):
        if isinstance(k, str):
            inner_dict = dict(self.items())
            return inner_dict[k]
        else: return self.to_tuple()[k]
    def __setattr__(self, name, value):
        if name in self.keys() and value is not None: super().__setitem__(name, value)
        super().__setattr__(name, value)
    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        super().__setattr__(key, value)
    def __reduce__(self):
        if not is_dataclass(self): return super().__reduce__()
        callable, _args, *remaining = super().__reduce__()
        args = tuple(getattr(self, field.name) for field in fields(self))
        return callable, args, *remaining
    def to_tuple(self) -> Tuple[Any]: return tuple(self[k] for k in self.keys())
if is_torch_available():
    import torch.utils._pytree as _torch_pytree
    def _model_output_flatten(output: ModelOutput) -> Tuple[List[Any], "_torch_pytree.Context"]: return list(output.values()), list(output.keys())
    def _model_output_unflatten(values: Iterable[Any], context: "_torch_pytree.Context", output_type=None) -> ModelOutput: return output_type(**dict(zip(context, values)))
    if version.parse(get_torch_version()) >= version.parse("2.2"): _torch_pytree.register_pytree_node(ModelOutput, _model_output_flatten, partial(_model_output_unflatten, output_type=ModelOutput), serialized_type_name=f"{ModelOutput.__module__}.{ModelOutput.__name__}")
    else: _torch_pytree._register_pytree_node(ModelOutput, _model_output_flatten, partial(_model_output_unflatten, output_type=ModelOutput))
class ExplicitEnum(str, Enum):
    @classmethod
    def _missing_(cls, value): raise ValueError(f"{value} is not a valid {cls.__name__}, please select one of {list(cls._value2member_map_.keys())}")
class PaddingStrategy(ExplicitEnum):
    LONGEST = "longest"
    MAX_LENGTH = "max_length"
    DO_NOT_PAD = "do_not_pad"
class TensorType(ExplicitEnum):
    PYTORCH = "pt"
    TENSORFLOW = "tf"
    NUMPY = "np"
    JAX = "jax"
    MLX = "mlx"
class ContextManagers:
    def __init__(self, context_managers: List[ContextManager]):
        self.context_managers = context_managers
        self.stack = ExitStack()
    def __enter__(self):
        for context_manager in self.context_managers: self.stack.enter_context(context_manager)
    def __exit__(self, *args, **kwargs): self.stack.__exit__(*args, **kwargs)
def can_return_loss(model_class):
    framework = infer_framework(model_class)
    if framework == "tf": signature = inspect.signature(model_class.call)
    elif framework == "pt": signature = inspect.signature(model_class.forward)
    else: signature = inspect.signature(model_class.__call__)
    for p in signature.parameters:
        if p == "return_loss" and signature.parameters[p].default is True: return True
    return False
def find_labels(model_class):
    model_name = model_class.__name__
    framework = infer_framework(model_class)
    if framework == "tf": signature = inspect.signature(model_class.call)
    elif framework == "pt": signature = inspect.signature(model_class.forward)
    else: signature = inspect.signature(model_class.__call__)
    if "QuestionAnswering" in model_name: return [p for p in signature.parameters if "label" in p or p in ("start_positions", "end_positions")]
    else: return [p for p in signature.parameters if "label" in p]
def flatten_dict(d: MutableMapping, parent_key: str = "", delimiter: str = "."):
    def _flatten_dict(d, parent_key="", delimiter="."):
        for k, v in d.items():
            key = str(parent_key) + delimiter + str(k) if parent_key else k
            if v and isinstance(v, MutableMapping): yield from flatten_dict(v, key, delimiter=delimiter).items()
            else: yield key, v
    return dict(_flatten_dict(d, parent_key, delimiter))
@contextmanager
def working_or_temp_dir(working_dir, use_temp_dir: bool = False):
    if use_temp_dir:
        with tempfile.TemporaryDirectory() as tmp_dir: yield tmp_dir
    else: yield working_dir
def transpose(array, axes=None):
    if is_numpy_array(array): return np.transpose(array, axes=axes)
    elif is_torch_tensor(array): return array.T if axes is None else array.permute(*axes)
    elif is_tf_tensor(array):
        import tensorflow as tf
        return tf.transpose(array, perm=axes)
    elif is_jax_tensor(array):
        import jax.numpy as jnp
        return jnp.transpose(array, axes=axes)
    else: raise ValueError(f"Type not supported for transpose: {type(array)}.")
def reshape(array, newshape):
    if is_numpy_array(array): return np.reshape(array, newshape)
    elif is_torch_tensor(array): return array.reshape(*newshape)
    elif is_tf_tensor(array):
        import tensorflow as tf
        return tf.reshape(array, newshape)
    elif is_jax_tensor(array):
        import jax.numpy as jnp
        return jnp.reshape(array, newshape)
    else: raise ValueError(f"Type not supported for reshape: {type(array)}.")
def squeeze(array, axis=None):
    if is_numpy_array(array): return np.squeeze(array, axis=axis)
    elif is_torch_tensor(array): return array.squeeze() if axis is None else array.squeeze(dim=axis)
    elif is_tf_tensor(array):
        import tensorflow as tf
        return tf.squeeze(array, axis=axis)
    elif is_jax_tensor(array):
        import jax.numpy as jnp
        return jnp.squeeze(array, axis=axis)
    else: raise ValueError(f"Type not supported for squeeze: {type(array)}.")
def expand_dims(array, axis):
    if is_numpy_array(array): return np.expand_dims(array, axis)
    elif is_torch_tensor(array): return array.unsqueeze(dim=axis)
    elif is_tf_tensor(array):
        import tensorflow as tf
        return tf.expand_dims(array, axis=axis)
    elif is_jax_tensor(array):
        import jax.numpy as jnp
        return jnp.expand_dims(array, axis=axis)
    else: raise ValueError(f"Type not supported for expand_dims: {type(array)}.")
def tensor_size(array):
    if is_numpy_array(array): return np.size(array)
    elif is_torch_tensor(array): return array.numel()
    elif is_tf_tensor(array):
        import tensorflow as tf
        return tf.size(array)
    elif is_jax_tensor(array): return array.size
    else: raise ValueError(f"Type not supported for tensor_size: {type(array)}.")
def add_model_info_to_auto_map(auto_map, repo_id):
    for key, value in auto_map.items():
        if isinstance(value, (tuple, list)): auto_map[key] = [f"{repo_id}--{v}" if (v is not None and "--" not in v) else v for v in value]
        elif value is not None and "--" not in value: auto_map[key] = f"{repo_id}--{value}"
    return auto_map
def add_model_info_to_custom_pipelines(custom_pipeline, repo_id):
    for task in custom_pipeline.keys():
        if "impl" in custom_pipeline[task]:
            module = custom_pipeline[task]["impl"]
            if "--" not in module: custom_pipeline[task]["impl"] = f"{repo_id}--{module}"
    return custom_pipeline
def infer_framework(model_class):
    for base_class in inspect.getmro(model_class):
        module = base_class.__module__
        name = base_class.__name__
        if module.startswith("tensorflow") or module.startswith("keras") or name == "TFPreTrainedModel": return "tf"
        elif module.startswith("torch") or name == "PreTrainedModel": return "pt"
        elif module.startswith("flax") or module.startswith("jax") or name == "FlaxPreTrainedModel": return "flax"
    else: raise TypeError(f"Could not infer framework from class {model_class}.")
def torch_int(x):
    if not is_torch_available(): return int(x)
    import torch
    return x.to(torch.int64) if torch.jit.is_tracing() and isinstance(x, torch.Tensor) else int(x)
def torch_float(x):
    if not is_torch_available(): return int(x)
    import torch
    return x.to(torch.float32) if torch.jit.is_tracing() and isinstance(x, torch.Tensor) else int(x)
def filter_out_non_signature_kwargs(extra: Optional[list] = None):
    extra = extra or []
    extra_params_to_pass = set(extra)
    def decorator(func):
        sig = inspect.signature(func)
        function_named_args = set(sig.parameters.keys())
        valid_kwargs_to_pass = function_named_args.union(extra_params_to_pass)
        is_instance_method = "self" in function_named_args
        is_class_method = "cls" in function_named_args
        func._filter_out_non_signature_kwargs = True
        @wraps(func)
        def wrapper(*args, **kwargs):
            valid_kwargs = {}
            invalid_kwargs = {}
            for k, v in kwargs.items():
                if k in valid_kwargs_to_pass: valid_kwargs[k] = v
                else: invalid_kwargs[k] = v
            if invalid_kwargs:
                invalid_kwargs_names = [f"'{k}'" for k in invalid_kwargs.keys()]
                invalid_kwargs_names = ", ".join(invalid_kwargs_names)
                if is_instance_method: cls_prefix = args[0].__class__.__name__ + "."
                elif is_class_method: cls_prefix = args[0].__name__ + "."
                else: cls_prefix = ""
                warnings.warn(f"The following named arguments are not valid for `{cls_prefix}{func.__name__}` and were ignored: {invalid_kwargs_names}", UserWarning, stacklevel=2)
            return func(*args, **valid_kwargs)
        return wrapper
    return decorator
class LossKwargs(TypedDict, total=False):
    num_items_in_batch: Optional[int]
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
