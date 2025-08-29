"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ..utils import OptionalDependencyNotAvailable, _LazyModule, is_flax_available, is_tf_available, is_torch_available
_import_structure = {"configuration_utils": ["GenerationConfig", "GenerationMode", "WatermarkingConfig"], "streamers": ["TextIteratorStreamer", "TextStreamer"]}
_import_structure["beam_constraints"] = ["Constraint", "ConstraintListState", "DisjunctiveConstraint", "PhrasalConstraint"]
_import_structure["beam_search"] = ["BeamHypotheses", "BeamScorer", "BeamSearchScorer", "ConstrainedBeamSearchScorer"]
_import_structure["candidate_generator"] = ["AssistedCandidateGenerator", "CandidateGenerator", "PromptLookupCandidateGenerator"]
_import_structure["logits_process"] = ["AlternatingCodebooksLogitsProcessor", "ClassifierFreeGuidanceLogitsProcessor", "EncoderNoRepeatNGramLogitsProcessor",
"EncoderRepetitionPenaltyLogitsProcessor", "EpsilonLogitsWarper", "EtaLogitsWarper", "ExponentialDecayLengthPenalty", "ForcedBOSTokenLogitsProcessor",
"ForcedEOSTokenLogitsProcessor", "HammingDiversityLogitsProcessor", "InfNanRemoveLogitsProcessor", "LogitNormalization", "LogitsProcessor", "LogitsProcessorList",
"LogitsWarper", "MinLengthLogitsProcessor", "MinNewTokensLengthLogitsProcessor", "MinPLogitsWarper", "NoBadWordsLogitsProcessor", "NoRepeatNGramLogitsProcessor",
"PrefixConstrainedLogitsProcessor", "RepetitionPenaltyLogitsProcessor", "SAPIAudioTimeStampLogitsProcessor", "SequenceBiasLogitsProcessor", "SuppressTokensLogitsProcessor", "SuppressTokensAtBeginLogitsProcessor",
"TemperatureLogitsWarper", "TopKLogitsWarper", "TopPLogitsWarper", "TypicalLogitsWarper", "UnbatchedClassifierFreeGuidanceLogitsProcessor", "WhisperTimeStampLogitsProcessor", "WatermarkLogitsProcessor"]
_import_structure["stopping_criteria"] = ["MaxNewTokensCriteria", "MaxLengthCriteria", "MaxTimeCriteria", "ConfidenceCriteria", "EosTokenCriteria", "StoppingCriteria", "StoppingCriteriaList", "validate_stopping_criteria", "StopStringCriteria"]
_import_structure["utils"] = ["GenerationMixin", "GreedySearchEncoderDecoderOutput", "GreedySearchDecoderOnlyOutput", "SampleEncoderDecoderOutput", "SampleDecoderOnlyOutput",
"BeamSearchEncoderDecoderOutput", "BeamSearchDecoderOnlyOutput", "BeamSampleEncoderDecoderOutput", "BeamSampleDecoderOnlyOutput", "ContrastiveSearchEncoderDecoderOutput",
"ContrastiveSearchDecoderOnlyOutput", "GenerateBeamDecoderOnlyOutput", "GenerateBeamEncoderDecoderOutput", "GenerateDecoderOnlyOutput", "GenerateEncoderDecoderOutput"]
_import_structure["watermarking"] = ["WatermarkDetector", "WatermarkDetectorOutput"]
_import_structure["tf_logits_process"] = ["TFForcedBOSTokenLogitsProcessor", "TFForcedEOSTokenLogitsProcessor", "TFForceTokensLogitsProcessor", "TFLogitsProcessor",
"TFLogitsProcessorList", "TFLogitsWarper", "TFMinLengthLogitsProcessor", "TFNoBadWordsLogitsProcessor", "TFNoRepeatNGramLogitsProcessor", "TFRepetitionPenaltyLogitsProcessor",
"TFSuppressTokensAtBeginLogitsProcessor", "TFSuppressTokensLogitsProcessor", "TFTemperatureLogitsWarper", "TFTopKLogitsWarper", "TFTopPLogitsWarper"]
_import_structure["tf_utils"] = ["TFGenerationMixin", "TFGreedySearchDecoderOnlyOutput", "TFGreedySearchEncoderDecoderOutput", "TFSampleEncoderDecoderOutput",
"TFSampleDecoderOnlyOutput", "TFBeamSearchEncoderDecoderOutput", "TFBeamSearchDecoderOnlyOutput", "TFBeamSampleEncoderDecoderOutput", "TFBeamSampleDecoderOnlyOutput",
"TFContrastiveSearchEncoderDecoderOutput", "TFContrastiveSearchDecoderOnlyOutput"]
_import_structure["flax_logits_process"] = ["FlaxForcedBOSTokenLogitsProcessor", "FlaxForcedEOSTokenLogitsProcessor", "FlaxForceTokensLogitsProcessor", "FlaxLogitsProcessor",
"FlaxLogitsProcessorList", "FlaxLogitsWarper", "FlaxMinLengthLogitsProcessor", "FlaxSAPIAudioTimeStampLogitsProcessor", "FlaxSuppressTokensAtBeginLogitsProcessor", "FlaxSuppressTokensLogitsProcessor", "FlaxTemperatureLogitsWarper",
"FlaxTopKLogitsWarper", "FlaxTopPLogitsWarper", "FlaxWhisperTimeStampLogitsProcessor", "FlaxNoRepeatNGramLogitsProcessor"]
_import_structure["flax_utils"] = ["FlaxGenerationMixin", "FlaxGreedySearchOutput", "FlaxSampleOutput", "FlaxBeamSearchOutput"]
if TYPE_CHECKING:
    from .configuration_utils import GenerationConfig, GenerationMode, WatermarkingConfig
    from .streamers import TextIteratorStreamer, TextStreamer
    from .beam_constraints import Constraint, ConstraintListState, DisjunctiveConstraint, PhrasalConstraint
    from .beam_search import BeamHypotheses, BeamScorer, BeamSearchScorer, ConstrainedBeamSearchScorer
    from .candidate_generator import AssistedCandidateGenerator, CandidateGenerator, PromptLookupCandidateGenerator
    from .logits_process import (AlternatingCodebooksLogitsProcessor, ClassifierFreeGuidanceLogitsProcessor, EncoderNoRepeatNGramLogitsProcessor, EncoderRepetitionPenaltyLogitsProcessor,
    EpsilonLogitsWarper, EtaLogitsWarper, ExponentialDecayLengthPenalty, ForcedBOSTokenLogitsProcessor, ForcedEOSTokenLogitsProcessor, HammingDiversityLogitsProcessor, InfNanRemoveLogitsProcessor,
    LogitNormalization, LogitsProcessor, LogitsProcessorList, LogitsWarper, MinLengthLogitsProcessor, MinNewTokensLengthLogitsProcessor, MinPLogitsWarper, NoBadWordsLogitsProcessor,
    NoRepeatNGramLogitsProcessor, PrefixConstrainedLogitsProcessor, RepetitionPenaltyLogitsProcessor, SAPIAudioTimeStampLogitsProcessor, SequenceBiasLogitsProcessor, SuppressTokensAtBeginLogitsProcessor, SuppressTokensLogitsProcessor,
    TemperatureLogitsWarper, TopKLogitsWarper, TopPLogitsWarper, TypicalLogitsWarper, UnbatchedClassifierFreeGuidanceLogitsProcessor, WatermarkLogitsProcessor, WhisperTimeStampLogitsProcessor)
    from .stopping_criteria import (ConfidenceCriteria, EosTokenCriteria, MaxLengthCriteria, MaxNewTokensCriteria, MaxTimeCriteria, StoppingCriteria, StoppingCriteriaList, StopStringCriteria, validate_stopping_criteria)
    from .utils import (BeamSampleDecoderOnlyOutput, BeamSampleEncoderDecoderOutput, BeamSearchDecoderOnlyOutput, BeamSearchEncoderDecoderOutput, ContrastiveSearchDecoderOnlyOutput,
    ContrastiveSearchEncoderDecoderOutput, GenerateBeamDecoderOnlyOutput, GenerateBeamEncoderDecoderOutput, GenerateDecoderOnlyOutput, GenerateEncoderDecoderOutput, GenerationMixin,
    GreedySearchDecoderOnlyOutput, GreedySearchEncoderDecoderOutput, SampleDecoderOnlyOutput, SampleEncoderDecoderOutput)
    from .watermarking import (WatermarkDetector, WatermarkDetectorOutput)
    from .tf_logits_process import (TFForcedBOSTokenLogitsProcessor, TFForcedEOSTokenLogitsProcessor, TFForceTokensLogitsProcessor, TFLogitsProcessor, TFLogitsProcessorList,
    TFLogitsWarper, TFMinLengthLogitsProcessor, TFNoBadWordsLogitsProcessor, TFNoRepeatNGramLogitsProcessor, TFRepetitionPenaltyLogitsProcessor, TFSuppressTokensAtBeginLogitsProcessor,
    TFSuppressTokensLogitsProcessor, TFTemperatureLogitsWarper, TFTopKLogitsWarper, TFTopPLogitsWarper)
    from .tf_utils import (TFBeamSampleDecoderOnlyOutput, TFBeamSampleEncoderDecoderOutput, TFBeamSearchDecoderOnlyOutput, TFBeamSearchEncoderDecoderOutput, TFContrastiveSearchDecoderOnlyOutput,
    TFContrastiveSearchEncoderDecoderOutput, TFGenerationMixin, TFGreedySearchDecoderOnlyOutput, TFGreedySearchEncoderDecoderOutput, TFSampleDecoderOnlyOutput, TFSampleEncoderDecoderOutput)
    from .flax_logits_process import (FlaxForcedBOSTokenLogitsProcessor, FlaxForcedEOSTokenLogitsProcessor, FlaxForceTokensLogitsProcessor, FlaxLogitsProcessor, FlaxLogitsProcessorList,
    FlaxLogitsWarper, FlaxMinLengthLogitsProcessor, FlaxNoRepeatNGramLogitsProcessor, FlaxSAPIAudioTimeStampLogitsProcessor, FlaxSuppressTokensAtBeginLogitsProcessor, FlaxSuppressTokensLogitsProcessor, FlaxTemperatureLogitsWarper,
    FlaxTopKLogitsWarper, FlaxTopPLogitsWarper, FlaxWhisperTimeStampLogitsProcessor)
    from .flax_utils import FlaxBeamSearchOutput, FlaxGenerationMixin, FlaxGreedySearchOutput, FlaxSampleOutput
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
