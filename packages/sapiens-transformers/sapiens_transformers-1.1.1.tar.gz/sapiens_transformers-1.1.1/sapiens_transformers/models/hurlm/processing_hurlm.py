"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...processing_utils import ImagesKwargs, ProcessingKwargs, ProcessorMixin, Unpack
from ...tokenization_utils_base import AddedToken, BatchEncoding, TextInput
from typing import TYPE_CHECKING, Dict, List, Optional, Union
if TYPE_CHECKING: from ...tokenization_utils_base import PreTokenizedInput
from ...image_utils import ImageInput, is_valid_image, load_image
from ...feature_extraction_utils import BatchFeature
from itertools import accumulate
import re
def is_url(val) -> bool: return isinstance(val, str) and val.startswith("http")
def is_image_or_image_url(elem): return is_url(elem) or is_valid_image(elem)
def _prompt_split_image(image_seq_len, image_rows, image_cols, fake_token_around_image, image_token, global_img_token):
    text_split_images = ""
    for n_h in range(image_rows):
        for n_w in range(image_cols): text_split_images += (f"{fake_token_around_image}" + f"<row_{n_h + 1}_col_{n_w + 1}>" + f"{image_token}" * image_seq_len)
        text_split_images += "\n"
    text_split_images += (f"\n{fake_token_around_image}" + f"{global_img_token}" + f"{image_token}" * image_seq_len + f"{fake_token_around_image}")
    return text_split_images
def _prompt_single_image(image_seq_len, fake_token_around_image, image_token, global_img_token): return (f"{fake_token_around_image}" + f"{global_img_token}" + f"{image_token}" * image_seq_len + f"{fake_token_around_image}")
def get_image_prompt_string(image_rows, image_cols, image_seq_len, fake_token_around_image, image_token, global_img_token):
    if image_rows == 0 and image_cols == 0: return _prompt_single_image(image_seq_len, fake_token_around_image=fake_token_around_image, image_token=image_token, global_img_token=global_img_token)
    return _prompt_split_image(image_seq_len, image_rows, image_cols, fake_token_around_image, image_token, global_img_token)
class HurLMImagesKwargs(ImagesKwargs, total=False):
    return_row_col_info: Optional[bool]
    max_image_size: Optional[Dict[str, int]]
class HurLMProcessorKwargs(ProcessingKwargs, total=False):
    images_kwargs: HurLMImagesKwargs
    _defaults = {"text_kwargs": {"add_special_tokens": True, "padding": False, "is_split_into_words": False}, "images_kwargs": {"return_row_col_info": True}}
HurLMProcessorKwargs.__annotations__["images_kwargs"] = HurLMImagesKwargs
class HurLMProcessor(ProcessorMixin):
    attributes = ["image_processor", "tokenizer"]
    image_processor_class = "HurLMImageProcessor"
    tokenizer_class = "AutoTokenizer"
    def __init__(self, image_processor, tokenizer=None, image_seq_len: int = 169, chat_template: str = None, **kwargs):
        if image_processor is None: raise ValueError("You need to specify an `image_processor`.")
        if tokenizer is None: raise ValueError("You need to specify a `tokenizer`.")
        self.fake_image_token = AddedToken("<fake_token_around_image>", normalized=False, special=True)
        self.image_token = AddedToken("<image>", normalized=False, special=True)
        self.end_of_utterance_token = AddedToken("<end_of_utterance>", normalized=False, special=True)
        self.global_image_tag = "<global-img>"
        self.image_seq_len = image_seq_len
        self._regex_to_remove_extra_special_tokens = re.compile(r"(\n?<global-img>\n?|<row_\d+_col_\d+>\n?)+")
        tokens_to_add = {"additional_special_tokens": [self.fake_image_token, self.image_token, self.end_of_utterance_token]}
        tokenizer.add_special_tokens(tokens_to_add)
        super().__init__(image_processor, tokenizer, chat_template=chat_template, **kwargs)
    def _extract_images_from_prompts(self, prompts):
        prompt_images = []
        for prompt in prompts:
            images = []
            for elem in prompt:
                if is_valid_image(elem): images.append(elem)
                elif is_url(elem): images.append(load_image(elem))
            prompt_images.append(images)
        return prompt_images
    def __call__(self, images: Union[ImageInput, List[ImageInput], List[List[ImageInput]]] = None, text: Union[TextInput, "PreTokenizedInput", List[TextInput], List["PreTokenizedInput"]] = None,
    audio=None, videos=None, image_seq_len: Optional[int] = None, **kwargs: Unpack[HurLMProcessorKwargs]) -> BatchEncoding:
        if text is None and images is None: raise ValueError("You must provide either `text` or `images`.")
        output_kwargs = self._merge_kwargs(HurLMProcessorKwargs, tokenizer_init_kwargs=self.tokenizer.init_kwargs, **kwargs)
        image_seq_len = image_seq_len if image_seq_len is not None else self.image_seq_len
        n_images_in_text = []
        n_images_in_images = []
        inputs = BatchFeature()
        if text is not None:
            if isinstance(text, str): text = [text]
            elif not isinstance(text, list) and not isinstance(text[0], str): raise ValueError("Invalid input text. Please provide a string, or a list of strings")
            n_images_in_text = [sample.count(self.image_token.content) for sample in text]
        if images is not None:
            if is_image_or_image_url(images): images = [[images]]
            elif isinstance(images, list) and is_image_or_image_url(images[0]):
                if text is not None:
                    if sum(n_images_in_text) != len(images): raise ValueError(f"The total number of {self.image_token.content} tokens in the prompts should be the same as the number of images passed. Found {sum(n_images_in_text)} {self.image_token.content} tokens and {len(images)} images.")
                    cumsum_images_in_text = [0] + list(accumulate(n_images_in_text))
                    images = [images[cumsum_images_in_text[i] : cumsum_images_in_text[i + 1]] for i in range(len(n_images_in_text))]
                else: images = [images]
            elif (not isinstance(images, list) and not isinstance(images[0], list) and not is_image_or_image_url(images[0][0])): raise ValueError("Invalid input images. Please provide a single image or a list of images or a list of list of images.")
            n_images_in_images = [len(sample) for sample in images]
            images = [[load_image(im) if is_url(im) else im for im in sample] for sample in images]
            image_inputs = self.image_processor(images, **output_kwargs["images_kwargs"])
            inputs.update(image_inputs)
            if text is not None:
                if n_images_in_images != n_images_in_text: raise ValueError(f"The number of images in the text {n_images_in_text} and images {n_images_in_images} should be the same.")
                image_rows = inputs.pop("rows", [[0] * len(text)])
                image_cols = inputs.pop("cols", [[0] * len(text)])
                fake_image_token = self.fake_image_token.content
                image_token = self.image_token.content
                global_img_token = self.global_image_tag
                prompt_strings = []
                for sample, sample_rows, sample_cols in zip(text, image_rows, image_cols):
                    image_prompt_strings = []
                    for n_rows, n_cols in zip(sample_rows, sample_cols):
                        image_prompt_string = get_image_prompt_string(n_rows, n_cols, image_seq_len, image_token=image_token, fake_token_around_image=fake_image_token, global_img_token=global_img_token)
                        image_prompt_strings.append(image_prompt_string)
                    split_sample = sample.split(image_token)
                    if len(split_sample) == 0: raise ValueError("The image token should be present in the text.")
                    sample = split_sample[0]
                    for i, image_prompt_string in enumerate(image_prompt_strings): sample += image_prompt_string + split_sample[i + 1]
                    prompt_strings.append(sample)
                text_inputs = self.tokenizer(text=prompt_strings, **output_kwargs["text_kwargs"])
                inputs.update(text_inputs)
        elif text is not None:
            if any(n_images_in_text): raise ValueError(f"Found {sum(n_images_in_text)} {self.image_token.content} tokens in the text but no images were passed.")
            text_inputs = self.tokenizer(text=text, **output_kwargs["text_kwargs"])
            inputs.update(text_inputs)
        return inputs
    def batch_decode(self, *args, **kwargs):
        batched_decode_output = self.tokenizer.batch_decode(*args, **kwargs)
        return [self._regex_to_remove_extra_special_tokens.sub("<image>", s) for s in batched_decode_output]
    def decode(self, *args, **kwargs):
        decode_output = self.tokenizer.decode(*args, **kwargs)
        return self._regex_to_remove_extra_special_tokens.sub("<image>", decode_output)
    @property
    def model_input_names(self):
        tokenizer_input_names = self.tokenizer.model_input_names
        image_processor_input_names = self.image_processor.model_input_names
        return list(dict.fromkeys(tokenizer_input_names + image_processor_input_names))
__all__ = ["HurLMProcessor"]
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
