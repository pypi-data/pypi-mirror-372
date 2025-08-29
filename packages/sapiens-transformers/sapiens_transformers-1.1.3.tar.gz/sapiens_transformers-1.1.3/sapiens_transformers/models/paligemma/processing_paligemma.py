"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import logging
from typing import List, Optional, Union
from ...feature_extraction_utils import BatchFeature
from ...image_utils import ImageInput, is_valid_image
from ...processing_utils import (ImagesKwargs, ProcessingKwargs, ProcessorMixin, TextKwargs, Unpack, _validate_images_text_input_order)
from ...tokenization_utils_base import (AddedToken, PreTokenizedInput, TextInput)
logger = logging.getLogger(__name__)
IMAGE_TOKEN = "<image>"
EXTRA_TOKENS = [f"<loc{i:0>4}>" for i in range(1024)] + [f"<seg{i:0>3}>" for i in range(128)]
class PaliGemmaTextKwargs(TextKwargs):
    suffix: Optional[Union[TextInput, PreTokenizedInput, List[TextInput], List[PreTokenizedInput]]]
class PaliGemmaImagesKwargs(ImagesKwargs):
    do_convert_rgb: Optional[bool]
class PaliGemmaProcessorKwargs(ProcessingKwargs, total=False):
    text_kwargs: PaliGemmaTextKwargs
    images_kwargs: PaliGemmaImagesKwargs
    _defaults = {"text_kwargs": {'padding': False}, "images_kwargs": {'data_format': 'channels_first'}}
def is_url(val) -> bool: return isinstance(val, str) and val.startswith("http")
def is_image_or_image_url(elem): return is_url(elem) or is_valid_image(elem)
def _is_str_or_image(elem): return isinstance(elem, (str)) or is_image_or_image_url(elem)
def build_string_from_input(prompt, bos_token, image_seq_len, image_token): return f"{image_token * image_seq_len}{bos_token}{prompt}\n"
class PaliGemmaProcessor(ProcessorMixin):
    attributes = ["image_processor", "tokenizer"]
    valid_kwargs = ["chat_template"]
    image_processor_class = "SiglipImageProcessor"
    tokenizer_class = ("GemmaTokenizer", "GemmaTokenizerFast")
    def __init__(self, image_processor=None, tokenizer=None, chat_template=None, **kwargs):
        if image_processor is None: raise ValueError("You need to specify an `image_processor`.")
        if tokenizer is None: raise ValueError("You need to specify a `tokenizer`.")
        if not hasattr(image_processor, "image_seq_length"): raise ValueError("Image processor is missing an `image_seq_length` attribute.")
        self.image_seq_length = image_processor.image_seq_length
        image_token = AddedToken(IMAGE_TOKEN, normalized=False, special=True)
        tokens_to_add = {"additional_special_tokens": [image_token]}
        tokenizer.add_special_tokens(tokens_to_add)
        tokenizer.add_tokens(EXTRA_TOKENS)
        self.image_token_id = tokenizer.convert_tokens_to_ids(IMAGE_TOKEN)
        tokenizer.add_bos_token = False
        tokenizer.add_eos_token = False
        super().__init__(image_processor, tokenizer, chat_template=chat_template)
    def __call__(self, images: ImageInput = None, text: Union[TextInput, PreTokenizedInput, List[TextInput], List[PreTokenizedInput]] = None, audio=None, videos=None,
    **kwargs: Unpack[PaliGemmaProcessorKwargs]) -> BatchFeature:
        images, text = _validate_images_text_input_order(images, text)
        output_kwargs = self._merge_kwargs(PaliGemmaProcessorKwargs, tokenizer_init_kwargs=self.tokenizer.init_kwargs, **kwargs)
        suffix = output_kwargs["text_kwargs"].pop("suffix", None)
        return_token_type_ids = True if suffix is not None else False
        if images is None: raise ValueError("`images` are expected as arguments to a `PaliGemmaProcessor` instance.")
        if text is None:
            logger.warning_once("You are using PaliGemma without a text prefix. It will perform as a picture-captioning model.")
            text = ""
        if isinstance(text, List) and isinstance(images, List):
            if len(images) < len(text): raise ValueError(f"Received {len(images)} images for {len(text)} prompts. Each prompt should be associated with an image.")
        if _is_str_or_image(text): text = [text]
        elif isinstance(text, list) and _is_str_or_image(text[0]): pass
        if suffix is not None and _is_str_or_image(suffix): suffix = [suffix]
        if suffix is not None: suffix = [sfx + self.tokenizer.eos_token for sfx in suffix]
        input_strings = [build_string_from_input(prompt=prompt, bos_token=self.tokenizer.bos_token, image_seq_len=self.image_seq_length, image_token=IMAGE_TOKEN) for prompt in text]
        pixel_values = self.image_processor(images, **output_kwargs["images_kwargs"])["pixel_values"]
        if output_kwargs["text_kwargs"].get("max_length", None) is not None: output_kwargs["text_kwargs"]["max_length"] += self.image_seq_length
        inputs = self.tokenizer(input_strings, text_pair=suffix, return_token_type_ids=return_token_type_ids, **output_kwargs["text_kwargs"])
        return_data = {**inputs, "pixel_values": pixel_values}
        if return_token_type_ids:
            labels = inputs["input_ids"].masked_fill(inputs["token_type_ids"] == 0, -100)
            return_data.update({"labels": labels})
        return BatchFeature(data=return_data)
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
