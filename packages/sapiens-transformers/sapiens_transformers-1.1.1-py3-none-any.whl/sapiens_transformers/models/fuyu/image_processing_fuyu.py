"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import math
from typing import Dict, List, Optional, Union
import numpy as np
from ...image_processing_utils import BaseImageProcessor, BatchFeature
from ...image_transforms import (pad, resize, to_channel_dimension_format)
from ...image_utils import (ChannelDimension, ImageInput, PILImageResampling, get_image_size, infer_channel_dimension_format, is_scaled_image, is_valid_image, make_list_of_images,
to_numpy_array, validate_preprocess_arguments)
from ...utils import (TensorType, filter_out_non_signature_kwargs, is_torch_available, is_torch_device, is_torch_dtype, logging, requires_backends)
if is_torch_available(): import torch
logger = logging.get_logger(__name__)
def make_list_of_list_of_images(images: Union[List[List[ImageInput]], List[ImageInput], ImageInput]) -> List[List[ImageInput]]:
    if is_valid_image(images): return [[images]]
    if isinstance(images, list) and all(isinstance(image, list) for image in images): return images
    if isinstance(images, list): return [make_list_of_images(image) for image in images]
    raise ValueError("images must be a list of list of images or a list of images or an image.")
class FuyuBatchFeature(BatchFeature):
    def convert_to_tensors(self, tensor_type: Optional[Union[str, TensorType]] = None):
        if tensor_type is None: return self
        is_tensor, as_tensor = self._get_is_as_tensor_fns(tensor_type=tensor_type)
        def _convert_tensor(elem):
            if is_tensor(elem): return elem
            return as_tensor(elem)
        def _safe_convert_tensor(elem):
            try: return _convert_tensor(elem)
            except:
                if key == "overflowing_values": raise ValueError("Unable to create tensor returning overflowing values of different lengths. ")
                raise ValueError("Unable to create tensor, you should probably activate padding with 'padding=True' to have batched tensors with the same length.")
        for key, value in self.items():
            if isinstance(value, list) and isinstance(value[0], list): self[key] = [[_safe_convert_tensor(elem) for elem in elems] for elems in value]
            elif isinstance(value, list): self[key] = [_safe_convert_tensor(elem) for elem in value]
            else: self[key] = _safe_convert_tensor(value)
        return self
    def to(self, *args, **kwargs) -> "BatchFeature":
        requires_backends(self, ["torch"])
        import torch
        new_data = {}
        device = kwargs.get("device")
        if device is None and len(args) > 0:
            arg = args[0]
            if is_torch_dtype(arg): pass
            elif isinstance(arg, str) or is_torch_device(arg) or isinstance(arg, int): device = arg
            else: raise ValueError(f"Attempting to cast a BatchFeature to type {str(arg)}. This is not supported.")
        def _to(elem):
            if torch.is_floating_point(elem): return elem.to(*args, **kwargs)
            if device is not None: return elem.to(device=device)
            return elem
        for k, v in self.items():
            if isinstance(v, list) and isinstance(v[0], list):
                new_v = []
                for elems in v: new_v.append([_to(elem) for elem in elems])
                new_data[k] = new_v
            elif isinstance(v, list): new_data[k] = [_to(elem) for elem in v]
            else: new_data[k] = _to(v)
        self.data = new_data
        return self
class FuyuImageProcessor(BaseImageProcessor):
    model_input_names = ["images", "image_input_ids", "image_patches", "image_patch_indices_per_batch", "image_patch_indices_per_subsequence"]
    def __init__(self, do_resize: bool = True, size: Optional[Dict[str, int]] = None, resample: PILImageResampling = PILImageResampling.BILINEAR, do_pad: bool = True,
    padding_value: float = 1.0, padding_mode: str = "constant", do_normalize: bool = True, image_mean: Union[float, List[float]] = 0.5, image_std: Union[float, List[float]] = 0.5,
    do_rescale: bool = True, rescale_factor: float = 1 / 255, patch_size: Optional[Dict[str, int]] = None, **kwargs):
        super().__init__(**kwargs)
        self.do_resize = do_resize
        self.size = size if size is not None else {"height": 1080, "width": 1920}
        self.resample = resample
        self.do_pad = do_pad
        self.padding_value = padding_value
        self.padding_mode = padding_mode
        self.do_normalize = do_normalize
        self.image_mean = image_mean
        self.image_std = image_std
        self.do_rescale = do_rescale
        self.rescale_factor = rescale_factor
        self.patch_size = patch_size if patch_size is not None else {"height": 30, "width": 30}
    def resize(self, image: np.ndarray, size: Dict[str, int], resample: PILImageResampling = PILImageResampling.BILINEAR, data_format: Optional[Union[str, ChannelDimension]] = None,
    input_data_format: Optional[Union[str, ChannelDimension]] = None, **kwargs) -> np.ndarray:
        image_height, image_width = get_image_size(image, input_data_format)
        target_height, target_width = size["height"], size["width"]
        if image_width <= target_width and image_height <= target_height: return image
        height_scale_factor = target_height / image_height
        width_scale_factor = target_width / image_width
        optimal_scale_factor = min(height_scale_factor, width_scale_factor)
        new_height = int(image_height * optimal_scale_factor)
        new_width = int(image_width * optimal_scale_factor)
        scaled_image = resize(image=image, size=(new_height, new_width), resample=resample, data_format=data_format, input_data_format=input_data_format, **kwargs)
        return scaled_image
    def pad_image(self, image: np.ndarray, size: Dict[str, int], mode: str = "constant", constant_values: float = 1.0, data_format: Optional[Union[str, ChannelDimension]] = None,
    input_data_format: Optional[Union[str, ChannelDimension]] = None) -> np.ndarray:
        image_height, image_width = get_image_size(image, input_data_format)
        target_height, target_width = size["height"], size["width"]
        padding_top = 0
        padding_left = 0
        padding_bottom = target_height - image_height
        padding_right = target_width - image_width
        padded_image = pad(image, padding=((padding_top, padding_bottom), (padding_left, padding_right)), mode=mode, constant_values=constant_values, data_format=data_format, input_data_format=input_data_format)
        return padded_image
    @filter_out_non_signature_kwargs()
    def preprocess(self, images, do_resize: Optional[bool] = None, size: Optional[Dict[str, int]] = None, resample: Optional[PILImageResampling] = None, do_pad: Optional[bool] = None,
    padding_value: Optional[float] = None, padding_mode: Optional[str] = None, do_normalize: Optional[bool] = None, image_mean: Optional[float] = None, image_std: Optional[float] = None,
    do_rescale: Optional[bool] = None, rescale_factor: Optional[float] = None, patch_size: Optional[Dict[str, int]] = None, data_format: Optional[Union[str, ChannelDimension]] = ChannelDimension.FIRST,
    input_data_format: Optional[Union[str, ChannelDimension]] = None, return_tensors: Optional[TensorType] = None):
        do_resize = do_resize if do_resize is not None else self.do_resize
        size = size if size is not None else self.size
        resample = resample if resample is not None else self.resample
        do_pad = do_pad if do_pad is not None else self.do_pad
        do_rescale = do_rescale if do_rescale is not None else self.do_rescale
        rescale_factor = rescale_factor if rescale_factor is not None else self.rescale_factor
        do_normalize = do_normalize if do_normalize is not None else self.do_normalize
        image_mean = image_mean if image_mean is not None else self.image_mean
        image_std = image_std if image_std is not None else self.image_std
        padding_value = padding_value if padding_value is not None else self.padding_value
        padding_mode = padding_mode if padding_mode is not None else self.padding_mode
        do_rescale = do_rescale if do_rescale is not None else self.do_rescale
        rescale_factor = rescale_factor if rescale_factor is not None else self.rescale_factor
        patch_size = patch_size if patch_size is not None else self.patch_size
        if isinstance(images, list) and any(isinstance(elem, list) and len(elem) >= 2 for elem in images): raise ValueError("Multiple images for a single sample are not yet supported.")
        batch_images = make_list_of_list_of_images(images)
        validate_preprocess_arguments(do_rescale=do_rescale, rescale_factor=rescale_factor, do_normalize=do_normalize, image_mean=image_mean, image_std=image_std, do_pad=do_pad,
        size_divisibility=size, do_resize=do_resize, size=size, resample=resample)
        batch_images = [[to_numpy_array(image) for image in images] for images in batch_images]
        if is_scaled_image(batch_images[0][0]) and do_rescale: logger.warning_once("It looks like you are trying to rescale already rescaled images. If the input images have pixel values between 0 and 1, set `do_rescale=False` to avoid rescaling them again.")
        if input_data_format is None: input_data_format = infer_channel_dimension_format(batch_images[0][0])
        original_image_sizes = [get_image_size(images[0], channel_dim=input_data_format) for images in batch_images]
        if do_resize: batch_images = [[self.resize(image, size=size, input_data_format=input_data_format) for image in images] for images in batch_images]
        image_sizes = [get_image_size(images[0], channel_dim=input_data_format) for images in batch_images]
        image_unpadded_heights = [[image_size[0]] for image_size in image_sizes]
        image_unpadded_widths = [[image_size[1]] for image_size in image_sizes]
        image_scale_factors = [[resized_size[0] / original_size[0]] for original_size, resized_size in zip(original_image_sizes, image_sizes)]
        if do_pad: batch_images = [[self.pad_image(image, size=size, mode=padding_mode, constant_values=padding_value, input_data_format=input_data_format) for image in images] for images in batch_images]
        if do_rescale: batch_images = [[self.rescale(image, scale=rescale_factor, input_data_format=input_data_format) for image in images] for images in batch_images]
        if do_normalize:batch_images = [[self.normalize(image, mean=image_mean, std=image_std, input_data_format=input_data_format) for image in images] for images in batch_images]
        if data_format is not None: batch_images = [[to_channel_dimension_format(image, data_format, input_data_format) for image in images] for images in batch_images]
        data = {"images": batch_images, "image_unpadded_heights": image_unpadded_heights, "image_unpadded_widths": image_unpadded_widths, "image_scale_factors": image_scale_factors}
        return FuyuBatchFeature(data=data, tensor_type=return_tensors)
    def get_num_patches(self, image_height: int, image_width: int, patch_size: Dict[str, int] = None) -> int:
        patch_size = patch_size if patch_size is not None else self.patch_size
        patch_height, patch_width = self.patch_size["height"], self.patch_size["width"]
        if image_height % patch_height != 0: raise ValueError(f"{image_height=} must be divisible by {patch_height}")
        if image_width % patch_width != 0: raise ValueError(f"{image_width=} must be divisible by {patch_width}")
        num_patches_per_dim_h = image_height // patch_height
        num_patches_per_dim_w = image_width // patch_width
        num_patches = num_patches_per_dim_h * num_patches_per_dim_w
        return num_patches
    def patchify_image(self, image: "torch.Tensor", patch_size: Optional[Dict[str, int]] = None) -> "torch.Tensor":
        requires_backends(self, ["torch"])
        patch_size = patch_size if patch_size is not None else self.patch_size
        patch_height, patch_width = patch_size["height"], patch_size["width"]
        batch_size, channels, _, _ = image.shape
        unfolded_along_height = image.unfold(2, patch_height, patch_height)
        patches = unfolded_along_height.unfold(3, patch_width, patch_width)
        patches = patches.contiguous()
        patches = patches.view(batch_size, channels, -1, patch_height, patch_width)
        patches = patches.permute(0, 2, 3, 4, 1)
        patches = patches.reshape(batch_size, -1, channels * patch_height * patch_width)
        return patches
    def preprocess_with_tokenizer_info(self, image_input: "torch.Tensor", image_present: "torch.Tensor", image_unpadded_h: "torch.Tensor", image_unpadded_w: "torch.Tensor",
    image_placeholder_id: int, image_newline_id: int, variable_sized: bool, patch_size: Optional[Dict[str, int]] = None) -> FuyuBatchFeature:
        requires_backends(self, ["torch"])
        patch_size = patch_size if patch_size is not None else self.patch_size
        patch_height, patch_width = patch_size["height"], patch_size["width"]
        images: List[List[torch.Tensor]] = []
        batch_image_patches: List[List[torch.Tensor]] = []
        batch_image_input_ids: List[List[torch.Tensor]] = []
        for batch_index in range(image_input.shape[0]):
            image_input_ids = []
            image_patches = []
            for subseq_index in range(image_input.shape[1]):
                if image_present[batch_index, subseq_index]:
                    image = image_input[batch_index, subseq_index]
                    image_height, image_width = image.shape[1], image.shape[2]
                    if variable_sized:
                        new_h = min(image_height, math.ceil(image_unpadded_h[batch_index, subseq_index] / patch_height) * patch_height)
                        new_w = min(image_width, math.ceil(image_unpadded_w[batch_index, subseq_index] / patch_width) * patch_width)
                        image = image[:, :new_h, :new_w]
                        image_height, image_width = new_h, new_w
                    num_patches = self.get_num_patches(image_height=image_height, image_width=image_width)
                    tensor_of_image_ids = torch.full([num_patches], image_placeholder_id, dtype=torch.int32, device=image_input.device)
                    patches = self.patchify_image(image=image.unsqueeze(0)).squeeze(0)
                    assert num_patches == patches.shape[0]
                    if variable_sized:
                        tensor_of_image_ids = tensor_of_image_ids.reshape(-1, image_width // patch_width)
                        newline_ids = torch.full([tensor_of_image_ids.shape[0], 1], image_newline_id, dtype=torch.int32, device=image_input.device)
                        tensor_of_image_ids = torch.cat([tensor_of_image_ids, newline_ids], dim=1)
                        tensor_of_image_ids = tensor_of_image_ids.reshape(-1)
                    images.append([image])
                    image_input_ids.append(tensor_of_image_ids)
                    image_patches.append(patches)
                else: image_input_ids.append(torch.tensor([], dtype=torch.int32, device=image_input.device))
            batch_image_input_ids.append(image_input_ids)
            batch_image_patches.append(image_patches)
        image_patch_indices_per_batch: List[List[torch.Tensor]] = []
        image_patch_indices_per_subsequence: List[List[torch.Tensor]] = []
        for sample_image_input_ids in batch_image_input_ids:
            index_offset = 0
            per_batch_indices = []
            per_subsequence_indices = []
            for subseq_image_input_ids in sample_image_input_ids:
                patches_mask = subseq_image_input_ids == image_placeholder_id
                num_patches = torch.count_nonzero(patches_mask)
                indices = torch.arange(num_patches, dtype=torch.int64, device=subseq_image_input_ids.device).type_as(subseq_image_input_ids)
                indices_in_stream_per_batch = torch.full_like(subseq_image_input_ids, -1)
                indices_in_stream_per_subsequence = torch.full_like(subseq_image_input_ids, -1)
                patches_inds = torch.nonzero(patches_mask, as_tuple=True)[0]
                indices_in_stream_per_batch[patches_inds] = indices + index_offset
                indices_in_stream_per_subsequence[patches_inds] = indices
                per_batch_indices.append(indices_in_stream_per_batch)
                per_subsequence_indices.append(indices_in_stream_per_subsequence)
                index_offset += num_patches
            image_patch_indices_per_batch.append(per_batch_indices)
            image_patch_indices_per_subsequence.append(per_subsequence_indices)
        return FuyuBatchFeature(data={"images": images, "image_input_ids": batch_image_input_ids, "image_patches": batch_image_patches, "image_patch_indices_per_batch": image_patch_indices_per_batch, "image_patch_indices_per_subsequence": image_patch_indices_per_subsequence})
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
