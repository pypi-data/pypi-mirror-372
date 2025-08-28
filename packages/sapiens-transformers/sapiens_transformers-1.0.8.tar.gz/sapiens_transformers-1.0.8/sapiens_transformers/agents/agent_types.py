"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import os
import pathlib
import tempfile
import uuid
import numpy as np
from ..utils import is_soundfile_availble, is_torch_available, is_vision_available, logging
logger = logging.get_logger(__name__)
if is_vision_available():
    from PIL import Image
    from PIL.Image import Image as ImageType
else: ImageType = object
if is_torch_available():
    import torch
    from torch import Tensor
else: Tensor = object
if is_soundfile_availble(): import soundfile as sf
class AgentType:
    def __init__(self, value): self._value = value
    def __str__(self): return self.to_string()
    def to_raw(self):
        logger.error("This is a raw AgentType of unknown type. Display in notebooks and string conversion will be unreliable")
        return self._value
    def to_string(self) -> str:
        logger.error("This is a raw AgentType of unknown type. Display in notebooks and string conversion will be unreliable")
        return str(self._value)
class AgentText(AgentType, str):
    def to_raw(self): return self._value
    def to_string(self): return str(self._value)
class AgentImage(AgentType, ImageType):
    def __init__(self, value):
        AgentType.__init__(self, value)
        ImageType.__init__(self)
        if not is_vision_available(): raise ImportError("PIL must be installed in order to handle images.")
        self._path = None
        self._raw = None
        self._tensor = None
        if isinstance(value, ImageType): self._raw = value
        elif isinstance(value, (str, pathlib.Path)): self._path = value
        elif isinstance(value, torch.Tensor): self._tensor = value
        elif isinstance(value, np.ndarray): self._tensor = torch.from_numpy(value)
        else: raise TypeError(f"Unsupported type for {self.__class__.__name__}: {type(value)}")
    def _ipython_display_(self, include=None, exclude=None):
        from IPython.display import Image, display
        display(Image(self.to_string()))
    def to_raw(self):
        if self._raw is not None: return self._raw
        if self._path is not None:
            self._raw = Image.open(self._path)
            return self._raw
        if self._tensor is not None:
            array = self._tensor.cpu().detach().numpy()
            return Image.fromarray((255 - array * 255).astype(np.uint8))
    def to_string(self):
        if self._path is not None: return self._path
        if self._raw is not None:
            directory = tempfile.mkdtemp()
            self._path = os.path.join(directory, str(uuid.uuid4()) + ".png")
            self._raw.save(self._path)
            return self._path
        if self._tensor is not None:
            array = self._tensor.cpu().detach().numpy()
            img = Image.fromarray((255 - array * 255).astype(np.uint8))
            directory = tempfile.mkdtemp()
            self._path = os.path.join(directory, str(uuid.uuid4()) + ".png")
            img.save(self._path)
            return self._path
    def save(self, output_bytes, format, **params):
        img = self.to_raw()
        img.save(output_bytes, format, **params)
class AgentAudio(AgentType, str):
    def __init__(self, value, samplerate=16_000):
        super().__init__(value)
        if not is_soundfile_availble(): raise ImportError("soundfile must be installed in order to handle audio.")
        self._path = None
        self._tensor = None
        self.samplerate = samplerate
        if isinstance(value, (str, pathlib.Path)): self._path = value
        elif is_torch_available() and isinstance(value, torch.Tensor): self._tensor = value
        elif isinstance(value, tuple):
            self.samplerate = value[0]
            if isinstance(value[1], np.ndarray): self._tensor = torch.from_numpy(value[1])
            else: self._tensor = torch.tensor(value[1])
        else: raise ValueError(f"Unsupported audio type: {type(value)}")
    def _ipython_display_(self, include=None, exclude=None):
        from IPython.display import Audio, display
        display(Audio(self.to_string(), rate=self.samplerate))
    def to_raw(self):
        if self._tensor is not None: return self._tensor
        if self._path is not None:
            tensor, self.samplerate = sf.read(self._path)
            self._tensor = torch.tensor(tensor)
            return self._tensor
    def to_string(self):
        if self._path is not None: return self._path
        if self._tensor is not None:
            directory = tempfile.mkdtemp()
            self._path = os.path.join(directory, str(uuid.uuid4()) + ".wav")
            sf.write(self._path, self._tensor, samplerate=self.samplerate)
            return self._path
AGENT_TYPE_MAPPING = {"string": AgentText, "image": AgentImage, "audio": AgentAudio}
INSTANCE_TYPE_MAPPING = {str: AgentText, ImageType: AgentImage}
if is_torch_available(): INSTANCE_TYPE_MAPPING[Tensor] = AgentAudio
def handle_agent_inputs(*args, **kwargs):
    args = [(arg.to_raw() if isinstance(arg, AgentType) else arg) for arg in args]
    kwargs = {k: (v.to_raw() if isinstance(v, AgentType) else v) for k, v in kwargs.items()}
    return args, kwargs
def handle_agent_outputs(output, output_type=None):
    if output_type in AGENT_TYPE_MAPPING:
        decoded_outputs = AGENT_TYPE_MAPPING[output_type](output)
        return decoded_outputs
    else:
        for _k, _v in INSTANCE_TYPE_MAPPING.items():
            if isinstance(output, _k): return _v(output)
        return output
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
