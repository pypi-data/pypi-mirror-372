'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from typing import Dict, List, Optional, Union
import numpy as np
import torch
from sapiens_transformers.image_processing_utils import BaseImageProcessor, BatchFeature, get_size_dict
from sapiens_transformers.image_transforms import convert_to_rgb, resize, to_channel_dimension_format
from sapiens_transformers.image_utils import OPENAI_CLIP_MEAN, OPENAI_CLIP_STD, ChannelDimension, ImageInput, PILImageResampling, infer_channel_dimension_format, is_scaled_image, make_list_of_images, to_numpy_array, valid_images
from sapiens_transformers.utils import TensorType, is_vision_available
from ...utils import numpy_to_pil
if is_vision_available(): import PIL.Image
class BlipImageProcessor(BaseImageProcessor):
    """Args:"""
    model_input_names = ['pixel_values']
    def __init__(self, do_resize: bool=True, size: Dict[str, int]=None, resample: PILImageResampling=PILImageResampling.BICUBIC, do_rescale: bool=True, rescale_factor: Union[int,
    float]=1 / 255, do_normalize: bool=True, image_mean: Optional[Union[float, List[float]]]=None, image_std: Optional[Union[float, List[float]]]=None,
    do_convert_rgb: bool=True, do_center_crop: bool=True, **kwargs) -> None:
        super().__init__(**kwargs)
        size = size if size is not None else {'height': 224, 'width': 224}
        size = get_size_dict(size, default_to_square=True)
        self.do_resize = do_resize
        self.size = size
        self.resample = resample
        self.do_rescale = do_rescale
        self.rescale_factor = rescale_factor
        self.do_normalize = do_normalize
        self.image_mean = image_mean if image_mean is not None else OPENAI_CLIP_MEAN
        self.image_std = image_std if image_std is not None else OPENAI_CLIP_STD
        self.do_convert_rgb = do_convert_rgb
        self.do_center_crop = do_center_crop
    def resize(self, image: np.ndarray, size: Dict[str, int], resample: PILImageResampling=PILImageResampling.BICUBIC, data_format: Optional[Union[str, ChannelDimension]]=None,
    input_data_format: Optional[Union[str, ChannelDimension]]=None, **kwargs) -> np.ndarray:
        """Returns:"""
        size = get_size_dict(size)
        if 'height' not in size or 'width' not in size: raise ValueError(f'The `size` dictionary must contain the keys `height` and `width`. Got {size.keys()}')
        output_size = (size['height'], size['width'])
        return resize(image, size=output_size, resample=resample, data_format=data_format, input_data_format=input_data_format, **kwargs)
    def preprocess(self, images: ImageInput, do_resize: Optional[bool]=None, size: Optional[Dict[str, int]]=None, resample: PILImageResampling=None, do_rescale: Optional[bool]=None,
    do_center_crop: Optional[bool]=None, rescale_factor: Optional[float]=None, do_normalize: Optional[bool]=None, image_mean: Optional[Union[float, List[float]]]=None,
    image_std: Optional[Union[float, List[float]]]=None, return_tensors: Optional[Union[str, TensorType]]=None, do_convert_rgb: bool=None, data_format: ChannelDimension=ChannelDimension.FIRST,
    input_data_format: Optional[Union[str, ChannelDimension]]=None, **kwargs) -> PIL.Image.Image:
        """Args:"""
        do_resize = do_resize if do_resize is not None else self.do_resize
        resample = resample if resample is not None else self.resample
        do_rescale = do_rescale if do_rescale is not None else self.do_rescale
        rescale_factor = rescale_factor if rescale_factor is not None else self.rescale_factor
        do_normalize = do_normalize if do_normalize is not None else self.do_normalize
        image_mean = image_mean if image_mean is not None else self.image_mean
        image_std = image_std if image_std is not None else self.image_std
        do_convert_rgb = do_convert_rgb if do_convert_rgb is not None else self.do_convert_rgb
        do_center_crop = do_center_crop if do_center_crop is not None else self.do_center_crop
        size = size if size is not None else self.size
        size = get_size_dict(size, default_to_square=False)
        images = make_list_of_images(images)
        if not valid_images(images): raise ValueError('Invalid image type. Must be of type PIL.Image.Image, numpy.ndarray, torch.Tensor, tf.Tensor or jax.ndarray.')
        if do_resize and size is None or resample is None: raise ValueError('Size and resample must be specified if do_resize is True.')
        if do_rescale and rescale_factor is None: raise ValueError('Rescale factor must be specified if do_rescale is True.')
        if do_normalize and (image_mean is None or image_std is None): raise ValueError('Image mean and std must be specified if do_normalize is True.')
        if do_convert_rgb: images = [convert_to_rgb(image) for image in images]
        images = [to_numpy_array(image) for image in images]
        if input_data_format is None: input_data_format = infer_channel_dimension_format(images[0])
        if do_resize: images = [self.resize(image=image, size=size, resample=resample, input_data_format=input_data_format) for image in images]
        if do_rescale: images = [self.rescale(image=image, scale=rescale_factor, input_data_format=input_data_format) for image in images]
        if do_normalize: images = [self.normalize(image=image, mean=image_mean, std=image_std, input_data_format=input_data_format) for image in images]
        if do_center_crop: images = [self.center_crop(image, size, input_data_format=input_data_format) for image in images]
        images = [to_channel_dimension_format(image, data_format, input_channel_dim=input_data_format) for image in images]
        encoded_outputs = BatchFeature(data={'pixel_values': images}, tensor_type=return_tensors)
        return encoded_outputs
    def postprocess(self, sample: torch.Tensor, output_type: str='pil'):
        if output_type not in ['pt', 'np', 'pil']: raise ValueError(f"output_type={output_type} is not supported. Make sure to choose one of ['pt', 'np', or 'pil']")
        sample = (sample / 2 + 0.5).clamp(0, 1)
        if output_type == 'pt': return sample
        sample = sample.cpu().permute(0, 2, 3, 1).numpy()
        if output_type == 'np': return sample
        sample = numpy_to_pil(sample)
        return sample
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
