'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ..utils import DummyObject, requires_backends
class OnnxStableDiffusionImg2ImgPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers', 'onnx']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers', 'onnx'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers', 'onnx'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers', 'onnx'])
class OnnxStableDiffusionInpaintPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers', 'onnx']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers', 'onnx'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers', 'onnx'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers', 'onnx'])
class OnnxStableDiffusionInpaintPipelineLegacy(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers', 'onnx']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers', 'onnx'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers', 'onnx'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers', 'onnx'])
class OnnxStableDiffusionPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers', 'onnx']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers', 'onnx'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers', 'onnx'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers', 'onnx'])
class OnnxStableDiffusionUpscalePipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers', 'onnx']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers', 'onnx'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers', 'onnx'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers', 'onnx'])
class StableDiffusionOnnxPipeline(metaclass=DummyObject):
    _backends = ['torch', 'sapiens_transformers', 'onnx']
    def __init__(self, *args, **kwargs): requires_backends(self, ['torch', 'sapiens_transformers', 'onnx'])
    @classmethod
    def from_config(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers', 'onnx'])
    @classmethod
    def from_pretrained(cls, *args, **kwargs): requires_backends(cls, ['torch', 'sapiens_transformers', 'onnx'])
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
