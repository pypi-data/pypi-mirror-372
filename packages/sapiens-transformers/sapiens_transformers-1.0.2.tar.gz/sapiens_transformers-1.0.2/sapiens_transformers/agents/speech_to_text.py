"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ..models.whisper import WhisperForConditionalGeneration, WhisperProcessor
from .tools import PipelineTool
class SpeechToTextTool(PipelineTool):
    default_checkpoint = "distil-whisper/distil-large-v3"
    description = "This is a tool that transcribes an audio into text. It returns the transcribed text."
    name = "transcriber"
    pre_processor_class = WhisperProcessor
    model_class = WhisperForConditionalGeneration
    inputs = {"audio": {"type": "audio", "description": "The audio to transcribe"}}
    output_type = "string"
    def encode(self, audio): return self.pre_processor(audio, return_tensors="pt")
    def forward(self, inputs): return self.model.generate(inputs["input_features"])
    def decode(self, outputs): return self.pre_processor.batch_decode(outputs, skip_special_tokens=True)[0]
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
