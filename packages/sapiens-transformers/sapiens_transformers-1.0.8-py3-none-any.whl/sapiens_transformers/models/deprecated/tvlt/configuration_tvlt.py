"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ....configuration_utils import PretrainedConfig
from ....utils import logging
logger = logging.get_logger(__name__)
class TvltConfig(PretrainedConfig):
    model_type = "tvlt"
    def __init__(self, image_size=224, spectrogram_length=2048, frequency_length=128, image_patch_size=[16, 16], audio_patch_size=[16, 16], num_image_channels=3, num_audio_channels=1,
    num_frames=8, hidden_size=768, num_hidden_layers=12, num_attention_heads=12, intermediate_size=3072, hidden_act="gelu", hidden_dropout_prob=0.0, attention_probs_dropout_prob=0.0,
    initializer_range=0.02, layer_norm_eps=1e-6, qkv_bias=True, use_mean_pooling=False, decoder_num_attention_heads=16, decoder_hidden_size=512, decoder_num_hidden_layers=8,
    decoder_intermediate_size=2048, pixel_mask_ratio=0.75, audio_mask_ratio=0.15, audio_mask_type="frame-level", task_matching=True, task_mae=True, loss_type="classification", **kwargs):
        super().__init__(**kwargs)
        if audio_mask_type not in ("frame-level", "patch_level"): raise ValueError("audio_mask_type must be one of two acceptable strategies - {'frame_level', 'patch-level') "+f"got {audio_mask_type}")
        self.image_size = image_size
        self.spectrogram_length = spectrogram_length
        self.frequency_length = frequency_length
        self.image_patch_size = image_patch_size
        self.audio_patch_size = audio_patch_size
        self.num_image_channels = num_image_channels
        self.num_audio_channels = num_audio_channels
        self.num_frames = num_frames
        self.hidden_size = hidden_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.intermediate_size = intermediate_size
        self.hidden_act = hidden_act
        self.hidden_dropout_prob = hidden_dropout_prob
        self.attention_probs_dropout_prob = attention_probs_dropout_prob
        self.initializer_range = initializer_range
        self.layer_norm_eps = layer_norm_eps
        self.qkv_bias = qkv_bias
        self.use_mean_pooling = use_mean_pooling
        self.decoder_num_attention_heads = decoder_num_attention_heads
        self.decoder_hidden_size = decoder_hidden_size
        self.decoder_num_hidden_layers = decoder_num_hidden_layers
        self.decoder_intermediate_size = decoder_intermediate_size
        self.pixel_mask_ratio = pixel_mask_ratio
        self.audio_mask_ratio = audio_mask_ratio
        self.audio_mask_type = audio_mask_type
        self.task_matching = task_matching
        self.task_mae = task_mae
        self.loss_type = loss_type
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
