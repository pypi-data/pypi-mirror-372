"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import argparse
import torch
from sapiens_transformers import ImageGPTConfig, ImageGPTForCausalLM, load_tf_weights_in_imagegpt
from sapiens_transformers.utils import CONFIG_NAME, WEIGHTS_NAME, logging
logging.set_verbosity_info()
def convert_imagegpt_checkpoint_to_pytorch(imagegpt_checkpoint_path, model_size, pytorch_dump_folder_path):
    MODELS = {"small": (512, 8, 24), "medium": (1024, 8, 36), "large": (1536, 16, 48)}
    n_embd, n_head, n_layer = MODELS[model_size]
    config = ImageGPTConfig(n_embd=n_embd, n_layer=n_layer, n_head=n_head)
    model = ImageGPTForCausalLM(config)
    load_tf_weights_in_imagegpt(model, config, imagegpt_checkpoint_path)
    pytorch_weights_dump_path = pytorch_dump_folder_path + "/" + WEIGHTS_NAME
    pytorch_config_dump_path = pytorch_dump_folder_path + "/" + CONFIG_NAME
    print(f"Save PyTorch model to {pytorch_weights_dump_path}")
    torch.save(model.state_dict(), pytorch_weights_dump_path)
    print(f"Save configuration file to {pytorch_config_dump_path}")
    with open(pytorch_config_dump_path, "w", encoding="utf-8") as f: f.write(config.to_json_string())
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--imagegpt_checkpoint_path", default=None, type=str, required=True, help="Path to the TensorFlow checkpoint path.")
    parser.add_argument("--model_size", default=None, type=str, required=True, help="Size of the model (can be either 'small', 'medium' or 'large').")
    parser.add_argument("--pytorch_dump_folder_path", default=None, type=str, required=True, help="Path to the output PyTorch model.")
    args = parser.parse_args()
    convert_imagegpt_checkpoint_to_pytorch(args.imagegpt_checkpoint_path, args.model_size, args.pytorch_dump_folder_path)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
