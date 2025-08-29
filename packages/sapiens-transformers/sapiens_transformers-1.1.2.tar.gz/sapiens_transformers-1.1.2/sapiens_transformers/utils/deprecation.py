"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import inspect
import warnings
from functools import wraps
from typing import Optional
import packaging.version
from .. import __version__
from . import ExplicitEnum
class Action(ExplicitEnum):
    NONE = "none"
    NOTIFY = "notify"
    NOTIFY_ALWAYS = "notify_always"
    RAISE = "raise"
def deprecate_kwarg(old_name: str, version: str, new_name: Optional[str] = None, warn_if_greater_or_equal_version: bool = False, raise_if_greater_or_equal_version: bool = False, raise_if_both_names: bool = False, additional_message: Optional[str] = None):
    deprecated_version = packaging.version.parse(version)
    current_version = packaging.version.parse(__version__)
    is_greater_or_equal_version = current_version >= deprecated_version
    if is_greater_or_equal_version: version_message = f"and removed starting from version {version}"
    else: version_message = f"and will be removed in version {version}"
    def wrapper(func):
        sig = inspect.signature(func)
        function_named_args = set(sig.parameters.keys())
        is_instance_method = "self" in function_named_args
        is_class_method = "cls" in function_named_args
        @wraps(func)
        def wrapped_func(*args, **kwargs):
            func_name = func.__name__
            if is_instance_method: func_name = f"{args[0].__class__.__name__}.{func_name}"
            elif is_class_method: func_name = f"{args[0].__name__}.{func_name}"
            minimum_action = Action.NONE
            message = None
            if old_name in kwargs and new_name in kwargs:
                minimum_action = Action.RAISE if raise_if_both_names else Action.NOTIFY_ALWAYS
                message = f"Both `{old_name}` and `{new_name}` are set for `{func_name}`. Using `{new_name}={kwargs[new_name]}` and ignoring deprecated `{old_name}={kwargs[old_name]}`."
                kwargs.pop(old_name)
            elif old_name in kwargs and new_name is not None and new_name not in kwargs:
                minimum_action = Action.NOTIFY
                message = f"`{old_name}` is deprecated {version_message} for `{func_name}`. Use `{new_name}` instead."
                kwargs[new_name] = kwargs.pop(old_name)
            elif old_name in kwargs:
                minimum_action = Action.NOTIFY
                message = f"`{old_name}` is deprecated {version_message} for `{func_name}`."
            if message is not None and additional_message is not None: message = f"{message} {additional_message}"
            if is_greater_or_equal_version:
                if raise_if_greater_or_equal_version and minimum_action != Action.NONE: minimum_action = Action.RAISE
                elif not warn_if_greater_or_equal_version and minimum_action == Action.NOTIFY: minimum_action = Action.NONE
            if minimum_action == Action.RAISE: raise ValueError(message)
            elif minimum_action in (Action.NOTIFY, Action.NOTIFY_ALWAYS): warnings.warn(message, FutureWarning, stacklevel=2)
            return func(*args, **kwargs)
        return wrapped_func
    return wrapper
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
