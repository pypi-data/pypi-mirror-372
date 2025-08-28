"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import argparse
import torch
from sapiens_transformers import OpenAIGPTConfig, OpenAIGPTModel, load_tf_weights_in_openai_gpt
from sapiens_transformers.utils import CONFIG_NAME, WEIGHTS_NAME, logging
logging.set_verbosity_info()
def convert_openai_checkpoint_to_pytorch(openai_checkpoint_folder_path, openai_config_file, pytorch_dump_folder_path):
    if openai_config_file == "": config = OpenAIGPTConfig()
    else: config = OpenAIGPTConfig.from_json_file(openai_config_file)
    model = OpenAIGPTModel(config)
    load_tf_weights_in_openai_gpt(model, config, openai_checkpoint_folder_path)
    pytorch_weights_dump_path = pytorch_dump_folder_path + "/" + WEIGHTS_NAME
    pytorch_config_dump_path = pytorch_dump_folder_path + "/" + CONFIG_NAME
    print(f"Save PyTorch model to {pytorch_weights_dump_path}")
    torch.save(model.state_dict(), pytorch_weights_dump_path)
    print(f"Save configuration file to {pytorch_config_dump_path}")
    with open(pytorch_config_dump_path, "w", encoding="utf-8") as f: f.write(config.to_json_string())
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--openai_checkpoint_folder_path", default=None, type=str, required=True, help="Path to the TensorFlow checkpoint path.")
    parser.add_argument("--pytorch_dump_folder_path", default=None, type=str, required=True, help="Path to the output PyTorch model.")
    parser.add_argument("--openai_config_file", default="", type=str, help=("An optional config json file corresponding to the pre-trained OpenAI model. \nThis specifies the model architecture."))
    args = parser.parse_args()
    convert_openai_checkpoint_to_pytorch(args.openai_checkpoint_folder_path, args.openai_config_file, args.pytorch_dump_folder_path)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
