"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import io
import math
from typing import Dict, Optional, Union
import numpy as np
from huggingface_hub import hf_hub_download
from ...image_processing_utils import BaseImageProcessor, BatchFeature
from ...image_transforms import convert_to_rgb, normalize, to_channel_dimension_format, to_pil_image
from ...image_utils import (ChannelDimension, ImageInput, get_image_size, infer_channel_dimension_format, make_list_of_images, to_numpy_array, valid_images)
from ...utils import TensorType, is_torch_available, is_vision_available, logging
from ...utils.import_utils import requires_backends
if is_vision_available():
    import textwrap
    from PIL import Image, ImageDraw, ImageFont
if is_torch_available(): import torch
logger = logging.get_logger(__name__)
DEFAULT_FONT_PATH = "ybelkada/fonts"
def torch_extract_patches(image_tensor, patch_height, patch_width):
    requires_backends(torch_extract_patches, ["torch"])
    image_tensor = image_tensor.unsqueeze(0)
    patches = torch.nn.functional.unfold(image_tensor, (patch_height, patch_width), stride=(patch_height, patch_width))
    patches = patches.reshape(image_tensor.size(0), image_tensor.size(1), patch_height, patch_width, -1)
    patches = patches.permute(0, 4, 2, 3, 1).reshape(image_tensor.size(2) // patch_height, image_tensor.size(3) // patch_width, image_tensor.size(1) * patch_height * patch_width)
    return patches.unsqueeze(0)
def render_text(text: str, text_size: int = 36, text_color: str = "black", background_color: str = "white", left_padding: int = 5, right_padding: int = 5, top_padding: int = 5,
bottom_padding: int = 5, font_bytes: Optional[bytes] = None, font_path: Optional[str] = None) -> Image.Image:
    requires_backends(render_text, "vision")
    wrapper = textwrap.TextWrapper(width=80)
    lines = wrapper.wrap(text=text)
    wrapped_text = "\n".join(lines)
    if font_bytes is not None and font_path is None: font = io.BytesIO(font_bytes)
    elif font_path is not None: font = font_path
    else: font = hf_hub_download(DEFAULT_FONT_PATH, "Arial.TTF")
    font = ImageFont.truetype(font, encoding="UTF-8", size=text_size)
    temp_draw = ImageDraw.Draw(Image.new("RGB", (1, 1), background_color))
    _, _, text_width, text_height = temp_draw.textbbox((0, 0), wrapped_text, font)
    image_width = text_width + left_padding + right_padding
    image_height = text_height + top_padding + bottom_padding
    image = Image.new("RGB", (image_width, image_height), background_color)
    draw = ImageDraw.Draw(image)
    draw.text(xy=(left_padding, top_padding), text=wrapped_text, fill=text_color, font=font)
    return image
def render_header(image: np.ndarray, header: str, input_data_format: Optional[Union[str, ChildProcessError]] = None, **kwargs):
    requires_backends(render_header, "vision")
    image = to_pil_image(image, input_data_format=input_data_format)
    header_image = render_text(header, **kwargs)
    new_width = max(header_image.width, image.width)
    new_height = int(image.height * (new_width / image.width))
    new_header_height = int(header_image.height * (new_width / header_image.width))
    new_image = Image.new("RGB", (new_width, new_height + new_header_height), "white")
    new_image.paste(header_image.resize((new_width, new_header_height)), (0, 0))
    new_image.paste(image.resize((new_width, new_height)), (0, new_header_height))
    new_image = to_numpy_array(new_image)
    if infer_channel_dimension_format(new_image) == ChannelDimension.LAST: new_image = to_channel_dimension_format(new_image, ChannelDimension.LAST)
    return new_image
class Pix2StructImageProcessor(BaseImageProcessor):
    model_input_names = ["flattened_patches"]
    def __init__(self, do_convert_rgb: bool = True, do_normalize: bool = True, patch_size: Dict[str, int] = None, max_patches: int = 2048, is_vqa: bool = False, **kwargs) -> None:
        super().__init__(**kwargs)
        self.patch_size = patch_size if patch_size is not None else {"height": 16, "width": 16}
        self.do_normalize = do_normalize
        self.do_convert_rgb = do_convert_rgb
        self.max_patches = max_patches
        self.is_vqa = is_vqa
    def extract_flattened_patches(self, image: np.ndarray, max_patches: int, patch_size: dict, input_data_format: Optional[Union[str, ChannelDimension]] = None, **kwargs) -> np.ndarray:
        requires_backends(self.extract_flattened_patches, "torch")
        image = to_channel_dimension_format(image, ChannelDimension.FIRST, input_data_format)
        image = torch.from_numpy(image)
        patch_height, patch_width = patch_size["height"], patch_size["width"]
        image_height, image_width = get_image_size(image, ChannelDimension.FIRST)
        scale = math.sqrt(max_patches * (patch_height / image_height) * (patch_width / image_width))
        num_feasible_rows = max(min(math.floor(scale * image_height / patch_height), max_patches), 1)
        num_feasible_cols = max(min(math.floor(scale * image_width / patch_width), max_patches), 1)
        resized_height = max(num_feasible_rows * patch_height, 1)
        resized_width = max(num_feasible_cols * patch_width, 1)
        image = torch.nn.functional.interpolate(image.unsqueeze(0), size=(resized_height, resized_width), mode="bilinear", align_corners=False, antialias=True).squeeze(0)
        patches = torch_extract_patches(image, patch_height, patch_width)
        patches_shape = patches.shape
        rows = patches_shape[1]
        columns = patches_shape[2]
        depth = patches_shape[3]
        patches = patches.reshape([rows * columns, depth])
        row_ids = torch.arange(rows).reshape([rows, 1]).repeat(1, columns).reshape([rows * columns, 1])
        col_ids = torch.arange(columns).reshape([1, columns]).repeat(rows, 1).reshape([rows * columns, 1])
        row_ids += 1
        col_ids += 1
        row_ids = row_ids.to(torch.float32)
        col_ids = col_ids.to(torch.float32)
        result = torch.cat([row_ids, col_ids, patches], -1)
        result = torch.nn.functional.pad(result, [0, 0, 0, max_patches - (rows * columns)]).float()
        result = to_numpy_array(result)
        return result
    def normalize(self, image: np.ndarray, data_format: Optional[Union[str, ChannelDimension]] = None, input_data_format: Optional[Union[str, ChannelDimension]] = None, **kwargs) -> np.ndarray:
        if image.dtype == np.uint8: image = image.astype(np.float32)
        mean = np.mean(image)
        std = np.std(image)
        adjusted_stddev = max(std, 1.0 / math.sqrt(np.prod(image.shape)))
        return normalize(image, mean=mean, std=adjusted_stddev, data_format=data_format, input_data_format=input_data_format, **kwargs)
    def preprocess(self, images: ImageInput, header_text: Optional[str] = None, do_convert_rgb: bool = None, do_normalize: Optional[bool] = None, max_patches: Optional[int] = None,
    patch_size: Optional[Dict[str, int]] = None, return_tensors: Optional[Union[str, TensorType]] = None, data_format: ChannelDimension = ChannelDimension.FIRST,
    input_data_format: Optional[Union[str, ChannelDimension]] = None, **kwargs) -> ImageInput:
        do_normalize = do_normalize if do_normalize is not None else self.do_normalize
        do_convert_rgb = do_convert_rgb if do_convert_rgb is not None else self.do_convert_rgb
        patch_size = patch_size if patch_size is not None else self.patch_size
        max_patches = max_patches if max_patches is not None else self.max_patches
        is_vqa = self.is_vqa
        if kwargs.get("data_format", None) is not None: raise ValueError("data_format is not an accepted input as the outputs are ")
        images = make_list_of_images(images)
        if not valid_images(images): raise ValueError("Invalid image type. Must be of type PIL.Image.Image, numpy.ndarray, torch.Tensor, tf.Tensor or jax.ndarray.")
        if do_convert_rgb: images = [convert_to_rgb(image) for image in images]
        images = [to_numpy_array(image) for image in images]
        if input_data_format is None: input_data_format = infer_channel_dimension_format(images[0])
        if is_vqa:
            if header_text is None: raise ValueError("A header text must be provided for VQA models.")
            font_bytes = kwargs.pop("font_bytes", None)
            font_path = kwargs.pop("font_path", None)
            if isinstance(header_text, str): header_text = [header_text] * len(images)
            images = [render_header(image, header_text[i], font_bytes=font_bytes, font_path=font_path) for i, image in enumerate(images)]
        if do_normalize: images = [self.normalize(image=image, input_data_format=input_data_format) for image in images]
        images = [self.extract_flattened_patches(image=image, max_patches=max_patches, patch_size=patch_size, input_data_format=input_data_format) for image in images]
        attention_masks = [(image.sum(axis=-1) != 0).astype(np.float32) for image in images]
        encoded_outputs = BatchFeature(data={"flattened_patches": images, "attention_mask": attention_masks}, tensor_type=return_tensors)
        return encoded_outputs
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
