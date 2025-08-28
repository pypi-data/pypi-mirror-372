"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import List, Union
from ...feature_extraction_utils import BatchFeature
from ...image_utils import ImageInput, is_valid_image, load_image
from ...processing_utils import ProcessingKwargs, ProcessorMixin, Unpack, _validate_images_text_input_order
from ...tokenization_utils_base import PreTokenizedInput, TextInput
from ...utils import is_torch_device, is_torch_dtype, is_torch_tensor, logging, requires_backends
logger = logging.get_logger(__name__)
class PixtralProcessorKwargs(ProcessingKwargs, total=False): _defaults = {"text_kwargs": {'padding': False}, "images_kwargs": {}, "common_kwargs": {'return_tensors': 'pt'}}
def is_url(val) -> bool: return isinstance(val, str) and val.startswith("http")
def is_image_or_image_url(elem): return is_url(elem) or is_valid_image(elem)
class BatchMixFeature(BatchFeature):
    def to(self, *args, **kwargs) -> "BatchMixFeature":
        requires_backends(self, ["torch"])
        import torch
        new_data = {}
        device = kwargs.get("device")
        if device is None and len(args) > 0:
            arg = args[0]
            if is_torch_dtype(arg): pass
            elif isinstance(arg, str) or is_torch_device(arg) or isinstance(arg, int): device = arg
            else: raise ValueError(f"Attempting to cast a BatchFeature to type {str(arg)}. This is not supported.")
        for k, v in self.items():
            if isinstance(v, list): new_data[k] = [element.to(*args, **kwargs) for sample in v for element in sample if is_torch_tensor(element)]
            elif torch.is_floating_point(v): new_data[k] = v.to(*args, **kwargs)
            elif device is not None: new_data[k] = v.to(device=device)
            else: new_data[k] = v
        self.data = new_data
        return self
class PixtralProcessor(ProcessorMixin):
    attributes = ["image_processor", "tokenizer"]
    valid_kwargs = ["chat_template", "patch_size", "image_token", "image_break_token", "image_end_token"]
    image_processor_class = "AutoImageProcessor"
    tokenizer_class = "AutoTokenizer"
    def __init__(self, image_processor=None, tokenizer=None, patch_size: int = 16, chat_template=None, image_token="[IMG]", image_break_token="[IMG_BREAK]",
    image_end_token="[IMG_END]", **kwargs):
        self.patch_size = patch_size
        self.image_token = image_token
        self.image_break_token = image_break_token
        self.image_end_token = image_end_token
        super().__init__(image_processor, tokenizer, chat_template=chat_template)
    def __call__(self, images: ImageInput = None, text: Union[TextInput, PreTokenizedInput, List[TextInput], List[PreTokenizedInput]] = None, audio=None, videos=None,
    **kwargs: Unpack[PixtralProcessorKwargs]) -> BatchMixFeature:
        images, text = _validate_images_text_input_order(images, text)
        output_kwargs = self._merge_kwargs(PixtralProcessorKwargs, tokenizer_init_kwargs=self.tokenizer.init_kwargs, **kwargs)
        if images is not None:
            if is_image_or_image_url(images): images = [[images]]
            elif isinstance(images, list) and is_image_or_image_url(images[0]): images = [images]
            elif (not isinstance(images, list) and not isinstance(images[0], list) and not is_image_or_image_url(images[0][0])): raise ValueError("Invalid input images. Please provide a single image or a list of images or a list of list of images.")
            images = [[load_image(im) for im in sample] for sample in images]
            image_inputs = self.image_processor(images, patch_size=self.patch_size, **output_kwargs["images_kwargs"])
        else: image_inputs = {}
        if isinstance(text, str): text = [text]
        elif not isinstance(text, list) and not isinstance(text[0], str): raise ValueError("Invalid input text. Please provide a string, or a list of strings")
        prompt_strings = text
        if image_inputs.get("pixel_values") is not None:
            images = image_inputs["pixel_values"]
            image_sizes = image_inputs.pop("image_sizes")
            prompt_strings = []
            for sample_images, sample_image_sizes, sample in zip(images, image_sizes, text):
                replace_strings = []
                for image, image_size in zip(sample_images, sample_image_sizes):
                    height, width = image_size
                    num_height_tokens = height // self.patch_size
                    num_width_tokens = width // self.patch_size
                    replace_tokens = [[self.image_token] * num_width_tokens + [self.image_break_token]] * num_height_tokens
                    replace_tokens = [item for sublist in replace_tokens for item in sublist]
                    replace_tokens[-1] = self.image_end_token
                    replace_str = "".join(replace_tokens)
                    replace_strings.append(replace_str)
                    sample = sample.replace(self.image_token, "<placeholder>", 1)
                while "<placeholder>" in sample:
                    replace_str = replace_strings.pop(0)
                    sample = sample.replace("<placeholder>", replace_str, 1)
                prompt_strings.append(sample)
        text_inputs = self.tokenizer(prompt_strings, **output_kwargs["text_kwargs"])
        return BatchMixFeature(data={**text_inputs, **image_inputs})
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
