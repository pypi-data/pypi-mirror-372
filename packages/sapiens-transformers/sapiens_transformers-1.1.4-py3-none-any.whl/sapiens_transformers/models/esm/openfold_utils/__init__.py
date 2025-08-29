"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from .chunk_utils import chunk_layer
from .data_transforms import make_atom14_masks
from .feats import atom14_to_atom37, frames_and_literature_positions_to_atom14_pos, torsion_angles_to_frames
from .loss import compute_predicted_aligned_error, compute_tm
from .protein import Protein as OFProtein
from .protein import to_pdb
from .rigid_utils import Rigid, Rotation
from .tensor_utils import dict_multimap, flatten_final_dims, permute_final_dims
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
