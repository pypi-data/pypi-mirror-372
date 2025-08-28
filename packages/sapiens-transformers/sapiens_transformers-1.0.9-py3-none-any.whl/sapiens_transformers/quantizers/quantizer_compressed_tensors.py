"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ..utils import is_compressed_tensors_available, is_torch_available, logging
from ..utils.quantization_config import QuantizationConfigMixin
from .base import HfQuantizer
if is_torch_available(): import torch
logger = logging.get_logger(__name__)
class CompressedTensorsHfQuantizer(HfQuantizer):
    requires_calibration = True
    required_packages = ["compressed_tensors"]
    def __init__(self, quantization_config: QuantizationConfigMixin, **kwargs):
        super().__init__(quantization_config, **kwargs)
        from compressed_tensors.compressors import ModelCompressor
        self.compressor = ModelCompressor.from_compression_config(quantization_config)
    def validate_environment(self, *args, **kwargs):
        if not is_compressed_tensors_available(): raise ImportError("Using `compressed_tensors` quantized models requires the compressed-tensors library: `pip install compressed-tensors`")
        if not is_torch_available(): raise ImportError("torch is required for using compressed-tensors quantization")
    def update_torch_dtype(self, torch_dtype: "torch.dtype") -> "torch.dtype":
        if torch_dtype is None:
            logger.info("Loading model using torch.float16 for compressed-tensors quantization")
            torch_dtype = torch.float16
        elif torch_dtype != torch.float16: logger.info("We suggest you to set `torch_dtype=torch.float16` for better efficiency with compressed_tensors.")
        return torch_dtype
    def _process_model_before_weight_loading(self, model, **kwargs):
        from compressed_tensors.quantization import apply_quantization_config
        ct_quantization_config = self.compressor.quantization_config
        apply_quantization_config(model, ct_quantization_config, run_compressed=True)
    def _process_model_after_weight_loading(self, model, **kwargs): pass
    @property
    def is_trainable(self): return False
    @property
    def is_serializable(self): return False
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
