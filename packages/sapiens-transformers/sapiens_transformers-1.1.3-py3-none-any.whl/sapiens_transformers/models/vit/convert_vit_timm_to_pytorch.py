"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import argparse
from pathlib import Path
import requests
import timm
import torch
from PIL import Image
from timm.data import ImageNetInfo, infer_imagenet_subset
from sapiens_transformers import DeiTImageProcessor, ViTConfig, ViTForImageClassification, ViTImageProcessor, ViTModel
from sapiens_transformers.utils import logging
logging.set_verbosity_info()
logger = logging.get_logger(__name__)
def create_rename_keys(config, base_model=False):
    rename_keys = []
    for i in range(config.num_hidden_layers):
        rename_keys.append((f"blocks.{i}.norm1.weight", f"vit.encoder.layer.{i}.layernorm_before.weight"))
        rename_keys.append((f"blocks.{i}.norm1.bias", f"vit.encoder.layer.{i}.layernorm_before.bias"))
        rename_keys.append((f"blocks.{i}.attn.proj.weight", f"vit.encoder.layer.{i}.attention.output.dense.weight"))
        rename_keys.append((f"blocks.{i}.attn.proj.bias", f"vit.encoder.layer.{i}.attention.output.dense.bias"))
        rename_keys.append((f"blocks.{i}.norm2.weight", f"vit.encoder.layer.{i}.layernorm_after.weight"))
        rename_keys.append((f"blocks.{i}.norm2.bias", f"vit.encoder.layer.{i}.layernorm_after.bias"))
        rename_keys.append((f"blocks.{i}.mlp.fc1.weight", f"vit.encoder.layer.{i}.intermediate.dense.weight"))
        rename_keys.append((f"blocks.{i}.mlp.fc1.bias", f"vit.encoder.layer.{i}.intermediate.dense.bias"))
        rename_keys.append((f"blocks.{i}.mlp.fc2.weight", f"vit.encoder.layer.{i}.output.dense.weight"))
        rename_keys.append((f"blocks.{i}.mlp.fc2.bias", f"vit.encoder.layer.{i}.output.dense.bias"))
    rename_keys.extend([("cls_token", "vit.embeddings.cls_token"), ("patch_embed.proj.weight", "vit.embeddings.patch_embeddings.projection.weight"),
    ("patch_embed.proj.bias", "vit.embeddings.patch_embeddings.projection.bias"), ("pos_embed", "vit.embeddings.position_embeddings")])
    if base_model:
        rename_keys.extend([("norm.weight", "layernorm.weight"), ("norm.bias", "layernorm.bias")])
        rename_keys = [(pair[0], pair[1][4:]) if pair[1].startswith("vit") else pair for pair in rename_keys]
    else: rename_keys.extend([("norm.weight", "vit.layernorm.weight"), ("norm.bias", "vit.layernorm.bias"), ("head.weight", "classifier.weight"), ("head.bias", "classifier.bias")])
    return rename_keys
def read_in_q_k_v(state_dict, config, base_model=False):
    for i in range(config.num_hidden_layers):
        if base_model: prefix = ""
        else: prefix = "vit."
        in_proj_weight = state_dict.pop(f"blocks.{i}.attn.qkv.weight")
        in_proj_bias = state_dict.pop(f"blocks.{i}.attn.qkv.bias")
        state_dict[f"{prefix}encoder.layer.{i}.attention.attention.query.weight"] = in_proj_weight[: config.hidden_size, :]
        state_dict[f"{prefix}encoder.layer.{i}.attention.attention.query.bias"] = in_proj_bias[: config.hidden_size]
        state_dict[f"{prefix}encoder.layer.{i}.attention.attention.key.weight"] = in_proj_weight[config.hidden_size : config.hidden_size * 2, :]
        state_dict[f"{prefix}encoder.layer.{i}.attention.attention.key.bias"] = in_proj_bias[config.hidden_size : config.hidden_size * 2]
        state_dict[f"{prefix}encoder.layer.{i}.attention.attention.value.weight"] = in_proj_weight[-config.hidden_size :, :]
        state_dict[f"{prefix}encoder.layer.{i}.attention.attention.value.bias"] = in_proj_bias[-config.hidden_size :]
def remove_classification_head_(state_dict):
    ignore_keys = ["head.weight", "head.bias"]
    for k in ignore_keys: state_dict.pop(k, None)
def rename_key(dct, old, new):
    val = dct.pop(old)
    dct[new] = val
def prepare_img():
    url = "http://images.cocodataset.org/val2017/000000039769.jpg"
    im = Image.open(requests.get(url, stream=True).raw)
    return im
@torch.no_grad()
def convert_vit_checkpoint(vit_name, pytorch_dump_folder_path):
    config = ViTConfig()
    base_model = False
    timm_model = timm.create_model(vit_name, pretrained=True)
    timm_model.eval()
    if not isinstance(getattr(timm_model, "fc_norm", None), torch.nn.Identity): raise ValueError(f"{vit_name} is not supported in transformers because of the presence of fc_norm.")
    if getattr(timm_model, "global_pool", None) == "avg": raise ValueError(f"{vit_name} is not supported in transformers because of use of global average pooling.")
    if "clip" in vit_name and not isinstance(getattr(timm_model, "norm_pre", None), torch.nn.Identity): raise ValueError(f"{vit_name} is not supported in transformers because it's a CLIP style ViT with norm_pre layer.")
    if "siglip" in vit_name and getattr(timm_model, "global_pool", None) == "map": raise ValueError(f"{vit_name} is not supported in transformers because it's a SigLIP style ViT with attn_pool.")
    if not isinstance(getattr(timm_model.blocks[0], "ls1", None), torch.nn.Identity) or not isinstance(getattr(timm_model.blocks[0], "ls2", None), torch.nn.Identity): raise ValueError(f"{vit_name} is not supported in transformers because it uses a layer scale in its blocks.")
    if not isinstance(timm_model.patch_embed, timm.layers.PatchEmbed): raise ValueError(f"{vit_name} is not supported in transformers because it is a hybrid ResNet-ViT.")
    config.patch_size = timm_model.patch_embed.patch_size[0]
    config.image_size = timm_model.patch_embed.img_size[0]
    config.hidden_size = timm_model.embed_dim
    config.intermediate_size = timm_model.blocks[0].mlp.fc1.out_features
    config.num_hidden_layers = len(timm_model.blocks)
    config.num_attention_heads = timm_model.blocks[0].attn.num_heads
    if timm_model.num_classes != 0:
        config.num_labels = timm_model.num_classes
        imagenet_subset = infer_imagenet_subset(timm_model)
        dataset_info = ImageNetInfo(imagenet_subset)
        config.id2label = {i: dataset_info.index_to_label_name(i) for i in range(dataset_info.num_classes())}
        config.label2id = {v: k for k, v in config.id2label.items()}
    else:
        print(f"{vit_name} is going to be converted as a feature extractor only.")
        base_model = True
    state_dict = timm_model.state_dict()
    if base_model: remove_classification_head_(state_dict)
    rename_keys = create_rename_keys(config, base_model)
    for src, dest in rename_keys: rename_key(state_dict, src, dest)
    read_in_q_k_v(state_dict, config, base_model)
    if base_model: model = ViTModel(config, add_pooling_layer=False).eval()
    else: model = ViTForImageClassification(config).eval()
    model.load_state_dict(state_dict)
    if "deit" in vit_name: image_processor = DeiTImageProcessor(size=config.image_size)
    else: image_processor = ViTImageProcessor(size=config.image_size)
    encoding = image_processor(images=prepare_img(), return_tensors="pt")
    pixel_values = encoding["pixel_values"]
    outputs = model(pixel_values)
    if base_model:
        timm_pooled_output = timm_model.forward_features(pixel_values)
        assert timm_pooled_output.shape == outputs.last_hidden_state.shape
        assert torch.allclose(timm_pooled_output, outputs.last_hidden_state, atol=1e-1)
    else:
        timm_logits = timm_model(pixel_values)
        assert timm_logits.shape == outputs.logits.shape
        assert torch.allclose(timm_logits, outputs.logits, atol=1e-3)
    Path(pytorch_dump_folder_path).mkdir(exist_ok=True)
    print(f"Saving model {vit_name} to {pytorch_dump_folder_path}")
    model.save_pretrained(pytorch_dump_folder_path)
    print(f"Saving image processor to {pytorch_dump_folder_path}")
    image_processor.save_pretrained(pytorch_dump_folder_path)
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--vit_name", default="vit_base_patch16_224", type=str, help="Name of the ViT timm model you'd like to convert.")
    parser.add_argument("--pytorch_dump_folder_path", default=None, type=str, help="Path to the output PyTorch model directory.")
    args = parser.parse_args()
    convert_vit_checkpoint(args.vit_name, args.pytorch_dump_folder_path)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
