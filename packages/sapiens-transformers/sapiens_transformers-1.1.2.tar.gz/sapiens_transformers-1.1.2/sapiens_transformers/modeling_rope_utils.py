"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from .configuration_utils import PretrainedConfig
from .utils import is_torch_available, logging
from typing import Optional, Tuple
import math
logger = logging.get_logger(__name__)
if is_torch_available(): import torch
def _compute_default_rope_parameters(config: Optional[PretrainedConfig] = None, device: Optional["torch.device"] = None, seq_len: Optional[int] = None, **rope_kwargs) -> Tuple["torch.Tensor", float]:
    if config is not None and len(rope_kwargs) > 0: raise ValueError(f"Unexpected arguments: `**rope_kwargs` and `config` are mutually exclusive in `_compute_default_rope_parameters`, got `rope_kwargs`={rope_kwargs} and `config`={config}")
    if len(rope_kwargs) > 0:
        base = rope_kwargs["base"]
        dim = rope_kwargs["dim"]
    elif config is not None:
        base = config.rope_theta
        partial_rotary_factor = config.partial_rotary_factor if hasattr(config, "partial_rotary_factor") else 1.0
        head_dim = getattr(config, "head_dim", config.hidden_size // config.num_attention_heads)
        dim = int(head_dim * partial_rotary_factor)
    attention_factor = 1.0
    inv_freq = 1.0 / (base ** (torch.arange(0, dim, 2, dtype=torch.int64).float().to(device) / dim))
    return inv_freq, attention_factor
def _compute_dynamic_ntk_parameters(config: Optional[PretrainedConfig] = None, device: Optional["torch.device"] = None, seq_len: Optional[int] = None, **rope_kwargs) -> Tuple["torch.Tensor", float]:
    if config is not None and len(rope_kwargs) > 0: raise ValueError(f"Unexpected arguments: `**rope_kwargs` and `config` are mutually exclusive in `_compute_dynamic_ntk_parameters`, got `rope_kwargs`={rope_kwargs} and `config`={config}")
    if len(rope_kwargs) > 0:
        base = rope_kwargs["base"]
        dim = rope_kwargs["dim"]
        max_position_embeddings = rope_kwargs["max_position_embeddings"]
        factor = rope_kwargs["factor"]
    elif config is not None:
        base = config.rope_theta
        partial_rotary_factor = config.partial_rotary_factor if hasattr(config, "partial_rotary_factor") else 1.0
        head_dim = getattr(config, "head_dim", config.hidden_size // config.num_attention_heads)
        dim = int(head_dim * partial_rotary_factor)
        max_position_embeddings = config.max_position_embeddings
        factor = config.rope_scaling["factor"]
    attention_factor = 1.0
    seq_len = seq_len if seq_len is not None and seq_len > max_position_embeddings else max_position_embeddings
    base = base * ((factor * seq_len / max_position_embeddings) - (factor - 1)) ** (dim / (dim - 2))
    inv_freq = 1.0 / (base ** (torch.arange(0, dim, 2, dtype=torch.int64).float().to(device) / dim))
    return inv_freq, attention_factor
def _compute_entity_parameters(config: PretrainedConfig, device: "torch.device", seq_len: Optional[int] = None, **rope_kwargs) -> Tuple["torch.Tensor", float]:
    inv_freq, attention_factor = _compute_default_rope_parameters(config, device, seq_len, **rope_kwargs)
    factor, low_freq_factor = config.rope_scaling["factor"], config.rope_scaling["low_freq_factor"]
    high_freq_factor, old_context_len = config.rope_scaling["high_freq_factor"], config.rope_scaling["original_max_position_embeddings"]
    low_freq_wavelen, high_freq_wavelen, wavelen = old_context_len / low_freq_factor, old_context_len / high_freq_factor, 2 * math.pi / inv_freq
    inv_freq_entity = torch.where(wavelen > low_freq_wavelen, inv_freq / factor, inv_freq)
    smooth_factor = (old_context_len / wavelen - low_freq_factor) / (high_freq_factor - low_freq_factor)
    smoothed_inv_freq = (1 - smooth_factor) * inv_freq_entity / factor + smooth_factor * inv_freq_entity
    is_medium_freq = ~(wavelen < high_freq_wavelen) * ~(wavelen > low_freq_wavelen)
    inv_freq_entity = torch.where(is_medium_freq, smoothed_inv_freq, inv_freq_entity)
    return inv_freq_entity, attention_factor
def _compute_llama3_parameters(config: PretrainedConfig, device: "torch.device", seq_len: Optional[int] = None, **rope_kwargs) -> Tuple["torch.Tensor", float]:
    inv_freq, attention_factor = _compute_default_rope_parameters(config, device, seq_len, **rope_kwargs)
    factor = config.rope_scaling["factor"]
    low_freq_factor = config.rope_scaling["low_freq_factor"]
    high_freq_factor = config.rope_scaling["high_freq_factor"]
    old_context_len = config.rope_scaling["original_max_position_embeddings"]
    low_freq_wavelen = old_context_len / low_freq_factor
    high_freq_wavelen = old_context_len / high_freq_factor
    wavelen = 2 * math.pi / inv_freq
    inv_freq_llama = torch.where(wavelen > low_freq_wavelen, inv_freq / factor, inv_freq)
    smooth_factor = (old_context_len / wavelen - low_freq_factor) / (high_freq_factor - low_freq_factor)
    smoothed_inv_freq = (1 - smooth_factor) * inv_freq_llama / factor + smooth_factor * inv_freq_llama
    is_medium_freq = ~(wavelen < high_freq_wavelen) * ~(wavelen > low_freq_wavelen)
    inv_freq_llama = torch.where(is_medium_freq, smoothed_inv_freq, inv_freq_llama)
    return inv_freq_llama, attention_factor
def _compute_longrope_parameters(config: PretrainedConfig, device: "torch.device", seq_len: Optional[int] = None, **rope_kwargs) -> Tuple["torch.Tensor", float]:
    if len(rope_kwargs) > 0: raise ValueError(f"Unexpected arguments: `**rope_kwargs` should be unset in `_compute_longrope_parameters`, got {rope_kwargs}")
    base = config.rope_theta
    partial_rotary_factor = config.partial_rotary_factor if hasattr(config, "partial_rotary_factor") else 1.0
    head_dim = getattr(config, "head_dim", config.hidden_size // config.num_attention_heads)
    dim = int(head_dim * partial_rotary_factor)
    long_factor = config.rope_scaling["long_factor"]
    short_factor = config.rope_scaling["short_factor"]
    factor = config.rope_scaling.get("factor")
    attention_factor = config.rope_scaling.get("attention_factor")
    if hasattr(config, "original_max_position_embeddings"):
        max_position_embeddings = config.original_max_position_embeddings
        expanded_max_position_embeddings = config.max_position_embeddings
        factor = expanded_max_position_embeddings / max_position_embeddings
    else:
        max_position_embeddings = config.max_position_embeddings
        expanded_max_position_embeddings = max_position_embeddings * factor
    if attention_factor is None:
        if factor <= 1.0: attention_factor = 1.0
        else: attention_factor = math.sqrt(1 + math.log(factor) / math.log(max_position_embeddings))
    if expanded_max_position_embeddings > max_position_embeddings: ext_factors = torch.tensor(long_factor, dtype=torch.float32, device=device)
    else: ext_factors = torch.tensor(short_factor, dtype=torch.float32, device=device)
    inv_freq_shape = torch.arange(0, dim, 2, dtype=torch.int64, device=device).float() / dim
    inv_freq = 1.0 / (ext_factors * base**inv_freq_shape)
    return inv_freq, attention_factor
def _compute_linear_scaling_rope_parameters(config: Optional[PretrainedConfig] = None, device: Optional["torch.device"] = None, seq_len: Optional[int] = None, **rope_kwargs) -> Tuple["torch.Tensor", float]:
    if config is not None and len(rope_kwargs) > 0: raise ValueError(f"Unexpected arguments: `**rope_kwargs` and `config` are mutually exclusive in `_compute_linear_scaling_rope_parameters`, got `rope_kwargs`={rope_kwargs} and `config`={config}")
    if len(rope_kwargs) > 0: factor = rope_kwargs["factor"]
    elif config is not None: factor = config.rope_scaling["factor"]
    inv_freq, attention_factor = _compute_default_rope_parameters(config, device, seq_len, **rope_kwargs)
    inv_freq /= factor
    return inv_freq, attention_factor
def _compute_sapama_parameters(config: PretrainedConfig, device: "torch.device", seq_len: Optional[int] = None, **rope_kwargs) -> Tuple["torch.Tensor", float]:
    inv_freq, attention_factor = _compute_default_rope_parameters(config, device, seq_len, **rope_kwargs)
    factor = config.rope_scaling["factor"]
    low_freq_factor = config.rope_scaling["low_freq_factor"]
    high_freq_factor = config.rope_scaling["high_freq_factor"]
    old_context_len = config.rope_scaling["original_max_position_embeddings"]
    low_freq_wavelen = old_context_len / low_freq_factor
    high_freq_wavelen = old_context_len / high_freq_factor
    wavelen = 2 * math.pi / inv_freq
    inv_freq_sapama = torch.where(wavelen > low_freq_wavelen, inv_freq / factor, inv_freq)
    smooth_factor = (old_context_len / wavelen - low_freq_factor) / (high_freq_factor - low_freq_factor)
    smoothed_inv_freq = (1 - smooth_factor) * inv_freq_sapama / factor + smooth_factor * inv_freq_sapama
    is_medium_freq = ~(wavelen < high_freq_wavelen) * ~(wavelen > low_freq_wavelen)
    inv_freq_sapama = torch.where(is_medium_freq, smoothed_inv_freq, inv_freq_sapama)
    return inv_freq_sapama, attention_factor
def _compute_yarn_parameters(config: PretrainedConfig, device: "torch.device", seq_len: Optional[int] = None, **rope_kwargs) -> Tuple["torch.Tensor", float]:
    if len(rope_kwargs) > 0: raise ValueError(f"Unexpected arguments: `**rope_kwargs` should be unset in `_compute_yarn_parameters`, got {rope_kwargs}")
    base = config.rope_theta
    partial_rotary_factor = config.partial_rotary_factor if hasattr(config, "partial_rotary_factor") else 1.0
    head_dim = getattr(config, "head_dim", config.hidden_size // config.num_attention_heads)
    dim = int(head_dim * partial_rotary_factor)
    max_position_embeddings = config.max_position_embeddings
    factor = config.rope_scaling["factor"]
    attention_factor = config.rope_scaling.get("attention_factor")
    if attention_factor is None: attention_factor = 0.1 * math.log(factor) + 1.0
    beta_fast = config.rope_scaling.get("beta_fast") or 32
    beta_slow = config.rope_scaling.get("beta_slow") or 1
    def find_correction_dim(num_rotations, dim, base, max_position_embeddings): return (dim * math.log(max_position_embeddings / (num_rotations * 2 * math.pi))) / (2 * math.log(base))
    def find_correction_range(low_rot, high_rot, dim, base, max_position_embeddings):
        low = math.floor(find_correction_dim(low_rot, dim, base, max_position_embeddings))
        high = math.ceil(find_correction_dim(high_rot, dim, base, max_position_embeddings))
        return max(low, 0), min(high, dim - 1)
    def linear_ramp_factor(min, max, dim):
        if min == max: max += 0.001
        linear_func = (torch.arange(dim, dtype=torch.float32) - min) / (max - min)
        ramp_func = torch.clamp(linear_func, 0, 1)
        return ramp_func
    pos_freqs = base ** (torch.arange(0, dim, 2).float().to(device) / dim)
    inv_freq_extrapolation = 1.0 / pos_freqs
    inv_freq_interpolation = 1.0 / (factor * pos_freqs)
    low, high = find_correction_range(beta_fast, beta_slow, dim, base, max_position_embeddings)
    inv_freq_extrapolation_factor = 1 - linear_ramp_factor(low, high, dim // 2).float().to(device)
    inv_freq = (inv_freq_interpolation * (1 - inv_freq_extrapolation_factor) + inv_freq_extrapolation * inv_freq_extrapolation_factor)
    return inv_freq, attention_factor
ROPE_INIT_FUNCTIONS = {"default": _compute_default_rope_parameters, "dynamic": _compute_dynamic_ntk_parameters, "entity": _compute_entity_parameters, "linear": _compute_linear_scaling_rope_parameters, "llama3": _compute_llama3_parameters, "longrope": _compute_longrope_parameters, "sapama": _compute_sapama_parameters, "yarn": _compute_yarn_parameters}
def _check_received_keys(rope_type: str, received_keys: set, required_keys: set, optional_keys: Optional[set] = None, ignore_keys: Optional[set] = None):
    if "type" in received_keys:
        received_keys -= {"type"}
        required_keys.add("rope_type")
    if ignore_keys is not None: received_keys -= ignore_keys
    missing_keys = required_keys - received_keys
    if missing_keys: raise KeyError(f"Missing required keys in `rope_scaling` for 'rope_type'='{rope_type}': {missing_keys}")
    if optional_keys is not None: unused_keys = received_keys - required_keys - optional_keys
    else: unused_keys = received_keys - required_keys
    if unused_keys: logger.warning(f"Unrecognized keys in `rope_scaling` for 'rope_type'='{rope_type}': {unused_keys}")
def _validate_default_rope_parameters(config: PretrainedConfig, ignore_keys: Optional[set] = None):
    rope_scaling = config.rope_scaling
    rope_type = rope_scaling.get("rope_type", rope_scaling.get("type", None))
    required_keys = {"rope_type"}
    received_keys = set(rope_scaling.keys())
    _check_received_keys(rope_type, received_keys, required_keys, ignore_keys=ignore_keys)
def _validate_dynamic_scaling_rope_parameters(config: PretrainedConfig, ignore_keys: Optional[set] = None):
    rope_scaling = config.rope_scaling
    rope_type = rope_scaling.get("rope_type", rope_scaling.get("type", None))
    required_keys = {"rope_type", "factor"}
    optional_keys = {"original_max_position_embeddings"}
    received_keys = set(rope_scaling.keys())
    _check_received_keys(rope_type, received_keys, required_keys, optional_keys, ignore_keys=ignore_keys)
    factor = rope_scaling["factor"]
    if factor is None or not isinstance(factor, float) or factor < 1.0: logger.warning(f"`rope_scaling`'s factor field must be a float >= 1, got {factor}")
def _validate_entity_parameters(config: PretrainedConfig, ignore_keys: Optional[set] = None):
    rope_scaling = config.rope_scaling
    rope_type = rope_scaling.get("rope_type", rope_scaling.get("type", None))
    required_keys, received_keys = {"rope_type", "factor", "original_max_position_embeddings", "low_freq_factor", "high_freq_factor"}, set(rope_scaling.keys())
    _check_received_keys(rope_type, received_keys, required_keys, ignore_keys=ignore_keys)
    factor = rope_scaling["factor"]
    if factor is None or not isinstance(factor, float) or factor < 1.0: logger.warning(f"`rope_scaling`'s factor field must be a float >= 1, got {factor}")
    low_freq_factor = rope_scaling["low_freq_factor"]
    high_freq_factor = rope_scaling["high_freq_factor"]
    if low_freq_factor is None or not isinstance(low_freq_factor, float): logger.warning(f"`rope_scaling`'s low_freq_factor field must be a float, got {low_freq_factor}")
    if high_freq_factor is None or not isinstance(high_freq_factor, float): logger.warning(f"`rope_scaling`'s high_freq_factor field must be a float, got {high_freq_factor}")
    if high_freq_factor <= low_freq_factor: logger.warning(f"`rope_scaling`'s high_freq_factor field must be greater than low_freq_factor, got high_freq_factor={high_freq_factor} and low_freq_factor={low_freq_factor}")
    original_max_position_embeddings = rope_scaling["original_max_position_embeddings"]
    if original_max_position_embeddings is None or not isinstance(original_max_position_embeddings, int): logger.warning(f"`rope_scaling`'s original_max_position_embeddings field must be an integer, got {original_max_position_embeddings}")
    if original_max_position_embeddings >= config.max_position_embeddings: logger.warning(f"`rope_scaling`'s original_max_position_embeddings field must be less than max_position_embeddings, got {original_max_position_embeddings} and max_position_embeddings={config.max_position_embeddings}")
def _validate_linear_scaling_rope_parameters(config: PretrainedConfig, ignore_keys: Optional[set] = None):
    rope_scaling = config.rope_scaling
    rope_type = rope_scaling.get("rope_type", rope_scaling.get("type", None))
    required_keys = {"rope_type", "factor"}
    received_keys = set(rope_scaling.keys())
    _check_received_keys(rope_type, received_keys, required_keys, ignore_keys=ignore_keys)
    factor = rope_scaling["factor"]
    if factor is None or not isinstance(factor, float) or factor < 1.0: logger.warning(f"`rope_scaling`'s factor field must be a float >= 1, got {factor}")
def _validate_llama3_parameters(config: PretrainedConfig, ignore_keys: Optional[set] = None):
    rope_scaling = config.rope_scaling
    rope_type = rope_scaling.get("rope_type", rope_scaling.get("type", None))
    required_keys = {"rope_type", "factor", "original_max_position_embeddings", "low_freq_factor", "high_freq_factor"}
    received_keys = set(rope_scaling.keys())
    _check_received_keys(rope_type, received_keys, required_keys, ignore_keys=ignore_keys)
    factor = rope_scaling["factor"]
    if factor is None or not isinstance(factor, float) or factor < 1.0: logger.warning(f"`rope_scaling`'s factor field must be a float >= 1, got {factor}")
    low_freq_factor = rope_scaling["low_freq_factor"]
    high_freq_factor = rope_scaling["high_freq_factor"]
    if low_freq_factor is None or not isinstance(low_freq_factor, float): logger.warning(f"`rope_scaling`'s low_freq_factor field must be a float, got {low_freq_factor}")
    if high_freq_factor is None or not isinstance(high_freq_factor, float): logger.warning(f"`rope_scaling`'s high_freq_factor field must be a float, got {high_freq_factor}")
    if high_freq_factor <= low_freq_factor: logger.warning(f"`rope_scaling`'s high_freq_factor field must be greater than low_freq_factor, got high_freq_factor={high_freq_factor} and low_freq_factor={low_freq_factor}")
    original_max_position_embeddings = rope_scaling["original_max_position_embeddings"]
    if original_max_position_embeddings is None or not isinstance(original_max_position_embeddings, int): logger.warning(f"`rope_scaling`'s original_max_position_embeddings field must be an integer, got {original_max_position_embeddings}")
    if original_max_position_embeddings >= config.max_position_embeddings: logger.warning(f"`rope_scaling`'s original_max_position_embeddings field must be less than max_position_embeddings, got {original_max_position_embeddings} and max_position_embeddings={config.max_position_embeddings}")
def _validate_longrope_parameters(config: PretrainedConfig, ignore_keys: Optional[set] = None):
    rope_scaling = config.rope_scaling
    rope_type = rope_scaling.get("rope_type", rope_scaling.get("type", None))
    required_keys = {"rope_type", "short_factor", "long_factor"}
    optional_keys = {"attention_factor", "factor", "original_max_position_embeddings"}
    received_keys = set(rope_scaling.keys())
    _check_received_keys(rope_type, received_keys, required_keys, optional_keys, ignore_keys=ignore_keys)
    partial_rotary_factor = config.partial_rotary_factor if hasattr(config, "partial_rotary_factor") else 1.0
    head_dim = getattr(config, "head_dim", config.hidden_size // config.num_attention_heads)
    dim = int(head_dim * partial_rotary_factor)
    short_factor = rope_scaling.get("short_factor")
    if not isinstance(short_factor, list) and all(isinstance(x, (int, float)) for x in short_factor): logger.warning(f"`rope_scaling`'s short_factor field must be a list of numbers, got {short_factor}")
    if not len(short_factor) == dim // 2: logger.warning(f"`rope_scaling`'s short_factor field must have length {dim // 2}, got {len(short_factor)}")
    long_factor = rope_scaling.get("long_factor")
    if not isinstance(long_factor, list) and all(isinstance(x, (int, float)) for x in long_factor): logger.warning(f"`rope_scaling`'s long_factor field must be a list of numbers, got {long_factor}")
    if not len(long_factor) == dim // 2: logger.warning(f"`rope_scaling`'s long_factor field must have length {dim // 2}, got {len(long_factor)}")
    if hasattr(config, "original_max_position_embeddings"): logger.warning_once("This model has set a `original_max_position_embeddings` field, to be used together with `max_position_embeddings` to determine a scaling factor. Please set the `factor` field of `rope_scaling` with this ratio instead -- we recommend the use of this field over `original_max_position_embeddings`, as it is compatible with most model architectures.")
    else:
        factor = rope_scaling.get("factor")
        if factor is None: logger.warning("Missing required keys in `rope_scaling`: 'factor'")
        elif not isinstance(factor, float) or factor < 1.0: logger.warning(f"`rope_scaling`'s factor field must be a float >= 1, got {factor}")
        attention_factor = rope_scaling.get("attention_factor")
        if attention_factor is not None:
            if not isinstance(attention_factor, float) or attention_factor < 0.0: logger.warning(f"`rope_scaling`'s attention_factor field must be a float greater than 0, got {attention_factor}")
def _validate_sapama_parameters(config: PretrainedConfig, ignore_keys: Optional[set] = None):
    rope_scaling = config.rope_scaling
    rope_type = rope_scaling.get("rope_type", rope_scaling.get("type", None))
    required_keys = {"rope_type", "factor", "original_max_position_embeddings", "low_freq_factor", "high_freq_factor"}
    received_keys = set(rope_scaling.keys())
    _check_received_keys(rope_type, received_keys, required_keys, ignore_keys=ignore_keys)
    factor = rope_scaling["factor"]
    if factor is None or not isinstance(factor, float) or factor < 1.0: logger.warning(f"`rope_scaling`'s factor field must be a float >= 1, got {factor}")
    low_freq_factor = rope_scaling["low_freq_factor"]
    high_freq_factor = rope_scaling["high_freq_factor"]
    if low_freq_factor is None or not isinstance(low_freq_factor, float): logger.warning(f"`rope_scaling`'s low_freq_factor field must be a float, got {low_freq_factor}")
    if high_freq_factor is None or not isinstance(high_freq_factor, float): logger.warning(f"`rope_scaling`'s high_freq_factor field must be a float, got {high_freq_factor}")
    if high_freq_factor <= low_freq_factor: logger.warning(f"`rope_scaling`'s high_freq_factor field must be greater than low_freq_factor, got high_freq_factor={high_freq_factor} and low_freq_factor={low_freq_factor}")
    original_max_position_embeddings = rope_scaling["original_max_position_embeddings"]
    if original_max_position_embeddings is None or not isinstance(original_max_position_embeddings, int): logger.warning(f"`rope_scaling`'s original_max_position_embeddings field must be an integer, got {original_max_position_embeddings}")
    if original_max_position_embeddings >= config.max_position_embeddings: logger.warning(f"`rope_scaling`'s original_max_position_embeddings field must be less than max_position_embeddings, got {original_max_position_embeddings} and max_position_embeddings={config.max_position_embeddings}")
def _validate_yarn_parameters(config: PretrainedConfig, ignore_keys: Optional[set] = None):
    rope_scaling = config.rope_scaling
    rope_type = rope_scaling.get("rope_type", rope_scaling.get("type", None))
    required_keys = {"rope_type", "factor"}
    optional_keys = {"attention_factor", "beta_fast", "beta_slow"}
    received_keys = set(rope_scaling.keys())
    _check_received_keys(rope_type, received_keys, required_keys, optional_keys, ignore_keys=ignore_keys)
    factor = rope_scaling["factor"]
    if factor is None or not isinstance(factor, float) or factor < 1.0: logger.warning(f"`rope_scaling`'s factor field must be a float >= 1, got {factor}")
    attention_factor = rope_scaling.get("attention_factor")
    if attention_factor is not None and (not isinstance(attention_factor, float) or attention_factor < 0): logger.warning(f"`rope_scaling`'s attention_factor field must be a float greater than 0, got {attention_factor}")
    beta_fast = rope_scaling.get("beta_fast")
    if beta_fast is not None and not isinstance(beta_fast, float): logger.warning(f"`rope_scaling`'s beta_fast field must be a float, got {beta_fast}")
    beta_slow = rope_scaling.get("beta_slow")
    if beta_slow is not None and not isinstance(beta_slow, float): logger.warning(f"`rope_scaling`'s beta_slow field must be a float, got {beta_slow}")
    if (beta_fast or 32) < (beta_slow or 1): logger.warning(f"`rope_scaling`'s beta_fast field must be greater than beta_slow, got beta_fast={beta_fast} (defaults to 32 if None) and beta_slow={beta_slow} (defaults to 1 if None)")
ROPE_VALIDATION_FUNCTIONS = {"default": _validate_default_rope_parameters, "dynamic": _validate_dynamic_scaling_rope_parameters, "entity": _validate_entity_parameters, "linear": _validate_linear_scaling_rope_parameters, "llama3": _validate_llama3_parameters, "longrope": _validate_longrope_parameters, "sapama": _validate_sapama_parameters, "yarn": _validate_yarn_parameters}
def rope_config_validation(config: PretrainedConfig, ignore_keys: Optional[set] = None):
    rope_scaling = getattr(config, "rope_scaling", None)
    if rope_scaling is None: return
    rope_type = rope_scaling.get("rope_type", rope_scaling.get("type", "default"))
    validation_fn = ROPE_VALIDATION_FUNCTIONS.get(rope_type)
    if validation_fn is not None: validation_fn(config, ignore_keys=ignore_keys)
    else: logger.warning(f"Missing validation function mapping in `ROPE_VALIDATION_FUNCTIONS` for 'rope_type'='{rope_type}'")
sapiens_technology_configuration_validation = rope_config_validation
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
