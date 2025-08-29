"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from dataclasses import asdict, dataclass
from typing import Optional
from ...configuration_utils import PretrainedConfig
from ...utils import logging
logger = logging.get_logger(__name__)
class EsmConfig(PretrainedConfig):
    model_type = "esm"
    def __init__(self, vocab_size=None, mask_token_id=None, pad_token_id=None, hidden_size=768, num_hidden_layers=12, num_attention_heads=12, intermediate_size=3072,
    hidden_dropout_prob=0.1, attention_probs_dropout_prob=0.1, max_position_embeddings=1026, initializer_range=0.02, layer_norm_eps=1e-12, position_embedding_type="absolute",
    use_cache=True, emb_layer_norm_before=None, token_dropout=False, is_folding_model=False, esmfold_config=None, vocab_list=None, **kwargs):
        super().__init__(pad_token_id=pad_token_id, mask_token_id=mask_token_id, **kwargs)
        self.vocab_size = vocab_size
        self.hidden_size = hidden_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.intermediate_size = intermediate_size
        self.hidden_dropout_prob = hidden_dropout_prob
        self.attention_probs_dropout_prob = attention_probs_dropout_prob
        self.max_position_embeddings = max_position_embeddings
        self.initializer_range = initializer_range
        self.layer_norm_eps = layer_norm_eps
        self.position_embedding_type = position_embedding_type
        self.use_cache = use_cache
        self.emb_layer_norm_before = emb_layer_norm_before
        self.token_dropout = token_dropout
        self.is_folding_model = is_folding_model
        if is_folding_model:
            if esmfold_config is None:
                logger.info("No esmfold_config supplied for folding model, using default values.")
                esmfold_config = EsmFoldConfig()
            elif isinstance(esmfold_config, dict): esmfold_config = EsmFoldConfig(**esmfold_config)
            self.esmfold_config = esmfold_config
            if vocab_list is None:
                logger.warning("No vocab_list supplied for folding model, assuming the ESM-2 vocabulary!")
                self.vocab_list = get_default_vocab_list()
            else: self.vocab_list = vocab_list
        else:
            self.esmfold_config = None
            self.vocab_list = None
        if self.esmfold_config is not None and getattr(self.esmfold_config, "use_esm_attn_map", False): raise ValueError("The port of ESMFold does not support use_esm_attn_map at this time!")
    def to_dict(self):
        output = super().to_dict()
        if isinstance(self.esmfold_config, EsmFoldConfig): output["esmfold_config"] = self.esmfold_config.to_dict()
        return output
@dataclass
class EsmFoldConfig:
    esm_type: str = None
    fp16_esm: bool = True
    use_esm_attn_map: bool = False
    esm_ablate_pairwise: bool = False
    esm_ablate_sequence: bool = False
    esm_input_dropout: float = 0
    embed_aa: bool = True
    bypass_lm: bool = False
    lddt_head_hid_dim: int = 128
    trunk: "TrunkConfig" = None
    def __post_init__(self):
        if self.trunk is None: self.trunk = TrunkConfig()
        elif isinstance(self.trunk, dict): self.trunk = TrunkConfig(**self.trunk)
    def to_dict(self):
        output = asdict(self)
        output["trunk"] = self.trunk.to_dict()
        return output
@dataclass
class TrunkConfig:
    num_blocks: int = 48
    sequence_state_dim: int = 1024
    pairwise_state_dim: int = 128
    sequence_head_width: int = 32
    pairwise_head_width: int = 32
    position_bins: int = 32
    dropout: float = 0
    layer_drop: float = 0
    cpu_grad_checkpoint: bool = False
    max_recycles: int = 4
    chunk_size: Optional[int] = 128
    structure_module: "StructureModuleConfig" = None
    def __post_init__(self):
        if self.structure_module is None: self.structure_module = StructureModuleConfig()
        elif isinstance(self.structure_module, dict): self.structure_module = StructureModuleConfig(**self.structure_module)
        if self.max_recycles <= 0: raise ValueError(f"`max_recycles` should be positive, got {self.max_recycles}.")
        if self.sequence_state_dim % self.sequence_state_dim != 0: raise ValueError(f"`sequence_state_dim` should be a round multiple of `sequence_state_dim`, got {self.sequence_state_dim} and {self.sequence_state_dim}.")
        if self.pairwise_state_dim % self.pairwise_state_dim != 0: raise ValueError(f"`pairwise_state_dim` should be a round multiple of `pairwise_state_dim`, got {self.pairwise_state_dim} and {self.pairwise_state_dim}.")
        sequence_num_heads = self.sequence_state_dim // self.sequence_head_width
        pairwise_num_heads = self.pairwise_state_dim // self.pairwise_head_width
        if self.sequence_state_dim != sequence_num_heads * self.sequence_head_width: raise ValueError(f"`sequence_state_dim` should be equal to `sequence_num_heads * sequence_head_width, got {self.sequence_state_dim} != {sequence_num_heads} * {self.sequence_head_width}.")
        if self.pairwise_state_dim != pairwise_num_heads * self.pairwise_head_width: raise ValueError(f"`pairwise_state_dim` should be equal to `pairwise_num_heads * pairwise_head_width, got {self.pairwise_state_dim} != {pairwise_num_heads} * {self.pairwise_head_width}.")
        if self.pairwise_state_dim % 2 != 0: raise ValueError(f"`pairwise_state_dim` should be even, got {self.pairwise_state_dim}.")
        if self.dropout >= 0.4: raise ValueError(f"`dropout` should not be greater than 0.4, got {self.dropout}.")
    def to_dict(self):
        output = asdict(self)
        output["structure_module"] = self.structure_module.to_dict()
        return output
@dataclass
class StructureModuleConfig:
    sequence_dim: int = 384
    pairwise_dim: int = 128
    ipa_dim: int = 16
    resnet_dim: int = 128
    num_heads_ipa: int = 12
    num_qk_points: int = 4
    num_v_points: int = 8
    dropout_rate: float = 0.1
    num_blocks: int = 8
    num_transition_layers: int = 1
    num_resnet_blocks: int = 2
    num_angles: int = 7
    trans_scale_factor: int = 10
    epsilon: float = 1e-8
    inf: float = 1e5
    def to_dict(self): return asdict(self)
def get_default_vocab_list():
    return ("<cls>", "<pad>", "<eos>", "<unk>", "L", "A", "G", "V", "S", "E", "R", "T", "I", "D", "P", "K", "Q", "N", "F", "Y", "M", "H", "W", "C",
    "X", "B", "U", "Z", "O", ".", "-", "<null_1>", "<mask>")
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
