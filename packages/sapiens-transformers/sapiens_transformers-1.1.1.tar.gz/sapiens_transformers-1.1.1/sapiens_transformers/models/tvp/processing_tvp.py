"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...processing_utils import ProcessorMixin
from ...tokenization_utils_base import BatchEncoding
class TvpProcessor(ProcessorMixin):
    attributes = ["image_processor", "tokenizer"]
    image_processor_class = "TvpImageProcessor"
    tokenizer_class = ("BertTokenizer", "BertTokenizerFast")
    def __init__(self, image_processor=None, tokenizer=None, **kwargs):
        if image_processor is None: raise ValueError("You need to specify an `image_processor`.")
        if tokenizer is None: raise ValueError("You need to specify a `tokenizer`.")
        super().__init__(image_processor, tokenizer)
    def __call__(self, text=None, videos=None, return_tensors=None, **kwargs):
        max_text_length = kwargs.pop("max_text_length", None)
        if text is None and videos is None: raise ValueError("You have to specify either text or videos. Both cannot be none.")
        encoding = {}
        if text is not None:
            textual_input = self.tokenizer.batch_encode_plus(text, truncation=True, padding="max_length", max_length=max_text_length, pad_to_max_length=True,
            return_tensors=return_tensors, return_token_type_ids=False, **kwargs)
            encoding.update(textual_input)
        if videos is not None:
            image_features = self.image_processor(videos, return_tensors=return_tensors, **kwargs)
            encoding.update(image_features)
        return BatchEncoding(data=encoding, tensor_type=return_tensors)
    def batch_decode(self, *args, **kwargs): return self.tokenizer.batch_decode(*args, **kwargs)
    def decode(self, *args, **kwargs): return self.tokenizer.decode(*args, **kwargs)
    def post_process_video_grounding(self, logits, video_durations):
        start, end = (round(logits.tolist()[0][0] * video_durations, 1), round(logits.tolist()[0][1] * video_durations, 1),)
        return start, end
    @property
    def model_input_names(self):
        tokenizer_input_names = self.tokenizer.model_input_names
        image_processor_input_names = self.image_processor.model_input_names
        return list(dict.fromkeys(tokenizer_input_names + image_processor_input_names))
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
