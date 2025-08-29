"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from math import ceil
def assert_device_map(device_map, num_blocks):
    blocks = list(range(0, num_blocks))
    device_map_blocks = [item for sublist in list(device_map.values()) for item in sublist]
    duplicate_blocks = []
    for i in device_map_blocks:
        if device_map_blocks.count(i) > 1 and i not in duplicate_blocks: duplicate_blocks.append(i)
    missing_blocks = [i for i in blocks if i not in device_map_blocks]
    extra_blocks = [i for i in device_map_blocks if i not in blocks]
    if len(duplicate_blocks) != 0: raise ValueError("Duplicate attention blocks specified in device_map. Attention blocks must be specified to one device. These attention blocks were specified more than once: " + str(duplicate_blocks))
    if len(missing_blocks) != 0: raise ValueError("There are attention blocks for this model that are not specified in the device_map. Add these attention blocks to a device on the device_map: " + str(missing_blocks))
    if len(extra_blocks) != 0: raise ValueError("The device_map contains more attention blocks than this model has. Remove these from the device_map:"+str(extra_blocks))
def get_device_map(n_layers, devices):
    layers = list(range(n_layers))
    n_blocks = int(ceil(n_layers / len(devices)))
    layers_list = [layers[i : i + n_blocks] for i in range(0, n_layers, n_blocks)]
    return dict(zip(devices, layers_list))
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
