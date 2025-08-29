'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ..utils import DummyObject, requires_backends
class AllegroPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class AltDiffusionImg2ImgPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class AltDiffusionPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class AmusedImg2ImgPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class AmusedInpaintPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class AmusedPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class AnimateDiffControlNetPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class AnimateDiffPAGPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class AnimateDiffPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class AnimateDiffSDXLPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class AnimateDiffSparseControlNetPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class AnimateDiffVideoToVideoControlNetPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class AnimateDiffVideoToVideoPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class AudioLDM2Pipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class AudioLDM2ProjectionModel(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class AudioLDM2UNet2DConditionModel(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class AudioLDMPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class AuraFlowPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class CLIPImageProjection(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class CogVideoXFunControlPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class CogVideoXImageToVideoPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class CogVideoXPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class CogVideoXVideoToVideoPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class CogView3PlusPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class CycleDiffusionPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class FluxControlImg2ImgPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class FluxControlInpaintPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class FluxControlNetImg2ImgPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class FluxControlNetInpaintPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class FluxControlNetPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class FluxControlPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class FluxFillPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class FluxImg2ImgPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class FluxInpaintPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class FluxPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class FluxPriorReduxPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class HunyuanDiTControlNetPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class HunyuanDiTPAGPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class HunyuanDiTPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class HunyuanVideoPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class I2VGenXLPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class IFImg2ImgPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class IFImg2ImgSuperResolutionPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class IFInpaintingPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class IFInpaintingSuperResolutionPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class IFPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class IFSuperResolutionPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class ImageTextPipelineOutput(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class Kandinsky3Img2ImgPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class Kandinsky3Pipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class KandinskyCombinedPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class KandinskyImg2ImgCombinedPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class KandinskyImg2ImgPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class KandinskyInpaintCombinedPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class KandinskyInpaintPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class KandinskyPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class KandinskyPriorPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class KandinskyV22CombinedPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class KandinskyV22ControlnetImg2ImgPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class KandinskyV22ControlnetPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class KandinskyV22Img2ImgCombinedPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class KandinskyV22Img2ImgPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class KandinskyV22InpaintCombinedPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class KandinskyV22InpaintPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class KandinskyV22Pipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class KandinskyV22PriorEmb2EmbPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class KandinskyV22PriorPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class LatentConsistencyModelImg2ImgPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class LatentConsistencyModelPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class LattePipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class LDMTextToImagePipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class LEditsPPPipelineStableDiffusion(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class LEditsPPPipelineStableDiffusionXL(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class LTXImageToVideoPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class LTXPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class LuminaText2ImgPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class MarigoldDepthPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class MarigoldNormalsPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class MochiPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class MusicLDMPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class PaintByExamplePipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class PIAPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class PixArtAlphaPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class PixArtSigmaPAGPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class PixArtSigmaPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class ReduxImageEncoder(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class SanaPAGPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class SanaPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class SAPIImageGenControlNetPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class SAPIImageGenImg2ImgPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class SAPIImageGenInpaintPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class SAPIImageGenPAGImg2ImgPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class SAPIImageGenPAGPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class SAPIImageGenPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class SAPIPhotoGenControlImg2ImgPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class SAPIPhotoGenControlInpaintPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class SAPIPhotoGenControlNetImg2ImgPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class SAPIPhotoGenControlNetInpaintPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class SAPIPhotoGenControlNetPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class SAPIPhotoGenControlPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class SAPIPhotoGenFillPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class SAPIPhotoGenImg2ImgPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class SAPIPhotoGenInpaintPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class SAPIPhotoGenPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class SAPIPhotoGenPriorReduxPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class SAPIVideoGenControlNetPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class SAPIVideoGenPAGPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class SAPIVideoGenPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class SAPIVideoGenSDXLPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class SAPIVideoGenSparseControlNetPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class SAPIVideoGenVideoToVideoControlNetPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class SAPIVideoGenVideoToVideoPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class SapiensImageGenPAGPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class SapiensImageGenPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class SapiensVideoGenImageToVideoPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class SapiensVideoGenPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class SemanticStableDiffusionPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class ShapEImg2ImgPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class ShapEPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableAudioPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableAudioProjectionModel(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableCascadeCombinedPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableCascadeDecoderPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableCascadePriorPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusion3ControlNetPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusion3Img2ImgPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusion3InpaintPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusion3PAGImg2ImgPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusion3PAGPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusion3Pipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusionAdapterPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusionAttendAndExcitePipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusionControlNetImg2ImgPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusionControlNetInpaintPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusionControlNetPAGInpaintPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusionControlNetPAGPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusionControlNetPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusionControlNetXSPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusionDepth2ImgPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusionDiffEditPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusionGLIGENPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusionGLIGENTextImagePipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusionImageVariationPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusionImg2ImgPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusionInpaintPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusionInpaintPipelineLegacy(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusionInstructPix2PixPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusionLatentUpscalePipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusionLDM3DPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusionModelEditingPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusionPAGImg2ImgPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusionPAGInpaintPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusionPAGPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusionPanoramaPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusionParadigmsPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusionPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusionPipelineSafe(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusionPix2PixZeroPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusionSAGPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusionUpscalePipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusionXLAdapterPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusionXLControlNetImg2ImgPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusionXLControlNetInpaintPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusionXLControlNetPAGImg2ImgPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusionXLControlNetPAGPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusionXLControlNetPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusionXLControlNetUnionImg2ImgPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusionXLControlNetUnionInpaintPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusionXLControlNetUnionPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusionXLControlNetXSPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusionXLImg2ImgPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusionXLInpaintPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusionXLInstructPix2PixPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusionXLPAGImg2ImgPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusionXLPAGInpaintPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusionXLPAGPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableDiffusionXLPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableUnCLIPImg2ImgPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableUnCLIPPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class StableVideoDiffusionPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class TextToVideoSDPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class TextToVideoZeroPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class TextToVideoZeroSDXLPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class UnCLIPImageVariationPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class UnCLIPPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class UniDiffuserModel(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class UniDiffuserPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class UniDiffuserTextDecoder(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class VersatileDiffusionDualGuidedPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class VersatileDiffusionImageVariationPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class VersatileDiffusionPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class VersatileDiffusionTextToImagePipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class VideoToVideoSDPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class VQDiffusionPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class WuerstchenCombinedPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class WuerstchenDecoderPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
class WuerstchenPriorPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers'])
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
