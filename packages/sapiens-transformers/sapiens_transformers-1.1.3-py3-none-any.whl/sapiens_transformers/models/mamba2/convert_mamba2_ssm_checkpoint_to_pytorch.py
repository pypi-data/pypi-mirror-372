"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import argparse
import json
from functools import partial
from os import path
from typing import Dict, Optional
import torch
from safetensors import safe_open
from safetensors.torch import save_model
from sapiens_transformers import GPTNeoXTokenizerFast, LlamaTokenizerFast, Mamba2Config, Mamba2ForCausalLM
def load_state_dict_from_safetensors(mamba2_checkpoint_path: str, ckpt_name: str) -> Dict[str, torch.Tensor]:
    original_state_dict = {}
    with safe_open(path.join(mamba2_checkpoint_path, ckpt_name), framework="pt") as f:
        for k in f.keys():
            newk = k.removeprefix("model.")
            original_state_dict[newk] = f.get_tensor(k).clone()
    return original_state_dict
def load_state_dict_from_torch(mamba2_checkpoint_path: str, ckpt_name: str) -> Dict[str, torch.Tensor]: return torch.load(path.join(mamba2_checkpoint_path, ckpt_name), map_location="cpu")
def convert_ssm_config_to_hf_config(config_ssm: Dict, mamba2_model_dict: Dict) -> Mamba2Config:
    hf_config = Mamba2Config()
    config_dict = mamba2_model_dict
    hf_config.hidden_size = config_ssm[config_dict["hidden_size"]]
    hf_config.num_heads = (hf_config.hidden_size * hf_config.expand) // hf_config.head_dim
    hf_config.num_hidden_layers = config_ssm[config_dict["num_hidden_layers"]]
    hf_config.n_groups = config_ssm.get(config_dict["n_groups"], 1)
    hf_config.tie_word_embeddings = config_ssm["tie_embeddings"]
    hf_config.bos_token_id = config_dict["bos_token_id"]
    hf_config.pad_token_id = config_dict["pad_token_id"]
    hf_config.eos_token_id = config_dict["eos_token_id"]
    vocab_size = config_ssm["vocab_size"]
    pad_vocab_size_multiple = config_ssm["pad_vocab_size_multiple"]
    if (vocab_size % pad_vocab_size_multiple) != 0: vocab_size += pad_vocab_size_multiple - (vocab_size % pad_vocab_size_multiple)
    hf_config.vocab_size = vocab_size
    return hf_config
def load_and_save_tokenizer(mamba2_model_type: str, output_dir: str, tokenizer_model_path: Optional[str] = None) -> None:
    tokenizer = None
    if tokenizer_model_path is not None and mamba2_model_type == "codestral":
        tokenizer_class = LlamaTokenizerFast
        tokenizer = tokenizer_class(tokenizer_model_path, legacy=False, from_slow=True)
    elif mamba2_model_type == "mamba_ssm": tokenizer = GPTNeoXTokenizerFast.from_pretrained("state-spaces/mamba-130m-hf", padding_side="left")
    if tokenizer is not None: tokenizer.save_pretrained(output_dir)
_MAMBA2_MODELS_DICT = {"codestral": {"hidden_size": "dim", "num_hidden_layers": "n_layers", "n_groups": "n_groups", "bos_token_id": 0, "pad_token_id": 1, "eos_token_id": 2, "config_name": "params.json",
"load_state_dict": partial(load_state_dict_from_safetensors, ckpt_name="consolidated.safetensors"), "load_and_save_tokenizer": partial(load_and_save_tokenizer, "codestral")},
"mamba_ssm": {"hidden_size": "d_model", "num_hidden_layers": "n_layer", "n_groups": "ngroups", "bos_token_id": 0, "pad_token_id": 0, "eos_token_id": 0, "config_name": "config.json",
"load_state_dict": partial(load_state_dict_from_torch, ckpt_name="pytorch_model.bin"), "load_and_save_tokenizer": partial(load_and_save_tokenizer, "mamba_ssm")}}
def convert_mamba2_checkpoint_file_to_huggingface_model_file(mamba2_checkpoint_path: str, mamba2_model_type: str, precision: str, output_dir: str, tokenizer_model_path: Optional[str] = None) -> None:
    mamba2_model_dict = _MAMBA2_MODELS_DICT[mamba2_model_type]
    config_path = path.join(mamba2_checkpoint_path, mamba2_model_dict["config_name"])
    with open(config_path, "r", encoding="utf-8") as json_file: config = json.load(json_file)
    hf_config = convert_ssm_config_to_hf_config(config_ssm=config, mamba2_model_dict=mamba2_model_dict)
    hf_config.save_pretrained(output_dir)
    original_state_dict = mamba2_model_dict["load_state_dict"](mamba2_checkpoint_path=mamba2_checkpoint_path)
    hf_model = Mamba2ForCausalLM(hf_config)
    hf_model.load_state_dict(original_state_dict)
    dtype = torch.float32 if precision == "fp32" else (torch.bfloat16 if precision == "bf16" else torch.float16)
    save_model(hf_model.to(dtype), path.join(output_dir, "model.safetensors"), metadata={"format": "pt"})
    mamba2_model_dict["load_and_save_tokenizer"](output_dir=output_dir, tokenizer_model_path=tokenizer_model_path)
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--mamba2_checkpoint_directory", type=str, required=True, help="Path to a directory containing the `pytorch_model.bin` or `.safetensors` mamba2_ssm checkpoint file to be converted.")
    parser.add_argument("-m", "--mamba2_model_type", type=str, default="mamba_ssm", const="mamba_ssm", required=True, choices=("codestral", "mamba_ssm"), help="The model type the conversion will be performed on. Can choose from either `codestral` or `mamba_ssm`.")
    parser.add_argument("-p", "--precision", type=str, default="fp16", const="fp16", required=True, choices=("fp32", "fp16", "bf16"), help="The precision the model will be saved in. Select from fp32, fp16 or bf16.")
    parser.add_argument("-o", "--output_dir", type=str, required=True, help="Path to directory to save the converted output model to.")
    parser.add_argument("-t", "--tokenizer_model_path", type=str, default=None, required=False, help="Path to a `codestral` tokenizer file.")
    args = parser.parse_args()
    convert_mamba2_checkpoint_file_to_huggingface_model_file(args.mamba2_checkpoint_directory, args.mamba2_model_type, args.precision, args.output_dir, args.tokenizer_model_path)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
