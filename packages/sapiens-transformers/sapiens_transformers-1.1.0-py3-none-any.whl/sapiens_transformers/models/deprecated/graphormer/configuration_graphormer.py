"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ....configuration_utils import PretrainedConfig
from ....utils import logging
logger = logging.get_logger(__name__)
class GraphormerConfig(PretrainedConfig):
    model_type = "graphormer"
    keys_to_ignore_at_inference = ["past_key_values"]
    def __init__(self, num_classes: int = 1, num_atoms: int = 512 * 9, num_edges: int = 512 * 3, num_in_degree: int = 512, num_out_degree: int = 512,
    num_spatial: int = 512, num_edge_dis: int = 128, multi_hop_max_dist: int = 5, spatial_pos_max: int = 1024, edge_type: str = "multi_hop", max_nodes: int = 512,
    share_input_output_embed: bool = False, num_hidden_layers: int = 12, embedding_dim: int = 768, ffn_embedding_dim: int = 768, num_attention_heads: int = 32,
    dropout: float = 0.1, attention_dropout: float = 0.1, activation_dropout: float = 0.1, layerdrop: float = 0.0, encoder_normalize_before: bool = False,
    pre_layernorm: bool = False, apply_graphormer_init: bool = False, activation_fn: str = "gelu", embed_scale: float = None, freeze_embeddings: bool = False,
    num_trans_layers_to_freeze: int = 0, traceable: bool = False, q_noise: float = 0.0, qn_block_size: int = 8, kdim: int = None, vdim: int = None, bias: bool = True,
    self_attention: bool = True, pad_token_id=0, bos_token_id=1, eos_token_id=2, **kwargs):
        self.num_classes = num_classes
        self.num_atoms = num_atoms
        self.num_in_degree = num_in_degree
        self.num_out_degree = num_out_degree
        self.num_edges = num_edges
        self.num_spatial = num_spatial
        self.num_edge_dis = num_edge_dis
        self.edge_type = edge_type
        self.multi_hop_max_dist = multi_hop_max_dist
        self.spatial_pos_max = spatial_pos_max
        self.max_nodes = max_nodes
        self.num_hidden_layers = num_hidden_layers
        self.embedding_dim = embedding_dim
        self.hidden_size = embedding_dim
        self.ffn_embedding_dim = ffn_embedding_dim
        self.num_attention_heads = num_attention_heads
        self.dropout = dropout
        self.attention_dropout = attention_dropout
        self.activation_dropout = activation_dropout
        self.layerdrop = layerdrop
        self.encoder_normalize_before = encoder_normalize_before
        self.pre_layernorm = pre_layernorm
        self.apply_graphormer_init = apply_graphormer_init
        self.activation_fn = activation_fn
        self.embed_scale = embed_scale
        self.freeze_embeddings = freeze_embeddings
        self.num_trans_layers_to_freeze = num_trans_layers_to_freeze
        self.share_input_output_embed = share_input_output_embed
        self.traceable = traceable
        self.q_noise = q_noise
        self.qn_block_size = qn_block_size
        self.kdim = kdim
        self.vdim = vdim
        self.self_attention = self_attention
        self.bias = bias
        super().__init__(pad_token_id=pad_token_id, bos_token_id=bos_token_id, eos_token_id=eos_token_id, **kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
