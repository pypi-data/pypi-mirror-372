"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from collections import defaultdict
from typing import Optional
from ..image_utils import load_image
from ..utils import (add_end_docstrings, is_torch_available, logging, requires_backends)
from .base import ChunkPipeline, build_pipeline_init_args
if is_torch_available():
    import torch
    from ..models.auto.modeling_auto import MODEL_FOR_MASK_GENERATION_MAPPING_NAMES
logger = logging.get_logger(__name__)
@add_end_docstrings(build_pipeline_init_args(has_image_processor=True),
    r"""
        points_per_batch (optional, int, default to 64):
            Sets the number of points run simultaneously by the model. Higher numbers may be faster but use more GPU
            memory.
        output_bboxes_mask (`bool`, optional, default to `False`):
            Whether or not to output the bounding box predictions.
        output_rle_masks (`bool`, optional, default to `False`):
            Whether or not to output the masks in `RLE` format""")
class MaskGenerationPipeline(ChunkPipeline):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        requires_backends(self, "vision")
        requires_backends(self, "torch")
        if self.framework != "pt": raise ValueError(f"The {self.__class__} is only available in PyTorch.")
        self.check_model_type(MODEL_FOR_MASK_GENERATION_MAPPING_NAMES)
    def _sanitize_parameters(self, **kwargs):
        preprocess_kwargs = {}
        postprocess_kwargs = {}
        forward_params = {}
        if "points_per_batch" in kwargs: preprocess_kwargs["points_per_batch"] = kwargs["points_per_batch"]
        if "points_per_crop" in kwargs: preprocess_kwargs["points_per_crop"] = kwargs["points_per_crop"]
        if "crops_n_layers" in kwargs: preprocess_kwargs["crops_n_layers"] = kwargs["crops_n_layers"]
        if "crop_overlap_ratio" in kwargs: preprocess_kwargs["crop_overlap_ratio"] = kwargs["crop_overlap_ratio"]
        if "crop_n_points_downscale_factor" in kwargs: preprocess_kwargs["crop_n_points_downscale_factor"] = kwargs["crop_n_points_downscale_factor"]
        if "timeout" in kwargs: preprocess_kwargs["timeout"] = kwargs["timeout"]
        if "pred_iou_thresh" in kwargs: forward_params["pred_iou_thresh"] = kwargs["pred_iou_thresh"]
        if "stability_score_offset" in kwargs: forward_params["stability_score_offset"] = kwargs["stability_score_offset"]
        if "mask_threshold" in kwargs: forward_params["mask_threshold"] = kwargs["mask_threshold"]
        if "stability_score_thresh" in kwargs: forward_params["stability_score_thresh"] = kwargs["stability_score_thresh"]
        if "crops_nms_thresh" in kwargs: postprocess_kwargs["crops_nms_thresh"] = kwargs["crops_nms_thresh"]
        if "output_rle_mask" in kwargs: postprocess_kwargs["output_rle_mask"] = kwargs["output_rle_mask"]
        if "output_bboxes_mask" in kwargs: postprocess_kwargs["output_bboxes_mask"] = kwargs["output_bboxes_mask"]
        return preprocess_kwargs, forward_params, postprocess_kwargs
    def __call__(self, image, *args, num_workers=None, batch_size=None, **kwargs): return super().__call__(image, *args, num_workers=num_workers, batch_size=batch_size, **kwargs)
    def preprocess(self, image, points_per_batch=64, crops_n_layers: int = 0, crop_overlap_ratio: float = 512 / 1500, points_per_crop: Optional[int] = 32, crop_n_points_downscale_factor: Optional[int] = 1, timeout: Optional[float] = None):
        image = load_image(image, timeout=timeout)
        target_size = self.image_processor.size["longest_edge"]
        crop_boxes, grid_points, cropped_images, input_labels = self.image_processor.generate_crop_boxes(image, target_size, crops_n_layers, crop_overlap_ratio, points_per_crop, crop_n_points_downscale_factor)
        model_inputs = self.image_processor(images=cropped_images, return_tensors="pt")
        if self.framework == "pt": model_inputs = model_inputs.to(self.torch_dtype)
        with self.device_placement():
            if self.framework == "pt":
                inference_context = self.get_inference_context()
                with inference_context():
                    model_inputs = self._ensure_tensor_on_device(model_inputs, device=self.device)
                    image_embeddings = self.model.get_image_embeddings(model_inputs.pop("pixel_values"))
                    model_inputs["image_embeddings"] = image_embeddings
        n_points = grid_points.shape[1]
        points_per_batch = points_per_batch if points_per_batch is not None else n_points
        if points_per_batch <= 0: raise ValueError("Cannot have points_per_batch<=0. Must be >=1 to returned batched outputs. To return all points at once, set points_per_batch to None")
        for i in range(0, n_points, points_per_batch):
            batched_points = grid_points[:, i : i + points_per_batch, :, :]
            labels = input_labels[:, i : i + points_per_batch]
            is_last = i == n_points - points_per_batch
            yield {"input_points": batched_points, "input_labels": labels, "input_boxes": crop_boxes, "is_last": is_last, **model_inputs}
    def _forward(self, model_inputs, pred_iou_thresh=0.88, stability_score_thresh=0.95, mask_threshold=0, stability_score_offset=1):
        input_boxes = model_inputs.pop("input_boxes")
        is_last = model_inputs.pop("is_last")
        original_sizes = model_inputs.pop("original_sizes").tolist()
        reshaped_input_sizes = model_inputs.pop("reshaped_input_sizes").tolist()
        model_outputs = self.model(**model_inputs)
        low_resolution_masks = model_outputs["pred_masks"]
        masks = self.image_processor.post_process_masks(low_resolution_masks, original_sizes, reshaped_input_sizes, mask_threshold, binarize=False)
        iou_scores = model_outputs["iou_scores"]
        masks, iou_scores, boxes = self.image_processor.filter_masks(masks[0], iou_scores[0], original_sizes[0], input_boxes[0], pred_iou_thresh, stability_score_thresh, mask_threshold, stability_score_offset)
        return {"masks": masks, "is_last": is_last, "boxes": boxes, "iou_scores": iou_scores}
    def postprocess(self, model_outputs, output_rle_mask=False, output_bboxes_mask=False, crops_nms_thresh=0.7):
        all_scores = []
        all_masks = []
        all_boxes = []
        for model_output in model_outputs:
            all_scores.append(model_output.pop("iou_scores"))
            all_masks.extend(model_output.pop("masks"))
            all_boxes.append(model_output.pop("boxes"))
        all_scores = torch.cat(all_scores)
        all_boxes = torch.cat(all_boxes)
        output_masks, iou_scores, rle_mask, bounding_boxes = self.image_processor.post_process_for_mask_generation(all_masks, all_scores, all_boxes, crops_nms_thresh)
        extra = defaultdict(list)
        for output in model_outputs:
            for k, v in output.items(): extra[k].append(v)
        optional = {}
        if output_rle_mask: optional["rle_mask"] = rle_mask
        if output_bboxes_mask: optional["bounding_boxes"] = bounding_boxes
        return {"masks": output_masks, "scores": iou_scores, **optional, **extra}
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
