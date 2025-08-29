"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import enum
import warnings
from typing import Dict
from ..utils import add_end_docstrings, is_tf_available, is_torch_available
from .base import Pipeline, build_pipeline_init_args
if is_torch_available():
    from ..models.auto.modeling_auto import MODEL_FOR_CAUSAL_LM_MAPPING_NAMES
    from .pt_utils import KeyDataset
if is_tf_available():
    import tensorflow as tf
    from ..models.auto.modeling_tf_auto import TF_MODEL_FOR_CAUSAL_LM_MAPPING_NAMES
class ReturnType(enum.Enum):
    TENSORS = 0
    NEW_TEXT = 1
    FULL_TEXT = 2
class Chat:
    def __init__(self, messages: Dict):
        for message in messages:
            if not ("role" in message and "content" in message): raise ValueError("When passing chat dicts as input, each dict must have a 'role' and 'content' key.")
        self.messages = messages
@add_end_docstrings(build_pipeline_init_args(has_tokenizer=True))
class TextGenerationPipeline(Pipeline):
    XL_PREFIX = """
    In 1991, the remains of Russian Tsar Nicholas II and his family (except for Alexei and Maria) are discovered. The
    voice of Nicholas's young son, Tsarevich Alexei Nikolaevich, narrates the remainder of the story. 1883 Western
    Siberia, a young Grigori Rasputin is asked by his father and a group of men to perform magic. Rasputin has a vision
    and denounces one of the men as a horse thief. Although his father initially slaps him for making such an
    accusation, Rasputin watches as the man is chased outside and beaten. Twenty years later, Rasputin sees a vision of
    the Virgin Mary, prompting him to become a priest. Rasputin quickly becomes famous, with people, even a bishop,
    begging for his blessing. <eod> </s> <eos>
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.check_model_type(TF_MODEL_FOR_CAUSAL_LM_MAPPING_NAMES if self.framework == "tf" else MODEL_FOR_CAUSAL_LM_MAPPING_NAMES)
        if "prefix" not in self._preprocess_params:
            prefix = None
            if self.prefix is not None: prefix = self.prefix
            if prefix is None and self.model.__class__.__name__ in ["XLNetLMHeadModel", "TransfoXLLMHeadModel", "TFXLNetLMHeadModel", "TFTransfoXLLMHeadModel"]: prefix = self.XL_PREFIX
            if prefix is not None:
                preprocess_params, forward_params, _ = self._sanitize_parameters(prefix=prefix, **self._forward_params)
                self._preprocess_params = {**self._preprocess_params, **preprocess_params}
                self._forward_params = {**self._forward_params, **forward_params}
    def _sanitize_parameters(self, return_full_text=None, return_tensors=None, return_text=None, return_type=None, clean_up_tokenization_spaces=None, prefix=None,
    handle_long_generation=None, stop_sequence=None, truncation=None, max_length=None, continue_final_message=None, **generate_kwargs):
        preprocess_params = {}
        add_special_tokens = False
        if "add_special_tokens" in generate_kwargs: add_special_tokens = preprocess_params["add_special_tokens"] = generate_kwargs.pop("add_special_tokens")
        if "padding" in generate_kwargs: preprocess_params["padding"] = generate_kwargs.pop("padding")
        if truncation is not None: preprocess_params["truncation"] = truncation
        if max_length is not None:
            preprocess_params["max_length"] = max_length
            generate_kwargs["max_length"] = max_length
        if prefix is not None: preprocess_params["prefix"] = prefix
        if prefix:
            prefix_inputs = self.tokenizer(prefix, padding=False, add_special_tokens=add_special_tokens, return_tensors=self.framework)
            generate_kwargs["prefix_length"] = prefix_inputs["input_ids"].shape[-1]
        if handle_long_generation is not None:
            if handle_long_generation not in {"hole"}: raise ValueError(f"{handle_long_generation} is not a valid value for `handle_long_generation` parameter expected [None, 'hole']")
            preprocess_params["handle_long_generation"] = handle_long_generation
        if continue_final_message is not None: preprocess_params["continue_final_message"] = continue_final_message
        preprocess_params.update(generate_kwargs)
        forward_params = generate_kwargs
        postprocess_params = {}
        if return_full_text is not None and return_type is None:
            if return_text is not None: raise ValueError("`return_text` is mutually exclusive with `return_full_text`")
            if return_tensors is not None: raise ValueError("`return_full_text` is mutually exclusive with `return_tensors`")
            return_type = ReturnType.FULL_TEXT if return_full_text else ReturnType.NEW_TEXT
        if return_tensors is not None and return_type is None:
            if return_text is not None: raise ValueError("`return_text` is mutually exclusive with `return_tensors`")
            return_type = ReturnType.TENSORS
        if return_type is not None: postprocess_params["return_type"] = return_type
        if clean_up_tokenization_spaces is not None: postprocess_params["clean_up_tokenization_spaces"] = clean_up_tokenization_spaces
        if continue_final_message is not None: postprocess_params["continue_final_message"] = continue_final_message
        if stop_sequence is not None:
            stop_sequence_ids = self.tokenizer.encode(stop_sequence, add_special_tokens=False)
            generate_kwargs["eos_token_id"] = stop_sequence_ids[0]
        return preprocess_params, forward_params, postprocess_params
    def _parse_and_tokenize(self, *args, **kwargs):
        if self.model.__class__.__name__ in ["TransfoXLLMHeadModel"]: kwargs.update({"add_space_before_punct_symbol": True})
        return super()._parse_and_tokenize(*args, **kwargs)
    def __call__(self, text_inputs, **kwargs):
        if isinstance(text_inputs, (list, tuple, KeyDataset) if is_torch_available() else (list, tuple)) and isinstance(text_inputs[0], (list, tuple, dict)):
            if isinstance(text_inputs[0], dict): return super().__call__(Chat(text_inputs), **kwargs)
            else:
                chats = [Chat(chat) for chat in text_inputs]  # 🐈 🐈 🐈
                return super().__call__(chats, **kwargs)
        else: return super().__call__(text_inputs, **kwargs)
    def preprocess(self, prompt_text, prefix="", handle_long_generation=None, add_special_tokens=None, truncation=None, padding=None, max_length=None, continue_final_message=None, **generate_kwargs):
        tokenizer_kwargs = {"add_special_tokens": add_special_tokens, "truncation": truncation, "padding": padding, "max_length": max_length}
        tokenizer_kwargs = {key: value for key, value in tokenizer_kwargs.items() if value is not None}
        if isinstance(prompt_text, Chat):
            tokenizer_kwargs.pop("add_special_tokens", None)
            if continue_final_message is None: continue_final_message = prompt_text.messages[-1]["role"] == "assistant"
            inputs = self.tokenizer.apply_chat_template(prompt_text.messages, add_generation_prompt=not continue_final_message, continue_final_message=continue_final_message, return_dict=True, return_tensors=self.framework, **tokenizer_kwargs)
        else: inputs = self.tokenizer(prefix + prompt_text, return_tensors=self.framework, **tokenizer_kwargs)
        inputs["prompt_text"] = prompt_text
        if handle_long_generation == "hole":
            cur_len = inputs["input_ids"].shape[-1]
            if "max_new_tokens" in generate_kwargs: new_tokens = generate_kwargs["max_new_tokens"]
            else:
                new_tokens = generate_kwargs.get("max_length", self.generation_config.max_length) - cur_len
                if new_tokens < 0: raise ValueError("We cannot infer how many new tokens are expected")
            if cur_len + new_tokens > self.tokenizer.model_max_length:
                keep_length = self.tokenizer.model_max_length - new_tokens
                if keep_length <= 0: raise ValueError("We cannot use `hole` to handle this generation the number of desired tokens exceeds the models max length")
                inputs["input_ids"] = inputs["input_ids"][:, -keep_length:]
                if "attention_mask" in inputs: inputs["attention_mask"] = inputs["attention_mask"][:, -keep_length:]
        return inputs
    def _forward(self, model_inputs, **generate_kwargs):
        input_ids = model_inputs["input_ids"]
        attention_mask = model_inputs.get("attention_mask", None)
        if input_ids.shape[1] == 0:
            input_ids = None
            attention_mask = None
            in_b = 1
        else: in_b = input_ids.shape[0]
        prompt_text = model_inputs.pop("prompt_text")
        prefix_length = generate_kwargs.pop("prefix_length", 0)
        if prefix_length > 0:
            has_max_new_tokens = "max_new_tokens" in generate_kwargs or ("generation_config" in generate_kwargs and generate_kwargs["generation_config"].max_new_tokens is not None)
            if not has_max_new_tokens:
                generate_kwargs["max_length"] = generate_kwargs.get("max_length") or self.generation_config.max_length
                generate_kwargs["max_length"] += prefix_length
            has_min_new_tokens = "min_new_tokens" in generate_kwargs or ("generation_config" in generate_kwargs and generate_kwargs["generation_config"].min_new_tokens is not None)
            if not has_min_new_tokens and "min_length" in generate_kwargs: generate_kwargs["min_length"] += prefix_length
        if "generation_config" not in generate_kwargs: generate_kwargs["generation_config"] = self.generation_config
        generated_sequence = self.model.generate(input_ids=input_ids, attention_mask=attention_mask, **generate_kwargs)
        out_b = generated_sequence.shape[0]
        if self.framework == "pt": generated_sequence = generated_sequence.reshape(in_b, out_b // in_b, *generated_sequence.shape[1:])
        elif self.framework == "tf": generated_sequence = tf.reshape(generated_sequence, (in_b, out_b // in_b, *generated_sequence.shape[1:]))
        return {"generated_sequence": generated_sequence, "input_ids": input_ids, "prompt_text": prompt_text}
    def postprocess(self, model_outputs, return_type=ReturnType.FULL_TEXT, clean_up_tokenization_spaces=True, continue_final_message=None):
        generated_sequence = model_outputs["generated_sequence"][0]
        input_ids = model_outputs["input_ids"]
        prompt_text = model_outputs["prompt_text"]
        generated_sequence = generated_sequence.numpy().tolist()
        records = []
        for sequence in generated_sequence:
            if return_type == ReturnType.TENSORS: record = {"generated_token_ids": sequence}
            elif return_type in {ReturnType.NEW_TEXT, ReturnType.FULL_TEXT}:
                text = self.tokenizer.decode(sequence, skip_special_tokens=True, clean_up_tokenization_spaces=clean_up_tokenization_spaces)
                if input_ids is None: prompt_length = 0
                else: prompt_length = len(self.tokenizer.decode(input_ids[0], skip_special_tokens=True, clean_up_tokenization_spaces=clean_up_tokenization_spaces))
                all_text = text[prompt_length:]
                if return_type == ReturnType.FULL_TEXT:
                    if isinstance(prompt_text, str): all_text = prompt_text + all_text
                    elif isinstance(prompt_text, Chat):
                        if continue_final_message is None: continue_final_message = prompt_text.messages[-1]["role"] == "assistant"
                        if continue_final_message: all_text = list(prompt_text.messages)[:-1] + [{"role": prompt_text.messages[-1]["role"], "content": prompt_text.messages[-1]["content"] + all_text}]
                        else: all_text = list(prompt_text.messages) + [{"role": "assistant", "content": all_text}]
                record = {"generated_text": all_text}
            records.append(record)
        return records
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
