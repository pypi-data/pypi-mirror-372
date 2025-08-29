"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
TARGET_BANDWIDTHS, UPSAMPLING_RATIOS = [1.5, 3.0, 6.0, 12.0, 24.0], [8, 5, 4, 2]
MAPPING_QUANTIZER = {'quantizer.vq.layers.*._codebook.inited': 'quantizer.layers.*.codebook.inited', 'quantizer.vq.layers.*._codebook.cluster_size': 'quantizer.layers.*.codebook.cluster_size',
'quantizer.vq.layers.*._codebook.embed': 'quantizer.layers.*.codebook.embed', 'quantizer.vq.layers.*._codebook.embed_avg': 'quantizer.layers.*.codebook.embed_avg'}
MAPPING_ENCODER = {'encoder.model.0.conv.conv': 'encoder.layers.0.conv', 'encoder.model.1.block.1.conv.conv': 'encoder.layers.1.block.1.conv', 'encoder.model.1.block.3.conv.conv': 'encoder.layers.1.block.3.conv',
'encoder.model.1.shortcut.conv.conv': 'encoder.layers.1.shortcut.conv', 'encoder.model.3.conv.conv': 'encoder.layers.3.conv', 'encoder.model.4.block.1.conv.conv': 'encoder.layers.4.block.1.conv',
'encoder.model.4.block.3.conv.conv': 'encoder.layers.4.block.3.conv', 'encoder.model.4.shortcut.conv.conv': 'encoder.layers.4.shortcut.conv', 'encoder.model.6.conv.conv': 'encoder.layers.6.conv',
'encoder.model.7.block.1.conv.conv': 'encoder.layers.7.block.1.conv', 'encoder.model.7.block.3.conv.conv': 'encoder.layers.7.block.3.conv', 'encoder.model.7.shortcut.conv.conv': 'encoder.layers.7.shortcut.conv',
'encoder.model.9.conv.conv': 'encoder.layers.9.conv', 'encoder.model.10.block.1.conv.conv': 'encoder.layers.10.block.1.conv', 'encoder.model.10.block.3.conv.conv': 'encoder.layers.10.block.3.conv',
'encoder.model.10.shortcut.conv.conv': 'encoder.layers.10.shortcut.conv', 'encoder.model.12.conv.conv': 'encoder.layers.12.conv', 'encoder.model.13.lstm': 'encoder.layers.13.lstm', 'encoder.model.15.conv.conv': 'encoder.layers.15.conv'}
MAPPING_ENCODER_48K = {'encoder.model.0.conv.norm': 'encoder.layers.0.norm', 'encoder.model.1.block.1.conv.norm': 'encoder.layers.1.block.1.norm', 'encoder.model.1.block.3.conv.norm': 'encoder.layers.1.block.3.norm',
'encoder.model.1.shortcut.conv.norm': 'encoder.layers.1.shortcut.norm', 'encoder.model.3.conv.norm': 'encoder.layers.3.norm', 'encoder.model.4.block.1.conv.norm': 'encoder.layers.4.block.1.norm',
'encoder.model.4.block.3.conv.norm': 'encoder.layers.4.block.3.norm', 'encoder.model.4.shortcut.conv.norm': 'encoder.layers.4.shortcut.norm', 'encoder.model.6.conv.norm': 'encoder.layers.6.norm',
'encoder.model.7.block.1.conv.norm': 'encoder.layers.7.block.1.norm', 'encoder.model.7.block.3.conv.norm': 'encoder.layers.7.block.3.norm', 'encoder.model.7.shortcut.conv.norm': 'encoder.layers.7.shortcut.norm',
'encoder.model.9.conv.norm': 'encoder.layers.9.norm', 'encoder.model.10.block.1.conv.norm': 'encoder.layers.10.block.1.norm', 'encoder.model.10.block.3.conv.norm': 'encoder.layers.10.block.3.norm',
'encoder.model.10.shortcut.conv.norm': 'encoder.layers.10.shortcut.norm', 'encoder.model.12.conv.norm': 'encoder.layers.12.norm', 'encoder.model.15.conv.norm': 'encoder.layers.15.norm'}
MAPPING_DECODER = {'decoder.model.0.conv.conv': 'decoder.layers.0.conv', 'decoder.model.1.lstm': 'decoder.layers.1.lstm', 'decoder.model.3.convtr.convtr': 'decoder.layers.3.conv',
'decoder.model.4.block.1.conv.conv': 'decoder.layers.4.block.1.conv', 'decoder.model.4.block.3.conv.conv': 'decoder.layers.4.block.3.conv', 'decoder.model.4.shortcut.conv.conv': 'decoder.layers.4.shortcut.conv',
'decoder.model.6.convtr.convtr': 'decoder.layers.6.conv', 'decoder.model.7.block.1.conv.conv': 'decoder.layers.7.block.1.conv', 'decoder.model.7.block.3.conv.conv': 'decoder.layers.7.block.3.conv',
'decoder.model.7.shortcut.conv.conv': 'decoder.layers.7.shortcut.conv', 'decoder.model.9.convtr.convtr': 'decoder.layers.9.conv', 'decoder.model.10.block.1.conv.conv': 'decoder.layers.10.block.1.conv',
'decoder.model.10.block.3.conv.conv': 'decoder.layers.10.block.3.conv', 'decoder.model.10.shortcut.conv.conv': 'decoder.layers.10.shortcut.conv', 'decoder.model.12.convtr.convtr': 'decoder.layers.12.conv',
'decoder.model.13.block.1.conv.conv': 'decoder.layers.13.block.1.conv', 'decoder.model.13.block.3.conv.conv': 'decoder.layers.13.block.3.conv', 'decoder.model.13.shortcut.conv.conv': 'decoder.layers.13.shortcut.conv',
'decoder.model.15.conv.conv': 'decoder.layers.15.conv'}
MAPPING_DECODER_48K = {'decoder.model.0.conv.norm': 'decoder.layers.0.norm', 'decoder.model.3.convtr.norm': 'decoder.layers.3.norm', 'decoder.model.4.block.1.conv.norm': 'decoder.layers.4.block.1.norm',
'decoder.model.4.block.3.conv.norm': 'decoder.layers.4.block.3.norm', 'decoder.model.4.shortcut.conv.norm': 'decoder.layers.4.shortcut.norm', 'decoder.model.6.convtr.norm': 'decoder.layers.6.norm',
'decoder.model.7.block.1.conv.norm': 'decoder.layers.7.block.1.norm', 'decoder.model.7.block.3.conv.norm': 'decoder.layers.7.block.3.norm', 'decoder.model.7.shortcut.conv.norm': 'decoder.layers.7.shortcut.norm',
'decoder.model.9.convtr.norm': 'decoder.layers.9.norm', 'decoder.model.10.block.1.conv.norm': 'decoder.layers.10.block.1.norm', 'decoder.model.10.block.3.conv.norm': 'decoder.layers.10.block.3.norm',
'decoder.model.10.shortcut.conv.norm': 'decoder.layers.10.shortcut.norm', 'decoder.model.12.convtr.norm': 'decoder.layers.12.norm', 'decoder.model.13.block.1.conv.norm': 'decoder.layers.13.block.1.norm',
'decoder.model.13.block.3.conv.norm': 'decoder.layers.13.block.3.norm', 'decoder.model.13.shortcut.conv.norm': 'decoder.layers.13.shortcut.norm', 'decoder.model.15.conv.norm': 'decoder.layers.15.norm'}
from typing import Optional as SapiensTechnologyOptional
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
