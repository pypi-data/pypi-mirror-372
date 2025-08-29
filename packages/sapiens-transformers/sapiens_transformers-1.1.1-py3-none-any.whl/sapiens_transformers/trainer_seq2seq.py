"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple, Union
from .integrations.deepspeed import is_deepspeed_zero3_enabled
from .generation.configuration_utils import GenerationConfig
from torch.utils.data import Dataset
from .trainer import Trainer
from .utils import logging
from copy import deepcopy
from pathlib import Path
from torch import nn
import warnings
import torch
if TYPE_CHECKING:
    from .data.data_collator import DataCollator
    from .modeling_utils import PreTrainedModel
    from .tokenization_utils_base import PreTrainedTokenizerBase
    from .trainer_callback import TrainerCallback
    from .trainer_utils import EvalPrediction, PredictionOutput
    from .training_args import TrainingArguments
logger = logging.get_logger(__name__)
class Seq2SeqTrainer(Trainer):
    def __init__(self, model: Union["PreTrainedModel", nn.Module] = None, args: "TrainingArguments" = None, data_collator: Optional["DataCollator"] = None, train_dataset: Optional[Dataset] = None,
    eval_dataset: Optional[Union[Dataset, Dict[str, Dataset]]] = None, tokenizer: Optional["PreTrainedTokenizerBase"] = None, model_init: Optional[Callable[[], "PreTrainedModel"]] = None,
    compute_metrics: Optional[Callable[["EvalPrediction"], Dict]] = None, callbacks: Optional[List["TrainerCallback"]] = None, optimizers: Tuple[torch.optim.Optimizer, torch.optim.lr_scheduler.LambdaLR] = (None, None),
    preprocess_logits_for_metrics: Optional[Callable[[torch.Tensor, torch.Tensor], torch.Tensor]] = None):
        super().__init__(model=model, args=args, data_collator=data_collator, train_dataset=train_dataset, eval_dataset=eval_dataset, tokenizer=tokenizer,
        model_init=model_init, compute_metrics=compute_metrics, callbacks=callbacks, optimizers=optimizers, preprocess_logits_for_metrics=preprocess_logits_for_metrics)
        if self.args.generation_config is not None:
            gen_config = self.load_generation_config(self.args.generation_config)
            self.model.generation_config = gen_config
    @staticmethod
    def load_generation_config(gen_config_arg: Union[str, GenerationConfig]) -> GenerationConfig:
        if isinstance(gen_config_arg, GenerationConfig): gen_config = deepcopy(gen_config_arg)
        else:
            pretrained_model_name = Path(gen_config_arg) if isinstance(gen_config_arg, str) else gen_config_arg
            config_file_name = None
            if pretrained_model_name.is_file():
                config_file_name = pretrained_model_name.name
                pretrained_model_name = pretrained_model_name.parent
            elif pretrained_model_name.is_dir(): pass
            else: pretrained_model_name = gen_config_arg
            gen_config = GenerationConfig.from_pretrained(pretrained_model_name, config_file_name)
        try:
            with warnings.catch_warnings(record=True) as caught_warnings: gen_config.validate()
            if len(caught_warnings) > 0: raise ValueError(str([w.message for w in caught_warnings]))
        except ValueError as exc: raise ValueError("The loaded generation config instance is invalid -- `GenerationConfig.validate()` throws warnings and/or exceptions. Fix these issues to train your model.\n\nThrown during validation:\n" + str(exc))
        return gen_config
    def evaluate(self, eval_dataset: Optional[Dataset] = None, ignore_keys: Optional[List[str]] = None, metric_key_prefix: str = "eval", **gen_kwargs) -> Dict[str, float]:
        gen_kwargs = gen_kwargs.copy()
        if (gen_kwargs.get("max_length") is None and gen_kwargs.get("max_new_tokens") is None and self.args.generation_max_length is not None): gen_kwargs["max_length"] = self.args.generation_max_length
        if gen_kwargs.get("num_beams") is None and self.args.generation_num_beams is not None: gen_kwargs["num_beams"] = self.args.generation_num_beams
        self.gather_function = self.accelerator.gather
        self._gen_kwargs = gen_kwargs
        return super().evaluate(eval_dataset, ignore_keys=ignore_keys, metric_key_prefix=metric_key_prefix)
    def predict(self, test_dataset: Dataset, ignore_keys: Optional[List[str]] = None, metric_key_prefix: str = "test", **gen_kwargs) -> "PredictionOutput":
        gen_kwargs = gen_kwargs.copy()
        if (gen_kwargs.get("max_length") is None and gen_kwargs.get("max_new_tokens") is None and self.args.generation_max_length is not None): gen_kwargs["max_length"] = self.args.generation_max_length
        if gen_kwargs.get("num_beams") is None and self.args.generation_num_beams is not None: gen_kwargs["num_beams"] = self.args.generation_num_beams
        self.gather_function = self.accelerator.gather
        self._gen_kwargs = gen_kwargs
        return super().predict(test_dataset, ignore_keys=ignore_keys, metric_key_prefix=metric_key_prefix)
    def prediction_step(self, model: nn.Module, inputs: Dict[str, Union[torch.Tensor, Any]], prediction_loss_only: bool, ignore_keys: Optional[List[str]] = None, **gen_kwargs) -> Tuple[Optional[float], Optional[torch.Tensor], Optional[torch.Tensor]]:
        if not self.args.predict_with_generate or prediction_loss_only: return super().prediction_step(model, inputs, prediction_loss_only=prediction_loss_only, ignore_keys=ignore_keys)
        has_labels = "labels" in inputs
        inputs = self._prepare_inputs(inputs)
        if len(gen_kwargs) == 0 and hasattr(self, "_gen_kwargs"): gen_kwargs = self._gen_kwargs.copy()
        if "num_beams" in gen_kwargs and gen_kwargs["num_beams"] is None: gen_kwargs.pop("num_beams")
        if "max_length" in gen_kwargs and gen_kwargs["max_length"] is None: gen_kwargs.pop("max_length")
        default_synced_gpus = True if is_deepspeed_zero3_enabled() else False
        gen_kwargs["synced_gpus"] = (gen_kwargs["synced_gpus"] if gen_kwargs.get("synced_gpus") is not None else default_synced_gpus)
        generation_inputs = inputs.copy()
        if ("labels" in generation_inputs and "decoder_input_ids" in generation_inputs and generation_inputs["labels"].shape == generation_inputs["decoder_input_ids"].shape): generation_inputs = {k: v for k, v in inputs.items() if k not in ("decoder_input_ids", "decoder_attention_mask")}
        generated_tokens = self.model.generate(**generation_inputs, **gen_kwargs)
        if self.model.generation_config._from_model_config: self.model.generation_config._from_model_config = False
        gen_config = self.model.generation_config
        if generated_tokens.shape[-1] < gen_config.max_length: generated_tokens = self._pad_tensors_to_max_len(generated_tokens, gen_config.max_length)
        elif gen_config.max_new_tokens is not None and generated_tokens.shape[-1] < gen_config.max_new_tokens + 1: generated_tokens = self._pad_tensors_to_max_len(generated_tokens, gen_config.max_new_tokens + 1)
        with torch.no_grad():
            if has_labels:
                with self.compute_loss_context_manager(): outputs = model(**inputs)
                if self.label_smoother is not None: loss = self.label_smoother(outputs, inputs["labels"]).mean().detach()
                else: loss = (outputs["loss"] if isinstance(outputs, dict) else outputs[0]).mean().detach()
            else: loss = None
        if self.args.prediction_loss_only: return loss, None, None
        if has_labels:
            labels = inputs["labels"]
            if labels.shape[-1] < gen_config.max_length: labels = self._pad_tensors_to_max_len(labels, gen_config.max_length)
            elif gen_config.max_new_tokens is not None and labels.shape[-1] < gen_config.max_new_tokens + 1: labels = self._pad_tensors_to_max_len(labels, gen_config.max_new_tokens + 1)
        else: labels = None
        return loss, generated_tokens, labels
    def _pad_tensors_to_max_len(self, tensor, max_length):
        if self.tokenizer is not None and hasattr(self.tokenizer, "pad_token_id"): pad_token_id = (self.tokenizer.pad_token_id if self.tokenizer.pad_token_id is not None else self.tokenizer.eos_token_id)
        else:
            if self.model.config.pad_token_id is not None: pad_token_id = self.model.config.pad_token_id
            else: raise ValueError("Pad_token_id must be set in the configuration of the model, in order to pad tensors")
        padded_tensor = pad_token_id * torch.ones((tensor.shape[0], max_length), dtype=tensor.dtype, device=tensor.device)
        padded_tensor[:, : tensor.shape[-1]] = tensor
        return padded_tensor
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
