"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...configuration_utils import PRETRAINED_SAPIENS_TECHNOLOGY as SapiensTechnologyForPretraining
from .sapi_music_import_variables import SapiensTechnologyOptional, TARGET_BANDWIDTHS, UPSAMPLING_RATIOS
class SAPIMusicConfig(SapiensTechnologyForPretraining):
    model_type = "sapi_music"
    def __init__(self, target_bandwidths=TARGET_BANDWIDTHS, sampling_rate=48000, audio_channels=2, normalize=False, chunk_length_s=None, overlap=None,
    hidden_size=256, num_filters=64, num_residual_layers=2, upsampling_ratios=UPSAMPLING_RATIOS, norm_type="weight_norm", kernel_size=14, last_kernel_size=14,
    residual_kernel_size=6, dilation_growth_rate=4, use_causal_conv=True, pad_mode="reflect", compress=4, num_lstm_layers=4, trim_right_ratio=2.0,
    codebook_size=2048, codebook_dim=None, use_conv_shortcut=True, **kwargs):
        self.target_bandwidths = target_bandwidths if type(target_bandwidths) in (tuple, list) else TARGET_BANDWIDTHS
        self.sampling_rate = sampling_rate if type(sampling_rate) in (int, float) else 48000
        self.audio_channels = audio_channels if type(audio_channels) in (int, float) else 2
        self.normalize = normalize if type(normalize) in (bool, int, float) else False
        self.chunk_length_s = chunk_length_s
        self.overlap = overlap
        self.hidden_size = hidden_size if type(hidden_size) in (int, float) else 256
        self.num_filters = num_filters if type(num_filters) in (int, float) else 64
        self.num_residual_layers = num_residual_layers if type(num_residual_layers) in (int, float) else 2
        self.upsampling_ratios = upsampling_ratios if type(upsampling_ratios) in (tuple, list) else UPSAMPLING_RATIOS
        self.norm_type = norm_type if type(norm_type) == str else "weight_norm"
        self.kernel_size = kernel_size if type(kernel_size) in (int, float) else 14
        self.last_kernel_size = last_kernel_size if type(last_kernel_size) in (int, float) else 14
        self.residual_kernel_size = residual_kernel_size if type(residual_kernel_size) in (int, float) else 6
        self.dilation_growth_rate = dilation_growth_rate if type(dilation_growth_rate) in (int, float) else 4
        self.use_causal_conv = use_causal_conv if type(use_causal_conv) in (bool, int, float) else True
        self.pad_mode = pad_mode if type(pad_mode) == str else "reflect"
        self.compress = compress if type(compress) in (int, float) else 4
        self.num_lstm_layers = num_lstm_layers if type(num_lstm_layers) in (int, float) else 4
        self.trim_right_ratio = trim_right_ratio if type(trim_right_ratio) in (int, float) else 2.0
        self.codebook_size = codebook_size if type(codebook_size) in (int, float) else 2048
        self.codebook_dim = codebook_dim if codebook_dim is not None else hidden_size
        self.use_conv_shortcut = use_conv_shortcut if type(use_conv_shortcut) in (bool, int, float) else True
        if self.norm_type not in ["weight_norm", "time_group_norm"]: raise ValueError(f'self.norm_type must be one of `"weight_norm"`, `"time_group_norm"`), got {self.norm_type}')
        super().__init__(**kwargs)
    @property
    def frame_rate(self) -> int:
        from math import ceil
        from numpy import prod
        return ceil(self.sampling_rate / prod(self.upsampling_ratios))
    @property
    def chunk_length(self) -> SapiensTechnologyOptional[int]: return None if self.chunk_length_s is None else int(self.chunk_length_s * self.sampling_rate)
    @property
    def chunk_stride(self) -> SapiensTechnologyOptional[int]: return None if self.chunk_length_s is None or self.overlap is None else max(1, int((1.0 - self.overlap) * self.chunk_length))
    @property
    def num_quantizers(self) -> int: return int(1000 * self.target_bandwidths[-1] // (self.frame_rate * 10))
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
