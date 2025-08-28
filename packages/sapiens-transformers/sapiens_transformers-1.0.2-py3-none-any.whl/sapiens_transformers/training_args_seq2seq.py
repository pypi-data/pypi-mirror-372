"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from .generation.configuration_utils import GenerationConfig
from .training_args import TrainingArguments
from dataclasses import dataclass, field
from .utils import add_start_docstrings
from typing import Optional, Union
from pathlib import Path
import logging
logger = logging.getLogger(__name__)
@dataclass
@add_start_docstrings(TrainingArguments.__doc__)
class Seq2SeqTrainingArguments(TrainingArguments):
    sortish_sampler: bool = field(default=False, metadata={"help": "Whether to use SortishSampler or not."})
    predict_with_generate: bool = field(default=False, metadata={"help": "Whether to use generate to calculate generative metrics (ROUGE, BLEU)."})
    generation_max_length: Optional[int] = field(default=None, metadata={'help': 'The `max_length` to use on each evaluation loop when `predict_with_generate=True`. Will default to the `max_length` value of the model configuration.'})
    generation_num_beams: Optional[int] = field(default=None, metadata={'help': 'The `num_beams` to use on each evaluation loop when `predict_with_generate=True`. Will default to the `num_beams` value of the model configuration.'})
    generation_config: Optional[Union[str, Path, GenerationConfig]] = field(default=None, metadata={'help': 'Model id, file path or url pointing to a GenerationConfig json file, to use during prediction.'})
    def to_dict(self):
        d = super().to_dict()
        for k, v in d.items():
            if isinstance(v, GenerationConfig): d[k] = v.to_dict()
        return d
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
