"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from collections import OrderedDict
from typing import Any, Mapping, Optional, Union
from ...configuration_utils import PretrainedConfig
from ...feature_extraction_utils import FeatureExtractionMixin
from ...onnx import OnnxConfig
from ...onnx.utils import compute_effective_axis_dimension
from ...tokenization_utils_base import PreTrainedTokenizerBase
from ...utils import TensorType, logging
logger = logging.get_logger(__name__)
class PerceiverConfig(PretrainedConfig):
    model_type = "perceiver"
    def __init__(self, num_latents=256, d_latents=1280, d_model=768, num_blocks=1, num_self_attends_per_block=26, num_self_attention_heads=8, num_cross_attention_heads=8,
    qk_channels=None, v_channels=None, cross_attention_shape_for_attention="kv", self_attention_widening_factor=1, cross_attention_widening_factor=1, hidden_act="gelu",
    attention_probs_dropout_prob=0.1, initializer_range=0.02, layer_norm_eps=1e-12, use_query_residual=True, vocab_size=262, max_position_embeddings=2048, image_size=56,
    train_size=[368, 496], num_frames=16, audio_samples_per_frame=1920, samples_per_patch=16, output_shape=[1, 16, 224, 224], output_num_channels=512,
    _label_trainable_num_channels=1024, **kwargs):
        super().__init__(**kwargs)
        self.num_latents = num_latents
        self.d_latents = d_latents
        self.d_model = d_model
        self.num_blocks = num_blocks
        self.num_self_attends_per_block = num_self_attends_per_block
        self.num_self_attention_heads = num_self_attention_heads
        self.num_cross_attention_heads = num_cross_attention_heads
        self.qk_channels = qk_channels
        self.v_channels = v_channels
        self.cross_attention_shape_for_attention = cross_attention_shape_for_attention
        self.self_attention_widening_factor = self_attention_widening_factor
        self.cross_attention_widening_factor = cross_attention_widening_factor
        self.hidden_act = hidden_act
        self.attention_probs_dropout_prob = attention_probs_dropout_prob
        self.initializer_range = initializer_range
        self.layer_norm_eps = layer_norm_eps
        self.use_query_residual = use_query_residual
        self.vocab_size = vocab_size
        self.max_position_embeddings = max_position_embeddings
        self.image_size = image_size
        self.train_size = train_size
        self.num_frames = num_frames
        self.audio_samples_per_frame = audio_samples_per_frame
        self.samples_per_patch = samples_per_patch
        self.output_shape = output_shape
        self.output_num_channels = output_num_channels
        self._label_trainable_num_channels = _label_trainable_num_channels
class PerceiverOnnxConfig(OnnxConfig):
    @property
    def inputs(self) -> Mapping[str, Mapping[int, str]]:
        if self.task == "multiple-choice": dynamic_axis = {0: "batch", 1: "choice", 2: "sequence"}
        else: dynamic_axis = {0: "batch", 1: "sequence"}
        return OrderedDict([("inputs", dynamic_axis), ("attention_mask", dynamic_axis)])
    @property
    def atol_for_validation(self) -> float: return 1e-4
    def generate_dummy_inputs(self, preprocessor: Union["PreTrainedTokenizerBase", "FeatureExtractionMixin"], batch_size: int = -1, seq_length: int = -1, num_choices: int = -1,
    is_pair: bool = False, framework: Optional[TensorType] = None, num_channels: int = 3, image_width: int = 40, image_height: int = 40) -> Mapping[str, Any]:
        if isinstance(preprocessor, PreTrainedTokenizerBase):
            batch_size = compute_effective_axis_dimension(batch_size, fixed_dimension=OnnxConfig.default_fixed_batch, num_token_to_add=0)
            token_to_add = preprocessor.num_special_tokens_to_add(is_pair)
            seq_length = compute_effective_axis_dimension(seq_length, fixed_dimension=OnnxConfig.default_fixed_sequence, num_token_to_add=token_to_add)
            dummy_input = [" ".join(["a"]) * seq_length] * batch_size
            inputs = dict(preprocessor(dummy_input, return_tensors=framework))
            inputs["inputs"] = inputs.pop("input_ids")
            return inputs
        elif isinstance(preprocessor, FeatureExtractionMixin) and preprocessor.model_input_names[0] == "pixel_values":
            batch_size = compute_effective_axis_dimension(batch_size, fixed_dimension=OnnxConfig.default_fixed_batch)
            dummy_input = self._generate_dummy_images(batch_size, num_channels, image_height, image_width)
            inputs = dict(preprocessor(images=dummy_input, return_tensors=framework))
            inputs["inputs"] = inputs.pop("pixel_values")
            return inputs
        else: raise ValueError("Unable to generate dummy inputs for the model. Please provide a tokenizer or a preprocessor.")
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
