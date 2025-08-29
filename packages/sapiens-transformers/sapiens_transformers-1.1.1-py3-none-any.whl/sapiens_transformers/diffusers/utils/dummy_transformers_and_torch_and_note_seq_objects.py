'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ..utils import DummyObject, requires_backends
class SpectrogramDiffusionPipeline(metaclass=DummyObject):
    _backends = ['sapiens_transformers', 'torch', 'note_seq']
    def __init__(self, *args, **kwargs): requires_backends(self, ['sapiens_transformers', 'torch', 'note_seq'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['sapiens_transformers', 'torch', 'note_seq'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['sapiens_transformers', 'torch', 'note_seq'])
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
