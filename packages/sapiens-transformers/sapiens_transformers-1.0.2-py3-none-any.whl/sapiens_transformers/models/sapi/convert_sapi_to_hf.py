"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from os import makedirs, path as _path, rename
from torch import device as t_device, float32 as t_float32, float16 as t_float16, bfloat16 as t_bfloat16, cat as t_cat, arange as t_arange, save as t_save
def convert(input_sapi_file=None, output_hf_file=None, precision=None, cpu_only=False) -> None:
    from pytorch_lightning import Trainer
    from sapiens_transformers.adaptations import SAPIStrategy
    dummy_trainer = Trainer(devices=1, accelerator="cpu", strategy=SAPIStrategy())
    from sapiens_transformers import SAPIGPTModel
    new_sapi_model = SAPIGPTModel()
    sapi_model = new_sapi_model.SAPIGPTModel
    model_config = sapi_model.restore_from(input_sapi_file, trainer=dummy_trainer, return_config=True)
    model_config.tensor_model_parallel_size, model_config.pipeline_model_parallel_size = 1, 1
    model_config.sequence_parallel, model_config.transformer_engine = False, True
    if cpu_only:
        map_location = t_device("cpu")
        model_config.use_cpu_initialization, model_config.dist_ckpt_load_on_device = True, False
    else: map_location = None
    model = sapi_model.restore_from(input_sapi_file, trainer=dummy_trainer, override_config_path=model_config, map_location=map_location)
    vocab_size = model.padded_vocab_size
    if precision is None: precision = model.cfg.precision
    if precision in [32, "32"]: dtype = t_float32
    elif precision in [16, "16", "16-mixed"]: dtype = t_float16
    elif precision in ["bf16", "bf16-mixed"]: dtype = t_bfloat16
    else: dtype = t_float32
    def param_to_weights(param=None): return param.to(dtype)
    from collections import OrderedDict
    checkpoint, hidden_size = OrderedDict(), model.cfg.hidden_size
    head_num, num_layers, ffn_hidden_size = model.cfg.num_attention_heads, model.cfg.num_layers, model.cfg.ffn_hidden_size
    num_query_groups = model.cfg.get("num_query_groups", head_num)
    if num_query_groups is None: num_query_groups = head_num
    heads_per_group, qkv_total_dim = head_num // num_query_groups, head_num + 2 * num_query_groups
    embed_weight, embed_weights_base_name = model.state_dict()["model.embedding.word_embeddings.weight"], "model.embed_tokens.weight"
    checkpoint[embed_weights_base_name] = param_to_weights(embed_weight)
    for inner_layer in range(int(num_layers)):
        qkv_weights = model.state_dict()[f"model.decoder.layers.{inner_layer}.self_attention.linear_qkv.weight"].reshape([qkv_total_dim, -1, hidden_size])
        q_slice = t_cat([t_arange((heads_per_group + 2) * i, (heads_per_group + 2) * i + heads_per_group) for i in range(num_query_groups)])
        k_slice, v_slice = t_arange(heads_per_group, qkv_total_dim, (heads_per_group + 2)), t_arange(heads_per_group + 1, qkv_total_dim, (heads_per_group + 2))
        q_weights_base_name, k_weights_base_name, v_weights_base_name = f"model.layers.{inner_layer}.self_attn.q_proj.weight", f"model.layers.{inner_layer}.self_attn.k_proj.weight", f"model.layers.{inner_layer}.self_attn.v_proj.weight"
        checkpoint[q_weights_base_name], checkpoint[k_weights_base_name], checkpoint[v_weights_base_name] = param_to_weights(qkv_weights[q_slice].reshape(-1, hidden_size)), param_to_weights(qkv_weights[k_slice].reshape(-1, hidden_size)), param_to_weights(qkv_weights[v_slice].reshape(-1, hidden_size))
        o_weight, o_weight_base_name = model.state_dict()[f"model.decoder.layers.{inner_layer}.self_attention.linear_proj.weight"], f"model.layers.{inner_layer}.self_attn.o_proj.weight"
        checkpoint[o_weight_base_name], mlp_weights = param_to_weights(o_weight), model.state_dict()[f"model.decoder.layers.{inner_layer}.mlp.linear_fc1.weight"]
        mlp_up_proj_weight = model.state_dict()[f"model.decoder.layers.{inner_layer}.mlp.linear_fc2.weight"]
        if mlp_weights.shape[0] != mlp_up_proj_weight.shape[1]:
            assert mlp_weights.shape[0] == 2 * mlp_up_proj_weight.shape[1]
            mlp_down_proj_weight, mlp_gate_proj_weight = mlp_weights[:ffn_hidden_size, :], mlp_weights[ffn_hidden_size:, :]
            mlp_down_proj_base_name, mlp_gate_proj_base_name = f"model.layers.{inner_layer}.mlp.gate_proj.weight", f"model.layers.{inner_layer}.mlp.up_proj.weight"
            checkpoint[mlp_down_proj_base_name], checkpoint[mlp_gate_proj_base_name] = param_to_weights(mlp_down_proj_weight), param_to_weights(mlp_gate_proj_weight)
        else:
            mlp_down_proj_weight, mlp_down_proj_base_name = mlp_weights, f"model.layers.{inner_layer}.mlp.up_proj.weight"
            checkpoint[mlp_down_proj_base_name] = param_to_weights(mlp_down_proj_weight)
        checkpoint[f"model.layers.{inner_layer}.mlp.down_proj.weight"] = param_to_weights(mlp_up_proj_weight)
        input_ln_weight, input_ln_base_name = model.state_dict()[f"model.decoder.layers.{inner_layer}.self_attention.linear_qkv.layer_norm_weight"], f"model.layers.{inner_layer}.input_layernorm.weight"
        checkpoint[input_ln_base_name] = param_to_weights(input_ln_weight)
        if (model.state_dict().get(f"model.decoder.layers.{inner_layer}.self_attention.linear_qkv.layer_norm_bias", None) is not None):
            input_ln_bias, input_ln_bias_name = model.state_dict()[f"model.decoder.layers.{inner_layer}.self_attention.linear_qkv.layer_norm_bias"], f"model.layers.{inner_layer}.input_layernorm.bias"
            checkpoint[input_ln_bias_name] = param_to_weights(input_ln_bias)
        post_attn_ln_weight, post_attn_ln_base_name = model.state_dict()[f"model.decoder.layers.{inner_layer}.mlp.linear_fc1.layer_norm_weight"], f"model.layers.{inner_layer}.post_attention_layernorm.weight"
        checkpoint[post_attn_ln_base_name] = param_to_weights(post_attn_ln_weight)
        if model.state_dict().get(f"model.decoder.layers.{inner_layer}.mlp.linear_fc1.layer_norm_bias", None) is not None:
            post_attn_ln_bias, post_attn_ln_bias_name = model.state_dict()[f"model.decoder.layers.{inner_layer}.mlp.linear_fc1.layer_norm_bias"], f"model.layers.{inner_layer}.post_attention_layernorm.bias"
            checkpoint[post_attn_ln_bias_name] = param_to_weights(post_attn_ln_bias)
    final_ln_weight, final_ln_base_name = model.state_dict()["model.decoder.final_layernorm.weight"], "model.norm.weight"
    checkpoint[final_ln_base_name] = param_to_weights(final_ln_weight)
    if model.state_dict().get("model.decoder.final_layernorm.bias", None) is not None:
        final_ln_bias, final_ln_bias_name = model.state_dict()["model.decoder.final_layernorm.bias"], "model.norm.bias"
        checkpoint[final_ln_bias_name] = param_to_weights(final_ln_bias)
    output_layer_weight, output_layer_base_name = model.state_dict()["model.output_layer.weight"], "lm_head.weight"
    checkpoint[output_layer_base_name] = param_to_weights(output_layer_weight)
    makedirs(_path.dirname(output_hf_file), exist_ok=True)
    t_save(checkpoint, output_hf_file)
    return model_config, model.tokenizer, dtype, vocab_size
def extract_sapi_tokenizer(sapi_file=None, model_config=None, output_hf_path=None, sapi_tokenizer=None):
    tokenizer_cfg = model_config.tokenizer
    from sapiens_transformers.adaptations import SAPITokenizer as SAPITokenizerX
    if tokenizer_cfg.library == "sentencepiece":
        tokenizer_fn, output_tokenizer = tokenizer_cfg.model[5:], f"{output_hf_path}/tokenizer.model"
        from shutil import copy
        end1, end2 = ''.join([chr(x) for x in [46, 115, 112]]), ''.join([chr(x) for x in [46, 110, 101, 109, 111]])
        if sapi_file.endswith(end1) or sapi_file.endswith(end2):
            import tarfile
            archive = tarfile.open(sapi_file, "r")
            archive.extract("./" + tokenizer_fn, output_hf_path)
            archive.close()
            rename(f"{output_hf_path}/{tokenizer_fn}", output_tokenizer)
        elif _path.isdir(sapi_file): copy(f"{sapi_file}/{tokenizer_fn}", output_tokenizer)
        from sapiens_transformers import SAPITokenizer, PreTrainedTokenizerFast
        tokenizer = SAPITokenizer.from_pretrained(output_hf_path, legacy=False)
        from sapiens_transformers.convert_slow_tokenizer import SAPIConverter
        tokenizer = PreTrainedTokenizerFast(tokenizer_object=SAPIConverter(tokenizer).converted(), model_input_names=["input_ids", "token_type_ids"])
        tokenizer.save_pretrained(output_hf_path)
    elif isinstance(sapi_tokenizer, SAPITokenizerX): sapi_tokenizer.tokenizer.save_pretrained(output_hf_path)
    else: raise ValueError(f"Unsupported tokenizer type: library: {tokenizer_cfg.library}, type: {tokenizer_cfg.type}")
def get_args():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("--input_name_or_path", type=str, default=None, required=True, help="Path to .sp file or extracted folder"), parser.add_argument("--output_path", type=str, default=None, required=False, help="")
    parser.add_argument("--hf_input_path", type=str, default=None, help="A Sapiens model path."), parser.add_argument("--hf_output_path", type=str, default=None, help="")
    parser.add_argument("--precision", type=str, default=None, help="Precision of output weights." "Defaults to precision of the input sp weights (model.cfg.trainer.precision)")
    parser.add_argument("--cpu-only", action="store_true", help="Load model in cpu only. Useful if the model cannot fit in GPU memory, " "but this option makes the conversion script significantly slower.")
    args = parser.parse_args()
    return args
def convert_hf_config(sapi_config=None, tokenizer=None, vocab_size=None, dtype=None, hf_output_path=None, hf_url="sapiens/SAPI"):
    DTYPE2HF = {t_bfloat16: "bfloat16", t_float16: "float16", t_float32: "float32"}
    hf_config = {"_name_or_path": hf_url, "architectures": ["SAPIForCausalLM"], "bos_token_id": tokenizer.bos_id, "eos_token_id": tokenizer.eos_id, "hidden_act": {'squared-relu': 'relu2', 'fast-swiglu': 'silu'}[sapi_config.activation],
    "hidden_size": sapi_config.hidden_size, "initializer_range": sapi_config.init_method_std, "intermediate_size": sapi_config.ffn_hidden_size, "max_position_embeddings": sapi_config.max_position_embeddings,
    "model_type": "sapi", "num_attention_heads": sapi_config.num_attention_heads, "num_hidden_layers": sapi_config.num_layers, "num_key_value_heads": sapi_config.get("num_query_groups", sapi_config.num_attention_heads),
    "norm_eps": sapi_config.layernorm_epsilon, "rope_theta": sapi_config.get("rotary_base", 10000), "partial_rotary_factor": sapi_config.get("rotary_percentage", 1.0),
    "tie_word_embeddings": False, "torch_dtype": DTYPE2HF[dtype], "sapiens_transformers_version": "4.32.0.dev0", "use_cache": True, "vocab_size": vocab_size}
    if sapi_config.kv_channels is not None: hf_config["kv_channels"] = sapi_config.kv_channels
    from json import dump
    dump(hf_config, open(f"{hf_output_path}/config.json", "w"), indent=2)
if __name__ == "__main__":
    args = get_args()
    if not args.hf_output_path: assert args.output_path is not None, "Need to provide either output_path or hf_output_path"
    else: args.output_path = f"{args.hf_output_path}/pytorch_model.bin"
    sapi_config, sapi_tokenizer, dtype, vocab_size = convert(args.input_name_or_path, args.output_path, precision=args.precision, cpu_only=args.cpu_only)
    if args.hf_input_path and args.hf_output_path: convert_hf_config(sapi_config, sapi_tokenizer, vocab_size, dtype, args.hf_output_path, args.hf_input_path), extract_sapi_tokenizer(args.input_name_or_path, sapi_config, args.hf_output_path, sapi_tokenizer)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
