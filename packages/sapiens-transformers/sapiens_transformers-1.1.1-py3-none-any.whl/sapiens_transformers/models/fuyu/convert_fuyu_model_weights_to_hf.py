"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import argparse
import os
import sys
import warnings
import flatdict
import torch
from sapiens_transformers import FuyuConfig, FuyuForCausalLM, LlamaTokenizer
try:
    from sapiens_transformers import LlamaTokenizerFast
    tokenizer_class = LlamaTokenizerFast
except ImportError as e:
    warnings.warn(e)
    warnings.warn("The converted tokenizer will be the `slow` tokenizer. To use the fast, update your `tokenizers` library and re-run the tokenizer conversion")
    tokenizer_class = LlamaTokenizer
KEYS_TO_MODIFY_MAPPING = {'self_attention': 'self_attn', 'language_model.encoder': 'language_model.model', 'word_embeddings_for_head': 'language_model.lm_head', 'language_model.embedding.word_embeddings': 'language_model.model.embed_tokens', 'vit_encoder.linear_encoder': 'vision_embed_tokens'}
KEYS_TO_REMOVE = {'image_patch_projection.weight', 'rotary_emb.inv_freq', 'image_patch_projection.bias', 'image_patch_projection'}
def rename_state_dict(state_dict):
    model_state_dict = {}
    for key, value in state_dict.items():
        for key_to_modify, new_key in KEYS_TO_MODIFY_MAPPING.items():
            if key_to_modify in key: key = key.replace(key_to_modify, new_key)
        if key in KEYS_TO_REMOVE: continue
        model_state_dict[key] = value
    return model_state_dict
def convert_fuyu_checkpoint(pytorch_dump_folder_path, ada_lib_path, pt_model_path, safe_serialization=False):
    sys.path.insert(0, ada_lib_path)
    model_state_dict_base = torch.load(pt_model_path, map_location="cpu")
    state_dict = flatdict.FlatDict(model_state_dict_base["model"], ".")
    state_dict = rename_state_dict(state_dict)
    transformers_config = FuyuConfig()
    model = FuyuForCausalLM(transformers_config).to(torch.bfloat16)
    model.load_state_dict(state_dict)
    model.save_pretrained(pytorch_dump_folder_path, safe_serialization=safe_serialization)
    transformers_config.save_pretrained(pytorch_dump_folder_path)
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", help="Location of Fuyu weights, which contains tokenizer.model and model folders")
    parser.add_argument("--pt_model_path", help="Location of Fuyu `model_optim_rng.pt`")
    parser.add_argument("--output_dir", help="Location to write HF model and tokenizer")
    parser.add_argument("--ada_lib_path", help="Location of original source code from adept to deserialize .pt checkpoint")
    parser.add_argument("--safe_serialization", type=bool, help="Whether or not to save using `safetensors`.")
    args = parser.parse_args()
    spm_path = os.path.join(args.input_dir, "adept_vocab.model")
    convert_fuyu_checkpoint(pytorch_dump_folder_path=args.output_dir, pt_model_path=args.pt_model_path, safe_serialization=args.safe_serialization, ada_lib_path=args.ada_lib_path)
    tokenizer = tokenizer_class(spm_path, bos_token="|ENDOFTEXT|", eos_token="|ENDOFTEXT|")
    tokenizer.save_pretrained(args.output_dir)
if __name__ == "__main__": main()
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
