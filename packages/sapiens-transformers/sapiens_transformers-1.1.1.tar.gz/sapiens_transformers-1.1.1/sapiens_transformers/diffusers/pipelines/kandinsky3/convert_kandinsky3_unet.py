'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import argparse
import fnmatch
from safetensors.torch import load_file
from ... import Kandinsky3UNet
MAPPING = {'to_time_embed.1': 'time_embedding.linear_1', 'to_time_embed.3': 'time_embedding.linear_2', 'in_layer': 'conv_in', 'out_layer.0': 'conv_norm_out', 'out_layer.2': 'conv_out',
'down_samples': 'down_blocks', 'up_samples': 'up_blocks', 'projection_lin': 'encoder_hid_proj.projection_linear', 'projection_ln': 'encoder_hid_proj.projection_norm',
'feature_pooling': 'add_time_condition', 'to_query': 'to_q', 'to_key': 'to_k', 'to_value': 'to_v', 'output_layer': 'to_out.0', 'self_attention_block': 'attentions.0'}
DYNAMIC_MAP = {'resnet_attn_blocks.*.0': 'resnets_in.*', 'resnet_attn_blocks.*.1': ('attentions.*', 1), 'resnet_attn_blocks.*.2': 'resnets_out.*'}
def convert_state_dict(unet_state_dict):
    """Returns:"""
    converted_state_dict = {}
    for key in unet_state_dict:
        new_key = key
        for pattern, new_pattern in MAPPING.items(): new_key = new_key.replace(pattern, new_pattern)
        for dyn_pattern, dyn_new_pattern in DYNAMIC_MAP.items():
            has_matched = False
            if fnmatch.fnmatch(new_key, f'*.{dyn_pattern}.*') and (not has_matched):
                star = int(new_key.split(dyn_pattern.split('.')[0])[-1].split('.')[1])
                if isinstance(dyn_new_pattern, tuple):
                    new_star = star + dyn_new_pattern[-1]
                    dyn_new_pattern = dyn_new_pattern[0]
                else: new_star = star
                pattern = dyn_pattern.replace('*', str(star))
                new_pattern = dyn_new_pattern.replace('*', str(new_star))
                new_key = new_key.replace(pattern, new_pattern)
                has_matched = True
        converted_state_dict[new_key] = unet_state_dict[key]
    return converted_state_dict
def main(model_path, output_path):
    unet_state_dict = load_file(model_path)
    config = {}
    converted_state_dict = convert_state_dict(unet_state_dict)
    unet = Kandinsky3UNet(config)
    unet.load_state_dict(converted_state_dict)
    unet.save_pretrained(output_path)
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert U-Net PyTorch model to Kandinsky3UNet format')
    parser.add_argument('--model_path', type=str, required=True, help='Path to the original U-Net PyTorch model')
    parser.add_argument('--output_path', type=str, required=True, help='Path to save the converted model')
    args = parser.parse_args()
    main(args.model_path, args.output_path)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
