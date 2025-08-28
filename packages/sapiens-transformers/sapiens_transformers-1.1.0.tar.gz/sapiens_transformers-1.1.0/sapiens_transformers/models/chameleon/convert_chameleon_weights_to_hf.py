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
import requests
import torch
import yaml
from sapiens_accelerator import init_empty_weights
from PIL import Image
from sapiens_transformers import (ChameleonConfig, ChameleonForCausalLM, ChameleonImageProcessor, ChameleonProcessor)
try: from sapiens_transformers import LlamaTokenizerFast
except ImportError: raise ValueError("Chameleon conversion supports only FastTokenizer and LlamaTokenizerFast can't be imported! Update your `tokenizers` library and re-run the tokenizer conversion.")
NUM_SHARDS = {'7B': 1, '30B': 4}
VOCAB_SIZE = 65536
def compute_intermediate_size(n, ffn_dim_multiplier=1, multiple_of=256): return multiple_of * ((int(ffn_dim_multiplier * int(8 * n / 3)) + multiple_of - 1) // multiple_of)
def read_json(path):
    with open(path, "r") as f: return json.load(f)
def write_json(text, path):
    with open(path, "w") as f: json.dump(text, f)
def write_model(model_path, input_base_path, model_size, chameleon_version=1):
    os.makedirs(model_path, exist_ok=True)
    input_model_path = os.path.join(input_base_path, "models", model_size.lower())
    params_path = os.path.join(input_model_path, "params.json")
    consolidate_params_path = os.path.join(input_model_path, "consolidate_params.json")
    params = read_json(params_path)
    if os.path.isfile(consolidate_params_path): params = {**params, **read_json(consolidate_params_path)}
    num_shards = NUM_SHARDS[model_size]
    model_parallel_size = params["model_parallel_size"]
    params = params.get("model", params)
    n_layers = params["n_layers"]
    n_heads = params["n_heads"]
    n_heads_per_shard = n_heads // num_shards
    dim = params["dim"]
    dims_per_head = dim // n_heads
    base = params.get("rope_theta", 10000.0)
    swin_norm = params["swin_norm"]
    if base > 10000.0: max_position_embeddings = 16384
    else:
        if chameleon_version == 1: max_position_embeddings = 4096
        else: raise NotImplementedError(f"Version {chameleon_version} of chameleon is not supported yet. Current supported versions of chameleon are [1].")
    if params.get("n_kv_heads", None) is not None:
        num_key_value_heads = params["n_kv_heads"]
        num_local_key_value_heads = n_heads_per_shard // num_key_value_heads
        key_value_dim = dim // num_key_value_heads
    else:
        num_key_value_heads = n_heads
        num_local_key_value_heads = n_heads_per_shard
        key_value_dim = dim
    print(f"Fetching all parameters from the checkpoint at {input_model_path}.")
    if num_shards == 1:
        loaded = None
        for possible_name in ["consolidated.pth", "consolidated.00.pth"]:
            possible_path = os.path.join(input_model_path, possible_name)
            if os.path.exists(possible_path):
                loaded = torch.load(possible_path, map_location="cpu")
                break
        assert loaded is not None
    else: loaded = [torch.load(os.path.join(input_model_path, f"consolidated.{i:02d}.pth"), map_location="cpu") for i in range(num_shards)]
    def permute(w, n_heads, dim1=dim, dim2=dim): return w.view(n_heads, dim1 // n_heads // 2, 2, dim2).transpose(1, 2).reshape(dim1, dim2)
    state_dict = {}
    for layer_i in range(n_layers):
        if num_shards == 1:
            state_dict.update({f"model.layers.{layer_i}.self_attn.q_proj.weight": permute(loaded[f"layers.{layer_i}.attention.wq.weight"], n_heads=n_heads), f"model.layers.{layer_i}.self_attn.k_proj.weight": permute(loaded[f"layers.{layer_i}.attention.wk.weight"], n_heads=num_key_value_heads, dim1=key_value_dim),
            f"model.layers.{layer_i}.self_attn.v_proj.weight": loaded[f"layers.{layer_i}.attention.wv.weight"], f"model.layers.{layer_i}.self_attn.o_proj.weight": loaded[f"layers.{layer_i}.attention.wo.weight"], f"model.layers.{layer_i}.mlp.gate_proj.weight": loaded[f"layers.{layer_i}.feed_forward.w1.weight"],
            f"model.layers.{layer_i}.mlp.down_proj.weight": loaded[f"layers.{layer_i}.feed_forward.w2.weight"], f"model.layers.{layer_i}.mlp.up_proj.weight": loaded[f"layers.{layer_i}.feed_forward.w3.weight"], f"model.layers.{layer_i}.input_layernorm.weight": loaded[f"layers.{layer_i}.attention_norm.weight"],
            f"model.layers.{layer_i}.post_attention_layernorm.weight": loaded[f"layers.{layer_i}.ffn_norm.weight"]})
            state_dict[f"model.layers.{layer_i}.self_attn.q_norm.weight"] = (loaded[f"layers.{layer_i}.attention.q_normalization.weight"].view(dims_per_head // 2, 2).t().reshape(1, -1).repeat_interleave(n_heads, 0))
            state_dict[f"model.layers.{layer_i}.self_attn.q_norm.bias"] = (loaded[f"layers.{layer_i}.attention.q_normalization.bias"].view(dims_per_head // 2, 2).t().reshape(1, -1).repeat_interleave(n_heads, 0))
            state_dict[f"model.layers.{layer_i}.self_attn.k_norm.weight"] = (loaded[f"layers.{layer_i}.attention.k_normalization.weight"].view(dims_per_head // 2, 2).t().reshape(1, -1).repeat_interleave(num_key_value_heads, 0))
            state_dict[f"model.layers.{layer_i}.self_attn.k_norm.bias"] = (loaded[f"layers.{layer_i}.attention.k_normalization.bias"].view(dims_per_head // 2, 2).t().reshape(1, -1).repeat_interleave(num_key_value_heads, 0))
        else:
            state_dict.update({f"model.layers.{layer_i}.input_layernorm.weight": torch.stack([l[f"layers.{layer_i}.attention_norm.weight"] for l in loaded]).mean(dim=0), f"model.layers.{layer_i}.post_attention_layernorm.weight": torch.stack([l[f"layers.{layer_i}.ffn_norm.weight"] for l in loaded]).mean(dim=0)})
            state_dict[f"model.layers.{layer_i}.self_attn.q_proj.weight"] = permute(torch.cat([loaded[i][f"layers.{layer_i}.attention.wq.weight"].view(n_heads_per_shard, dims_per_head, dim) for i in range(num_shards)], dim=0).reshape(dim, dim), n_heads=n_heads)
            state_dict[f"model.layers.{layer_i}.self_attn.k_proj.weight"] = permute(torch.cat([loaded[i][f"layers.{layer_i}.attention.wk.weight"].view(num_local_key_value_heads, dims_per_head, dim) for i in range(num_shards)], dim=0).reshape(key_value_dim, dim), n_heads=num_key_value_heads, dim1=key_value_dim)
            state_dict[f"model.layers.{layer_i}.self_attn.q_norm.weight"] = (torch.cat([l[f"layers.{layer_i}.attention.q_normalization.weight"].unsqueeze(0) for l in loaded]).view(num_shards, dims_per_head // 2, 2).transpose(1, 2).reshape(num_shards, -1).repeat_interleave(n_heads // num_shards, 0))
            state_dict[f"model.layers.{layer_i}.self_attn.q_norm.bias"] = (torch.cat([l[f"layers.{layer_i}.attention.q_normalization.bias"].unsqueeze(0) for l in loaded]).view(num_shards, dims_per_head // 2, 2).transpose(1, 2).reshape(num_shards, -1).repeat_interleave(n_heads // num_shards, 0))
            state_dict[f"model.layers.{layer_i}.self_attn.k_norm.weight"] = (torch.cat([l[f"layers.{layer_i}.attention.k_normalization.weight"].unsqueeze(0) for l in loaded]).view(num_shards, dims_per_head // 2, 2).transpose(1, 2).reshape(num_shards, -1).repeat_interleave(num_key_value_heads // num_shards, 0))
            state_dict[f"model.layers.{layer_i}.self_attn.k_norm.bias"] = (torch.cat([l[f"layers.{layer_i}.attention.k_normalization.bias"].unsqueeze(0) for l in loaded]).view(num_shards, dims_per_head // 2, 2).transpose(1, 2).reshape(num_shards, -1).repeat_interleave(num_key_value_heads // num_shards, 0))
            state_dict[f"model.layers.{layer_i}.self_attn.v_proj.weight"] = torch.cat([loaded[i][f"layers.{layer_i}.attention.wv.weight"].view(num_local_key_value_heads, dims_per_head, dim) for i in range(num_shards)], dim=0).reshape(key_value_dim, dim)
            state_dict[f"model.layers.{layer_i}.self_attn.o_proj.weight"] = torch.cat([loaded[i][f"layers.{layer_i}.attention.wo.weight"] for i in range(num_shards)], dim=1)
            state_dict[f"model.layers.{layer_i}.mlp.gate_proj.weight"] = torch.cat([loaded[i][f"layers.{layer_i}.feed_forward.w1.weight"] for i in range(num_shards)], dim=0)
            state_dict[f"model.layers.{layer_i}.mlp.down_proj.weight"] = torch.cat([loaded[i][f"layers.{layer_i}.feed_forward.w2.weight"] for i in range(num_shards)], dim=1)
            state_dict[f"model.layers.{layer_i}.mlp.up_proj.weight"] = torch.cat([loaded[i][f"layers.{layer_i}.feed_forward.w3.weight"] for i in range(num_shards)], dim=0)
    if num_shards == 1: state_dict.update({"model.embed_tokens.weight": loaded["tok_embeddings.weight"], "model.norm.weight": loaded["norm.weight"], "lm_head.weight": loaded["output.weight"]})
    else: state_dict.update({"model.embed_tokens.weight": torch.cat([loaded[i]["tok_embeddings.weight"] for i in range(num_shards)], dim=1), "model.norm.weight": torch.stack([loaded[i]["norm.weight"] for i in range(num_shards)]).mean(dim=0), "lm_head.weight": torch.cat([loaded[i]["output.weight"] for i in range(num_shards)], dim=0)})
    vqgan_path = os.path.join(input_base_path, "tokenizer/vqgan.ckpt")
    vqgan_state_dict = torch.load(vqgan_path, map_location="cpu")["state_dict"]
    for k, v in vqgan_state_dict.items():
        if "decoder" in k: continue
        state_dict[f"model.vqmodel.{k}"] = v
    ffn_dim_multiplier = params["ffn_dim_multiplier"] if "ffn_dim_multiplier" in params else 1
    multiple_of = params["multiple_of"] if "multiple_of" in params else 256
    with open(os.path.join(input_base_path, "tokenizer/text_tokenizer.json")) as tokenizer_file:
        tokenizer_config = json.load(tokenizer_file)
        vocabulary_map = tokenizer_config["model"]["vocab"]
        vocabulary_map["<image>"] = vocabulary_map["<reserved08707>"]
        del vocabulary_map["<reserved08707>"]
        for token in tokenizer_config["added_tokens"]:
            if token["content"] == "<reserved08707>": token["content"] = "<image>"
    with open(os.path.join(input_base_path, "tokenizer/text_tokenizer_modified.json"), "w") as f: json.dump(tokenizer_config, f)
    vq_keys_to_replace = [("ch", "base_channels"), ("out_ch", "out_channels"), ("n_embed", "num_embeddings"), ("ch_mult", "channel_multiplier"), ("double_z", "double_latent"), ("z_channels", "latent_channels")]
    with open(os.path.join(input_base_path, "tokenizer/vqgan.yaml")) as vqgan_cfg_file:
        vq_config = yaml.safe_load(vqgan_cfg_file)["model"]["params"]
        vq_config.update(**vq_config["ddconfig"])
        for old, new in vq_keys_to_replace: vq_config[new] = vq_config[old]
        del vq_config["ddconfig"]
        del vq_config["ckpt_path"]
        del vq_config["lossconfig"]
    config = ChameleonConfig(hidden_size=dim, intermediate_size=compute_intermediate_size(dim, ffn_dim_multiplier, multiple_of), num_attention_heads=params["n_heads"],
    num_hidden_layers=params["n_layers"], rms_norm_eps=params["norm_eps"], num_key_value_heads=num_key_value_heads, vocab_size=VOCAB_SIZE, rope_theta=base, max_position_embeddings=max_position_embeddings,
    model_parallel_size=model_parallel_size, swin_norm=swin_norm, vq_config=vq_config, vocabulary_map=vocabulary_map)
    with init_empty_weights(): model = ChameleonForCausalLM(config)
    model.load_state_dict(state_dict, assign=True, strict=False)
    model.save_pretrained(model_path, safe_serialization=True)
    tokenizer = LlamaTokenizerFast(tokenizer_file=os.path.join(input_base_path, "tokenizer/text_tokenizer_modified.json"), legacy=False)
    tokenizer.sep_token_id = 8710
    tokenizer.pad_token_id = 1
    image_processor = ChameleonImageProcessor()
    processor = ChameleonProcessor(image_processor=image_processor, tokenizer=tokenizer)
    processor.save_pretrained(model_path)
    del state_dict
    del loaded
    del vqgan_state_dict
    gc.collect()
    print("Loading the checkpoint in a Chameleon model...")
    print("*" * 100)
    model = ChameleonForCausalLM.from_pretrained(model_path, attn_implementation="eager", torch_dtype=torch.bfloat16, device_map="auto")
    processor = ChameleonProcessor.from_pretrained(model_path)
    prompt = "I'm very intrigued by this work of art:<image>Please tell me about the artist."
    image = Image.open(requests.get("https://uploads4.wikiart.org/images/paul-klee/death-for-the-idea-1915.jpg!Large.jpg", stream=True).raw)
    inputs = processor(prompt, images=image, return_tensors="pt").to(model.device, torch.bfloat16)
    length = inputs.input_ids.shape[1]
    out = model.generate(**inputs, max_new_tokens=40, do_sample=False)
    generated_text = processor.batch_decode(out[:, length:], skip_special_tokens=True)[0]
    print(f"Generation for single-image: {generated_text}")
    print("*" * 100)
    prompt = "I used to know a lot about constellations when I was younger, but as I grew older, I forgot most of what I knew. These are the only two constellations that I really remember now.<image><image>I would like for you to tell me about 3 more constellations and give me a little bit of history about the constellation."
    image = Image.open(requests.get("https://nineplanets.org/wp-content/uploads/2020/12/the-big-dipper-1.jpg", stream=True).raw)
    image_2 = Image.open(requests.get("https://www.kxan.com/wp-content/uploads/sites/40/2020/10/ORION.jpg", stream=True).raw)
    inputs = processor(prompt, images=[image, image_2], return_tensors="pt").to(model.device, dtype=torch.bfloat16)
    length = inputs.input_ids.shape[1]
    out = model.generate(**inputs, max_new_tokens=50, do_sample=False)
    generated_text = processor.batch_decode(out[:, length:], skip_special_tokens=True)[0]
    print(f"Generation for multi-image: {generated_text}")
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", help="Location of Chameleon weights")
    parser.add_argument("--model_size", choices=["7B", "30B"], help="models correspond to the finetuned versions, and are specific to the Chameleon official release. For more details on Chameleon, checkout the original repo: https://github.com/facebookresearch/chameleon")
    parser.add_argument("--output_dir", help="Location to write HF model")
    parser.add_argument("--test_inference", action="store_true", help="Whether to load the model for generation to test it's converted correctly.")
    parser.add_argument("--chameleon_version", choices=[1], default=1, type=int, help="Version of the Chameleon model to convert")
    args = parser.parse_args()
    write_model(model_path=args.output_dir, input_base_path=args.input_dir, model_size=args.model_size, chameleon_version=args.chameleon_version)
if __name__ == "__main__": main()
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
