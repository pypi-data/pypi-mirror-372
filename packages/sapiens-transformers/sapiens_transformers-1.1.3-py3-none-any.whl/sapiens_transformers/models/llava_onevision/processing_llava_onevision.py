"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import math
import os
from typing import Iterable, List, Union
from ...feature_extraction_utils import BatchFeature
from ...image_processing_utils import select_best_resolution
from ...image_utils import ImageInput, VideoInput, get_image_size, to_numpy_array
from ...processing_utils import ProcessingKwargs, ProcessorMixin, Unpack
from ...tokenization_utils_base import PreTokenizedInput, TextInput
from ...utils import logging
from ..auto import AutoImageProcessor
logger = logging.get_logger(__name__)
class LlavaOnevisionProcessorKwargs(ProcessingKwargs, total=False): _defaults = {"text_kwargs": {'padding': False}, "image_kwargs": {}, "video_kwargs": {}}
class LlavaOnevisionProcessor(ProcessorMixin):
    attributes = ["image_processor", "tokenizer", "video_processor"]
    valid_kwargs = ["chat_template", "num_image_tokens", "vision_feature_select_strategy", "image_token", "video_token"]
    image_processor_class = "AutoImageProcessor"
    tokenizer_class = "AutoTokenizer"
    video_processor_class = "LlavaOnevisionVideoProcessor"
    def __init__(self, image_processor=None, tokenizer=None, video_processor=None, num_image_tokens=None, vision_feature_select_strategy=None, chat_template=None,
    image_token="<image>", video_token="<video>", **kwargs):
        self.num_image_tokens = num_image_tokens
        self.vision_feature_select_strategy = vision_feature_select_strategy
        self.image_token = image_token
        self.video_token = video_token
        super().__init__(image_processor, tokenizer, video_processor, chat_template=chat_template)
    def __call__(self, images: ImageInput = None, text: Union[TextInput, PreTokenizedInput, List[TextInput], List[PreTokenizedInput]] = None, audio=None,
    videos: VideoInput = None, **kwargs: Unpack[LlavaOnevisionProcessorKwargs]) -> BatchFeature:
        output_kwargs = self._merge_kwargs(LlavaOnevisionProcessorKwargs, tokenizer_init_kwargs=self.tokenizer.init_kwargs, **kwargs)
        if isinstance(text, str): text = [text]
        elif not isinstance(text, list) and not isinstance(text[0], str): raise ValueError("Invalid input text. Please provide a string, or a list of strings")
        image_inputs = video_inputs = {}
        if images is not None:
            image_inputs = self.image_processor(images, **output_kwargs["images_kwargs"])
            image_sizes = iter(image_inputs["image_sizes"])
            height, width = get_image_size(to_numpy_array(image_inputs["pixel_values"][0][0]), channel_dim=output_kwargs["images_kwargs"].get("data_format"))
            text = self._expand_image_tokens(text, image_sizes, height, width, self.image_token)
        if videos is not None:
            video_inputs = self.video_processor(videos, **output_kwargs["videos_kwargs"])
            one_video = to_numpy_array(video_inputs["pixel_values_videos"][0])
            height, width = get_image_size(one_video[0], channel_dim=output_kwargs["images_kwargs"].get("data_format"))
            num_frames = one_video.shape[0]
            patches_height_width = int(math.sqrt(self.num_image_tokens))
            pooled_height_width = math.ceil(patches_height_width / 2)
            num_video_tokens = (num_frames * pooled_height_width * pooled_height_width) + 1
            text = [sample.replace(self.video_token, self.video_token * num_video_tokens) for sample in text]
        _ = output_kwargs["text_kwargs"].pop("padding_side", None)
        text_inputs = self.tokenizer(text, **output_kwargs["text_kwargs"])
        return BatchFeature(data={**text_inputs, **image_inputs, **video_inputs})
    def _expand_image_tokens(self, text: List[TextInput], image_sizes: Iterable[Union[List[int], int]], height: int, width: int, special_token: str, num_frames: int = 1):
        prompt_strings = []
        for sample in text:
            while special_token in sample:
                image_size_list = next(image_sizes)
                orig_height, orig_width = image_size_list[0] if num_frames != 1 else image_size_list
                num_image_tokens = self._get_number_of_features(orig_height, orig_width, height, width)
                if self.vision_feature_select_strategy == "default": num_image_tokens -= 1
                sample = sample.replace(special_token, "<placeholder>" * num_image_tokens * num_frames, 1)
            prompt_strings.append(sample)
        text = [sample.replace("<placeholder>", special_token) for sample in prompt_strings]
        return text
    def _get_number_of_features(self, orig_height: int, orig_width: int, height: int, width: int) -> int:
        image_grid_pinpoints = self.image_processor.image_grid_pinpoints
        height_best_resolution, width_best_resolution = select_best_resolution([orig_height, orig_width], image_grid_pinpoints)
        scale_height, scale_width = height_best_resolution // height, width_best_resolution // width
        patches_height = patches_width = int(math.sqrt(self.num_image_tokens))
        unpadded_features, newline_features = self._get_unpadded_features(orig_height, orig_width, patches_height, patches_width, scale_height, scale_width)
        base_features = self.num_image_tokens
        num_image_tokens = unpadded_features + newline_features + base_features
        return num_image_tokens
    def _get_unpadded_features(self, height, width, patches_height, patches_width, scale_height, scale_width):
        current_height = patches_height * scale_height
        current_width = patches_width * scale_width
        original_aspect_ratio = width / height
        current_aspect_ratio = current_width / current_height
        if original_aspect_ratio > current_aspect_ratio:
            new_height = int(height * (current_width / width))
            padding = (current_height - new_height) // 2
            current_height -= padding * 2
        else:
            new_width = int(width * (current_height / height))
            padding = (current_width - new_width) // 2
            current_width -= padding * 2
        unpadded_features = current_height * current_width
        newline_features = current_height
        ratio = math.sqrt(current_height * current_width / (9 * patches_height**2))
        if ratio > 1.1:
            unpadded_features = int(current_height // ratio) * int(current_width // ratio)
            newline_features = int(current_height // ratio)
        return (unpadded_features, newline_features)
    def batch_decode(self, *args, **kwargs): return self.tokenizer.batch_decode(*args, **kwargs)
    def decode(self, *args, **kwargs): return self.tokenizer.decode(*args, **kwargs)
    @property
    def model_input_names(self):
        tokenizer_input_names = self.tokenizer.model_input_names
        image_processor_input_names = self.image_processor.model_input_names
        return list(dict.fromkeys(tokenizer_input_names + image_processor_input_names))
    def save_pretrained(self, save_directory, **kwargs):
        if os.path.isfile(save_directory): raise ValueError(f"Provided path ({save_directory}) should be a directory, not a file")
        os.makedirs(save_directory, exist_ok=True)
        video_processor_path = os.path.join(save_directory, "video_processor")
        self.video_processor.save_pretrained(video_processor_path)
        video_processor_present = "video_processor" in self.attributes
        if video_processor_present: self.attributes.remove("video_processor")
        outputs = super().save_pretrained(save_directory, **kwargs)
        if video_processor_present: self.attributes += ["video_processor"]
        return outputs
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path, **kwargs):
        processor = super().from_pretrained(pretrained_model_name_or_path, **kwargs)
        if isinstance(processor, tuple): processor = processor[0]
        try:
            video_processor = AutoImageProcessor.from_pretrained(pretrained_model_name_or_path, subfolder="video_processor")
            processor.video_processor = video_processor
        except EnvironmentError: logger.info("You are loading `LlavaOnevisionProcessor` but the indicated `path` doesn't contain a folder called `video_processor`. It is strongly recommended to load and save the processor again so the video processor is saved in a separate config.")
        return processor
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
