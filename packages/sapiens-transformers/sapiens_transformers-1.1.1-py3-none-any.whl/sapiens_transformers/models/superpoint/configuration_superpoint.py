"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import List
from ...configuration_utils import PretrainedConfig
from ...utils import logging
logger = logging.get_logger(__name__)
class SuperPointConfig(PretrainedConfig):
    model_type = "superpoint"
    def __init__(self, encoder_hidden_sizes: List[int] = [64, 64, 128, 128], decoder_hidden_size: int = 256, keypoint_decoder_dim: int = 65, descriptor_decoder_dim: int = 256,
    keypoint_threshold: float = 0.005, max_keypoints: int = -1, nms_radius: int = 4, border_removal_distance: int = 4, initializer_range=0.02, **kwargs):
        self.encoder_hidden_sizes = encoder_hidden_sizes
        self.decoder_hidden_size = decoder_hidden_size
        self.keypoint_decoder_dim = keypoint_decoder_dim
        self.descriptor_decoder_dim = descriptor_decoder_dim
        self.keypoint_threshold = keypoint_threshold
        self.max_keypoints = max_keypoints
        self.nms_radius = nms_radius
        self.border_removal_distance = border_removal_distance
        self.initializer_range = initializer_range
        super().__init__(**kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
