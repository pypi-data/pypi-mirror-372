"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ..utils import (OptionalDependencyNotAvailable, _LazyModule, is_torch_available)
_import_structure = {"agents": ["Agent", "CodeAgent", "ManagedAgent", "ReactAgent", "ReactCodeAgent", "ReactJsonAgent", "Toolbox"], "llm_engine": ["HfApiEngine", "TransformersEngine"],
"monitoring": ["stream_to_gradio"], "tools": ["PipelineTool", "Tool", "ToolCollection", "launch_gradio_demo", "load_tool", "tool"]}
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else:
    _import_structure["default_tools"] = ["FinalAnswerTool", "PythonInterpreterTool"]
    _import_structure["document_question_answering"] = ["DocumentQuestionAnsweringTool"]
    _import_structure["image_question_answering"] = ["ImageQuestionAnsweringTool"]
    _import_structure["search"] = ["DuckDuckGoSearchTool", "VisitWebpageTool"]
    _import_structure["speech_to_text"] = ["SpeechToTextTool"]
    _import_structure["text_to_speech"] = ["TextToSpeechTool"]
    _import_structure["translation"] = ["TranslationTool"]
if TYPE_CHECKING:
    from .agents import Agent, CodeAgent, ManagedAgent, ReactAgent, ReactCodeAgent, ReactJsonAgent, Toolbox
    from .llm_engine import HfApiEngine, TransformersEngine
    from .monitoring import stream_to_gradio
    from .tools import PipelineTool, Tool, ToolCollection, launch_gradio_demo, load_tool, tool
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else:
        from .default_tools import FinalAnswerTool, PythonInterpreterTool
        from .document_question_answering import DocumentQuestionAnsweringTool
        from .image_question_answering import ImageQuestionAnsweringTool
        from .search import DuckDuckGoSearchTool, VisitWebpageTool
        from .speech_to_text import SpeechToTextTool
        from .text_to_speech import TextToSpeechTool
        from .translation import TranslationTool
else:
    import sys
    sys.modules[__name__] = _LazyModule(__name__, globals()["__file__"], _import_structure, module_spec=__spec__)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
