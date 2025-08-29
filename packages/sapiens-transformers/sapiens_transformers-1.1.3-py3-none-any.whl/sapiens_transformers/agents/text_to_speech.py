"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import torch
from ..models.speecht5 import SpeechT5ForTextToSpeech, SpeechT5HifiGan, SpeechT5Processor
from ..utils import is_datasets_available
from .tools import PipelineTool
if is_datasets_available(): from datasets import load_dataset
class TextToSpeechTool(PipelineTool):
    default_checkpoint = "microsoft/speecht5_tts"
    description = ("This is a tool that reads an English text out loud. It returns a waveform object containing the sound.")
    name = "text_to_speech"
    pre_processor_class = SpeechT5Processor
    model_class = SpeechT5ForTextToSpeech
    post_processor_class = SpeechT5HifiGan
    inputs = {"text": {"type": "string", "description": "The text to read out loud (in English)"}}
    output_type = "audio"
    def setup(self):
        if self.post_processor is None: self.post_processor = "microsoft/speecht5_hifigan"
        super().setup()
    def encode(self, text, speaker_embeddings=None):
        inputs = self.pre_processor(text=text, return_tensors="pt", truncation=True)
        if speaker_embeddings is None:
            if not is_datasets_available(): raise ImportError("Datasets needs to be installed if not passing speaker embeddings.")
            embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation", trust_remote_code=True)
            speaker_embeddings = torch.tensor(embeddings_dataset[7305]["xvector"]).unsqueeze(0)
        return {"input_ids": inputs["input_ids"], "speaker_embeddings": speaker_embeddings}
    def forward(self, inputs):
        with torch.no_grad(): return self.model.generate_speech(**inputs)
    def decode(self, outputs):
        with torch.no_grad(): return self.post_processor(outputs).cpu().detach()
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
