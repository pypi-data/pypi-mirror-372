"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from .utils import ExplicitEnum, is_torch_available, logging
import collections
if is_torch_available(): import torch
logger = logging.get_logger(__name__)
class DebugUnderflowOverflow:
    def __init__(self, model, max_frames_to_save=21, trace_batch_nums=[], abort_after_batch_num=None):
        self.model = model
        self.trace_batch_nums = trace_batch_nums
        self.abort_after_batch_num = abort_after_batch_num
        self.frames = collections.deque([], max_frames_to_save)
        self.frame = []
        self.batch_number = 0
        self.total_calls = 0
        self.detected_overflow = False
        self.prefix = "                 "
        self.analyse_model()
        self.register_forward_hook()
    def save_frame(self, frame=None):
        if frame is not None: self.expand_frame(frame)
        self.frames.append("\n".join(self.frame))
        self.frame = []
    def expand_frame(self, line): self.frame.append(line)
    def trace_frames(self):
        print("\n".join(self.frames))
        self.frames = []
    def reset_saved_frames(self): self.frames = []
    def dump_saved_frames(self):
        print(f"\nDetected inf/nan during batch_number={self.batch_number}")
        print(f"Last {len(self.frames)} forward frames:")
        print(f"{'abs min':8} {'abs max':8} metadata")
        print("\n".join(self.frames))
        print("\n\n")
        self.frames = []
    def analyse_model(self): self.module_names = {m: name for name, m in self.model.named_modules()}
    def analyse_variable(self, var, ctx):
        if torch.is_tensor(var):
            self.expand_frame(get_abs_min_max(var, ctx))
            if detect_overflow(var, ctx): self.detected_overflow = True
        elif var is None: self.expand_frame(f"{'None':>17} {ctx}")
        else: self.expand_frame(f"{'not a tensor':>17} {ctx}")
    def batch_start_frame(self):
        self.expand_frame(f"\n\n{self.prefix} *** Starting batch number={self.batch_number} ***")
        self.expand_frame(f"{'abs min':8} {'abs max':8} metadata")
    def batch_end_frame(self): self.expand_frame(f"{self.prefix} *** Finished batch number={self.batch_number-1} ***\n\n")
    def create_frame(self, module, input, output):
        self.expand_frame(f"{self.prefix} {self.module_names[module]} {module.__class__.__name__}")
        for name, p in module.named_parameters(recurse=False): self.analyse_variable(p, name)
        if isinstance(input, tuple):
            for i, x in enumerate(input): self.analyse_variable(x, f"input[{i}]")
        else: self.analyse_variable(input, "input")
        if isinstance(output, tuple):
            for i, x in enumerate(output):
                if isinstance(x, tuple):
                    for j, y in enumerate(x): self.analyse_variable(y, f"output[{i}][{j}]")
                else: self.analyse_variable(x, f"output[{i}]")
        else: self.analyse_variable(output, "output")
        self.save_frame()
    def register_forward_hook(self): self.model.apply(self._register_forward_hook)
    def _register_forward_hook(self, module): module.register_forward_hook(self.forward_hook)
    def forward_hook(self, module, input, output):
        last_frame_of_batch = False
        trace_mode = True if self.batch_number in self.trace_batch_nums else False
        if trace_mode: self.reset_saved_frames()
        if self.total_calls == 0: self.batch_start_frame()
        self.total_calls += 1
        if module == self.model:
            self.batch_number += 1
            last_frame_of_batch = True
        self.create_frame(module, input, output)
        if trace_mode: self.trace_frames()
        if last_frame_of_batch: self.batch_start_frame()
        if self.detected_overflow and not trace_mode:
            self.dump_saved_frames()
            raise ValueError("DebugUnderflowOverflow: inf/nan detected, aborting as there is no point running further. Please scroll up above this traceback to see the activation values prior to this event.")
        if self.abort_after_batch_num is not None and self.batch_number > self.abort_after_batch_num: raise ValueError(f"DebugUnderflowOverflow: aborting after {self.batch_number} batches due to `abort_after_batch_num={self.abort_after_batch_num}` arg")
def get_abs_min_max(var, ctx):
    abs_var = var.abs()
    return f"{abs_var.min():8.2e} {abs_var.max():8.2e} {ctx}"
def detect_overflow(var, ctx):
    detected = False
    if torch.isnan(var).any().item():
        detected = True
        print(f"{ctx} has nans")
    if torch.isinf(var).any().item():
        detected = True
        print(f"{ctx} has infs")
    if 0:
        n100 = var[torch.ge(var.abs(), 100)]
        if n100.numel() > 0: print(f"{ctx}:  n100={n100.numel()}")
        n1000 = var[torch.ge(var.abs(), 1000)]
        if n1000.numel() > 0: print(f"{ctx}: n1000={n1000.numel()}")
        n10000 = var[torch.ge(var.abs(), 10000)]
        if n10000.numel() > 0: print(f"{ctx}: n10000={n10000.numel()}")
    if 0: print(f"min={var.min():9.2e} max={var.max():9.2e}")
    if 0: print(f"min={var.min():9.2e} max={var.max():9.2e} var={var.var():9.2e} mean={var.mean():9.2e} ({ctx})")
    return detected
class DebugOption(ExplicitEnum):
    UNDERFLOW_OVERFLOW = "underflow_overflow"
    TPU_METRICS_DEBUG = "tpu_metrics_debug"
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
