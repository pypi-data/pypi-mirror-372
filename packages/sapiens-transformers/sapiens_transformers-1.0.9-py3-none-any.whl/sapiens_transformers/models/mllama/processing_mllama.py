"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import List, Optional, Union
import numpy as np
try: from typing import Unpack
except ImportError: from typing_extensions import Unpack
from ...feature_extraction_utils import BatchFeature
from ...image_utils import ImageInput
from ...processing_utils import (ImagesKwargs, ProcessingKwargs, ProcessorMixin)
from ...tokenization_utils_base import (BatchEncoding, PreTokenizedInput, TextInput)
from .image_processing_mllama import make_list_of_images
class MllamaImagesKwargs(ImagesKwargs, total=False): max_image_tiles: Optional[int]
class MllamaProcessorKwargs(ProcessingKwargs, total=False):
    images_kwargs: MllamaImagesKwargs
    _defaults = {"image_kwargs": {'max_image_tiles': 4}}
def get_cross_attention_token_mask(input_ids: List[int], image_token_id: int) -> List[List[int]]:
    image_token_locations = [i for i, token in enumerate(input_ids) if token == image_token_id]
    if len(image_token_locations) == 0: return []
    if len(image_token_locations) == 1: return [[image_token_locations[0], -1]]
    vision_masks = [[loc1, loc2] for loc1, loc2 in zip(image_token_locations[:-1], image_token_locations[1:])]
    vision_masks.append([image_token_locations[-1], len(input_ids)])
    last_mask_end = vision_masks[-1][1]
    for vision_mask in vision_masks[::-1]:
        if vision_mask[0] == vision_mask[1] - 1: vision_mask[1] = last_mask_end
        last_mask_end = vision_mask[1]
    return vision_masks
def convert_sparse_cross_attention_mask_to_dense(cross_attention_token_mask: List[List[List[int]]], num_tiles: List[List[int]], max_num_tiles: int, length: int) -> np.ndarray:
    batch_size = len(cross_attention_token_mask)
    max_num_images = max([len(masks) for masks in cross_attention_token_mask])
    cross_attention_mask = np.zeros(shape=(batch_size, length, max_num_images, max_num_tiles), dtype=np.int64)
    for sample_idx, (sample_masks, sample_num_tiles) in enumerate(zip(cross_attention_token_mask, num_tiles)):
        for mask_idx, (locations, mask_num_tiles) in enumerate(zip(sample_masks, sample_num_tiles)):
            if len(locations) == 2:
                start, end = locations
                end = min(end, length)
                if end == -1: end = length
                cross_attention_mask[sample_idx, start:end, mask_idx, :mask_num_tiles] = 1
    return cross_attention_mask
def build_string_from_input(prompt: str, bos_token: str, image_token: str) -> str:
    if bos_token in prompt: return prompt
    num_image_tokens_on_start = 0
    while prompt.startswith(image_token):
        prompt = prompt[len(image_token) :]
        num_image_tokens_on_start += 1
    return f"{image_token * num_image_tokens_on_start}{bos_token}{prompt}"
class MllamaProcessor(ProcessorMixin):
    attributes = ["image_processor", "tokenizer"]
    image_processor_class = "MllamaImageProcessor"
    tokenizer_class = "PreTrainedTokenizerFast"
    def __init__(self, image_processor, tokenizer):
        self.image_token = "<|image|>"
        self.image_token_id = tokenizer.convert_tokens_to_ids(self.image_token)
        self.python_token = "<|python_tag|>"
        self.python_token_id = tokenizer.convert_tokens_to_ids(self.python_token)
        self.bos_token = tokenizer.bos_token
        self.chat_template = tokenizer.chat_template
        super().__init__(image_processor, tokenizer)
    def __call__(self, images: Optional[ImageInput] = None, text: Optional[Union[TextInput, PreTokenizedInput, List[TextInput], List[PreTokenizedInput]]] = None, **kwargs: Unpack[MllamaProcessorKwargs]) -> BatchEncoding:
        if text is None and images is None: raise ValueError("You must specify either text or images.")
        output_kwargs = self._merge_kwargs(MllamaProcessorKwargs, tokenizer_init_kwargs=self.tokenizer.init_kwargs, **kwargs)
        text_kwargs = output_kwargs["text_kwargs"]
        images_kwargs = output_kwargs["images_kwargs"]
        common_kwargs = output_kwargs["common_kwargs"]
        data = {}
        if text is not None:
            if isinstance(text, str): text = [text]
            elif not (isinstance(text, (list, tuple)) and all(isinstance(t, str) for t in text)): raise ValueError("Invalid input text. Please provide a string, or a list of strings")
            n_images_in_text = [t.count(self.image_token) for t in text]
            text = [build_string_from_input(text_item, self.bos_token, self.image_token) for text_item in text]
            _ = text_kwargs.pop("padding_side", None)
            encoding = self.tokenizer(text, **text_kwargs)
            data.update(encoding)
        n_images_in_images = [0]
        if images is not None:
            images = make_list_of_images(images)
            n_images_in_images = [len(sample) for sample in images]
        if text is not None:
            if any(batch_img == 0 for batch_img in n_images_in_text) and not all(batch_img == 0 for batch_img in n_images_in_text): raise ValueError("If a batch of text is provided, there should be either no images or at least one image per sample")
            if sum(n_images_in_images) != sum(n_images_in_text):
                if images is None: raise ValueError("No image were provided, but there are image tokens in the prompt")
                else: raise ValueError(f"The number of image token ({sum(n_images_in_images)}) should be the same as in the number of provided images ({sum(n_images_in_images)})")
        if images is not None:
            image_features = self.image_processor(images, **images_kwargs)
            num_tiles = image_features.pop("num_tiles")
            data.update(image_features)
        if images is not None and text is not None:
            cross_attention_token_mask = [get_cross_attention_token_mask(token_ids, self.image_token_id) for token_ids in encoding["input_ids"]]
            cross_attention_mask = convert_sparse_cross_attention_mask_to_dense(cross_attention_token_mask, num_tiles=num_tiles, max_num_tiles=self.image_processor.max_image_tiles,
            length=max(len(input_ids) for input_ids in encoding["input_ids"]))
            data["cross_attention_mask"] = cross_attention_mask
        return_tensors = common_kwargs.pop("return_tensors", None)
        batch_encoding = BatchFeature(data=data, tensor_type=return_tensors)
        return batch_encoding
    def batch_decode(self, *args, **kwargs): return self.tokenizer.batch_decode(*args, **kwargs)
    def decode(self, *args, **kwargs): return self.tokenizer.decode(*args, **kwargs)
    @property
    def model_input_names(self):
        tokenizer_input_names = self.tokenizer.model_input_names
        image_processor_input_names = self.image_processor.model_input_names
        return list(tokenizer_input_names + image_processor_input_names + ["cross_attention_mask"])
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
