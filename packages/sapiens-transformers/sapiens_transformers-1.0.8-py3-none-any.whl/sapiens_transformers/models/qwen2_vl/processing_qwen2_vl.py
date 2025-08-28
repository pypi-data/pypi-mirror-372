"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import List, Union
from ...feature_extraction_utils import BatchFeature
from ...image_utils import ImageInput, VideoInput
from ...processing_utils import ProcessingKwargs, ProcessorMixin, Unpack
from ...tokenization_utils_base import PreTokenizedInput, TextInput
from ...utils import logging
logger = logging.get_logger(__name__)
class Qwen2VLProcessorKwargs(ProcessingKwargs, total=False): _defaults = {"text_kwargs": {'padding': False}}
class Qwen2VLProcessor(ProcessorMixin):
    attributes = ["image_processor", "tokenizer"]
    valid_kwargs = ["chat_template"]
    image_processor_class = "Qwen2VLImageProcessor"
    tokenizer_class = ("Qwen2Tokenizer", "Qwen2TokenizerFast")
    def __init__(self, image_processor=None, tokenizer=None, chat_template=None, **kwargs): super().__init__(image_processor, tokenizer, chat_template=chat_template)
    def __call__(self, images: ImageInput = None, text: Union[TextInput, PreTokenizedInput, List[TextInput], List[PreTokenizedInput]] = None, videos: VideoInput = None,
    **kwargs: Unpack[Qwen2VLProcessorKwargs]) -> BatchFeature:
        output_kwargs = self._merge_kwargs(Qwen2VLProcessorKwargs, tokenizer_init_kwargs=self.tokenizer.init_kwargs, **kwargs)
        if images is not None:
            image_inputs = self.image_processor(images=images, videos=None, **output_kwargs["images_kwargs"])
            image_grid_thw = image_inputs["image_grid_thw"]
        else:
            image_inputs = {}
            image_grid_thw = None
        if videos is not None:
            videos_inputs = self.image_processor(images=None, videos=videos, **output_kwargs["videos_kwargs"])
            video_grid_thw = videos_inputs["video_grid_thw"]
        else:
            videos_inputs = {}
            video_grid_thw = None
        if not isinstance(text, list): text = [text]
        if image_grid_thw is not None:
            merge_length = self.image_processor.merge_size**2
            index = 0
            for i in range(len(text)):
                while "<|image_pad|>" in text[i]:
                    text[i] = text[i].replace("<|image_pad|>", "<|placeholder|>" * (image_grid_thw[index].prod() // merge_length), 1)
                    index += 1
                text[i] = text[i].replace("<|placeholder|>", "<|image_pad|>")
        if video_grid_thw is not None:
            merge_length = self.image_processor.merge_size**2
            index = 0
            for i in range(len(text)):
                while "<|video_pad|>" in text[i]:
                    text[i] = text[i].replace("<|video_pad|>", "<|placeholder|>" * (video_grid_thw[index].prod() // merge_length), 1)
                    index += 1
                text[i] = text[i].replace("<|placeholder|>", "<|video_pad|>")
        _ = output_kwargs["text_kwargs"].pop("padding_side", None)
        text_inputs = self.tokenizer(text, **output_kwargs["text_kwargs"])
        return BatchFeature(data={**text_inputs, **image_inputs, **videos_inputs})
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
