'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ..utils import DummyObject, requires_backends
class StableDiffusionKDiffusionPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers', 'k_diffusion']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers', 'k_diffusion'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers', 'k_diffusion'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers', 'k_diffusion'])
class StableDiffusionXLKDiffusionPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers', 'k_diffusion']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers', 'k_diffusion'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers', 'k_diffusion'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers', 'k_diffusion'])
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
