"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...utils import logging
from ..t5.modeling_tf_t5 import TFT5EncoderModel, TFT5ForConditionalGeneration, TFT5Model
from .configuration_mt5 import MT5Config
logger = logging.get_logger(__name__)
_CONFIG_FOR_DOC = "T5Config"
class TFMT5Model(TFT5Model):
    model_type = "mt5"
    config_class = MT5Config
class TFMT5ForConditionalGeneration(TFT5ForConditionalGeneration):
    model_type = "mt5"
    config_class = MT5Config
class TFMT5EncoderModel(TFT5EncoderModel):
    model_type = "mt5"
    config_class = MT5Config
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
