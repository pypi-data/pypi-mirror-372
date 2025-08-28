"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from .utils import (is_sagemaker_mp_enabled, is_torch_available, is_torch_xla_available, is_training_run_on_sagemaker, logging)
from torch.utils.data import Dataset, IterableDataset, RandomSampler, Sampler
from .integrations.deepspeed import is_deepspeed_zero3_enabled
from typing import Any, Dict, Iterator, List, Optional, Union
from torch.utils.data.distributed import DistributedSampler
from .tokenization_utils_base import BatchEncoding
from dataclasses import dataclass, field
from contextlib import contextmanager
from collections.abc import Mapping
from logging import StreamHandler
import torch.distributed as dist
from itertools import chain
from torch import nn
import numpy as np
import warnings
import datetime
import torch
import json
import math
import copy
import sys
import io
import os
if is_training_run_on_sagemaker(): logging.add_handler(StreamHandler(sys.stdout))
if is_torch_xla_available(): import torch_xla.core.xla_model as xm
if is_torch_available():
    from .pytorch_utils import is_torch_greater_or_equal_than_2_0
    if is_torch_greater_or_equal_than_2_0: from torch.optim.lr_scheduler import LRScheduler
    else: from torch.optim.lr_scheduler import _LRScheduler as LRScheduler
logger = logging.get_logger(__name__)
def get_dataloader_sampler(dataloader):
    if hasattr(dataloader, "batch_sampler") and dataloader.batch_sampler is not None: return get_dataloader_sampler(dataloader.batch_sampler)
    elif hasattr(dataloader, "sampler"): return dataloader.sampler
def atleast_1d(tensor_or_array: Union[torch.Tensor, np.ndarray]):
    if isinstance(tensor_or_array, torch.Tensor):
        if hasattr(torch, "atleast_1d"): tensor_or_array = torch.atleast_1d(tensor_or_array)
        elif tensor_or_array.ndim < 1: tensor_or_array = tensor_or_array[None]
    else: tensor_or_array = np.atleast_1d(tensor_or_array)
    return tensor_or_array
def torch_pad_and_concatenate(tensor1, tensor2, padding_index=-100):
    tensor1 = atleast_1d(tensor1)
    tensor2 = atleast_1d(tensor2)
    if len(tensor1.shape) == 1 or tensor1.shape[1] == tensor2.shape[1]: return torch.cat((tensor1, tensor2), dim=0)
    new_shape = (tensor1.shape[0] + tensor2.shape[0], max(tensor1.shape[1], tensor2.shape[1])) + tensor1.shape[2:]
    result = tensor1.new_full(new_shape, padding_index)
    result[: tensor1.shape[0], : tensor1.shape[1]] = tensor1
    result[tensor1.shape[0] :, : tensor2.shape[1]] = tensor2
    return result
def numpy_pad_and_concatenate(array1, array2, padding_index=-100):
    array1 = atleast_1d(array1)
    array2 = atleast_1d(array2)
    if len(array1.shape) == 1 or array1.shape[1] == array2.shape[1]: return np.concatenate((array1, array2), axis=0)
    new_shape = (array1.shape[0] + array2.shape[0], max(array1.shape[1], array2.shape[1])) + array1.shape[2:]
    result = np.full_like(array1, padding_index, shape=new_shape)
    result[: array1.shape[0], : array1.shape[1]] = array1
    result[array1.shape[0] :, : array2.shape[1]] = array2
    return result
def nested_concat(tensors, new_tensors, padding_index=-100):
    if not (isinstance(tensors, torch.Tensor) and isinstance(new_tensors, torch.Tensor)): assert (type(tensors) is type(new_tensors)), f"Expected `tensors` and `new_tensors` to have the same type but found {type(tensors)} and {type(new_tensors)}."
    if isinstance(tensors, (list, tuple)): return type(tensors)(nested_concat(t, n, padding_index=padding_index) for t, n in zip(tensors, new_tensors))
    elif isinstance(tensors, torch.Tensor): return torch_pad_and_concatenate(tensors, new_tensors, padding_index=padding_index)
    elif isinstance(tensors, Mapping): return type(tensors)({k: nested_concat(t, new_tensors[k], padding_index=padding_index) for k, t in tensors.items()})
    elif isinstance(tensors, np.ndarray): return numpy_pad_and_concatenate(tensors, new_tensors, padding_index=padding_index)
    else: raise TypeError(f"Unsupported type for concatenation: got {type(tensors)}")
def find_batch_size(tensors):
    if isinstance(tensors, (list, tuple)):
        for t in tensors:
            result = find_batch_size(t)
            if result is not None: return result
    elif isinstance(tensors, Mapping):
        for key, value in tensors.items():
            result = find_batch_size(value)
            if result is not None: return result
    elif isinstance(tensors, torch.Tensor): return tensors.shape[0] if len(tensors.shape) >= 1 else None
    elif isinstance(tensors, np.ndarray): return tensors.shape[0] if len(tensors.shape) >= 1 else None
def nested_numpify(tensors):
    if isinstance(tensors, (list, tuple)): return type(tensors)(nested_numpify(t) for t in tensors)
    if isinstance(tensors, Mapping): return type(tensors)({k: nested_numpify(t) for k, t in tensors.items()})
    t = tensors.cpu()
    if t.dtype == torch.bfloat16: t = t.to(torch.float32)
    return t.numpy()
def nested_detach(tensors):
    if isinstance(tensors, (list, tuple)): return type(tensors)(nested_detach(t) for t in tensors)
    elif isinstance(tensors, Mapping): return type(tensors)({k: nested_detach(t) for k, t in tensors.items()})
    return tensors.detach() if isinstance(tensors, torch.Tensor) else tensors
def nested_xla_mesh_reduce(tensors, name):
    if is_torch_xla_available():
        import torch_xla.core.xla_model as xm
        if isinstance(tensors, (list, tuple)): return type(tensors)(nested_xla_mesh_reduce(t, f"{name}_{i}") for i, t in enumerate(tensors))
        if isinstance(tensors, Mapping): return type(tensors)({k: nested_xla_mesh_reduce(t, f"{name}_{i}") for i, (k, t) in enumerate(tensors.items())})
        tensors = atleast_1d(tensors)
        return xm.mesh_reduce(name, tensors, torch.cat)
    else: raise ImportError("Torch xla must be installed to use `nested_xla_mesh_reduce`")
def distributed_concat(tensor: Any, num_total_examples: Optional[int] = None) -> Any:
    try:
        if isinstance(tensor, (tuple, list)): return type(tensor)(distributed_concat(t, num_total_examples) for t in tensor)
        if isinstance(tensor, Mapping): return type(tensor)({k: distributed_concat(t, num_total_examples) for k, t in tensor.items()})
        tensor = atleast_1d(tensor).contiguous()
        output_tensors = [tensor.clone() for _ in range(dist.get_world_size())]
        dist.all_gather(output_tensors, tensor)
        concat = torch.cat(output_tensors, dim=0)
        if num_total_examples is not None: concat = concat[:num_total_examples]
        return concat
    except AssertionError: raise AssertionError("Not currently using distributed training")
def distributed_broadcast_scalars(scalars: List[Union[int, float]], num_total_examples: Optional[int] = None, device: Optional[torch.device] = torch.device("cuda")) -> torch.Tensor:
    try:
        tensorized_scalar = torch.tensor(scalars).to(device)
        output_tensors = [tensorized_scalar.clone() for _ in range(dist.get_world_size())]
        dist.all_gather(output_tensors, tensorized_scalar)
        concat = torch.cat(output_tensors, dim=0)
        if num_total_examples is not None: concat = concat[:num_total_examples]
        return concat
    except AssertionError: raise AssertionError("Not currently using distributed training")
def reissue_pt_warnings(caught_warnings):
    if len(caught_warnings) > 1:
        for w in caught_warnings:
            if w.category is not UserWarning: warnings.warn(w.message, w.category)
@contextmanager
def torch_distributed_zero_first(local_rank: int):
    if local_rank not in [-1, 0]: dist.barrier()
    yield
    if local_rank == 0: dist.barrier()
class DistributedSamplerWithLoop(DistributedSampler):
    def __init__(self, dataset, batch_size, **kwargs):
        super().__init__(dataset, **kwargs)
        self.batch_size = batch_size
    def __iter__(self):
        indices = list(super().__iter__())
        remainder = 0 if len(indices) % self.batch_size == 0 else self.batch_size - len(indices) % self.batch_size
        start_remainder = 1 if self.rank < len(self.dataset) % self.num_replicas else 0
        indices += indices[start_remainder : start_remainder + remainder]
        return iter(indices)
class EvalLoopContainer:
    def __init__(self, do_nested_concat: bool = True, padding_index: int = -100):
        self.do_nested_concat = do_nested_concat
        self.padding_index = padding_index
        self.tensors = None
        self.arrays = None
    def add(self, tensors) -> None:
        if self.tensors is None: self.tensors = tensors if self.do_nested_concat else [tensors]
        elif self.do_nested_concat: self.tensors = nested_concat(self.tensors, tensors, padding_index=self.padding_index)
        else: self.tensors.append(tensors)
    def to_cpu_and_numpy(self) -> None:
        if self.tensors is None: return
        new_arrays = nested_numpify(self.tensors)
        if self.arrays is None: self.arrays = new_arrays
        elif self.do_nested_concat: self.arrays = nested_concat(self.arrays, new_arrays, padding_index=self.padding_index)
        else: self.arrays.extend(new_arrays)
        self.tensors = None
    def get_arrays(self):
        self.to_cpu_and_numpy()
        return self.arrays
class SequentialDistributedSampler(Sampler):
    def __init__(self, dataset, num_replicas=None, rank=None, batch_size=None):
        if num_replicas is None:
            if not dist.is_available(): raise RuntimeError("Requires distributed package to be available")
            num_replicas = dist.get_world_size()
        if rank is None:
            if not dist.is_available(): raise RuntimeError("Requires distributed package to be available")
            rank = dist.get_rank()
        self.dataset = dataset
        self.num_replicas = num_replicas
        self.rank = rank
        num_samples = len(self.dataset)
        if batch_size is not None: self.num_samples = int(math.ceil(num_samples / (batch_size * num_replicas))) * batch_size
        else: self.num_samples = int(math.ceil(num_samples / num_replicas))
        self.total_size = self.num_samples * self.num_replicas
        self.batch_size = batch_size
    def __iter__(self):
        indices = list(range(len(self.dataset)))
        indices += indices[: (self.total_size - len(indices))]
        assert (len(indices) == self.total_size), f"Indices length {len(indices)} and total size {self.total_size} mismatched"
        indices = indices[self.rank * self.num_samples : (self.rank + 1) * self.num_samples]
        assert (len(indices) == self.num_samples), f"Indices length {len(indices)} and sample number {self.num_samples} mismatched"
        return iter(indices)
    def __len__(self): return self.num_samples
def get_tpu_sampler(dataset: torch.utils.data.Dataset, batch_size: int):
    if xm.xrt_world_size() <= 1: return RandomSampler(dataset)
    return DistributedSampler(dataset, num_replicas=xm.xrt_world_size(), rank=xm.get_ordinal())
def nested_new_like(arrays, num_samples, padding_index=-100):
    if isinstance(arrays, (list, tuple)): return type(arrays)(nested_new_like(x, num_samples) for x in arrays)
    return np.full_like(arrays, padding_index, shape=(num_samples, *arrays.shape[1:]))
def expand_like(arrays, new_seq_length, padding_index=-100):
    result = np.full_like(arrays, padding_index, shape=(arrays.shape[0], new_seq_length) + arrays.shape[2:])
    result[:, : arrays.shape[1]] = arrays
    return result
def nested_truncate(tensors, limit):
    if isinstance(tensors, (list, tuple)): return type(tensors)(nested_truncate(t, limit) for t in tensors)
    if isinstance(tensors, Mapping): return type(tensors)({k: nested_truncate(t, limit) for k, t in tensors.items()})
    return tensors[:limit]
class DistributedTensorGatherer:
    def __init__(self, world_size, num_samples, make_multiple_of=None, padding_index=-100):
        self.world_size = world_size
        self.num_samples = num_samples
        total_size = world_size if make_multiple_of is None else world_size * make_multiple_of
        self.total_samples = int(np.ceil(num_samples / total_size)) * total_size
        self.process_length = self.total_samples // world_size
        self._storage = None
        self._offsets = None
        self.padding_index = padding_index
    def add_arrays(self, arrays):
        if arrays is None: return
        if self._storage is None:
            self._storage = nested_new_like(arrays, self.total_samples, padding_index=self.padding_index)
            self._offsets = list(range(0, self.total_samples, self.process_length))
        slice_len, self._storage = self._nested_set_tensors(self._storage, arrays)
        for i in range(self.world_size): self._offsets[i] += slice_len
    def _nested_set_tensors(self, storage, arrays):
        if isinstance(arrays, (list, tuple)):
            result = [self._nested_set_tensors(x, y) for x, y in zip(storage, arrays)]
            return result[0][0], type(arrays)(r[1] for r in result)
        assert (arrays.shape[0] % self.world_size == 0), f"Arrays passed should all have a first dimension multiple of {self.world_size}, found {arrays.shape[0]}."
        slice_len = arrays.shape[0] // self.world_size
        for i in range(self.world_size):
            if len(arrays.shape) == 1: storage[self._offsets[i] : self._offsets[i] + slice_len] = arrays[i * slice_len : (i + 1) * slice_len]
            else:
                if len(storage.shape) > 1 and storage.shape[1] < arrays.shape[1]: storage = expand_like(storage, arrays.shape[1], padding_index=self.padding_index)
                storage[self._offsets[i] : self._offsets[i] + slice_len, : arrays.shape[1]] = arrays[i * slice_len : (i + 1) * slice_len]
        return slice_len, storage
    def finalize(self):
        if self._storage is None: return
        if self._offsets[0] != self.process_length: logger.warning("Not all data has been set. Are you sure you passed all values?")
        return nested_truncate(self._storage, self.num_samples)
@dataclass
class LabelSmoother:
    epsilon: float = 0.1
    ignore_index: int = -100
    def __call__(self, model_output, labels, shift_labels=False):
        logits = model_output["logits"] if isinstance(model_output, dict) else model_output[0]
        if shift_labels:
            logits = logits[..., :-1, :].contiguous()
            labels = labels[..., 1:].contiguous()
        log_probs = -nn.functional.log_softmax(logits, dim=-1)
        if labels.dim() == log_probs.dim() - 1: labels = labels.unsqueeze(-1)
        padding_mask = labels.eq(self.ignore_index)
        labels = torch.clamp(labels, min=0)
        nll_loss = log_probs.gather(dim=-1, index=labels)
        smoothed_loss = log_probs.sum(dim=-1, keepdim=True, dtype=torch.float32)
        nll_loss.masked_fill_(padding_mask, 0.0)
        smoothed_loss.masked_fill_(padding_mask, 0.0)
        num_active_elements = padding_mask.numel() - padding_mask.long().sum()
        nll_loss = nll_loss.sum() / num_active_elements
        smoothed_loss = smoothed_loss.sum() / (num_active_elements * log_probs.shape[-1])
        return (1 - self.epsilon) * nll_loss + self.epsilon * smoothed_loss
def get_length_grouped_indices(lengths, batch_size, mega_batch_mult=None, generator=None):
    if mega_batch_mult is None:
        mega_batch_mult = min(len(lengths) // (batch_size * 4), 50)
        if mega_batch_mult == 0: mega_batch_mult = 1
    indices = torch.randperm(len(lengths), generator=generator)
    megabatch_size = mega_batch_mult * batch_size
    megabatches = [indices[i : i + megabatch_size].tolist() for i in range(0, len(lengths), megabatch_size)]
    megabatches = [sorted(megabatch, key=lambda i: lengths[i], reverse=True) for megabatch in megabatches]
    megabatch_maximums = [lengths[megabatch[0]] for megabatch in megabatches]
    max_idx = torch.argmax(torch.tensor(megabatch_maximums)).item()
    megabatches[0][0], megabatches[max_idx][0] = megabatches[max_idx][0], megabatches[0][0]
    return [i for megabatch in megabatches for i in megabatch]
class LengthGroupedSampler(Sampler):
    def __init__(self, batch_size: int, dataset: Optional[Dataset] = None, lengths: Optional[List[int]] = None, model_input_name: Optional[str] = None, generator=None):
        if dataset is None and lengths is None: raise ValueError("One of dataset and lengths must be provided.")
        self.batch_size = batch_size
        if lengths is None:
            model_input_name = model_input_name if model_input_name is not None else "input_ids"
            if (not (isinstance(dataset[0], dict) or isinstance(dataset[0], BatchEncoding)) or model_input_name not in dataset[0]): raise ValueError(f"Can only automatically infer lengths for datasets whose items are dictionaries with an '{model_input_name}' key.")
            lengths = [len(feature[model_input_name]) for feature in dataset]
        elif isinstance(lengths, torch.Tensor):
            logger.info("If lengths is a torch.Tensor, LengthGroupedSampler will be slow. Converting lengths to List[int]...")
            lengths = lengths.tolist()
        self.lengths = lengths
        self.generator = generator
    def __len__(self): return len(self.lengths)
    def __iter__(self):
        indices = get_length_grouped_indices(self.lengths, self.batch_size, generator=self.generator)
        return iter(indices)
class DistributedLengthGroupedSampler(DistributedSampler):
    def __init__(self, batch_size: int, dataset: Optional[Dataset] = None, num_replicas: Optional[int] = None, rank: Optional[int] = None, seed: int = 0, drop_last: bool = False, lengths: Optional[List[int]] = None, model_input_name: Optional[str] = None):
        if dataset is None and lengths is None: raise ValueError("One of dataset and lengths must be provided.")
        if num_replicas is None:
            if not dist.is_available(): raise RuntimeError("Requires distributed package to be available")
            num_replicas = dist.get_world_size()
        if rank is None:
            if not dist.is_available(): raise RuntimeError("Requires distributed package to be available")
            rank = dist.get_rank()
        self.batch_size = batch_size
        self.num_replicas = num_replicas
        self.rank = rank
        self.epoch = 0
        self.drop_last = drop_last
        if lengths is None:
            model_input_name = model_input_name if model_input_name is not None else "input_ids"
            if (not (isinstance(dataset[0], dict) or isinstance(dataset[0], BatchEncoding)) or model_input_name not in dataset[0]): raise ValueError(f"Can only automatically infer lengths for datasets whose items are dictionaries with an '{model_input_name}' key.")
            lengths = [len(feature[model_input_name]) for feature in dataset]
        elif isinstance(lengths, torch.Tensor):
            logger.info("If lengths is a torch.Tensor, DistributedLengthGroupedSampler will be slow. Converting lengths to List[int]...")
            lengths = lengths.tolist()
        self.lengths = lengths
        if self.drop_last and len(self.lengths) % self.num_replicas != 0: self.num_samples = math.ceil((len(self.lengths) - self.num_replicas) / self.num_replicas)
        else: self.num_samples = math.ceil(len(self.lengths) / self.num_replicas)
        self.total_size = self.num_samples * self.num_replicas
        self.seed = seed
    def __iter__(self) -> Iterator:
        g = torch.Generator()
        g.manual_seed(self.seed + self.epoch)
        indices = get_length_grouped_indices(self.lengths, self.batch_size, generator=g)
        if not self.drop_last: indices += indices[: (self.total_size - len(indices))]
        else: indices = indices[: self.total_size]
        assert len(indices) == self.total_size
        indices = indices[self.rank : self.total_size : self.num_replicas]
        assert len(indices) == self.num_samples
        return iter(indices)
class ShardSampler(Sampler):
    def __init__(self, dataset: Dataset, batch_size: int = 1, drop_last: bool = False, num_processes: int = 1, process_index: int = 0):
        self.dataset = dataset
        self.batch_size = batch_size
        self.drop_last = drop_last
        self.num_processes = num_processes
        self.process_index = process_index
        self.total_batch_size = total_batch_size = batch_size * num_processes
        num_batches = len(dataset) // total_batch_size if drop_last else math.ceil(len(dataset) / total_batch_size)
        self.total_num_samples = num_batches * total_batch_size
    def __iter__(self):
        indices = list(range(len(self.dataset)))
        while len(indices) < self.total_num_samples: indices += indices[: (self.total_num_samples - len(indices))]
        result = []
        for batch_start in range(self.batch_size * self.process_index, self.total_num_samples, self.total_batch_size): result += indices[batch_start : batch_start + self.batch_size]
        return iter(result)
    def __len__(self): return self.total_num_samples // self.num_processes
class IterableDatasetShard(IterableDataset):
    def __init__(self, dataset: IterableDataset, batch_size: int = 1, drop_last: bool = False, num_processes: int = 1, process_index: int = 0, seed: int = 0):
        self.dataset = dataset
        self.batch_size = batch_size
        self.drop_last = drop_last
        self.num_processes = num_processes
        self.process_index = process_index
        self.seed = seed
        self.epoch = 0
        self.num_examples = 0
    def set_epoch(self, epoch):
        self.epoch = epoch
        if hasattr(self.dataset, "set_epoch"): self.dataset.set_epoch(epoch)
    def __iter__(self):
        self.num_examples = 0
        if (not hasattr(self.dataset, "set_epoch") and hasattr(self.dataset, "generator") and isinstance(self.dataset.generator, torch.Generator)): self.dataset.generator.manual_seed(self.seed + self.epoch)
        real_batch_size = self.batch_size * self.num_processes
        process_slice = range(self.process_index * self.batch_size, (self.process_index + 1) * self.batch_size)
        first_batch = None
        current_batch = []
        for element in self.dataset:
            self.num_examples += 1
            current_batch.append(element)
            if len(current_batch) == real_batch_size:
                for i in process_slice: yield current_batch[i]
                if first_batch is None: first_batch = current_batch.copy()
                current_batch = []
        if not self.drop_last and len(current_batch) > 0:
            if first_batch is None: first_batch = current_batch.copy()
            while len(current_batch) < real_batch_size: current_batch += first_batch
            for i in process_slice: yield current_batch[i]
    def __len__(self):
        if self.drop_last: return (len(self.dataset) // (self.batch_size * self.num_processes)) * self.batch_size
        else: return math.ceil(len(self.dataset) / (self.batch_size * self.num_processes)) * self.batch_size
def _get_learning_rate(self):
    if self.is_deepspeed_enabled:
        try: last_lr = self.lr_scheduler.get_last_lr()[0]
        except AssertionError as e:
            if "need to call step" in str(e):
                logger.warning("tried to get lr value before scheduler/optimizer started stepping, returning lr=0")
                last_lr = 0
            else: raise
    else:
        if isinstance(self.lr_scheduler, torch.optim.lr_scheduler.ReduceLROnPlateau): last_lr = self.optimizer.param_groups[0]["lr"]
        else: last_lr = self.lr_scheduler.get_last_lr()[0]
        if torch.is_tensor(last_lr): last_lr = last_lr.item()
    return last_lr
def _secs2timedelta(secs):
    msec = int(abs(secs - int(secs)) * 100)
    return f"{datetime.timedelta(seconds=int(secs))}.{msec:02d}"
def metrics_format(self, metrics: Dict[str, float]) -> Dict[str, float]:
    metrics_copy = metrics.copy()
    for k, v in metrics_copy.items():
        if "_mem_" in k: metrics_copy[k] = f"{ v >> 20 }MB"
        elif "_runtime" in k: metrics_copy[k] = _secs2timedelta(v)
        elif k == "total_flos": metrics_copy[k] = f"{ int(v) >> 30 }GF"
        elif isinstance(metrics_copy[k], float): metrics_copy[k] = round(v, 4)
    return metrics_copy
def log_metrics(self, split, metrics):
    if not self.is_world_process_zero(): return
    print(f"***** {split} metrics *****")
    metrics_formatted = self.metrics_format(metrics)
    k_width = max(len(str(x)) for x in metrics_formatted.keys())
    v_width = max(len(str(x)) for x in metrics_formatted.values())
    for key in sorted(metrics_formatted.keys()): print(f"  {key: <{k_width}} = {metrics_formatted[key]:>{v_width}}")
def save_metrics(self, split, metrics, combined=True):
    if not self.is_world_process_zero(): return
    path = os.path.join(self.args.output_dir, f"{split}_results.json")
    with open(path, "w") as f: json.dump(metrics, f, indent=4, sort_keys=True)
    if combined:
        path = os.path.join(self.args.output_dir, "all_results.json")
        if os.path.exists(path):
            with open(path, "r") as f: all_metrics = json.load(f)
        else: all_metrics = {}
        all_metrics.update(metrics)
        with open(path, "w") as f: json.dump(all_metrics, f, indent=4, sort_keys=True)
def save_state(self):
    if not self.is_world_process_zero(): return
    path = os.path.join(self.args.output_dir, "trainer_state.json")
    self.state.save_to_json(path)
def get_model_param_count(model, trainable_only=False):
    if is_deepspeed_zero3_enabled():
        def numel(p): return p.ds_numel if hasattr(p, "ds_numel") else p.numel()
    else:
        def numel(p): return p.numel()
    return sum(numel(p) for p in model.parameters() if not trainable_only or p.requires_grad)
def get_parameter_names(model, forbidden_layer_types):
    result = []
    for name, child in model.named_children(): result += [f"{name}.{n}" for n in get_parameter_names(child, forbidden_layer_types) if not isinstance(child, tuple(forbidden_layer_types))]
    result += list(model._parameters.keys())
    return result
def get_module_class_from_name(module, name):
    modules_children = list(module.children())
    if module.__class__.__name__ == name: return module.__class__
    elif len(modules_children) == 0: return
    else:
        for child_module in modules_children:
            module_class = get_module_class_from_name(child_module, name)
            if module_class is not None: return module_class
def remove_dummy_checkpoint(is_main_process, output_dir, filenames):
    if is_main_process:
        for filename in filenames:
            file = os.path.join(output_dir, filename)
            if os.path.isfile(file): os.remove(file)
if is_sagemaker_mp_enabled():
    import smdistributed.modelparallel.torch as smp
    @smp.step()
    def smp_forward_backward(model, inputs, gradient_accumulation_steps=1):
        outputs = model(**inputs)
        loss = outputs["loss"] if isinstance(outputs, dict) else outputs[0]
        loss /= gradient_accumulation_steps
        model.backward(loss)
        return loss
    @smp.step()
    def smp_forward_only(model, inputs): return model(**inputs)
    def smp_gather(tensor):
        if isinstance(tensor, (list, tuple)): return type(tensor)(smp_gather(t) for t in tensor)
        elif isinstance(tensor, dict): return type(tensor)({k: smp_gather(v) for k, v in tensor.items()})
        elif not isinstance(tensor, torch.Tensor): raise TypeError(f"Can't gather the values of type {type(tensor)}, only of nested list/tuple/dicts of tensors.")
        all_tensors = smp.allgather(tensor, smp.CommGroup.DP_GROUP)
        all_tensors = [atleast_1d(t) for t in all_tensors]
        return torch.cat([t.cpu() for t in all_tensors], dim=0)
    def smp_nested_concat(tensor):
        if isinstance(tensor, (list, tuple)): return type(tensor)(smp_nested_concat(t) for t in tensor)
        elif isinstance(tensor, dict): return type(tensor)({k: smp_nested_concat(v) for k, v in tensor.items()})
        return tensor.concat().detach().cpu()
@dataclass
class AcceleratorConfig:
    split_batches: bool = field(default=False, metadata={'help': 'Whether or not the accelerator should split the batches yielded by the dataloaders across the devices. If `True` the actual batch size used will be the same on any kind of distributed processes, but it must be a round multiple of the `num_processes` you are using. If `False`, actual batch size used will be the one set in your script multiplied by the number of processes.'})
    dispatch_batches: bool = field(default=None, metadata={'help': 'If set to `True`, the dataloader prepared by the Accelerator is only iterated through on the main process and then the batches are split and broadcast to each process. Will default to `True` for `DataLoader` whose underlying dataset is an `IterableDataslet`, `False` otherwise.'})
    even_batches: bool = field(default=True, metadata={'help': 'If set to `True`, in cases where the total batch size across all processes does not exactly divide the dataset, samples at the start of the dataset will be duplicated so the batch can be divided equally among all workers.'})
    use_seedable_sampler: bool = field(default=True, metadata={'help': 'Whether or not use a fully seedable random sampler ([`sapiens_accelerator.data_loader.SeedableRandomSampler`]).Ensures training results are fully reproducable using a different sampling technique. While seed-to-seed results may differ, on average the differences are neglible when usingmultiple different seeds to compare. Should also be ran with [`~utils.set_seed`] for the best results.'})
    non_blocking: Optional[bool] = field(default=False, metadata={'help': 'Whether to use non-blocking CUDA calls to help minimize synchronization during distributed training with prepared `DataLoader` inputs being moved to device. Best if used with `pin_memory=True` in the `TrainingArguments`. Requires sapiens_accelerator v0.30.0.'})
    gradient_accumulation_kwargs: Optional[Dict] = field(default=None, metadata={'help': 'Additional kwargs to configure gradient accumulation, see [`sapiens_accelerator.utils.GradientAccumulationPlugin`]. Any of the following (optional) keys are acceptable: num_steps (`int`): Will take precedence over [`~.TrainingArguments.gradient_accumulation_steps`] if the latter is set to 1, otherwise an exception will be raised. adjust_scheduler (`bool`): Whether to adjust the scheduler steps to account for [`~.TrainingArguments.gradient_accumulation_steps`]. The [`sapiens_accelerator.utils.GradientAccumulationPlugin`] default is `True`. sync_each_batch (`bool`): Whether to synchronize the gradients at each data batch. The [`sapiens_accelerator.utils.GradientAccumulationPlugin`] default is `False`.'})
    use_configured_state: bool = field(default=False, metadata={'help': 'Whether or not to use a pre-configured `AcceleratorState` or `PartialState` defined before calling `TrainingArguments`.If `True`, an `Accelerator` or `PartialState` must be initialized. May lead to issues using sweeps or hyperparameter tuning.'})
    @classmethod
    def from_json_file(cls, json_file):
        open_file = io.open if os.path.exists(json_file) else open
        with open_file(json_file, "r", encoding="utf-8") as f: config_dict = json.load(f)
        extra_keys = sorted(key for key in config_dict.keys() if key not in cls.__dataclass_fields__.keys())
        if len(extra_keys) > 0: raise ValueError(f"The config file at {json_file} had unknown keys ({extra_keys}), please try upgrading your `transformers` version or fix (and potentially remove these keys) from your config file.")
        return cls(**config_dict)
    def to_dict(self): return copy.deepcopy(self.__dict__)
    def pop(self, key, default=None): return self.__dict__.pop(key, default)
class LayerWiseDummyOptimizer(torch.optim.Optimizer):
    def __init__(self, optimizer_dict=None, *args, **kwargs):
        dummy_tensor = torch.randn(1, 1)
        self.optimizer_dict = optimizer_dict
        super().__init__([dummy_tensor], {"lr": kwargs.get("lr", 1e-03)})
    def zero_grad(self, set_to_none: bool = True) -> None: pass
    def step(self, closure=None) -> Optional[float]: pass
class LayerWiseDummyScheduler(LRScheduler):
    def __init__(self, *args, **kwargs):
        self.default_lr = kwargs["lr"]
        optimizer = LayerWiseDummyOptimizer(**kwargs)
        last_epoch = -1
        verbose = False
        super().__init__(optimizer, last_epoch, verbose)
    def get_lr(self):
        lrs = [self.default_lr]
        if self.optimizer is not None:
            param_wise_lrs = [[group["lr"] for group in optim.param_groups] for optim in self.optimizer.optimizer_dict.values()]
            lrs = list(chain(*param_wise_lrs))
        return lrs
    def _get_closed_form_lr(self): return self.base_lrs
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
