"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from collections import OrderedDict
from typing import Mapping
from ...configuration_utils import PretrainedConfig
from ...onnx import OnnxConfig
from ...utils import logging
logger = logging.get_logger(__name__)
class XLMConfig(PretrainedConfig):
    model_type = "xlm"
    attribute_map = {'hidden_size': 'emb_dim', 'num_attention_heads': 'n_heads', 'num_hidden_layers': 'n_layers', 'n_words': 'vocab_size'}
    def __init__(self, vocab_size=30145, emb_dim=2048, n_layers=12, n_heads=16, dropout=0.1, attention_dropout=0.1, gelu_activation=True, sinusoidal_embeddings=False,
    causal=False, asm=False, n_langs=1, use_lang_emb=True, max_position_embeddings=512, embed_init_std=2048**-0.5, layer_norm_eps=1e-12, init_std=0.02, bos_index=0,
    eos_index=1, pad_index=2, unk_index=3, mask_index=5, is_encoder=True, summary_type="first", summary_use_proj=True, summary_activation=None, summary_proj_to_labels=True,
    summary_first_dropout=0.1, start_n_top=5, end_n_top=5, mask_token_id=0, lang_id=0, pad_token_id=2, bos_token_id=0, **kwargs):
        self.vocab_size = vocab_size
        self.emb_dim = emb_dim
        self.n_layers = n_layers
        self.n_heads = n_heads
        self.dropout = dropout
        self.attention_dropout = attention_dropout
        self.gelu_activation = gelu_activation
        self.sinusoidal_embeddings = sinusoidal_embeddings
        self.causal = causal
        self.asm = asm
        self.n_langs = n_langs
        self.use_lang_emb = use_lang_emb
        self.layer_norm_eps = layer_norm_eps
        self.bos_index = bos_index
        self.eos_index = eos_index
        self.pad_index = pad_index
        self.unk_index = unk_index
        self.mask_index = mask_index
        self.is_encoder = is_encoder
        self.max_position_embeddings = max_position_embeddings
        self.embed_init_std = embed_init_std
        self.init_std = init_std
        self.summary_type = summary_type
        self.summary_use_proj = summary_use_proj
        self.summary_activation = summary_activation
        self.summary_proj_to_labels = summary_proj_to_labels
        self.summary_first_dropout = summary_first_dropout
        self.start_n_top = start_n_top
        self.end_n_top = end_n_top
        self.mask_token_id = mask_token_id
        self.lang_id = lang_id
        if "n_words" in kwargs: self.n_words = kwargs["n_words"]
        super().__init__(pad_token_id=pad_token_id, bos_token_id=bos_token_id, **kwargs)
class XLMOnnxConfig(OnnxConfig):
    @property
    def inputs(self) -> Mapping[str, Mapping[int, str]]:
        if self.task == "multiple-choice": dynamic_axis = {0: "batch", 1: "choice", 2: "sequence"}
        else: dynamic_axis = {0: "batch", 1: "sequence"}
        return OrderedDict([("input_ids", dynamic_axis), ("attention_mask", dynamic_axis), ("token_type_ids", dynamic_axis)])
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
