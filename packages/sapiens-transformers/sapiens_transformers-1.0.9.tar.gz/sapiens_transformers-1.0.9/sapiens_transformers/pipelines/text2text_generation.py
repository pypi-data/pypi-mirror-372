"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import enum
import warnings
from ..tokenization_utils import TruncationStrategy
from ..utils import add_end_docstrings, is_tf_available, is_torch_available, logging
from .base import Pipeline, build_pipeline_init_args
if is_tf_available():
    import tensorflow as tf
    from ..models.auto.modeling_tf_auto import TF_MODEL_FOR_SEQ_TO_SEQ_CAUSAL_LM_MAPPING_NAMES
if is_torch_available(): from ..models.auto.modeling_auto import MODEL_FOR_SEQ_TO_SEQ_CAUSAL_LM_MAPPING_NAMES
logger = logging.get_logger(__name__)
class ReturnType(enum.Enum):
    TENSORS = 0
    TEXT = 1
@add_end_docstrings(build_pipeline_init_args(has_tokenizer=True))
class Text2TextGenerationPipeline(Pipeline):
    return_name = "generated"
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.check_model_type(TF_MODEL_FOR_SEQ_TO_SEQ_CAUSAL_LM_MAPPING_NAMES if self.framework == "tf" else MODEL_FOR_SEQ_TO_SEQ_CAUSAL_LM_MAPPING_NAMES)
    def _sanitize_parameters(self, return_tensors=None, return_text=None, return_type=None, clean_up_tokenization_spaces=None, truncation=None, stop_sequence=None, **generate_kwargs):
        preprocess_params = {}
        if truncation is not None: preprocess_params["truncation"] = truncation
        forward_params = generate_kwargs
        postprocess_params = {}
        if return_tensors is not None and return_type is None: return_type = ReturnType.TENSORS if return_tensors else ReturnType.TEXT
        if return_type is not None: postprocess_params["return_type"] = return_type
        if clean_up_tokenization_spaces is not None: postprocess_params["clean_up_tokenization_spaces"] = clean_up_tokenization_spaces
        if stop_sequence is not None:
            stop_sequence_ids = self.tokenizer.encode(stop_sequence, add_special_tokens=False)
            generate_kwargs["eos_token_id"] = stop_sequence_ids[0]
        return preprocess_params, forward_params, postprocess_params
    def check_inputs(self, input_length: int, min_length: int, max_length: int): return True
    def _parse_and_tokenize(self, *args, truncation):
        prefix = self.prefix if self.prefix is not None else ""
        if isinstance(args[0], list):
            if self.tokenizer.pad_token_id is None: raise ValueError("Please make sure that the tokenizer has a pad_token_id when using a batch input")
            args = ([prefix + arg for arg in args[0]],)
            padding = True
        elif isinstance(args[0], str):
            args = (prefix + args[0],)
            padding = False
        else: raise ValueError(f" `args[0]`: {args[0]} have the wrong format. The should be either of type `str` or type `list`")
        inputs = self.tokenizer(*args, padding=padding, truncation=truncation, return_tensors=self.framework)
        if "token_type_ids" in inputs: del inputs["token_type_ids"]
        return inputs
    def __call__(self, *args, **kwargs):
        result = super().__call__(*args, **kwargs)
        if (isinstance(args[0], list) and all(isinstance(el, str) for el in args[0]) and all(len(res) == 1 for res in result)): return [res[0] for res in result]
        return result
    def preprocess(self, inputs, truncation=TruncationStrategy.DO_NOT_TRUNCATE, **kwargs):
        inputs = self._parse_and_tokenize(inputs, truncation=truncation, **kwargs)
        return inputs
    def _forward(self, model_inputs, **generate_kwargs):
        if self.framework == "pt": in_b, input_length = model_inputs["input_ids"].shape
        elif self.framework == "tf": in_b, input_length = tf.shape(model_inputs["input_ids"]).numpy()
        self.check_inputs(input_length, generate_kwargs.get("min_length", self.generation_config.min_length), generate_kwargs.get("max_length", self.generation_config.max_length))
        if "generation_config" not in generate_kwargs: generate_kwargs["generation_config"] = self.generation_config
        output_ids = self.model.generate(**model_inputs, **generate_kwargs)
        out_b = output_ids.shape[0]
        if self.framework == "pt": output_ids = output_ids.reshape(in_b, out_b // in_b, *output_ids.shape[1:])
        elif self.framework == "tf": output_ids = tf.reshape(output_ids, (in_b, out_b // in_b, *output_ids.shape[1:]))
        return {"output_ids": output_ids}
    def postprocess(self, model_outputs, return_type=ReturnType.TEXT, clean_up_tokenization_spaces=False):
        records = []
        for output_ids in model_outputs["output_ids"][0]:
            if return_type == ReturnType.TENSORS: record = {f"{self.return_name}_token_ids": output_ids}
            elif return_type == ReturnType.TEXT: record = {f"{self.return_name}_text": self.tokenizer.decode(output_ids, skip_special_tokens=True, clean_up_tokenization_spaces=clean_up_tokenization_spaces)}
            records.append(record)
        return records
@add_end_docstrings(build_pipeline_init_args(has_tokenizer=True))
class SummarizationPipeline(Text2TextGenerationPipeline):
    return_name = "summary"
    def __call__(self, *args, **kwargs): return super().__call__(*args, **kwargs)
    def check_inputs(self, input_length: int, min_length: int, max_length: int) -> bool:
        if max_length < min_length: logger.warning(f"Your min_length={min_length} must be inferior than your max_length={max_length}.")
        if input_length < max_length: logger.warning(f"Your max_length is set to {max_length}, but your input_length is only {input_length}. Since this is a summarization task, where outputs shorter than the input are typically wanted, you might consider decreasing max_length manually, e.g. summarizer('...', max_length={input_length//2})")
@add_end_docstrings(build_pipeline_init_args(has_tokenizer=True))
class TranslationPipeline(Text2TextGenerationPipeline):
    return_name = "translation"
    def check_inputs(self, input_length: int, min_length: int, max_length: int):
        if input_length > 0.9 * max_length: logger.warning(f"Your input_length: {input_length} is bigger than 0.9 * max_length: {max_length}. You might consider increasing your max_length manually, e.g. translator('...', max_length=400)")
        return True
    def preprocess(self, *args, truncation=TruncationStrategy.DO_NOT_TRUNCATE, src_lang=None, tgt_lang=None):
        if getattr(self.tokenizer, "_build_translation_inputs", None): return self.tokenizer._build_translation_inputs(*args, return_tensors=self.framework, truncation=truncation, src_lang=src_lang, tgt_lang=tgt_lang)
        else: return super()._parse_and_tokenize(*args, truncation=truncation)
    def _sanitize_parameters(self, src_lang=None, tgt_lang=None, **kwargs):
        preprocess_params, forward_params, postprocess_params = super()._sanitize_parameters(**kwargs)
        if src_lang is not None: preprocess_params["src_lang"] = src_lang
        if tgt_lang is not None: preprocess_params["tgt_lang"] = tgt_lang
        if src_lang is None and tgt_lang is None:
            task = kwargs.get("task", self.task)
            items = task.split("_")
            if task and len(items) == 4:
                preprocess_params["src_lang"] = items[1]
                preprocess_params["tgt_lang"] = items[3]
        return preprocess_params, forward_params, postprocess_params
    def __call__(self, *args, **kwargs): return super().__call__(*args, **kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
