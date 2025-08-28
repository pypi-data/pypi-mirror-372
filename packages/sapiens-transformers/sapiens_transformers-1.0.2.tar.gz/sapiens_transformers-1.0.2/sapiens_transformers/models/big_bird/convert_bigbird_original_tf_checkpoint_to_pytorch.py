"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import argparse
from sapiens_transformers import BigBirdConfig, BigBirdForPreTraining, BigBirdForQuestionAnswering, load_tf_weights_in_big_bird
from sapiens_transformers.utils import logging
logging.set_verbosity_info()
def convert_tf_checkpoint_to_pytorch(tf_checkpoint_path, big_bird_config_file, pytorch_dump_path, is_trivia_qa):
    config = BigBirdConfig.from_json_file(big_bird_config_file)
    print(f"Building PyTorch model from configuration: {config}")
    if is_trivia_qa: model = BigBirdForQuestionAnswering(config)
    else: model = BigBirdForPreTraining(config)
    load_tf_weights_in_big_bird(model, tf_checkpoint_path, is_trivia_qa=is_trivia_qa)
    print(f"Save PyTorch model to {pytorch_dump_path}")
    model.save_pretrained(pytorch_dump_path)
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--tf_checkpoint_path", default=None, type=str, required=True, help="Path to the TensorFlow checkpoint path.")
    parser.add_argument("--big_bird_config_file", default=None, type=str, required=True, help=("The config json file corresponding to the pre-trained BERT model. \nThis specifies the model architecture."))
    parser.add_argument("--pytorch_dump_path", default=None, type=str, required=True, help="Path to the output PyTorch model.")
    parser.add_argument("--is_trivia_qa", action="store_true", help="Whether to convert a model with a trivia_qa head.")
    args = parser.parse_args()
    convert_tf_checkpoint_to_pytorch(args.tf_checkpoint_path, args.big_bird_config_file, args.pytorch_dump_path, args.is_trivia_qa)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
