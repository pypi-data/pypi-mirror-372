from __future__ import annotations
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from torchvision.transforms import InterpolationMode
from torchvision import io, transforms
from functools import lru_cache
from packaging import version
from io import BytesIO
from PIL import Image
import torchvision
import requests
import base64
import torch
import math
import time
import sys
import os
IMAGE_FACTOR, MIN_PIXELS, MAX_PIXELS, MAX_RATIO = 28, 4 * 28 * 28, 16384 * 28 * 28, 200
VIDEO_MIN_PIXELS, VIDEO_MAX_PIXELS, VIDEO_TOTAL_PIXELS = 128 * 28 * 28, 768 * 28 * 28, 24576 * 28 * 28
FRAME_FACTOR, FPS, FPS_MIN_FRAMES, FPS_MAX_FRAMES = 2, 2.0, 4, 768
def round_by_factor(number: int, factor: int) -> int: return round(number / factor) * factor
def ceil_by_factor(number: int, factor: int) -> int: return math.ceil(number / factor) * factor
def floor_by_factor(number: int, factor: int) -> int: return math.floor(number / factor) * factor
def smart_resize(height: int, width: int, factor: int = IMAGE_FACTOR, min_pixels: int = MIN_PIXELS, max_pixels: int = MAX_PIXELS) -> tuple[int, int]:
    if max(height, width) / min(height, width) > MAX_RATIO: raise ValueError(f"absolute aspect ratio must be smaller than {MAX_RATIO}, got {max(height, width) / min(height, width)}")
    h_bar = max(factor, round_by_factor(height, factor))
    w_bar = max(factor, round_by_factor(width, factor))
    if h_bar * w_bar > max_pixels:
        beta = math.sqrt((height * width) / max_pixels)
        h_bar, w_bar = floor_by_factor(height / beta, factor), floor_by_factor(width / beta, factor)
    elif h_bar * w_bar < min_pixels:
        beta = math.sqrt(min_pixels / (height * width))
        h_bar, w_bar = ceil_by_factor(height * beta, factor), ceil_by_factor(width * beta, factor)
    return h_bar, w_bar
def fetch_image(ele: dict[str, str | Image.Image], size_factor: int = IMAGE_FACTOR) -> Image.Image:
    if "image" in ele: image = ele["image"]
    else: image = ele["image_url"]
    image_obj = None
    if isinstance(image, Image.Image): image_obj = image
    elif image.startswith("http://") or image.startswith("https://"): image_obj = Image.open(requests.get(image, stream=True).raw)
    elif image.startswith("file://"): image_obj = Image.open(image[7:])
    elif image.startswith("data:image"):
        if "base64," in image:
            _, base64_data = image.split("base64,", 1)
            data = base64.b64decode(base64_data)
            image_obj = Image.open(BytesIO(data))
    else: image_obj = Image.open(image)
    if image_obj is None: raise ValueError(f"Unrecognized image input, support local path, http url, base64 and PIL.Image, got {image}")
    image = image_obj.convert("RGB")
    if "resized_height" in ele and "resized_width" in ele: resized_height, resized_width = smart_resize(ele["resized_height"], ele["resized_width"], factor=size_factor)
    else:
        width, height = image.size
        min_pixels = ele.get("min_pixels", MIN_PIXELS)
        max_pixels = ele.get("max_pixels", MAX_PIXELS)
        resized_height, resized_width = smart_resize(height, width, factor=size_factor, min_pixels=min_pixels, max_pixels=max_pixels)
    image = image.resize((resized_width, resized_height))
    return image
def smart_nframes(ele: dict, total_frames: int, video_fps: int | float) -> int:
    assert not ("fps" in ele and "nframes" in ele), "Only accept either `fps` or `nframes`"
    if "nframes" in ele: nframes = round_by_factor(ele["nframes"], FRAME_FACTOR)
    else:
        fps = ele.get("fps", FPS)
        min_frames = ceil_by_factor(ele.get("min_frames", FPS_MIN_FRAMES), FRAME_FACTOR)
        max_frames = floor_by_factor(ele.get("max_frames", min(FPS_MAX_FRAMES, total_frames)), FRAME_FACTOR)
        nframes = total_frames / video_fps * fps
        nframes = min(max(nframes, min_frames), max_frames)
        nframes = round_by_factor(nframes, FRAME_FACTOR)
    if not (FRAME_FACTOR <= nframes and nframes <= total_frames): raise ValueError(f"nframes should in interval [{FRAME_FACTOR}, {total_frames}], but got {nframes}.")
    return nframes
def _read_video_torchvision(ele: dict) -> torch.Tensor:
    video_path = ele["video"]
    if version.parse(torchvision.__version__) < version.parse("0.19.0"):
        if "file://" in video_path: video_path = video_path[7:]
    st = time.time()
    video, audio, info = io.read_video(video_path, start_pts=ele.get("video_start", 0.0), end_pts=ele.get("video_end", None), pts_unit="sec", output_format="TCHW")
    total_frames, video_fps = video.size(0), info["video_fps"]
    nframes = smart_nframes(ele, total_frames=total_frames, video_fps=video_fps)
    idx = torch.linspace(0, total_frames - 1, nframes).round().long()
    video = video[idx]
    return video
def is_decord_available() -> bool:
    import importlib.util
    return importlib.util.find_spec("decord") is not None
def _read_video_decord(ele: dict) -> torch.Tensor:
    import decord
    video_path = ele["video"]
    st = time.time()
    vr = decord.VideoReader(video_path)
    if 'video_start' in ele or 'video_end' in ele: raise NotImplementedError("not support start_pts and end_pts in decord for now.")
    total_frames, video_fps = len(vr), vr.get_avg_fps()
    nframes = smart_nframes(ele, total_frames=total_frames, video_fps=video_fps)
    idx = torch.linspace(0, total_frames - 1, nframes).round().long().tolist()
    video = vr.get_batch(idx).asnumpy()
    video = torch.tensor(video).permute(0, 3, 1, 2)
    return video
VIDEO_READER_BACKENDS = {"decord": _read_video_decord, "torchvision": _read_video_torchvision}
FORCE_QWENVL_VIDEO_READER = os.getenv("FORCE_QWENVL_VIDEO_READER", None)
@lru_cache(maxsize=1)
def get_video_reader_backend() -> str:
    if FORCE_QWENVL_VIDEO_READER is not None: video_reader_backend = FORCE_QWENVL_VIDEO_READER
    elif is_decord_available(): video_reader_backend = "decord"
    else: video_reader_backend = "torchvision"
    return video_reader_backend
def fetch_video(ele: dict, image_factor: int = IMAGE_FACTOR) -> torch.Tensor | list[Image.Image]:
    if isinstance(ele["video"], str):
        video_reader_backend = get_video_reader_backend()
        video = VIDEO_READER_BACKENDS[video_reader_backend](ele)
        nframes, _, height, width = video.shape
        min_pixels = ele.get("min_pixels", VIDEO_MIN_PIXELS)
        total_pixels = ele.get("total_pixels", VIDEO_TOTAL_PIXELS)
        max_pixels = max(min(VIDEO_MAX_PIXELS, total_pixels / nframes * FRAME_FACTOR), int(min_pixels * 1.05))
        max_pixels = ele.get("max_pixels", max_pixels)
        if "resized_height" in ele and "resized_width" in ele: resized_height, resized_width = smart_resize(ele["resized_height"], ele["resized_width"], factor=image_factor)
        else: resized_height, resized_width = smart_resize(height, width, factor=image_factor, min_pixels=min_pixels, max_pixels=max_pixels)
        video = transforms.functional.resize(video, [resized_height, resized_width], interpolation=InterpolationMode.BICUBIC, antialias=True).float()
        return video
    else:
        assert isinstance(ele["video"], (list, tuple))
        process_info = ele.copy()
        process_info.pop("type", None)
        process_info.pop("video", None)
        images = [fetch_image({"image": video_element, **process_info}, size_factor=image_factor) for video_element in ele["video"]]
        nframes = ceil_by_factor(len(images), FRAME_FACTOR)
        if len(images) < nframes: images.extend([images[-1]] * (nframes - len(images)))
        return images
def extract_vision_info(conversations: list[dict] | list[list[dict]]) -> list[dict]:
    vision_infos = []
    if isinstance(conversations[0], dict): conversations = [conversations]
    for conversation in conversations:
        for message in conversation:
            if isinstance(message["content"], list):
                for ele in message["content"]:
                    if ("image" in ele or "image_url" in ele or "video" in ele or ele["type"] in ("image", "image_url", "video")): vision_infos.append(ele)
    return vision_infos
def process_vision_info(conversations: list[dict] | list[list[dict]]) -> tuple[list[Image.Image] | None, list[torch.Tensor | list[Image.Image]] | None]:
    vision_infos = extract_vision_info(conversations)
    image_inputs = []
    video_inputs = []
    for vision_info in vision_infos:
        if "image" in vision_info or "image_url" in vision_info: image_inputs.append(fetch_image(vision_info))
        elif "video" in vision_info: video_inputs.append(fetch_video(vision_info))
        else: raise ValueError("image, image_url or video should in content.")
    if len(image_inputs) == 0: image_inputs = None
    if len(video_inputs) == 0: video_inputs = None
    return image_inputs, video_inputs
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
