'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ..utils import DummyObject, requires_backends
class CosineDPMSolverMultistepScheduler(metaclass=DummyObject):
    _backends = ['torch', 'torchsde']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'torchsde'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'torchsde'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'torchsde'])
class DPMSolverSDEScheduler(metaclass=DummyObject):
    _backends = ['torch', 'torchsde']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'torchsde'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'torchsde'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'torchsde'])
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
