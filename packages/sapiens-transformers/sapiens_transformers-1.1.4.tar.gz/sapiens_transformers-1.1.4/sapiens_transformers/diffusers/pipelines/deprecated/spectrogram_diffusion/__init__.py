'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from typing import TYPE_CHECKING
from ....utils import DIFFUSERS_SLOW_IMPORT, _LazyModule, is_note_seq_available, OptionalDependencyNotAvailable, is_torch_available, is_transformers_available, get_objects_from_module
_dummy_objects = {}
_import_structure = {}
try:
    if not (is_transformers_available() and is_torch_available()): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable:
    from ....utils import dummy_torch_and_transformers_objects
    _dummy_objects.update(get_objects_from_module(dummy_torch_and_transformers_objects))
else:
    _import_structure['continous_encoder'] = ['SpectrogramContEncoder']
    _import_structure['notes_encoder'] = ['SpectrogramNotesEncoder']
    _import_structure['pipeline_spectrogram_diffusion'] = ['SpectrogramContEncoder', 'SpectrogramDiffusionPipeline', 'T5FilmDecoder']
try:
    if not (is_transformers_available() and is_torch_available() and is_note_seq_available()): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable:
    from ....utils import dummy_transformers_and_torch_and_note_seq_objects
    _dummy_objects.update(get_objects_from_module(dummy_transformers_and_torch_and_note_seq_objects))
else: _import_structure['midi_utils'] = ['MidiProcessor']
if TYPE_CHECKING or DIFFUSERS_SLOW_IMPORT:
    try:
        if not (is_transformers_available() and is_torch_available()): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: from ....utils.dummy_torch_and_transformers_objects import *
    else:
        from .pipeline_spectrogram_diffusion import SpectrogramDiffusionPipeline
        from .pipeline_spectrogram_diffusion import SpectrogramContEncoder
        from .pipeline_spectrogram_diffusion import SpectrogramNotesEncoder
        from .pipeline_spectrogram_diffusion import T5FilmDecoder
    try:
        if not (is_transformers_available() and is_torch_available() and is_note_seq_available()): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: from ....utils.dummy_transformers_and_torch_and_note_seq_objects import *
    else: from .midi_utils import MidiProcessor
else:
    import sys
    sys.modules[__name__] = _LazyModule(__name__, globals()['__file__'], _import_structure, module_spec=__spec__)
    for name, value in _dummy_objects.items(): setattr(sys.modules[__name__], name, value)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
