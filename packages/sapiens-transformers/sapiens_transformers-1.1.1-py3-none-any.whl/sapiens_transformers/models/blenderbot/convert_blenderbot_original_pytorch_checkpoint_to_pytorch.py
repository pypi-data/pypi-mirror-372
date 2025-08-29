"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import argparse
import torch
from sapiens_transformers import BlenderbotConfig, BlenderbotForConditionalGeneration
from sapiens_transformers.utils import logging
logging.set_verbosity_info()
logger = logging.get_logger(__name__)
PATTERNS = [["attention", "attn"], ["encoder_attention", "encoder_attn"], ["q_lin", "q_proj"], ["k_lin", "k_proj"], ["v_lin", "v_proj"], ["out_lin", "out_proj"],
["norm_embeddings", "layernorm_embedding"], ["position_embeddings", "embed_positions"], ["embeddings", "embed_tokens"], ["ffn.lin", "fc"]]
def rename_state_dict_key(k):
    if k == "embeddings.weight": return "shared.weight"
    for parlai_name, hf_name in PATTERNS: k = k.replace(parlai_name, hf_name)
    if k.startswith("encoder"):
        k = k.replace(".attn", ".self_attn")
        k = k.replace("norm1", "self_attn_layer_norm")
        k = k.replace("norm2", "final_layer_norm")
    elif k.startswith("decoder"):
        k = k.replace("norm1", "self_attn_layer_norm")
        k = k.replace("norm2", "encoder_attn_layer_norm")
        k = k.replace("norm3", "final_layer_norm")
    return k
def rename_layernorm_keys(sd):
    keys = ["model.encoder.layernorm_embedding.weight", "model.encoder.layernorm_embedding.bias", "model.decoder.layernorm_embedding.weight", "model.decoder.layernorm_embedding.bias"]
    for k in keys:
        v = sd.pop(k)
        new_k = k.replace("layernorm_embedding", "layer_norm")
        assert new_k not in sd
        sd[new_k] = v
IGNORE_KEYS = ["START"]
@torch.no_grad()
def convert_parlai_checkpoint(checkpoint_path, pytorch_dump_folder_path, config_json_path):
    model = torch.load(checkpoint_path, map_location="cpu")
    sd = model["model"]
    cfg = BlenderbotConfig.from_json_file(config_json_path)
    m = BlenderbotForConditionalGeneration(cfg)
    valid_keys = m.model.state_dict().keys()
    failures = []
    mapping = {}
    for k, v in sd.items():
        if k in IGNORE_KEYS: continue
        new_k = rename_state_dict_key(k)
        if new_k not in valid_keys: failures.append([k, new_k])
        else: mapping[new_k] = v
    if cfg.normalize_before: rename_layernorm_keys(sd)
    m.model.load_state_dict(mapping, strict=True)
    m.half()
    m.save_pretrained(pytorch_dump_folder_path)
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--src_path", type=str, help="like blenderbot-model.bin")
    parser.add_argument("--save_dir", default="hf_blenderbot", type=str, help="Where to save converted model.")
    parser.add_argument("--hf_config_json", default="blenderbot-3b-config.json", type=str, help="Path to config to use")
    args = parser.parse_args()
    convert_parlai_checkpoint(args.src_path, args.save_dir, args.hf_config_json)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
