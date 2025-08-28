"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import os
from shutil import copyfile
from typing import Any, Dict, List, Optional, Tuple, Union
import sentencepiece as spm
from ...tokenization_utils import AddedToken, PreTrainedTokenizer
from ...tokenization_utils_base import (BatchEncoding, EncodedInput, PreTokenizedInput, TextInput, TextInputPair, TruncationStrategy)
from ...utils import PaddingStrategy, TensorType, add_end_docstrings, logging
from ..xlm_roberta.tokenization_xlm_roberta import (SPIECE_UNDERLINE, VOCAB_FILES_NAMES)
logger = logging.get_logger(__name__)
LAYOUTXLM_ENCODE_KWARGS_DOCSTRING = r"""
            add_special_tokens (`bool`, *optional*, defaults to `True`):
                Whether or not to encode the sequences with the special tokens relative to their model.
            padding (`bool`, `str` or [`~file_utils.PaddingStrategy`], *optional*, defaults to `False`):
                Activates and controls padding. Accepts the following values:
                - `True` or `'longest'`: Pad to the longest sequence in the batch (or no padding if only a single
                  sequence if provided).
                - `'max_length'`: Pad to a maximum length specified with the argument `max_length` or to the maximum
                  acceptable input length for the model if that argument is not provided.
                - `False` or `'do_not_pad'` (default): No padding (i.e., can output a batch with sequences of different
                  lengths).
            truncation (`bool`, `str` or [`~tokenization_utils_base.TruncationStrategy`], *optional*, defaults to `False`):
                Activates and controls truncation. Accepts the following values:
                - `True` or `'longest_first'`: Truncate to a maximum length specified with the argument `max_length` or
                  to the maximum acceptable input length for the model if that argument is not provided. This will
                  truncate token by token, removing a token from the longest sequence in the pair if a pair of
                  sequences (or a batch of pairs) is provided.
                - `'only_first'`: Truncate to a maximum length specified with the argument `max_length` or to the
                  maximum acceptable input length for the model if that argument is not provided. This will only
                  truncate the first sequence of a pair if a pair of sequences (or a batch of pairs) is provided.
                - `'only_second'`: Truncate to a maximum length specified with the argument `max_length` or to the
                  maximum acceptable input length for the model if that argument is not provided. This will only
                  truncate the second sequence of a pair if a pair of sequences (or a batch of pairs) is provided.
                - `False` or `'do_not_truncate'` (default): No truncation (i.e., can output batch with sequence lengths
                  greater than the model maximum admissible input size).
            max_length (`int`, *optional*):
                Controls the maximum length to use by one of the truncation/padding parameters.
                If left unset or set to `None`, this will use the predefined model maximum length if a maximum length
                is required by one of the truncation/padding parameters. If the model has no specific maximum input
                length (like XLNet) truncation/padding to a maximum length will be deactivated.
            stride (`int`, *optional*, defaults to 0):
                If set to a number along with `max_length`, the overflowing tokens returned when
                `return_overflowing_tokens=True` will contain some tokens from the end of the truncated sequence
                returned to provide some overlap between truncated and overflowing sequences. The value of this
                argument defines the number of overlapping tokens.
            pad_to_multiple_of (`int`, *optional*):
                If set will pad the sequence to a multiple of the provided value. This is especially useful to enable
                the use of Tensor Cores on NVIDIA hardware with compute capability `>= 7.5` (Volta).
            return_tensors (`str` or [`~file_utils.TensorType`], *optional*):
                If set, will return tensors instead of list of python integers. Acceptable values are:
                - `'tf'`: Return TensorFlow `tf.constant` objects.
                - `'pt'`: Return PyTorch `torch.Tensor` objects.
                - `'np'`: Return Numpy `np.ndarray` objects.
            return_token_type_ids (`bool`, *optional*):
                Whether to return token type IDs. If left to the default, will return the token type IDs according to
                the specific tokenizer's default, defined by the `return_outputs` attribute.
                [What are token type IDs?](../glossary#token-type-ids)
            return_attention_mask (`bool`, *optional*):
                Whether to return the attention mask. If left to the default, will return the attention mask according
                to the specific tokenizer's default, defined by the `return_outputs` attribute.
                [What are attention masks?](../glossary#attention-mask)
            return_overflowing_tokens (`bool`, *optional*, defaults to `False`):
                Whether or not to return overflowing token sequences. If a pair of sequences of input ids (or a batch
                of pairs) is provided with `truncation_strategy = longest_first` or `True`, an error is raised instead
                of returning overflowing tokens.
            return_special_tokens_mask (`bool`, *optional*, defaults to `False`):
                Whether or not to return special tokens mask information.
            return_offsets_mapping (`bool`, *optional*, defaults to `False`):
                Whether or not to return `(char_start, char_end)` for each token.
                This is only available on fast tokenizers inheriting from [`PreTrainedTokenizerFast`], if using
                Python's tokenizer, this method will raise `NotImplementedError`.
            return_length  (`bool`, *optional*, defaults to `False`):
                Whether or not to return the lengths of the encoded inputs.
            verbose (`bool`, *optional*, defaults to `True`):
                Whether or not to print more information and warnings.
            *kwargs*: passed to the `self.tokenize()` method
        Return:
            [`BatchEncoding`]: A [`BatchEncoding`] with the following fields:
            - *input_ids* -- List of token ids to be fed to a model.
              [What are input IDs?](../glossary#input-ids)
            - *bbox* -- List of bounding boxes to be fed to a model.
            - *token_type_ids* -- List of token type ids to be fed to a model (when `return_token_type_ids=True` or
              if *"token_type_ids"* is in `self.model_input_names`).
              [What are token type IDs?](../glossary#token-type-ids)
            - *attention_mask* -- List of indices specifying which tokens should be attended to by the model (when
              `return_attention_mask=True` or if *"attention_mask"* is in `self.model_input_names`).
              [What are attention masks?](../glossary#attention-mask)
            - *labels* -- List of labels to be fed to a model. (when `word_labels` is specified).
            - *overflowing_tokens* -- List of overflowing tokens sequences (when a `max_length` is specified and
              `return_overflowing_tokens=True`).
            - *num_truncated_tokens* -- Number of tokens truncated (when a `max_length` is specified and
              `return_overflowing_tokens=True`).
            - *special_tokens_mask* -- List of 0s and 1s, with 1 specifying added special tokens and 0 specifying
              regular sequence tokens (when `add_special_tokens=True` and `return_special_tokens_mask=True`).
            - *length* -- The length of the inputs (when `return_length=True`).
"""
class LayoutXLMTokenizer(PreTrainedTokenizer):
    vocab_files_names = VOCAB_FILES_NAMES
    model_input_names = ["input_ids", "attention_mask"]
    def __init__(self, vocab_file, bos_token="<s>", eos_token="</s>", sep_token="</s>", cls_token="<s>", unk_token="<unk>", pad_token="<pad>", mask_token="<mask>",
    cls_token_box=[0, 0, 0, 0], sep_token_box=[1000, 1000, 1000, 1000], pad_token_box=[0, 0, 0, 0], pad_token_label=-100, only_label_first_subword=True,
    sp_model_kwargs: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        mask_token = AddedToken(mask_token, lstrip=True, special=True) if isinstance(mask_token, str) else mask_token
        self.sp_model_kwargs = {} if sp_model_kwargs is None else sp_model_kwargs
        self.sp_model = spm.SentencePieceProcessor(**self.sp_model_kwargs)
        self.sp_model.Load(str(vocab_file))
        self.vocab_file = vocab_file
        self.fairseq_tokens_to_ids = {"<s>": 0, "<pad>": 1, "</s>": 2, "<unk>": 3}
        self.fairseq_offset = 1
        self.fairseq_tokens_to_ids["<mask>"] = len(self.sp_model) + self.fairseq_offset
        self.fairseq_ids_to_tokens = {v: k for k, v in self.fairseq_tokens_to_ids.items()}
        self.cls_token_box = cls_token_box
        self.sep_token_box = sep_token_box
        self.pad_token_box = pad_token_box
        self.pad_token_label = pad_token_label
        self.only_label_first_subword = only_label_first_subword
        super().__init__(bos_token=bos_token, eos_token=eos_token, unk_token=unk_token, sep_token=sep_token, cls_token=cls_token, pad_token=pad_token, mask_token=mask_token,
        cls_token_box=cls_token_box, sep_token_box=sep_token_box, pad_token_box=pad_token_box, pad_token_label=pad_token_label, only_label_first_subword=only_label_first_subword,
        sp_model_kwargs=self.sp_model_kwargs, **kwargs)
    def __getstate__(self):
        state = self.__dict__.copy()
        state["sp_model"] = None
        state["sp_model_proto"] = self.sp_model.serialized_model_proto()
        return state
    def __setstate__(self, d):
        self.__dict__ = d
        if not hasattr(self, "sp_model_kwargs"): self.sp_model_kwargs = {}
        self.sp_model = spm.SentencePieceProcessor(**self.sp_model_kwargs)
        self.sp_model.LoadFromSerializedProto(self.sp_model_proto)
    def build_inputs_with_special_tokens(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None) -> List[int]:
        if token_ids_1 is None: return [self.cls_token_id] + token_ids_0 + [self.sep_token_id]
        cls = [self.cls_token_id]
        sep = [self.sep_token_id]
        return cls + token_ids_0 + sep + sep + token_ids_1 + sep
    def get_special_tokens_mask(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None, already_has_special_tokens: bool = False) -> List[int]:
        if already_has_special_tokens: return super().get_special_tokens_mask(token_ids_0=token_ids_0, token_ids_1=token_ids_1, already_has_special_tokens=True)
        if token_ids_1 is None: return [1] + ([0] * len(token_ids_0)) + [1]
        return [1] + ([0] * len(token_ids_0)) + [1, 1] + ([0] * len(token_ids_1)) + [1]
    def create_token_type_ids_from_sequences(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None) -> List[int]:
        sep = [self.sep_token_id]
        cls = [self.cls_token_id]
        if token_ids_1 is None: return len(cls + token_ids_0 + sep) * [0]
        return len(cls + token_ids_0 + sep + sep + token_ids_1 + sep) * [0]
    @property
    def vocab_size(self): return len(self.sp_model) + self.fairseq_offset + 1
    def get_vocab(self):
        vocab = {self.convert_ids_to_tokens(i): i for i in range(self.vocab_size)}
        vocab.update(self.added_tokens_encoder)
        return vocab
    def _tokenize(self, text: str) -> List[str]: return self.sp_model.encode(text, out_type=str)
    def _convert_token_to_id(self, token):
        if token in self.fairseq_tokens_to_ids: return self.fairseq_tokens_to_ids[token]
        spm_id = self.sp_model.PieceToId(token)
        return spm_id + self.fairseq_offset if spm_id else self.unk_token_id
    def _convert_id_to_token(self, index):
        if index in self.fairseq_ids_to_tokens: return self.fairseq_ids_to_tokens[index]
        return self.sp_model.IdToPiece(index - self.fairseq_offset)
    def convert_tokens_to_string(self, tokens):
        out_string = "".join(tokens).replace(SPIECE_UNDERLINE, " ").strip()
        return out_string
    def save_vocabulary(self, save_directory: str, filename_prefix: Optional[str] = None) -> Tuple[str]:
        if not os.path.isdir(save_directory):
            logger.error(f"Vocabulary path ({save_directory}) should be a directory")
            return
        out_vocab_file = os.path.join(save_directory, (filename_prefix + "-" if filename_prefix else "") + VOCAB_FILES_NAMES["vocab_file"])
        if os.path.abspath(self.vocab_file) != os.path.abspath(out_vocab_file) and os.path.isfile(self.vocab_file): copyfile(self.vocab_file, out_vocab_file)
        elif not os.path.isfile(self.vocab_file):
            with open(out_vocab_file, "wb") as fi:
                content_spiece_model = self.sp_model.serialized_model_proto()
                fi.write(content_spiece_model)
        return (out_vocab_file,)
    @add_end_docstrings(LAYOUTXLM_ENCODE_KWARGS_DOCSTRING)
    def __call__(self, text: Union[TextInput, PreTokenizedInput, List[TextInput], List[PreTokenizedInput]], text_pair: Optional[Union[PreTokenizedInput, List[PreTokenizedInput]]] = None,
    boxes: Union[List[List[int]], List[List[List[int]]]] = None, word_labels: Optional[Union[List[int], List[List[int]]]] = None, add_special_tokens: bool = True,
    padding: Union[bool, str, PaddingStrategy] = False, truncation: Union[bool, str, TruncationStrategy] = None, max_length: Optional[int] = None,
    stride: int = 0, pad_to_multiple_of: Optional[int] = None, padding_side: Optional[bool] = None, return_tensors: Optional[Union[str, TensorType]] = None,
    return_token_type_ids: Optional[bool] = None, return_attention_mask: Optional[bool] = None, return_overflowing_tokens: bool = False,
    return_special_tokens_mask: bool = False, return_offsets_mapping: bool = False, return_length: bool = False, verbose: bool = True, **kwargs) -> BatchEncoding:
        def _is_valid_text_input(t):
            if isinstance(t, str): return True
            elif isinstance(t, (list, tuple)):
                if len(t) == 0: return True
                elif isinstance(t[0], str): return True
                elif isinstance(t[0], (list, tuple)): return len(t[0]) == 0 or isinstance(t[0][0], str)
                else: return False
            else: return False
        if text_pair is not None:
            if not _is_valid_text_input(text): raise ValueError("text input must of type `str` (single example) or `List[str]` (batch of examples). ")
            if not isinstance(text_pair, (list, tuple)): raise ValueError("words must of type `List[str]` (single pretokenized example), or `List[List[str]]` (batch of pretokenized examples).")
        else:
            if not isinstance(text, (list, tuple)): raise ValueError("Words must of type `List[str]` (single pretokenized example), or `List[List[str]]` (batch of pretokenized examples).")
        if text_pair is not None: is_batched = isinstance(text, (list, tuple))
        else: is_batched = isinstance(text, (list, tuple)) and text and isinstance(text[0], (list, tuple))
        words = text if text_pair is None else text_pair
        if boxes is None: raise ValueError("You must provide corresponding bounding boxes")
        if is_batched:
            if len(words) != len(boxes): raise ValueError("You must provide words and boxes for an equal amount of examples")
            for words_example, boxes_example in zip(words, boxes):
                if len(words_example) != len(boxes_example): raise ValueError("You must provide as many words as there are bounding boxes")
        else:
            if len(words) != len(boxes): raise ValueError("You must provide as many words as there are bounding boxes")
        if is_batched:
            if text_pair is not None and len(text) != len(text_pair): raise ValueError(f"batch length of `text`: {len(text)} does not match batch length of `text_pair`: {len(text_pair)}.")
            batch_text_or_text_pairs = list(zip(text, text_pair)) if text_pair is not None else text
            is_pair = bool(text_pair is not None)
            return self.batch_encode_plus(batch_text_or_text_pairs=batch_text_or_text_pairs, is_pair=is_pair, boxes=boxes, word_labels=word_labels, add_special_tokens=add_special_tokens,
            padding=padding, truncation=truncation, max_length=max_length, stride=stride, pad_to_multiple_of=pad_to_multiple_of, padding_side=padding_side, return_tensors=return_tensors,
            return_token_type_ids=return_token_type_ids, return_attention_mask=return_attention_mask, return_overflowing_tokens=return_overflowing_tokens, return_special_tokens_mask=return_special_tokens_mask,
            return_offsets_mapping=return_offsets_mapping, return_length=return_length, verbose=verbose, **kwargs)
        else:
            return self.encode_plus(text=text, text_pair=text_pair, boxes=boxes, word_labels=word_labels, add_special_tokens=add_special_tokens, padding=padding, truncation=truncation,
            max_length=max_length, stride=stride, pad_to_multiple_of=pad_to_multiple_of, padding_side=padding_side, return_tensors=return_tensors, return_token_type_ids=return_token_type_ids,
            return_attention_mask=return_attention_mask, return_overflowing_tokens=return_overflowing_tokens, return_special_tokens_mask=return_special_tokens_mask,
            return_offsets_mapping=return_offsets_mapping, return_length=return_length, verbose=verbose, **kwargs)
    def _batch_encode_plus(self, batch_text_or_text_pairs: Union[List[TextInput], List[TextInputPair], List[PreTokenizedInput]], is_pair: bool = None,
    boxes: Optional[List[List[List[int]]]] = None, word_labels: Optional[List[List[int]]] = None, add_special_tokens: bool = True, padding_strategy: PaddingStrategy = PaddingStrategy.DO_NOT_PAD,
    truncation_strategy: TruncationStrategy = TruncationStrategy.DO_NOT_TRUNCATE, max_length: Optional[int] = None, stride: int = 0, pad_to_multiple_of: Optional[int] = None,
    padding_side: Optional[bool] = None, return_tensors: Optional[Union[str, TensorType]] = None, return_token_type_ids: Optional[bool] = None, return_attention_mask: Optional[bool] = None,
    return_overflowing_tokens: bool = False, return_special_tokens_mask: bool = False, return_offsets_mapping: bool = False, return_length: bool = False, verbose: bool = True, **kwargs) -> BatchEncoding:
        if return_offsets_mapping: raise NotImplementedError("return_offset_mapping is not available when using Python tokenizers. To use this feature, change your tokenizer to one deriving from sapiens_transformers.PreTrainedTokenizerFast.")
        batch_outputs = self._batch_prepare_for_model(batch_text_or_text_pairs=batch_text_or_text_pairs, is_pair=is_pair, boxes=boxes, word_labels=word_labels, add_special_tokens=add_special_tokens,
        padding_strategy=padding_strategy, truncation_strategy=truncation_strategy, max_length=max_length, stride=stride, pad_to_multiple_of=pad_to_multiple_of, padding_side=padding_side,
        return_attention_mask=return_attention_mask, return_token_type_ids=return_token_type_ids, return_overflowing_tokens=return_overflowing_tokens, return_special_tokens_mask=return_special_tokens_mask,
        return_length=return_length, return_tensors=return_tensors, verbose=verbose)
        return BatchEncoding(batch_outputs)
    @add_end_docstrings(LAYOUTXLM_ENCODE_KWARGS_DOCSTRING)
    def _batch_prepare_for_model(self, batch_text_or_text_pairs, is_pair: bool = None, boxes: Optional[List[List[int]]] = None, word_labels: Optional[List[List[int]]] = None,
    add_special_tokens: bool = True, padding_strategy: PaddingStrategy = PaddingStrategy.DO_NOT_PAD, truncation_strategy: TruncationStrategy = TruncationStrategy.DO_NOT_TRUNCATE,
    max_length: Optional[int] = None, stride: int = 0, pad_to_multiple_of: Optional[int] = None, padding_side: Optional[bool] = None, return_tensors: Optional[str] = None,
    return_token_type_ids: Optional[bool] = None, return_attention_mask: Optional[bool] = None, return_overflowing_tokens: bool = False, return_special_tokens_mask: bool = False,
    return_length: bool = False, verbose: bool = True) -> BatchEncoding:
        batch_outputs = {}
        for idx, example in enumerate(zip(batch_text_or_text_pairs, boxes)):
            batch_text_or_text_pair, boxes_example = example
            outputs = self.prepare_for_model(batch_text_or_text_pair[0] if is_pair else batch_text_or_text_pair, batch_text_or_text_pair[1] if is_pair else None,
            boxes_example, word_labels=word_labels[idx] if word_labels is not None else None, add_special_tokens=add_special_tokens, padding=PaddingStrategy.DO_NOT_PAD.value,
            truncation=truncation_strategy.value, max_length=max_length, stride=stride, pad_to_multiple_of=None, padding_side=None, return_attention_mask=False,
            return_token_type_ids=return_token_type_ids, return_overflowing_tokens=return_overflowing_tokens, return_special_tokens_mask=return_special_tokens_mask,
            return_length=return_length, return_tensors=None, prepend_batch_axis=False, verbose=verbose)
            for key, value in outputs.items():
                if key not in batch_outputs: batch_outputs[key] = []
                batch_outputs[key].append(value)
        batch_outputs = self.pad(batch_outputs, padding=padding_strategy.value, max_length=max_length, pad_to_multiple_of=pad_to_multiple_of, padding_side=padding_side, return_attention_mask=return_attention_mask)
        batch_outputs = BatchEncoding(batch_outputs, tensor_type=return_tensors)
        return batch_outputs
    def _encode_plus(self, text: Union[TextInput, PreTokenizedInput], text_pair: Optional[PreTokenizedInput] = None, boxes: Optional[List[List[int]]] = None,
    word_labels: Optional[List[int]] = None, add_special_tokens: bool = True, padding_strategy: PaddingStrategy = PaddingStrategy.DO_NOT_PAD, truncation_strategy: TruncationStrategy = TruncationStrategy.DO_NOT_TRUNCATE,
    max_length: Optional[int] = None, stride: int = 0, pad_to_multiple_of: Optional[int] = None, padding_side: Optional[bool] = None, return_tensors: Optional[Union[str, TensorType]] = None,
    return_token_type_ids: Optional[bool] = None, return_attention_mask: Optional[bool] = None, return_overflowing_tokens: bool = False, return_special_tokens_mask: bool = False,
    return_offsets_mapping: bool = False, return_length: bool = False, verbose: bool = True, **kwargs) -> BatchEncoding:
        if return_offsets_mapping: raise NotImplementedError("return_offset_mapping is not available when using Python tokenizers. To use this feature, change your tokenizer to one deriving from sapiens_transformers.PreTrainedTokenizerFast.")
        return self.prepare_for_model(text=text, text_pair=text_pair, boxes=boxes, word_labels=word_labels, add_special_tokens=add_special_tokens, padding=padding_strategy.value,
        truncation=truncation_strategy.value, max_length=max_length, stride=stride, pad_to_multiple_of=pad_to_multiple_of, padding_side=padding_side, return_tensors=return_tensors,
        prepend_batch_axis=True, return_attention_mask=return_attention_mask, return_token_type_ids=return_token_type_ids, return_overflowing_tokens=return_overflowing_tokens,
        return_special_tokens_mask=return_special_tokens_mask, return_length=return_length, verbose=verbose)
    @add_end_docstrings(LAYOUTXLM_ENCODE_KWARGS_DOCSTRING)
    def prepare_for_model(self, text: Union[TextInput, PreTokenizedInput], text_pair: Optional[PreTokenizedInput] = None, boxes: Optional[List[List[int]]] = None,
    word_labels: Optional[List[int]] = None, add_special_tokens: bool = True, padding: Union[bool, str, PaddingStrategy] = False, truncation: Union[bool, str, TruncationStrategy] = None,
    max_length: Optional[int] = None, stride: int = 0, pad_to_multiple_of: Optional[int] = None, padding_side: Optional[bool] = None, return_tensors: Optional[Union[str, TensorType]] = None,
    return_token_type_ids: Optional[bool] = None, return_attention_mask: Optional[bool] = None, return_overflowing_tokens: bool = False, return_special_tokens_mask: bool = False,
    return_offsets_mapping: bool = False, return_length: bool = False, verbose: bool = True, prepend_batch_axis: bool = False, **kwargs) -> BatchEncoding:
        padding_strategy, truncation_strategy, max_length, kwargs = self._get_padding_truncation_strategies(padding=padding, truncation=truncation, max_length=max_length,
        pad_to_multiple_of=pad_to_multiple_of, verbose=verbose, **kwargs)
        tokens = []
        pair_tokens = []
        token_boxes = []
        pair_token_boxes = []
        labels = []
        if text_pair is None:
            if word_labels is None:
                for word, box in zip(text, boxes):
                    if len(word) < 1: continue
                    word_tokens = self.tokenize(word)
                    tokens.extend(word_tokens)
                    token_boxes.extend([box] * len(word_tokens))
            else:
                for word, box, label in zip(text, boxes, word_labels):
                    if len(word) < 1: continue
                    word_tokens = self.tokenize(word)
                    tokens.extend(word_tokens)
                    token_boxes.extend([box] * len(word_tokens))
                    if self.only_label_first_subword: labels.extend([label] + [self.pad_token_label] * (len(word_tokens) - 1))
                    else: labels.extend([label] * len(word_tokens))
        else:
            tokens = self.tokenize(text)
            token_boxes = [self.pad_token_box for _ in range(len(tokens))] + [self.sep_token_box]
            for word, box in zip(text_pair, boxes):
                if len(word) < 1: continue
                word_tokens = self.tokenize(word)
                pair_tokens.extend(word_tokens)
                pair_token_boxes.extend([box] * len(word_tokens))
        ids = self.convert_tokens_to_ids(tokens)
        pair_ids = self.convert_tokens_to_ids(pair_tokens) if pair_tokens else None
        pair = bool(pair_ids is not None)
        len_ids = len(ids)
        len_pair_ids = len(pair_ids) if pair else 0
        total_len = len_ids + len_pair_ids + (self.num_special_tokens_to_add(pair=pair) if add_special_tokens else 0)
        overflowing_tokens = []
        overflowing_token_boxes = []
        overflowing_labels = []
        if truncation_strategy != TruncationStrategy.DO_NOT_TRUNCATE and max_length and total_len > max_length: (ids, token_boxes, pair_ids, pair_token_boxes, labels, overflowing_tokens, overflowing_token_boxes,
        overflowing_labels) = self.truncate_sequences(ids, token_boxes, pair_ids=pair_ids, pair_token_boxes=pair_token_boxes, labels=labels, num_tokens_to_remove=total_len - max_length, truncation_strategy=truncation_strategy, stride=stride)
        if return_token_type_ids and not add_special_tokens: raise ValueError("Asking to return token_type_ids while setting add_special_tokens to False results in an undefined behavior. Please set add_special_tokens to True or set return_token_type_ids to None.")
        if return_token_type_ids is None: return_token_type_ids = "token_type_ids" in self.model_input_names
        if return_attention_mask is None: return_attention_mask = "attention_mask" in self.model_input_names
        encoded_inputs = {}
        if return_overflowing_tokens:
            encoded_inputs["overflowing_tokens"] = overflowing_tokens
            encoded_inputs["overflowing_token_boxes"] = overflowing_token_boxes
            encoded_inputs["overflowing_labels"] = overflowing_labels
            encoded_inputs["num_truncated_tokens"] = total_len - max_length
        if add_special_tokens:
            sequence = self.build_inputs_with_special_tokens(ids, pair_ids)
            token_type_ids = self.create_token_type_ids_from_sequences(ids, pair_ids)
            token_boxes = [self.cls_token_box] + token_boxes + [self.sep_token_box]
            if pair_token_boxes: pair_token_boxes = pair_token_boxes + [self.sep_token_box]
            if labels: labels = [self.pad_token_label] + labels + [self.pad_token_label]
        else:
            sequence = ids + pair_ids if pair else ids
            token_type_ids = [0] * len(ids) + ([0] * len(pair_ids) if pair else [])
        encoded_inputs["input_ids"] = sequence
        encoded_inputs["bbox"] = token_boxes + pair_token_boxes
        if return_token_type_ids: encoded_inputs["token_type_ids"] = token_type_ids
        if return_special_tokens_mask:
            if add_special_tokens: encoded_inputs["special_tokens_mask"] = self.get_special_tokens_mask(ids, pair_ids)
            else: encoded_inputs["special_tokens_mask"] = [0] * len(sequence)
        if labels: encoded_inputs["labels"] = labels
        self._eventual_warn_about_too_long_sequence(encoded_inputs["input_ids"], max_length, verbose)
        if padding_strategy != PaddingStrategy.DO_NOT_PAD or return_attention_mask: encoded_inputs = self.pad(encoded_inputs, max_length=max_length, padding=padding_strategy.value,
        pad_to_multiple_of=pad_to_multiple_of, padding_side=padding_side, return_attention_mask=return_attention_mask)
        if return_length: encoded_inputs["length"] = len(encoded_inputs["input_ids"])
        batch_outputs = BatchEncoding(encoded_inputs, tensor_type=return_tensors, prepend_batch_axis=prepend_batch_axis)
        return batch_outputs
    def truncate_sequences(self, ids: List[int], token_boxes: List[List[int]], pair_ids: Optional[List[int]] = None, pair_token_boxes: Optional[List[List[int]]] = None,
    labels: Optional[List[int]] = None, num_tokens_to_remove: int = 0, truncation_strategy: Union[str, TruncationStrategy] = "longest_first", stride: int = 0) -> Tuple[List[int], List[int], List[int]]:
        if num_tokens_to_remove <= 0: return ids, token_boxes, pair_ids, pair_token_boxes, labels, [], [], []
        if not isinstance(truncation_strategy, TruncationStrategy): truncation_strategy = TruncationStrategy(truncation_strategy)
        overflowing_tokens = []
        overflowing_token_boxes = []
        overflowing_labels = []
        if truncation_strategy == TruncationStrategy.LONGEST_FIRST:
            for _ in range(num_tokens_to_remove):
                if pair_ids is None or len(ids) > len(pair_ids):
                    if not overflowing_tokens: window_len = min(len(ids), stride + 1)
                    else: window_len = 1
                    overflowing_tokens.extend(ids[-window_len:])
                    overflowing_token_boxes.extend(token_boxes[-window_len:])
                    overflowing_labels.extend(labels[-window_len:])
                    ids = ids[:-1]
                    token_boxes = token_boxes[:-1]
                    labels = labels[:-1]
                else:
                    if not overflowing_tokens: window_len = min(len(pair_ids), stride + 1)
                    else: window_len = 1
                    overflowing_tokens.extend(pair_ids[-window_len:])
                    overflowing_token_boxes.extend(pair_token_boxes[-window_len:])
                    pair_ids = pair_ids[:-1]
                    pair_token_boxes = pair_token_boxes[:-1]
        elif truncation_strategy == TruncationStrategy.ONLY_FIRST:
            if len(ids) > num_tokens_to_remove:
                window_len = min(len(ids), stride + num_tokens_to_remove)
                overflowing_tokens = ids[-window_len:]
                overflowing_token_boxes = token_boxes[-window_len:]
                overflowing_labels = labels[-window_len:]
                ids = ids[:-num_tokens_to_remove]
                token_boxes = token_boxes[:-num_tokens_to_remove]
                labels = labels[:-num_tokens_to_remove]
            else: logger.error(f"We need to remove {num_tokens_to_remove} to truncate the input but the first sequence has a length {len(ids)}. Please select another truncation strategy than {truncation_strategy}, for instance 'longest_first' or 'only_second'.")
        elif truncation_strategy == TruncationStrategy.ONLY_SECOND and pair_ids is not None:
            if len(pair_ids) > num_tokens_to_remove:
                window_len = min(len(pair_ids), stride + num_tokens_to_remove)
                overflowing_tokens = pair_ids[-window_len:]
                overflowing_token_boxes = pair_token_boxes[-window_len:]
                pair_ids = pair_ids[:-num_tokens_to_remove]
                pair_token_boxes = pair_token_boxes[:-num_tokens_to_remove]
            else: logger.error(f"We need to remove {num_tokens_to_remove} to truncate the input but the second sequence has a length {len(pair_ids)}. Please select another truncation strategy than {truncation_strategy}, for instance 'longest_first' or 'only_first'.")
        return (ids, token_boxes, pair_ids, pair_token_boxes, labels, overflowing_tokens, overflowing_token_boxes, overflowing_labels)
    def _pad(self, encoded_inputs: Union[Dict[str, EncodedInput], BatchEncoding], max_length: Optional[int] = None, padding_strategy: PaddingStrategy = PaddingStrategy.DO_NOT_PAD,
    pad_to_multiple_of: Optional[int] = None, padding_side: Optional[bool] = None, return_attention_mask: Optional[bool] = None) -> dict:
        if return_attention_mask is None: return_attention_mask = "attention_mask" in self.model_input_names
        required_input = encoded_inputs[self.model_input_names[0]]
        if padding_strategy == PaddingStrategy.LONGEST: max_length = len(required_input)
        if max_length is not None and pad_to_multiple_of is not None and (max_length % pad_to_multiple_of != 0): max_length = ((max_length // pad_to_multiple_of) + 1) * pad_to_multiple_of
        needs_to_be_padded = padding_strategy != PaddingStrategy.DO_NOT_PAD and len(required_input) != max_length
        if return_attention_mask and "attention_mask" not in encoded_inputs: encoded_inputs["attention_mask"] = [1] * len(required_input)
        if needs_to_be_padded:
            difference = max_length - len(required_input)
            padding_side = padding_side if padding_side is not None else self.padding_side
            if padding_side == "right":
                if return_attention_mask: encoded_inputs["attention_mask"] = encoded_inputs["attention_mask"] + [0] * difference
                if "token_type_ids" in encoded_inputs: encoded_inputs["token_type_ids"] = (encoded_inputs["token_type_ids"] + [self.pad_token_type_id] * difference)
                if "bbox" in encoded_inputs: encoded_inputs["bbox"] = encoded_inputs["bbox"] + [self.pad_token_box] * difference
                if "labels" in encoded_inputs: encoded_inputs["labels"] = encoded_inputs["labels"] + [self.pad_token_label] * difference
                if "special_tokens_mask" in encoded_inputs: encoded_inputs["special_tokens_mask"] = encoded_inputs["special_tokens_mask"] + [1] * difference
                encoded_inputs[self.model_input_names[0]] = required_input + [self.pad_token_id] * difference
            elif padding_side == "left":
                if return_attention_mask: encoded_inputs["attention_mask"] = [0] * difference + encoded_inputs["attention_mask"]
                if "token_type_ids" in encoded_inputs: encoded_inputs["token_type_ids"] = [self.pad_token_type_id] * difference + encoded_inputs["token_type_ids"]
                if "bbox" in encoded_inputs: encoded_inputs["bbox"] = [self.pad_token_box] * difference + encoded_inputs["bbox"]
                if "labels" in encoded_inputs: encoded_inputs["labels"] = [self.pad_token_label] * difference + encoded_inputs["labels"]
                if "special_tokens_mask" in encoded_inputs: encoded_inputs["special_tokens_mask"] = [1] * difference + encoded_inputs["special_tokens_mask"]
                encoded_inputs[self.model_input_names[0]] = [self.pad_token_id] * difference + required_input
            else: raise ValueError("Invalid padding strategy:" + str(padding_side))
        return encoded_inputs
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
