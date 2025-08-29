"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from os import makedirs, path as _path, listdir
from torch import arange as t_arange, load as t_load, cat as t_cat, save as t_save, bfloat16 as t_bfloat16, float16 as t_float16
from sapiens_transformers import EntityConfig, GenerationConfig, EntityForCausalLM, PreTrainedTokenizerFast, EntityTokenizer
from sapiens_transformers.convert_slow_tokenizer import TikTokenConverter
try: from sapiens_transformers import EntityTokenizerFast
except ImportError as error: EntityTokenizerFast = None
CONTEXT_LENGTH_FOR_VERSION, NUM_SHARDS = {"3.1": 131072, "3": 8192, "2": 4096, "1": 2048}, {'7B': 1, '8B': 1, '8Bf': 1, '7Bf': 1, '13B': 2, '13Bf': 2, '34B': 4, '30B': 4, '65B': 8, '70B': 8, '70Bf': 8, '405B': 8, '405B-MP16': 16}
def write_model(model_path=None, input_base_path=None, model_size=None, safe_serialization=True, entity_version="1", vocab_size=None, num_shards=None, instruct=False):
    makedirs(model_path, exist_ok=True)
    tmp_model_path = _path.join(model_path, "tmp")
    makedirs(tmp_model_path, exist_ok=True)
    from json import load, dump
    def read_json(path):
        with open(path, "r") as file: return load(file)
    params, num_shards = read_json(_path.join(input_base_path, "params.json")), NUM_SHARDS[model_size] if num_shards is None else num_shards
    params = params.get("model", params)
    n_layers, n_heads = params["n_layers"], params["n_heads"]
    n_heads_per_shard, dim = n_heads // num_shards, params["dim"]
    dims_per_head, base = dim // n_heads, params.get("rope_theta", 10000.0)
    inv_freq = 1.0 / (base ** (t_arange(0, dims_per_head, 2).float() / dims_per_head))
    if base > 10000.0 and float(entity_version) < 3: max_position_embeddings = 16384
    else: max_position_embeddings = CONTEXT_LENGTH_FOR_VERSION[entity_version]
    if params.get("n_kv_heads", None) is not None:
        num_key_value_heads = params["n_kv_heads"]
        num_key_value_heads_per_shard, key_value_dim = num_key_value_heads // num_shards, dims_per_head * num_key_value_heads
    else: num_key_value_heads, num_key_value_heads_per_shard, key_value_dim = n_heads, n_heads_per_shard, dim
    def permute(w=None, n_heads=None, dim1=dim, dim2=dim): return w.view(n_heads, dim1 // n_heads // 2, 2, dim2).transpose(1, 2).reshape(dim1, dim2)
    if num_shards == 1: loaded = t_load(_path.join(input_base_path, "consolidated.00.pth"), map_location="cpu")
    else: loaded = [t_load(_path.join(input_base_path, file), map_location="cpu") for file in sorted([file for file in listdir(input_base_path) if file.endswith(".pth")])]
    param_count, index_dict = 0, {"weight_map": {}}
    for layer_i in range(n_layers):
        filename = f"pytorch_model-{layer_i + 1}-of-{n_layers + 1}.bin"
        if num_shards == 1:
            state_dict = {f"model.layers.{layer_i}.self_attn.q_proj.weight": permute(loaded[f"layers.{layer_i}.attention.wq.weight"], n_heads=n_heads),
            f"model.layers.{layer_i}.self_attn.k_proj.weight": permute(loaded[f"layers.{layer_i}.attention.wk.weight"], n_heads=num_key_value_heads, dim1=key_value_dim),
            f"model.layers.{layer_i}.self_attn.v_proj.weight": loaded[f"layers.{layer_i}.attention.wv.weight"], f"model.layers.{layer_i}.self_attn.o_proj.weight": loaded[f"layers.{layer_i}.attention.wo.weight"],
            f"model.layers.{layer_i}.mlp.gate_proj.weight": loaded[f"layers.{layer_i}.feed_forward.w1.weight"], f"model.layers.{layer_i}.mlp.down_proj.weight": loaded[f"layers.{layer_i}.feed_forward.w2.weight"],
            f"model.layers.{layer_i}.mlp.up_proj.weight": loaded[f"layers.{layer_i}.feed_forward.w3.weight"], f"model.layers.{layer_i}.input_layernorm.weight": loaded[f"layers.{layer_i}.attention_norm.weight"],
            f"model.layers.{layer_i}.post_attention_layernorm.weight": loaded[f"layers.{layer_i}.ffn_norm.weight"]}
        else:
            state_dict = {f"model.layers.{layer_i}.input_layernorm.weight": loaded[0][f"layers.{layer_i}.attention_norm.weight"].clone(),
            f"model.layers.{layer_i}.post_attention_layernorm.weight": loaded[0][f"layers.{layer_i}.ffn_norm.weight"].clone()}
            state_dict[f"model.layers.{layer_i}.self_attn.q_proj.weight"] = permute(t_cat([loaded[i][f"layers.{layer_i}.attention.wq.weight"].view(n_heads_per_shard, dims_per_head, dim)
            for i in range(len(loaded))], dim=0).reshape(dim, dim), n_heads=n_heads)
            state_dict[f"model.layers.{layer_i}.self_attn.k_proj.weight"] = permute(t_cat([loaded[i][f"layers.{layer_i}.attention.wk.weight"].view(num_key_value_heads_per_shard, dims_per_head, dim)
            for i in range(len(loaded))], dim=0).reshape(key_value_dim, dim), num_key_value_heads, key_value_dim, dim)
            state_dict[f"model.layers.{layer_i}.self_attn.v_proj.weight"] = t_cat([loaded[i][f"layers.{layer_i}.attention.wv.weight"].view(num_key_value_heads_per_shard, dims_per_head, dim)
            for i in range(len(loaded))], dim=0).reshape(key_value_dim, dim)
            state_dict[f"model.layers.{layer_i}.self_attn.o_proj.weight"] = t_cat([loaded[i][f"layers.{layer_i}.attention.wo.weight"] for i in range(len(loaded))], dim=1)
            state_dict[f"model.layers.{layer_i}.mlp.gate_proj.weight"] = t_cat([loaded[i][f"layers.{layer_i}.feed_forward.w1.weight"] for i in range(len(loaded))], dim=0)
            state_dict[f"model.layers.{layer_i}.mlp.down_proj.weight"] = t_cat([loaded[i][f"layers.{layer_i}.feed_forward.w2.weight"] for i in range(len(loaded))], dim=1)
            state_dict[f"model.layers.{layer_i}.mlp.up_proj.weight"] = t_cat([loaded[i][f"layers.{layer_i}.feed_forward.w3.weight"] for i in range(len(loaded))], dim=0)
        state_dict[f"model.layers.{layer_i}.self_attn.rotary_emb.inv_freq"] = inv_freq
        for k, v in state_dict.items():
            index_dict["weight_map"][k] = filename
            param_count += v.numel()
        t_save(state_dict, _path.join(tmp_model_path, filename))
    filename = f"pytorch_model-{n_layers + 1}-of-{n_layers + 1}.bin"
    if num_shards == 1: state_dict = {"model.embed_tokens.weight": loaded["tok_embeddings.weight"], "model.norm.weight": loaded["norm.weight"], "lm_head.weight": loaded["output.weight"]}
    else: state_dict = {"model.norm.weight": loaded[0]["norm.weight"], "model.embed_tokens.weight": t_cat([loaded[i]["tok_embeddings.weight"] for i in range(len(loaded))], dim=0 if entity_version in ["3", "3.1"] else 1),
    "lm_head.weight": t_cat([loaded[i]["output.weight"] for i in range(len(loaded))], dim=0)}
    for k, v in state_dict.items():
        index_dict["weight_map"][k] = filename
        param_count += v.numel()
    t_save(state_dict, _path.join(tmp_model_path, filename))
    index_dict["metadata"] = {"total_size": param_count * 2}
    def write_json(text, path):
        with open(path, "w") as file: dump(text, file)
    write_json(index_dict, _path.join(tmp_model_path, "pytorch_model.bin.index.json"))
    ffn_dim_multiplier, multiple_of = params["ffn_dim_multiplier"] if "ffn_dim_multiplier" in params else 1, params["multiple_of"] if "multiple_of" in params else 256
    if entity_version in ["3", "3.1"]:
        bos_token_id = 128000
        if instruct: eos_token_id = [128001, 128008, 128009]
        else: eos_token_id = 128001
    else: bos_token_id, eos_token_id = 1, 2
    def compute_intermediate_size(n, ffn_dim_multiplier=1, multiple_of=256): return multiple_of * ((int(ffn_dim_multiplier * int(8 * n / 3)) + multiple_of - 1) // multiple_of)
    config = EntityConfig(hidden_size=dim, intermediate_size=compute_intermediate_size(dim, ffn_dim_multiplier, multiple_of), num_attention_heads=params["n_heads"],
    num_hidden_layers=params["n_layers"], rms_norm_eps=params["norm_eps"], num_key_value_heads=num_key_value_heads, vocab_size=vocab_size, rope_theta=base,
    max_position_embeddings=max_position_embeddings, bos_token_id=bos_token_id, eos_token_id=eos_token_id)
    config.save_pretrained(tmp_model_path)
    if instruct: GenerationConfig(do_sample=True, temperature=0.6, top_p=0.9, bos_token_id=bos_token_id, eos_token_id=eos_token_id).save_pretrained(tmp_model_path)
    del state_dict
    del loaded
    from gc import collect
    collect()
    print("Loading the checkpoint in a Entity model.")
    model = EntityForCausalLM.from_pretrained(tmp_model_path, torch_dtype=t_bfloat16, low_cpu_mem_usage=True)
    del model.config._name_or_path
    model.config.torch_dtype = t_float16
    print("Saving in the Transformers format.")
    model.save_pretrained(model_path, safe_serialization=safe_serialization)
    from shutil import rmtree
    rmtree(tmp_model_path, ignore_errors=True)
class EntityConverter(TikTokenConverter):
    def __init__(self, vocab_file=None, special_tokens=None, instruct=False, model_max_length=None, **kwargs):
        super().__init__(vocab_file, additional_special_tokens=special_tokens, **kwargs)
        tokenizer = self.converted()
        chat_template = (
            "{% set loop_messages = messages %}"
            "{% for message in loop_messages %}"
            "{% set content = '<|start_header_id|>' + message['role'] + '<|end_header_id|>\n\n'+ message['content'] | trim + '<|eot_id|>' %}"
            "{% if loop.index0 == 0 %}"
            "{% set content = bos_token + content %}"
            "{% endif %}"
            "{{ content }}"
            "{% endfor %}"
            "{{ '<|start_header_id|>assistant<|end_header_id|>\n\n' }}"
        )
        self.tokenizer = PreTrainedTokenizerFast(tokenizer_object=tokenizer, bos_token="<|begin_of_text|>", eos_token="<|end_of_text|>" if not instruct else "<|eot_id|>",
        chat_template=chat_template if instruct else None, model_input_names=["input_ids", "attention_mask"], model_max_length=model_max_length)
def write_tokenizer(tokenizer_path=None, input_tokenizer_path=None, entity_version="2", special_tokens=None, instruct=False):
    tokenizer_class = EntityTokenizer if EntityTokenizerFast is None else EntityTokenizerFast
    if entity_version in ["3", "3.1"]: tokenizer = EntityConverter(input_tokenizer_path, special_tokens, instruct, model_max_length=CONTEXT_LENGTH_FOR_VERSION[entity_version]).tokenizer
    else: tokenizer = tokenizer_class(input_tokenizer_path)
    print(f"Saving a {tokenizer_class.__name__} to {tokenizer_path}.")
    tokenizer.save_pretrained(tokenizer_path)
    return tokenizer
DEFAULT_ENTITY_SPECIAL_TOKENS = {"3": ["<|begin_of_text|>", "<|end_of_text|>", "<|reserved_special_token_0|>", "<|reserved_special_token_1|>", "<|reserved_special_token_2|>", "<|reserved_special_token_3|>",
"<|start_header_id|>", "<|end_header_id|>", "<|reserved_special_token_4|>", "<|eot_id|>"] + [f"<|reserved_special_token_{i}|>" for i in range(5, 256 - 5)],
"3.1": ["<|begin_of_text|>", "<|end_of_text|>", "<|reserved_special_token_0|>", "<|reserved_special_token_1|>", "<|finetune_right_pad_id|>", "<|reserved_special_token_2|>",
"<|start_header_id|>", "<|end_header_id|>", "<|eom_id|>", "<|eot_id|>", "<|python_tag|>"] + [f"<|reserved_special_token_{i}|>" for i in range(3, 256 - 8)]}
def main():
    from argparse import ArgumentParser
    from typing import List
    parser = ArgumentParser()
    parser.add_argument("--input_dir", help="Location of Entity weights, which contains tokenizer.model and model folders")
    parser.add_argument("--model_size", default=None, help="'f' Deprecated in favor of `num_shards`: models correspond to the finetuned versions, and are specific to the Entity official release. For more details on Entity.")
    parser.add_argument("--output_dir", help="Location to write Sapiens model and tokenizer"), parser.add_argument("--safe_serialization", default=True, type=bool, help="Whether or not to save using `safetensors`.")
    parser.add_argument("--entity_version", choices=["1", "2", "3", "3.1"], default="1", type=str, help="Version of the Entity model to convert. Controls the context size")
    parser.add_argument("--num_shards", default=None, type=int, help="The number of individual shards used for the model. Does not have to be the same as the number of consolidated_xx.pth")
    parser.add_argument("--special_tokens", default=None, type=List[str], help="The list of special tokens that should be added to the model.")
    parser.add_argument("--instruct", default=False, type=bool, help="Whether the model is an instruct model or not. Will affect special tokens for entity.")
    args = parser.parse_args()
    if args.model_size is None and args.num_shards is None: raise ValueError("You have to set at least `num_shards` if you are not giving the `model_size`")
    if args.special_tokens is None: args.special_tokens = DEFAULT_ENTITY_SPECIAL_TOKENS.get(str(args.entity_version), [])
    spm_path = _path.join(args.input_dir, "tokenizer.model")
    vocab_size = len(write_tokenizer(args.output_dir, spm_path, entity_version=args.entity_version, special_tokens=args.special_tokens, instruct=args.instruct))
    if args.model_size != "tokenizer_only": write_model(model_path=args.output_dir, input_base_path=args.input_dir, model_size=args.model_size, safe_serialization=args.safe_serialization, entity_version=args.entity_version,
    vocab_size=vocab_size, num_shards=args.num_shards, instruct=args.instruct)
if __name__ == "__main__": main()
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
