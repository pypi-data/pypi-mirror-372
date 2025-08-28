"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import Any, Dict
import sys
import os
outnull_file = open(os.devnull, "w")
errnull_file = open(os.devnull, "w")
STDOUT_FILENO = 1
STDERR_FILENO = 2
class suppress_stdout_stderr(object):
    sys = sys
    os = os
    def __init__(self, disable: bool = True): self.disable = disable
    def __enter__(self):
        if self.disable: return self
        self.old_stdout_fileno_undup = STDOUT_FILENO
        self.old_stderr_fileno_undup = STDERR_FILENO
        self.old_stdout_fileno = self.os.dup(self.old_stdout_fileno_undup)
        self.old_stderr_fileno = self.os.dup(self.old_stderr_fileno_undup)
        self.old_stdout = self.sys.stdout
        self.old_stderr = self.sys.stderr
        self.os.dup2(outnull_file.fileno(), self.old_stdout_fileno_undup)
        self.os.dup2(errnull_file.fileno(), self.old_stderr_fileno_undup)
        self.sys.stdout = outnull_file
        self.sys.stderr = errnull_file
        return self
    def __exit__(self, *_):
        if self.disable: return
        self.sys.stdout = self.old_stdout
        self.sys.stderr = self.old_stderr
        self.os.dup2(self.old_stdout_fileno, self.old_stdout_fileno_undup)
        self.os.dup2(self.old_stderr_fileno, self.old_stderr_fileno_undup)
        self.os.close(self.old_stdout_fileno)
        self.os.close(self.old_stderr_fileno)
class MetaSingleton(type):
    _instances: Dict[type, Any] = {}
    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        if cls not in cls._instances: cls._instances[cls] = super(MetaSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
class Singleton(object, metaclass=MetaSingleton):
    def __init__(self): super(Singleton, self).__init__()
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
