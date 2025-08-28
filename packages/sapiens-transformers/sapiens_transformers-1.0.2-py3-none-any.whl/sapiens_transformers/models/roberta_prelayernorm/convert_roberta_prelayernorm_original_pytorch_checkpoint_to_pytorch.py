"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import argparse
import torch
from huggingface_hub import hf_hub_download
from sapiens_transformers import AutoTokenizer, RobertaPreLayerNormConfig, RobertaPreLayerNormForMaskedLM
from sapiens_transformers.utils import logging
logging.set_verbosity_info()
logger = logging.get_logger(__name__)
def convert_roberta_prelayernorm_checkpoint_to_pytorch(checkpoint_repo: str, pytorch_dump_folder_path: str):
    config = RobertaPreLayerNormConfig.from_pretrained(checkpoint_repo, architectures=["RobertaPreLayerNormForMaskedLM"])
    original_state_dict = torch.load(hf_hub_download(repo_id=checkpoint_repo, filename="pytorch_model.bin"))
    state_dict = {}
    for tensor_key, tensor_value in original_state_dict.items():
        if tensor_key.startswith("roberta."): tensor_key = "roberta_prelayernorm." + tensor_key[len("roberta.") :]
        if tensor_key.endswith(".self.LayerNorm.weight") or tensor_key.endswith(".self.LayerNorm.bias"): continue
        state_dict[tensor_key] = tensor_value
    model = RobertaPreLayerNormForMaskedLM.from_pretrained(pretrained_model_name_or_path=None, config=config, state_dict=state_dict)
    model.save_pretrained(pytorch_dump_folder_path)
    tokenizer = AutoTokenizer.from_pretrained(checkpoint_repo)
    tokenizer.save_pretrained(pytorch_dump_folder_path)
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint-repo", default=None, type=str, required=True, help="Path the official PyTorch dump, e.g. 'andreasmadsen/efficient_mlm_m0.40'.")
    parser.add_argument("--pytorch_dump_folder_path", default=None, type=str, required=True, help="Path to the output PyTorch model.")
    args = parser.parse_args()
    convert_roberta_prelayernorm_checkpoint_to_pytorch(args.checkpoint_repo, args.pytorch_dump_folder_path)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
