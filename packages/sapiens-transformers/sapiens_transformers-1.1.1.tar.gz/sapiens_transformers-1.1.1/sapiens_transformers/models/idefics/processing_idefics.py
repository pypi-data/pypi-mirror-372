"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import Callable, List, Optional, Union
from urllib.parse import urlparse
from ...feature_extraction_utils import BatchFeature
from ...processing_utils import ProcessorMixin
from ...tokenization_utils_base import BatchEncoding, PaddingStrategy, TextInput, TruncationStrategy
from ...utils import is_tf_available, is_torch_available
if is_torch_available(): import torch
if is_tf_available(): import tensorflow as tf
IMAGE_TOKEN = "<image>"
def incremental_to_binary_attention_mask(incremental_mask, return_tensors, num_classes=-1):
    if num_classes != -1:
        if return_tensors == "pt": incremental_mask[incremental_mask >= num_classes] = -1
        elif return_tensors == "tf": incremental_mask = tf.where(incremental_mask >= num_classes, -1, incremental_mask)
    if return_tensors == "pt":
        negatives = incremental_mask == -1
        incremental_mask[negatives] = 0
        attn_mask = torch.nn.functional.one_hot(incremental_mask, num_classes=num_classes)
        attn_mask[negatives, :] = 0
    elif return_tensors == "tf":
        negatives = tf.equal(incremental_mask, -1)
        incremental_mask = tf.where(negatives, 0, incremental_mask)
        attn_mask = tf.one_hot(incremental_mask, depth=num_classes)
        negatives_expanded = tf.expand_dims(negatives, -1)
        attn_mask = tf.where(negatives_expanded, tf.zeros_like(attn_mask), attn_mask)
    return attn_mask
def image_attention_mask_for_packed_input_ids(input_ids, tokenizer, return_tensors):
    if return_tensors == "pt": return image_attention_mask_for_packed_input_ids_pt(input_ids, tokenizer)
    elif return_tensors == "tf": return image_attention_mask_for_packed_input_ids_tf(input_ids, tokenizer)
def image_attention_mask_for_packed_input_ids_pt(input_ids, tokenizer):
    image_attention_mask = torch.full_like(input_ids, fill_value=-1)
    next_image_attention_mask = torch.full_like(input_ids, fill_value=-1)
    image_token_id = tokenizer.convert_tokens_to_ids(IMAGE_TOKEN)
    eod_token_id = tokenizer.eos_token_id
    for batch_idx in range(input_ids.size(0)):
        count = -1
        seen_eod = False
        for idx, token_id in enumerate(input_ids[batch_idx]):
            if token_id == image_token_id:
                count += 1
                image_attention_mask[batch_idx][idx] = count
                seen_eod = False
            else: image_attention_mask[batch_idx][idx] = count
            if seen_eod: image_attention_mask[batch_idx][idx] = -1
            if token_id == eod_token_id: seen_eod = True
    for batch_idx in range(input_ids.size(0)):
        count = -1
        seen_eod = False
        for idx in range(input_ids[batch_idx].size(0) - 1, -1, -1):
            token_id = input_ids[batch_idx][idx]
            if token_id == image_token_id:
                count += 1
                next_image_attention_mask[batch_idx][idx] = count
                seen_eod = False
            else: next_image_attention_mask[batch_idx][idx] = count
            if token_id == eod_token_id: seen_eod = True
            if seen_eod: next_image_attention_mask[batch_idx][idx] = -1
        non_negative_indices = next_image_attention_mask[batch_idx] != -1
        next_image_attention_mask[batch_idx][non_negative_indices] -= count
        next_image_attention_mask[batch_idx][non_negative_indices] *= -1
    return image_attention_mask, next_image_attention_mask
def image_attention_mask_for_packed_input_ids_tf(input_ids, tokenizer):
    image_token_id = tokenizer.convert_tokens_to_ids(IMAGE_TOKEN)
    eod_token_id = tokenizer.eos_token_id
    batch_size = tf.shape(input_ids)[0]
    image_attention_mask = tf.fill(tf.shape(input_ids), -1)
    next_image_attention_mask = tf.fill(tf.shape(input_ids), -1)
    for batch_idx in range(batch_size):
        count = -1
        seen_eod = False
        seq_length = tf.shape(input_ids)[1]
        for idx in range(seq_length - 1, -1, -1):
            token_id = input_ids[batch_idx, idx].numpy()
            if token_id == image_token_id:
                count += 1
                indices = [[batch_idx, idx]]
                updates = [count]
                image_attention_mask = tf.tensor_scatter_nd_update(image_attention_mask, indices, updates)
                next_image_attention_mask = tf.tensor_scatter_nd_update(next_image_attention_mask, indices, updates)
            elif token_id == eod_token_id and not seen_eod:
                seen_eod = True
                count = 0
                indices = [[batch_idx, idx]]
                updates = [count]
                next_image_attention_mask = tf.tensor_scatter_nd_update(next_image_attention_mask, indices, updates)
            if seen_eod and token_id != eod_token_id:
                indices = [[batch_idx, idx]]
                updates = [-1]
                next_image_attention_mask = tf.tensor_scatter_nd_update(next_image_attention_mask, indices, updates)
    return image_attention_mask, next_image_attention_mask
def is_url(string):
    if " " in string: return False
    result = urlparse(string)
    return all([result.scheme, result.netloc])
class IdeficsProcessor(ProcessorMixin):
    attributes = ["image_processor", "tokenizer"]
    valid_kwargs = ["image_size", "add_end_of_utterance_token"]
    image_processor_class = "IdeficsImageProcessor"
    tokenizer_class = "LlamaTokenizerFast"
    def __init__(self, image_processor, tokenizer=None, image_size=224, add_end_of_utterance_token=None, **kwargs):
        if image_processor is None: raise ValueError("You need to specify an `image_processor`.")
        if tokenizer is None: raise ValueError("You need to specify a `tokenizer`.")
        super().__init__(image_processor, tokenizer)
        self.current_processor = self.image_processor
        self.image_token_id = tokenizer.convert_tokens_to_ids(IMAGE_TOKEN)
        self.default_image_dims = (self.image_processor.image_num_channels, self.image_processor.image_size, self.image_processor.image_size)
        self.tokenizer_was_trained_with_end_of_utterance_token = (True if "<end_of_utterance>" in self.tokenizer.special_tokens_map.get("additional_special_tokens", []) else False)
    def __call__(self, prompts: Union[List[TextInput], List[List[TextInput]]], padding: Union[bool, str, PaddingStrategy] = "longest", truncation: Union[bool, str, TruncationStrategy] = None,
    max_length: Optional[int] = None, transform: Callable = None, add_eos_token=False, add_end_of_utterance_token=None, debug=False, return_tensors="pt") -> BatchEncoding:
        if add_end_of_utterance_token is None: add_end_of_utterance_token = self.tokenizer_was_trained_with_end_of_utterance_token
        if not any(isinstance(i, list) for i in prompts): prompts = [prompts]
        fake_token = "<fake_token_around_image>"
        image_token = "<image>"
        end_of_utterance_token = "<end_of_utterance>"
        def image_tokens(last_was_image):
            if last_was_image: return image_token + fake_token
            else: return fake_token + image_token + fake_token
        all_prompts = []
        all_images = []
        for sample in prompts:
            full_text = f"{self.tokenizer.bos_token}"
            image_objects = []
            last_was_image = False
            last_was_text = False
            for i, item in enumerate(sample):
                if i > 0: last_was_text = True if not last_was_image else False
                if isinstance(item, str):
                    item = item.strip(" ")
                    if is_url(item):
                        image = self.image_processor.fetch_images(item)
                        full_text += image_tokens(last_was_image)
                        image_objects.append(image)
                        last_was_image = True
                    else:
                        if add_end_of_utterance_token and last_was_text: full_text += end_of_utterance_token
                        full_text += item
                        last_was_image = False
                else:
                    full_text += image_tokens(last_was_image)
                    image_objects.append(item)
                    last_was_image = True
            if add_eos_token: full_text += self.tokenizer.eos_token
            if debug is True: print(f"{full_text=}")
            image_objects = self.image_processor(image_objects, transform=transform, return_tensors=return_tensors)
            all_prompts.append(full_text)
            all_images.append(image_objects)
        text_encoding = self.tokenizer(text=all_prompts, add_special_tokens=False, padding=padding, truncation=truncation, max_length=max_length)
        all_texts = text_encoding["input_ids"]
        all_attention_masks = text_encoding["attention_mask"]
        max_num_images = max(len(x) for x in all_images)
        max_num_images = max(1, max_num_images)
        at_least_one_image = sum(len(x) for x in all_images) > 0
        output_input_ids = []
        output_images = []
        output_attention_masks = []
        for text, attention_mask, images in zip(all_texts, all_attention_masks, all_images):
            padded_input_ids = text
            image_count = padded_input_ids.count(self.image_token_id)
            local_max_num_images = min(image_count, max_num_images)
            current_images = images[:local_max_num_images]
            if len(current_images) > 0:
                if return_tensors == "pt":
                    padded_image_tensor = torch.zeros(max_num_images, *current_images.size()[1:])
                    padded_image_tensor[: current_images.size(0)] = current_images
                elif return_tensors == "tf":
                    image_shape = tf.shape(current_images)[1:]
                    padded_shape = tf.concat([[max_num_images], image_shape], axis=0)
                    padded_image_tensor = tf.zeros(padded_shape, dtype=current_images.dtype)
                    num_images = tf.shape(current_images)[0]
                    indices = tf.reshape(tf.range(num_images), (-1, 1))
                    updates = current_images
                    padded_image_tensor = tf.tensor_scatter_nd_update(padded_image_tensor, indices, updates)
            else:
                if return_tensors == "pt": padded_image_tensor = torch.zeros(max_num_images, *self.default_image_dims)
                elif return_tensors == "tf": padded_image_tensor = tf.zeros((max_num_images, *self.default_image_dims))
            output_images.append(padded_image_tensor)
            if return_tensors == "pt":
                output_input_ids.append(torch.tensor(padded_input_ids))
                output_attention_masks.append(torch.tensor(attention_mask))
            elif return_tensors == "tf":
                output_input_ids.append(tf.convert_to_tensor(padded_input_ids, dtype=tf.int32))
                output_attention_masks.append(attention_mask)
        if return_tensors == "pt":
            output_input_ids = torch.stack(output_input_ids)
            output_images = torch.stack(output_images)
            output_attention_masks = torch.stack(output_attention_masks)
        elif return_tensors == "tf":
            output_input_ids = tf.stack(output_input_ids)
            output_images = tf.stack(output_images)
            output_attention_masks = tf.stack(output_attention_masks)
        if at_least_one_image:
            image_attention_mask, _ = image_attention_mask_for_packed_input_ids(output_input_ids, self.tokenizer, return_tensors)
            image_attention_mask = incremental_to_binary_attention_mask(image_attention_mask, return_tensors, num_classes=max_num_images)
        else:
            if return_tensors == "pt": image_attention_mask = torch.zeros(output_input_ids.shape[0], output_input_ids.shape[1], 1, dtype=torch.bool)
            elif return_tensors == "tf": image_attention_mask = tf.zeros((output_input_ids.shape[0], output_input_ids.shape[1], 1), dtype=tf.bool)
        return BatchFeature(data={"input_ids": output_input_ids, "attention_mask": output_attention_masks, "pixel_values": output_images, "image_attention_mask": image_attention_mask})
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
