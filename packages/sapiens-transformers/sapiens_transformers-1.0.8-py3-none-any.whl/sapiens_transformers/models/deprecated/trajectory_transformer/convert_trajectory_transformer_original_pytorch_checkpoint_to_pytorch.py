"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import torch
import trajectory.utils as utils
from sapiens_transformers import TrajectoryTransformerModel
class Parser(utils.Parser):
    dataset: str = "halfcheetah-medium-expert-v2"
    config: str = "config.offline"
def convert_trajectory_transformer_original_pytorch_checkpoint_to_pytorch(logbase, dataset, loadpath, epoch, device):
    gpt, gpt_epoch = utils.load_model(logbase, dataset, loadpath, epoch=epoch, device=device)
    trajectory_transformer = TrajectoryTransformerModel(gpt.config)
    trajectory_transformer.tok_emb.load_state_dict(gpt.tok_emb.state_dict())
    trajectory_transformer.pos_emb = gpt.pos_emb
    trajectory_transformer.drop.load_state_dict(gpt.drop.state_dict())
    trajectory_transformer.ln_f.load_state_dict(gpt.ln_f.state_dict())
    trajectory_transformer.head.load_state_dict(gpt.head.state_dict())
    for i, block in enumerate(gpt.blocks):
        trajectory_transformer.blocks[i].ln1.load_state_dict(gpt.blocks[i].ln1.state_dict())
        trajectory_transformer.blocks[i].ln2.load_state_dict(gpt.blocks[i].ln2.state_dict())
        trajectory_transformer.blocks[i].attn.load_state_dict(gpt.blocks[i].attn.state_dict())
        trajectory_transformer.blocks[i].l1.load_state_dict(gpt.blocks[i].mlp[0].state_dict())
        trajectory_transformer.blocks[i].act.load_state_dict(gpt.blocks[i].mlp[1].state_dict())
        trajectory_transformer.blocks[i].l2.load_state_dict(gpt.blocks[i].mlp[2].state_dict())
        trajectory_transformer.blocks[i].drop.load_state_dict(gpt.blocks[i].mlp[3].state_dict())
    torch.save(trajectory_transformer.state_dict(), "pytorch_model.bin")
if __name__ == "__main__":
    args = Parser().parse_args("plan")
    convert_trajectory_transformer_original_pytorch_checkpoint_to_pytorch(args.logbase, args.dataset, args.gpt_loadpath, args.gpt_epoch, args.device)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
