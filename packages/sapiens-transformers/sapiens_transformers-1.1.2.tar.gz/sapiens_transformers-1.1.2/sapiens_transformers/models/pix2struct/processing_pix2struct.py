"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import List, Optional, Union
from ...feature_extraction_utils import BatchFeature
from ...processing_utils import ImagesKwargs, ProcessingKwargs, ProcessorMixin, Unpack
from ...tokenization_utils_base import BatchEncoding, PreTokenizedInput, TextInput
class Pix2StructImagesKwargs(ImagesKwargs, total=False):
    max_patches: Optional[int]
    header_text: Optional[Union[TextInput, PreTokenizedInput, List[TextInput], List[PreTokenizedInput]]]
class Pix2StructProcessorKwargs(ProcessingKwargs, total=False):
    images_kwargs: Pix2StructImagesKwargs
    _defaults = {"text_kwargs": {'add_special_tokens': True, 'padding': False, 'stride': 0, 'return_overflowing_tokens': False, 'return_special_tokens_mask': False,
    'return_offsets_mapping': False, 'return_token_type_ids': False, 'return_length': False, 'verbose': True}, "images_kwargs": {'max_patches': 2048}}
class Pix2StructProcessor(ProcessorMixin):
    attributes = ["image_processor", "tokenizer"]
    image_processor_class = "Pix2StructImageProcessor"
    tokenizer_class = ("T5Tokenizer", "T5TokenizerFast")
    def __init__(self, image_processor, tokenizer):
        tokenizer.return_token_type_ids = False
        super().__init__(image_processor, tokenizer)
    def __call__(self, images=None, text: Union[TextInput, PreTokenizedInput, List[TextInput], List[PreTokenizedInput]] = None, audio=None, videos=None,
    **kwargs: Unpack[Pix2StructProcessorKwargs]) -> Union[BatchEncoding, BatchFeature]:
        if images is None and text is None: raise ValueError("You have to specify either images or text.")
        output_kwargs = self._merge_kwargs(Pix2StructProcessorKwargs, tokenizer_init_kwargs=self.tokenizer.init_kwargs, **kwargs)
        if images is None and not self.image_processor.is_vqa:
            self.current_processor = self.tokenizer
            text_encoding = self.tokenizer(text=text, **output_kwargs["text_kwargs"])
            return text_encoding
        if not self.image_processor.is_vqa: encoding_image_processor = self.image_processor(images, **output_kwargs["images_kwargs"])
        else:
            output_kwargs["images_kwargs"].setdefault("header_text", text)
            encoding_image_processor = self.image_processor(images, **output_kwargs["images_kwargs"])
        if text is not None and not self.image_processor.is_vqa:
            text_encoding = self.tokenizer(text=text, **output_kwargs["text_kwargs"])
            if "attention_mask" in text_encoding: text_encoding["decoder_attention_mask"] = text_encoding.pop("attention_mask")
            if "input_ids" in text_encoding: text_encoding["decoder_input_ids"] = text_encoding.pop("input_ids")
        else: text_encoding = None
        if text_encoding is not None: encoding_image_processor.update(text_encoding)
        return encoding_image_processor
    def batch_decode(self, *args, **kwargs): return self.tokenizer.batch_decode(*args, **kwargs)
    def decode(self, *args, **kwargs): return self.tokenizer.decode(*args, **kwargs)
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
