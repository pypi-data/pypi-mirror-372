"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import Dict, List, Optional, Union
from sapiens_transformers.tokenization_utils_base import PreTokenizedInput, TextInput, TruncationStrategy
from ...processing_utils import ProcessorMixin
from ...utils import PaddingStrategy, TensorType
class NougatProcessor(ProcessorMixin):
    attributes = ["image_processor", "tokenizer"]
    image_processor_class = "AutoImageProcessor"
    tokenizer_class = "AutoTokenizer"
    def __init__(self, image_processor, tokenizer):
        super().__init__(image_processor, tokenizer)
        self.current_processor = self.image_processor
    def __call__(self, images=None, text=None, do_crop_margin: bool = None, do_resize: bool = None, size: Dict[str, int] = None, resample: "PILImageResampling" = None,
    do_thumbnail: bool = None, do_align_long_axis: bool = None, do_pad: bool = None, do_rescale: bool = None, rescale_factor: Union[int, float] = None,
    do_normalize: bool = None, image_mean: Optional[Union[float, List[float]]] = None, image_std: Optional[Union[float, List[float]]] = None,
    data_format: Optional["ChannelDimension"] = "channels_first", input_data_format: Optional[Union[str, "ChannelDimension"]] = None,
    text_pair: Optional[Union[TextInput, PreTokenizedInput, List[TextInput], List[PreTokenizedInput]]] = None,
    text_target: Union[TextInput, PreTokenizedInput, List[TextInput], List[PreTokenizedInput]] = None,
    text_pair_target: Optional[Union[TextInput, PreTokenizedInput, List[TextInput], List[PreTokenizedInput]]] = None,
    add_special_tokens: bool = True, padding: Union[bool, str, PaddingStrategy] = False, truncation: Union[bool, str, TruncationStrategy] = None,
    max_length: Optional[int] = None, stride: int = 0, is_split_into_words: bool = False, pad_to_multiple_of: Optional[int] = None,
    return_tensors: Optional[Union[str, TensorType]] = None, return_token_type_ids: Optional[bool] = None, return_attention_mask: Optional[bool] = None,
    return_overflowing_tokens: bool = False, return_special_tokens_mask: bool = False, return_offsets_mapping: bool = False, return_length: bool = False, verbose: bool = True):
        if images is None and text is None: raise ValueError("You need to specify either an `images` or `text` input to process.")
        if images is not None:
            inputs = self.image_processor(images, do_crop_margin=do_crop_margin, do_resize=do_resize, size=size, resample=resample, do_thumbnail=do_thumbnail, do_align_long_axis=do_align_long_axis,
            do_pad=do_pad, do_rescale=do_rescale, rescale_factor=rescale_factor, do_normalize=do_normalize, image_mean=image_mean, image_std=image_std, return_tensors=return_tensors,
            data_format=data_format, input_data_format=input_data_format)
        if text is not None:
            encodings = self.tokenizer(text, text_pair=text_pair, text_target=text_target, text_pair_target=text_pair_target, add_special_tokens=add_special_tokens,
            padding=padding, truncation=truncation, max_length=max_length, stride=stride, is_split_into_words=is_split_into_words, pad_to_multiple_of=pad_to_multiple_of,
            return_tensors=return_tensors, return_token_type_ids=return_token_type_ids, return_attention_mask=return_attention_mask, return_overflowing_tokens=return_overflowing_tokens,
            return_special_tokens_mask=return_special_tokens_mask, return_offsets_mapping=return_offsets_mapping, return_length=return_length, verbose=verbose)
        if text is None: return inputs
        elif images is None: return encodings
        else:
            inputs["labels"] = encodings["input_ids"]
            return inputs
    def batch_decode(self, *args, **kwargs): return self.tokenizer.batch_decode(*args, **kwargs)
    def decode(self, *args, **kwargs): return self.tokenizer.decode(*args, **kwargs)
    def post_process_generation(self, *args, **kwargs): return self.tokenizer.post_process_generation(*args, **kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
