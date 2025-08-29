"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from .glue import glue_convert_examples_to_features, glue_output_modes, glue_processors, glue_tasks_num_labels
from .squad import SquadExample, SquadFeatures, SquadV1Processor, SquadV2Processor, squad_convert_examples_to_features
from .utils import DataProcessor, InputExample, InputFeatures, SingleSentenceClassificationProcessor
from .xnli import xnli_output_modes, xnli_processors, xnli_tasks_num_labels
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
