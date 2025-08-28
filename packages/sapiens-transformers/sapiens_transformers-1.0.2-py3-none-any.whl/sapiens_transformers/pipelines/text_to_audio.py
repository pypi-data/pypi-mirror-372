"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import List, Union
from ..utils import is_torch_available
from .base import Pipeline
if is_torch_available():
    from ..models.auto.modeling_auto import MODEL_FOR_TEXT_TO_SPECTROGRAM_MAPPING
    from ..models.speecht5.modeling_speecht5 import SpeechT5HifiGan
DEFAULT_VOCODER_ID = "microsoft/speecht5_hifigan"
class TextToAudioPipeline(Pipeline):
    def __init__(self, *args, vocoder=None, sampling_rate=None, **kwargs):
        super().__init__(*args, **kwargs)
        if self.framework == "tf": raise ValueError("The TextToAudioPipeline is only available in PyTorch.")
        self.vocoder = None
        if self.model.__class__ in MODEL_FOR_TEXT_TO_SPECTROGRAM_MAPPING.values(): self.vocoder = (SpeechT5HifiGan.from_pretrained(DEFAULT_VOCODER_ID).to(self.model.device) if vocoder is None else vocoder)
        self.sampling_rate = sampling_rate
        if self.vocoder is not None: self.sampling_rate = self.vocoder.config.sampling_rate
        if self.sampling_rate is None:
            config = self.model.config
            gen_config = self.model.__dict__.get("generation_config", None)
            if gen_config is not None: config.update(gen_config.to_dict())
            for sampling_rate_name in ["sample_rate", "sampling_rate"]:
                sampling_rate = getattr(config, sampling_rate_name, None)
                if sampling_rate is not None: self.sampling_rate = sampling_rate
    def preprocess(self, text, **kwargs):
        if isinstance(text, str): text = [text]
        if self.model.config.model_type == "bark":
            new_kwargs = {"max_length": self.generation_config.semantic_config.get("max_input_semantic_length", 256), "add_special_tokens": False, "return_attention_mask": True, "return_token_type_ids": False, "padding": "max_length"}
            new_kwargs.update(kwargs)
            kwargs = new_kwargs
        output = self.tokenizer(text, **kwargs, return_tensors="pt")
        return output
    def _forward(self, model_inputs, **kwargs):
        kwargs = self._ensure_tensor_on_device(kwargs, device=self.device)
        forward_params = kwargs["forward_params"]
        generate_kwargs = kwargs["generate_kwargs"]
        if self.model.can_generate():
            generate_kwargs = self._ensure_tensor_on_device(generate_kwargs, device=self.device)
            if "generation_config" not in generate_kwargs: generate_kwargs["generation_config"] = self.generation_config
            forward_params.update(generate_kwargs)
            output = self.model.generate(**model_inputs, **forward_params)
        else:
            if len(generate_kwargs): raise ValueError(f"You're using the `TextToAudioPipeline` with a forward-only model, but `generate_kwargs` is non empty. For forward-only TTA models, please use `forward_params` instead of of `generate_kwargs`. For reference, here are the `generate_kwargs` used here: {generate_kwargs.keys()}")
            output = self.model(**model_inputs, **forward_params)[0]
        if self.vocoder is not None: output = self.vocoder(output)
        return output
    def __call__(self, text_inputs: Union[str, List[str]], **forward_params): return super().__call__(text_inputs, **forward_params)
    def _sanitize_parameters(self, preprocess_params=None, forward_params=None, generate_kwargs=None):
        params = {"forward_params": forward_params if forward_params else {}, "generate_kwargs": generate_kwargs if generate_kwargs else {}}
        if preprocess_params is None: preprocess_params = {}
        postprocess_params = {}
        return preprocess_params, params, postprocess_params
    def postprocess(self, waveform):
        output_dict = {}
        if isinstance(waveform, dict): waveform = waveform["waveform"]
        elif isinstance(waveform, tuple): waveform = waveform[0]
        output_dict["audio"] = waveform.cpu().float().numpy()
        output_dict["sampling_rate"] = self.sampling_rate
        return output_dict
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
