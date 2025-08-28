"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from array import array
import numpy as np
from tokenizers import Tokenizer, decoders, normalizers, pre_tokenizers
from tokenizers.models import BPE
from .. import AddedToken
from ..convert_slow_tokenizer import EntityConverter, LlamaConverter, Qwen2Converter, SapamaConverter, SapiensConverter
from ..utils import logging
from ..utils.logging import tqdm
logger = logging.get_logger(__name__)
GGUF_TENSOR_MAPPING = {"entity": {'token_embd': 'model.embed_tokens', 'blk': 'model.layers', 'ffn_up': 'mlp.up_proj', 'ffn_down': 'mlp.down_proj', 'ffn_gate': 'mlp.gate_proj', 'ffn_norm': 'post_attention_layernorm', 'attn_norm': 'input_layernorm', 'attn_q': 'self_attn.q_proj', 'attn_v': 'self_attn.v_proj', 'attn_k': 'self_attn.k_proj', 'attn_output': 'self_attn.o_proj', 'output.weight': 'lm_head.weight', 'output_norm': 'model.norm'},
"llama": {'token_embd': 'model.embed_tokens', 'blk': 'model.layers', 'ffn_up': 'mlp.up_proj', 'ffn_down': 'mlp.down_proj', 'ffn_gate': 'mlp.gate_proj', 'ffn_norm': 'post_attention_layernorm', 'attn_norm': 'input_layernorm', 'attn_q': 'self_attn.q_proj', 'attn_v': 'self_attn.v_proj', 'attn_k': 'self_attn.k_proj', 'attn_output': 'self_attn.o_proj', 'output.weight': 'lm_head.weight', 'output_norm': 'model.norm'},
"mistral": {'token_embd': 'model.embed_tokens', 'blk': 'model.layers', 'ffn_up': 'mlp.up_proj', 'ffn_down': 'mlp.down_proj', 'ffn_gate': 'mlp.gate_proj', 'ffn_norm': 'post_attention_layernorm', 'attn_norm': 'input_layernorm', 'attn_q': 'self_attn.q_proj', 'attn_v': 'self_attn.v_proj', 'attn_k': 'self_attn.k_proj', 'attn_output': 'self_attn.o_proj', 'output.weight': 'lm_head.weight', 'output_norm': 'model.norm'},
"phi3": {'token_embd': 'model.embed_tokens', 'blk': 'model.layers', 'ffn_up': 'mlp.gate_up_proj', 'ffn_down': 'mlp.down_proj', 'ffn_gate': 'mlp.gate_up_proj', 'ffn_norm': 'post_attention_layernorm', 'attn_norm': 'input_layernorm', 'attn_qkv': 'self_attn.qkv_proj', 'attn_output': 'self_attn.o_proj', 'output.weight': 'lm_head.weight', 'output_norm': 'model.norm'},
"qwen2": {'token_embd': 'model.embed_tokens', 'blk': 'model.layers', 'ffn_up': 'mlp.up_proj', 'ffn_down': 'mlp.down_proj', 'ffn_gate': 'mlp.gate_proj', 'ffn_norm': 'post_attention_layernorm', 'attn_norm': 'input_layernorm', 'attn_q': 'self_attn.q_proj', 'attn_v': 'self_attn.v_proj', 'attn_k': 'self_attn.k_proj', 'attn_output': 'self_attn.o_proj', 'output.weight': 'lm_head.weight', 'output_norm': 'model.norm'},
"qwen2moe": {'token_embd': 'model.embed_tokens', 'blk': 'model.layers', 'ffn_up': 'mlp.up_proj', 'ffn_down': 'mlp.down_proj', 'ffn_gate': 'mlp.gate_proj', 'ffn_norm': 'post_attention_layernorm', 'attn_norm': 'input_layernorm', 'attn_q': 'self_attn.q_proj', 'attn_v': 'self_attn.v_proj', 'attn_k': 'self_attn.k_proj', 'attn_output': 'self_attn.o_proj', 'output.weight': 'lm_head.weight', 'output_norm': 'model.norm'},
"sapama": {'token_embd': 'model.embed_tokens', 'blk': 'model.layers', 'ffn_up': 'mlp.up_proj', 'ffn_down': 'mlp.down_proj', 'ffn_gate': 'mlp.gate_proj', 'ffn_norm': 'post_attention_layernorm', 'attn_norm': 'input_layernorm', 'attn_q': 'self_attn.q_proj', 'attn_v': 'self_attn.v_proj', 'attn_k': 'self_attn.k_proj', 'attn_output': 'self_attn.o_proj', 'output.weight': 'lm_head.weight', 'output_norm': 'model.norm'},
"sapiens": {'token_embd': 'model.embed_tokens', 'blk': 'model.layers', 'ffn_up': 'mlp.up_proj', 'ffn_down': 'mlp.down_proj', 'ffn_gate': 'mlp.gate_proj', 'ffn_norm': 'post_attention_layernorm', 'attn_norm': 'input_layernorm', 'attn_q': 'self_attn.q_proj', 'attn_v': 'self_attn.v_proj', 'attn_k': 'self_attn.k_proj', 'attn_output': 'self_attn.o_proj', 'output.weight': 'lm_head.weight', 'output_norm': 'model.norm'},
"sastral": {'token_embd': 'model.embed_tokens', 'blk': 'model.layers', 'ffn_up': 'mlp.up_proj', 'ffn_down': 'mlp.down_proj', 'ffn_gate': 'mlp.gate_proj', 'ffn_norm': 'post_attention_layernorm', 'attn_norm': 'input_layernorm', 'attn_q': 'self_attn.q_proj', 'attn_v': 'self_attn.v_proj', 'attn_k': 'self_attn.k_proj', 'attn_output': 'self_attn.o_proj', 'output.weight': 'lm_head.weight', 'output_norm': 'model.norm'}}
GGUF_CONFIG_MAPPING = {"entity": {'context_length': 'max_position_embeddings', 'block_count': 'num_hidden_layers', 'feed_forward_length': 'intermediate_size', 'embedding_length': 'hidden_size', 'rope.dimension_count': 'head_dim', 'rope.freq_base': 'rope_theta', 'attention.head_count': 'num_attention_heads', 'attention.head_count_kv': 'num_key_value_heads', 'attention.layer_norm_rms_epsilon': 'rms_norm_eps', 'vocab_size': 'vocab_size'},
"general": {'architecture': 'model_type', 'name': '_model_name_or_path'},
"llama": {'context_length': 'max_position_embeddings', 'block_count': 'num_hidden_layers', 'feed_forward_length': 'intermediate_size', 'embedding_length': 'hidden_size', 'rope.dimension_count': 'head_dim', 'rope.freq_base': 'rope_theta', 'attention.head_count': 'num_attention_heads', 'attention.head_count_kv': 'num_key_value_heads', 'attention.layer_norm_rms_epsilon': 'rms_norm_eps', 'vocab_size': 'vocab_size'},
"mistral": {'context_length': 'max_position_embeddings', 'block_count': 'num_hidden_layers', 'feed_forward_length': 'intermediate_size', 'embedding_length': 'hidden_size', 'rope.dimension_count': 'head_dim', 'rope.freq_base': 'rope_theta', 'attention.head_count': 'num_attention_heads', 'attention.head_count_kv': 'num_key_value_heads', 'attention.layer_norm_rms_epsilon': 'rms_norm_eps', 'vocab_size': 'vocab_size'},
"phi3": {'context_length': 'max_position_embeddings', 'block_count': 'num_hidden_layers', 'feed_forward_length': 'intermediate_size', 'embedding_length': 'hidden_size', 'rope.dimension_count': None, 'rope.freq_base': 'rope_theta', 'attention.head_count': 'num_attention_heads', 'attention.head_count_kv': 'num_key_value_heads', 'attention.layer_norm_rms_epsilon': 'rms_norm_eps', 'vocab_size': 'vocab_size'},
"qwen2": {'context_length': 'max_position_embeddings', 'block_count': 'num_hidden_layers', 'feed_forward_length': 'intermediate_size', 'embedding_length': 'hidden_size', 'rope.dimension_count': None, 'rope.freq_base': 'rope_theta', 'attention.head_count': 'num_attention_heads', 'attention.head_count_kv': 'num_key_value_heads', 'attention.layer_norm_rms_epsilon': 'rms_norm_eps', 'vocab_size': 'vocab_size'},
"qwen2moe": {'context_length': 'max_position_embeddings', 'block_count': 'num_hidden_layers', 'feed_forward_length': 'intermediate_size', 'embedding_length': 'hidden_size', 'rope.dimension_count': None, 'rope.freq_base': 'rope_theta', 'attention.head_count': 'num_attention_heads', 'attention.head_count_kv': 'num_key_value_heads', 'attention.layer_norm_rms_epsilon': 'rms_norm_eps', 'vocab_size': 'vocab_size'},
"sapama": {'context_length': 'max_position_embeddings', 'block_count': 'num_hidden_layers', 'feed_forward_length': 'intermediate_size', 'embedding_length': 'hidden_size', 'rope.dimension_count': 'head_dim', 'rope.freq_base': 'rope_theta', 'attention.head_count': 'num_attention_heads', 'attention.head_count_kv': 'num_key_value_heads', 'attention.layer_norm_rms_epsilon': 'rms_norm_eps', 'vocab_size': 'vocab_size'},
"sapiens": {'context_length': 'max_position_embeddings', 'block_count': 'num_hidden_layers', 'feed_forward_length': 'intermediate_size', 'embedding_length': 'hidden_size', 'rope.dimension_count': None, 'rope.freq_base': 'rope_theta', 'attention.head_count': 'num_attention_heads', 'attention.head_count_kv': 'num_key_value_heads', 'attention.layer_norm_rms_epsilon': 'rms_norm_eps', 'vocab_size': 'vocab_size'},
"sastral": {'context_length': 'max_position_embeddings', 'block_count': 'num_hidden_layers', 'feed_forward_length': 'intermediate_size', 'embedding_length': 'hidden_size', 'rope.dimension_count': 'head_dim', 'rope.freq_base': 'rope_theta', 'attention.head_count': 'num_attention_heads', 'attention.head_count_kv': 'num_key_value_heads', 'attention.layer_norm_rms_epsilon': 'rms_norm_eps', 'vocab_size': 'vocab_size'},
"tokenizer": {'ggml.bos_token_id': 'bos_token_id', 'ggml.eos_token_id': 'eos_token_id', 'ggml.unknown_token_id': 'unk_token_id', 'ggml.padding_token_id': 'pad_token_id'}}
GGUF_TOKENIZER_MAPPING = {"tokenizer": {'ggml.model': 'tokenizer_type', 'ggml.tokens': 'tokens', 'ggml.scores': 'scores', 'ggml.token_type': 'token_type', 'ggml.merges': 'merges', 'ggml.bos_token_id': 'bos_token_id', 'ggml.eos_token_id': 'eos_token_id', 'ggml.unknown_token_id': 'unk_token_id', 'ggml.padding_token_id': 'pad_token_id', 'ggml.add_space_prefix': 'add_prefix_space'},
"tokenizer_config": {'chat_template': 'chat_template', 'ggml.model': 'model_type', 'ggml.bos_token_id': 'bos_token_id', 'ggml.eos_token_id': 'eos_token_id', 'ggml.unknown_token_id': 'unk_token_id', 'ggml.padding_token_id': 'pad_token_id'}}
def _gguf_parse_value(_value, data_type):
    if not isinstance(data_type, list): data_type = [data_type]
    if len(data_type) == 1:
        data_type = data_type[0]
        array_data_type = None
    else:
        if data_type[0] != 9: raise ValueError("Received multiple types, therefore expected the first type to indicate an array.")
        data_type, array_data_type = data_type
    if data_type in [0, 1, 2, 3, 4, 5, 10, 11]: _value = int(_value[0])
    elif data_type in [6, 12]: _value = float(_value[0])
    elif data_type in [7]: _value = bool(_value[0])
    elif data_type in [8]: _value = array("B", list(_value)).tobytes().decode()
    elif data_type in [9]: _value = _gguf_parse_value(_value, array_data_type)
    return _value
class GGUFEntityConverter(EntityConverter):
    def __init__(self, tokenizer_dict):
        self.proto = GGUFTokenizerSkeleton(tokenizer_dict)
        self.original_tokenizer = self.proto
        self.additional_kwargs = {}
        self.is_entity_tokenizer = getattr(self.proto, "tokenizer_type", "entity") != "entity"
    def vocab(self, proto): return list(zip(proto.tokens, proto.scores))
    def merges(self, proto): return proto.merges
    def tokenizer(self, proto):
        vocab_scores = self.vocab(self.proto)
        merges = self.merges(self.proto)
        bpe_vocab = {word: i for i, (word, _score) in enumerate(vocab_scores)}
        unk_token = proto.tokens[proto.unk_token_id] if proto.unk_token_id is not None else None
        bos_token = proto.tokens[proto.bos_token_id] if getattr(proto, "bos_token_id", None) is not None else None
        eos_token = proto.tokens[proto.bos_token_id] if getattr(proto, "eos_token_id", None) is not None else None
        tokenizer = Tokenizer(BPE(bpe_vocab, merges, unk_token=unk_token, fuse_unk=True, byte_fallback=True))
        special_tokens = []
        if not hasattr(self.proto, "token_type"):
            if unk_token is not None: special_tokens.append(AddedToken(unk_token, normalized=False, special=True))
            if bos_token is not None: special_tokens.append(AddedToken(bos_token, normalized=False, special=True))
            if eos_token is not None: special_tokens.append(AddedToken(eos_token, normalized=False, special=True))
        else:
            special_tokens_idx = np.where(np.array(self.proto.token_type) == 3)[0]
            for idx in special_tokens_idx: special_tokens.append(AddedToken(self.proto.tokens[idx], normalized=False, special=True))
        if len(special_tokens) != 0: tokenizer.add_special_tokens(special_tokens)
        if len(self.proto.added_tokens) != 0: tokenizer.add_tokens([AddedToken(added_token, normalized=False, special=False) for added_token in self.proto.added_tokens])
        self.additional_kwargs["unk_token"] = unk_token
        self.additional_kwargs["eos_token"] = bos_token
        self.additional_kwargs["bos_token"] = eos_token
        if self.is_entity_tokenizer:
            self.additional_kwargs["add_prefix_space"] = None
            self.additional_kwargs["clean_up_tokenization_spaces"] = True
            self.additional_kwargs["legacy"] = False
            self.original_tokenizer.legacy = False
        return tokenizer
    def decoder(self, replacement, add_prefix_space):
        sequence = [decoders.ByteFallback(), decoders.Fuse(), decoders.Replace("▁", " ")]
        if self.is_entity_tokenizer: sequence += [decoders.ByteLevel(add_prefix_space=False, trim_offsets=False, use_regex=True)]
        if add_prefix_space: sequence += [decoders.Strip(content=" ", left=1)]
        return decoders.Sequence(sequence)
    def converted(self):
        tokenizer = self.tokenizer(self.proto)
        normalizer = self.normalizer(self.proto)
        if normalizer is not None: tokenizer.normalizer = normalizer
        replacement = "▁"
        add_prefix_space = True
        if hasattr(self.original_tokenizer, "add_prefix_space"): add_prefix_space = self.original_tokenizer.add_prefix_space
        pre_tokenizer = self.pre_tokenizer(replacement, add_prefix_space)
        if pre_tokenizer is not None: tokenizer.pre_tokenizer = pre_tokenizer
        tokenizer.decoder = self.decoder(replacement, add_prefix_space)
        post_processor = self.post_processor()
        if post_processor: tokenizer.post_processor = post_processor
        if self.is_entity_tokenizer:
            tokenizer.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False, trim_offsets=False, use_regex=True)
            tokenizer.normalizer = normalizers.Sequence([])
        return tokenizer
class GGUFTokenizerSkeleton:
    def __init__(self, dict_):
        for k, v in dict_.items(): setattr(self, k, v)
        if not hasattr(self, "merges"):
            if not hasattr(self, "tokens") or not hasattr(self, "scores"): raise ValueError("tokens and scores need to be passed for a LLaMa tokenizer without merges to be instantiated.")
            tokens = self.tokens
            scores = self.scores
            vocab = {t: scores[i] for i, t in enumerate(tokens)}
            logger.warning("Merges were not in checkpoint, building merges on the fly.")
            merges = []
            for merge, piece_score in tqdm(vocab.items()):
                local = []
                for index in range(1, len(merge)):
                    piece_l, piece_r = merge[:index], merge[index:]
                    if piece_l in tokens and piece_r in tokens: local.append((piece_l, piece_r, piece_score))
                local = sorted(local, key=lambda x: (vocab[x[0]], vocab[x[1]]), reverse=True)
                merges.extend(local)
            merges = sorted(merges, key=lambda val: val[2], reverse=True)
            merges = [(val[0], val[1]) for val in merges]
            self.merges = merges
        else:
            self.merges = [tuple(merge.split(" ")) for merge in self.merges]
            if not hasattr(self, "scores"): self.scores = [None for _ in range(len(self.tokens))]
        if not hasattr(self, "added_tokens"): self.added_tokens = []
        if not hasattr(self, "unk_token_id"): self.unk_token_id = None
        if hasattr(self, "unknown_token_id") and self.unk_token_id is None: self.unk_token_id = self.unknown_token_id
class GGUFLlamaConverter(LlamaConverter):
    def __init__(self, tokenizer_dict):
        self.proto = GGUFTokenizerSkeleton(tokenizer_dict)
        self.original_tokenizer = self.proto
        self.additional_kwargs = {}
        self.is_llama_3_tokenizer = getattr(self.proto, "tokenizer_type", "llama") != "llama"
    def vocab(self, proto): return list(zip(proto.tokens, proto.scores))
    def merges(self, proto): return proto.merges
    def tokenizer(self, proto):
        vocab_scores = self.vocab(self.proto)
        merges = self.merges(self.proto)
        bpe_vocab = {word: i for i, (word, _score) in enumerate(vocab_scores)}
        unk_token = proto.tokens[proto.unk_token_id] if proto.unk_token_id is not None else None
        bos_token = proto.tokens[proto.bos_token_id] if getattr(proto, "bos_token_id", None) is not None else None
        eos_token = proto.tokens[proto.bos_token_id] if getattr(proto, "eos_token_id", None) is not None else None
        tokenizer = Tokenizer(BPE(bpe_vocab, merges, unk_token=unk_token, fuse_unk=True, byte_fallback=True))
        special_tokens = []
        if not hasattr(self.proto, "token_type"):
            if unk_token is not None: special_tokens.append(AddedToken(unk_token, normalized=False, special=True))
            if bos_token is not None: special_tokens.append(AddedToken(bos_token, normalized=False, special=True))
            if eos_token is not None: special_tokens.append(AddedToken(eos_token, normalized=False, special=True))
        else:
            special_tokens_idx = np.where(np.array(self.proto.token_type) == 3)[0]
            for idx in special_tokens_idx: special_tokens.append(AddedToken(self.proto.tokens[idx], normalized=False, special=True))
        if len(special_tokens) != 0: tokenizer.add_special_tokens(special_tokens)
        if len(self.proto.added_tokens) != 0: tokenizer.add_tokens([AddedToken(added_token, normalized=False, special=False) for added_token in self.proto.added_tokens])
        self.additional_kwargs["unk_token"] = unk_token
        self.additional_kwargs["eos_token"] = bos_token
        self.additional_kwargs["bos_token"] = eos_token
        if self.is_llama_3_tokenizer:
            self.additional_kwargs["add_prefix_space"] = None
            self.additional_kwargs["clean_up_tokenization_spaces"] = True
            self.additional_kwargs["legacy"] = False
            self.original_tokenizer.legacy = False
        return tokenizer
    def decoder(self, replacement, add_prefix_space):
        sequence = [decoders.ByteFallback(), decoders.Fuse(), decoders.Replace("▁", " ")]
        if self.is_llama_3_tokenizer: sequence += [decoders.ByteLevel(add_prefix_space=False, trim_offsets=False, use_regex=True)]
        if add_prefix_space: sequence += [decoders.Strip(content=" ", left=1)]
        return decoders.Sequence(sequence)
    def converted(self):
        tokenizer = self.tokenizer(self.proto)
        normalizer = self.normalizer(self.proto)
        if normalizer is not None: tokenizer.normalizer = normalizer
        replacement = "▁"
        add_prefix_space = True
        if hasattr(self.original_tokenizer, "add_prefix_space"): add_prefix_space = self.original_tokenizer.add_prefix_space
        pre_tokenizer = self.pre_tokenizer(replacement, add_prefix_space)
        if pre_tokenizer is not None: tokenizer.pre_tokenizer = pre_tokenizer
        tokenizer.decoder = self.decoder(replacement, add_prefix_space)
        post_processor = self.post_processor()
        if post_processor: tokenizer.post_processor = post_processor
        if self.is_llama_3_tokenizer:
            tokenizer.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False, trim_offsets=False, use_regex=True)
            tokenizer.normalizer = normalizers.Sequence([])
        return tokenizer
class GGUFQwen2Converter(Qwen2Converter):
    def __init__(self, tokenizer_dict):
        self.original_tokenizer = GGUFTokenizerSkeleton(tokenizer_dict)
        self.additional_kwargs = {}
    def converted(self) -> Tokenizer:
        vocab = {word: i for i, word in enumerate(self.original_tokenizer.tokens)}
        merges = self.original_tokenizer.merges
        tokenizer = super().converted(vocab, merges)
        tokenizer.add_special_tokens([AddedToken("<|endoftext|>", normalized=False, special=True), AddedToken("<|im_start|>", normalized=False, special=True), AddedToken("<|im_end|>", normalized=False, special=True)])
        return tokenizer
class GGUFPhi3Converter(LlamaConverter):
    def __init__(self, tokenizer_dict):
        self.proto = GGUFTokenizerSkeleton(tokenizer_dict)
        self.original_tokenizer = self.proto
        self.additional_kwargs = {}
    def vocab(self, proto): return list(zip(proto.tokens, proto.scores))
    def merges(self, proto): return proto.merges
    def tokenizer(self, proto):
        vocab_scores = self.vocab(self.proto)
        merges = self.merges(self.proto)
        bpe_vocab = {word: i for i, (word, _score) in enumerate(vocab_scores)}
        tokenizer = Tokenizer(BPE(bpe_vocab, merges))
        tokenizer.add_special_tokens([AddedToken("</s>", rstrip=True, lstrip=False, normalized=False, special=True), AddedToken("<|endoftext|>", normalized=False, special=True), AddedToken("<|assistant|>", rstrip=True,
        normalized=False, special=True), AddedToken("<|placeholder1|>", rstrip=True, normalized=False, special=True), AddedToken("<|placeholder2|>", rstrip=True, normalized=False, special=True), AddedToken("<|placeholder3|>",
        rstrip=True, normalized=False, special=True), AddedToken("<|placeholder4|>", rstrip=True, normalized=False, special=True), AddedToken("<|system|>", rstrip=True, normalized=False, special=True), AddedToken("<|end|>",
        rstrip=True, normalized=False, special=True), AddedToken("<|placeholder5|>", rstrip=True, normalized=False, special=True), AddedToken("<|placeholder6|>", rstrip=True, normalized=False, special=True), AddedToken("<|user|>",
        rstrip=True, normalized=False, special=True)])
        self.additional_kwargs["unk_token"] = (proto.tokens[proto.unk_token_id] if proto.unk_token_id is not None else None)
        self.additional_kwargs["eos_token"] = (proto.tokens[proto.eos_token_id] if proto.eos_token_id is not None else None)
        self.additional_kwargs["bos_token"] = (proto.tokens[proto.bos_token_id] if proto.bos_token_id is not None else None)
        self.additional_kwargs["pad_token"] = (proto.tokens[proto.pad_token_id] if proto.pad_token_id is not None else None)
        return tokenizer
    def decoder(self, replacement, add_prefix_space):
        sequence = [decoders.ByteFallback(), decoders.Fuse(), decoders.Replace(replacement, " ")]
        if add_prefix_space: sequence += [decoders.Strip(content=" ", left=1)]
        return decoders.Sequence(sequence)
    def converted(self) -> Tokenizer:
        tokenizer = self.tokenizer(self.proto)
        replacement = "▁"
        add_prefix_space = True
        if hasattr(self.original_tokenizer, "add_prefix_space"): add_prefix_space = self.original_tokenizer.add_prefix_space
        tokenizer.decoder = self.decoder(replacement, add_prefix_space)
        return tokenizer
class GGUFSapamaConverter(SapamaConverter):
    def __init__(self, tokenizer_dict):
        self.proto = GGUFTokenizerSkeleton(tokenizer_dict)
        self.original_tokenizer = self.proto
        self.additional_kwargs = {}
        self.is_sapama_tokenizer = getattr(self.proto, "tokenizer_type", "sapama") != "sapama"
    def vocab(self, proto): return list(zip(proto.tokens, proto.scores))
    def merges(self, proto): return proto.merges
    def tokenizer(self, proto):
        vocab_scores = self.vocab(self.proto)
        merges = self.merges(self.proto)
        bpe_vocab = {word: i for i, (word, _score) in enumerate(vocab_scores)}
        unk_token = proto.tokens[proto.unk_token_id] if proto.unk_token_id is not None else None
        bos_token = proto.tokens[proto.bos_token_id] if getattr(proto, "bos_token_id", None) is not None else None
        eos_token = proto.tokens[proto.bos_token_id] if getattr(proto, "eos_token_id", None) is not None else None
        tokenizer = Tokenizer(BPE(bpe_vocab, merges, unk_token=unk_token, fuse_unk=True, byte_fallback=True))
        special_tokens = []
        if not hasattr(self.proto, "token_type"):
            if unk_token is not None: special_tokens.append(AddedToken(unk_token, normalized=False, special=True))
            if bos_token is not None: special_tokens.append(AddedToken(bos_token, normalized=False, special=True))
            if eos_token is not None: special_tokens.append(AddedToken(eos_token, normalized=False, special=True))
        else:
            special_tokens_idx = np.where(np.array(self.proto.token_type) == 3)[0]
            for idx in special_tokens_idx: special_tokens.append(AddedToken(self.proto.tokens[idx], normalized=False, special=True))
        if len(special_tokens) != 0: tokenizer.add_special_tokens(special_tokens)
        if len(self.proto.added_tokens) != 0: tokenizer.add_tokens([AddedToken(added_token, normalized=False, special=False) for added_token in self.proto.added_tokens])
        self.additional_kwargs["unk_token"] = unk_token
        self.additional_kwargs["eos_token"] = bos_token
        self.additional_kwargs["bos_token"] = eos_token
        if self.is_sapama_tokenizer:
            self.additional_kwargs["add_prefix_space"] = None
            self.additional_kwargs["clean_up_tokenization_spaces"] = True
            self.additional_kwargs["legacy"] = False
            self.original_tokenizer.legacy = False
        return tokenizer
    def decoder(self, replacement, add_prefix_space):
        sequence = [decoders.ByteFallback(), decoders.Fuse(), decoders.Replace("▁", " ")]
        if self.is_sapama_tokenizer: sequence += [decoders.ByteLevel(add_prefix_space=False, trim_offsets=False, use_regex=True)]
        if add_prefix_space: sequence += [decoders.Strip(content=" ", left=1)]
        return decoders.Sequence(sequence)
    def converted(self):
        tokenizer = self.tokenizer(self.proto)
        normalizer = self.normalizer(self.proto)
        if normalizer is not None: tokenizer.normalizer = normalizer
        replacement = "▁"
        add_prefix_space = True
        if hasattr(self.original_tokenizer, "add_prefix_space"): add_prefix_space = self.original_tokenizer.add_prefix_space
        pre_tokenizer = self.pre_tokenizer(replacement, add_prefix_space)
        if pre_tokenizer is not None: tokenizer.pre_tokenizer = pre_tokenizer
        tokenizer.decoder = self.decoder(replacement, add_prefix_space)
        post_processor = self.post_processor()
        if post_processor: tokenizer.post_processor = post_processor
        if self.is_sapama_tokenizer:
            tokenizer.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False, trim_offsets=False, use_regex=True)
            tokenizer.normalizer = normalizers.Sequence([])
        return tokenizer
class GGUFSapiensConverter(SapiensConverter):
    def __init__(self, tokenizer_dict):
        self.original_tokenizer = GGUFTokenizerSkeleton(tokenizer_dict)
        self.additional_kwargs = {}
    def converted(self) -> Tokenizer:
        vocab = {word: i for i, word in enumerate(self.original_tokenizer.tokens)}
        merges = self.original_tokenizer.merges
        tokenizer = super().converted(vocab, merges)
        tokenizer.add_special_tokens([AddedToken("<|endoftext|>", normalized=False, special=True), AddedToken("<|im_start|>", normalized=False, special=True), AddedToken("<|im_end|>", normalized=False, special=True)])
        return tokenizer
GGUF_TO_FAST_CONVERTERS = {"entity": GGUFEntityConverter, "llama": GGUFLlamaConverter, "phi3": GGUFPhi3Converter, "qwen2": GGUFQwen2Converter, "qwen2_moe": GGUFQwen2Converter, "sapama": GGUFSapamaConverter, "sapiens": GGUFSapiensConverter}
def convert_gguf_tokenizer(architecture, tokenizer_dict) -> Tokenizer:
    tokenizer_class_name = architecture
    converter = GGUF_TO_FAST_CONVERTERS[tokenizer_class_name](tokenizer_dict)
    fast_tokenizer = converter.converted()
    return fast_tokenizer, converter.additional_kwargs
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
