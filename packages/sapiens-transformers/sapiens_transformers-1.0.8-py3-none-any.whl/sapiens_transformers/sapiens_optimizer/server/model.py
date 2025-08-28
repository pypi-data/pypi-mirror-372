from __future__ import annotations
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import json
from typing import Dict, Optional, Union, List
import sapiens_transformers.sapiens_optimizer as sapiens_optimizer
import sapiens_transformers.sapiens_optimizer.sapiens_speculative as sapiens_speculative
import sapiens_transformers.sapiens_optimizer.sapiens_tokenizer as sapiens_tokenizer
from .settings import ModelSettings
class SapiensProxy:
    def __init__(self, models: List[ModelSettings]) -> None:
        assert len(models) > 0, "No models provided!"
        self._model_settings_dict: dict[str, ModelSettings] = {}
        for model in models:
            if not model.model_alias: model.model_alias = model.model
            self._model_settings_dict[model.model_alias] = model
        self._current_model: Optional[sapiens_optimizer.Sapiens] = None
        self._current_model_alias: Optional[str] = None
        self._default_model_settings: ModelSettings = models[0]
        self._default_model_alias: str = self._default_model_settings.model_alias
        self._current_model = self.load_llama_from_model_settings(self._default_model_settings)
        self._current_model_alias = self._default_model_alias
    def __call__(self, model: Optional[str] = None) -> sapiens_optimizer.Sapiens:
        if model is None: model = self._default_model_alias
        if model not in self._model_settings_dict: model = self._default_model_alias
        if model == self._current_model_alias:
            if self._current_model is not None: return self._current_model
        if self._current_model: self._current_model.close()
        self._current_model = None
        settings = self._model_settings_dict[model]
        self._current_model = self.load_llama_from_model_settings(settings)
        self._current_model_alias = model
        return self._current_model
    def __getitem__(self, model: str): return self._model_settings_dict[model].model_dump()
    def __setitem__(self, model: str, settings: Union[ModelSettings, str, bytes]):
        if isinstance(settings, (bytes, str)): settings = ModelSettings.model_validate_json(settings)
        self._model_settings_dict[model] = settings
    def __iter__(self):
        for model in self._model_settings_dict: yield model
    def free(self):
        if self._current_model:
            self._current_model.close()
            del self._current_model
    @staticmethod
    def load_llama_from_model_settings(settings: ModelSettings) -> sapiens_optimizer.Sapiens:
        chat_handler = None
        if settings.chat_format == "llava-1-5":
            assert settings.clip_model_path is not None, "clip model not found"
            if settings.hf_model_repo_id is not None:
                chat_handler = (sapiens_optimizer.sapiens_chat_format.Llava15ChatHandler.from_pretrained(repo_id=settings.hf_model_repo_id,
                filename=settings.clip_model_path, verbose=settings.verbose))
            else: chat_handler = sapiens_optimizer.sapiens_chat_format.Llava15ChatHandler(clip_model_path=settings.clip_model_path, verbose=settings.verbose)
        elif settings.chat_format == "obsidian":
            assert settings.clip_model_path is not None, "clip model not found"
            if settings.hf_model_repo_id is not None: chat_handler = (sapiens_optimizer.sapiens_chat_format.ObsidianChatHandler.from_pretrained(repo_id=settings.hf_model_repo_id,
            filename=settings.clip_model_path, verbose=settings.verbose))
            else: chat_handler = sapiens_optimizer.sapiens_chat_format.ObsidianChatHandler(clip_model_path=settings.clip_model_path, verbose=settings.verbose)
        elif settings.chat_format == "llava-1-6":
            assert settings.clip_model_path is not None, "clip model not found"
            if settings.hf_model_repo_id is not None: chat_handler = (sapiens_optimizer.sapiens_chat_format.Llava16ChatHandler.from_pretrained(repo_id=settings.hf_model_repo_id, filename=settings.clip_model_path, verbose=settings.verbose))
            else: chat_handler = sapiens_optimizer.sapiens_chat_format.Llava16ChatHandler(clip_model_path=settings.clip_model_path, verbose=settings.verbose)
        elif settings.chat_format == "moondream":
            assert settings.clip_model_path is not None, "clip model not found"
            if settings.hf_model_repo_id is not None: chat_handler = (sapiens_optimizer.sapiens_chat_format.MoondreamChatHandler.from_pretrained(repo_id=settings.hf_model_repo_id, filename=settings.clip_model_path, verbose=settings.verbose))
            else: chat_handler = sapiens_optimizer.sapiens_chat_format.MoondreamChatHandler(clip_model_path=settings.clip_model_path, verbose=settings.verbose)
        elif settings.chat_format == "nanollava":
            assert settings.clip_model_path is not None, "clip model not found"
            if settings.hf_model_repo_id is not None: chat_handler = (sapiens_optimizer.sapiens_chat_format.NanoLlavaChatHandler.from_pretrained(repo_id=settings.hf_model_repo_id,
            filename=settings.clip_model_path, verbose=settings.verbose))
            else: chat_handler = sapiens_optimizer.sapiens_chat_format.NanoLlavaChatHandler(clip_model_path=settings.clip_model_path, verbose=settings.verbose)
        elif settings.chat_format == "llama-3-vision-alpha":
            assert settings.clip_model_path is not None, "clip model not found"
            if settings.hf_model_repo_id is not None: chat_handler = (sapiens_optimizer.sapiens_chat_format.SapiensVisionAlpha.from_pretrained(repo_id=settings.hf_model_repo_id,
            filename=settings.clip_model_path, verbose=settings.verbose))
            else: chat_handler = sapiens_optimizer.sapiens_chat_format.SapiensVisionAlpha(clip_model_path=settings.clip_model_path, verbose=settings.verbose)
        elif settings.chat_format == "minicpm-v-2.6":
            assert settings.clip_model_path is not None, "clip model not found"
            if settings.hf_model_repo_id is not None: chat_handler = (sapiens_optimizer.sapiens_chat_format.MiniCPMv26ChatHandler.from_pretrained(repo_id=settings.hf_model_repo_id, filename=settings.clip_model_path, verbose=settings.verbose))
            else: chat_handler = sapiens_optimizer.sapiens_chat_format.MiniCPMv26ChatHandler(clip_model_path=settings.clip_model_path, verbose=settings.verbose)
        elif settings.chat_format == "hf-autotokenizer":
            assert (settings.hf_pretrained_model_name_or_path is not None), "hf_pretrained_model_name_or_path must be set for hf-autotokenizer"
            chat_handler = (sapiens_optimizer.sapiens_chat_format.hf_autotokenizer_to_chat_completion_handler(settings.hf_pretrained_model_name_or_path))
        elif settings.chat_format == "hf-tokenizer-config":
            assert (settings.hf_tokenizer_config_path is not None), "hf_tokenizer_config_path must be set for hf-tokenizer-config"
            chat_handler = sapiens_optimizer.sapiens_chat_format.hf_tokenizer_config_to_chat_completion_handler(json.load(open(settings.hf_tokenizer_config_path)))
        tokenizer: Optional[sapiens_optimizer.BaseSapiensTokenizer] = None
        if settings.hf_pretrained_model_name_or_path is not None: tokenizer = sapiens_tokenizer.SapiensHFTokenizer.from_pretrained(settings.hf_pretrained_model_name_or_path)
        draft_model = None
        if settings.draft_model is not None: draft_model = sapiens_speculative.SapiensPromptLookupDecoding(num_pred_tokens=settings.draft_model_num_pred_tokens)
        kv_overrides: Optional[Dict[str, Union[bool, int, float, str]]] = None
        if settings.kv_overrides is not None:
            assert isinstance(settings.kv_overrides, list)
            kv_overrides = {}
            for kv in settings.kv_overrides:
                key, value = kv.split("=")
                if ":" in value:
                    value_type, value = value.split(":")
                    if value_type == "bool": kv_overrides[key] = value.lower() in ["true", "1"]
                    elif value_type == "int": kv_overrides[key] = int(value)
                    elif value_type == "float": kv_overrides[key] = float(value)
                    elif value_type == "str": kv_overrides[key] = value
                    else: raise ValueError(f"Unknown value type {value_type}")
        import functools
        kwargs = {}
        if settings.hf_model_repo_id is not None: create_fn = functools.partial(sapiens_optimizer.Sapiens.from_pretrained, repo_id=settings.hf_model_repo_id, filename=settings.model)
        else:
            create_fn = sapiens_optimizer.Sapiens
            kwargs["model_path"] = settings.model
        _model = create_fn(**kwargs, n_gpu_layers=settings.n_gpu_layers, split_mode=settings.split_mode, main_gpu=settings.main_gpu, tensor_split=settings.tensor_split,
        vocab_only=settings.vocab_only, use_mmap=settings.use_mmap, use_mlock=settings.use_mlock, kv_overrides=kv_overrides, rpc_servers=settings.rpc_servers,
        seed=settings.seed, n_ctx=settings.n_ctx, n_batch=settings.n_batch, n_ubatch=settings.n_ubatch, n_threads=settings.n_threads, n_threads_batch=settings.n_threads_batch,
        rope_scaling_type=settings.rope_scaling_type, rope_freq_base=settings.rope_freq_base, rope_freq_scale=settings.rope_freq_scale, yarn_ext_factor=settings.yarn_ext_factor,
        yarn_attn_factor=settings.yarn_attn_factor, yarn_beta_fast=settings.yarn_beta_fast, yarn_beta_slow=settings.yarn_beta_slow, yarn_orig_ctx=settings.yarn_orig_ctx,
        mul_mat_q=settings.mul_mat_q, logits_all=settings.logits_all, embedding=settings.embedding, offload_kqv=settings.offload_kqv, flash_attn=settings.flash_attn,
        last_n_tokens_size=settings.last_n_tokens_size, lora_base=settings.lora_base, lora_path=settings.lora_path, numa=settings.numa, chat_format=settings.chat_format,
        chat_handler=chat_handler, draft_model=draft_model, type_k=settings.type_k, type_v=settings.type_v, tokenizer=tokenizer, verbose=settings.verbose)
        if settings.cache:
            if settings.cache_type == "disk":
                if settings.verbose: print(f"Using disk cache with size {settings.cache_size}")
                cache = sapiens_optimizer.SapiensDiskCache(capacity_bytes=settings.cache_size)
            else:
                if settings.verbose: print(f"Using ram cache with size {settings.cache_size}")
                cache = sapiens_optimizer.SapiensRAMCache(capacity_bytes=settings.cache_size)
            _model.set_cache(cache)
        return _model
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
