"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING, Any, Mapping, Optional, OrderedDict
from packaging import version
from ...configuration_utils import PretrainedConfig
from ...onnx import OnnxConfig
from ...utils import logging
from ..auto.configuration_auto import AutoConfig
if TYPE_CHECKING: from ... import PreTrainedTokenizerBase, TensorType
logger = logging.get_logger(__name__)
class VisionEncoderDecoderConfig(PretrainedConfig):
    model_type = "vision-encoder-decoder"
    is_composition = True
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if "encoder" not in kwargs or "decoder" not in kwargs: raise ValueError(f"A configuraton of type {self.model_type} cannot be instantiated because not both `encoder` and `decoder` sub-configurations are passed, but only {kwargs}")
        encoder_config = kwargs.pop("encoder")
        encoder_model_type = encoder_config.pop("model_type")
        decoder_config = kwargs.pop("decoder")
        decoder_model_type = decoder_config.pop("model_type")
        self.encoder = AutoConfig.for_model(encoder_model_type, **encoder_config)
        self.decoder = AutoConfig.for_model(decoder_model_type, **decoder_config)
        self.is_encoder_decoder = True
    @classmethod
    def from_encoder_decoder_configs(cls, encoder_config: PretrainedConfig, decoder_config: PretrainedConfig, **kwargs) -> PretrainedConfig:
        logger.info("Setting `config.is_decoder=True` and `config.add_cross_attention=True` for decoder_config")
        decoder_config.is_decoder = True
        decoder_config.add_cross_attention = True
        return cls(encoder=encoder_config.to_dict(), decoder=decoder_config.to_dict(), **kwargs)
class VisionEncoderDecoderEncoderOnnxConfig(OnnxConfig):
    torch_onnx_minimum_version = version.parse("1.11")
    @property
    def inputs(self) -> Mapping[str, Mapping[int, str]]: return OrderedDict([("pixel_values", {0: "batch", 1: "num_channels", 2: "height", 3: "width"})])
    @property
    def atol_for_validation(self) -> float: return 1e-4
    @property
    def outputs(self) -> Mapping[str, Mapping[int, str]]: return OrderedDict({"last_hidden_state": {0: "batch", 1: "encoder_sequence"}})
class VisionEncoderDecoderDecoderOnnxConfig(OnnxConfig):
    @property
    def inputs(self) -> Mapping[str, Mapping[int, str]]:
        common_inputs = OrderedDict()
        common_inputs["input_ids"] = {0: "batch", 1: "past_decoder_sequence + sequence"}
        common_inputs["attention_mask"] = {0: "batch", 1: "past_decoder_sequence + sequence"}
        common_inputs["encoder_hidden_states"] = {0: "batch", 1: "encoder_sequence"}
        return common_inputs
    def generate_dummy_inputs(self, tokenizer: "PreTrainedTokenizerBase", batch_size: int = -1, seq_length: int = -1, is_pair: bool = False, framework: Optional["TensorType"] = None) -> Mapping[str, Any]:
        import torch
        common_inputs = OrderedDict()
        dummy_input = super().generate_dummy_inputs(tokenizer, batch_size=batch_size, seq_length=seq_length, is_pair=is_pair, framework=framework)
        batch, encoder_sequence = dummy_input["input_ids"].shape
        encoder_hidden_states_shape = (batch, encoder_sequence, self._config.encoder_hidden_size)
        common_inputs["input_ids"] = dummy_input.pop("input_ids")
        common_inputs["attention_mask"] = dummy_input.pop("attention_mask")
        common_inputs["encoder_hidden_states"] = torch.zeros(encoder_hidden_states_shape)
        return common_inputs
class VisionEncoderDecoderOnnxConfig(OnnxConfig):
    @property
    def inputs(self) -> None: pass
    def get_encoder_config(self, encoder_config: PretrainedConfig) -> OnnxConfig: return VisionEncoderDecoderEncoderOnnxConfig(encoder_config)
    def get_decoder_config(self, encoder_config: PretrainedConfig, decoder_config: PretrainedConfig, feature: str = "default") -> OnnxConfig:
        decoder_config.encoder_hidden_size = encoder_config.hidden_size
        return VisionEncoderDecoderDecoderOnnxConfig(decoder_config, feature)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
