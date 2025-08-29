"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import argparse
import gc
import json
import os
import shutil
import warnings
import torch
from safetensors.torch import load_file as safe_load_file
from sapiens_transformers import (LlamaTokenizer, MistralConfig, MistralForCausalLM)
try:
    from sapiens_transformers import LlamaTokenizerFast
    tokenizer_class = LlamaTokenizerFast
except ImportError as e:
    warnings.warn(e)
    warnings.warn("The converted tokenizer will be the `slow` tokenizer. To use the fast, update your `tokenizers` library and re-run the tokenizer conversion")
    tokenizer_class = LlamaTokenizer
NUM_SHARDS = {"7B": 1}
def compute_intermediate_size(n, ffn_dim_multiplier=1, multiple_of=256): return multiple_of * ((int(ffn_dim_multiplier * int(8 * n / 3)) + multiple_of - 1) // multiple_of)
def read_json(path):
    with open(path, "r") as f: return json.load(f)
def write_json(text, path):
    with open(path, "w") as f: json.dump(text, f)
def write_model(model_path, input_base_path, model_size, tokenizer_path=None, safe_serialization=True, is_v3=False):
    if not os.path.isfile(os.path.join(input_base_path, "params.json")): input_base_path = os.path.join(input_base_path, model_size)
    os.makedirs(model_path, exist_ok=True)
    tmp_model_path = os.path.join(model_path, "tmp")
    os.makedirs(tmp_model_path, exist_ok=True)
    params = read_json(os.path.join(input_base_path, "params.json"))
    num_shards = NUM_SHARDS[model_size]
    sliding_window = params.get("sliding_window", None)
    if sliding_window is not None: sliding_window = int(sliding_window)
    n_layers = params["n_layers"]
    n_heads = params["n_heads"]
    n_heads_per_shard = n_heads // num_shards
    dim = params["dim"]
    dims_per_head = dim // n_heads
    base = params.get("rope_theta", 10000.0)
    inv_freq = 1.0 / (base ** (torch.arange(0, dims_per_head, 2).float() / dims_per_head))
    max_position_embeddings = 4096 * 8
    if tokenizer_path is not None:
        tokenizer = tokenizer_class(tokenizer_path + ".v3" if is_v3 else "")
        tokenizer.save_pretrained(model_path)
    vocab_size = tokenizer.vocab_size if tokenizer_path is not None else 32000
    if "n_kv_heads" in params:
        num_key_value_heads = params["n_kv_heads"]
        num_local_key_value_heads = num_key_value_heads // num_shards
        key_value_dim = dims_per_head * num_local_key_value_heads
    else:
        num_key_value_heads = n_heads
        num_local_key_value_heads = n_heads_per_shard
        key_value_dim = dim
    def permute(w, n_heads=n_heads, dim1=dim, dim2=dim): return w.view(n_heads, dim1 // n_heads // 2, 2, dim2).transpose(1, 2).reshape(dim1, dim2)
    print(f"Fetching all parameters from the checkpoint at {input_base_path}.")
    if is_v3: loaded = [safe_load_file(os.path.join(input_base_path, "consolidated.safetensors"))]
    else: loaded = [torch.load(os.path.join(input_base_path, f"consolidated.{i:02d}.pth"), map_location="cpu") for i in range(num_shards)]
    param_count = 0
    index_dict = {"weight_map": {}}
    for layer_i in range(n_layers):
        filename = f"pytorch_model-{layer_i + 1}-of-{n_layers + 1}.bin"
        state_dict = {f"model.layers.{layer_i}.input_layernorm.weight": loaded[0][f"layers.{layer_i}.attention_norm.weight"].clone(),
        f"model.layers.{layer_i}.post_attention_layernorm.weight": loaded[0][f"layers.{layer_i}.ffn_norm.weight"].clone()}
        state_dict[f"model.layers.{layer_i}.self_attn.q_proj.weight"] = permute(torch.cat([loaded[i][f"layers.{layer_i}.attention.wq.weight"].view(n_heads_per_shard, dims_per_head, dim)
        for i in range(num_shards)], dim=0).reshape(dim, dim))
        state_dict[f"model.layers.{layer_i}.self_attn.k_proj.weight"] = permute(torch.cat([loaded[i][f"layers.{layer_i}.attention.wk.weight"].view(num_local_key_value_heads, dims_per_head, dim)
        for i in range(num_shards)], dim=0).reshape(key_value_dim, dim), num_key_value_heads, key_value_dim, dim)
        state_dict[f"model.layers.{layer_i}.self_attn.v_proj.weight"] = torch.cat([loaded[i][f"layers.{layer_i}.attention.wv.weight"].view(num_local_key_value_heads, dims_per_head, dim)
        for i in range(num_shards)], dim=0).reshape(key_value_dim, dim)
        state_dict[f"model.layers.{layer_i}.self_attn.o_proj.weight"] = torch.cat([loaded[i][f"layers.{layer_i}.attention.wo.weight"] for i in range(num_shards)], dim=1)
        state_dict[f"model.layers.{layer_i}.mlp.gate_proj.weight"] = torch.cat([loaded[i][f"layers.{layer_i}.feed_forward.w1.weight"] for i in range(num_shards)], dim=0)
        state_dict[f"model.layers.{layer_i}.mlp.down_proj.weight"] = torch.cat([loaded[i][f"layers.{layer_i}.feed_forward.w2.weight"] for i in range(num_shards)], dim=1)
        state_dict[f"model.layers.{layer_i}.mlp.up_proj.weight"] = torch.cat([loaded[i][f"layers.{layer_i}.feed_forward.w3.weight"] for i in range(num_shards)], dim=0)
        state_dict[f"model.layers.{layer_i}.self_attn.rotary_emb.inv_freq"] = inv_freq
        for k, v in state_dict.items():
            index_dict["weight_map"][k] = filename
            param_count += v.numel()
        torch.save(state_dict, os.path.join(tmp_model_path, filename))
    filename = f"pytorch_model-{n_layers + 1}-of-{n_layers + 1}.bin"
    state_dict = {"model.norm.weight": loaded[0]["norm.weight"], "model.embed_tokens.weight": torch.cat([loaded[i]["tok_embeddings.weight"] for i in range(num_shards)], dim=1),
    "lm_head.weight": torch.cat([loaded[i]["output.weight"] for i in range(num_shards)], dim=0)}
    for k, v in state_dict.items():
        index_dict["weight_map"][k] = filename
        param_count += v.numel()
    torch.save(state_dict, os.path.join(tmp_model_path, filename))
    index_dict["metadata"] = {"total_size": param_count * 2}
    write_json(index_dict, os.path.join(tmp_model_path, "pytorch_model.bin.index.json"))
    config = MistralConfig(hidden_size=dim, intermediate_size=params["hidden_dim"], num_attention_heads=params["n_heads"], num_hidden_layers=params["n_layers"],
    rms_norm_eps=params["norm_eps"], num_key_value_heads=num_key_value_heads, vocab_size=vocab_size, rope_theta=base, max_position_embeddings=max_position_embeddings, sliding_window=sliding_window)
    config.save_pretrained(tmp_model_path)
    del state_dict
    del loaded
    gc.collect()
    print("Loading the checkpoint in a Mistral model.")
    model = MistralForCausalLM.from_pretrained(tmp_model_path, torch_dtype=torch.bfloat16, low_cpu_mem_usage=True)
    del model.config._name_or_path
    model.config.torch_dtype = torch.float16
    print("Saving in the Transformers format.")
    model.save_pretrained(model_path, safe_serialization=safe_serialization)
    shutil.rmtree(tmp_model_path)
def write_tokenizer(tokenizer_path, input_tokenizer_path):
    print(f"Saving a {tokenizer_class.__name__} to {tokenizer_path}.")
    tokenizer = tokenizer_class(input_tokenizer_path)
    tokenizer.save_pretrained(tokenizer_path)
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", help="Location of Mistral weights, which contains tokenizer.model and model folders")
    parser.add_argument("--model_size", choices=["7B", "tokenizer_only"], help="'f' models correspond to the finetuned versions, and are specific to the Mistral2 official release.")
    parser.add_argument("--output_dir", help="Location to write HF model and tokenizer")
    parser.add_argument("--safe_serialization", type=bool, help="Whether or not to save using `safetensors`.")
    parser.add_argument("--is_v3", action="store_true", help="Whether the checkpoints correspond to the 3rd version or not.")
    args = parser.parse_args()
    spm_path = os.path.join(args.input_dir, "tokenizer.model")
    if args.model_size != "tokenizer_only": write_model(model_path=args.output_dir, input_base_path=args.input_dir, model_size=args.model_size, safe_serialization=args.safe_serialization, tokenizer_path=spm_path, is_v3=args.is_v3)
    else: write_tokenizer(args.output_dir, spm_path)
if __name__ == "__main__": main()
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
