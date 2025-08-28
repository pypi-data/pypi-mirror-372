"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import argparse
import collections
import torch
from flax import traverse_util
from t5x import checkpoints
from sapiens_transformers import T5Config, T5EncoderModel, T5ForConditionalGeneration
from sapiens_transformers.utils import logging
logging.set_verbosity_info()
def t5x_attention_lookup(params, i, prefix, layer_name="attention"):
    k = params[f"{prefix}/layers_{i}/{layer_name}/key/kernel"]
    o = params[f"{prefix}/layers_{i}/{layer_name}/out/kernel"]
    q = params[f"{prefix}/layers_{i}/{layer_name}/query/kernel"]
    v = params[f"{prefix}/layers_{i}/{layer_name}/value/kernel"]
    return k, o, q, v
def t5x_mlp_lookup(params, i, prefix, split_mlp_wi=False):
    if split_mlp_wi:
        wi_0 = params[f"{prefix}/layers_{i}/mlp/wi_0/kernel"]
        wi_1 = params[f"{prefix}/layers_{i}/mlp/wi_1/kernel"]
        wi = (wi_0, wi_1)
    else: wi = params[f"{prefix}/layers_{i}/mlp/wi/kernel"]
    wo = params[f"{prefix}/layers_{i}/mlp/wo/kernel"]
    return wi, wo
def t5x_layer_norm_lookup(params, i, prefix, layer_name): return params[f"{prefix}/layers_{i}/{layer_name}/scale"]
def convert_t5x_to_pytorch(variables: dict, *, num_layers: int, num_decoder_layers: int, is_encoder_only: bool):
    old = traverse_util.flatten_dict(variables["target"])
    old = {"/".join(k): v for k, v in old.items()}
    split_mlp_wi = "encoder/layers_0/mlp/wi_0/kernel" in old
    print("Split MLP:", split_mlp_wi)
    new = collections.OrderedDict()
    new["shared.weight"] = old["token_embedder/embedding"]
    for i in range(num_layers):
        layer_norm = t5x_layer_norm_lookup(old, i, "encoder", "pre_attention_layer_norm")
        k, o, q, v = t5x_attention_lookup(old, i, "encoder", "attention")
        new[f"encoder.block.{i}.layer.0.layer_norm.weight"] = layer_norm
        new[f"encoder.block.{i}.layer.0.SelfAttention.k.weight"] = k.T
        new[f"encoder.block.{i}.layer.0.SelfAttention.o.weight"] = o.T
        new[f"encoder.block.{i}.layer.0.SelfAttention.q.weight"] = q.T
        new[f"encoder.block.{i}.layer.0.SelfAttention.v.weight"] = v.T
        layer_norm = t5x_layer_norm_lookup(old, i, "encoder", "pre_mlp_layer_norm")
        wi, wo = t5x_mlp_lookup(old, i, "encoder", split_mlp_wi)
        new[f"encoder.block.{i}.layer.1.layer_norm.weight"] = layer_norm
        if split_mlp_wi:
            new[f"encoder.block.{i}.layer.1.DenseReluDense.wi_0.weight"] = wi[0].T
            new[f"encoder.block.{i}.layer.1.DenseReluDense.wi_1.weight"] = wi[1].T
        else: new[f"encoder.block.{i}.layer.1.DenseReluDense.wi.weight"] = wi.T
        new[f"encoder.block.{i}.layer.1.DenseReluDense.wo.weight"] = wo.T
    new["encoder.block.0.layer.0.SelfAttention.relative_attention_bias.weight"] = old["encoder/relpos_bias/rel_embedding"].T
    new["encoder.final_layer_norm.weight"] = old["encoder/encoder_norm/scale"]
    if not is_encoder_only:
        for i in range(num_decoder_layers):
            layer_norm = t5x_layer_norm_lookup(old, i, "decoder", "pre_self_attention_layer_norm")
            k, o, q, v = t5x_attention_lookup(old, i, "decoder", "self_attention")
            new[f"decoder.block.{i}.layer.0.layer_norm.weight"] = layer_norm
            new[f"decoder.block.{i}.layer.0.SelfAttention.k.weight"] = k.T
            new[f"decoder.block.{i}.layer.0.SelfAttention.o.weight"] = o.T
            new[f"decoder.block.{i}.layer.0.SelfAttention.q.weight"] = q.T
            new[f"decoder.block.{i}.layer.0.SelfAttention.v.weight"] = v.T
            layer_norm = t5x_layer_norm_lookup(old, i, "decoder", "pre_cross_attention_layer_norm")
            k, o, q, v = t5x_attention_lookup(old, i, "decoder", "encoder_decoder_attention")
            new[f"decoder.block.{i}.layer.1.layer_norm.weight"] = layer_norm
            new[f"decoder.block.{i}.layer.1.EncDecAttention.k.weight"] = k.T
            new[f"decoder.block.{i}.layer.1.EncDecAttention.o.weight"] = o.T
            new[f"decoder.block.{i}.layer.1.EncDecAttention.q.weight"] = q.T
            new[f"decoder.block.{i}.layer.1.EncDecAttention.v.weight"] = v.T
            layer_norm = t5x_layer_norm_lookup(old, i, "decoder", "pre_mlp_layer_norm")
            wi, wo = t5x_mlp_lookup(old, i, "decoder", split_mlp_wi)
            new[f"decoder.block.{i}.layer.2.layer_norm.weight"] = layer_norm
            if split_mlp_wi:
                new[f"decoder.block.{i}.layer.2.DenseReluDense.wi_0.weight"] = wi[0].T
                new[f"decoder.block.{i}.layer.2.DenseReluDense.wi_1.weight"] = wi[1].T
            else: new[f"decoder.block.{i}.layer.2.DenseReluDense.wi.weight"] = wi.T
            new[f"decoder.block.{i}.layer.2.DenseReluDense.wo.weight"] = wo.T
        new["decoder.final_layer_norm.weight"] = old["decoder/decoder_norm/scale"]
        new["decoder.block.0.layer.0.SelfAttention.relative_attention_bias.weight"] = old["decoder/relpos_bias/rel_embedding"].T
        if "decoder/logits_dense/kernel" in old: new["lm_head.weight"] = old["decoder/logits_dense/kernel"].T
    return new
def make_state_dict(converted_params, is_encoder_only: bool):
    state_dict = collections.OrderedDict([(k, torch.from_numpy(v.copy())) for (k, v) in converted_params.items()])
    if "encoder.embed_tokens.weight" not in state_dict: state_dict["encoder.embed_tokens.weight"] = state_dict["shared.weight"]
    if not is_encoder_only:
        if "decoder.embed_tokens.weight" not in state_dict: state_dict["decoder.embed_tokens.weight"] = state_dict["shared.weight"]
        if "lm_head.weight" not in state_dict:
            print("Using shared word embeddings as lm_head.")
            state_dict["lm_head.weight"] = state_dict["shared.weight"]
    return state_dict
def load_t5x_weights_in_t5(model, config, t5x_checkpoint_path, is_encoder_only):
    variables = checkpoints.load_t5x_checkpoint(t5x_checkpoint_path)
    converted = convert_t5x_to_pytorch(variables, num_layers=config.num_layers, num_decoder_layers=config.num_decoder_layers, is_encoder_only=is_encoder_only)
    state_dict = make_state_dict(converted, is_encoder_only)
    model.load_state_dict(state_dict, strict=True)
def convert_t5x_checkpoint_to_pytorch(t5x_checkpoint_path, config_file, pytorch_dump_path, is_encoder_only: bool = False):
    config = T5Config.from_json_file(config_file)
    print(f"Building PyTorch model from configuration: {config}")
    if is_encoder_only: model = T5EncoderModel(config)
    else: model = T5ForConditionalGeneration(config)
    load_t5x_weights_in_t5(model, config, t5x_checkpoint_path, is_encoder_only)
    print(f"Save PyTorch model to {pytorch_dump_path}")
    model.save_pretrained(pytorch_dump_path)
    model.from_pretrained(pytorch_dump_path)
    print("Done")
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Converts a native T5X checkpoint into a PyTorch checkpoint.")
    parser.add_argument("--t5x_checkpoint_path", default=None, type=str, required=True, help="Path to the T5X checkpoint.")
    parser.add_argument("--config_file", default=None, type=str, required=True, help="The config json file corresponding to the pre-trained T5 model.\nThis specifies the model architecture.")
    parser.add_argument("--pytorch_dump_path", default=None, type=str, required=True, help="Path to the output PyTorch model.")
    parser.add_argument("--is_encoder_only", action="store_true", help="Check if the model is encoder-decoder model", default=False)
    args = parser.parse_args()
    convert_t5x_checkpoint_to_pytorch(args.t5x_checkpoint_path, args.config_file, args.pytorch_dump_path, args.is_encoder_only)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
