"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from collections import OrderedDict
from typing import TYPE_CHECKING, Any, Mapping, Optional
from ...configuration_utils import PretrainedConfig
from ...onnx import OnnxConfig
from ...utils import logging
if TYPE_CHECKING: from ... import FeatureExtractionMixin, TensorType
logger = logging.get_logger(__name__)
class ImageGPTConfig(PretrainedConfig):
    model_type = "imagegpt"
    keys_to_ignore_at_inference = ["past_key_values"]
    attribute_map = {'hidden_size': 'n_embd', 'max_position_embeddings': 'n_positions', 'num_attention_heads': 'n_head', 'num_hidden_layers': 'n_layer'}
    def __init__(self, vocab_size=512 + 1, n_positions=32 * 32, n_embd=512, n_layer=24, n_head=8, n_inner=None, activation_function="quick_gelu", resid_pdrop=0.1,
    embd_pdrop=0.1, attn_pdrop=0.1, layer_norm_epsilon=1e-5, initializer_range=0.02, scale_attn_weights=True, use_cache=True, tie_word_embeddings=False,
    scale_attn_by_inverse_layer_idx=False, reorder_and_upcast_attn=False, **kwargs):
        self.vocab_size = vocab_size
        self.n_positions = n_positions
        self.n_embd = n_embd
        self.n_layer = n_layer
        self.n_head = n_head
        self.n_inner = n_inner
        self.activation_function = activation_function
        self.resid_pdrop = resid_pdrop
        self.embd_pdrop = embd_pdrop
        self.attn_pdrop = attn_pdrop
        self.layer_norm_epsilon = layer_norm_epsilon
        self.initializer_range = initializer_range
        self.scale_attn_weights = scale_attn_weights
        self.use_cache = use_cache
        self.scale_attn_by_inverse_layer_idx = scale_attn_by_inverse_layer_idx
        self.reorder_and_upcast_attn = reorder_and_upcast_attn
        self.tie_word_embeddings = tie_word_embeddings
        super().__init__(tie_word_embeddings=tie_word_embeddings, **kwargs)
class ImageGPTOnnxConfig(OnnxConfig):
    @property
    def inputs(self) -> Mapping[str, Mapping[int, str]]: return OrderedDict([("input_ids", {0: "batch", 1: "sequence"})])
    def generate_dummy_inputs(self, preprocessor: "FeatureExtractionMixin", batch_size: int = 1, seq_length: int = -1, is_pair: bool = False, framework: Optional["TensorType"] = None,
    num_channels: int = 3, image_width: int = 32, image_height: int = 32) -> Mapping[str, Any]:
        input_image = self._generate_dummy_images(batch_size, num_channels, image_height, image_width)
        inputs = dict(preprocessor(images=input_image, return_tensors=framework))
        return inputs
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
