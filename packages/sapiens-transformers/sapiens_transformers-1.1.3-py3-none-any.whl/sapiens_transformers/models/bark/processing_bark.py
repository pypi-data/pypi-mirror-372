"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import json
import os
from typing import Optional
import numpy as np
from ...feature_extraction_utils import BatchFeature
from ...processing_utils import ProcessorMixin
from ...utils import logging
from ...utils.hub import get_file_from_repo
from ..auto import AutoTokenizer
logger = logging.get_logger(__name__)
class BarkProcessor(ProcessorMixin):
    tokenizer_class = "AutoTokenizer"
    attributes = ["tokenizer"]
    preset_shape = {'semantic_prompt': 1, 'coarse_prompt': 2, 'fine_prompt': 2}
    def __init__(self, tokenizer, speaker_embeddings=None):
        super().__init__(tokenizer)
        self.speaker_embeddings = speaker_embeddings
    @classmethod
    def from_pretrained(cls, pretrained_processor_name_or_path, speaker_embeddings_dict_path="speaker_embeddings_path.json", **kwargs):
        if speaker_embeddings_dict_path is not None:
            speaker_embeddings_path = get_file_from_repo(pretrained_processor_name_or_path, speaker_embeddings_dict_path, subfolder=kwargs.pop("subfolder", None), cache_dir=kwargs.pop("cache_dir", None),
            force_download=kwargs.pop("force_download", False), proxies=kwargs.pop("proxies", None), resume_download=kwargs.pop("resume_download", None), local_files_only=kwargs.pop("local_files_only", False),
            token=kwargs.pop("use_auth_token", None), revision=kwargs.pop("revision", None))
            if speaker_embeddings_path is None:
                logger.warning(f"`{os.path.join(pretrained_processor_name_or_path,speaker_embeddings_dict_path)}` does not exists, no preloaded speaker embeddings will be used - Make sure to provide a correct path to the json dictionnary if wanted, otherwise set `speaker_embeddings_dict_path=None`.")
                speaker_embeddings = None
            else:
                with open(speaker_embeddings_path) as speaker_embeddings_json: speaker_embeddings = json.load(speaker_embeddings_json)
        else: speaker_embeddings = None
        tokenizer = AutoTokenizer.from_pretrained(pretrained_processor_name_or_path, **kwargs)
        return cls(tokenizer=tokenizer, speaker_embeddings=speaker_embeddings)
    def save_pretrained(self, save_directory, speaker_embeddings_dict_path="speaker_embeddings_path.json", speaker_embeddings_directory="speaker_embeddings", push_to_hub: bool = False, **kwargs):
        if self.speaker_embeddings is not None:
            os.makedirs(os.path.join(save_directory, speaker_embeddings_directory, "v2"), exist_ok=True)
            embeddings_dict = {}
            embeddings_dict["repo_or_path"] = save_directory
            for prompt_key in self.speaker_embeddings:
                if prompt_key != "repo_or_path":
                    voice_preset = self._load_voice_preset(prompt_key)
                    tmp_dict = {}
                    for key in self.speaker_embeddings[prompt_key]:
                        np.save(os.path.join(embeddings_dict["repo_or_path"], speaker_embeddings_directory, f"{prompt_key}_{key}"), voice_preset[key], allow_pickle=False)
                        tmp_dict[key] = os.path.join(speaker_embeddings_directory, f"{prompt_key}_{key}.npy")
                    embeddings_dict[prompt_key] = tmp_dict
            with open(os.path.join(save_directory, speaker_embeddings_dict_path), "w") as fp: json.dump(embeddings_dict, fp)
        super().save_pretrained(save_directory, push_to_hub, **kwargs)
    def _load_voice_preset(self, voice_preset: str = None, **kwargs):
        voice_preset_paths = self.speaker_embeddings[voice_preset]
        voice_preset_dict = {}
        for key in ["semantic_prompt", "coarse_prompt", "fine_prompt"]:
            if key not in voice_preset_paths: raise ValueError(f"Voice preset unrecognized, missing {key} as a key in self.speaker_embeddings[{voice_preset}].")
            path = get_file_from_repo(self.speaker_embeddings.get("repo_or_path", "/"), voice_preset_paths[key], subfolder=kwargs.pop("subfolder", None), cache_dir=kwargs.pop("cache_dir", None),
            force_download=kwargs.pop("force_download", False), proxies=kwargs.pop("proxies", None), resume_download=kwargs.pop("resume_download", None), local_files_only=kwargs.pop("local_files_only", False),
            token=kwargs.pop("use_auth_token", None), revision=kwargs.pop("revision", None))
            if path is None: raise ValueError(f'`{os.path.join(self.speaker_embeddings.get("repo_or_path", "/"),voice_preset_paths[key])}` does not exists, no preloaded voice preset will be used - Make sure to provide correct paths to the {voice_preset} embeddings.')
            voice_preset_dict[key] = np.load(path)
        return voice_preset_dict
    def _validate_voice_preset_dict(self, voice_preset: Optional[dict] = None):
        for key in ["semantic_prompt", "coarse_prompt", "fine_prompt"]:
            if key not in voice_preset: raise ValueError(f"Voice preset unrecognized, missing {key} as a key.")
            if not isinstance(voice_preset[key], np.ndarray): raise TypeError(f"{key} voice preset must be a {str(self.preset_shape[key])}D ndarray.")
            if len(voice_preset[key].shape) != self.preset_shape[key]: raise ValueError(f"{key} voice preset must be a {str(self.preset_shape[key])}D ndarray.")
    def __call__(self, text=None, voice_preset=None, return_tensors="pt", max_length=256, add_special_tokens=False, return_attention_mask=True, return_token_type_ids=False, **kwargs):
        if voice_preset is not None and not isinstance(voice_preset, dict):
            if (isinstance(voice_preset, str) and self.speaker_embeddings is not None and voice_preset in self.speaker_embeddings): voice_preset = self._load_voice_preset(voice_preset)
            else:
                if isinstance(voice_preset, str) and not voice_preset.endswith(".npz"): voice_preset = voice_preset + ".npz"
                voice_preset = np.load(voice_preset)
        if voice_preset is not None:
            self._validate_voice_preset_dict(voice_preset, **kwargs)
            voice_preset = BatchFeature(data=voice_preset, tensor_type=return_tensors)
        encoded_text = self.tokenizer(text, return_tensors=return_tensors, padding="max_length", max_length=max_length, return_attention_mask=return_attention_mask, return_token_type_ids=return_token_type_ids, add_special_tokens=add_special_tokens, **kwargs)
        if voice_preset is not None: encoded_text["history_prompt"] = voice_preset
        return encoded_text
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
