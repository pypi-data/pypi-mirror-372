"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import warnings
from typing import List, Union
from ...image_utils import ImageInput
from ...processing_utils import ProcessingKwargs, ProcessorMixin, Unpack
from ...tokenization_utils_base import BatchEncoding, PreTokenizedInput, TextInput
class ChineseClipProcessorKwargs(ProcessingKwargs, total=False): _defaults = {}
class ChineseCLIPProcessor(ProcessorMixin):
    attributes = ["image_processor", "tokenizer"]
    image_processor_class = "ChineseCLIPImageProcessor"
    tokenizer_class = ("BertTokenizer", "BertTokenizerFast")
    def __init__(self, image_processor=None, tokenizer=None, **kwargs):
        feature_extractor = None
        if "feature_extractor" in kwargs:
            warnings.warn("The `feature_extractor` argument is deprecated and will be removed in v5, use `image_processor` instead.", FutureWarning)
            feature_extractor = kwargs.pop("feature_extractor")
        image_processor = image_processor if image_processor is not None else feature_extractor
        if image_processor is None: raise ValueError("You need to specify an `image_processor`.")
        if tokenizer is None: raise ValueError("You need to specify a `tokenizer`.")
        super().__init__(image_processor, tokenizer)
        self.current_processor = self.image_processor
    def __call__(self, text: Union[TextInput, PreTokenizedInput, List[TextInput], List[PreTokenizedInput]] = None, images: ImageInput = None,
    audio=None, videos=None, **kwargs: Unpack[ChineseClipProcessorKwargs]) -> BatchEncoding:
        if text is None and images is None: raise ValueError("You have to specify either text or images. Both cannot be none.")
        output_kwargs = self._merge_kwargs(ChineseClipProcessorKwargs, tokenizer_init_kwargs=self.tokenizer.init_kwargs, **kwargs)
        if text is not None: encoding = self.tokenizer(text, **output_kwargs["text_kwargs"])
        if images is not None: image_features = self.image_processor(images, **output_kwargs["images_kwargs"])
        if "return_tensors" in output_kwargs["common_kwargs"]: return_tensors = output_kwargs["common_kwargs"].pop("return_tensors", None)
        if text is not None and images is not None:
            encoding["pixel_values"] = image_features.pixel_values
            return encoding
        elif text is not None: return encoding
        else: return BatchEncoding(data=dict(**image_features), tensor_type=return_tensors)
    def batch_decode(self, *args, **kwargs): return self.tokenizer.batch_decode(*args, **kwargs)
    def decode(self, *args, **kwargs): return self.tokenizer.decode(*args, **kwargs)
    @property
    def model_input_names(self):
        tokenizer_input_names = self.tokenizer.model_input_names
        image_processor_input_names = self.image_processor.model_input_names
        return list(dict.fromkeys(tokenizer_input_names + image_processor_input_names))
    @property
    def feature_extractor_class(self):
        warnings.warn("`feature_extractor_class` is deprecated and will be removed in v5. Use `image_processor_class` instead.", FutureWarning)
        return self.image_processor_class
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
