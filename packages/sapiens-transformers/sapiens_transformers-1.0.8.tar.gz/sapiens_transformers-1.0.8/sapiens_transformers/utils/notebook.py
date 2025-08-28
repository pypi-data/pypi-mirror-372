"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import re
import time
from typing import Optional
import IPython.display as disp
from ..trainer_callback import TrainerCallback
from ..trainer_utils import IntervalStrategy, has_length
def format_time(t):
    "Format `t` (in seconds) to (h):mm:ss"
    t = int(t)
    h, m, s = t // 3600, (t // 60) % 60, t % 60
    return f"{h}:{m:02d}:{s:02d}" if h != 0 else f"{m:02d}:{s:02d}"
def html_progress_bar(value, total, prefix, label, width=300):
    return f"""
    <div>
      {prefix}
      <progress value='{value}' max='{total}' style='width:{width}px; height:20px; vertical-align: middle;'></progress>
      {label}
    </div>
    """
def text_to_html_table(items):
    "Put the texts in `items` in an HTML table."
    html_code = """<table border="1" class="dataframe">\n"""
    html_code += """  <thead>\n <tr style="text-align: left;">\n"""
    for i in items[0]: html_code += f"      <th>{i}</th>\n"
    html_code += "    </tr>\n  </thead>\n  <tbody>\n"
    for line in items[1:]:
        html_code += "    <tr>\n"
        for elt in line:
            elt = f"{elt:.6f}" if isinstance(elt, float) else str(elt)
            html_code += f"      <td>{elt}</td>\n"
        html_code += "    </tr>\n"
    html_code += "  </tbody>\n</table><p>"
    return html_code
class NotebookProgressBar:
    warmup = 5
    update_every = 0.2
    def __init__(self, total: int, prefix: Optional[str] = None, leave: bool = True, parent: Optional["NotebookTrainingTracker"] = None, width: int = 300):
        self.total = total
        self.prefix = "" if prefix is None else prefix
        self.leave = leave
        self.parent = parent
        self.width = width
        self.last_value = None
        self.comment = None
        self.output = None
        self.value = None
        self.label = None
    def update(self, value: int, force_update: bool = False, comment: str = None):
        self.value = value
        if comment is not None: self.comment = comment
        if self.last_value is None:
            self.start_time = self.last_time = time.time()
            self.start_value = self.last_value = value
            self.elapsed_time = self.predicted_remaining = None
            self.first_calls = self.warmup
            self.wait_for = 1
            self.update_bar(value)
        elif value <= self.last_value and not force_update: return
        elif force_update or self.first_calls > 0 or value >= min(self.last_value + self.wait_for, self.total):
            if self.first_calls > 0: self.first_calls -= 1
            current_time = time.time()
            self.elapsed_time = current_time - self.start_time
            if value > self.start_value: self.average_time_per_item = self.elapsed_time / (value - self.start_value)
            else: self.average_time_per_item = None
            if value >= self.total:
                value = self.total
                self.predicted_remaining = None
                if not self.leave: self.close()
            elif self.average_time_per_item is not None: self.predicted_remaining = self.average_time_per_item * (self.total - value)
            self.update_bar(value)
            self.last_value = value
            self.last_time = current_time
            if (self.average_time_per_item is None) or (self.average_time_per_item == 0): self.wait_for = 1
            else: self.wait_for = max(int(self.update_every / self.average_time_per_item), 1)
    def update_bar(self, value, comment=None):
        spaced_value = " " * (len(str(self.total)) - len(str(value))) + str(value)
        if self.elapsed_time is None: self.label = f"[{spaced_value}/{self.total} : < :"
        elif self.predicted_remaining is None: self.label = f"[{spaced_value}/{self.total} {format_time(self.elapsed_time)}"
        else:
            self.label = (f"[{spaced_value}/{self.total} {format_time(self.elapsed_time)} < {format_time(self.predicted_remaining)}")
            if self.average_time_per_item == 0: self.label += ", +inf it/s"
            else: self.label += f", {1/self.average_time_per_item:.2f} it/s"
        self.label += "]" if self.comment is None or len(self.comment) == 0 else f", {self.comment}]"
        self.display()
    def display(self):
        self.html_code = html_progress_bar(self.value, self.total, self.prefix, self.label, self.width)
        if self.parent is not None:
            self.parent.display()
            return
        if self.output is None: self.output = disp.display(disp.HTML(self.html_code), display_id=True)
        else: self.output.update(disp.HTML(self.html_code))
    def close(self):
        "Closes the progress bar."
        if self.parent is None and self.output is not None: self.output.update(disp.HTML(""))
class NotebookTrainingTracker(NotebookProgressBar):
    def __init__(self, num_steps, column_names=None):
        super().__init__(num_steps)
        self.inner_table = None if column_names is None else [column_names]
        self.child_bar = None
    def display(self):
        self.html_code = html_progress_bar(self.value, self.total, self.prefix, self.label, self.width)
        if self.inner_table is not None: self.html_code += text_to_html_table(self.inner_table)
        if self.child_bar is not None: self.html_code += self.child_bar.html_code
        if self.output is None: self.output = disp.display(disp.HTML(self.html_code), display_id=True)
        else: self.output.update(disp.HTML(self.html_code))
    def write_line(self, values):
        if self.inner_table is None: self.inner_table = [list(values.keys()), list(values.values())]
        else:
            columns = self.inner_table[0]
            for key in values.keys():
                if key not in columns: columns.append(key)
            self.inner_table[0] = columns
            if len(self.inner_table) > 1:
                last_values = self.inner_table[-1]
                first_column = self.inner_table[0][0]
                if last_values[0] != values[first_column]: self.inner_table.append([values[c] if c in values else "No Log" for c in columns])
                else:
                    new_values = values
                    for c in columns:
                        if c not in new_values.keys(): new_values[c] = last_values[columns.index(c)]
                    self.inner_table[-1] = [new_values[c] for c in columns]
            else: self.inner_table.append([values[c] for c in columns])
    def add_child(self, total, prefix=None, width=300):
        self.child_bar = NotebookProgressBar(total, prefix=prefix, parent=self, width=width)
        return self.child_bar
    def remove_child(self):
        self.child_bar = None
        self.display()
class NotebookProgressCallback(TrainerCallback):
    def __init__(self):
        self.training_tracker = None
        self.prediction_bar = None
        self._force_next_update = False
    def on_train_begin(self, args, state, control, **kwargs):
        self.first_column = "Epoch" if args.eval_strategy == IntervalStrategy.EPOCH else "Step"
        self.training_loss = 0
        self.last_log = 0
        column_names = [self.first_column] + ["Training Loss"]
        if args.eval_strategy != IntervalStrategy.NO: column_names.append("Validation Loss")
        self.training_tracker = NotebookTrainingTracker(state.max_steps, column_names)
    def on_step_end(self, args, state, control, **kwargs):
        epoch = int(state.epoch) if int(state.epoch) == state.epoch else f"{state.epoch:.2f}"
        self.training_tracker.update(state.global_step + 1, comment=f"Epoch {epoch}/{state.num_train_epochs}", force_update=self._force_next_update)
        self._force_next_update = False
    def on_prediction_step(self, args, state, control, eval_dataloader=None, **kwargs):
        if not has_length(eval_dataloader): return
        if self.prediction_bar is None:
            if self.training_tracker is not None: self.prediction_bar = self.training_tracker.add_child(len(eval_dataloader))
            else: self.prediction_bar = NotebookProgressBar(len(eval_dataloader))
            self.prediction_bar.update(1)
        else: self.prediction_bar.update(self.prediction_bar.value + 1)
    def on_predict(self, args, state, control, **kwargs):
        if self.prediction_bar is not None: self.prediction_bar.close()
        self.prediction_bar = None
    def on_log(self, args, state, control, logs=None, **kwargs):
        if args.eval_strategy == IntervalStrategy.NO and "loss" in logs:
            values = {"Training Loss": logs["loss"]}
            values["Step"] = state.global_step
            self.training_tracker.write_line(values)
    def on_evaluate(self, args, state, control, metrics=None, **kwargs):
        if self.training_tracker is not None:
            values = {"Training Loss": "No log", "Validation Loss": "No log"}
            for log in reversed(state.log_history):
                if "loss" in log:
                    values["Training Loss"] = log["loss"]
                    break
            if self.first_column == "Epoch": values["Epoch"] = int(state.epoch)
            else: values["Step"] = state.global_step
            metric_key_prefix = "eval"
            for k in metrics:
                if k.endswith("_loss"): metric_key_prefix = re.sub(r"\_loss$", "", k)
            _ = metrics.pop("total_flos", None)
            _ = metrics.pop("epoch", None)
            _ = metrics.pop(f"{metric_key_prefix}_runtime", None)
            _ = metrics.pop(f"{metric_key_prefix}_samples_per_second", None)
            _ = metrics.pop(f"{metric_key_prefix}_steps_per_second", None)
            _ = metrics.pop(f"{metric_key_prefix}_jit_compilation_time", None)
            for k, v in metrics.items():
                splits = k.split("_")
                name = " ".join([part.capitalize() for part in splits[1:]])
                if name == "Loss": name = "Validation Loss"
                values[name] = v
            self.training_tracker.write_line(values)
            self.training_tracker.remove_child()
            self.prediction_bar = None
            self._force_next_update = True
    def on_train_end(self, args, state, control, **kwargs):
        self.training_tracker.update(state.global_step, comment=f"Epoch {int(state.epoch)}/{state.num_train_epochs}", force_update=True)
        self.training_tracker = None
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
