"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from os import makedirs, path as _path
from json import load, dump
from sapiens_transformers.models.modular_entity.configuration_modular_entity import ModularEntityTextConfig, ModularEntityVisionConfig
from sapiens_transformers.models.modular_entity.image_processing_modular_entity import get_all_supported_aspect_ratios
from sapiens_transformers import (ModularEntityConfig, ModularEntityForConditionalGeneration, GenerationConfig, PreTrainedTokenizerFast, ModularEntityImageProcessor)
import torch.nn.functional as Functional
from typing import Optional, List
CONTEXT_LENGTH, ORIGINAL_TO_CONVERTED_KEY_MAPPING = 131072, {'text_model.norm.weight': 'language_model.model.norm.weight', 'text_model.output.weight': 'language_model.lm_head.weight',
'text_model.tok_embeddings': 'language_model.model.embed_tokens', 'text_model.learnable_embedding': 'language_model.model.learnable_embedding', 'text_model.rope.freqs': None,
'text_model.cross_attention_layers.(\\d+).gate_attn': 'language_model.model.layers.\\1.cross_attn_attn_gate', 'text_model.cross_attention_layers.(\\d+).gate_ffwd': 'language_model.model.layers.\\1.cross_attn_mlp_gate',
'text_model.cross_attention_layers.(\\d+).attention.w(q|k|v|o)': 'language_model.model.layers.\\1.cross_attn.\\2_proj', 'text_model.cross_attention_layers.(\\d+).attention.(q|k)_norm': 'language_model.model.layers.\\1.cross_attn.\\2_norm',
'text_model.cross_attention_layers.(\\d+).attention_norm.weight': 'language_model.model.layers.\\1.input_layernorm.weight', 'text_model.cross_attention_layers.(\\d+).attention.wk.layer_norm_weight': 'language_model.model.layers.\\1.post_attention_layernorm.weight',
'text_model.cross_attention_layers.(\\d+).feed_forward.w1.weight': 'language_model.model.layers.\\1.mlp.gate_proj.weight', 'text_model.cross_attention_layers.(\\d+).feed_forward.w2.weight': 'language_model.model.layers.\\1.mlp.down_proj.weight',
'text_model.cross_attention_layers.(\\d+).feed_forward.w3.weight': 'language_model.model.layers.\\1.mlp.up_proj.weight', 'text_model.cross_attention_layers.(\\d+).ffn_norm.weight': 'language_model.model.layers.\\1.post_attention_layernorm.weight',
'text_model.layers.(\\d+).attention.w(q|k|v|o).weight': 'language_model.model.layers.\\1.self_attn.\\2_proj.weight', 'text_model.layers.(\\d+).attention_norm.weight': 'language_model.model.layers.\\1.input_layernorm.weight',
'text_model.layers.(\\d+).feed_forward.w1.': 'language_model.model.layers.\\1.mlp.gate_proj.', 'text_model.layers.(\\d+).feed_forward.w2.': 'language_model.model.layers.\\1.mlp.down_proj.', 'text_model.layers.(\\d+).feed_forward.w3.': 'language_model.model.layers.\\1.mlp.up_proj.',
'text_model.layers.(\\d+).ffn_norm.weight': 'language_model.model.layers.\\1.post_attention_layernorm.weight', 'vision_model.vision_encoder.conv1._linear': 'vision_model.patch_embedding', 'vision_model.vision_projection.': 'multi_modal_projector.',
'vision_model.vision_encoder.(global_transformer|transformer).resblocks.(\\d+).attn.wq': 'vision_model.\\1.layers.\\2.self_attn.q_proj', 'vision_model.vision_encoder.(global_transformer|transformer).resblocks.(\\d+).attn.wk': 'vision_model.\\1.layers.\\2.self_attn.k_proj',
'vision_model.vision_encoder.(global_transformer|transformer).resblocks.(\\d+).attn.wv': 'vision_model.\\1.layers.\\2.self_attn.v_proj', 'vision_model.vision_encoder.(global_transformer|transformer).resblocks.(\\d+).attn.wo': 'vision_model.\\1.layers.\\2.self_attn.o_proj',
'vision_model.vision_encoder.(global_transformer|transformer).resblocks.(\\d+).mlp.c_fc': 'vision_model.\\1.layers.\\2.mlp.fc1', 'vision_model.vision_encoder.(global_transformer|transformer).resblocks.(\\d+).mlp.c_proj': 'vision_model.\\1.layers.\\2.mlp.fc2',
'vision_model.vision_encoder.(global_transformer|transformer).resblocks.(\\d+).ln_1': 'vision_model.\\1.layers.\\2.input_layernorm', 'vision_model.vision_encoder.(global_transformer|transformer).resblocks.(\\d+).ln_2': 'vision_model.\\1.layers.\\2.post_attention_layernorm',
'vision_model.vision_encoder.global_transformer.resblocks.(\\d+).(gate_ffn|gate_attn)': 'vision_model.global_transformer.layers.\\1.\\2', 'vision_model.vision_encoder.ln_(pre|post).(weight|bias)': 'vision_model.vision_encoder.layernorm_\\1.\\2',
'vision_model.vision_encoder.positional_embedding\\b': 'vision_model.gated_positional_embedding.embedding', 'vision_model.vision_encoder.gated_positional_embedding\\b': 'vision_model.gated_positional_embedding.tile_embedding.weight',
'vision_model.vision_encoder.gated_positional_embedding_gate': 'vision_model.gated_positional_embedding.gate', 'vision_model.vision_encoder.pre_tile_pos_embed.embedding': 'vision_model.pre_tile_positional_embedding.embedding.weight',
'vision_model.vision_encoder.post_tile_pos_embed.embedding': 'vision_model.post_tile_positional_embedding.embedding.weight', 'vision_model.vision_encoder.pre_tile_pos_embed.gate': 'vision_model.pre_tile_positional_embedding.gate',
'vision_model.vision_encoder.post_tile_pos_embed.gate': 'vision_model.post_tile_positional_embedding.gate', 'vision_model.vision_encoder.(?=\\w)': 'vision_model.'}
def write_model(model_path, input_base_path, num_shards, safe_serialization=True, instruct=False):
    makedirs(model_path, exist_ok=True)
    with open(_path.join(input_base_path, "params.json"), "r") as f: params = load(f)
    params = params.get("model", params)
    torch_dtype, text_vocab_size, text_num_layers = "bfloat16", params["vocab_size"], params["n_layers"]
    text_dim, text_num_heads, text_rms_norm_eps = params["dim"], params["n_heads"], params["norm_eps"]
    text_rope_theta, cross_attention_num_layers = params["rope_theta"], params["vision_num_cross_attention_layers"]
    rope_scaling = {'rope_type': 'entity', 'factor': 8.0, 'low_freq_factor': 1.0, 'high_freq_factor': 4.0, 'original_max_position_embeddings': 8192}
    max_position_embeddings, text_num_heads_per_shard, text_dim_per_head = CONTEXT_LENGTH, text_num_heads // num_shards, text_dim // text_num_heads
    def compute_intermediate_size(hidden_dim, multiple_of=1024, ffn_dim_multiplier=1.3): return multiple_of * ((int(ffn_dim_multiplier * (4 * int(2 * hidden_dim / 3))) + multiple_of - 1) // multiple_of)
    text_intermediate_size = compute_intermediate_size(text_dim, multiple_of=params["multiple_of"])
    if params.get("n_kv_heads", None) is not None:
        text_num_key_value_heads = params["n_kv_heads"]
        text_num_key_value_heads_per_shard, text_key_value_dim = text_num_key_value_heads // num_shards, text_dim_per_head * text_num_key_value_heads
    else: text_num_key_value_heads, text_num_key_value_heads_per_shard, text_key_value_dim = text_num_heads, text_num_heads_per_shard, text_dim
    from math import ceil
    cross_attention_frequency, text_num_total_layers = ceil(text_num_layers / cross_attention_num_layers), text_num_layers + cross_attention_num_layers
    self_attention_layers_shift = [k for k in range(text_num_total_layers) if k not in list(range(cross_attention_frequency - 1, text_num_total_layers, cross_attention_frequency + 1))]
    bos_token_id, eos_token_id, pad_token_id = 128000, [128001, 128008, 128009] if instruct else 128001, 128004
    text_config = ModularEntityTextConfig(num_attention_heads=text_num_heads, vocab_size=text_vocab_size, hidden_size=text_dim, rms_norm_eps=text_rms_norm_eps, rope_theta=text_rope_theta,
    num_hidden_layers=text_num_total_layers, cross_attention_layers=cross_attention_layers_shift, intermediate_size=text_intermediate_size, max_position_embeddings=max_position_embeddings,
    rope_scaling=rope_scaling, bos_token_id=bos_token_id, eos_token_id=eos_token_id, pad_token_id=pad_token_id, tie_word_embeddings=False, torch_dtype=torch_dtype)
    vision_tile_size, vision_max_num_tiles = params["vision_chunk_size"], params["vision_max_num_chunks"]
    vision_patch_size, vision_num_channels, vision_num_layers, vision_num_layers_global, vision_dim, vision_num_heads = 14, 3, 32, 8, 1280, 16
    vision_intermediate_layers_indices, vision_dim_per_head, vision_num_heads_per_shard = [3, 7, 15, 23, 30], vision_dim // vision_num_heads, vision_num_heads // num_shards
    vision_intermediate_size, vision_supported_aspect_ratios = vision_dim * 4, get_all_supported_aspect_ratios(vision_max_num_tiles)
    vision_config = ModularEntityVisionConfig(hidden_size=vision_dim, patch_size=vision_patch_size, num_channels=vision_num_channels, intermediate_size=vision_intermediate_size,
    num_hidden_layers=vision_num_layers, num_attention_heads=vision_num_heads, num_global_layers=vision_num_layers_global, intermediate_layers_indices=vision_intermediate_layers_indices,
    image_size=vision_tile_size, max_num_tiles=vision_max_num_tiles, supported_aspect_ratios=vision_supported_aspect_ratios, torch_dtype=torch_dtype)
    config = ModularEntityConfig(vision_config=vision_config, text_config=text_config, torch_dtype=torch_dtype)
    config.architectures = ["ModularEntityForConditionalGeneration"]
    config.save_pretrained(model_path)
    print("Model config saved successfully...")
    print(f"Fetching all parameters from the checkpoint at {input_base_path}...")
    from torch import load as t_load, Tensor as t_Tensor, cat as t_cat, zeros as t_zeros, device as t_device, bfloat16 as t_bfloat16
    if num_shards == 1: loaded = [t_load(_path.join(input_base_path, "consolidated.pth"), map_location="cpu", mmap=True)]
    else: loaded = [t_load(_path.join(input_base_path, f"consolidated.{i:02d}.pth"), map_location="cpu", mmap=True) for i in range(num_shards)]
    print("Converting model...")
    from regex import sub, search
    def convert_old_keys_to_new_keys(state_dict_keys: dict = None):
        output_dict = {}
        if state_dict_keys is not None:
            old_text = "\n".join(state_dict_keys)
            new_text = old_text
            for pattern, replacement in ORIGINAL_TO_CONVERTED_KEY_MAPPING.items():
                if replacement is None:
                    new_text = sub(pattern, "", new_text)
                    continue
                new_text = sub(pattern, replacement, new_text)
            output_dict = dict(zip(old_text.split("\n"), new_text.split("\n")))
        return output_dict
    def permute_for_rope(input_tensor, n_heads, dim1, dim2): return input_tensor.reshape(dim1, dim2).view(n_heads, dim1 // n_heads // 2, 2, dim2).transpose(1, 2).reshape(dim1, dim2)
    def is_param_different_across_shards(key): return any(search(pattern, key) for pattern in [r"vision_model.patch_embedding.weight",r"vision_model.(transformer|global_transformer).layers.(\d+).self_attn.(q|k|v|o)_proj.weight",r"vision_model.(transformer|global_transformer).layers.(\d+).mlp.fc1.(weight|bias)",r"vision_model.(transformer|global_transformer).layers.(\d+).mlp.fc2.weight",  r"multi_modal_projector.(weight|bias)",r"language_model.model.embed_tokens.weight",r"language_model.lm_head.weight",r"language_model.model.layers.(\d+).self_attn.(q|k|v|o)_proj.weight",r"language_model.model.layers.(\d+).cross_attn.(q|k|v|o)_proj.weight",r"language_model.model.layers.(\d+).mlp.(up|down|gate)_proj.weight",r"language_model.model.learnable_embedding.weight"])
    def get_concat_dim(key): return 1 if any(search(pattern, key) for pattern in [r"vision_model.(transformer|global_transformer).layers.(\d+).mlp.fc2.weight",r"vision_model.(transformer|global_transformer).layers.(\d+).self_attn.o_proj.weight",r"language_model.model.layers.(\d+).cross_attn.o_proj.weight",r"language_model.model.layers.(\d+).self_attn.o_proj.weight",r"language_model.model.layers.(\d+).mlp.down_proj.weight"]) else 0
    def interpolate_positional_embedding(embeddings: t_Tensor, vision_tile_size: int, vision_patch_size: int) -> t_Tensor:
        cls_embedding, positional_embedding = embeddings[:1], embeddings[1:]
        total_num_patches, dim = positional_embedding.shape
        num_patches, new_num_patches = int(round(total_num_patches**0.5)), vision_tile_size // vision_patch_size
        if num_patches == new_num_patches: return embeddings
        return t_cat([cls_embedding, Functional.interpolate(positional_embedding.transpose(0, 1).reshape(1, dim, num_patches, num_patches), size=(new_num_patches, new_num_patches), mode="bicubic", align_corners=False).reshape(dim, -1).transpose(0, 1)], dim=0)
    def pre_compute_positional_embedding(embedding):
        max_num_tiles, *shapes = embedding.shape
        hidden_size, supported_aspect_ratios = shapes[-1], get_all_supported_aspect_ratios(max_num_tiles)
        max_aspect_ratio_id, num_patches = len(supported_aspect_ratios), 1 if len(shapes) == 2 else shapes[1]
        precomputed_embeddings = t_zeros(max_aspect_ratio_id + 1, max_num_tiles, num_patches, hidden_size, device=embedding.device, dtype=embedding.dtype)
        for i, (height, width) in enumerate(supported_aspect_ratios): precomputed_embeddings[i + 1, : height * width] = embedding[:height, :width].reshape(height * width, num_patches, hidden_size)
        return precomputed_embeddings.flatten(1)
    all_keys = list(loaded[0].keys())
    new_keys, state_dict = convert_old_keys_to_new_keys(all_keys), {}
    for key in all_keys:
        new_key = new_keys[key]
        if ("cross_attention" in key or "text_model.layers" in key) and "language_model" in new_key:
            shift = cross_attention_layers_shift if "cross_attention" in key else self_attention_layers_shift
            new_key = sub(r"layers.(\d+).", lambda _match: f"layers.{shift[int(_match.groups()[0])]}.", new_key)
        current_parameter = [chunk.pop(key).contiguous().clone() for chunk in loaded]
        if not is_param_different_across_shards(new_key): current_parameter = current_parameter[0]
        concat_dim = get_concat_dim(new_key)
        if search("(k|v|q)_proj.weight", new_key) and "language_model" in new_key:
            if "q_proj" in new_key: param_num_heads, param_num_head_per_shard, param_dim = text_num_heads, text_num_heads_per_shard, text_dim
            else: param_num_heads, param_num_head_per_shard, param_dim = text_num_key_value_heads, text_num_key_value_heads_per_shard, text_key_value_dim
            current_parameter = t_cat([param.view(param_num_head_per_shard, text_dim_per_head, text_dim) for param in current_parameter], dim=concat_dim)
            if "cross_attn" not in new_key and "v_proj.weight" not in new_key: current_parameter = permute_for_rope(current_parameter, param_num_heads, param_dim, text_dim)
            state_dict[new_key] = current_parameter.reshape(param_num_heads * text_dim_per_head, text_dim)
        elif "vision_model" in new_key and search("(k|v|q)_proj", new_key): state_dict[new_key] = t_cat([param.view(vision_num_heads_per_shard, vision_dim_per_head, vision_dim) for param in current_parameter], dim=concat_dim).reshape(vision_num_heads * vision_dim_per_head, vision_dim)
        elif new_key == "vision_model.patch_embedding.weight": state_dict[new_key] = t_cat(current_parameter, dim=concat_dim).reshape(-1, vision_num_channels, vision_patch_size, vision_patch_size)
        elif new_key.endswith("gate"): state_dict[new_key] = current_parameter[0].view(1)
        elif "vision_model.gated_positional_embedding.embedding" in new_key: state_dict[new_key] = interpolate_positional_embedding(current_parameter, vision_tile_size, vision_patch_size)
        elif "vision_model.gated_positional_embedding.tile_embedding.weight" in new_key: state_dict[new_key] = pre_compute_positional_embedding(interpolate_positional_embedding(current_parameter.permute(2, 0, 1, 3).flatten(1), vision_tile_size, vision_patch_size).reshape(-1, vision_max_num_tiles, vision_max_num_tiles, vision_dim).permute(1, 2, 0, 3))
        elif "tile_positional_embedding.embedding" in new_key: state_dict[new_key] = pre_compute_positional_embedding(current_parameter)
        elif new_key != "":
            if isinstance(current_parameter, list): current_parameter = t_cat(current_parameter, dim=concat_dim)
            state_dict[new_key] = current_parameter
    state_dict["language_model.model.embed_tokens.weight"] = t_cat([state_dict["language_model.model.embed_tokens.weight"], state_dict.pop("language_model.model.learnable_embedding.weight")], dim=0)
    del loaded
    from gc import collect
    collect()
    print("Loading the checkpoint in a ModularEntity model.")
    with t_device("meta"): model = ModularEntityForConditionalGeneration(config)
    model.load_state_dict(state_dict, strict=True, assign=True)
    print("Checkpoint loaded successfully.")
    del model.config._name_or_path
    print("Saving the model.")
    model.save_pretrained(model_path, safe_serialization=safe_serialization)
    del state_dict, model
    collect()
    print("Reloading the model to check if it's saved correctly.")
    ModularEntityForConditionalGeneration.from_pretrained(model_path, torch_dtype=t_bfloat16, device_map="auto")
    print("Model reloaded successfully.")
    if instruct: GenerationConfig(do_sample=True, temperature=0.6, top_p=0.9, bos_token_id=bos_token_id, eos_token_id=eos_token_id, pad_token_id=pad_token_id).save_pretrained(model_path)
from sapiens_transformers.convert_slow_tokenizer import TikTokenConverter
class ModularEntityConverter(TikTokenConverter):
    def __init__(self, vocab_file, special_tokens: List[str], pattern: str, model_max_length: int, chat_template: Optional[str] = None, **kwargs):
        super().__init__(vocab_file, pattern=pattern)
        self.additional_special_tokens = special_tokens
        tokenizer = self.converted()
        if chat_template is not None: kwargs["chat_template"] = chat_template
        self.tokenizer = PreTrainedTokenizerFast(tokenizer_object=tokenizer, model_input_names=["input_ids", "attention_mask"], model_max_length=model_max_length, **kwargs)
def write_tokenizer(tokenizer_path: str, save_dir: str, instruct: bool = False):
    model_max_length = CONTEXT_LENGTH
    pattern = r"(?i:'s|'t|'re|'ve|'m|'ll|'d)|[^\r\n\p{L}\p{N}]?\p{L}+|\p{N}{1,3}| ?[^\s\p{L}\p{N}]+[\r\n]*|\s*[\r\n]+|\s+(?!\S)|\s+"
    num_reserved_special_tokens = 256
    special_tokens = ["<|begin_of_text|>", "<|end_of_text|>", "<|reserved_special_token_0|>", "<|reserved_special_token_1|>", "<|finetune_right_pad_id|>",
    "<|step_id|>", "<|start_header_id|>", "<|end_header_id|>", "<|eom_id|>", "<|eot_id|>", "<|python_tag|>"]
    special_tokens += [f"<|reserved_special_token_{i + 2}|>" for i in range(num_reserved_special_tokens - len(special_tokens))]
    special_tokens.append("<|image|>")
    chat_template = (
        "{% for message in messages %}"
        "{% if loop.index0 == 0 %}"
        "{{ bos_token }}"
        "{% endif %}"
        "{{ '<|start_header_id|>' + message['role'] + '<|end_header_id|>\n\n' }}"
        "{% if message['content'] is string %}"
        "{{ message['content'] }}"
        "{% else %}"
        "{% for content in message['content'] %}"
        "{% if content['type'] == 'image' %}"
        "{{ '<|image|>' }}"
        "{% elif content['type'] == 'text' %}"
        "{{ content['text'] }}"
        "{% endif %}"
        "{% endfor %}"
        "{% endif %}"
        "{{ '<|eot_id|>' }}"
        "{% endfor %}"
        "{% if add_generation_prompt %}"
        "{{ '<|start_header_id|>assistant<|end_header_id|>\n\n' }}"
        "{% endif %}"
    )
    converter = ModularEntityConverter(vocab_file=tokenizer_path, pattern=pattern, special_tokens=special_tokens, model_max_length=model_max_length, chat_template=chat_template if instruct else None,
    bos_token="<|begin_of_text|>", eos_token="<|end_of_text|>" if not instruct else "<|eot_id|>", pad_token="<|finetune_right_pad_id|>")
    tokenizer = converter.tokenizer
    tokenizer.save_pretrained(save_dir)
    if instruct:
        print("Saving chat template...")
        chat_template_path = _path.join(save_dir, "chat_template.json")
        with open(chat_template_path, "w") as file: dump({"chat_template": chat_template}, file, indent=2)
def write_image_processor(config_path: str, save_dir: str):
    with open(config_path, "r") as f: params = load(f)
    tile_size, max_image_tiles = params["vision_chunk_size"], params["vision_max_num_chunks"]
    image_processor = ModularEntityImageProcessor(do_resize=True, size={"height": tile_size, "width": tile_size}, do_rescale=True, rescale_factor=1 / 255, do_normalize=True,
    image_mean=[0.48145466, 0.4578275, 0.40821073], image_std=[0.26862954, 0.26130258, 0.27577711], do_pad=True, max_image_tiles=max_image_tiles)
    image_processor.save_pretrained(save_dir)
def main():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("--input_dir", default="", help="Location of Entity weights, which contains tokenizer.model and model folders")
    parser.add_argument("--output_dir", default="", help="Location to write Sapiens model and tokenizer")
    parser.add_argument("--safe_serialization", default=True, type=bool, help="Whether or not to save using `safetensors`.")
    parser.add_argument("--special_tokens", default=None, type=List[str], help="The list of special tokens that should be added to the model.")
    parser.add_argument("--num_shards", default=1, type=int, help="The number of individual shards used for the model. Does not have to be the same as the number of consolidated_xx.pth")
    parser.add_argument("--instruct", action="store_true", help="Whether the model is an instruct model")
    args = parser.parse_args()
    write_model(model_path=args.output_dir, input_base_path=args.input_dir, safe_serialization=args.safe_serialization, num_shards=args.num_shards, instruct=args.instruct)
    write_tokenizer(tokenizer_path=_path.join(args.input_dir, "tokenizer.model"), save_dir=args.output_dir, instruct=args.instruct)
    write_image_processor(config_path=_path.join(args.input_dir, "params.json"), save_dir=args.output_dir)
if __name__ == "__main__": main()
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
