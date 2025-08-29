"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from collections import OrderedDict
from typing import TYPE_CHECKING, Any, Mapping, Optional
from packaging import version
from ...configuration_utils import PretrainedConfig
from ...onnx import OnnxConfig
from ...onnx.utils import compute_effective_axis_dimension
from ...utils import logging
if TYPE_CHECKING:
    from ...processing_utils import ProcessorMixin
    from ...utils import TensorType
logger = logging.get_logger(__name__)
class LayoutLMv3Config(PretrainedConfig):
    model_type = "layoutlmv3"
    def __init__(self, vocab_size=50265, hidden_size=768, num_hidden_layers=12, num_attention_heads=12, intermediate_size=3072, hidden_act="gelu", hidden_dropout_prob=0.1,
    attention_probs_dropout_prob=0.1, max_position_embeddings=512, type_vocab_size=2, initializer_range=0.02, layer_norm_eps=1e-5, pad_token_id=1, bos_token_id=0, eos_token_id=2,
    max_2d_position_embeddings=1024, coordinate_size=128, shape_size=128, has_relative_attention_bias=True, rel_pos_bins=32, max_rel_pos=128, rel_2d_pos_bins=64, max_rel_2d_pos=256,
    has_spatial_attention_bias=True, text_embed=True, visual_embed=True, input_size=224, num_channels=3, patch_size=16, classifier_dropout=None, **kwargs):
        super().__init__(vocab_size=vocab_size, hidden_size=hidden_size, num_hidden_layers=num_hidden_layers, num_attention_heads=num_attention_heads, intermediate_size=intermediate_size,
        hidden_act=hidden_act, hidden_dropout_prob=hidden_dropout_prob, attention_probs_dropout_prob=attention_probs_dropout_prob, max_position_embeddings=max_position_embeddings,
        type_vocab_size=type_vocab_size, initializer_range=initializer_range, layer_norm_eps=layer_norm_eps, pad_token_id=pad_token_id, bos_token_id=bos_token_id, eos_token_id=eos_token_id, **kwargs)
        self.max_2d_position_embeddings = max_2d_position_embeddings
        self.coordinate_size = coordinate_size
        self.shape_size = shape_size
        self.has_relative_attention_bias = has_relative_attention_bias
        self.rel_pos_bins = rel_pos_bins
        self.max_rel_pos = max_rel_pos
        self.has_spatial_attention_bias = has_spatial_attention_bias
        self.rel_2d_pos_bins = rel_2d_pos_bins
        self.max_rel_2d_pos = max_rel_2d_pos
        self.text_embed = text_embed
        self.visual_embed = visual_embed
        self.input_size = input_size
        self.num_channels = num_channels
        self.patch_size = patch_size
        self.classifier_dropout = classifier_dropout
class LayoutLMv3OnnxConfig(OnnxConfig):
    torch_onnx_minimum_version = version.parse("1.12")
    @property
    def inputs(self) -> Mapping[str, Mapping[int, str]]:
        if self.task in ["question-answering", "sequence-classification"]:
            return OrderedDict([("input_ids", {0: "batch", 1: "sequence"}), ("attention_mask", {0: "batch", 1: "sequence"}), ("bbox", {0: "batch", 1: "sequence"}),
            ("pixel_values", {0: "batch", 1: "num_channels", 2: "height", 3: "width"})])
        else:
            return OrderedDict([("input_ids", {0: "batch", 1: "sequence"}), ("bbox", {0: "batch", 1: "sequence"}), ("attention_mask", {0: "batch", 1: "sequence"}),
            ("pixel_values", {0: "batch", 1: "num_channels"})])
    @property
    def atol_for_validation(self) -> float: return 1e-5
    @property
    def default_onnx_opset(self) -> int: return 12
    def generate_dummy_inputs(self, processor: "ProcessorMixin", batch_size: int = -1, seq_length: int = -1, is_pair: bool = False, framework: Optional["TensorType"] = None,
    num_channels: int = 3, image_width: int = 40, image_height: int = 40) -> Mapping[str, Any]:
        setattr(processor.image_processor, "apply_ocr", False)
        batch_size = compute_effective_axis_dimension(batch_size, fixed_dimension=OnnxConfig.default_fixed_batch, num_token_to_add=0)
        token_to_add = processor.tokenizer.num_special_tokens_to_add(is_pair)
        seq_length = compute_effective_axis_dimension(seq_length, fixed_dimension=OnnxConfig.default_fixed_sequence, num_token_to_add=token_to_add)
        dummy_text = [[" ".join([processor.tokenizer.unk_token]) * seq_length]] * batch_size
        dummy_bboxes = [[[48, 84, 73, 128]]] * batch_size
        dummy_image = self._generate_dummy_images(batch_size, num_channels, image_height, image_width)
        inputs = dict(processor(dummy_image, text=dummy_text, boxes=dummy_bboxes, return_tensors=framework))
        return inputs
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
