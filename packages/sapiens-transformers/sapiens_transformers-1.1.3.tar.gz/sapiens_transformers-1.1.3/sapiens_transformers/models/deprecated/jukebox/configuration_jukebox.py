"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import os
from typing import List, Union
from ....configuration_utils import PretrainedConfig
from ....utils import logging
logger = logging.get_logger(__name__)
_LARGE_ATTENTION = ["block_attn", "transpose_block_attn", "prev_block_attn", "block_attn", "transpose_block_attn", "prev_block_attn", "block_attn", "transpose_block_attn",
"prev_block_attn", "block_attn", "transpose_block_attn", "prev_block_attn", "block_attn", "transpose_block_attn", "prev_block_attn", "block_attn", "transpose_block_attn",
"prev_block_attn", "cross_attention", "block_attn", "transpose_block_attn", "prev_block_attn", "block_attn", "transpose_block_attn", "prev_block_attn", "block_attn",
"transpose_block_attn", "prev_block_attn", "cross_attention", "block_attn", "transpose_block_attn", "prev_block_attn", "block_attn", "transpose_block_attn", "prev_block_attn",
"block_attn", "transpose_block_attn", "prev_block_attn", "cross_attention", "block_attn", "transpose_block_attn", "prev_block_attn", "block_attn", "transpose_block_attn",
"prev_block_attn", "block_attn", "transpose_block_attn", "prev_block_attn", "cross_attention", "block_attn", "transpose_block_attn", "prev_block_attn", "block_attn",
"transpose_block_attn", "prev_block_attn", "block_attn", "transpose_block_attn", "prev_block_attn", "cross_attention", "block_attn", "transpose_block_attn", "prev_block_attn",
"block_attn", "transpose_block_attn", "prev_block_attn", "block_attn", "transpose_block_attn", "prev_block_attn", "cross_attention", "block_attn", "transpose_block_attn",
"prev_block_attn", "block_attn", "transpose_block_attn", "prev_block_attn", "block_attn", "transpose_block_attn", "prev_block_attn", "cross_attention"]
_RawColumnPreviousRowAttention = ["block_attn", "transpose_block_attn", "prev_block_attn"]
_FullDenseAttention = ["dense_attention"]
_PrimePrimeDenseAttention = ["prime_attn", "prime_attn", "dense_attn"]
def full_dense_attention(layer): return _FullDenseAttention[0]
def raw_column_previous_row_attention(layer): return _RawColumnPreviousRowAttention[layer % 3]
def large_separated_enc_dec_w_lyrics(layer): return _LARGE_ATTENTION[layer % 79]
def enc_dec_with_lyrics(layer):
    if layer % 16 == 15: return _PrimePrimeDenseAttention[layer % 3]
    return _RawColumnPreviousRowAttention[layer % 3]
ATTENTION_PATTERNS = {"full_dense_attention": full_dense_attention, "raw_column_previous_row_attention": raw_column_previous_row_attention,
"large_separated_enc_dec_w_lyrics": large_separated_enc_dec_w_lyrics, "enc_dec_with_lyrics": enc_dec_with_lyrics}
class JukeboxPriorConfig(PretrainedConfig):
    model_type = "jukebox_prior"
    attribute_map = {'max_position_embeddings': 'n_positions', 'num_attention_heads': 'n_head'}
    def __init__(self, act_fn="quick_gelu", level=0, alignment_head=2, alignment_layer=68, attention_multiplier=0.25, attention_pattern="enc_dec_with_lyrics", attn_dropout=0,
    attn_res_scale=False, blocks=64, conv_res_scale=None, num_layers=72, emb_dropout=0, encoder_config=None, encoder_loss_fraction=0.4, hidden_size=2048, init_scale=0.2,
    is_encoder_decoder=True, lyric_vocab_size=80, mask=False, max_duration=600, max_nb_genres=1, merged_decoder=True, metadata_conditioning=True, metadata_dims=[604, 7898],
    min_duration=0, mlp_multiplier=1.0, music_vocab_size=2048, n_ctx=6144, n_heads=2, nb_relevant_lyric_tokens=384, res_conv_depth=3, res_conv_width=128, res_convolution_multiplier=1,
    res_dilation_cycle=None, res_dilation_growth_rate=1, res_downs_t=[3, 2, 2], res_strides_t=[2, 2, 2], resid_dropout=0, sampling_rate=44100, spread=None, timing_dims=64, zero_out=False, **kwargs):
        self.act_fn = act_fn
        self.alignment_head = alignment_head
        self.alignment_layer = alignment_layer
        self.attention_multiplier = attention_multiplier
        self.attention_pattern = attention_pattern
        self.attn_dropout = attn_dropout
        self.attn_res_scale = attn_res_scale
        self.blocks = blocks
        self.conv_res_scale = conv_res_scale
        self.num_layers = num_layers
        self.emb_dropout = emb_dropout
        self.music_vocab_size = music_vocab_size
        if encoder_config is not None: self.encoder_config = JukeboxPriorConfig(**encoder_config)
        else: self.encoder_config = None
        self.encoder_loss_fraction = encoder_loss_fraction
        self.init_scale = init_scale
        self.is_encoder_decoder = is_encoder_decoder
        self.lyric_vocab_size = lyric_vocab_size
        self.level = level
        self.mask = mask
        self.max_duration = max_duration
        self.max_nb_genres = max_nb_genres
        self.merged_decoder = merged_decoder
        self.metadata_conditioning = metadata_conditioning
        self.metadata_dims = metadata_dims
        self.min_duration = min_duration
        self.mlp_multiplier = mlp_multiplier
        self.n_ctx = n_ctx
        self.n_heads = n_heads
        self.nb_relevant_lyric_tokens = nb_relevant_lyric_tokens
        self.res_conv_depth = res_conv_depth
        self.res_conv_width = res_conv_width
        self.res_convolution_multiplier = res_convolution_multiplier
        self.res_dilation_cycle = res_dilation_cycle
        self.res_dilation_growth_rate = res_dilation_growth_rate
        self.res_downs_t = res_downs_t
        self.res_strides_t = res_strides_t
        self.resid_dropout = resid_dropout
        self.sampling_rate = sampling_rate
        self.spread = spread
        self.timing_dims = timing_dims
        self.hidden_size = hidden_size
        self.zero_out = zero_out
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path: Union[str, os.PathLike], level=0, **kwargs) -> "PretrainedConfig":
        cls._set_token_in_kwargs(kwargs)
        config_dict, kwargs = cls.get_config_dict(pretrained_model_name_or_path, **kwargs)
        if config_dict.get("model_type") == "jukebox": config_dict = config_dict[f"prior_{level}"]
        if "model_type" in config_dict and hasattr(cls, "model_type") and config_dict["model_type"] != cls.model_type: logger.warning(f"You are using a model of type {config_dict['model_type']} to instantiate a model of type {cls.model_type}. This is not supported for all configurations of models and can yield errors.")
        return cls.from_dict(config_dict, **kwargs)
class JukeboxVQVAEConfig(PretrainedConfig):
    model_type = "jukebox_vqvae"
    def __init__(self, act_fn="relu", nb_discrete_codes=2048, commit=0.02, conv_input_shape=1, conv_res_scale=False, embed_dim=64, hop_fraction=[0.125, 0.5, 0.5], levels=3,
    lmu=0.99, multipliers=[2, 1, 1], res_conv_depth=4, res_conv_width=32, res_convolution_multiplier=1, res_dilation_cycle=None, res_dilation_growth_rate=3, res_downs_t=[3, 2, 2],
    res_strides_t=[2, 2, 2], sample_length=1058304, init_scale=0.2, zero_out=False, **kwargs):
        self.hop_fraction = hop_fraction
        self.conv_input_shape = conv_input_shape
        self.sample_length = sample_length
        self.levels = levels
        self.embed_dim = embed_dim
        self.nb_discrete_codes = nb_discrete_codes
        self.res_conv_width = res_conv_width
        self.res_conv_depth = res_conv_depth
        self.res_convolution_multiplier = res_convolution_multiplier
        self.res_dilation_growth_rate = res_dilation_growth_rate
        self.res_dilation_cycle = res_dilation_cycle
        self.multipliers = multipliers
        self.res_downs_t = res_downs_t
        self.res_strides_t = res_strides_t
        self.lmu = lmu
        self.commit = commit
        self.conv_res_scale = conv_res_scale
        self.act_fn = act_fn
        self.init_scale = init_scale
        self.zero_out = zero_out
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path: Union[str, os.PathLike], **kwargs) -> "PretrainedConfig":
        cls._set_token_in_kwargs(kwargs)
        config_dict, kwargs = cls.get_config_dict(pretrained_model_name_or_path, **kwargs)
        if config_dict.get("model_type") == "jukebox": config_dict = config_dict["vqvae_config"]
        if "model_type" in config_dict and hasattr(cls, "model_type") and config_dict["model_type"] != cls.model_type: logger.warning(f"You are using a model of type {config_dict['model_type']} to instantiate a model of type {cls.model_type}. This is not supported for all configurations of models and can yield errors.")
        return cls.from_dict(config_dict, **kwargs)
class JukeboxConfig(PretrainedConfig):
    model_type = "jukebox"
    def __init__(self, vqvae_config=None, prior_config_list=None, nb_priors=3, sampling_rate=44100, timing_dims=64, min_duration=0, max_duration=600.0, max_nb_genres=5, metadata_conditioning=True, **kwargs):
        if vqvae_config is None:
            vqvae_config = {}
            logger.info("vqvae_config is None. initializing the JukeboxVQVAE with default values.")
        self.vqvae_config = JukeboxVQVAEConfig(**vqvae_config)
        if prior_config_list is not None: self.prior_configs = [JukeboxPriorConfig(**prior_config) for prior_config in prior_config_list]
        else:
            self.prior_configs = []
            for prior_idx in range(nb_priors):
                prior_config = kwargs.pop(f"prior_{prior_idx}", None)
                if prior_config is None:
                    prior_config = {}
                    logger.info(f"prior_{prior_idx}'s  config is None. Initializing the JukeboxPriorConfig list with default values.")
                self.prior_configs.append(JukeboxPriorConfig(**prior_config))
        self.hop_fraction = self.vqvae_config.hop_fraction
        self.nb_priors = nb_priors
        self.max_nb_genres = max_nb_genres
        self.sampling_rate = sampling_rate
        self.timing_dims = timing_dims
        self.min_duration = min_duration
        self.max_duration = max_duration
        self.metadata_conditioning = metadata_conditioning
        super().__init__(**kwargs)
    @classmethod
    def from_configs(cls, prior_configs: List[JukeboxPriorConfig], vqvae_config: JukeboxVQVAEConfig, **kwargs):
        prior_config_list = [config.to_dict() for config in prior_configs]
        return cls(prior_config_list=prior_config_list, vqvae_config_dict=vqvae_config.to_dict(), **kwargs)
    def to_dict(self):
        result = super().to_dict()
        result["prior_config_list"] = [config.to_dict() for config in result.pop("prior_configs")]
        return result
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
