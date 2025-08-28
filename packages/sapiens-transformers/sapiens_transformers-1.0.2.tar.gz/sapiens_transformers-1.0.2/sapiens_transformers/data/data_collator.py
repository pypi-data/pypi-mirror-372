"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import random
import warnings
from collections.abc import Mapping
from dataclasses import dataclass
from random import randint
from typing import Any, Callable, Dict, List, NewType, Optional, Tuple, Union
import numpy as np
from ..models.bert import BertTokenizer, BertTokenizerFast
from ..tokenization_utils_base import PreTrainedTokenizerBase
from ..utils import PaddingStrategy
InputDataClass = NewType("InputDataClass", Any)
DataCollator = NewType("DataCollator", Callable[[List[InputDataClass]], Dict[str, Any]])
class DataCollatorMixin:
    def __call__(self, features, return_tensors=None):
        if return_tensors is None: return_tensors = self.return_tensors
        if return_tensors == "tf": return self.tf_call(features)
        elif return_tensors == "pt": return self.torch_call(features)
        elif return_tensors == "np": return self.numpy_call(features)
        else: raise ValueError(f"Framework '{return_tensors}' not recognized!")
def pad_without_fast_tokenizer_warning(tokenizer, *pad_args, **pad_kwargs):
    if not hasattr(tokenizer, "deprecation_warnings"): return tokenizer.pad(*pad_args, **pad_kwargs)
    warning_state = tokenizer.deprecation_warnings.get("Asking-to-pad-a-fast-tokenizer", False)
    tokenizer.deprecation_warnings["Asking-to-pad-a-fast-tokenizer"] = True
    try: padded = tokenizer.pad(*pad_args, **pad_kwargs)
    finally: tokenizer.deprecation_warnings["Asking-to-pad-a-fast-tokenizer"] = warning_state
    return padded
def default_data_collator(features: List[InputDataClass], return_tensors="pt") -> Dict[str, Any]:
    if return_tensors == "pt": return torch_default_data_collator(features)
    elif return_tensors == "tf": return tf_default_data_collator(features)
    elif return_tensors == "np": return numpy_default_data_collator(features)
@dataclass
class DefaultDataCollator(DataCollatorMixin):
    return_tensors: str = "pt"
    def __call__(self, features: List[Dict[str, Any]], return_tensors=None) -> Dict[str, Any]:
        if return_tensors is None: return_tensors = self.return_tensors
        return default_data_collator(features, return_tensors)
def torch_default_data_collator(features: List[InputDataClass]) -> Dict[str, Any]:
    import torch
    if not isinstance(features[0], Mapping): features = [vars(f) for f in features]
    first = features[0]
    batch = {}
    if "label" in first and first["label"] is not None:
        label = first["label"].item() if isinstance(first["label"], torch.Tensor) else first["label"]
        dtype = torch.long if isinstance(label, int) else torch.float
        batch["labels"] = torch.tensor([f["label"] for f in features], dtype=dtype)
    elif "label_ids" in first and first["label_ids"] is not None:
        if isinstance(first["label_ids"], torch.Tensor): batch["labels"] = torch.stack([f["label_ids"] for f in features])
        else:
            dtype = torch.long if isinstance(first["label_ids"][0], int) else torch.float
            batch["labels"] = torch.tensor([f["label_ids"] for f in features], dtype=dtype)
    for k, v in first.items():
        if k not in ("label", "label_ids") and v is not None and not isinstance(v, str):
            if isinstance(v, torch.Tensor): batch[k] = torch.stack([f[k] for f in features])
            elif isinstance(v, np.ndarray): batch[k] = torch.from_numpy(np.stack([f[k] for f in features]))
            else: batch[k] = torch.tensor([f[k] for f in features])
    return batch
def tf_default_data_collator(features: List[InputDataClass]) -> Dict[str, Any]:
    import tensorflow as tf
    if not isinstance(features[0], Mapping): features = [vars(f) for f in features]
    first = features[0]
    batch = {}
    if "label" in first and first["label"] is not None: label_col_name = "label"
    elif "label_ids" in first and first["label_ids"] is not None: label_col_name = "label_ids"
    elif "labels" in first and first["labels"] is not None: label_col_name = "labels"
    else: label_col_name = None
    if label_col_name is not None:
        if isinstance(first[label_col_name], tf.Tensor): dtype = tf.int64 if first[label_col_name].dtype.is_integer else tf.float32
        elif isinstance(first[label_col_name], np.ndarray) or isinstance(first[label_col_name], np.generic): dtype = tf.int64 if np.issubdtype(first[label_col_name].dtype, np.integer) else tf.float32
        elif isinstance(first[label_col_name], (tuple, list)): dtype = tf.int64 if isinstance(first[label_col_name][0], int) else tf.float32
        else: dtype = tf.int64 if isinstance(first[label_col_name], int) else tf.float32
        batch["labels"] = tf.convert_to_tensor([f[label_col_name] for f in features], dtype=dtype)
    for k, v in first.items():
        if k not in ("label", "label_ids", "labels") and v is not None and not isinstance(v, str):
            if isinstance(v, (tf.Tensor, np.ndarray)): batch[k] = tf.stack([f[k] for f in features])
            else: batch[k] = tf.convert_to_tensor([f[k] for f in features])
    return batch
def numpy_default_data_collator(features: List[InputDataClass]) -> Dict[str, Any]:
    if not isinstance(features[0], Mapping): features = [vars(f) for f in features]
    first = features[0]
    batch = {}
    if "label" in first and first["label"] is not None:
        label = first["label"].item() if isinstance(first["label"], np.ndarray) else first["label"]
        dtype = np.int64 if isinstance(label, int) else np.float32
        batch["labels"] = np.array([f["label"] for f in features], dtype=dtype)
    elif "label_ids" in first and first["label_ids"] is not None:
        if isinstance(first["label_ids"], np.ndarray): batch["labels"] = np.stack([f["label_ids"] for f in features])
        else:
            dtype = np.int64 if isinstance(first["label_ids"][0], int) else np.float32
            batch["labels"] = np.array([f["label_ids"] for f in features], dtype=dtype)
    for k, v in first.items():
        if k not in ("label", "label_ids") and v is not None and not isinstance(v, str):
            if isinstance(v, np.ndarray): batch[k] = np.stack([f[k] for f in features])
            else: batch[k] = np.array([f[k] for f in features])
    return batch
@dataclass
class DataCollatorWithPadding:
    tokenizer: PreTrainedTokenizerBase
    padding: Union[bool, str, PaddingStrategy] = True
    max_length: Optional[int] = None
    pad_to_multiple_of: Optional[int] = None
    return_tensors: str = "pt"
    def __call__(self, features: List[Dict[str, Any]]) -> Dict[str, Any]:
        batch = pad_without_fast_tokenizer_warning(self.tokenizer, features, padding=self.padding, max_length=self.max_length, pad_to_multiple_of=self.pad_to_multiple_of, return_tensors=self.return_tensors)
        if "label" in batch:
            batch["labels"] = batch["label"]
            del batch["label"]
        if "label_ids" in batch:
            batch["labels"] = batch["label_ids"]
            del batch["label_ids"]
        return batch
@dataclass
class DataCollatorForTokenClassification(DataCollatorMixin):
    tokenizer: PreTrainedTokenizerBase
    padding: Union[bool, str, PaddingStrategy] = True
    max_length: Optional[int] = None
    pad_to_multiple_of: Optional[int] = None
    label_pad_token_id: int = -100
    return_tensors: str = "pt"
    def torch_call(self, features):
        import torch
        label_name = "label" if "label" in features[0].keys() else "labels"
        labels = [feature[label_name] for feature in features] if label_name in features[0].keys() else None
        no_labels_features = [{k: v for k, v in feature.items() if k != label_name} for feature in features]
        batch = pad_without_fast_tokenizer_warning(self.tokenizer, no_labels_features, padding=self.padding, max_length=self.max_length, pad_to_multiple_of=self.pad_to_multiple_of, return_tensors="pt")
        if labels is None: return batch
        sequence_length = batch["input_ids"].shape[1]
        padding_side = self.tokenizer.padding_side
        def to_list(tensor_or_iterable):
            if isinstance(tensor_or_iterable, torch.Tensor): return tensor_or_iterable.tolist()
            return list(tensor_or_iterable)
        if padding_side == "right": batch[label_name] = [to_list(label) + [self.label_pad_token_id] * (sequence_length - len(label)) for label in labels]
        else: batch[label_name] = [[self.label_pad_token_id] * (sequence_length - len(label)) + to_list(label) for label in labels]
        batch[label_name] = torch.tensor(batch[label_name], dtype=torch.int64)
        return batch
    def tf_call(self, features):
        import tensorflow as tf
        label_name = "label" if "label" in features[0].keys() else "labels"
        labels = [feature[label_name] for feature in features] if label_name in features[0].keys() else None
        batch = pad_without_fast_tokenizer_warning(self.tokenizer, features, padding=self.padding, max_length=self.max_length, pad_to_multiple_of=self.pad_to_multiple_of, return_tensors="tf" if labels is None else None)
        if labels is None: return batch
        sequence_length = tf.convert_to_tensor(batch["input_ids"]).shape[1]
        padding_side = self.tokenizer.padding_side
        if padding_side == "right": batch["labels"] = [list(label) + [self.label_pad_token_id] * (sequence_length - len(label)) for label in labels]
        else: batch["labels"] = [[self.label_pad_token_id] * (sequence_length - len(label)) + list(label) for label in labels]
        batch = {k: tf.convert_to_tensor(v, dtype=tf.int64) for k, v in batch.items()}
        return batch
    def numpy_call(self, features):
        label_name = "label" if "label" in features[0].keys() else "labels"
        labels = [feature[label_name] for feature in features] if label_name in features[0].keys() else None
        batch = pad_without_fast_tokenizer_warning(self.tokenizer, features, padding=self.padding, max_length=self.max_length, pad_to_multiple_of=self.pad_to_multiple_of, return_tensors="np" if labels is None else None)
        if labels is None: return batch
        sequence_length = np.array(batch["input_ids"]).shape[1]
        padding_side = self.tokenizer.padding_side
        if padding_side == "right": batch["labels"] = [list(label) + [self.label_pad_token_id] * (sequence_length - len(label)) for label in labels]
        else: batch["labels"] = [[self.label_pad_token_id] * (sequence_length - len(label)) + list(label) for label in labels]
        batch = {k: np.array(v, dtype=np.int64) for k, v in batch.items()}
        return batch
def _torch_collate_batch(examples, tokenizer, pad_to_multiple_of: Optional[int] = None):
    import torch
    if isinstance(examples[0], (list, tuple, np.ndarray)): examples = [torch.tensor(e, dtype=torch.long) for e in examples]
    length_of_first = examples[0].size(0)
    are_tensors_same_length = all(x.size(0) == length_of_first for x in examples)
    if are_tensors_same_length and (pad_to_multiple_of is None or length_of_first % pad_to_multiple_of == 0): return torch.stack(examples, dim=0)
    if tokenizer._pad_token is None: raise ValueError(f"You are attempting to pad samples but the tokenizer you are using ({tokenizer.__class__.__name__}) does not have a pad token.")
    max_length = max(x.size(0) for x in examples)
    if pad_to_multiple_of is not None and (max_length % pad_to_multiple_of != 0): max_length = ((max_length // pad_to_multiple_of) + 1) * pad_to_multiple_of
    result = examples[0].new_full([len(examples), max_length], tokenizer.pad_token_id)
    for i, example in enumerate(examples):
        if tokenizer.padding_side == "right": result[i, : example.shape[0]] = example
        else: result[i, -example.shape[0] :] = example
    return result
def _tf_collate_batch(examples, tokenizer, pad_to_multiple_of: Optional[int] = None):
    import tensorflow as tf
    if isinstance(examples[0], (list, tuple)): examples = [tf.convert_to_tensor(e, dtype=tf.int64) for e in examples]
    length_of_first = len(examples[0])
    are_tensors_same_length = all(len(x) == length_of_first for x in examples)
    if are_tensors_same_length and (pad_to_multiple_of is None or length_of_first % pad_to_multiple_of == 0): return tf.stack(examples, axis=0)
    if tokenizer._pad_token is None: raise ValueError(f"You are attempting to pad samples but the tokenizer you are using ({tokenizer.__class__.__name__}) does not have a pad token.")
    max_length = max(len(x) for x in examples)
    if pad_to_multiple_of is not None and (max_length % pad_to_multiple_of != 0): max_length = ((max_length // pad_to_multiple_of) + 1) * pad_to_multiple_of
    result = []
    rank = tf.rank(examples[0])
    paddings = np.zeros((rank, 2), dtype=np.int32)
    for example in examples:
        if tokenizer.padding_side == "right": paddings[0, 1] = max_length - len(example)
        else: paddings[0, 0] = max_length - len(example)
        result.append(tf.pad(example, paddings, constant_values=tokenizer.pad_token_id))
    return tf.stack(result, axis=0)
def _numpy_collate_batch(examples, tokenizer, pad_to_multiple_of: Optional[int] = None):
    if isinstance(examples[0], (list, tuple)): examples = [np.array(e, dtype=np.int64) for e in examples]
    length_of_first = len(examples[0])
    are_tensors_same_length = all(len(x) == length_of_first for x in examples)
    if are_tensors_same_length and (pad_to_multiple_of is None or length_of_first % pad_to_multiple_of == 0): return np.stack(examples, axis=0)
    if tokenizer._pad_token is None: raise ValueError(f"You are attempting to pad samples but the tokenizer you are using ({tokenizer.__class__.__name__}) does not have a pad token.")
    max_length = max(len(x) for x in examples)
    if pad_to_multiple_of is not None and (max_length % pad_to_multiple_of != 0): max_length = ((max_length // pad_to_multiple_of) + 1) * pad_to_multiple_of
    result = np.full(shape=(len(examples), max_length), fill_value=tokenizer.pad_token_id, dtype=examples[0].dtype)
    for i, example in enumerate(examples):
        if tokenizer.padding_side == "right": result[i, : example.shape[0]] = example
        else: result[i, -example.shape[0] :] = example
    return result
def tolist(x):
    if isinstance(x, list): return x
    elif hasattr(x, "numpy"): x = x.numpy()
    return x.tolist()
@dataclass
class DataCollatorForSeq2Seq:
    tokenizer: PreTrainedTokenizerBase
    model: Optional[Any] = None
    padding: Union[bool, str, PaddingStrategy] = True
    max_length: Optional[int] = None
    pad_to_multiple_of: Optional[int] = None
    label_pad_token_id: int = -100
    return_tensors: str = "pt"
    def __call__(self, features, return_tensors=None):
        if return_tensors is None: return_tensors = self.return_tensors
        label_name = "label" if "label" in features[0].keys() else "labels"
        labels = [feature[label_name] for feature in features] if label_name in features[0].keys() else None
        if labels is not None and all(label is None for label in labels): labels = None
        non_labels_features = [{k: v for k, v in feature.items() if k != label_name} for feature in features]
        batch = pad_without_fast_tokenizer_warning(self.tokenizer, non_labels_features, padding=self.padding, max_length=self.max_length, pad_to_multiple_of=self.pad_to_multiple_of, return_tensors=return_tensors)
        no_padding = self.padding is False or self.padding == PaddingStrategy.DO_NOT_PAD
        if labels is not None:
            if no_padding:
                if isinstance(features[0][label_name], list): batch["labels"] = list(labels)
                else: batch["labels"] = [np.concatenate([label, []]) for label in labels]
            else:
                max_padding = self.padding == PaddingStrategy.MAX_LENGTH and self.max_length is not None
                max_label_length = max(len(l) for l in labels) if not max_padding else self.max_length
                if self.pad_to_multiple_of is not None: max_label_length = ((max_label_length + self.pad_to_multiple_of - 1) // self.pad_to_multiple_of * self.pad_to_multiple_of)
                padding_side = self.tokenizer.padding_side
                if isinstance(features[0][label_name], list): batch["labels"] = [label + [self.label_pad_token_id] * (max_label_length - len(label)) if padding_side == "right" else [self.label_pad_token_id] * (max_label_length - len(label)) + label for label in labels]
                else: batch["labels"] = [np.concatenate([label, np.array([self.label_pad_token_id] * (max_label_length - len(label)), dtype=np.int64)]) if padding_side == "right" else np.concatenate([np.array([self.label_pad_token_id] * (max_label_length - len(label)), dtype=np.int64), label]) for label in labels]
        if batch.get("labels", None) is not None:
            if return_tensors == "pt":
                import torch
                batch["labels"] = torch.tensor(batch["labels"], dtype=torch.int64)
            elif return_tensors == "tf":
                import tensorflow as tf
                batch["labels"] = tf.constant(batch["labels"], dtype=tf.int64)
            else: batch["labels"] = np.array(batch["labels"], dtype=np.int64)
        else: batch["labels"] = None
        if (labels is not None and self.model is not None and hasattr(self.model, "prepare_decoder_input_ids_from_labels")):
            decoder_input_ids = self.model.prepare_decoder_input_ids_from_labels(labels=batch["labels"])
            batch["decoder_input_ids"] = decoder_input_ids
        return batch
@dataclass
class DataCollatorForLanguageModeling(DataCollatorMixin):
    tokenizer: PreTrainedTokenizerBase
    mlm: bool = True
    mlm_probability: float = 0.15
    pad_to_multiple_of: Optional[int] = None
    tf_experimental_compile: bool = False
    return_tensors: str = "pt"
    def __post_init__(self):
        if self.mlm and self.tokenizer.mask_token is None: raise ValueError("This tokenizer does not have a mask token which is necessary for masked language modeling. You should pass `mlm=False` to train on causal language modeling instead.")
        if self.tf_experimental_compile:
            import tensorflow as tf
            self.tf_mask_tokens = tf.function(self.tf_mask_tokens, jit_compile=True)
    @staticmethod
    def tf_bernoulli(shape, probability):
        import tensorflow as tf
        prob_matrix = tf.fill(shape, probability)
        return tf.cast(prob_matrix - tf.random.uniform(shape, 0, 1) >= 0, tf.bool)
    def tf_mask_tokens(self, inputs: Any, vocab_size, mask_token_id, special_tokens_mask: Optional[Any] = None) -> Tuple[Any, Any]:
        import tensorflow as tf
        mask_token_id = tf.cast(mask_token_id, inputs.dtype)
        input_shape = tf.shape(inputs)
        masked_indices = self.tf_bernoulli(input_shape, self.mlm_probability) & ~special_tokens_mask
        labels = tf.where(masked_indices, inputs, -100)
        indices_replaced = self.tf_bernoulli(input_shape, 0.8) & masked_indices
        inputs = tf.where(indices_replaced, mask_token_id, inputs)
        indices_random = self.tf_bernoulli(input_shape, 0.5) & masked_indices & ~indices_replaced
        random_words = tf.random.uniform(input_shape, maxval=vocab_size, dtype=inputs.dtype)
        inputs = tf.where(indices_random, random_words, inputs)
        return inputs, labels
    def tf_call(self, examples: List[Union[List[int], Any, Dict[str, Any]]]) -> Dict[str, Any]:
        import tensorflow as tf
        if isinstance(examples[0], Mapping): batch = pad_without_fast_tokenizer_warning(self.tokenizer, examples, return_tensors="tf", pad_to_multiple_of=self.pad_to_multiple_of)
        else: batch = {"input_ids": _tf_collate_batch(examples, self.tokenizer, pad_to_multiple_of=self.pad_to_multiple_of)}
        special_tokens_mask = batch.pop("special_tokens_mask", None)
        if self.mlm:
            if special_tokens_mask is None:
                special_tokens_mask = [self.tokenizer.get_special_tokens_mask(val, already_has_special_tokens=True) for val in batch["input_ids"].numpy().tolist()]
                special_tokens_mask = tf.cast(tf.convert_to_tensor(special_tokens_mask, dtype=tf.int64), tf.bool)
            else: special_tokens_mask = tf.cast(special_tokens_mask, tf.bool)
            batch["input_ids"], batch["labels"] = self.tf_mask_tokens(tf.cast(batch["input_ids"], tf.int64), special_tokens_mask=special_tokens_mask, mask_token_id=self.tokenizer.mask_token_id, vocab_size=len(self.tokenizer))
        else:
            labels = batch["input_ids"]
            if self.tokenizer.pad_token_id is not None: labels = tf.where(labels == self.tokenizer.pad_token_id, -100, labels)
            else: labels = tf.identity(labels)
            batch["labels"] = labels
        return batch
    def torch_call(self, examples: List[Union[List[int], Any, Dict[str, Any]]]) -> Dict[str, Any]:
        if isinstance(examples[0], Mapping): batch = pad_without_fast_tokenizer_warning(self.tokenizer, examples, return_tensors="pt", pad_to_multiple_of=self.pad_to_multiple_of)
        else: batch = {"input_ids": _torch_collate_batch(examples, self.tokenizer, pad_to_multiple_of=self.pad_to_multiple_of)}
        special_tokens_mask = batch.pop("special_tokens_mask", None)
        if self.mlm: batch["input_ids"], batch["labels"] = self.torch_mask_tokens(batch["input_ids"], special_tokens_mask=special_tokens_mask)
        else:
            labels = batch["input_ids"].clone()
            if self.tokenizer.pad_token_id is not None: labels[labels == self.tokenizer.pad_token_id] = -100
            batch["labels"] = labels
        return batch
    def torch_mask_tokens(self, inputs: Any, special_tokens_mask: Optional[Any] = None) -> Tuple[Any, Any]:
        import torch
        labels = inputs.clone()
        probability_matrix = torch.full(labels.shape, self.mlm_probability)
        if special_tokens_mask is None:
            special_tokens_mask = [self.tokenizer.get_special_tokens_mask(val, already_has_special_tokens=True) for val in labels.tolist()]
            special_tokens_mask = torch.tensor(special_tokens_mask, dtype=torch.bool)
        else: special_tokens_mask = special_tokens_mask.bool()
        probability_matrix.masked_fill_(special_tokens_mask, value=0.0)
        masked_indices = torch.bernoulli(probability_matrix).bool()
        labels[~masked_indices] = -100
        indices_replaced = torch.bernoulli(torch.full(labels.shape, 0.8)).bool() & masked_indices
        inputs[indices_replaced] = self.tokenizer.convert_tokens_to_ids(self.tokenizer.mask_token)
        indices_random = torch.bernoulli(torch.full(labels.shape, 0.5)).bool() & masked_indices & ~indices_replaced
        random_words = torch.randint(len(self.tokenizer), labels.shape, dtype=torch.long)
        inputs[indices_random] = random_words[indices_random]
        return inputs, labels
    def numpy_call(self, examples: List[Union[List[int], Any, Dict[str, Any]]]) -> Dict[str, Any]:
        if isinstance(examples[0], Mapping): batch = pad_without_fast_tokenizer_warning(self.tokenizer, examples, return_tensors="np", pad_to_multiple_of=self.pad_to_multiple_of)
        else: batch = {"input_ids": _numpy_collate_batch(examples, self.tokenizer, pad_to_multiple_of=self.pad_to_multiple_of)}
        special_tokens_mask = batch.pop("special_tokens_mask", None)
        if self.mlm: batch["input_ids"], batch["labels"] = self.numpy_mask_tokens(batch["input_ids"], special_tokens_mask=special_tokens_mask)
        else:
            labels = np.copy(batch["input_ids"])
            if self.tokenizer.pad_token_id is not None: labels[labels == self.tokenizer.pad_token_id] = -100
            batch["labels"] = labels
        return batch
    def numpy_mask_tokens(self, inputs: Any, special_tokens_mask: Optional[Any] = None) -> Tuple[Any, Any]:
        labels = np.copy(inputs)
        probability_matrix = np.full(labels.shape, self.mlm_probability)
        if special_tokens_mask is None:
            special_tokens_mask = [self.tokenizer.get_special_tokens_mask(val, already_has_special_tokens=True) for val in labels.tolist()]
            special_tokens_mask = np.array(special_tokens_mask, dtype=bool)
        else: special_tokens_mask = special_tokens_mask.astype(bool)
        probability_matrix[special_tokens_mask] = 0
        masked_indices = np.random.binomial(1, probability_matrix, size=probability_matrix.shape).astype(bool)
        labels[~masked_indices] = -100
        indices_replaced = np.random.binomial(1, 0.8, size=labels.shape).astype(bool) & masked_indices
        inputs[indices_replaced] = self.tokenizer.mask_token_id
        indices_random = (np.random.binomial(1, 0.5, size=labels.shape).astype(bool) & masked_indices & ~indices_replaced)
        random_words = np.random.randint(low=0, high=len(self.tokenizer), size=np.count_nonzero(indices_random), dtype=np.int64)
        inputs[indices_random] = random_words
        return inputs, labels
@dataclass
class DataCollatorForWholeWordMask(DataCollatorForLanguageModeling):
    def torch_call(self, examples: List[Union[List[int], Any, Dict[str, Any]]]) -> Dict[str, Any]:
        if isinstance(examples[0], Mapping): input_ids = [e["input_ids"] for e in examples]
        else:
            input_ids = examples
            examples = [{"input_ids": e} for e in examples]
        batch_input = _torch_collate_batch(input_ids, self.tokenizer, pad_to_multiple_of=self.pad_to_multiple_of)
        mask_labels = []
        for e in examples:
            ref_tokens = []
            for id in tolist(e["input_ids"]):
                token = self.tokenizer._convert_id_to_token(id)
                ref_tokens.append(token)
            if "chinese_ref" in e:
                ref_pos = tolist(e["chinese_ref"])
                len_seq = len(e["input_ids"])
                for i in range(len_seq):
                    if i in ref_pos: ref_tokens[i] = "##" + ref_tokens[i]
            mask_labels.append(self._whole_word_mask(ref_tokens))
        batch_mask = _torch_collate_batch(mask_labels, self.tokenizer, pad_to_multiple_of=self.pad_to_multiple_of)
        inputs, labels = self.torch_mask_tokens(batch_input, batch_mask)
        return {"input_ids": inputs, "labels": labels}
    def tf_call(self, examples: List[Union[List[int], Any, Dict[str, Any]]]) -> Dict[str, Any]:
        import tensorflow as tf
        if isinstance(examples[0], Mapping): input_ids = [e["input_ids"] for e in examples]
        else:
            input_ids = examples
            examples = [{"input_ids": e} for e in examples]
        batch_input = _tf_collate_batch(input_ids, self.tokenizer, pad_to_multiple_of=self.pad_to_multiple_of)
        mask_labels = []
        for e in examples:
            ref_tokens = []
            for id in tolist(e["input_ids"]):
                token = self.tokenizer._convert_id_to_token(id)
                ref_tokens.append(token)
            if "chinese_ref" in e:
                ref_pos = tolist(e["chinese_ref"])
                len_seq = len(e["input_ids"])
                for i in range(len_seq):
                    if i in ref_pos: ref_tokens[i] = "##" + ref_tokens[i]
            mask_labels.append(self._whole_word_mask(ref_tokens))
        batch_mask = _tf_collate_batch(mask_labels, self.tokenizer, pad_to_multiple_of=self.pad_to_multiple_of)
        inputs, labels = self.tf_mask_tokens(tf.cast(batch_input, tf.int64), batch_mask)
        return {"input_ids": inputs, "labels": labels}
    def numpy_call(self, examples: List[Union[List[int], Any, Dict[str, Any]]]) -> Dict[str, Any]:
        if isinstance(examples[0], Mapping): input_ids = [e["input_ids"] for e in examples]
        else:
            input_ids = examples
            examples = [{"input_ids": e} for e in examples]
        batch_input = _numpy_collate_batch(input_ids, self.tokenizer, pad_to_multiple_of=self.pad_to_multiple_of)
        mask_labels = []
        for e in examples:
            ref_tokens = []
            for id in tolist(e["input_ids"]):
                token = self.tokenizer._convert_id_to_token(id)
                ref_tokens.append(token)
            if "chinese_ref" in e:
                ref_pos = tolist(e["chinese_ref"])
                len_seq = len(e["input_ids"])
                for i in range(len_seq):
                    if i in ref_pos: ref_tokens[i] = "##" + ref_tokens[i]
            mask_labels.append(self._whole_word_mask(ref_tokens))
        batch_mask = _numpy_collate_batch(mask_labels, self.tokenizer, pad_to_multiple_of=self.pad_to_multiple_of)
        inputs, labels = self.numpy_mask_tokens(batch_input, batch_mask)
        return {"input_ids": inputs, "labels": labels}
    def _whole_word_mask(self, input_tokens: List[str], max_predictions=512):
        if not isinstance(self.tokenizer, (BertTokenizer, BertTokenizerFast)): warnings.warn("DataCollatorForWholeWordMask is only suitable for BertTokenizer-like tokenizers. Please refer to the documentation for more information.")
        cand_indexes = []
        for i, token in enumerate(input_tokens):
            if token == "[CLS]" or token == "[SEP]": continue
            if len(cand_indexes) >= 1 and token.startswith("##"): cand_indexes[-1].append(i)
            else: cand_indexes.append([i])
        random.shuffle(cand_indexes)
        num_to_predict = min(max_predictions, max(1, int(round(len(input_tokens) * self.mlm_probability))))
        masked_lms = []
        covered_indexes = set()
        for index_set in cand_indexes:
            if len(masked_lms) >= num_to_predict: break
            if len(masked_lms) + len(index_set) > num_to_predict: continue
            is_any_index_covered = False
            for index in index_set:
                if index in covered_indexes:
                    is_any_index_covered = True
                    break
            if is_any_index_covered: continue
            for index in index_set:
                covered_indexes.add(index)
                masked_lms.append(index)
        if len(covered_indexes) != len(masked_lms): raise ValueError("Length of covered_indexes is not equal to length of masked_lms.")
        mask_labels = [1 if i in covered_indexes else 0 for i in range(len(input_tokens))]
        return mask_labels
    def torch_mask_tokens(self, inputs: Any, mask_labels: Any) -> Tuple[Any, Any]:
        import torch
        if self.tokenizer.mask_token is None: raise ValueError("This tokenizer does not have a mask token which is necessary for masked language modeling. Remove the --mlm flag if you want to use this tokenizer.")
        labels = inputs.clone()
        probability_matrix = mask_labels
        special_tokens_mask = [self.tokenizer.get_special_tokens_mask(val, already_has_special_tokens=True) for val in labels.tolist()]
        probability_matrix.masked_fill_(torch.tensor(special_tokens_mask, dtype=torch.bool), value=0.0)
        if self.tokenizer._pad_token is not None:
            padding_mask = labels.eq(self.tokenizer.pad_token_id)
            probability_matrix.masked_fill_(padding_mask, value=0.0)
        masked_indices = probability_matrix.bool()
        labels[~masked_indices] = -100
        indices_replaced = torch.bernoulli(torch.full(labels.shape, 0.8)).bool() & masked_indices
        inputs[indices_replaced] = self.tokenizer.convert_tokens_to_ids(self.tokenizer.mask_token)
        indices_random = torch.bernoulli(torch.full(labels.shape, 0.5)).bool() & masked_indices & ~indices_replaced
        random_words = torch.randint(len(self.tokenizer), labels.shape, dtype=torch.long)
        inputs[indices_random] = random_words[indices_random]
        return inputs, labels
    def tf_mask_tokens(self, inputs: Any, mask_labels: Any) -> Tuple[Any, Any]:
        import tensorflow as tf
        input_shape = tf.shape(inputs)
        if self.tokenizer.mask_token is None: raise ValueError("This tokenizer does not have a mask token which is necessary for masked language modeling. Remove the --mlm flag if you want to use this tokenizer.")
        labels = tf.identity(inputs)
        masked_indices = tf.cast(mask_labels, tf.bool)
        special_tokens_mask = [self.tokenizer.get_special_tokens_mask(val, already_has_special_tokens=True) for val in labels]
        masked_indices = masked_indices & ~tf.cast(special_tokens_mask, dtype=tf.bool)
        if self.tokenizer._pad_token is not None:
            padding_mask = inputs == self.tokenizer.pad_token_id
            masked_indices = masked_indices & ~padding_mask
        labels = tf.where(masked_indices, inputs, -100)
        indices_replaced = self.tf_bernoulli(input_shape, 0.8) & masked_indices
        inputs = tf.where(indices_replaced, self.tokenizer.mask_token_id, inputs)
        indices_random = self.tf_bernoulli(input_shape, 0.5) & masked_indices & ~indices_replaced
        random_words = tf.random.uniform(input_shape, maxval=len(self.tokenizer), dtype=tf.int64)
        inputs = tf.where(indices_random, random_words, inputs)
        return inputs, labels
    def numpy_mask_tokens(self, inputs: Any, mask_labels: Any) -> Tuple[Any, Any]:
        if self.tokenizer.mask_token is None: raise ValueError("This tokenizer does not have a mask token which is necessary for masked language modeling. Remove the --mlm flag if you want to use this tokenizer.")
        labels = np.copy(inputs)
        masked_indices = mask_labels.astype(bool)
        special_tokens_mask = [self.tokenizer.get_special_tokens_mask(val, already_has_special_tokens=True) for val in labels.tolist()]
        masked_indices[np.array(special_tokens_mask, dtype=bool)] = 0
        if self.tokenizer._pad_token is not None:
            padding_mask = labels == self.tokenizer.pad_token_id
            masked_indices[padding_mask] = 0
        labels[~masked_indices] = -100
        indices_replaced = np.random.binomial(1, 0.8, size=labels.shape).astype(bool) & masked_indices
        inputs[indices_replaced] = self.tokenizer.convert_tokens_to_ids(self.tokenizer.mask_token)
        indices_random = (np.random.binomial(1, 0.5, size=labels.shape).astype(bool) & masked_indices & ~indices_replaced)
        random_words = np.random.randint(low=0, high=len(self.tokenizer), size=labels.shape, dtype=np.int64)
        inputs[indices_random] = random_words[indices_random]
        return inputs, labels
@dataclass
class DataCollatorForSOP(DataCollatorForLanguageModeling):
    def __init__(self, *args, **kwargs): warnings.warn("DataCollatorForSOP is deprecated and will be removed in a future version, you can now use DataCollatorForLanguageModeling instead.", FutureWarning)
    def __call__(self, examples: List[Dict[str, Any]]) -> Dict[str, Any]:
        import torch
        from torch.nn.utils.rnn import pad_sequence
        input_ids = [example["input_ids"] for example in examples]
        input_ids = _torch_collate_batch(input_ids, self.tokenizer)
        input_ids, labels, attention_mask = self.mask_tokens(input_ids)
        token_type_ids = [example["token_type_ids"] for example in examples]
        token_type_ids = pad_sequence(token_type_ids, batch_first=True, padding_value=self.tokenizer.pad_token_id)
        sop_label_list = [example["sentence_order_label"] for example in examples]
        sentence_order_label = torch.stack(sop_label_list)
        return {"input_ids": input_ids, "labels": labels, "attention_mask": attention_mask, "token_type_ids": token_type_ids, "sentence_order_label": sentence_order_label}
    def mask_tokens(self, inputs: Any) -> Tuple[Any, Any, Any]:
        import torch
        if self.tokenizer.mask_token is None: raise ValueError("This tokenizer does not have a mask token which is necessary for masked language modeling. Remove the --mlm flag if you want to use this tokenizer.")
        labels = inputs.clone()
        probability_matrix = torch.full(labels.shape, self.mlm_probability)
        special_tokens_mask = [self.tokenizer.get_special_tokens_mask(val, already_has_special_tokens=True) for val in labels.tolist()]
        probability_matrix.masked_fill_(torch.tensor(special_tokens_mask, dtype=torch.bool), value=0.0)
        if self.tokenizer._pad_token is not None:
            padding_mask = labels.eq(self.tokenizer.pad_token_id)
            probability_matrix.masked_fill_(padding_mask, value=0.0)
        masked_indices = torch.bernoulli(probability_matrix).bool()
        attention_mask = (~masked_indices).float()
        if self.tokenizer._pad_token is not None:
            attention_padding_mask = labels.eq(self.tokenizer.pad_token_id)
            attention_mask.masked_fill_(attention_padding_mask, value=1.0)
        labels[~masked_indices] = -100
        indices_replaced = torch.bernoulli(torch.full(labels.shape, 0.8)).bool() & masked_indices
        inputs[indices_replaced] = self.tokenizer.convert_tokens_to_ids(self.tokenizer.mask_token)
        indices_random = torch.bernoulli(torch.full(labels.shape, 0.5)).bool() & masked_indices & ~indices_replaced
        random_words = torch.randint(len(self.tokenizer), labels.shape, dtype=torch.long)
        inputs[indices_random] = random_words[indices_random]
        return inputs, labels, attention_mask
@dataclass
class DataCollatorForPermutationLanguageModeling(DataCollatorMixin):
    tokenizer: PreTrainedTokenizerBase
    plm_probability: float = 1 / 6
    max_span_length: int = 5
    return_tensors: str = "pt"
    def torch_call(self, examples: List[Union[List[int], Any, Dict[str, Any]]]) -> Dict[str, Any]:
        if isinstance(examples[0], Mapping): examples = [e["input_ids"] for e in examples]
        batch = _torch_collate_batch(examples, self.tokenizer)
        inputs, perm_mask, target_mapping, labels = self.torch_mask_tokens(batch)
        return {"input_ids": inputs, "perm_mask": perm_mask, "target_mapping": target_mapping, "labels": labels}
    def tf_call(self, examples: List[Union[List[int], Any, Dict[str, Any]]]) -> Dict[str, Any]:
        if isinstance(examples[0], Mapping): examples = [e["input_ids"] for e in examples]
        batch = _tf_collate_batch(examples, self.tokenizer)
        inputs, perm_mask, target_mapping, labels = self.tf_mask_tokens(batch)
        return {"input_ids": inputs, "perm_mask": perm_mask, "target_mapping": target_mapping, "labels": labels}
    def numpy_call(self, examples: List[Union[List[int], Any, Dict[str, Any]]]) -> Dict[str, Any]:
        if isinstance(examples[0], Mapping): examples = [e["input_ids"] for e in examples]
        batch = _numpy_collate_batch(examples, self.tokenizer)
        inputs, perm_mask, target_mapping, labels = self.numpy_mask_tokens(batch)
        return {"input_ids": inputs, "perm_mask": perm_mask, "target_mapping": target_mapping, "labels": labels}
    def torch_mask_tokens(self, inputs: Any) -> Tuple[Any, Any, Any, Any]:
        import torch
        if self.tokenizer.mask_token is None: raise ValueError("This tokenizer does not have a mask token which is necessary for permutation language modeling. Please add a mask token if you want to use this tokenizer.")
        if inputs.size(1) % 2 != 0: raise ValueError("This collator requires that sequence lengths be even to create a leakage-free perm_mask. Please see relevant comments in source code for details.")
        labels = inputs.clone()
        masked_indices = torch.full(labels.shape, 0, dtype=torch.bool)
        target_mapping = torch.zeros((labels.size(0), labels.size(1), labels.size(1)), dtype=torch.float32)
        for i in range(labels.size(0)):
            cur_len = 0
            max_len = labels.size(1)
            while cur_len < max_len:
                span_length = torch.randint(1, self.max_span_length + 1, (1,)).item()
                context_length = int(span_length / self.plm_probability)
                start_index = cur_len + torch.randint(context_length - span_length + 1, (1,)).item()
                masked_indices[i, start_index : start_index + span_length] = 1
                cur_len += context_length
            target_mapping[i] = torch.eye(labels.size(1))
        special_tokens_mask = torch.tensor([self.tokenizer.get_special_tokens_mask(val, already_has_special_tokens=True) for val in labels.tolist()], dtype=torch.bool)
        masked_indices.masked_fill_(special_tokens_mask, value=0.0)
        if self.tokenizer._pad_token is not None:
            padding_mask = labels.eq(self.tokenizer.pad_token_id)
            masked_indices.masked_fill_(padding_mask, value=0.0)
        non_func_mask = ~(padding_mask | special_tokens_mask)
        inputs[masked_indices] = self.tokenizer.mask_token_id
        labels[~masked_indices] = -100
        perm_mask = torch.zeros((labels.size(0), labels.size(1), labels.size(1)), dtype=torch.float32)
        for i in range(labels.size(0)):
            perm_index = torch.arange(labels.size(1))
            perm_index = perm_index.reshape((-1, labels.size(1) // 2)).transpose(0, 1)
            perm_index = perm_index[torch.randperm(labels.size(1) // 2)]
            perm_index = torch.flatten(perm_index.transpose(0, 1))
            perm_index.masked_fill_(~masked_indices[i] & non_func_mask[i], -1)
            perm_mask[i] = (perm_index.reshape((labels.size(1), 1)) <= perm_index.reshape((1, labels.size(1)))) & masked_indices[i]
        return inputs.long(), perm_mask, target_mapping, labels.long()
    def tf_mask_tokens(self, inputs: Any) -> Tuple[Any, Any, Any, Any]:
        import tensorflow as tf
        if self.tokenizer.mask_token is None: raise ValueError("This tokenizer does not have a mask token which is necessary for permutation language modeling. Please add a mask token if you want to use this tokenizer.")
        if tf.shape(inputs)[1] % 2 != 0: raise ValueError("This collator requires that sequence lengths be even to create a leakage-free perm_mask. Please see relevant comments in source code for details.")
        labels = tf.identity(inputs)
        masked_indices = np.full(labels.shape.as_list(), 0, dtype=bool)
        labels_shape = tf.shape(labels)
        target_mapping = np.zeros((labels_shape[0], labels_shape[1], labels_shape[1]), dtype=np.float32)
        for i in range(len(labels)):
            cur_len = 0
            max_len = tf.shape(labels)[1]
            while cur_len < max_len:
                span_length = randint(1, self.max_span_length + 1)
                context_length = int(span_length / self.plm_probability)
                start_index = cur_len + randint(0, context_length - span_length + 1)
                masked_indices[i, start_index : start_index + span_length] = 1
                cur_len += context_length
            target_mapping[i] = np.eye(labels_shape[1])
        masked_indices = tf.cast(tf.convert_to_tensor(masked_indices), dtype=tf.bool)
        target_mapping = tf.convert_to_tensor(target_mapping)
        special_tokens_mask = tf.convert_to_tensor([self.tokenizer.get_special_tokens_mask(val, already_has_special_tokens=True) for val in labels.numpy().tolist()])
        special_tokens_mask = tf.cast(special_tokens_mask, dtype=tf.bool)
        masked_indices = masked_indices & ~special_tokens_mask
        if self.tokenizer._pad_token is not None:
            padding_mask = labels == self.tokenizer.pad_token_id
            masked_indices = masked_indices & ~padding_mask
        non_func_mask = ~(padding_mask | special_tokens_mask)
        inputs = tf.where(masked_indices, self.tokenizer.mask_token_id, inputs)
        labels = tf.where(masked_indices, labels, -100)
        perm_mask = []
        for i in range(len(labels)):
            perm_index = tf.range(labels_shape[1])
            perm_index = tf.transpose(tf.reshape(perm_index, (-1, labels_shape[1] // 2)))
            perm_index = tf.random.shuffle(perm_index)
            perm_index = tf.reshape(tf.transpose(perm_index), (-1,))
            perm_index = tf.where(~masked_indices[i] & non_func_mask[i], -1, perm_index)
            perm_mask.append((tf.reshape(perm_index, (labels_shape[1], 1)) <= tf.reshape(perm_index, (1, labels_shape[1]))) & masked_indices[i])
        perm_mask = tf.stack(perm_mask, axis=0)
        return tf.cast(inputs, tf.int64), tf.cast(perm_mask, tf.float32), target_mapping, tf.cast(labels, tf.int64)
    def numpy_mask_tokens(self, inputs: Any) -> Tuple[Any, Any, Any, Any]:
        if self.tokenizer.mask_token is None: raise ValueError("This tokenizer does not have a mask token which is necessary for permutation language modeling. Please add a mask token if you want to use this tokenizer.")
        if inputs.shape[1] % 2 != 0: raise ValueError("This collator requires that sequence lengths be even to create a leakage-free perm_mask. Please see relevant comments in source code for details.")
        labels = np.copy(inputs)
        masked_indices = np.full(labels.shape, 0, dtype=bool)
        target_mapping = np.zeros((labels.shape[0], labels.shape[1], labels.shape[1]), dtype=np.float32)
        for i in range(labels.shape[0]):
            cur_len = 0
            max_len = labels.shape[1]
            while cur_len < max_len:
                span_length = randint(1, self.max_span_length + 1)
                context_length = int(span_length / self.plm_probability)
                start_index = cur_len + randint(0, context_length - span_length + 1)
                masked_indices[i, start_index : start_index + span_length] = 1
                cur_len += context_length
            target_mapping[i] = np.eye(labels.shape[1])
        special_tokens_mask = np.array([self.tokenizer.get_special_tokens_mask(val, already_has_special_tokens=True) for val in labels.tolist()], dtype=bool)
        masked_indices[special_tokens_mask] = 0
        if self.tokenizer._pad_token is not None:
            padding_mask = labels == self.tokenizer.pad_token_id
            masked_indices[padding_mask] = 0.0
        non_func_mask = ~(padding_mask | special_tokens_mask)
        inputs[masked_indices] = self.tokenizer.mask_token_id
        labels[~masked_indices] = -100
        perm_mask = np.zeros((labels.shape[0], labels.shape[1], labels.shape[1]), dtype=np.float32)
        for i in range(labels.shape[0]):
            perm_index = np.arange(labels.shape[1])
            perm_index = perm_index.reshape((-1, labels.shape[1] // 2)).T
            np.random.shuffle(perm_index)
            perm_index = perm_index.T.flatten()
            perm_index[~masked_indices[i] & non_func_mask[i]] = -1
            perm_mask[i] = (perm_index.reshape((labels.shape[1], 1)) <= perm_index.reshape((1, labels.shape[1]))) & masked_indices[i]
        return inputs.astype(np.int64), perm_mask, target_mapping, labels.astype(np.int64)
@dataclass
class DataCollatorWithFlattening(DefaultDataCollator):
    def __init__(self, *args, return_position_ids=True, separator_id=-100, **kwargs):
        super().__init__(*args, **kwargs)
        self.return_position_ids = return_position_ids
        self.separator_id = separator_id
        warnings.warn("Using `DataCollatorWithFlattening` will flatten the entire mini batch into single long sequence. Make sure your attention computation is able to handle it!")
    def __call__(self, features, return_tensors=None, separator_id=None):
        if return_tensors is None: return_tensors = self.return_tensors
        if separator_id is None: separator_id = self.separator_id
        is_labels_provided = "labels" in features[0]
        ret = {"input_ids": [], "labels": []}
        if self.return_position_ids: ret.update({"position_ids": []})
        for idx in range(0, len(features)):
            ret["input_ids"] += features[idx]["input_ids"]
            if is_labels_provided: ret["labels"] += [separator_id] + features[idx]["labels"][1:]
            else: ret["labels"] += [separator_id] + features[idx]["input_ids"][1:]
            if self.return_position_ids: ret["position_ids"] += list(range(len(features[idx]["input_ids"])))
        return default_data_collator([ret], return_tensors)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
