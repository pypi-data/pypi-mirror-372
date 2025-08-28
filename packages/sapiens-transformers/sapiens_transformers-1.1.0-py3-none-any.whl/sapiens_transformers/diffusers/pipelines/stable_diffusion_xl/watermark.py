'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import numpy as np
import torch
from ...utils import is_invisible_watermark_available
if is_invisible_watermark_available(): from imwatermark import WatermarkEncoder
WATERMARK_MESSAGE = 197828617679262
WATERMARK_BITS = [int(bit) for bit in bin(WATERMARK_MESSAGE)[2:]]
class StableDiffusionXLWatermarker:
    def __init__(self):
        self.watermark = WATERMARK_BITS
        self.encoder = WatermarkEncoder()
        self.encoder.set_watermark('bits', self.watermark)
    def apply_watermark(self, images: torch.Tensor):
        if images.shape[-1] < 256: return images
        images = (255 * (images / 2 + 0.5)).cpu().permute(0, 2, 3, 1).float().numpy()
        images = images[:, :, :, ::-1]
        images = [self.encoder.encode(image, 'dwtDct')[:, :, ::-1] for image in images]
        images = np.array(images)
        images = torch.from_numpy(images).permute(0, 3, 1, 2)
        images = torch.clamp(2 * (images / 255 - 0.5), min=-1.0, max=1.0)
        return images
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
