"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import argparse
import json
import math
from typing import Tuple
import torch
from sapiens_transformers import AutoTokenizer, MambaConfig, MambaForCausalLM
from sapiens_transformers.utils import logging
from sapiens_transformers.utils.import_utils import is_mamba_ssm_available
if is_mamba_ssm_available():
    from mamba_ssm.models.config_mamba import MambaConfig as MambaConfigSSM
    from mamba_ssm.models.mixer_seq_simple import MambaLMHeadModel
    def convert_ssm_config_to_hf_config(config_ssm: MambaConfigSSM) -> MambaConfig:
        hf_config = MambaConfig()
        hf_config.hidden_size = config_ssm.d_model
        hf_config.intermediate_size = config_ssm.d_model * 2
        hf_config.time_step_rank = math.ceil(config_ssm.d_model / 16)
        hf_config.num_hidden_layers = config_ssm.n_layer
        vocab_size = config_ssm.vocab_size
        pad_vocab_size_multiple = config_ssm.pad_vocab_size_multiple
        if (vocab_size % pad_vocab_size_multiple) != 0: vocab_size += pad_vocab_size_multiple - (vocab_size % pad_vocab_size_multiple)
        hf_config.vocab_size = vocab_size
        return hf_config
logging.set_verbosity_info()
logger = logging.get_logger(__name__)
def convert_mamba_ssm_checkpoint_to_huggingface_model(original_state_dict: dict, original_ssm_config_dict: dict) -> Tuple[MambaForCausalLM, AutoTokenizer]:
    if not is_mamba_ssm_available(): raise ImportError("Calling convert_mamba_ssm_checkpoint_to_huggingface_model requires the mamba_ssm library to be installed. Please install it with `pip install mamba_ssm`.")
    original_ssm_config = MambaConfigSSM(**original_ssm_config_dict)
    hf_config = convert_ssm_config_to_hf_config(original_ssm_config)
    converted_state_dict = original_state_dict
    hf_model = MambaForCausalLM(hf_config)
    tokenizer = AutoTokenizer.from_pretrained("EleutherAI/gpt-neox-20b")
    hf_model.load_state_dict(converted_state_dict)
    return (hf_model, tokenizer)
def validate_converted_model(original_state_dict: dict, original_ssm_config_dict: dict, hf_model: MambaForCausalLM, tokenizer: AutoTokenizer) -> None:
    torch_device = "cuda"
    original_config = MambaConfigSSM(**original_ssm_config_dict)
    original_model = MambaLMHeadModel(original_config).to(torch_device)
    original_model.load_state_dict(original_state_dict)
    hf_model = hf_model.to(torch_device)
    input_ids = tokenizer("Hey how are you doing?", return_tensors="pt")["input_ids"].to(torch_device)
    with torch.no_grad():
        original_model_logits = original_model(input_ids).logits
        hf_model_logits = hf_model(input_ids).logits
    if not torch.allclose(original_model_logits, hf_model_logits, atol=1e-3): raise ValueError("The converted model did not return the same logits as the original model.")
    logger.info("Model conversion validated successfully.")
def convert_mamba_checkpoint_file_to_huggingface_model_file(mamba_checkpoint_path: str, config_json_file: str, output_dir: str) -> None:
    if not is_mamba_ssm_available(): raise ImportError("Calling convert_mamba_checkpoint_file_to_huggingface_model_file requires the mamba_ssm library to be installed. Please install it with `pip install mamba_ssm`.")
    if not torch.cuda.is_available(): raise ValueError("This script is to be run with a CUDA device, as the original mamba_ssm model does not support cpu.")
    logger.info(f"Loading model from {mamba_checkpoint_path} based on config from {config_json_file}")
    original_state_dict = torch.load(mamba_checkpoint_path, map_location="cpu")
    with open(config_json_file, "r", encoding="utf-8") as json_file: original_ssm_config_dict = json.load(json_file)
    hf_model, tokenizer = convert_mamba_ssm_checkpoint_to_huggingface_model(original_state_dict, original_ssm_config_dict)
    validate_converted_model(original_state_dict, original_ssm_config_dict, hf_model, tokenizer)
    logger.info(f"Model converted successfully. Saving model to {output_dir}")
    hf_model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--mamba_checkpoint_file", type=str, required=True, help="Path to a `pytorch_model.bin` mamba_ssm checkpoint file to be converted.")
    parser.add_argument("-c", "--config_json_file", type=str, required=True, help="Path to a `config.json` file corresponding to a MambaConfig of the original mamba_ssm model.")
    parser.add_argument("-o", "--output_dir", type=str, required=True, help="Path to directory to save the converted output model to.")
    args = parser.parse_args()
    convert_mamba_checkpoint_file_to_huggingface_model_file(args.mamba_checkpoint_file, args.config_json_file, args.output_dir)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
