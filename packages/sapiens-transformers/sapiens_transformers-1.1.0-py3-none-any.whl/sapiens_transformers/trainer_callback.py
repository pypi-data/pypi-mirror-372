"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from .trainer_utils import IntervalStrategy, has_length
from typing import Dict, List, Optional, Union
from .training_args import TrainingArguments
from dataclasses import dataclass
from tqdm.auto import tqdm
from .utils import logging
import numpy as np
import dataclasses
import json
logger = logging.get_logger(__name__)
@dataclass
class TrainerState:
    epoch: Optional[float] = None
    global_step: int = 0
    max_steps: int = 0
    logging_steps: int = 500
    eval_steps: int = 500
    save_steps: int = 500
    train_batch_size: int = None
    num_train_epochs: int = 0
    num_input_tokens_seen: int = 0
    total_flos: float = 0
    log_history: List[Dict[str, float]] = None
    best_metric: Optional[float] = None
    best_model_checkpoint: Optional[str] = None
    is_local_process_zero: bool = True
    is_world_process_zero: bool = True
    is_hyper_param_search: bool = False
    trial_name: str = None
    trial_params: Dict[str, Union[str, float, int, bool]] = None
    stateful_callbacks: List["TrainerCallback"] = None
    def __post_init__(self):
        if self.log_history is None: self.log_history = []
        if self.stateful_callbacks is None: self.stateful_callbacks = {}
        elif isinstance(self.stateful_callbacks, dict): pass
        else:
            stateful_callbacks = {}
            for callback in self.stateful_callbacks:
                if not isinstance(callback, (ExportableState)): raise TypeError(f"All callbacks passed to be saved must inherit `ExportableState`, but received {type(callback)}")
                name = callback.__class__.__name__
                if name in stateful_callbacks:
                    if not isinstance(stateful_callbacks[name], list): stateful_callbacks[name] = [stateful_callbacks[name]]
                    stateful_callbacks[name].append(callback.state())
                else: stateful_callbacks[name] = callback.state()
            self.stateful_callbacks = stateful_callbacks
    def save_to_json(self, json_path: str):
        json_string = json.dumps(dataclasses.asdict(self), indent=2, sort_keys=True) + "\n"
        with open(json_path, "w", encoding="utf-8") as f: f.write(json_string)
    @classmethod
    def load_from_json(cls, json_path: str):
        with open(json_path, "r", encoding="utf-8") as f: text = f.read()
        return cls(**json.loads(text))
class ExportableState:
    def state(self) -> dict: raise NotImplementedError("You must implement a `state` function to utilize this class.")
    @classmethod
    def from_state(cls, state):
        instance = cls(**state["args"])
        for k, v in state["attributes"].items(): setattr(instance, k, v)
        return instance
@dataclass
class TrainerControl(ExportableState):
    should_training_stop: bool = False
    should_epoch_stop: bool = False
    should_save: bool = False
    should_evaluate: bool = False
    should_log: bool = False
    def _new_training(self): self.should_training_stop = False
    def _new_epoch(self): self.should_epoch_stop = False
    def _new_step(self):
        self.should_save = False
        self.should_evaluate = False
        self.should_log = False
    def state(self) -> dict: return {"args": {"should_training_stop": self.should_training_stop, "should_epoch_stop": self.should_epoch_stop, "should_save": self.should_save, "should_evaluate": self.should_evaluate, "should_log": self.should_log}, "attributes": {}}
class TrainerCallback:
    def on_init_end(self, args: TrainingArguments, state: TrainerState, control: TrainerControl, **kwargs): pass
    def on_train_begin(self, args: TrainingArguments, state: TrainerState, control: TrainerControl, **kwargs): pass
    def on_train_end(self, args: TrainingArguments, state: TrainerState, control: TrainerControl, **kwargs): pass
    def on_epoch_begin(self, args: TrainingArguments, state: TrainerState, control: TrainerControl, **kwargs): pass
    def on_epoch_end(self, args: TrainingArguments, state: TrainerState, control: TrainerControl, **kwargs): pass
    def on_step_begin(self, args: TrainingArguments, state: TrainerState, control: TrainerControl, **kwargs): pass
    def on_pre_optimizer_step(self, args: TrainingArguments, state: TrainerState, control: TrainerControl, **kwargs): pass
    def on_optimizer_step(self, args: TrainingArguments, state: TrainerState, control: TrainerControl, **kwargs): pass
    def on_substep_end(self, args: TrainingArguments, state: TrainerState, control: TrainerControl, **kwargs): pass
    def on_step_end(self, args: TrainingArguments, state: TrainerState, control: TrainerControl, **kwargs): pass
    def on_evaluate(self, args: TrainingArguments, state: TrainerState, control: TrainerControl, **kwargs): pass
    def on_predict(self, args: TrainingArguments, state: TrainerState, control: TrainerControl, metrics, **kwargs): pass
    def on_save(self, args: TrainingArguments, state: TrainerState, control: TrainerControl, **kwargs): pass
    def on_log(self, args: TrainingArguments, state: TrainerState, control: TrainerControl, **kwargs): pass
    def on_prediction_step(self, args: TrainingArguments, state: TrainerState, control: TrainerControl, **kwargs): pass
class CallbackHandler(TrainerCallback):
    def __init__(self, callbacks, model, tokenizer, optimizer, lr_scheduler):
        self.callbacks = []
        for cb in callbacks: self.add_callback(cb)
        self.model = model
        self.tokenizer = tokenizer
        self.optimizer = optimizer
        self.lr_scheduler = lr_scheduler
        self.train_dataloader = None
        self.eval_dataloader = None
        if not any(isinstance(cb, DefaultFlowCallback) for cb in self.callbacks): logger.warning("The Trainer will not work properly if you don't have a `DefaultFlowCallback` in its callbacks. You\nshould add one before training with `trainer.add_callback(DefaultFlowCallback). The current list of callbacks is\n:"+self.callback_list)
    def add_callback(self, callback):
        cb = callback() if isinstance(callback, type) else callback
        cb_class = callback if isinstance(callback, type) else callback.__class__
        if cb_class in [c.__class__ for c in self.callbacks]: logger.warning(f"You are adding a {cb_class} to the callbacks of this Trainer, but there is already one. The current list of callbacks is\n:"+self.callback_list)
        self.callbacks.append(cb)
    def pop_callback(self, callback):
        if isinstance(callback, type):
            for cb in self.callbacks:
                if isinstance(cb, callback):
                    self.callbacks.remove(cb)
                    return cb
        else:
            for cb in self.callbacks:
                if cb == callback:
                    self.callbacks.remove(cb)
                    return cb
    def remove_callback(self, callback):
        if isinstance(callback, type):
            for cb in self.callbacks:
                if isinstance(cb, callback):
                    self.callbacks.remove(cb)
                    return
        else: self.callbacks.remove(callback)
    @property
    def callback_list(self): return "\n".join(cb.__class__.__name__ for cb in self.callbacks)
    def on_init_end(self, args: TrainingArguments, state: TrainerState, control: TrainerControl): return self.call_event("on_init_end", args, state, control)
    def on_train_begin(self, args: TrainingArguments, state: TrainerState, control: TrainerControl):
        control.should_training_stop = False
        return self.call_event("on_train_begin", args, state, control)
    def on_train_end(self, args: TrainingArguments, state: TrainerState, control: TrainerControl): return self.call_event("on_train_end", args, state, control)
    def on_epoch_begin(self, args: TrainingArguments, state: TrainerState, control: TrainerControl):
        control.should_epoch_stop = False
        return self.call_event("on_epoch_begin", args, state, control)
    def on_epoch_end(self, args: TrainingArguments, state: TrainerState, control: TrainerControl): return self.call_event("on_epoch_end", args, state, control)
    def on_step_begin(self, args: TrainingArguments, state: TrainerState, control: TrainerControl):
        control.should_log = False
        control.should_evaluate = False
        control.should_save = False
        return self.call_event("on_step_begin", args, state, control)
    def on_pre_optimizer_step(self, args: TrainingArguments, state: TrainerState, control: TrainerControl): return self.call_event("on_pre_optimizer_step", args, state, control)
    def on_optimizer_step(self, args: TrainingArguments, state: TrainerState, control: TrainerControl): return self.call_event("on_optimizer_step", args, state, control)
    def on_substep_end(self, args: TrainingArguments, state: TrainerState, control: TrainerControl): return self.call_event("on_substep_end", args, state, control)
    def on_step_end(self, args: TrainingArguments, state: TrainerState, control: TrainerControl): return self.call_event("on_step_end", args, state, control)
    def on_evaluate(self, args: TrainingArguments, state: TrainerState, control: TrainerControl, metrics):
        control.should_evaluate = False
        return self.call_event("on_evaluate", args, state, control, metrics=metrics)
    def on_predict(self, args: TrainingArguments, state: TrainerState, control: TrainerControl, metrics): return self.call_event("on_predict", args, state, control, metrics=metrics)
    def on_save(self, args: TrainingArguments, state: TrainerState, control: TrainerControl):
        control.should_save = False
        return self.call_event("on_save", args, state, control)
    def on_log(self, args: TrainingArguments, state: TrainerState, control: TrainerControl, logs):
        control.should_log = False
        return self.call_event("on_log", args, state, control, logs=logs)
    def on_prediction_step(self, args: TrainingArguments, state: TrainerState, control: TrainerControl): return self.call_event("on_prediction_step", args, state, control)
    def call_event(self, event, args, state, control, **kwargs):
        for callback in self.callbacks:
            result = getattr(callback, event)(args, state, control, model=self.model, tokenizer=self.tokenizer, optimizer=self.optimizer, lr_scheduler=self.lr_scheduler, train_dataloader=self.train_dataloader, eval_dataloader=self.eval_dataloader, **kwargs)
            if result is not None: control = result
        return control
class DefaultFlowCallback(TrainerCallback):
    def on_step_end(self, args: TrainingArguments, state: TrainerState, control: TrainerControl, **kwargs):
        if state.global_step == 1 and args.logging_first_step: control.should_log = True
        if args.logging_strategy == IntervalStrategy.STEPS and state.global_step % state.logging_steps == 0: control.should_log = True
        if (args.eval_strategy == IntervalStrategy.STEPS and state.global_step % state.eval_steps == 0 and args.eval_delay <= state.global_step): control.should_evaluate = True
        if (args.save_strategy == IntervalStrategy.STEPS and state.save_steps > 0 and state.global_step % state.save_steps == 0): control.should_save = True
        if state.global_step >= state.max_steps:
            control.should_training_stop = True
            if args.save_strategy != IntervalStrategy.NO: control.should_save = True
        return control
    def on_epoch_end(self, args: TrainingArguments, state: TrainerState, control: TrainerControl, **kwargs):
        if args.logging_strategy == IntervalStrategy.EPOCH: control.should_log = True
        if args.eval_strategy == IntervalStrategy.EPOCH and args.eval_delay <= state.epoch: control.should_evaluate = True
        if args.save_strategy == IntervalStrategy.EPOCH: control.should_save = True
        return control
class ProgressCallback(TrainerCallback):
    def __init__(self):
        self.training_bar = None
        self.prediction_bar = None
    def on_train_begin(self, args, state, control, **kwargs):
        if state.is_world_process_zero: self.training_bar = tqdm(total=state.max_steps, dynamic_ncols=True)
        self.current_step = 0
    def on_step_end(self, args, state, control, **kwargs):
        if state.is_world_process_zero:
            self.training_bar.update(state.global_step - self.current_step)
            self.current_step = state.global_step
    def on_prediction_step(self, args, state, control, eval_dataloader=None, **kwargs):
        if state.is_world_process_zero and has_length(eval_dataloader):
            if self.prediction_bar is None: self.prediction_bar = tqdm(total=len(eval_dataloader), leave=self.training_bar is None, dynamic_ncols=True)
            self.prediction_bar.update(1)
    def on_evaluate(self, args, state, control, **kwargs):
        if state.is_world_process_zero:
            if self.prediction_bar is not None: self.prediction_bar.close()
            self.prediction_bar = None
    def on_predict(self, args, state, control, **kwargs):
        if state.is_world_process_zero:
            if self.prediction_bar is not None: self.prediction_bar.close()
            self.prediction_bar = None
    def on_log(self, args, state, control, logs=None, **kwargs):
        if state.is_world_process_zero and self.training_bar is not None:
            shallow_logs = {}
            for k, v in logs.items(): shallow_logs[k] = v
            _ = shallow_logs.pop("total_flos", None)
            if "epoch" in shallow_logs: shallow_logs["epoch"] = round(shallow_logs["epoch"], 2)
            self.training_bar.write(str(shallow_logs))
    def on_train_end(self, args, state, control, **kwargs):
        if state.is_world_process_zero:
            self.training_bar.close()
            self.training_bar = None
class PrinterCallback(TrainerCallback):
    def on_log(self, args, state, control, logs=None, **kwargs):
        _ = logs.pop("total_flos", None)
        if state.is_local_process_zero: print(logs)
class EarlyStoppingCallback(TrainerCallback, ExportableState):
    def __init__(self, early_stopping_patience: int = 1, early_stopping_threshold: Optional[float] = 0.0):
        self.early_stopping_patience = early_stopping_patience
        self.early_stopping_threshold = early_stopping_threshold
        self.early_stopping_patience_counter = 0
    def check_metric_value(self, args, state, control, metric_value):
        operator = np.greater if args.greater_is_better else np.less
        if state.best_metric is None or (operator(metric_value, state.best_metric) and abs(metric_value - state.best_metric) > self.early_stopping_threshold): self.early_stopping_patience_counter = 0
        else: self.early_stopping_patience_counter += 1
    def on_train_begin(self, args, state, control, **kwargs):
        assert args.load_best_model_at_end, "EarlyStoppingCallback requires load_best_model_at_end = True"
        assert (args.metric_for_best_model is not None), "EarlyStoppingCallback requires metric_for_best_model is defined"
        assert (args.eval_strategy != IntervalStrategy.NO), "EarlyStoppingCallback requires IntervalStrategy of steps or epoch"
    def on_evaluate(self, args, state, control, metrics, **kwargs):
        metric_to_check = args.metric_for_best_model
        if not metric_to_check.startswith("eval_"): metric_to_check = f"eval_{metric_to_check}"
        metric_value = metrics.get(metric_to_check)
        if metric_value is None:
            logger.warning(f"early stopping required metric_for_best_model, but did not find {metric_to_check} so early stopping is disabled")
            return
        self.check_metric_value(args, state, control, metric_value)
        if self.early_stopping_patience_counter >= self.early_stopping_patience: control.should_training_stop = True
    def state(self) -> dict: return {"args": {"early_stopping_patience": self.early_stopping_patience, "early_stopping_threshold": self.early_stopping_threshold}, "attributes": {"early_stopping_patience_counter": self.early_stopping_patience_counter}}
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
