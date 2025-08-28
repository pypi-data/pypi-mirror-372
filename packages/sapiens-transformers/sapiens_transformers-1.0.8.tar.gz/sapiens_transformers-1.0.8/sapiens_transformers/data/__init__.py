"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from .data_collator import (DataCollatorForLanguageModeling, DataCollatorForPermutationLanguageModeling, DataCollatorForSeq2Seq,
DataCollatorForSOP, DataCollatorForTokenClassification, DataCollatorForWholeWordMask, DataCollatorWithFlattening, DataCollatorWithPadding, DefaultDataCollator, default_data_collator)
from .metrics import glue_compute_metrics, xnli_compute_metrics
from .processors import (DataProcessor, InputExample, InputFeatures, SingleSentenceClassificationProcessor, SquadExample, SquadFeatures, SquadV1Processor,
SquadV2Processor, glue_convert_examples_to_features, glue_output_modes, glue_processors, glue_tasks_num_labels, squad_convert_examples_to_features, xnli_output_modes, xnli_processors, xnli_tasks_num_labels)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
