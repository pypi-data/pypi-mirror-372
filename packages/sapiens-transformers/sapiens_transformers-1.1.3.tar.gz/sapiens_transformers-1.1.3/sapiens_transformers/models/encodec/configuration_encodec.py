"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import math
from typing import Optional
import numpy as np
from ...configuration_utils import PretrainedConfig
from ...utils import logging
logger = logging.get_logger(__name__)
class EncodecConfig(PretrainedConfig):
    model_type = "encodec"
    def __init__(self, target_bandwidths=[1.5, 3.0, 6.0, 12.0, 24.0], sampling_rate=24_000, audio_channels=1, normalize=False, chunk_length_s=None, overlap=None,
    hidden_size=128, num_filters=32, num_residual_layers=1, upsampling_ratios=[8, 5, 4, 2], norm_type="weight_norm", kernel_size=7, last_kernel_size=7,
    residual_kernel_size=3, dilation_growth_rate=2, use_causal_conv=True, pad_mode="reflect", compress=2, num_lstm_layers=2, trim_right_ratio=1.0,
    codebook_size=1024, codebook_dim=None, use_conv_shortcut=True, **kwargs):
        self.target_bandwidths = target_bandwidths
        self.sampling_rate = sampling_rate
        self.audio_channels = audio_channels
        self.normalize = normalize
        self.chunk_length_s = chunk_length_s
        self.overlap = overlap
        self.hidden_size = hidden_size
        self.num_filters = num_filters
        self.num_residual_layers = num_residual_layers
        self.upsampling_ratios = upsampling_ratios
        self.norm_type = norm_type
        self.kernel_size = kernel_size
        self.last_kernel_size = last_kernel_size
        self.residual_kernel_size = residual_kernel_size
        self.dilation_growth_rate = dilation_growth_rate
        self.use_causal_conv = use_causal_conv
        self.pad_mode = pad_mode
        self.compress = compress
        self.num_lstm_layers = num_lstm_layers
        self.trim_right_ratio = trim_right_ratio
        self.codebook_size = codebook_size
        self.codebook_dim = codebook_dim if codebook_dim is not None else hidden_size
        self.use_conv_shortcut = use_conv_shortcut
        if self.norm_type not in ["weight_norm", "time_group_norm"]: raise ValueError(f'self.norm_type must be one of `"weight_norm"`, `"time_group_norm"`), got {self.norm_type}')
        super().__init__(**kwargs)
    @property
    def chunk_length(self) -> Optional[int]:
        if self.chunk_length_s is None: return None
        else: return int(self.chunk_length_s * self.sampling_rate)
    @property
    def chunk_stride(self) -> Optional[int]:
        if self.chunk_length_s is None or self.overlap is None: return None
        else: return max(1, int((1.0 - self.overlap) * self.chunk_length))
    @property
    def frame_rate(self) -> int:
        hop_length = np.prod(self.upsampling_ratios)
        return math.ceil(self.sampling_rate / hop_length)
    @property
    def num_quantizers(self) -> int: return int(1000 * self.target_bandwidths[-1] // (self.frame_rate * 10))
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
