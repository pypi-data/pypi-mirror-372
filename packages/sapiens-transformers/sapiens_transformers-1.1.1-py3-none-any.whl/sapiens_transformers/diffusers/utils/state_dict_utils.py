'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import enum
class StateDictType(enum.Enum):
    DIFFUSERS_OLD = 'sapiens_transformers.diffusers_old'
    KOHYA_SS = 'kohya_ss'
    PEFT = 'peft'
    DIFFUSERS = 'sapiens_transformers.diffusers'
UNET_TO_DIFFUSERS = {'.to_out_lora.up': '.to_out.0.lora_B', '.to_out_lora.down': '.to_out.0.lora_A', '.to_q_lora.down': '.to_q.lora_A', '.to_q_lora.up': '.to_q.lora_B',
'.to_k_lora.down': '.to_k.lora_A', '.to_k_lora.up': '.to_k.lora_B', '.to_v_lora.down': '.to_v.lora_A', '.to_v_lora.up': '.to_v.lora_B', '.lora.up': '.lora_B',
'.lora.down': '.lora_A', '.to_out.lora_magnitude_vector': '.to_out.0.lora_magnitude_vector'}
DIFFUSERS_TO_PEFT = {'.q_proj.lora_linear_layer.up': '.q_proj.lora_B', '.q_proj.lora_linear_layer.down': '.q_proj.lora_A', '.k_proj.lora_linear_layer.up': '.k_proj.lora_B',
'.k_proj.lora_linear_layer.down': '.k_proj.lora_A', '.v_proj.lora_linear_layer.up': '.v_proj.lora_B', '.v_proj.lora_linear_layer.down': '.v_proj.lora_A',
'.out_proj.lora_linear_layer.up': '.out_proj.lora_B', '.out_proj.lora_linear_layer.down': '.out_proj.lora_A', '.lora_linear_layer.up': '.lora_B', '.lora_linear_layer.down': '.lora_A',
'text_projection.lora.down.weight': 'text_projection.lora_A.weight', 'text_projection.lora.up.weight': 'text_projection.lora_B.weight'}
DIFFUSERS_OLD_TO_PEFT = {'.to_q_lora.up': '.q_proj.lora_B', '.to_q_lora.down': '.q_proj.lora_A', '.to_k_lora.up': '.k_proj.lora_B', '.to_k_lora.down': '.k_proj.lora_A',
'.to_v_lora.up': '.v_proj.lora_B', '.to_v_lora.down': '.v_proj.lora_A', '.to_out_lora.up': '.out_proj.lora_B', '.to_out_lora.down': '.out_proj.lora_A',
'.lora_linear_layer.up': '.lora_B', '.lora_linear_layer.down': '.lora_A'}
PEFT_TO_DIFFUSERS = {'.q_proj.lora_B': '.q_proj.lora_linear_layer.up', '.q_proj.lora_A': '.q_proj.lora_linear_layer.down', '.k_proj.lora_B': '.k_proj.lora_linear_layer.up',
'.k_proj.lora_A': '.k_proj.lora_linear_layer.down', '.v_proj.lora_B': '.v_proj.lora_linear_layer.up', '.v_proj.lora_A': '.v_proj.lora_linear_layer.down',
'.out_proj.lora_B': '.out_proj.lora_linear_layer.up', '.out_proj.lora_A': '.out_proj.lora_linear_layer.down', 'to_k.lora_A': 'to_k.lora.down', 'to_k.lora_B': 'to_k.lora.up',
'to_q.lora_A': 'to_q.lora.down', 'to_q.lora_B': 'to_q.lora.up', 'to_v.lora_A': 'to_v.lora.down', 'to_v.lora_B': 'to_v.lora.up',
'to_out.0.lora_A': 'to_out.0.lora.down', 'to_out.0.lora_B': 'to_out.0.lora.up'}
DIFFUSERS_OLD_TO_DIFFUSERS = {'.to_q_lora.up': '.q_proj.lora_linear_layer.up', '.to_q_lora.down': '.q_proj.lora_linear_layer.down', '.to_k_lora.up': '.k_proj.lora_linear_layer.up',
'.to_k_lora.down': '.k_proj.lora_linear_layer.down', '.to_v_lora.up': '.v_proj.lora_linear_layer.up', '.to_v_lora.down': '.v_proj.lora_linear_layer.down',
'.to_out_lora.up': '.out_proj.lora_linear_layer.up', '.to_out_lora.down': '.out_proj.lora_linear_layer.down', '.to_k.lora_magnitude_vector': '.k_proj.lora_magnitude_vector',
'.to_v.lora_magnitude_vector': '.v_proj.lora_magnitude_vector', '.to_q.lora_magnitude_vector': '.q_proj.lora_magnitude_vector',
'.to_out.lora_magnitude_vector': '.out_proj.lora_magnitude_vector'}
PEFT_TO_KOHYA_SS = {'lora_A': 'lora_down', 'lora_B': 'lora_up'}
PEFT_STATE_DICT_MAPPINGS = {StateDictType.DIFFUSERS_OLD: DIFFUSERS_OLD_TO_PEFT, StateDictType.DIFFUSERS: DIFFUSERS_TO_PEFT}
DIFFUSERS_STATE_DICT_MAPPINGS = {StateDictType.DIFFUSERS_OLD: DIFFUSERS_OLD_TO_DIFFUSERS, StateDictType.PEFT: PEFT_TO_DIFFUSERS}
KOHYA_STATE_DICT_MAPPINGS = {StateDictType.PEFT: PEFT_TO_KOHYA_SS}
KEYS_TO_ALWAYS_REPLACE = {'.processor.': '.'}
def convert_state_dict(state_dict, mapping):
    """Returns:"""
    converted_state_dict = {}
    for k, v in state_dict.items():
        for pattern in KEYS_TO_ALWAYS_REPLACE.keys():
            if pattern in k:
                new_pattern = KEYS_TO_ALWAYS_REPLACE[pattern]
                k = k.replace(pattern, new_pattern)
        for pattern in mapping.keys():
            if pattern in k:
                new_pattern = mapping[pattern]
                k = k.replace(pattern, new_pattern)
                break
        converted_state_dict[k] = v
    return converted_state_dict
def convert_state_dict_to_peft(state_dict, original_type=None, **kwargs):
    """Args:"""
    if original_type is None:
        if any(('to_out_lora' in k for k in state_dict.keys())): original_type = StateDictType.DIFFUSERS_OLD
        elif any(('lora_linear_layer' in k for k in state_dict.keys())): original_type = StateDictType.DIFFUSERS
        else: raise ValueError('Could not automatically infer state dict type')
    if original_type not in PEFT_STATE_DICT_MAPPINGS.keys(): raise ValueError(f'Original type {original_type} is not supported')
    mapping = PEFT_STATE_DICT_MAPPINGS[original_type]
    return convert_state_dict(state_dict, mapping)
def convert_state_dict_to_diffusers(state_dict, original_type=None, **kwargs):
    """Args:"""
    peft_adapter_name = kwargs.pop('adapter_name', None)
    if peft_adapter_name is not None: peft_adapter_name = '.' + peft_adapter_name
    else: peft_adapter_name = ''
    if original_type is None:
        if any(('to_out_lora' in k for k in state_dict.keys())): original_type = StateDictType.DIFFUSERS_OLD
        elif any((f'.lora_A{peft_adapter_name}.weight' in k for k in state_dict.keys())): original_type = StateDictType.PEFT
        elif any(('lora_linear_layer' in k for k in state_dict.keys())): return state_dict
        else: raise ValueError('Could not automatically infer state dict type')
    if original_type not in DIFFUSERS_STATE_DICT_MAPPINGS.keys(): raise ValueError(f'Original type {original_type} is not supported')
    mapping = DIFFUSERS_STATE_DICT_MAPPINGS[original_type]
    return convert_state_dict(state_dict, mapping)
def convert_unet_state_dict_to_peft(state_dict):
    mapping = UNET_TO_DIFFUSERS
    return convert_state_dict(state_dict, mapping)
def convert_all_state_dict_to_peft(state_dict):
    try: peft_dict = convert_state_dict_to_peft(state_dict)
    except Exception as e:
        if str(e) == 'Could not automatically infer state dict type': peft_dict = convert_unet_state_dict_to_peft(state_dict)
        else: raise
    if not any(('lora_A' in key or 'lora_B' in key for key in peft_dict.keys())): raise ValueError('Your LoRA was not converted to PEFT')
    return peft_dict
def convert_state_dict_to_kohya(state_dict, original_type=None, **kwargs):
    """Args:"""
    try: import torch
    except ImportError: raise
    peft_adapter_name = kwargs.pop('adapter_name', None)
    if peft_adapter_name is not None: peft_adapter_name = '.' + peft_adapter_name
    else: peft_adapter_name = ''
    if original_type is None:
        if any((f'.lora_A{peft_adapter_name}.weight' in k for k in state_dict.keys())): original_type = StateDictType.PEFT
    if original_type not in KOHYA_STATE_DICT_MAPPINGS.keys(): raise ValueError(f'Original type {original_type} is not supported')
    kohya_ss_partial_state_dict = convert_state_dict(state_dict, KOHYA_STATE_DICT_MAPPINGS[StateDictType.PEFT])
    kohya_ss_state_dict = {}
    for kohya_key, weight in kohya_ss_partial_state_dict.items():
        if 'text_encoder_2.' in kohya_key: kohya_key = kohya_key.replace('text_encoder_2.', 'lora_te2.')
        elif 'text_encoder.' in kohya_key: kohya_key = kohya_key.replace('text_encoder.', 'lora_te1.')
        elif 'unet' in kohya_key: kohya_key = kohya_key.replace('unet', 'lora_unet')
        elif 'lora_magnitude_vector' in kohya_key: kohya_key = kohya_key.replace('lora_magnitude_vector', 'dora_scale')
        kohya_key = kohya_key.replace('.', '_', kohya_key.count('.') - 2)
        kohya_key = kohya_key.replace(peft_adapter_name, '')
        kohya_ss_state_dict[kohya_key] = weight
        if 'lora_down' in kohya_key:
            alpha_key = f"{kohya_key.split('.')[0]}.alpha"
            kohya_ss_state_dict[alpha_key] = torch.tensor(len(weight))
    return kohya_ss_state_dict
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
