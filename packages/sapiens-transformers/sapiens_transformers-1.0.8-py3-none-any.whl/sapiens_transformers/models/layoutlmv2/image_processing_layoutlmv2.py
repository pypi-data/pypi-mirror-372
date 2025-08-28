"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import Dict, Optional, Union
import numpy as np
from ...image_processing_utils import BaseImageProcessor, BatchFeature, get_size_dict
from ...image_transforms import flip_channel_order, resize, to_channel_dimension_format, to_pil_image
from ...image_utils import (ChannelDimension, ImageInput, PILImageResampling, infer_channel_dimension_format, make_list_of_images, to_numpy_array, valid_images, validate_preprocess_arguments)
from ...utils import (TensorType, filter_out_non_signature_kwargs, is_pytesseract_available, is_vision_available, logging, requires_backends)
if is_vision_available(): import PIL
if is_pytesseract_available(): import pytesseract
logger = logging.get_logger(__name__)
def normalize_box(box, width, height): return [int(1000 * (box[0] / width)), int(1000 * (box[1] / height)), int(1000 * (box[2] / width)), int(1000 * (box[3] / height))]
def apply_tesseract(image: np.ndarray, lang: Optional[str], tesseract_config: Optional[str] = None, input_data_format: Optional[Union[str, ChannelDimension]] = None):
    tesseract_config = tesseract_config if tesseract_config is not None else ""
    pil_image = to_pil_image(image, input_data_format=input_data_format)
    image_width, image_height = pil_image.size
    data = pytesseract.image_to_data(pil_image, lang=lang, output_type="dict", config=tesseract_config)
    words, left, top, width, height = data["text"], data["left"], data["top"], data["width"], data["height"]
    irrelevant_indices = [idx for idx, word in enumerate(words) if not word.strip()]
    words = [word for idx, word in enumerate(words) if idx not in irrelevant_indices]
    left = [coord for idx, coord in enumerate(left) if idx not in irrelevant_indices]
    top = [coord for idx, coord in enumerate(top) if idx not in irrelevant_indices]
    width = [coord for idx, coord in enumerate(width) if idx not in irrelevant_indices]
    height = [coord for idx, coord in enumerate(height) if idx not in irrelevant_indices]
    actual_boxes = []
    for x, y, w, h in zip(left, top, width, height):
        actual_box = [x, y, x + w, y + h]
        actual_boxes.append(actual_box)
    normalized_boxes = []
    for box in actual_boxes: normalized_boxes.append(normalize_box(box, image_width, image_height))
    assert len(words) == len(normalized_boxes), "Not as many words as there are bounding boxes"
    return words, normalized_boxes
class LayoutLMv2ImageProcessor(BaseImageProcessor):
    model_input_names = ["pixel_values"]
    def __init__(self, do_resize: bool = True, size: Dict[str, int] = None, resample: PILImageResampling = PILImageResampling.BILINEAR, apply_ocr: bool = True,
    ocr_lang: Optional[str] = None, tesseract_config: Optional[str] = "", **kwargs) -> None:
        super().__init__(**kwargs)
        size = size if size is not None else {"height": 224, "width": 224}
        size = get_size_dict(size)
        self.do_resize = do_resize
        self.size = size
        self.resample = resample
        self.apply_ocr = apply_ocr
        self.ocr_lang = ocr_lang
        self.tesseract_config = tesseract_config
    def resize(self, image: np.ndarray, size: Dict[str, int], resample: PILImageResampling = PILImageResampling.BILINEAR, data_format: Optional[Union[str, ChannelDimension]] = None,
    input_data_format: Optional[Union[str, ChannelDimension]] = None, **kwargs) -> np.ndarray:
        size = get_size_dict(size)
        if "height" not in size or "width" not in size: raise ValueError(f"The `size` dictionary must contain the keys `height` and `width`. Got {size.keys()}")
        output_size = (size["height"], size["width"])
        return resize(image, size=output_size, resample=resample, data_format=data_format, input_data_format=input_data_format, **kwargs)
    @filter_out_non_signature_kwargs()
    def preprocess(self, images: ImageInput, do_resize: bool = None, size: Dict[str, int] = None, resample: PILImageResampling = None, apply_ocr: bool = None, ocr_lang: Optional[str] = None,
    tesseract_config: Optional[str] = None, return_tensors: Optional[Union[str, TensorType]] = None, data_format: ChannelDimension = ChannelDimension.FIRST,
    input_data_format: Optional[Union[str, ChannelDimension]] = None) -> PIL.Image.Image:
        do_resize = do_resize if do_resize is not None else self.do_resize
        size = size if size is not None else self.size
        size = get_size_dict(size)
        resample = resample if resample is not None else self.resample
        apply_ocr = apply_ocr if apply_ocr is not None else self.apply_ocr
        ocr_lang = ocr_lang if ocr_lang is not None else self.ocr_lang
        tesseract_config = tesseract_config if tesseract_config is not None else self.tesseract_config
        images = make_list_of_images(images)
        if not valid_images(images): raise ValueError("Invalid image type. Must be of type PIL.Image.Image, numpy.ndarray, torch.Tensor, tf.Tensor or jax.ndarray.")
        validate_preprocess_arguments(do_resize=do_resize, size=size, resample=resample)
        images = [to_numpy_array(image) for image in images]
        if input_data_format is None: input_data_format = infer_channel_dimension_format(images[0])
        if apply_ocr:
            requires_backends(self, "pytesseract")
            words_batch = []
            boxes_batch = []
            for image in images:
                words, boxes = apply_tesseract(image, ocr_lang, tesseract_config, input_data_format=input_data_format)
                words_batch.append(words)
                boxes_batch.append(boxes)
        if do_resize: images = [self.resize(image=image, size=size, resample=resample, input_data_format=input_data_format) for image in images]
        images = [flip_channel_order(image, input_data_format=input_data_format) for image in images]
        images = [to_channel_dimension_format(image, data_format, input_channel_dim=input_data_format) for image in images]
        data = BatchFeature(data={"pixel_values": images}, tensor_type=return_tensors)
        if apply_ocr:
            data["words"] = words_batch
            data["boxes"] = boxes_batch
        return data
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
