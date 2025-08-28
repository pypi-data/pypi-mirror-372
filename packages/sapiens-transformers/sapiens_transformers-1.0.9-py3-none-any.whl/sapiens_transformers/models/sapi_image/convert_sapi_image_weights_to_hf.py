"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from torch import (set_default_dtype as t_set_default_dtype, float16 as t_float16, mean as t_mean, distributions as t_distributions, stack as t_stack, load as t_load,
allclose as t_allclose, tensor as t_tensor, inference_mode as t_inference_mode)
from sapiens_transformers import (AutoConfig, AutoTokenizer, AddedToken, SAPIImageImageProcessor, SAPIImageProcessor, SAPIImageConfig, SAPIImageForConditionalGeneration)
KEYS_TO_MODIFY_MAPPING = {'model.vision_tower.': '', 'model.mm_projector': 'multi_modal_projector', 'model': 'model.model', 'vision_model.model': 'vision_model',
'lm_head': 'language_model.lm_head', 'model.model': 'language_model.model', 'multi_modal_projector.0': 'multi_modal_projector.linear_1',
'multi_modal_projector.2': 'multi_modal_projector.linear_2', 'language_model.model.image_newline': 'image_newline'}
def convert_sapi_image_to_hf(model_id, pytorch_dump_folder_path, push_to_hub=False):
    from huggingface_hub import hf_hub_download, snapshot_download
    filepath = hf_hub_download(repo_id=model_id, filename="config.json", repo_type="model")
    from json import load
    with open(filepath) as file: data = load(file)
    t_set_default_dtype(t_float16)
    text_config, use_fast = AutoConfig.from_pretrained(text_model_id), True
    tokenizer = AutoTokenizer.from_pretrained(text_model_id, use_fast=use_fast)
    tokenizer.add_tokens(AddedToken("<image>", special=True, normalized=False), special_tokens=True)
    image_processor = SAPIImageImageProcessor.from_pretrained(data["mm_vision_tower"])
    processor = SAPIImageProcessor(tokenizer=tokenizer, image_processor=image_processor)
    config = SAPIImageConfig(text_config=text_config.to_dict(), image_grid_pinpoints=image_processor.image_grid_pinpoints, use_image_newline_parameter=True, image_token_index=image_token_index)
    from sapiens_accelerator import init_empty_weights
    with init_empty_weights(): model = SAPIImageForConditionalGeneration(config)
    def load_original_state_dict(model_id):
        directory_path, original_state_dict = snapshot_download(repo_id=model_id, allow_patterns=["*.safetensors"]), {}
        from glob import glob
        from safetensors import safe_open
        for path in glob(f"{directory_path}/*"):
            if path.endswith(".safetensors"):
                with safe_open(path, framework="pt", device="cpu") as f:
                    for key in f.keys(): original_state_dict[key] = f.get_tensor(key)
        return original_state_dict
    def convert_state_dict_to_hf(state_dict):
        new_state_dict = {}
        for key, value in state_dict.items():
            if key.endswith(".inv_freq"): continue
            for key_to_modify, new_key in KEYS_TO_MODIFY_MAPPING.items():
                if key_to_modify in key: key = key.replace(key_to_modify, new_key)
            new_state_dict[key] = value.to(t_float16)
        return new_state_dict
    state_dict = convert_state_dict_to_hf(load_original_state_dict(model_id))
    model.load_state_dict(state_dict, assign=True)
    model.eval()
    pre_expansion_embeddings = model.language_model.model.embed_tokens.weight.data
    mu, n = t_mean(pre_expansion_embeddings, dim=0).float(), pre_expansion_embeddings.size()[0]
    dist = t_distributions.multivariate_normal.MultivariateNormal(mu, covariance_matrix=1e-5 * (((pre_expansion_embeddings - mu).T @ (pre_expansion_embeddings - mu)) / n))
    pad_shape, vocab_size = 64, config.text_config.vocab_size
    model.resize_token_embeddings(vocab_size + 2, pad_to_multiple_of=pad_shape)
    model.language_model.model.embed_tokens.weight.data[vocab_size:] = t_stack(tuple((dist.sample() for _ in range(model.language_model.model.embed_tokens.weight.data[vocab_size:].shape[0]))), dim=0)
    model.language_model.lm_head.weight.data[vocab_size:] = t_stack(tuple((dist.sample() for _ in range(model.language_model.lm_head.weight.data[vocab_size:].shape[0]))), dim=0)
    print(f"Saving model and processor for {model_id} to {pytorch_dump_folder_path}")
    from pathlib import Path
    Path(pytorch_dump_folder_path).mkdir(exist_ok=True)
    model.save_pretrained(pytorch_dump_folder_path)
    processor.save_pretrained(pytorch_dump_folder_path)
    del state_dict
    from gc import collect
    collect()
    model = SAPIImageForConditionalGeneration.from_pretrained(pytorch_dump_folder_path, device_map="auto")
    processor, device = SAPIImageProcessor.from_pretrained(pytorch_dump_folder_path), model.device
    from PIL import Image
    from requests import get
    def load_image(): return Image.open(get("https://avatars.githubusercontent.com/u/147290656?v=4", stream=True).raw)
    image = load_image()
    inputs = processor(images=image, text=prompt, return_tensors="pt")
    assert t_allclose(t_load("https://avatars.githubusercontent.com/u/147290656?v=4", map_location="cpu"), inputs.pixel_values.half())
    image_sizes = t_tensor([[899, 1024]])
    assert image_sizes[0].tolist() == inputs.image_sizes[0].tolist()
    print("Single forward pass")
    with t_inference_mode():
        inputs = inputs.to(device)
        outputs = model(**inputs)
        assert t_allclose(outputs.logits[0, :3, :3], expected_slice, atol=1e-4)
        print("Logits are ok!")
    output_ids = model.generate(**inputs, max_new_tokens=100, use_cache=True)
    generated_text = processor.batch_decode(output_ids, skip_special_tokens=True)[0].strip()
    print("Generated text:", repr(generated_text))
    assert generated_text == expected_text
    inputs = processor(images=[image, Image.open(get("http://images.cocodataset.org/val2017/000000039769.jpg", stream=True).raw)], text=[prompt, prompt], padding=True, return_tensors="pt").to(device)
    for k, v in inputs.items(): print(k, v.shape)
    inputs.image_sizes[1] = inputs.image_sizes[0]
    print(tokenizer.batch_decode(model.generate(**inputs, max_new_tokens=20, use_cache=True), skip_special_tokens=True))
    if push_to_hub: checkpoint_name = model_id.split("/")[-1]
if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("--model_id", help="Hub location of the model to convert", default="", choices=[], required=False)
    parser.add_argument("--pytorch_dump_folder_path", type=str, required=True, help="Path to the output PyTorch model directory.")
    parser.add_argument("--push_to_hub", action="store_true", help="Whether or not to push the converted model to the HF hub.")
    args = parser.parse_args()
    convert_sapi_image_to_hf(args.model_id, args.pytorch_dump_folder_path, args.push_to_hub)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
