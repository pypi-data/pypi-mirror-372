"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...processing_utils import ProcessingKwargs, ProcessorMixin, Unpack, _validate_images_text_input_order
from ...image_utils import ImageInput, get_image_size, to_numpy_array
from typing import Union, List
from ...tokenization_utils_base import TextInput, PreTokenizedInput
from ...feature_extraction_utils import BatchFeature
class SAPIImageProcessorKwargs(ProcessingKwargs, total=False): _defaults = {"text_kwargs": {'padding': False}, "images_kwargs": {'do_pad': True}}
class SAPIImageProcessor(ProcessorMixin):
    attributes, valid_kwargs, image_processor_class, tokenizer_class = ["image_processor", "tokenizer"], ["chat_template", "patch_size", "vision_feature_select_strategy", "image_token"], "AutoImageProcessor", "AutoTokenizer"
    def __init__(self, image_processor=None, tokenizer=None, patch_size=None, vision_feature_select_strategy=None, chat_template=None, image_token="<image>", **kwargs):
        self.patch_size, self.vision_feature_select_strategy, self.image_token = patch_size, vision_feature_select_strategy, image_token
        super().__init__(image_processor, tokenizer, chat_template=chat_template)
    def _get_unpadded_features(self, height, width, patches_height, patches_width, scale_height, scale_width):
        current_height, current_width = patches_height * scale_height, patches_width * scale_width
        original_aspect_ratio, current_aspect_ratio = width / height, current_width / current_height
        if original_aspect_ratio > current_aspect_ratio: current_height -= ((current_height - ((height * current_width) // width)) // 2) * 2
        else: current_width -= ((current_width - ((width * current_height) // height)) // 2) * 2
        return (current_height * current_width, current_height)
    def _get_number_of_features(self, orig_height: int, orig_width: int, height: int, width: int) -> int:
        from ...image_processing_utils import select_best_resolution
        image_grid_pinpoints = self.image_processor.image_grid_pinpoints
        height_best_resolution, width_best_resolution = select_best_resolution([orig_height, orig_width], image_grid_pinpoints)
        scale_height, scale_width = height_best_resolution // height, width_best_resolution // width
        patches_height, patches_width = height // self.patch_size, width // self.patch_size
        unpadded_features, newline_features = self._get_unpadded_features(orig_height, orig_width, patches_height, patches_width, scale_height, scale_width)
        return unpadded_features + newline_features + (patches_height * patches_width + 1)
    def __call__(self, images: ImageInput = None, text: Union[TextInput, PreTokenizedInput, List[TextInput], List[PreTokenizedInput]] = None, audio=None, videos=None,
    **kwargs: Unpack[SAPIImageProcessorKwargs]) -> BatchFeature:
        if images is None and text is None: raise ValueError("You have to specify at least images or text.")
        images, text = _validate_images_text_input_order(images, text)
        output_kwargs, prompt_strings = self._merge_kwargs(SAPIImageProcessorKwargs, tokenizer_init_kwargs=self.tokenizer.init_kwargs, **kwargs), text
        if images is not None: image_inputs = self.image_processor(images, **output_kwargs["images_kwargs"])
        else: image_inputs = {}
        if isinstance(text, str): text = [text]
        elif not isinstance(text, list) and not isinstance(text[0], str): raise ValueError("Invalid input text. Please provide a string, or a list of strings")
        if image_inputs:
            if self.patch_size is not None and self.vision_feature_select_strategy is not None:
                image_sizes, prompt_strings = iter(image_inputs["image_sizes"]), []
                height, width = get_image_size(to_numpy_array(image_inputs["pixel_values"][0][0]))
                for sample in text:
                    while self.image_token in sample:
                        orig_height, orig_width = next(image_sizes)
                        num_image_tokens = self._get_number_of_features(orig_height, orig_width, height, width)
                        if self.vision_feature_select_strategy == "default": num_image_tokens -= 1
                        sample = sample.replace(self.image_token, "<placeholder>" * num_image_tokens, 1)
                    prompt_strings.append(sample)
                prompt_strings = [sample.replace("<placeholder>", self.image_token) for sample in prompt_strings]
        text_inputs = self.tokenizer(prompt_strings, **output_kwargs["text_kwargs"])
        return BatchFeature(data={**text_inputs, **image_inputs})
    def batch_decode(self, *args, **kwargs): return self.tokenizer.batch_decode(*args, **kwargs)
    def decode(self, *args, **kwargs): return self.tokenizer.decode(*args, **kwargs)
    @property
    def model_input_names(self): return list(dict.fromkeys(self.tokenizer.model_input_names + self.image_processor.model_input_names))
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
