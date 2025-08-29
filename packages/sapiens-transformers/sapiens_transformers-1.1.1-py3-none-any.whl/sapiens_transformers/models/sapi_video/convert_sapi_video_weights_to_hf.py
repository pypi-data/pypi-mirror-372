"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from torch import set_default_dtype as t_set_default_dtype, bfloat16 as t_bfloat16, mean as t_mean, distributions as t_distributions, stack as t_stack
from sapiens_transformers import (AutoConfig, AutoTokenizer, AddedToken, SAPIImageImageProcessor, SAPIVideoImageProcessor, SAPIVideoProcessor, SAPIVideoConfig, SAPIVideoForConditionalGeneration)
def convert_sapi_video_to_hf(model_id, pytorch_dump_folder_path, push_to_hub=False):
    from huggingface_hub import hf_hub_download
    filepath = hf_hub_download(repo_id=model_id, filename="config.json", repo_type="model")
    from json import load
    with open(filepath) as file: data = load(file)
    vision_model_id = data["mm_vision_tower"]
    t_set_default_dtype(t_bfloat16)
    text_config = AutoConfig.from_pretrained(text_model_id)
    text_config = text_config.to_dict()
    text_config.update(overwrite_text_config)
    tokenizer = AutoTokenizer.from_pretrained(text_model_id, use_fast=True, padding_side="left")
    tokenizer.add_tokens(AddedToken("<video>", special=True, normalized=False), special_tokens=True)
    tokenizer.add_tokens(AddedToken("<image>", special=True, normalized=False), special_tokens=True)
    image_processor, video_processor = SAPIImageImageProcessor.from_pretrained(vision_model_id), SAPIVideoImageProcessor.from_pretrained(vision_model_id)
    chat_sapi_video = (
        "{% for message in messages %}"
        "{% if message['role'] == 'system' %}"
        "{{ message['content'][0]['text'] }}"
        "{% else %}"
        "{{ message['role'].upper() + ': '}}"
        "{% endif %}"
        "{# Render all images first #}"
        "{% for content in message['content'] | selectattr('type', 'equalto', 'image') %}"
        "{{ '<image>\n' }}"
        "{% endfor %}"
        "{# Render all text next #}"
        "{% for content in message['content'] | selectattr('type', 'equalto', 'text') %}"
        "{{ content['text'] + ' '}}"
        "{% endfor %}"
        "{% endfor %}"
        "{% if add_generation_prompt %}"
        "{{ 'ASSISTANT:' }}"
        "{% endif %}"
    )
    processor = SAPIVideoProcessor(tokenizer=tokenizer, video_processor=video_processor, image_processor=image_processor, chat_template=chat_sapi_video)
    config = SAPIVideoConfig(text_config=text_config, image_grid_pinpoints=image_processor.image_grid_pinpoints, use_image_newline_parameter=True, video_token_index=video_token_index, image_token_index=image_token_index)
    from sapiens_accelerator import init_empty_weights
    with init_empty_weights(): model = SAPIVideoForConditionalGeneration(config)
    def load_original_state_dict(model_id):
        from huggingface_hub import snapshot_download
        from glob import glob
        from safetensors import safe_open
        directory_path, original_state_dict = snapshot_download(repo_id=model_id, allow_patterns=["*.safetensors"]), {}
        for path in glob(f"{directory_path}/*"):
            if path.endswith(".safetensors"):
                with safe_open(path, framework="pt", device="cpu") as f:
                    for key in f.keys(): original_state_dict[key] = f.get_tensor(key)
        return original_state_dict
    def convert_state_dict_to_hf(state_dict):
        new_state_dict = {}
        for key, value in state_dict.items():
            if key.endswith(".inv_freq"): continue
            KEYS_TO_MODIFY_MAPPING = {'model.vision_tower.': '', '.vision_resampler': '', 'model.mm_projector': 'multi_modal_projector', 'model': 'model.model', 'vision_model.model': 'vision_model',
            'lm_head': 'language_model.lm_head', 'model.model': 'language_model.model', 'multi_modal_projector.0': 'multi_modal_projector.linear_1', 'multi_modal_projector.2': 'multi_modal_projector.linear_2',
            'language_model.model.image_newline': 'image_newline'}
            for key_to_modify, new_key in KEYS_TO_MODIFY_MAPPING.items():
                if key_to_modify in key: key = key.replace(key_to_modify, new_key)
            new_state_dict[key] = value.to(t_bfloat16)
        return new_state_dict
    model.load_state_dict(convert_state_dict_to_hf(load_original_state_dict(model_id)), assign=True, strict=True)
    pre_expansion_embeddings = model.language_model.model.embed_tokens.weight.data
    mu, n = t_mean(pre_expansion_embeddings, dim=0).float(), pre_expansion_embeddings.size()[0]
    dist = t_distributions.multivariate_normal.MultivariateNormal(mu, covariance_matrix=1e-5 * (((pre_expansion_embeddings - mu).T @ (pre_expansion_embeddings - mu)) / n))
    vocab_size = config.text_config.vocab_size
    num_tokens = vocab_size + 3
    model.resize_token_embeddings(num_tokens, pad_to_multiple_of=64)
    model.language_model.model.embed_tokens.weight.data[vocab_size:] = t_stack(tuple((dist.sample() for _ in range(model.language_model.model.embed_tokens.weight.data[vocab_size:].shape[0]))), dim=0)
    model.language_model.lm_head.weight.data[vocab_size:] = t_stack(tuple((dist.sample() for _ in range(model.language_model.lm_head.weight.data[vocab_size:].shape[0]))), dim=0)
    if pytorch_dump_folder_path is not None:
        from pathlib import Path
        Path(pytorch_dump_folder_path).mkdir(exist_ok=True)
        model.save_pretrained(pytorch_dump_folder_path)
        processor.save_pretrained(pytorch_dump_folder_path)
    if push_to_hub: repo_id = model_id.split("/")[-1]
if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("--model_id", help="Hub location of the model to convert", default="", choices=[], required=False)
    parser.add_argument("--pytorch_dump_folder_path", default=None, type=str, help="Path to the output PyTorch model directory.")
    parser.add_argument("--push_to_hub", action="store_true", help="Whether or not to push the converted model to the HF hub.")
    args = parser.parse_args()
    convert_sapi_video_to_hf(args.model_id, args.pytorch_dump_folder_path, args.push_to_hub)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
