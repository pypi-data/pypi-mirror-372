"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import json
import os
import pickle
import random
import time
import warnings
from typing import Dict, List, Optional
import torch
from filelock import FileLock
from torch.utils.data import Dataset
from ...tokenization_utils import PreTrainedTokenizer
from ...utils import logging
logger = logging.get_logger(__name__)
DEPRECATION_WARNING = ("This dataset will be removed from the library soon, preprocessing should be handled with the HF Datasets library. You can have a look at this example script for pointers: {0}")
class TextDataset(Dataset):
    def __init__(self, tokenizer: PreTrainedTokenizer, file_path: str, block_size: int, overwrite_cache=False, cache_dir: Optional[str] = None):
        if os.path.isfile(file_path) is False: raise ValueError(f"Input file path {file_path} not found")
        block_size = block_size - tokenizer.num_special_tokens_to_add(pair=False)
        directory, filename = os.path.split(file_path)
        cached_features_file = os.path.join(cache_dir if cache_dir is not None else directory, f"cached_lm_{tokenizer.__class__.__name__}_{block_size}_{filename}")
        lock_path = cached_features_file + ".lock"
        with FileLock(lock_path):
            if os.path.exists(cached_features_file) and not overwrite_cache:
                start = time.time()
                with open(cached_features_file, "rb") as handle: self.examples = pickle.load(handle)
                logger.info(f"Loading features from cached file {cached_features_file} [took %.3f s]", time.time() - start)
            else:
                logger.info(f"Creating features from dataset file at {directory}")
                self.examples = []
                with open(file_path, encoding="utf-8") as f: text = f.read()
                tokenized_text = tokenizer.convert_tokens_to_ids(tokenizer.tokenize(text))
                for i in range(0, len(tokenized_text) - block_size + 1, block_size): self.examples.append(tokenizer.build_inputs_with_special_tokens(tokenized_text[i : i + block_size]))
                start = time.time()
                with open(cached_features_file, "wb") as handle: pickle.dump(self.examples, handle, protocol=pickle.HIGHEST_PROTOCOL)
                logger.info(f"Saving features into cached file {cached_features_file} [took {time.time() - start:.3f} s]")
    def __len__(self): return len(self.examples)
    def __getitem__(self, i) -> torch.Tensor: return torch.tensor(self.examples[i], dtype=torch.long)
class LineByLineTextDataset(Dataset):
    def __init__(self, tokenizer: PreTrainedTokenizer, file_path: str, block_size: int):
        if os.path.isfile(file_path) is False: raise ValueError(f"Input file path {file_path} not found")
        logger.info(f"Creating features from dataset file at {file_path}")
        with open(file_path, encoding="utf-8") as f: lines = [line for line in f.read().splitlines() if (len(line) > 0 and not line.isspace())]
        batch_encoding = tokenizer(lines, add_special_tokens=True, truncation=True, max_length=block_size)
        self.examples = batch_encoding["input_ids"]
        self.examples = [{"input_ids": torch.tensor(e, dtype=torch.long)} for e in self.examples]
    def __len__(self): return len(self.examples)
    def __getitem__(self, i) -> Dict[str, torch.tensor]: return self.examples[i]
class LineByLineWithRefDataset(Dataset):
    def __init__(self, tokenizer: PreTrainedTokenizer, file_path: str, block_size: int, ref_path: str):
        if os.path.isfile(file_path) is False: raise ValueError(f"Input file path {file_path} not found")
        if os.path.isfile(ref_path) is False: raise ValueError(f"Ref file path {file_path} not found")
        logger.info(f"Creating features from dataset file at {file_path}")
        logger.info(f"Use ref segment results at {ref_path}")
        with open(file_path, encoding="utf-8") as f: data = f.readlines()
        data = [line.strip() for line in data if len(line) > 0 and not line.isspace()]
        with open(ref_path, encoding="utf-8") as f: ref = [json.loads(line) for line in f.read().splitlines() if (len(line) > 0 and not line.isspace())]
        if len(data) != len(ref): raise ValueError(f"Length of Input file should be equal to Ref file. But the length of {file_path} is {len(data)} while length of {ref_path} is {len(ref)}")
        batch_encoding = tokenizer(data, add_special_tokens=True, truncation=True, max_length=block_size)
        self.examples = batch_encoding["input_ids"]
        self.examples = [{"input_ids": torch.tensor(e, dtype=torch.long)} for e in self.examples]
        n = len(self.examples)
        for i in range(n): self.examples[i]["chinese_ref"] = torch.tensor(ref[i], dtype=torch.long)
    def __len__(self): return len(self.examples)
    def __getitem__(self, i) -> Dict[str, torch.tensor]: return self.examples[i]
class LineByLineWithSOPTextDataset(Dataset):
    def __init__(self, tokenizer: PreTrainedTokenizer, file_dir: str, block_size: int):
        if os.path.isdir(file_dir) is False: raise ValueError(f"{file_dir} is not a directory")
        logger.info(f"Creating features from dataset file folder at {file_dir}")
        self.examples = []
        for file_name in os.listdir(file_dir):
            file_path = os.path.join(file_dir, file_name)
            if os.path.isfile(file_path) is False: raise ValueError(f"{file_path} is not a file")
            article_open = False
            with open(file_path, encoding="utf-8") as f:
                original_lines = f.readlines()
                article_lines = []
                for line in original_lines:
                    if "<doc id=" in line: article_open = True
                    elif "</doc>" in line:
                        article_open = False
                        document = [tokenizer.convert_tokens_to_ids(tokenizer.tokenize(line)) for line in article_lines[1:] if (len(line) > 0 and not line.isspace())]
                        examples = self.create_examples_from_document(document, block_size, tokenizer)
                        self.examples.extend(examples)
                        article_lines = []
                    else:
                        if article_open: article_lines.append(line)
        logger.info("Dataset parse finished.")
    def create_examples_from_document(self, document, block_size, tokenizer, short_seq_prob=0.1):
        max_num_tokens = block_size - tokenizer.num_special_tokens_to_add(pair=True)
        target_seq_length = max_num_tokens
        if random.random() < short_seq_prob: target_seq_length = random.randint(2, max_num_tokens)
        examples = []
        current_chunk = []
        current_length = 0
        i = 0
        while i < len(document):
            segment = document[i]
            if not segment:
                i += 1
                continue
            current_chunk.append(segment)
            current_length += len(segment)
            if i == len(document) - 1 or current_length >= target_seq_length:
                if current_chunk:
                    a_end = 1
                    if len(current_chunk) >= 2: a_end = random.randint(1, len(current_chunk) - 1)
                    tokens_a = []
                    for j in range(a_end): tokens_a.extend(current_chunk[j])
                    tokens_b = []
                    for j in range(a_end, len(current_chunk)): tokens_b.extend(current_chunk[j])
                    if len(tokens_a) == 0 or len(tokens_b) == 0: continue
                    if random.random() < 0.5:
                        is_next = False
                        tokens_a, tokens_b = tokens_b, tokens_a
                    else: is_next = True
                    def truncate_seq_pair(tokens_a, tokens_b, max_num_tokens):
                        while True:
                            total_length = len(tokens_a) + len(tokens_b)
                            if total_length <= max_num_tokens: break
                            trunc_tokens = tokens_a if len(tokens_a) > len(tokens_b) else tokens_b
                            if not (len(trunc_tokens) >= 1): raise ValueError("Sequence length to be truncated must be no less than one")
                            if random.random() < 0.5: del trunc_tokens[0]
                            else: trunc_tokens.pop()
                    truncate_seq_pair(tokens_a, tokens_b, max_num_tokens)
                    if not (len(tokens_a) >= 1): raise ValueError(f"Length of sequence a is {len(tokens_a)} which must be no less than 1")
                    if not (len(tokens_b) >= 1): raise ValueError(f"Length of sequence b is {len(tokens_b)} which must be no less than 1")
                    input_ids = tokenizer.build_inputs_with_special_tokens(tokens_a, tokens_b)
                    token_type_ids = tokenizer.create_token_type_ids_from_sequences(tokens_a, tokens_b)
                    example = {"input_ids": torch.tensor(input_ids, dtype=torch.long), "token_type_ids": torch.tensor(token_type_ids, dtype=torch.long), "sentence_order_label": torch.tensor(0 if is_next else 1, dtype=torch.long)}
                    examples.append(example)
                current_chunk = []
                current_length = 0
            i += 1
        return examples
    def __len__(self): return len(self.examples)
    def __getitem__(self, i) -> Dict[str, torch.tensor]: return self.examples[i]
class TextDatasetForNextSentencePrediction(Dataset):
    def __init__(self, tokenizer: PreTrainedTokenizer, file_path: str, block_size: int, overwrite_cache=False, short_seq_probability=0.1, nsp_probability=0.5):
        if not os.path.isfile(file_path): raise ValueError(f"Input file path {file_path} not found")
        self.short_seq_probability = short_seq_probability
        self.nsp_probability = nsp_probability
        directory, filename = os.path.split(file_path)
        cached_features_file = os.path.join(directory, f"cached_nsp_{tokenizer.__class__.__name__}_{block_size}_{filename}")
        self.tokenizer = tokenizer
        lock_path = cached_features_file + ".lock"
        with FileLock(lock_path):
            if os.path.exists(cached_features_file) and not overwrite_cache:
                start = time.time()
                with open(cached_features_file, "rb") as handle: self.examples = pickle.load(handle)
                logger.info(f"Loading features from cached file {cached_features_file} [took %.3f s]", time.time() - start)
            else:
                logger.info(f"Creating features from dataset file at {directory}")
                self.documents = [[]]
                with open(file_path, encoding="utf-8") as f:
                    while True:
                        line = f.readline()
                        if not line: break
                        line = line.strip()
                        if not line and len(self.documents[-1]) != 0: self.documents.append([])
                        tokens = tokenizer.tokenize(line)
                        tokens = tokenizer.convert_tokens_to_ids(tokens)
                        if tokens: self.documents[-1].append(tokens)
                logger.info(f"Creating examples from {len(self.documents)} documents.")
                self.examples = []
                for doc_index, document in enumerate(self.documents): self.create_examples_from_document(document, doc_index, block_size)
                start = time.time()
                with open(cached_features_file, "wb") as handle: pickle.dump(self.examples, handle, protocol=pickle.HIGHEST_PROTOCOL)
                logger.info(f"Saving features into cached file {cached_features_file} [took {time.time() - start:.3f} s]")
    def create_examples_from_document(self, document: List[List[int]], doc_index: int, block_size: int):
        max_num_tokens = block_size - self.tokenizer.num_special_tokens_to_add(pair=True)
        target_seq_length = max_num_tokens
        if random.random() < self.short_seq_probability: target_seq_length = random.randint(2, max_num_tokens)
        current_chunk = []
        current_length = 0
        i = 0
        while i < len(document):
            segment = document[i]
            current_chunk.append(segment)
            current_length += len(segment)
            if i == len(document) - 1 or current_length >= target_seq_length:
                if current_chunk:
                    a_end = 1
                    if len(current_chunk) >= 2: a_end = random.randint(1, len(current_chunk) - 1)
                    tokens_a = []
                    for j in range(a_end): tokens_a.extend(current_chunk[j])
                    tokens_b = []
                    if len(current_chunk) == 1 or random.random() < self.nsp_probability:
                        is_random_next = True
                        target_b_length = target_seq_length - len(tokens_a)
                        for _ in range(10):
                            random_document_index = random.randint(0, len(self.documents) - 1)
                            if random_document_index != doc_index: break
                        random_document = self.documents[random_document_index]
                        random_start = random.randint(0, len(random_document) - 1)
                        for j in range(random_start, len(random_document)):
                            tokens_b.extend(random_document[j])
                            if len(tokens_b) >= target_b_length: break
                        num_unused_segments = len(current_chunk) - a_end
                        i -= num_unused_segments
                    else:
                        is_random_next = False
                        for j in range(a_end, len(current_chunk)):
                            tokens_b.extend(current_chunk[j])
                    if not (len(tokens_a) >= 1): raise ValueError(f"Length of sequence a is {len(tokens_a)} which must be no less than 1")
                    if not (len(tokens_b) >= 1): raise ValueError(f"Length of sequence b is {len(tokens_b)} which must be no less than 1")
                    input_ids = self.tokenizer.build_inputs_with_special_tokens(tokens_a, tokens_b)
                    token_type_ids = self.tokenizer.create_token_type_ids_from_sequences(tokens_a, tokens_b)
                    example = {"input_ids": torch.tensor(input_ids, dtype=torch.long), "token_type_ids": torch.tensor(token_type_ids, dtype=torch.long), "next_sentence_label": torch.tensor(1 if is_random_next else 0, dtype=torch.long)}
                    self.examples.append(example)
                current_chunk = []
                current_length = 0
            i += 1
    def __len__(self): return len(self.examples)
    def __getitem__(self, i): return self.examples[i]
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
