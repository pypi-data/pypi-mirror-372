"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING, List, Optional, Union
from ...feature_extraction_utils import BatchFeature
from ...image_processing_utils import select_best_resolution
from ...image_utils import ImageInput, VideoInput, get_image_size, to_numpy_array
from ...processing_utils import ProcessorMixin
from ...tokenization_utils_base import PaddingStrategy, PreTokenizedInput, TextInput, TruncationStrategy
from ...utils import TensorType, logging
if TYPE_CHECKING: pass
logger = logging.get_logger(__name__)
class LlavaNextVideoProcessor(ProcessorMixin):
    attributes = ["video_processor", "image_processor", "tokenizer"]
    valid_kwargs = ["chat_template", "patch_size", "vision_feature_select_strategy", "image_token", "video_token"]
    image_processor_class = "LlavaNextImageProcessor"
    video_processor_class = "LlavaNextVideoImageProcessor"
    tokenizer_class = ("LlamaTokenizer", "LlamaTokenizerFast")
    def __init__(self, video_processor=None, image_processor=None, tokenizer=None, chat_template=None, patch_size=None, vision_feature_select_strategy=None,
    video_token="<video>", image_token="<image>", **kwargs):
        self.patch_size = patch_size
        self.vision_feature_select_strategy = vision_feature_select_strategy
        self.image_token = image_token
        self.video_token = video_token
        super().__init__(video_processor, image_processor, tokenizer, chat_template=chat_template)
    def __call__(self, text: Union[TextInput, PreTokenizedInput, List[TextInput], List[PreTokenizedInput]], images: ImageInput = None, videos: VideoInput = None,
    padding: Union[bool, str, PaddingStrategy] = False, truncation: Union[bool, str, TruncationStrategy] = None, max_length: int = None,
    return_tensors: Optional[Union[str, TensorType]] = TensorType.PYTORCH) -> BatchFeature:
        if images is not None: image_inputs = self.image_processor(images, return_tensors=return_tensors)
        else: image_inputs = {}
        if videos is not None: videos_inputs = self.video_processor(videos, return_tensors=return_tensors)
        else: videos_inputs = {}
        if isinstance(text, str): text = [text]
        elif not isinstance(text, list) and not isinstance(text[0], str): raise ValueError("Invalid input text. Please provide a string, or a list of strings")
        if self.patch_size is None or self.vision_feature_select_strategy is None: logger.warning_once("Expanding inputs for image/video tokens in LLaVa-NeXT-Video should be done in processing. Please add `patch_size` and `vision_feature_select_strategy` to the model's processing config or set directly with `processor.patch_size = {{patch_size}}` and processor.vision_feature_select_strategy = {{vision_feature_select_strategy}}`. Using processors without these attributes in the config is deprecated and will throw an error in v1.0.")
        else:
            if image_inputs:
                image_sizes = iter(image_inputs["image_sizes"])
                height, width = get_image_size(to_numpy_array(image_inputs["pixel_values"][0][0]))
                prompt_strings = []
                for sample in text:
                    while self.image_token in sample:
                        image_size = next(image_sizes)
                        orig_height, orig_width = image_size
                        num_image_tokens = self._get_number_of_features(orig_height, orig_width, height, width)
                        if self.vision_feature_select_strategy == "default": num_image_tokens -= 1
                        sample = sample.replace(self.image_token, "<placeholder>" * num_image_tokens, 1)
                    prompt_strings.append(sample)
                text = [sample.replace("<placeholder>", self.image_token) for sample in prompt_strings]
            if videos_inputs:
                one_video = to_numpy_array(videos_inputs.get("pixel_values_videos")[0])
                height, width = get_image_size(one_video[0])
                num_frames = one_video.shape[0]
                num_image_tokens = (height // self.patch_size) * (width // self.patch_size)
                num_video_tokens = num_image_tokens // 4 * num_frames
                prompt_strings = []
                for sample in text:
                    sample = sample.replace(self.video_token, self.video_token * num_video_tokens)
                    prompt_strings.append(sample)
                text = prompt_strings
        text_inputs = self.tokenizer(text, return_tensors=return_tensors, padding=padding, truncation=truncation, max_length=max_length)
        return BatchFeature(data={**text_inputs, **image_inputs, **videos_inputs})
    def _get_number_of_features(self, orig_height: int, orig_width: int, height: int, width: int) -> int:
        image_grid_pinpoints = self.image_processor.image_grid_pinpoints
        height_best_resolution, width_best_resolution = select_best_resolution([orig_height, orig_width], image_grid_pinpoints)
        scale_height, scale_width = height_best_resolution // height, width_best_resolution // width
        patches_height = height // self.patch_size
        patches_width = width // self.patch_size
        unpadded_features, newline_features = self._get_unpadded_features(orig_height, orig_width, patches_height, patches_width, scale_height, scale_width)
        base_features = patches_height * patches_width + 1
        num_image_tokens = unpadded_features + newline_features + base_features
        return num_image_tokens
    def _get_unpadded_features(self, height, width, patches_height, patches_width, scale_height, scale_width):
        current_height = patches_height * scale_height
        current_width = patches_width * scale_width
        original_aspect_ratio = width / height
        current_aspect_ratio = current_width / current_height
        if original_aspect_ratio > current_aspect_ratio:
            new_height = (height * current_width) // width
            padding = (current_height - new_height) // 2
            current_height -= padding * 2
        else:
            new_width = (width * current_height) // height
            padding = (current_width - new_width) // 2
            current_width -= padding * 2
        unpadded_features = current_height * current_width
        newline_features = current_height
        return (unpadded_features, newline_features)
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
