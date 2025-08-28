'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from .configuration_utils import ConfigMixin, register_to_config
from .utils import CONFIG_NAME, PIL_INTERPOLATION, deprecate
from typing import List, Optional, Tuple, Union
from PIL import Image, ImageFilter, ImageOps
import torch.nn.functional as F
import numpy as np
import PIL.Image
import torch
import math
PipelineImageInput = Union[PIL.Image.Image, np.ndarray, torch.Tensor, List[PIL.Image.Image], List[np.ndarray], List[torch.Tensor]]
PipelineDepthInput = PipelineImageInput
def is_valid_image(image) -> bool:
    """Returns:"""
    return isinstance(image, PIL.Image.Image) or (isinstance(image, (np.ndarray, torch.Tensor)) and image.ndim in (2, 3))
def is_valid_image_imagelist(images):
    """Returns:"""
    if isinstance(images, (np.ndarray, torch.Tensor)) and images.ndim == 4: return True
    elif is_valid_image(images): return True
    elif isinstance(images, list): return all((is_valid_image(image) for image in images))
    return False
class VaeImageProcessor(ConfigMixin):
    """Args:"""
    config_name = CONFIG_NAME
    @register_to_config
    def __init__(self, do_resize: bool=True, vae_scale_factor: int=8, vae_latent_channels: int=4, resample: str='lanczos', do_normalize: bool=True, do_binarize: bool=False, do_convert_rgb: bool=False, do_convert_grayscale: bool=False):
        super().__init__()
        if do_convert_rgb and do_convert_grayscale: raise ValueError('`do_convert_rgb` and `do_convert_grayscale` can not both be set to `True`, if you intended to convert the image into RGB format, please set `do_convert_grayscale = False`.', ' if you intended to convert the image into grayscale format, please set `do_convert_rgb = False`')
    @staticmethod
    def numpy_to_pil(images: np.ndarray) -> List[PIL.Image.Image]:
        """Returns:"""
        if images.ndim == 3: images = images[None, ...]
        images = (images * 255).round().astype('uint8')
        if images.shape[-1] == 1: pil_images = [Image.fromarray(image.squeeze(), mode='L') for image in images]
        else: pil_images = [Image.fromarray(image) for image in images]
        return pil_images
    @staticmethod
    def pil_to_numpy(images: Union[List[PIL.Image.Image], PIL.Image.Image]) -> np.ndarray:
        """Returns:"""
        if not isinstance(images, list): images = [images]
        images = [np.array(image).astype(np.float32) / 255.0 for image in images]
        images = np.stack(images, axis=0)
        return images
    @staticmethod
    def numpy_to_pt(images: np.ndarray) -> torch.Tensor:
        """Returns:"""
        if images.ndim == 3: images = images[..., None]
        images = torch.from_numpy(images.transpose(0, 3, 1, 2))
        return images
    @staticmethod
    def pt_to_numpy(images: torch.Tensor) -> np.ndarray:
        """Returns:"""
        images = images.cpu().permute(0, 2, 3, 1).float().numpy()
        return images
    @staticmethod
    def normalize(images: Union[np.ndarray, torch.Tensor]) -> Union[np.ndarray, torch.Tensor]:
        """Returns:"""
        return 2.0 * images - 1.0
    @staticmethod
    def denormalize(images: Union[np.ndarray, torch.Tensor]) -> Union[np.ndarray, torch.Tensor]:
        """Returns:"""
        return (images * 0.5 + 0.5).clamp(0, 1)
    @staticmethod
    def convert_to_rgb(image: PIL.Image.Image) -> PIL.Image.Image:
        """Returns:"""
        image = image.convert('RGB')
        return image
    @staticmethod
    def convert_to_grayscale(image: PIL.Image.Image) -> PIL.Image.Image:
        """Returns:"""
        image = image.convert('L')
        return image
    @staticmethod
    def blur(image: PIL.Image.Image, blur_factor: int=4) -> PIL.Image.Image:
        """Returns:"""
        image = image.filter(ImageFilter.GaussianBlur(blur_factor))
        return image
    @staticmethod
    def get_crop_region(mask_image: PIL.Image.Image, width: int, height: int, pad=0):
        """Returns:"""
        mask_image = mask_image.convert('L')
        mask = np.array(mask_image)
        h, w = mask.shape
        crop_left = 0
        for i in range(w):
            if not (mask[:, i] == 0).all(): break
            crop_left += 1
        crop_right = 0
        for i in reversed(range(w)):
            if not (mask[:, i] == 0).all(): break
            crop_right += 1
        crop_top = 0
        for i in range(h):
            if not (mask[i] == 0).all(): break
            crop_top += 1
        crop_bottom = 0
        for i in reversed(range(h)):
            if not (mask[i] == 0).all(): break
            crop_bottom += 1
        x1, y1, x2, y2 = (int(max(crop_left - pad, 0)), int(max(crop_top - pad, 0)), int(min(w - crop_right + pad, w)), int(min(h - crop_bottom + pad, h)))
        ratio_crop_region = (x2 - x1) / (y2 - y1)
        ratio_processing = width / height
        if ratio_crop_region > ratio_processing:
            desired_height = (x2 - x1) / ratio_processing
            desired_height_diff = int(desired_height - (y2 - y1))
            y1 -= desired_height_diff // 2
            y2 += desired_height_diff - desired_height_diff // 2
            if y2 >= mask_image.height:
                diff = y2 - mask_image.height
                y2 -= diff
                y1 -= diff
            if y1 < 0:
                y2 -= y1
                y1 -= y1
            if y2 >= mask_image.height:
                y2 = mask_image.height
        else:
            desired_width = (y2 - y1) * ratio_processing
            desired_width_diff = int(desired_width - (x2 - x1))
            x1 -= desired_width_diff // 2
            x2 += desired_width_diff - desired_width_diff // 2
            if x2 >= mask_image.width:
                diff = x2 - mask_image.width
                x2 -= diff
                x1 -= diff
            if x1 < 0:
                x2 -= x1
                x1 -= x1
            if x2 >= mask_image.width:
                x2 = mask_image.width
        return (x1, y1, x2, y2)
    def _resize_and_fill(self, image: PIL.Image.Image, width: int, height: int) -> PIL.Image.Image:
        """Returns:"""
        ratio = width / height
        src_ratio = image.width / image.height
        src_w = width if ratio < src_ratio else image.width * height // image.height
        src_h = height if ratio >= src_ratio else image.height * width // image.width
        resized = image.resize((src_w, src_h), resample=PIL_INTERPOLATION['lanczos'])
        res = Image.new('RGB', (width, height))
        res.paste(resized, box=(width // 2 - src_w // 2, height // 2 - src_h // 2))
        if ratio < src_ratio:
            fill_height = height // 2 - src_h // 2
            if fill_height > 0:
                res.paste(resized.resize((width, fill_height), box=(0, 0, width, 0)), box=(0, 0))
                res.paste(resized.resize((width, fill_height), box=(0, resized.height, width, resized.height)), box=(0, fill_height + src_h))
        elif ratio > src_ratio:
            fill_width = width // 2 - src_w // 2
            if fill_width > 0:
                res.paste(resized.resize((fill_width, height), box=(0, 0, 0, height)), box=(0, 0))
                res.paste(resized.resize((fill_width, height), box=(resized.width, 0, resized.width, height)), box=(fill_width + src_w, 0))
        return res
    def _resize_and_crop(self, image: PIL.Image.Image, width: int, height: int) -> PIL.Image.Image:
        """Returns:"""
        ratio = width / height
        src_ratio = image.width / image.height
        src_w = width if ratio > src_ratio else image.width * height // image.height
        src_h = height if ratio <= src_ratio else image.height * width // image.width
        resized = image.resize((src_w, src_h), resample=PIL_INTERPOLATION['lanczos'])
        res = Image.new('RGB', (width, height))
        res.paste(resized, box=(width // 2 - src_w // 2, height // 2 - src_h // 2))
        return res
    def resize(self, image: Union[PIL.Image.Image, np.ndarray, torch.Tensor], height: int, width: int, resize_mode: str='default') -> Union[PIL.Image.Image, np.ndarray, torch.Tensor]:
        """Returns:"""
        if resize_mode != 'default' and (not isinstance(image, PIL.Image.Image)): raise ValueError(f'Only PIL image input is supported for resize_mode {resize_mode}')
        if isinstance(image, PIL.Image.Image):
            if resize_mode == 'default': image = image.resize((width, height), resample=PIL_INTERPOLATION[self.config.resample])
            elif resize_mode == 'fill': image = self._resize_and_fill(image, width, height)
            elif resize_mode == 'crop': image = self._resize_and_crop(image, width, height)
            else: raise ValueError(f'resize_mode {resize_mode} is not supported')
        elif isinstance(image, torch.Tensor): image = torch.nn.functional.interpolate(image, size=(height, width))
        elif isinstance(image, np.ndarray):
            image = self.numpy_to_pt(image)
            image = torch.nn.functional.interpolate(image, size=(height, width))
            image = self.pt_to_numpy(image)
        return image
    def binarize(self, image: PIL.Image.Image) -> PIL.Image.Image:
        """Returns:"""
        image[image < 0.5] = 0
        image[image >= 0.5] = 1
        return image
    def _denormalize_conditionally(self, images: torch.Tensor, do_denormalize: Optional[List[bool]]=None) -> torch.Tensor:
        """Args:"""
        if do_denormalize is None: return self.denormalize(images) if self.config.do_normalize else images
        return torch.stack([self.denormalize(images[i]) if do_denormalize[i] else images[i] for i in range(images.shape[0])])
    def get_default_height_width(self, image: Union[PIL.Image.Image, np.ndarray, torch.Tensor], height: Optional[int]=None, width: Optional[int]=None) -> Tuple[int, int]:
        """Returns:"""
        if height is None:
            if isinstance(image, PIL.Image.Image): height = image.height
            elif isinstance(image, torch.Tensor): height = image.shape[2]
            else: height = image.shape[1]
        if width is None:
            if isinstance(image, PIL.Image.Image): width = image.width
            elif isinstance(image, torch.Tensor): width = image.shape[3]
            else: width = image.shape[2]
        width, height = (x - x % self.config.vae_scale_factor for x in (width, height))
        return (height, width)
    def preprocess(self, image: PipelineImageInput, height: Optional[int]=None, width: Optional[int]=None, resize_mode: str='default', crops_coords: Optional[Tuple[int, int, int, int]]=None) -> torch.Tensor:
        """Returns:"""
        supported_formats = (PIL.Image.Image, np.ndarray, torch.Tensor)
        if self.config.do_convert_grayscale and isinstance(image, (torch.Tensor, np.ndarray)) and (image.ndim == 3):
            if isinstance(image, torch.Tensor): image = image.unsqueeze(1)
            elif image.shape[-1] == 1: image = np.expand_dims(image, axis=0)
            else: image = np.expand_dims(image, axis=-1)
        if isinstance(image, list) and isinstance(image[0], np.ndarray) and (image[0].ndim == 4): image = np.concatenate(image, axis=0)
        if isinstance(image, list) and isinstance(image[0], torch.Tensor) and (image[0].ndim == 4): image = torch.cat(image, axis=0)
        if not is_valid_image_imagelist(image): raise ValueError(f"Input is in incorrect format. Currently, we only support {', '.join((str(x) for x in supported_formats))}")
        if not isinstance(image, list): image = [image]
        if isinstance(image[0], PIL.Image.Image):
            if crops_coords is not None: image = [i.crop(crops_coords) for i in image]
            if self.config.do_resize:
                height, width = self.get_default_height_width(image[0], height, width)
                image = [self.resize(i, height, width, resize_mode=resize_mode) for i in image]
            if self.config.do_convert_rgb: image = [self.convert_to_rgb(i) for i in image]
            elif self.config.do_convert_grayscale: image = [self.convert_to_grayscale(i) for i in image]
            image = self.pil_to_numpy(image)
            image = self.numpy_to_pt(image)
        elif isinstance(image[0], np.ndarray):
            image = np.concatenate(image, axis=0) if image[0].ndim == 4 else np.stack(image, axis=0)
            image = self.numpy_to_pt(image)
            height, width = self.get_default_height_width(image, height, width)
            if self.config.do_resize: image = self.resize(image, height, width)
        elif isinstance(image[0], torch.Tensor):
            image = torch.cat(image, axis=0) if image[0].ndim == 4 else torch.stack(image, axis=0)
            if self.config.do_convert_grayscale and image.ndim == 3: image = image.unsqueeze(1)
            channel = image.shape[1]
            if channel == self.config.vae_latent_channels: return image
            height, width = self.get_default_height_width(image, height, width)
            if self.config.do_resize: image = self.resize(image, height, width)
        do_normalize = self.config.do_normalize
        if do_normalize and image.min() < 0: do_normalize = False
        if do_normalize: image = self.normalize(image)
        if self.config.do_binarize: image = self.binarize(image)
        return image
    def postprocess(self, image: torch.Tensor, output_type: str='pil', do_denormalize: Optional[List[bool]]=None) -> Union[PIL.Image.Image, np.ndarray, torch.Tensor]:
        """Returns:"""
        if not isinstance(image, torch.Tensor): raise ValueError(f'Input for postprocessing is in incorrect format: {type(image)}. We only support pytorch tensor')
        if output_type not in ['latent', 'pt', 'np', 'pil']:
            deprecation_message = f'the output_type {output_type} is outdated and has been set to `np`. Please make sure to set it to one of these instead: `pil`, `np`, `pt`, `latent`'
            deprecate('Unsupported output_type', '1.0.0', deprecation_message, standard_warn=False)
            output_type = 'np'
        if output_type == 'latent': return image
        image = self._denormalize_conditionally(image, do_denormalize)
        if output_type == 'pt': return image
        image = self.pt_to_numpy(image)
        if output_type == 'np': return image
        if output_type == 'pil': return self.numpy_to_pil(image)
    def apply_overlay(self, mask: PIL.Image.Image, init_image: PIL.Image.Image, image: PIL.Image.Image, crop_coords: Optional[Tuple[int, int, int, int]]=None) -> PIL.Image.Image:
        """Returns:"""
        width, height = (init_image.width, init_image.height)
        init_image_masked = PIL.Image.new('RGBa', (width, height))
        init_image_masked.paste(init_image.convert('RGBA').convert('RGBa'), mask=ImageOps.invert(mask.convert('L')))
        init_image_masked = init_image_masked.convert('RGBA')
        if crop_coords is not None:
            x, y, x2, y2 = crop_coords
            w = x2 - x
            h = y2 - y
            base_image = PIL.Image.new('RGBA', (width, height))
            image = self.resize(image, height=h, width=w, resize_mode='crop')
            base_image.paste(image, (x, y))
            image = base_image.convert('RGB')
        image = image.convert('RGBA')
        image.alpha_composite(init_image_masked)
        image = image.convert('RGB')
        return image
class VaeImageProcessorLDM3D(VaeImageProcessor):
    """Args:"""
    config_name = CONFIG_NAME
    @register_to_config
    def __init__(self, do_resize: bool=True, vae_scale_factor: int=8, resample: str='lanczos', do_normalize: bool=True): super().__init__()
    @staticmethod
    def numpy_to_pil(images: np.ndarray) -> List[PIL.Image.Image]:
        """Returns:"""
        if images.ndim == 3: images = images[None, ...]
        images = (images * 255).round().astype('uint8')
        if images.shape[-1] == 1: pil_images = [Image.fromarray(image.squeeze(), mode='L') for image in images]
        else: pil_images = [Image.fromarray(image[:, :, :3]) for image in images]
        return pil_images
    @staticmethod
    def depth_pil_to_numpy(images: Union[List[PIL.Image.Image], PIL.Image.Image]) -> np.ndarray:
        """Returns:"""
        if not isinstance(images, list): images = [images]
        images = [np.array(image).astype(np.float32) / (2 ** 16 - 1) for image in images]
        images = np.stack(images, axis=0)
        return images
    @staticmethod
    def rgblike_to_depthmap(image: Union[np.ndarray, torch.Tensor]) -> Union[np.ndarray, torch.Tensor]:
        """Returns:"""
        return image[:, :, 1] * 2 ** 8 + image[:, :, 2]
    def numpy_to_depth(self, images: np.ndarray) -> List[PIL.Image.Image]:
        """Returns:"""
        if images.ndim == 3: images = images[None, ...]
        images_depth = images[:, :, :, 3:]
        if images.shape[-1] == 6:
            images_depth = (images_depth * 255).round().astype('uint8')
            pil_images = [Image.fromarray(self.rgblike_to_depthmap(image_depth), mode='I;16') for image_depth in images_depth]
        elif images.shape[-1] == 4:
            images_depth = (images_depth * 65535.0).astype(np.uint16)
            pil_images = [Image.fromarray(image_depth, mode='I;16') for image_depth in images_depth]
        else: raise Exception('Not supported')
        return pil_images
    def postprocess(self, image: torch.Tensor, output_type: str='pil', do_denormalize: Optional[List[bool]]=None) -> Union[PIL.Image.Image, np.ndarray, torch.Tensor]:
        """Returns:"""
        if not isinstance(image, torch.Tensor): raise ValueError(f'Input for postprocessing is in incorrect format: {type(image)}. We only support pytorch tensor')
        if output_type not in ['latent', 'pt', 'np', 'pil']:
            deprecation_message = f'the output_type {output_type} is outdated and has been set to `np`. Please make sure to set it to one of these instead: `pil`, `np`, `pt`, `latent`'
            deprecate('Unsupported output_type', '1.0.0', deprecation_message, standard_warn=False)
            output_type = 'np'
        image = self._denormalize_conditionally(image, do_denormalize)
        image = self.pt_to_numpy(image)
        if output_type == 'np':
            if image.shape[-1] == 6: image_depth = np.stack([self.rgblike_to_depthmap(im[:, :, 3:]) for im in image], axis=0)
            else: image_depth = image[:, :, :, 3:]
            return (image[:, :, :, :3], image_depth)
        if output_type == 'pil': return (self.numpy_to_pil(image), self.numpy_to_depth(image))
        else: raise Exception(f'This type {output_type} is not supported')
    def preprocess(self, rgb: Union[torch.Tensor, PIL.Image.Image, np.ndarray], depth: Union[torch.Tensor, PIL.Image.Image, np.ndarray], height: Optional[int]=None, width: Optional[int]=None, target_res: Optional[int]=None) -> torch.Tensor:
        """Returns:"""
        supported_formats = (PIL.Image.Image, np.ndarray, torch.Tensor)
        if self.config.do_convert_grayscale and isinstance(rgb, (torch.Tensor, np.ndarray)) and (rgb.ndim == 3): raise Exception('This is not yet supported')
        if isinstance(rgb, supported_formats):
            rgb = [rgb]
            depth = [depth]
        elif not (isinstance(rgb, list) and all((isinstance(i, supported_formats) for i in rgb))): raise ValueError(f"Input is in incorrect format: {[type(i) for i in rgb]}. Currently, we only support {', '.join(supported_formats)}")
        if isinstance(rgb[0], PIL.Image.Image):
            if self.config.do_convert_rgb: raise Exception('This is not yet supported')
            if self.config.do_resize or target_res:
                height, width = self.get_default_height_width(rgb[0], height, width) if not target_res else target_res
                rgb = [self.resize(i, height, width) for i in rgb]
                depth = [self.resize(i, height, width) for i in depth]
            rgb = self.pil_to_numpy(rgb)
            rgb = self.numpy_to_pt(rgb)
            depth = self.depth_pil_to_numpy(depth)
            depth = self.numpy_to_pt(depth)
        elif isinstance(rgb[0], np.ndarray):
            rgb = np.concatenate(rgb, axis=0) if rgb[0].ndim == 4 else np.stack(rgb, axis=0)
            rgb = self.numpy_to_pt(rgb)
            height, width = self.get_default_height_width(rgb, height, width)
            if self.config.do_resize: rgb = self.resize(rgb, height, width)
            depth = np.concatenate(depth, axis=0) if rgb[0].ndim == 4 else np.stack(depth, axis=0)
            depth = self.numpy_to_pt(depth)
            height, width = self.get_default_height_width(depth, height, width)
            if self.config.do_resize: depth = self.resize(depth, height, width)
        elif isinstance(rgb[0], torch.Tensor): raise Exception('This is not yet supported')
        do_normalize = self.config.do_normalize
        if rgb.min() < 0 and do_normalize: do_normalize = False
        if do_normalize:
            rgb = self.normalize(rgb)
            depth = self.normalize(depth)
        if self.config.do_binarize:
            rgb = self.binarize(rgb)
            depth = self.binarize(depth)
        return (rgb, depth)
class IPAdapterMaskProcessor(VaeImageProcessor):
    """Args:"""
    config_name = CONFIG_NAME
    @register_to_config
    def __init__(self, do_resize: bool=True, vae_scale_factor: int=8, resample: str='lanczos', do_normalize: bool=False, do_binarize: bool=True, do_convert_grayscale: bool=True): super().__init__(do_resize=do_resize, vae_scale_factor=vae_scale_factor, resample=resample, do_normalize=do_normalize, do_binarize=do_binarize, do_convert_grayscale=do_convert_grayscale)
    @staticmethod
    def downsample(mask: torch.Tensor, batch_size: int, num_queries: int, value_embed_dim: int):
        """Returns:"""
        o_h = mask.shape[1]
        o_w = mask.shape[2]
        ratio = o_w / o_h
        mask_h = int(math.sqrt(num_queries / ratio))
        mask_h = int(mask_h) + int(num_queries % int(mask_h) != 0)
        mask_w = num_queries // mask_h
        mask_downsample = F.interpolate(mask.unsqueeze(0), size=(mask_h, mask_w), mode='bicubic').squeeze(0)
        if mask_downsample.shape[0] < batch_size: mask_downsample = mask_downsample.repeat(batch_size, 1, 1)
        mask_downsample = mask_downsample.view(mask_downsample.shape[0], -1)
        downsampled_area = mask_h * mask_w
        if downsampled_area < num_queries: mask_downsample = F.pad(mask_downsample, (0, num_queries - mask_downsample.shape[1]), value=0.0)
        if downsampled_area > num_queries: mask_downsample = mask_downsample[:, :num_queries]
        mask_downsample = mask_downsample.view(mask_downsample.shape[0], mask_downsample.shape[1], 1).repeat(1, 1, value_embed_dim)
        return mask_downsample
class PixArtImageProcessor(VaeImageProcessor):
    """Args:"""
    @register_to_config
    def __init__(self, do_resize: bool=True, vae_scale_factor: int=8, resample: str='lanczos', do_normalize: bool=True, do_binarize: bool=False, do_convert_grayscale: bool=False): super().__init__(do_resize=do_resize, vae_scale_factor=vae_scale_factor, resample=resample, do_normalize=do_normalize, do_binarize=do_binarize, do_convert_grayscale=do_convert_grayscale)
    @staticmethod
    def classify_height_width_bin(height: int, width: int, ratios: dict) -> Tuple[int, int]:
        """Returns:"""
        ar = float(height / width)
        closest_ratio = min(ratios.keys(), key=lambda ratio: abs(float(ratio) - ar))
        default_hw = ratios[closest_ratio]
        return (int(default_hw[0]), int(default_hw[1]))
    @staticmethod
    def resize_and_crop_tensor(samples: torch.Tensor, new_width: int, new_height: int) -> torch.Tensor:
        """Returns:"""
        orig_height, orig_width = (samples.shape[2], samples.shape[3])
        if orig_height != new_height or orig_width != new_width:
            ratio = max(new_height / orig_height, new_width / orig_width)
            resized_width = int(orig_width * ratio)
            resized_height = int(orig_height * ratio)
            samples = F.interpolate(samples, size=(resized_height, resized_width), mode='bilinear', align_corners=False)
            start_x = (resized_width - new_width) // 2
            end_x = start_x + new_width
            start_y = (resized_height - new_height) // 2
            end_y = start_y + new_height
            samples = samples[:, :, start_y:end_y, start_x:end_x]
        return samples
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
