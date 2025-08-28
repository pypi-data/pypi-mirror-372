"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import copy
import math
import re
from typing import List, Optional, Tuple, Union
from ...image_processing_utils import BatchFeature
from ...image_utils import ImageInput, is_batched
from ...processing_utils import ImagesKwargs, ProcessingKwargs, ProcessorMixin, TextKwargs, Unpack
from ...tokenization_utils import AddedToken
from ...tokenization_utils_base import BatchEncoding, TextInput
BboxInput = Union[List[Tuple[int, int]], List[Tuple[float, float, float, float]], List[List[Tuple[int, int]]], List[List[Tuple[float, float, float]]]]
class Kosmos2ImagesKwargs(ImagesKwargs, total=False):
    bboxes: Optional[List[float]]
    num_image_tokens: Optional[int]
    first_image_token_id: Optional[int]
class Kosmos2TextKwargs(TextKwargs, total=False): add_eos_token: Optional[bool]
class Kosmos2ProcessorKwargs(ProcessingKwargs, total=False):
    text_kwargs: Kosmos2TextKwargs
    images_kwargs: Kosmos2ImagesKwargs
    _defaults = {"text_kwargs": {'add_special_tokens': True, 'padding': False, 'stride': 0, 'return_overflowing_tokens': False, 'return_special_tokens_mask': False, 'return_offsets_mapping': False,
    'return_token_type_ids': False, 'verbose': True, 'add_eos_token': False}, "images_kwargs": {'num_image_tokens': 64}}
class Kosmos2Processor(ProcessorMixin):
    attributes = ["image_processor", "tokenizer"]
    valid_kwargs = ["num_patch_index_tokens"]
    image_processor_class = "CLIPImageProcessor"
    tokenizer_class = "AutoTokenizer"
    def __init__(self, image_processor, tokenizer, num_patch_index_tokens=1024, *kwargs):
        tokenizer.return_token_type_ids = False
        self.eod_token = "</doc>"
        self.boi_token = "<image>"
        self.eoi_token = "</image>"
        self.eoc_token = "</chunk>"
        self.eol_token = "</line>"
        self.bop_token = "<phrase>"
        self.eop_token = "</phrase>"
        self.boo_token = "<object>"
        self.eoo_token = "</object>"
        self.dom_token = "</delimiter_of_multi_objects/>"
        self.grd_token = "<grounding>"
        self.tag_tokens = [self.eod_token, self.boi_token, self.eoi_token, self.eoc_token, self.eol_token, self.bop_token, self.eop_token, self.boo_token, self.eoo_token, self.dom_token, self.grd_token]
        self.num_patch_index_tokens = num_patch_index_tokens
        patch_index_tokens = [f"<patch_index_{str(x).zfill(4)}>" for x in range(self.num_patch_index_tokens)]
        tokens_to_add = []
        for token in self.tag_tokens + patch_index_tokens: tokens_to_add.append(AddedToken(token, lstrip=True, rstrip=False, normalized=False))
        tokenizer.add_tokens(tokens_to_add)
        super().__init__(image_processor, tokenizer)
    def __call__(self, images: ImageInput = None, text: Union[TextInput, List[TextInput]] = None, audio=None, videos=None, **kwargs: Unpack[Kosmos2ProcessorKwargs]) -> BatchFeature:
        if images is None and text is None: raise ValueError("You have to specify either images or text.")
        output_kwargs = self._merge_kwargs(Kosmos2ProcessorKwargs, tokenizer_init_kwargs=self.tokenizer.init_kwargs, **kwargs)
        bboxes = output_kwargs["images_kwargs"].pop("bboxes", None)
        num_image_tokens = output_kwargs["images_kwargs"].pop("num_image_tokens", 64)
        first_image_token_id = output_kwargs["images_kwargs"].pop("first_image_token_id", None)
        add_eos_token = output_kwargs["text_kwargs"].pop("add_eos_token", False)
        add_special_tokens = output_kwargs["text_kwargs"]["add_special_tokens"]
        padding = output_kwargs["text_kwargs"]["padding"]
        return_tensors = output_kwargs["text_kwargs"].setdefault("return_tensors", None)
        encoding = BatchFeature()
        if images is not None:
            image_encoding = self.image_processor(images, **output_kwargs["images_kwargs"])
            encoding.update(image_encoding)
        if text is not None:
            text = self.preprocess_examples(text, images, bboxes, num_image_tokens=num_image_tokens)
            if add_special_tokens and not add_eos_token:
                if isinstance(text, str): text = f"{self.tokenizer.bos_token}{text}"
                elif isinstance(text, list): text = [f"{self.tokenizer.bos_token}{s}" for s in text]
            output_kwargs["text_kwargs"]["add_special_tokens"] = (output_kwargs["text_kwargs"]["add_special_tokens"] and add_eos_token)
            output_kwargs["text_kwargs"]["padding"] = padding if images is None else False
            output_kwargs["text_kwargs"]["return_tensors"] = return_tensors if images is None else None
            text_encoding = self.tokenizer(text=text, **output_kwargs["text_kwargs"])
            encoding.update(text_encoding)
        output_kwargs["text_kwargs"]["add_special_tokens"] = add_special_tokens
        output_kwargs["text_kwargs"]["padding"] = padding
        output_kwargs["text_kwargs"]["return_tensors"] = return_tensors
        if text is not None and images is not None:
            if first_image_token_id is None: first_image_token_id = self.tokenizer.unk_token_id + 1
            with_bos = add_special_tokens
            start_index = int(with_bos) + 1
            image_token_ids = list(range(first_image_token_id, first_image_token_id + num_image_tokens))
            base_image_embeds_position_mask = [0] + [1] * num_image_tokens + [0]
            input_ids = []
            image_embeds_position_mask = []
            all_input_ids = encoding["input_ids"]
            if isinstance(text, str):
                all_input_ids = [all_input_ids]
                encoding["attention_mask"] = [encoding["attention_mask"]]
            for text_ids in all_input_ids:
                text_ids = text_ids[:start_index] + image_token_ids + text_ids[start_index + num_image_tokens :]
                input_ids.append(text_ids)
                mask = copy.copy(base_image_embeds_position_mask)
                if with_bos: mask = [0] + mask
                mask += [0] * (len(text_ids) - len(mask))
                image_embeds_position_mask.append(mask)
            if isinstance(text, list):
                sorted_length = sorted([(idx, len(x)) for idx, x in enumerate(text_encoding.input_ids)], key=lambda x: x[-1])
                _, min_len_not_padded = sorted_length[0]
                idx, _ = sorted_length[-1]
                output_kwargs["text_kwargs"]["add_special_tokens"] = (output_kwargs["text_kwargs"]["add_special_tokens"] and add_eos_token)
                output_kwargs["text_kwargs"]["return_tensors"] = None
                text_encoding = self.tokenizer(text=[text[idx]], **output_kwargs["text_kwargs"])
                max_len_padded = len(text_encoding.input_ids[0])
                if min_len_not_padded != max_len_padded:
                    if self.tokenizer.padding_side == "right":
                        input_ids = [x + [self.tokenizer.pad_token_id] * (max_len_padded - len(x)) for x in input_ids]
                        image_embeds_position_mask = [x + [0] * (max_len_padded - len(x)) for x in image_embeds_position_mask]
                        encoding["attention_mask"] = [x + [0] * (max_len_padded - len(x)) for x in encoding["attention_mask"]]
                    elif self.tokenizer.padding_side == "left":
                        input_ids = [[self.tokenizer.pad_token_id] * (max_len_padded - len(x)) + x for x in input_ids]
                        image_embeds_position_mask = [[0] * (max_len_padded - len(x)) + x for x in image_embeds_position_mask]
                        encoding["attention_mask"] = [[0] * (max_len_padded - len(x)) + x for x in encoding["attention_mask"]]
            if isinstance(text, str) and return_tensors is None:
                input_ids = input_ids[0]
                encoding["attention_mask"] = encoding["attention_mask"][0]
                image_embeds_position_mask = image_embeds_position_mask[0]
            encoding.update(BatchEncoding(data={"input_ids": input_ids, "attention_mask": encoding["attention_mask"], "image_embeds_position_mask": image_embeds_position_mask}, tensor_type=return_tensors))
        return encoding
    def _check_bboxes_for_single_text(self, bboxes):
        if bboxes is None: return
        elif not isinstance(bboxes, list): raise ValueError("`bboxes` (for a single text example) should be `None` or a list.")
        for bbox in bboxes:
            if bbox is None: continue
            elif not isinstance(bbox, list): bbox = [bbox]
            for element in bbox:
                if not isinstance(element, tuple) or not ((len(element) == 2 and all(isinstance(x, int)
                for x in element)) or (len(element) == 4 and all(isinstance(x, float) for x in element))):
                    raise ValueError("Each element in `bboxes` (for a single text example) should be either `None`, a tuple containing 2 integers or 4 float point numbers, or a list containing such tuples. Also make sure the arguments `texts` and `bboxes` passed to `preprocess_text` are both in batches or both for a single example.")
    def _preprocess_single_example(self, text, image, bboxes, img_info_tokens):
        text = text.strip()
        if image is not None: text = f"{img_info_tokens} {text}"
        text = self._insert_patch_index_tokens(text, bboxes)
        return text
    def preprocess_examples(self, texts: Union[TextInput, List[TextInput]], images: ImageInput = None, bboxes: BboxInput = None, num_image_tokens: Optional[int] = 64) -> Union[str, List[str]]:
        img_tokens = [self.boi_token] * num_image_tokens
        img_info_tokens = " ".join([self.boi_token] + img_tokens + [self.eoi_token])
        batched = True
        if isinstance(texts, str):
            batched = False
            texts = [texts]
        if images is None: images = [None] * len(texts)
        elif not is_batched(images): images = [images]
        if len(texts) != len(images): raise ValueError(f"The number of examples in `texts` and `images` should be the same. Got {len(texts)} v.s. {len(images)} instead.")
        if not batched:
            self._check_bboxes_for_single_text(bboxes)
            bboxes = [bboxes]
        elif bboxes is not None:
            if not isinstance(bboxes, list): raise ValueError("`bboxes` should be `None` or a list (as a batch) when `texts` is passed as a batch.")
            for x in bboxes: self._check_bboxes_for_single_text(x)
        else: bboxes = [None] * len(texts)
        if len(bboxes) != len(texts): raise ValueError(f"The number of examples in `texts` and `bboxes` should be the same. Got {len(texts)} v.s. {len(bboxes)} instead.")
        result = [self._preprocess_single_example(text, image, bbox, img_info_tokens) for text, image, bbox in zip(texts, images, bboxes)]
        if not batched: result = result[0]
        return result
    def batch_decode(self, *args, **kwargs): return self.tokenizer.batch_decode(*args, **kwargs)
    def decode(self, *args, **kwargs): return self.tokenizer.decode(*args, **kwargs)
    def post_process_generation(self, text, cleanup_and_extract=True):
        caption = text.split(self.eoi_token)[-1]
        if cleanup_and_extract: return clean_text_and_extract_entities_with_bboxes(caption)
        return caption
    @property
    def model_input_names(self):
        tokenizer_input_names = self.tokenizer.model_input_names
        image_processor_input_names = self.image_processor.model_input_names
        return list(dict.fromkeys(tokenizer_input_names + image_processor_input_names))
    def _insert_patch_index_tokens(self, text: str, bboxes: Union[List[Tuple[int]], List[Tuple[float]]]) -> str:
        if bboxes is None or len(bboxes) == 0: return text
        matched_phrases = list(re.finditer(r"<phrase>.+?</phrase>", string=text))
        if len(matched_phrases) != len(bboxes): raise ValueError(f"The number of elements in `bboxes` should be the same as the number of `<phrase> ... </phrase>` pairs in `text`. Got {len(matched_phrases)} v.s. {len(bboxes)} instead.")
        curr_pos = 0
        buffer = []
        for matched, bbox in zip(matched_phrases, bboxes):
            _, end = matched.span()
            buffer.append(text[curr_pos:end])
            curr_pos = end
            if bbox is None: continue
            if isinstance(bbox, tuple): bbox = [bbox]
            patch_index_strings = []
            if not all(box is not None for box in bbox): raise ValueError("The multiple bounding boxes for a single phrase should not contain any `None` value.")
            for box in bbox:
                patch_index_1, patch_index_2 = self._convert_bbox_to_patch_index_tokens(box)
                patch_index_strings.append(f"{patch_index_1} {patch_index_2}")
            if len(patch_index_strings) == 0: continue
            position_str = " </delimiter_of_multi_objects/> ".join(patch_index_strings)
            buffer.append(f"<object> {position_str} </object>")
        if curr_pos < len(text): buffer.append(text[curr_pos:])
        text = "".join(buffer)
        return text
    def _convert_bbox_to_patch_index_tokens(self, bbox: Union[Tuple[int, int], Tuple[float, float, float, float]]) -> Tuple[str, str]:
        if len(bbox) == 2: idx_1, idx_2 = bbox
        else:
            num_patches_per_side = int(math.sqrt(self.num_patch_index_tokens))
            idx_1, idx_2 = coordinate_to_patch_index(bbox, num_patches_per_side)
        token_1 = f"<patch_index_{str(idx_1).zfill(4)}>"
        token_2 = f"<patch_index_{str(idx_2).zfill(4)}>"
        return token_1, token_2
def coordinate_to_patch_index(bbox: Tuple[float, float, float, float], num_patches_per_side: int) -> Tuple[int, int]:
    (x1, y1, x2, y2) = bbox
    if not (x2 > x1 and y2 > y1): raise ValueError("The coordinates in `bbox` should be `(x1, y1, x2, y2)` with `x2 > x1` and `y2 > y1`.")
    ul_x = math.floor(x1 * num_patches_per_side)
    ul_y = math.floor(y1 * num_patches_per_side)
    lr_x = math.ceil(x2 * num_patches_per_side - 1)
    lr_y = math.ceil(y2 * num_patches_per_side - 1)
    ul_idx = ul_y * num_patches_per_side + ul_x
    lr_idx = lr_y * num_patches_per_side + lr_x
    return ul_idx, lr_idx
def patch_index_to_coordinate(ul_idx: int, lr_idx: int, num_patches_per_side: int):
    cell_size = 1.0 / num_patches_per_side
    ul_x = ul_idx % num_patches_per_side
    ul_y = ul_idx // num_patches_per_side
    lr_x = lr_idx % num_patches_per_side
    lr_y = lr_idx // num_patches_per_side
    if ul_idx == lr_idx:
        x1 = ul_x * cell_size
        y1 = ul_y * cell_size
        x2 = lr_x * cell_size + cell_size
        y2 = lr_y * cell_size + cell_size
    elif ul_x == lr_x or ul_y == lr_y:
        x1 = ul_x * cell_size
        y1 = ul_y * cell_size
        x2 = lr_x * cell_size + cell_size
        y2 = lr_y * cell_size + cell_size
    else:
        x1 = ul_x * cell_size + cell_size / 2
        y1 = ul_y * cell_size + cell_size / 2
        x2 = lr_x * cell_size + cell_size / 2
        y2 = lr_y * cell_size + cell_size / 2
    return x1, y1, x2, y2
def extract_entities_with_patch_indices(text):
    pattern = r"(?:(<phrase>([^<]+)</phrase>))?<object>((?:<patch_index_\d+><patch_index_\d+></delimiter_of_multi_objects/>)*<patch_index_\d+><patch_index_\d+>)</object>"
    matches = re.finditer(pattern, text)
    entities_with_patch_indices = []
    for match in matches:
        span = match.span(2)
        phrase_tag, phrase, match_content = match.groups()
        if not phrase_tag:
            phrase = None
            span = (match.span(0)[0], match.span(0)[0])
        patch_index_pairs = match_content.split("</delimiter_of_multi_objects/>")
        entity_bboxes = []
        for pair in patch_index_pairs:
            x = re.search(r"<patch_index_(\d+)>", pair)
            y = re.search(r"<patch_index_(\d+)>", pair[1:])
            if x and y:
                if phrase: entity_bboxes.append((int(x.group(1)), int(y.group(1))))
                else: entity_bboxes.append((int(x.group(1)), int(y.group(1))))
        if phrase: entities_with_patch_indices.append((phrase, span, entity_bboxes))
        else:
            for bbox in entity_bboxes:
                entity = f"<patch_index_{bbox[0]}><patch_index_{bbox[1]}>"
                entities_with_patch_indices.append((entity, span, [bbox]))
    return entities_with_patch_indices
def adjust_entity_positions(entity, text):
    entity_name, (start, end) = entity
    adjusted_start = len(re.sub("<.*?>", "", text[:start]))
    adjusted_end = len(re.sub("<.*?>", "", text[:end]))
    adjusted_entity = (entity_name, (adjusted_start, adjusted_end))
    return adjusted_entity
def _cleanup_spaces(text, entities):
    new_text = text.strip()
    leading_spaces = len(text) - len(text.lstrip())
    new_entities = []
    for entity_name, (start, end), bboxes in entities:
        entity_name_leading_spaces = len(entity_name) - len(entity_name.lstrip())
        entity_name_trailing_spaces = len(entity_name) - len(entity_name.rstrip())
        start = start - leading_spaces + entity_name_leading_spaces
        end = end - leading_spaces - entity_name_trailing_spaces
        entity_name = entity_name.strip()
        new_entities.append((entity_name, (start, end), bboxes))
    return new_text, new_entities
def clean_text_and_extract_entities_with_bboxes(text, num_patches_per_side=32):
    processed_text = re.sub("<.*?>", "", text)
    entities_with_patch_indices = extract_entities_with_patch_indices(text)
    entities = []
    for item in entities_with_patch_indices:
        entity, bboxes = item[0:2], item[2]
        adjusted_entity = adjust_entity_positions(entity, text)
        bboxes_in_coords = [patch_index_to_coordinate(bbox[0], bbox[1], num_patches_per_side) for bbox in bboxes]
        entities.append(adjusted_entity + (bboxes_in_coords,))
    return _cleanup_spaces(processed_text, entities)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
