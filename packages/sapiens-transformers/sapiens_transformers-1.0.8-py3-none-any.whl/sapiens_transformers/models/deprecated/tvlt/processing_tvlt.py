"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ....processing_utils import ProcessorMixin
class TvltProcessor(ProcessorMixin):
    attributes = ["image_processor", "feature_extractor"]
    image_processor_class = "TvltImageProcessor"
    feature_extractor_class = "TvltFeatureExtractor"
    def __init__(self, image_processor, feature_extractor):
        super().__init__(image_processor=image_processor, feature_extractor=feature_extractor)
        self.image_processor = image_processor
        self.feature_extractor = feature_extractor
    def __call__(self, images=None, audio=None, images_mixed=None, sampling_rate=None, mask_audio=False, mask_pixel=False, *args, **kwargs):
        if images is None and audio is None: raise ValueError("You need to specify either an `images` or `audio` input to process.")
        images_mixed_dict = None
        if images is not None: images_dict = self.image_processor(images, mask_pixel=mask_pixel, *args, **kwargs)
        if images_mixed is not None: images_mixed_dict = self.image_processor(images_mixed, is_mixed=True, *args, **kwargs)
        if audio is not None: audio_dict = self.feature_extractor(audio, *args, sampling_rate=sampling_rate, mask_audio=mask_audio, **kwargs)
        output_dict = {}
        if audio is not None: output_dict.update(audio_dict)
        if images is not None: output_dict.update(images_dict)
        if images_mixed_dict is not None: output_dict.update(images_mixed_dict)
        return output_dict
    @property
    def model_input_names(self):
        image_processor_input_names = self.image_processor.model_input_names
        feature_extractor_input_names = self.feature_extractor.model_input_names
        return list(dict.fromkeys(image_processor_input_names + feature_extractor_input_names))
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
