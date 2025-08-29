"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import argparse
import os
import torch
from sapiens_transformers.utils import WEIGHTS_NAME
DIALOGPT_MODELS = ["small", "medium", "large"]
OLD_KEY = "lm_head.decoder.weight"
NEW_KEY = "lm_head.weight"
def convert_dialogpt_checkpoint(checkpoint_path: str, pytorch_dump_folder_path: str):
    d = torch.load(checkpoint_path)
    d[NEW_KEY] = d.pop(OLD_KEY)
    os.makedirs(pytorch_dump_folder_path, exist_ok=True)
    torch.save(d, os.path.join(pytorch_dump_folder_path, WEIGHTS_NAME))
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dialogpt_path", default=".", type=str)
    args = parser.parse_args()
    for MODEL in DIALOGPT_MODELS:
        checkpoint_path = os.path.join(args.dialogpt_path, f"{MODEL}_ft.pkl")
        pytorch_dump_folder_path = f"./DialoGPT-{MODEL}"
        convert_dialogpt_checkpoint(checkpoint_path, pytorch_dump_folder_path)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
