"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from . import IntervalStrategy, PreTrainedTokenizerBase
from huggingface_hub import Repository, create_repo
from typing import Callable, List, Optional, Union
from .modelcard import TrainingSummary
from .modeling_tf_utils import keras
from packaging.version import parse
from pathlib import Path
import tensorflow as tf
from time import sleep
import numpy as np
import logging
import os
logger = logging.getLogger(__name__)
class KerasMetricCallback(keras.callbacks.Callback):
    def __init__(self, metric_fn: Callable, eval_dataset: Union[tf.data.Dataset, np.ndarray, tf.Tensor, tuple, dict], output_cols: Optional[List[str]] = None, label_cols: Optional[List[str]] = None,
    batch_size: Optional[int] = None, predict_with_generate: bool = False, use_xla_generation: bool = False, generate_kwargs: Optional[dict] = None):
        super().__init__()
        self.metric_fn = metric_fn
        self.batch_size = batch_size
        if not isinstance(eval_dataset, tf.data.Dataset):
            if batch_size is None: raise ValueError("When passing data to KerasMetricCallback that is not a pre-batched tf.data.Dataset the batch_size argument must be set.")
            eval_dataset = tf.data.Dataset.from_tensor_slices(eval_dataset).batch(batch_size, drop_remainder=False)
        self.eval_dataset = eval_dataset
        self.predict_with_generate = predict_with_generate
        self.output_cols = output_cols
        if isinstance(eval_dataset.element_spec, tuple) and len(eval_dataset.element_spec) == 2: input_spec, label_spec = eval_dataset.element_spec
        else:
            input_spec = eval_dataset.element_spec
            label_spec = None
        if label_cols is not None:
            for label in label_cols:
                if label not in input_spec: raise ValueError(f"Label {label} is in label_cols but could not be found in the dataset inputs!")
            self.label_cols = label_cols
            self.use_keras_label = False
        elif label_spec is not None:
            self.label_cols = None
            self.use_keras_label = True
        elif "labels" in input_spec:
            self.label_cols = ["labels"]
            self.use_keras_label = False
            logging.warning("No label_cols specified for KerasMetricCallback, assuming you want the 'labels' key.")
        elif "start_positions" in input_spec and "end_positions" in input_spec:
            self.label_cols = ["start_positions", "end_positions"]
            self.use_keras_label = False
            logging.warning("No label_cols specified for KerasMetricCallback, assuming you want the start_positions and end_positions keys.")
        else: raise ValueError("Could not autodetect label_cols for KerasMetricCallback, please specify them!")
        if parse(tf.__version__) < parse("2.7"): logging.warning("TF versions less than 2.7 may encounter issues with KerasMetricCallback!")
        self.use_xla_generation = use_xla_generation
        self.generate_kwargs = {} if generate_kwargs is None else generate_kwargs
        self.generation_function = None
    @staticmethod
    def _concatenate_batches(batches, padding_index=-100):
        if batches[0].ndim == 1 or all(batch.shape[1] == batches[0].shape[1] for batch in batches): return np.concatenate(batches, axis=0)
        max_len = max([batch.shape[1] for batch in batches])
        num_samples = sum([batch.shape[0] for batch in batches])
        output = np.full_like(batches[0], fill_value=padding_index, shape=[num_samples, max_len] + list(batches[0].shape[2:]))
        i = 0
        for batch in batches:
            output[i : i + len(batch), : batch.shape[1]] = batch
            i += len(batch)
        return output
    def _postprocess_predictions_or_labels(self, inputs):
        if isinstance(inputs[0], dict):
            outputs = {}
            for key in inputs[0].keys(): outputs[key] = self._concatenate_batches([batch[key] for batch in inputs])
            if len(outputs) == 1: outputs = list(outputs.values())[0]
        elif isinstance(inputs[0], list) or isinstance(inputs[0], tuple):
            outputs = []
            for input_list in zip(*inputs): outputs.append(self._concatenate_batches(input_list))
            if len(outputs) == 1: outputs = outputs[0]
        elif isinstance(inputs[0], np.ndarray): outputs = self._concatenate_batches(inputs)
        elif isinstance(inputs[0], tf.Tensor): outputs = self._concatenate_batches([tensor.numpy() for tensor in inputs])
        else: raise TypeError(f"Couldn't handle batch of type {type(inputs[0])}!")
        return outputs
    def on_epoch_end(self, epoch, logs=None):
        if hasattr(self.model, "config"): ignore_keys = getattr(self.model.config, "keys_to_ignore_at_inference", [])
        else: ignore_keys = []
        main_input_name = None
        if self.predict_with_generate:
            if hasattr(self.model, "encoder") and hasattr(self.model.encoder, "main_input_name"): main_input_name = self.model.encoder.main_input_name
            else: main_input_name = getattr(self.model, "main_input_name", "input_ids")
            if self.use_xla_generation and self.generation_function is None:
                def generation_function(inputs, attention_mask): return self.model.generate(inputs, attention_mask=attention_mask, **self.generate_kwargs)
                self.generation_function = tf.function(generation_function, jit_compile=True)
        prediction_list = []
        label_list = []
        for batch in self.eval_dataset:
            if isinstance(batch, tuple): batch, labels = batch
            else: labels = None
            if self.predict_with_generate:
                if isinstance(batch, dict):
                    generation_inputs = batch[main_input_name]
                    attention_mask = batch.get("attention_mask", None)
                else:
                    generation_inputs = batch
                    attention_mask = None
                if self.use_xla_generation: predictions = self.generation_function(generation_inputs, attention_mask=attention_mask)
                else: predictions = self.model.generate(generation_inputs, attention_mask=attention_mask, **self.generate_kwargs)
            else:
                predictions = self.model.predict_on_batch(batch)
                if isinstance(predictions, dict):
                    predictions = dict(predictions)
                    if self.output_cols is not None: predictions = {key: predictions[key] for key in self.output_cols}
                    else: predictions = {key: val for key, val in predictions.items() if key not in ignore_keys + ["loss"]}
            prediction_list.append(predictions)
            if not self.use_keras_label: labels = {key: batch[key].numpy() for key in self.label_cols}
            elif isinstance(labels, dict): labels = {key: array.numpy() for key, array in labels.items()}
            elif isinstance(labels, list) or isinstance(labels, tuple): labels = [array.numpy() for array in labels]
            elif isinstance(labels, tf.Tensor): labels = labels.numpy()
            else: raise TypeError(f"Confused by labels of type {type(labels)}")
            label_list.append(labels)
        all_preds = self._postprocess_predictions_or_labels(prediction_list)
        all_labels = self._postprocess_predictions_or_labels(label_list)
        metric_output = self.metric_fn((all_preds, all_labels))
        if not isinstance(metric_output, dict): raise TypeError(f"metric_fn should return a dict mapping metric names to values but instead returned {metric_output}")
        logs.update(metric_output)
class PushToHubCallback(keras.callbacks.Callback):
    def __init__(self, output_dir: Union[str, Path], save_strategy: Union[str, IntervalStrategy] = "epoch", save_steps: Optional[int] = None, tokenizer: Optional[PreTrainedTokenizerBase] = None,
    hub_model_id: Optional[str] = None, hub_token: Optional[str] = None, checkpoint: bool = False, **model_card_args):
        super().__init__()
        if checkpoint and save_strategy != "epoch": raise ValueError("Cannot save checkpoints when save_strategy is not 'epoch'!")
        if isinstance(save_strategy, str): save_strategy = IntervalStrategy(save_strategy.lower())
        self.save_strategy = save_strategy
        if self.save_strategy == IntervalStrategy.STEPS and (not isinstance(save_steps, int) or save_steps <= 0): raise ValueError("Please supply a positive integer argument for save_steps when save_strategy == 'steps'!")
        self.save_steps = save_steps
        output_dir = Path(output_dir)
        if hub_model_id is None: hub_model_id = output_dir.absolute().name
        self.hub_model_id = create_repo(repo_id=hub_model_id, exist_ok=True, token=hub_token).repo_id
        self.output_dir = output_dir
        self.repo = Repository(str(self.output_dir), clone_from=self.hub_model_id, token=hub_token)
        self.tokenizer = tokenizer
        self.last_job = None
        self.checkpoint = checkpoint
        self.training_history = None
        self.model_card_args = model_card_args
    def on_train_begin(self, logs=None): self.training_history = []
    def on_train_batch_end(self, batch, logs=None):
        if self.save_strategy == IntervalStrategy.STEPS and (batch + 1) % self.save_steps == 0:
            if self.last_job is not None and not self.last_job.is_done: return
            self.model.save_pretrained(self.output_dir)
            if self.tokenizer is not None: self.tokenizer.save_pretrained(self.output_dir)
            _, self.last_job = self.repo.push_to_hub(commit_message=f"Training in progress steps {batch}", blocking=False)
    def on_epoch_end(self, epoch, logs=None):
        logs = logs.copy()
        if "epoch" not in logs: logs["epoch"] = epoch
        self.training_history.append(logs)
        if self.save_strategy == IntervalStrategy.EPOCH:
            if self.last_job is not None and not self.last_job.is_done: return
            self.model.save_pretrained(self.output_dir)
            if self.tokenizer is not None: self.tokenizer.save_pretrained(self.output_dir)
            if self.checkpoint:
                checkpoint_dir = os.path.join(self.output_dir, "checkpoint")
                self.model._save_checkpoint(checkpoint_dir, epoch)
            train_summary = TrainingSummary.from_keras(model=self.model, model_name=self.hub_model_id, keras_history=self.training_history, **self.model_card_args)
            model_card = train_summary.to_model_card()
            with (self.output_dir / "README.md").open("w") as f: f.write(model_card)
            _, self.last_job = self.repo.push_to_hub(commit_message=f"Training in progress epoch {epoch}", blocking=False)
    def on_train_end(self, logs=None):
        if self.last_job is not None and not self.last_job.is_done:
            logging.info("Pushing the last epoch to the Hub, this may take a while...")
            while not self.last_job.is_done: sleep(1)
        else:
            self.model.save_pretrained(self.output_dir)
            if self.tokenizer is not None: self.tokenizer.save_pretrained(self.output_dir)
            train_summary = TrainingSummary.from_keras(model=self.model, model_name=self.hub_model_id, keras_history=self.training_history, **self.model_card_args)
            model_card = train_summary.to_model_card()
            with (self.output_dir / "README.md").open("w") as f: f.write(model_card)
            self.repo.push_to_hub(commit_message="End of training", blocking=True)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
