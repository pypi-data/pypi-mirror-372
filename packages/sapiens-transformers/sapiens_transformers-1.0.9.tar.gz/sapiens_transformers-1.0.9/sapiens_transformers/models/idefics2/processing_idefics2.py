"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING, List, Optional, Union
from ...feature_extraction_utils import BatchFeature
from ...image_utils import ImageInput, is_valid_image, load_image
from ...processing_utils import ProcessorMixin
from ...tokenization_utils_base import AddedToken, BatchEncoding, PaddingStrategy, TextInput, TruncationStrategy
from ...utils import TensorType, logging
if TYPE_CHECKING: from ...tokenization_utils_base import PreTokenizedInput
logger = logging.get_logger(__name__)
def is_url(val) -> bool: return isinstance(val, str) and val.startswith("http")
def is_image_or_image_url(elem): return is_url(elem) or is_valid_image(elem)
class Idefics2Processor(ProcessorMixin):
    attributes = ["image_processor", "tokenizer"]
    valid_kwargs = ["image_seq_len", "chat_template"]
    image_processor_class = "Idefics2ImageProcessor"
    tokenizer_class = "AutoTokenizer"
    def __init__(self, image_processor, tokenizer=None, image_seq_len: int = 64, chat_template: str = None, **kwargs):
        if image_processor is None: raise ValueError("You need to specify an `image_processor`.")
        if tokenizer is None: raise ValueError("You need to specify a `tokenizer`.")
        self.fake_image_token = AddedToken("<fake_token_around_image>", normalized=False, special=True)
        self.image_token = AddedToken("<image>", normalized=False, special=True)
        self.end_of_utterance_token = AddedToken("<end_of_utterance>", normalized=False, special=True)
        self.image_seq_len = image_seq_len
        tokens_to_add = {"additional_special_tokens": [self.fake_image_token, self.image_token, self.end_of_utterance_token]}
        tokenizer.add_special_tokens(tokens_to_add)
        super().__init__(image_processor, tokenizer, chat_template=chat_template)
    def _extract_images_from_prompts(self, prompts):
        prompt_images = []
        for prompt in prompts:
            images = []
            for elem in prompt:
                if is_valid_image(elem): images.append(elem)
                elif is_url(elem): images.append(load_image(elem))
            prompt_images.append(images)
        return prompt_images
    def __call__(self, text: Union[TextInput, "PreTokenizedInput", List[TextInput], List["PreTokenizedInput"]] = None, images: Union[ImageInput, List[ImageInput], List[List[ImageInput]]] = None,
    image_seq_len: Optional[int] = None, padding: Union[bool, str, PaddingStrategy] = False, truncation: Union[bool, str, TruncationStrategy] = None, max_length: Optional[int] = None,
    is_split_into_words: bool = False, add_special_tokens: bool = True, return_tensors: Optional[Union[str, TensorType]] = None) -> BatchEncoding:
        image_seq_len = image_seq_len if image_seq_len is not None else self.image_seq_len
        n_images_in_text = []
        inputs = BatchFeature()
        if text is not None:
            if isinstance(text, str): text = [text]
            elif not isinstance(text, list) and not isinstance(text[0], str): raise ValueError("Invalid input text. Please provide a string, or a list of strings")
            fake_image_token = self.fake_image_token.content
            image_token = self.image_token.content
            image_str = f"{fake_image_token}{image_token * image_seq_len}{fake_image_token}"
            if self.image_processor.do_image_splitting: image_str = image_str * 5
            prompt_strings = []
            for sample in text:
                n_images_in_text.append(sample.count(image_token))
                sample = sample.replace(image_token, image_str)
                sample = sample.replace(f"{fake_image_token}{fake_image_token}", f"{fake_image_token}")
                prompt_strings.append(sample)
            text_inputs = self.tokenizer(text=prompt_strings, add_special_tokens=add_special_tokens, padding=padding, truncation=truncation, max_length=max_length,
            is_split_into_words=is_split_into_words, return_tensors=return_tensors)
            inputs.update(text_inputs)
        if images is not None:
            if is_image_or_image_url(images): images = [[images]]
            elif isinstance(images, list) and is_image_or_image_url(images[0]): images = [images]
            elif (not isinstance(images, list) and not isinstance(images[0], list) and not is_image_or_image_url(images[0][0])): raise ValueError("Invalid input images. Please provide a single image or a list of images or a list of list of images.")
            n_images_in_images = [len(sample) for sample in images]
            if text is not None and not n_images_in_images == n_images_in_text: raise ValueError(f"The number of images in the text {n_images_in_text} and images  {n_images_in_images} should be the same.")
            images = [[load_image(im) for im in sample] for sample in images]
            image_inputs = self.image_processor(images, return_tensors=return_tensors)
            inputs.update(image_inputs)
        return inputs
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
