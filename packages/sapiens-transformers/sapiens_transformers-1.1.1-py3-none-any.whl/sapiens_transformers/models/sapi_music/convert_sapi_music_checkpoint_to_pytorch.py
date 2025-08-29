"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
MAPPING_48K, MAPPING_24K = {**MAPPING_QUANTIZER, **MAPPING_ENCODER, **MAPPING_ENCODER_48K, **MAPPING_DECODER, **MAPPING_DECODER_48K}, {**MAPPING_QUANTIZER, **MAPPING_ENCODER, **MAPPING_DECODER}
from .sapi_music_import_variables import MAPPING_QUANTIZER, MAPPING_ENCODER, MAPPING_ENCODER_48K, MAPPING_DECODER, MAPPING_DECODER_48K
from sapiens_transformers import (SAPIMusicConfig, SAPIMusicFeatureExtractor, SAPIMusicModel)
from torch import no_grad as t_no_grad, load as t_load
TOP_LEVEL_KEYS, IGNORE_KEYS = [], []
@t_no_grad()
def convert_checkpoint(model_name, checkpoint_path, pytorch_dump_folder_path, config_path=None, repo_id=None):
    if config_path is not None: config = SAPIMusicConfig.from_pretrained(config_path)
    else: config = SAPIMusicConfig()
    model = SAPIMusicModel(config)
    feature_extractor = SAPIMusicFeatureExtractor(feature_size=config.audio_channels, sampling_rate=config.sampling_rate, chunk_length_s=config.chunk_length_s, overlap=config.overlap)
    feature_extractor.save_pretrained(pytorch_dump_folder_path)
    original_checkpoint = t_load(checkpoint_path)
    if "best_state" in original_checkpoint: original_checkpoint = original_checkpoint["best_state"]
    def recursively_load_weights(orig_dict, hf_model, model_name):
        unused_weights = []
        def set_recursively(hf_pointer, key, value, full_name, weight_type):
            for attribute in key.split("."): hf_pointer = getattr(hf_pointer, attribute)
            if weight_type is not None: hf_shape = getattr(hf_pointer, weight_type).shape
            else: hf_shape = hf_pointer.shape
            if hf_shape != value.shape: raise ValueError(f"Shape of hf {key + '.' + weight_type if weight_type is not None else ''} is {hf_shape}, but should be {value.shape} for {full_name}")
            if weight_type == "weight": hf_pointer.weight.data = value
            elif weight_type == "weight_g": hf_pointer.weight_g.data = value
            elif weight_type == "weight_v": hf_pointer.weight_v.data = value
            elif weight_type == "bias": hf_pointer.bias.data = value
            elif weight_type == "running_mean": hf_pointer.running_mean.data = value
            elif weight_type == "running_var": hf_pointer.running_var.data = value
            elif weight_type == "num_batches_tracked": hf_pointer.num_batches_tracked.data = value
            elif weight_type == "weight_ih_l0": hf_pointer.weight_ih_l0.data = value
            elif weight_type == "weight_hh_l0": hf_pointer.weight_hh_l0.data = value
            elif weight_type == "bias_ih_l0": hf_pointer.bias_ih_l0.data = value
            elif weight_type == "bias_hh_l0": hf_pointer.bias_hh_l0.data = value
            elif weight_type == "weight_ih_l1": hf_pointer.weight_ih_l1.data = value
            elif weight_type == "weight_hh_l1": hf_pointer.weight_hh_l1.data = value
            elif weight_type == "bias_ih_l1": hf_pointer.bias_ih_l1.data = value
            elif weight_type == "bias_hh_l1": hf_pointer.bias_hh_l1.data = value
            else: hf_pointer.data = value
        def should_ignore(name, ignore_keys):
            for key in ignore_keys:
                if key.endswith(".*"):
                    if name.startswith(key[:-1]): return True
                elif ".*." in key:
                    prefix, suffix = key.split(".*.")
                    if prefix in name and suffix in name: return True
                elif key in name: return True
            return False
        for name, value in orig_dict.items():
            if should_ignore(name, IGNORE_KEYS): continue
            is_used = False
            for key, mapped_key in MAPPING.items():
                if "*" in key:
                    prefix, suffix = key.split(".*.")
                    if prefix in name and suffix in name: key = suffix
                if key in name:
                    if key.endswith("embed") and name.endswith("embed_avg"): continue
                    is_used = True
                    if "*" in mapped_key: mapped_key = mapped_key.replace("*", name.split(key)[0].split(".")[-2])
                    if "weight_g" in name: weight_type = "weight_g"
                    elif "weight_v" in name: weight_type = "weight_v"
                    elif "weight_ih_l0" in name: weight_type = "weight_ih_l0"
                    elif "weight_hh_l0" in name: weight_type = "weight_hh_l0"
                    elif "bias_ih_l0" in name: weight_type = "bias_ih_l0"
                    elif "bias_hh_l0" in name: weight_type = "bias_hh_l0"
                    elif "weight_ih_l1" in name: weight_type = "weight_ih_l1"
                    elif "weight_hh_l1" in name: weight_type = "weight_hh_l1"
                    elif "bias_ih_l1" in name: weight_type = "bias_ih_l1"
                    elif "bias_hh_l1" in name: weight_type = "bias_hh_l1"
                    elif "bias" in name: weight_type = "bias"
                    elif "weight" in name: weight_type = "weight"
                    elif "running_mean" in name: weight_type = "running_mean"
                    elif "running_var" in name: weight_type = "running_var"
                    elif "num_batches_tracked" in name: weight_type = "num_batches_tracked"
                    else: weight_type = None
                    set_recursively(hf_model, mapped_key, value, name, weight_type)
                continue
            if not is_used: unused_weights.append(name)
    recursively_load_weights(original_checkpoint, model, model_name)
    model.save_pretrained(pytorch_dump_folder_path)
    if repo_id:
        print("Pushing to the hub...")
        feature_extractor.push_to_hub(repo_id)
        model.push_to_hub(repo_id)
if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("--model", default="", type=str, help="The model to convert.")
    parser.add_argument("--checkpoint_path", required=True, default=None, type=str, help="Path to original checkpoint")
    parser.add_argument("--config_path", default=None, type=str, help="Path to hf config.json of model to convert")
    parser.add_argument("--pytorch_dump_folder_path", required=True, default=None, type=str, help="Path to the output PyTorch model.")
    parser.add_argument("--push_to_hub", default=None, type=str, help="Where to upload the converted model.")
    args = parser.parse_args()
    convert_checkpoint(args.model, args.checkpoint_path, args.pytorch_dump_folder_path, args.config_path, args.push_to_hub)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
