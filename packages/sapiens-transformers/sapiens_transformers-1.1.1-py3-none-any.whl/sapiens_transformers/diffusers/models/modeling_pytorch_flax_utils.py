'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from flax.traverse_util import flatten_dict
from flax.serialization import from_bytes
from pickle import UnpicklingError
import jax.numpy as jnp
import numpy as np
import jax
def load_flax_checkpoint_in_pytorch_model(pt_model, model_file):
    try:
        with open(model_file, 'rb') as flax_state_f: flax_state = from_bytes(None, flax_state_f.read())
    except UnpicklingError as e:
        try:
            with open(model_file) as f:
                if f.read().startswith('version'): raise OSError('You seem to have cloned a repository without having git-lfs installed. Please install git-lfs and run `git lfs install` followed by `git lfs pull` in the folder you cloned.')
                else: raise ValueError from e
        except (UnicodeDecodeError, ValueError): raise EnvironmentError(f'Unable to convert {model_file} to Flax deserializable object. ')
    return load_flax_weights_in_pytorch_model(pt_model, flax_state)
def load_flax_weights_in_pytorch_model(pt_model, flax_state):
    try: import torch
    except ImportError: raise
    is_type_bf16 = flatten_dict(jax.tree_util.tree_map(lambda x: x.dtype == jnp.bfloat16, flax_state)).values()
    if any(is_type_bf16): flax_state = jax.tree_util.tree_map(lambda params: params.astype(np.float32) if params.dtype == jnp.bfloat16 else params, flax_state)
    pt_model.base_model_prefix = ''
    flax_state_dict = flatten_dict(flax_state, sep='.')
    pt_model_dict = pt_model.state_dict()
    unexpected_keys = []
    missing_keys = set(pt_model_dict.keys())
    for flax_key_tuple, flax_tensor in flax_state_dict.items():
        flax_key_tuple_array = flax_key_tuple.split('.')
        if flax_key_tuple_array[-1] == 'kernel' and flax_tensor.ndim == 4:
            flax_key_tuple_array = flax_key_tuple_array[:-1] + ['weight']
            flax_tensor = jnp.transpose(flax_tensor, (3, 2, 0, 1))
        elif flax_key_tuple_array[-1] == 'kernel':
            flax_key_tuple_array = flax_key_tuple_array[:-1] + ['weight']
            flax_tensor = flax_tensor.T
        elif flax_key_tuple_array[-1] == 'scale': flax_key_tuple_array = flax_key_tuple_array[:-1] + ['weight']
        if 'time_embedding' not in flax_key_tuple_array:
            for i, flax_key_tuple_string in enumerate(flax_key_tuple_array): flax_key_tuple_array[i] = flax_key_tuple_string.replace('_0', '.0').replace('_1', '.1').replace('_2', '.2').replace('_3', '.3').replace('_4', '.4').replace('_5', '.5').replace('_6', '.6').replace('_7', '.7').replace('_8', '.8').replace('_9', '.9')
        flax_key = '.'.join(flax_key_tuple_array)
        if flax_key in pt_model_dict:
            if flax_tensor.shape != pt_model_dict[flax_key].shape: raise ValueError(f'Flax checkpoint seems to be incorrect. Weight {flax_key_tuple} was expected to be of shape {pt_model_dict[flax_key].shape}, but is {flax_tensor.shape}.')
            else:
                flax_tensor = np.asarray(flax_tensor) if not isinstance(flax_tensor, np.ndarray) else flax_tensor
                pt_model_dict[flax_key] = torch.from_numpy(flax_tensor)
                missing_keys.remove(flax_key)
        else: unexpected_keys.append(flax_key)
    pt_model.load_state_dict(pt_model_dict)
    missing_keys = list(missing_keys)
    return pt_model
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
