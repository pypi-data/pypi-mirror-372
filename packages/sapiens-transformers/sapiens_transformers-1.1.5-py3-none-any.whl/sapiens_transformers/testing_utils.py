"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from .utils import (SAPIENS_ACCELERATOR_MIN_VERSION, GGUF_MIN_VERSION, is_sapiens_accelerator_available, is_apex_available, is_aqlm_available, is_auto_awq_available, is_auto_gptq_available,
is_av_available, is_sapiens_machine_available, is_sapiens_machine_multi_backend_available, is_bs4_available, is_compressed_tensors_available, is_cv2_available, is_cython_available,
is_decord_available, is_detectron2_available, is_eetq_available, is_essentia_available, is_faiss_available, is_fbgemm_gpu_available, is_flash_attn_2_available, is_flax_available,
is_fsdp_available, is_ftfy_available, is_g2p_en_available, is_galore_torch_available, is_gguf_available, is_grokadamw_available, is_ipex_available, is_jieba_available,
is_jinja_available, is_jumanpp_available, is_keras_nlp_available, is_levenshtein_available, is_librosa_available, is_liger_kernel_available, is_lomo_available, is_natten_available,
is_nltk_available, is_onnx_available, is_optimum_available, is_pandas_available, is_peft_available, is_phonemizer_available, is_pretty_midi_available, is_pyctcdecode_available,
is_pytesseract_available, is_pytest_available, is_pytorch_quantization_available, is_quanto_available, is_rjieba_available, is_sacremoses_available, is_safetensors_available,
is_schedulefree_available, is_scipy_available, is_sentencepiece_available, is_seqio_available, is_soundfile_availble, is_spacy_available, is_sudachi_available, is_sudachi_projection_available,
is_tensorflow_probability_available, is_tensorflow_text_available, is_tf2onnx_available, is_tf_available, is_tiktoken_available, is_timm_available, is_tokenizers_available, is_torch_available,
is_torch_bf16_available_on_device, is_torch_bf16_cpu_available, is_torch_bf16_gpu_available, is_torch_deterministic, is_torch_fp16_available_on_device, is_torch_neuroncore_available,
is_torch_npu_available, is_torch_sdpa_available, is_torch_tensorrt_fx_available, is_torch_tf32_available, is_torch_xla_available, is_torch_xpu_available, is_torchao_available,
is_torchaudio_available, is_torchdynamo_available, is_torchvision_available, is_vision_available, strtobool)
from .integrations import (is_clearml_available, is_optuna_available, is_ray_available, is_sigopt_available, is_tensorboard_available, is_wandb_available)
from typing import Callable, Dict, Iterable, Iterator, List, Optional, Union
from .integrations.deepspeed import is_deepspeed_available
from sapiens_transformers import logging as transformers_logging
from collections import defaultdict
from collections.abc import Mapping
from unittest.mock import patch
from functools import wraps
from unittest import mock
from pathlib import Path
from io import StringIO
import multiprocessing
import collections
import contextlib
import subprocess
import functools
import importlib
import tempfile
import unittest
import urllib3
import doctest
import inspect
import logging
import shutil
import shlex
import time
import sys
import os
import re
if is_sapiens_accelerator_available(): from sapiens_accelerator.state import AcceleratorState, PartialState
if is_pytest_available():
    from _pytest.doctest import (Module, _get_checker, _get_continue_on_failure, _get_runner, _is_mocked, _patch_unwrap_mock_aware, get_optionflags)
    from _pytest.outcomes import skip
    from _pytest.pathlib import import_path
    from pytest import DoctestItem
else:
    Module = object
    DoctestItem = object
SMALL_MODEL_IDENTIFIER = "julien-c/bert-xsmall-dummy"
DUMMY_UNKNOWN_IDENTIFIER = "julien-c/dummy-unknown"
DUMMY_DIFF_TOKENIZER_IDENTIFIER = "julien-c/dummy-diff-tokenizer"
USER = "__DUMMY_TRANSFORMERS_USER__"
ENDPOINT_STAGING = "https://hub-ci.huggingface.co"
TOKEN = "hf_94wBhPGp6KrrTH3KDchhKpRxZwd6dmHWLL"
if is_torch_available():
    import torch
    IS_ROCM_SYSTEM = torch.version.hip is not None
    IS_CUDA_SYSTEM = torch.version.cuda is not None
else:
    IS_ROCM_SYSTEM = False
    IS_CUDA_SYSTEM = False
def parse_flag_from_env(key, default=False):
    try: value = os.environ[key]
    except KeyError: _value = default
    else:
        try: _value = strtobool(value)
        except ValueError: raise ValueError(f"If set, {key} must be yes or no.")
    return _value
def parse_int_from_env(key, default=None):
    try: value = os.environ[key]
    except KeyError: _value = default
    else:
        try: _value = int(value)
        except ValueError: raise ValueError(f"If set, {key} must be a int.")
    return _value
_run_slow_tests = parse_flag_from_env("RUN_SLOW", default=False)
_run_pt_tf_cross_tests = parse_flag_from_env("RUN_PT_TF_CROSS_TESTS", default=True)
_run_pt_flax_cross_tests = parse_flag_from_env("RUN_PT_FLAX_CROSS_TESTS", default=True)
_run_custom_tokenizers = parse_flag_from_env("RUN_CUSTOM_TOKENIZERS", default=False)
_run_staging = parse_flag_from_env("HUGGINGFACE_CO_STAGING", default=False)
_tf_gpu_memory_limit = parse_int_from_env("TF_GPU_MEMORY_LIMIT", default=None)
_run_pipeline_tests = parse_flag_from_env("RUN_PIPELINE_TESTS", default=True)
_run_agent_tests = parse_flag_from_env("RUN_AGENT_TESTS", default=False)
_run_third_party_device_tests = parse_flag_from_env("RUN_THIRD_PARTY_DEVICE_TESTS", default=False)
def get_device_count():
    import torch
    if is_torch_xpu_available(): num_devices = torch.xpu.device_count()
    else: num_devices = torch.cuda.device_count()
    return num_devices
def is_pt_tf_cross_test(test_case):
    if not _run_pt_tf_cross_tests or not is_torch_available() or not is_tf_available(): return unittest.skip(reason="test is PT+TF test")(test_case)
    else:
        try: import pytest
        except ImportError: return test_case
        else: return pytest.mark.is_pt_tf_cross_test()(test_case)
def is_pt_flax_cross_test(test_case):
    if not _run_pt_flax_cross_tests or not is_torch_available() or not is_flax_available(): return unittest.skip(reason="test is PT+FLAX test")(test_case)
    else:
        try: import pytest
        except ImportError: return test_case
        else: return pytest.mark.is_pt_flax_cross_test()(test_case)
def is_staging_test(test_case):
    if not _run_staging: return unittest.skip(reason="test is staging test")(test_case)
    else:
        try: import pytest
        except ImportError: return test_case
        else: return pytest.mark.is_staging_test()(test_case)
def is_pipeline_test(test_case):
    if not _run_pipeline_tests: return unittest.skip(reason="test is pipeline test")(test_case)
    else:
        try: import pytest
        except ImportError: return test_case
        else: return pytest.mark.is_pipeline_test()(test_case)
def is_agent_test(test_case):
    if not _run_agent_tests: return unittest.skip(reason="test is an agent test")(test_case)
    else:
        try: import pytest
        except ImportError: return test_case
        else: return pytest.mark.is_agent_test()(test_case)
def slow(test_case): return unittest.skipUnless(_run_slow_tests, "test is slow")(test_case)
def tooslow(test_case): return unittest.skip(reason="test is too slow")(test_case)
def skip_if_not_implemented(test_func):
    @functools.wraps(test_func)
    def wrapper(*args, **kwargs):
        try: return test_func(*args, **kwargs)
        except NotImplementedError as e: raise unittest.SkipTest(f"Test skipped due to NotImplementedError: {e}")
    return wrapper
def apply_skip_if_not_implemented(cls):
    for attr_name in dir(cls):
        if attr_name.startswith("test_"):
            attr = getattr(cls, attr_name)
            if callable(attr): setattr(cls, attr_name, skip_if_not_implemented(attr))
    return cls
def custom_tokenizers(test_case): return unittest.skipUnless(_run_custom_tokenizers, "test of custom tokenizers")(test_case)
def require_bs4(test_case): return unittest.skipUnless(is_bs4_available(), "test requires BeautifulSoup4")(test_case)
def require_galore_torch(test_case): return unittest.skipUnless(is_galore_torch_available(), "test requires GaLore")(test_case)
def require_lomo(test_case): return unittest.skipUnless(is_lomo_available(), "test requires LOMO")(test_case)
def require_grokadamw(test_case): return unittest.skipUnless(is_grokadamw_available(), "test requires GrokAdamW")(test_case)
def require_schedulefree(test_case): return unittest.skipUnless(is_schedulefree_available(), "test requires schedulefree")(test_case)
def require_cv2(test_case): return unittest.skipUnless(is_cv2_available(), "test requires OpenCV")(test_case)
def require_levenshtein(test_case): return unittest.skipUnless(is_levenshtein_available(), "test requires Levenshtein")(test_case)
def require_nltk(test_case): return unittest.skipUnless(is_nltk_available(), "test requires NLTK")(test_case)
def require_sapiens_accelerator(test_case, min_version: str = SAPIENS_ACCELERATOR_MIN_VERSION): return unittest.skipUnless(is_sapiens_accelerator_available(min_version), f"test requires sapiens_accelerator version >= {min_version}")(test_case)
def require_gguf(test_case, min_version: str = GGUF_MIN_VERSION): return unittest.skipUnless(is_gguf_available(min_version), f"test requires gguf version >= {min_version}")(test_case)
def require_fsdp(test_case, min_version: str = "1.12.0"): return unittest.skipUnless(is_fsdp_available(min_version), f"test requires torch version >= {min_version}")(test_case)
def require_g2p_en(test_case): return unittest.skipUnless(is_g2p_en_available(), "test requires g2p_en")(test_case)
def require_safetensors(test_case): return unittest.skipUnless(is_safetensors_available(), "test requires safetensors")(test_case)
def require_rjieba(test_case): return unittest.skipUnless(is_rjieba_available(), "test requires rjieba")(test_case)
def require_jieba(test_case): return unittest.skipUnless(is_jieba_available(), "test requires jieba")(test_case)
def require_jinja(test_case): return unittest.skipUnless(is_jinja_available(), "test requires jinja")(test_case)
def require_tf2onnx(test_case): return unittest.skipUnless(is_tf2onnx_available(), "test requires tf2onnx")(test_case)
def require_onnx(test_case): return unittest.skipUnless(is_onnx_available(), "test requires ONNX")(test_case)
def require_timm(test_case): return unittest.skipUnless(is_timm_available(), "test requires Timm")(test_case)
def require_natten(test_case): return unittest.skipUnless(is_natten_available(), "test requires natten")(test_case)
def require_torch(test_case): return unittest.skipUnless(is_torch_available(), "test requires PyTorch")(test_case)
def require_flash_attn(test_case): return unittest.skipUnless(is_flash_attn_2_available(), "test requires Flash Attention")(test_case)
def require_torch_sdpa(test_case): return unittest.skipUnless(is_torch_sdpa_available(), "test requires PyTorch SDPA")(test_case)
def require_read_token(fn):
    token = os.getenv("HF_HUB_READ_TOKEN")
    @wraps(fn)
    def _inner(*args, **kwargs):
        if token is not None:
            with patch("huggingface_hub.utils._headers.get_token", return_value=token): return fn(*args, **kwargs)
        else: return fn(*args, **kwargs)
    return _inner
def require_peft(test_case): return unittest.skipUnless(is_peft_available(), "test requires PEFT")(test_case)
def require_torchvision(test_case): return unittest.skipUnless(is_torchvision_available(), "test requires Torchvision")(test_case)
def require_torch_or_tf(test_case): return unittest.skipUnless(is_torch_available() or is_tf_available(), "test requires PyTorch or TensorFlow")(test_case)
def require_intel_extension_for_pytorch(test_case): return unittest.skipUnless(is_ipex_available(), "test requires Intel Extension for PyTorch to be installed and match current PyTorch version, see https://github.com/intel/intel-extension-for-pytorch",)(test_case)
def require_tensorflow_probability(test_case): return unittest.skipUnless(is_tensorflow_probability_available(), "test requires TensorFlow probability")(test_case)
def require_torchaudio(test_case): return unittest.skipUnless(is_torchaudio_available(), "test requires torchaudio")(test_case)
def require_tf(test_case): return unittest.skipUnless(is_tf_available(), "test requires TensorFlow")(test_case)
def require_flax(test_case): return unittest.skipUnless(is_flax_available(), "test requires JAX & Flax")(test_case)
def require_sentencepiece(test_case): return unittest.skipUnless(is_sentencepiece_available(), "test requires SentencePiece")(test_case)
def require_sacremoses(test_case): return unittest.skipUnless(is_sacremoses_available(), "test requires Sacremoses")(test_case)
def require_seqio(test_case): return unittest.skipUnless(is_seqio_available(), "test requires Seqio")(test_case)
def require_scipy(test_case): return unittest.skipUnless(is_scipy_available(), "test requires Scipy")(test_case)
def require_tokenizers(test_case): return unittest.skipUnless(is_tokenizers_available(), "test requires tokenizers")(test_case)
def require_tensorflow_text(test_case): return unittest.skipUnless(is_tensorflow_text_available(), "test requires tensorflow_text")(test_case)
def require_keras_nlp(test_case): return unittest.skipUnless(is_keras_nlp_available(), "test requires keras_nlp")(test_case)
def require_pandas(test_case): return unittest.skipUnless(is_pandas_available(), "test requires pandas")(test_case)
def require_pytesseract(test_case): return unittest.skipUnless(is_pytesseract_available(), "test requires PyTesseract")(test_case)
def require_pytorch_quantization(test_case): return unittest.skipUnless(is_pytorch_quantization_available(), "test requires PyTorch Quantization Toolkit")(test_case)
def require_vision(test_case): return unittest.skipUnless(is_vision_available(), "test requires vision")(test_case)
def require_ftfy(test_case): return unittest.skipUnless(is_ftfy_available(), "test requires ftfy")(test_case)
def require_spacy(test_case): return unittest.skipUnless(is_spacy_available(), "test requires spacy")(test_case)
def require_decord(test_case): return unittest.skipUnless(is_decord_available(), "test requires decord")(test_case)
def require_torch_multi_gpu(test_case):
    if not is_torch_available(): return unittest.skip(reason="test requires PyTorch")(test_case)
    device_count = get_device_count()
    return unittest.skipUnless(device_count > 1, "test requires multiple GPUs")(test_case)
def require_torch_multi_accelerator(test_case):
    if not is_torch_available(): return unittest.skip(reason="test requires PyTorch")(test_case)
    return unittest.skipUnless(backend_device_count(torch_device) > 1, "test requires multiple accelerators")(test_case)
def require_torch_non_multi_gpu(test_case):
    if not is_torch_available(): return unittest.skip(reason="test requires PyTorch")(test_case)
    import torch
    return unittest.skipUnless(torch.cuda.device_count() < 2, "test requires 0 or 1 GPU")(test_case)
def require_torch_non_multi_accelerator(test_case):
    if not is_torch_available(): return unittest.skip(reason="test requires PyTorch")(test_case)
    return unittest.skipUnless(backend_device_count(torch_device) < 2, "test requires 0 or 1 accelerator")(test_case)
def require_torch_up_to_2_gpus(test_case):
    if not is_torch_available(): return unittest.skip(reason="test requires PyTorch")(test_case)
    import torch
    return unittest.skipUnless(torch.cuda.device_count() < 3, "test requires 0 or 1 or 2 GPUs")(test_case)
def require_torch_up_to_2_accelerators(test_case):
    if not is_torch_available(): return unittest.skip(reason="test requires PyTorch")(test_case)
    return unittest.skipUnless(backend_device_count(torch_device) < 3, "test requires 0 or 1 or 2 accelerators")
    (test_case)
def require_torch_xla(test_case): return unittest.skipUnless(is_torch_xla_available(), "test requires TorchXLA")(test_case)
def require_torch_neuroncore(test_case): return unittest.skipUnless(is_torch_neuroncore_available(check_device=False), "test requires PyTorch NeuronCore")(test_case)
def require_torch_npu(test_case): return unittest.skipUnless(is_torch_npu_available(), "test requires PyTorch NPU")(test_case)
def require_torch_multi_npu(test_case):
    if not is_torch_npu_available(): return unittest.skip(reason="test requires PyTorch NPU")(test_case)
    return unittest.skipUnless(torch.npu.device_count() > 1, "test requires multiple NPUs")(test_case)
def require_torch_xpu(test_case): return unittest.skipUnless(is_torch_xpu_available(), "test requires XPU device")(test_case)
def require_non_xpu(test_case): return unittest.skipUnless(torch_device != "xpu", "test requires a non-XPU")(test_case)
def require_torch_multi_xpu(test_case):
    if not is_torch_xpu_available(): return unittest.skip(reason="test requires PyTorch XPU")(test_case)
    return unittest.skipUnless(torch.xpu.device_count() > 1, "test requires multiple XPUs")(test_case)
if is_torch_available():
    import torch
    if "TRANSFORMERS_TEST_BACKEND" in os.environ:
        backend = os.environ["TRANSFORMERS_TEST_BACKEND"]
        try: _ = importlib.import_module(backend)
        except ModuleNotFoundError as e: raise ModuleNotFoundError(f"Failed to import `TRANSFORMERS_TEST_BACKEND` '{backend}'! This should be the name of an installed module. The original error (look up to see its traceback):\n{e}") from e
    if "TRANSFORMERS_TEST_DEVICE" in os.environ:
        torch_device = os.environ["TRANSFORMERS_TEST_DEVICE"]
        if torch_device == "cuda" and not torch.cuda.is_available(): raise ValueError(f"TRANSFORMERS_TEST_DEVICE={torch_device}, but CUDA is unavailable. Please double-check your testing environment.")
        if torch_device == "xpu" and not is_torch_xpu_available(): raise ValueError(f"TRANSFORMERS_TEST_DEVICE={torch_device}, but XPU is unavailable. Please double-check your testing environment.")
        if torch_device == "npu" and not is_torch_npu_available(): raise ValueError(f"TRANSFORMERS_TEST_DEVICE={torch_device}, but NPU is unavailable. Please double-check your testing environment.")
        try: _ = torch.device(torch_device)
        except RuntimeError as e: raise RuntimeError(f"Unknown testing device specified by environment variable `TRANSFORMERS_TEST_DEVICE`: {torch_device}") from e
    elif torch.cuda.is_available(): torch_device = "cuda"
    elif _run_third_party_device_tests and is_torch_npu_available(): torch_device = "npu"
    elif _run_third_party_device_tests and is_torch_xpu_available(): torch_device = "xpu"
    else: torch_device = "cpu"
else: torch_device = None
if is_tf_available(): import tensorflow as tf
if is_flax_available():
    import jax
    jax_device = jax.default_backend()
else: jax_device = None
def require_torchdynamo(test_case): return unittest.skipUnless(is_torchdynamo_available(), "test requires TorchDynamo")(test_case)
def require_torchao(test_case): return unittest.skipUnless(is_torchao_available(), "test requires torchao")(test_case)
def require_torch_tensorrt_fx(test_case): return unittest.skipUnless(is_torch_tensorrt_fx_available(), "test requires Torch-TensorRT FX")(test_case)
def require_torch_gpu(test_case): return unittest.skipUnless(torch_device == "cuda", "test requires CUDA")(test_case)
def require_torch_gpu_if_sapiens_not_multi_backend_enabled(test_case):
    if is_sapiens_machine_available() and is_sapiens_machine_multi_backend_available(): return test_case
    return require_torch_gpu(test_case)
def require_torch_accelerator(test_case): return unittest.skipUnless(torch_device is not None and torch_device != "cpu", "test requires accelerator")(test_case)
def require_torch_fp16(test_case): return unittest.skipUnless(is_torch_fp16_available_on_device(torch_device), "test requires device with fp16 support")(test_case)
def require_torch_bf16(test_case): return unittest.skipUnless(is_torch_bf16_available_on_device(torch_device), "test requires device with bf16 support")(test_case)
def require_torch_bf16_gpu(test_case): return unittest.skipUnless(is_torch_bf16_gpu_available(), "test requires torch>=1.10, using Ampere GPU or newer arch with cuda>=11.0",)(test_case)
def require_torch_bf16_cpu(test_case): return unittest.skipUnless(is_torch_bf16_cpu_available(), "test requires torch>=1.10, using CPU",)(test_case)
def require_deterministic_for_xpu(test_case):
    if is_torch_xpu_available(): return unittest.skipUnless(is_torch_deterministic(), "test requires torch to use deterministic algorithms")(test_case)
    else: return test_case
def require_torch_tf32(test_case): return unittest.skipUnless(is_torch_tf32_available(), "test requires Ampere or a newer GPU arch, cuda>=11 and torch>=1.7")(test_case)
def require_detectron2(test_case): return unittest.skipUnless(is_detectron2_available(), "test requires `detectron2`")(test_case)
def require_faiss(test_case): return unittest.skipUnless(is_faiss_available(), "test requires `faiss`")(test_case)
def require_optuna(test_case): return unittest.skipUnless(is_optuna_available(), "test requires optuna")(test_case)
def require_ray(test_case): return unittest.skipUnless(is_ray_available(), "test requires Ray/tune")(test_case)
def require_sigopt(test_case): return unittest.skipUnless(is_sigopt_available(), "test requires SigOpt")(test_case)
def require_wandb(test_case): return unittest.skipUnless(is_wandb_available(), "test requires wandb")(test_case)
def require_clearml(test_case): return unittest.skipUnless(is_clearml_available(), "test requires clearml")(test_case)
def require_soundfile(test_case): return unittest.skipUnless(is_soundfile_availble(), "test requires soundfile")(test_case)
def require_deepspeed(test_case): return unittest.skipUnless(is_deepspeed_available(), "test requires deepspeed")(test_case)
def require_apex(test_case): return unittest.skipUnless(is_apex_available(), "test requires apex")(test_case)
def require_aqlm(test_case): return unittest.skipUnless(is_aqlm_available(), "test requires aqlm")(test_case)
def require_eetq(test_case): return unittest.skipUnless(is_eetq_available(), "test requires eetq")(test_case)
def require_av(test_case): return unittest.skipUnless(is_av_available(), "test requires av")(test_case)
def require_sapiens_machine(test_case):
    if is_sapiens_machine_available() and is_torch_available():
        try:
            import pytest
            return pytest.mark.sapiens_machine(test_case)
        except ImportError: return test_case
    else: return unittest.skip(reason="test requires sapiens_machine and torch")(test_case)
def require_optimum(test_case): return unittest.skipUnless(is_optimum_available(), "test requires optimum")(test_case)
def require_tensorboard(test_case): return unittest.skipUnless(is_tensorboard_available(), "test requires tensorboard")
def require_auto_gptq(test_case): return unittest.skipUnless(is_auto_gptq_available(), "test requires auto-gptq")(test_case)
def require_auto_awq(test_case): return unittest.skipUnless(is_auto_awq_available(), "test requires autoawq")(test_case)
def require_quanto(test_case): return unittest.skipUnless(is_quanto_available(), "test requires quanto")(test_case)
def require_compressed_tensors(test_case): return unittest.skipUnless(is_compressed_tensors_available(), "test requires compressed_tensors")(test_case)
def require_fbgemm_gpu(test_case): return unittest.skipUnless(is_fbgemm_gpu_available(), "test requires fbgemm-gpu")(test_case)
def require_phonemizer(test_case): return unittest.skipUnless(is_phonemizer_available(), "test requires phonemizer")(test_case)
def require_pyctcdecode(test_case): return unittest.skipUnless(is_pyctcdecode_available(), "test requires pyctcdecode")(test_case)
def require_librosa(test_case): return unittest.skipUnless(is_librosa_available(), "test requires librosa")(test_case)
def require_liger_kernel(test_case): return unittest.skipUnless(is_liger_kernel_available(), "test requires liger_kernel")(test_case)
def require_essentia(test_case): return unittest.skipUnless(is_essentia_available(), "test requires essentia")(test_case)
def require_pretty_midi(test_case): return unittest.skipUnless(is_pretty_midi_available(), "test requires pretty_midi")(test_case)
def cmd_exists(cmd): return shutil.which(cmd) is not None
def require_usr_bin_time(test_case): return unittest.skipUnless(cmd_exists("/usr/bin/time"), "test requires /usr/bin/time")(test_case)
def require_sudachi(test_case): return unittest.skipUnless(is_sudachi_available(), "test requires sudachi")(test_case)
def require_sudachi_projection(test_case): return unittest.skipUnless(is_sudachi_projection_available(), "test requires sudachi which supports projection")(test_case)
def require_jumanpp(test_case): return unittest.skipUnless(is_jumanpp_available(), "test requires jumanpp")(test_case)
def require_cython(test_case): return unittest.skipUnless(is_cython_available(), "test requires cython")(test_case)
def require_tiktoken(test_case): return unittest.skipUnless(is_tiktoken_available(), "test requires TikToken")(test_case)
def get_gpu_count():
    if is_torch_available():
        import torch
        return torch.cuda.device_count()
    elif is_tf_available():
        import tensorflow as tf
        return len(tf.config.list_physical_devices("GPU"))
    elif is_flax_available():
        import jax
        return jax.device_count()
    else: return 0
def get_tests_dir(append_path=None):
    caller__file__ = inspect.stack()[1][1]
    tests_dir = os.path.abspath(os.path.dirname(caller__file__))
    while not tests_dir.endswith("tests"): tests_dir = os.path.dirname(tests_dir)
    if append_path: return os.path.join(tests_dir, append_path)
    else: return tests_dir
def apply_print_resets(buf): return re.sub(r"^.*\r", "", buf, 0, re.M)
def assert_screenout(out, what):
    out_pr = apply_print_resets(out).lower()
    match_str = out_pr.find(what.lower())
    assert match_str != -1, f"expecting to find {what} in output: f{out_pr}"
class CaptureStd:
    def __init__(self, out=True, err=True, replay=True):
        self.replay = replay
        if out:
            self.out_buf = StringIO()
            self.out = "error: CaptureStd context is unfinished yet, called too early"
        else:
            self.out_buf = None
            self.out = "not capturing stdout"
        if err:
            self.err_buf = StringIO()
            self.err = "error: CaptureStd context is unfinished yet, called too early"
        else:
            self.err_buf = None
            self.err = "not capturing stderr"
    def __enter__(self):
        if self.out_buf:
            self.out_old = sys.stdout
            sys.stdout = self.out_buf
        if self.err_buf:
            self.err_old = sys.stderr
            sys.stderr = self.err_buf
        return self
    def __exit__(self, *exc):
        if self.out_buf:
            sys.stdout = self.out_old
            captured = self.out_buf.getvalue()
            if self.replay: sys.stdout.write(captured)
            self.out = apply_print_resets(captured)
        if self.err_buf:
            sys.stderr = self.err_old
            captured = self.err_buf.getvalue()
            if self.replay: sys.stderr.write(captured)
            self.err = captured
    def __repr__(self):
        msg = ""
        if self.out_buf: msg += f"stdout: {self.out}\n"
        if self.err_buf: msg += f"stderr: {self.err}\n"
        return msg
class CaptureStdout(CaptureStd):
    def __init__(self, replay=True): super().__init__(err=False, replay=replay)
class CaptureStderr(CaptureStd):
    def __init__(self, replay=True): super().__init__(out=False, replay=replay)
class CaptureLogger:
    def __init__(self, logger):
        self.logger = logger
        self.io = StringIO()
        self.sh = logging.StreamHandler(self.io)
        self.out = ""
    def __enter__(self):
        self.logger.addHandler(self.sh)
        return self
    def __exit__(self, *exc):
        self.logger.removeHandler(self.sh)
        self.out = self.io.getvalue()
    def __repr__(self): return f"captured: {self.out}\n"
@contextlib.contextmanager
def LoggingLevel(level):
    orig_level = transformers_logging.get_verbosity()
    try:
        transformers_logging.set_verbosity(level)
        yield
    finally: transformers_logging.set_verbosity(orig_level)
@contextlib.contextmanager
def ExtendSysPath(path: Union[str, os.PathLike]) -> Iterator[None]:
    path = os.fspath(path)
    try:
        sys.path.insert(0, path)
        yield
    finally: sys.path.remove(path)
class TestCasePlus(unittest.TestCase):
    def setUp(self):
        self.teardown_tmp_dirs = []
        self._test_file_path = inspect.getfile(self.__class__)
        path = Path(self._test_file_path).resolve()
        self._test_file_dir = path.parents[0]
        for up in [1, 2, 3]:
            tmp_dir = path.parents[up]
            if (tmp_dir / "src").is_dir() and (tmp_dir / "tests").is_dir(): break
        if tmp_dir: self._repo_root_dir = tmp_dir
        else: raise ValueError(f"can't figure out the root of the repo from {self._test_file_path}")
        self._tests_dir = self._repo_root_dir / "tests"
        self._examples_dir = self._repo_root_dir / "examples"
        self._src_dir = self._repo_root_dir / "src"
    @property
    def test_file_path(self): return self._test_file_path
    @property
    def test_file_path_str(self): return str(self._test_file_path)
    @property
    def test_file_dir(self): return self._test_file_dir
    @property
    def test_file_dir_str(self): return str(self._test_file_dir)
    @property
    def tests_dir(self): return self._tests_dir
    @property
    def tests_dir_str(self): return str(self._tests_dir)
    @property
    def examples_dir(self): return self._examples_dir
    @property
    def examples_dir_str(self): return str(self._examples_dir)
    @property
    def repo_root_dir(self): return self._repo_root_dir
    @property
    def repo_root_dir_str(self): return str(self._repo_root_dir)
    @property
    def src_dir(self): return self._src_dir
    @property
    def src_dir_str(self): return str(self._src_dir)
    def get_env(self):
        env = os.environ.copy()
        paths = [self.src_dir_str]
        if "/examples" in self.test_file_dir_str: paths.append(self.examples_dir_str)
        else: paths.append(self.tests_dir_str)
        paths.append(env.get("PYTHONPATH", ""))
        env["PYTHONPATH"] = ":".join(paths)
        return env
    def get_auto_remove_tmp_dir(self, tmp_dir=None, before=None, after=None):
        if tmp_dir is not None:
            if before is None: before = True
            if after is None: after = False
            path = Path(tmp_dir).resolve()
            if not tmp_dir.startswith("./"): raise ValueError(f"`tmp_dir` can only be a relative path, i.e. `./some/path`, but received `{tmp_dir}`")
            if before is True and path.exists(): shutil.rmtree(tmp_dir, ignore_errors=True)
            path.mkdir(parents=True, exist_ok=True)
        else:
            if before is None: before = True
            if after is None: after = True
            tmp_dir = tempfile.mkdtemp()
        if after is True: self.teardown_tmp_dirs.append(tmp_dir)
        return tmp_dir
    def python_one_liner_max_rss(self, one_liner_str):
        if not cmd_exists("/usr/bin/time"): raise ValueError("/usr/bin/time is required, install with `apt install time`")
        cmd = shlex.split(f"/usr/bin/time -f %M python -c '{one_liner_str}'")
        with CaptureStd() as cs: execute_subprocess_async(cmd, env=self.get_env())
        max_rss = int(cs.err.split("\n")[-2].replace("stderr: ", "")) * 1024
        return max_rss
    def tearDown(self):
        for path in self.teardown_tmp_dirs: shutil.rmtree(path, ignore_errors=True)
        self.teardown_tmp_dirs = []
        if is_sapiens_accelerator_available():
            AcceleratorState._reset_state()
            PartialState._reset_state()
            for k in list(os.environ.keys()):
                if "SAPIENS_ACCELERATOR" in k: del os.environ[k]
def mockenv(**kwargs): return mock.patch.dict(os.environ, kwargs)
@contextlib.contextmanager
def mockenv_context(*remove, **update):
    env = os.environ
    update = update or {}
    remove = remove or []
    stomped = (set(update.keys()) | set(remove)) & set(env.keys())
    update_after = {k: env[k] for k in stomped}
    remove_after = frozenset(k for k in update if k not in env)
    try:
        env.update(update)
        [env.pop(k, None) for k in remove]
        yield
    finally:
        env.update(update_after)
        [env.pop(k) for k in remove_after]
pytest_opt_registered = {}
def pytest_addoption_shared(parser):
    option = "--make-reports"
    if option not in pytest_opt_registered:
        parser.addoption(option, action="store", default=False, help="generate report files. The value of this option is used as a prefix to report names")
        pytest_opt_registered[option] = 1
def pytest_terminal_summary_main(tr, id):
    from _pytest.config import create_terminal_writer
    if not len(id): id = "tests"
    config = tr.config
    orig_writer = config.get_terminal_writer()
    orig_tbstyle = config.option.tbstyle
    orig_reportchars = tr.reportchars
    dir = f"reports/{id}"
    Path(dir).mkdir(parents=True, exist_ok=True)
    report_files = {k: f"{dir}/{k}.txt" for k in ["durations", "errors", "failures_long", "failures_short", "failures_line", "passes", "stats", "summary_short", "warnings"]}
    dlist = []
    for replist in tr.stats.values():
        for rep in replist:
            if hasattr(rep, "duration"): dlist.append(rep)
    if dlist:
        dlist.sort(key=lambda x: x.duration, reverse=True)
        with open(report_files["durations"], "w") as f:
            durations_min = 0.05  # sec
            f.write("slowest durations\n")
            for i, rep in enumerate(dlist):
                if rep.duration < durations_min:
                    f.write(f"{len(dlist)-i} durations < {durations_min} secs were omitted")
                    break
                f.write(f"{rep.duration:02.2f}s {rep.when:<8} {rep.nodeid}\n")
    def summary_failures_short(tr):
        reports = tr.getreports("failed")
        if not reports: return
        tr.write_sep("=", "FAILURES SHORT STACK")
        for rep in reports:
            msg = tr._getfailureheadline(rep)
            tr.write_sep("_", msg, red=True, bold=True)
            longrepr = re.sub(r".*_ _ _ (_ ){10,}_ _ ", "", rep.longreprtext, 0, re.M | re.S)
            tr._tw.line(longrepr)
    config.option.tbstyle = "auto"
    with open(report_files["failures_long"], "w") as f:
        tr._tw = create_terminal_writer(config, f)
        tr.summary_failures()
    with open(report_files["failures_short"], "w") as f:
        tr._tw = create_terminal_writer(config, f)
        summary_failures_short(tr)
    config.option.tbstyle = "line"
    with open(report_files["failures_line"], "w") as f:
        tr._tw = create_terminal_writer(config, f)
        tr.summary_failures()
    with open(report_files["errors"], "w") as f:
        tr._tw = create_terminal_writer(config, f)
        tr.summary_errors()
    with open(report_files["warnings"], "w") as f:
        tr._tw = create_terminal_writer(config, f)
        tr.summary_warnings()
        tr.summary_warnings()
    tr.reportchars = "wPpsxXEf"
    with open(report_files["summary_short"], "w") as f:
        tr._tw = create_terminal_writer(config, f)
        tr.short_test_summary()
    with open(report_files["stats"], "w") as f:
        tr._tw = create_terminal_writer(config, f)
        tr.summary_stats()
    tr._tw = orig_writer
    tr.reportchars = orig_reportchars
    config.option.tbstyle = orig_tbstyle
import asyncio
class _RunOutput:
    def __init__(self, returncode, stdout, stderr):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
async def _read_stream(stream, callback):
    while True:
        line = await stream.readline()
        if line: callback(line)
        else: break
async def _stream_subprocess(cmd, env=None, stdin=None, timeout=None, quiet=False, echo=False) -> _RunOutput:
    if echo: print("\nRunning: ", " ".join(cmd))
    p = await asyncio.create_subprocess_exec(cmd[0], *cmd[1:], stdin=stdin, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, env=env)
    out = []
    err = []
    def tee(line, sink, pipe, label=""):
        line = line.decode("utf-8").rstrip()
        sink.append(line)
        if not quiet: print(label, line, file=pipe)
    await asyncio.wait([_read_stream(p.stdout, lambda l: tee(l, out, sys.stdout, label="stdout:")), _read_stream(p.stderr, lambda l: tee(l, err, sys.stderr, label="stderr:"))], timeout=timeout)
    return _RunOutput(await p.wait(), out, err)
def execute_subprocess_async(cmd, env=None, stdin=None, timeout=180, quiet=False, echo=True) -> _RunOutput:
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(_stream_subprocess(cmd, env=env, stdin=stdin, timeout=timeout, quiet=quiet, echo=echo))
    cmd_str = " ".join(cmd)
    if result.returncode > 0:
        stderr = "\n".join(result.stderr)
        raise RuntimeError(f"'{cmd_str}' failed with returncode {result.returncode}\n\nThe combined stderr from workers follows:\n{stderr}")
    if not result.stdout and not result.stderr: raise RuntimeError(f"'{cmd_str}' produced no output.")
    return result
def pytest_xdist_worker_id():
    worker = os.environ.get("PYTEST_XDIST_WORKER", "gw0")
    worker = re.sub(r"^gw", "", worker, 0, re.M)
    return int(worker)
def get_torch_dist_unique_port():
    port = 29500
    uniq_delta = pytest_xdist_worker_id()
    return port + uniq_delta
def nested_simplify(obj, decimals=3):
    import numpy as np
    if isinstance(obj, list): return [nested_simplify(item, decimals) for item in obj]
    if isinstance(obj, tuple): return tuple([nested_simplify(item, decimals) for item in obj])
    elif isinstance(obj, np.ndarray): return nested_simplify(obj.tolist())
    elif isinstance(obj, Mapping): return {nested_simplify(k, decimals): nested_simplify(v, decimals) for k, v in obj.items()}
    elif isinstance(obj, (str, int, np.int64)): return obj
    elif obj is None: return obj
    elif is_torch_available() and isinstance(obj, torch.Tensor): return nested_simplify(obj.tolist(), decimals)
    elif is_tf_available() and tf.is_tensor(obj): return nested_simplify(obj.numpy().tolist())
    elif isinstance(obj, float): return round(obj, decimals)
    elif isinstance(obj, (np.int32, np.float32, np.float16)): return nested_simplify(obj.item(), decimals)
    else: raise Exception(f"Not supported: {type(obj)}")
def check_json_file_has_correct_format(file_path):
    with open(file_path, "r") as f:
        lines = f.readlines()
        if len(lines) == 1: assert lines[0] == "{}"
        else:
            assert len(lines) >= 3
            assert lines[0].strip() == "{"
            for line in lines[1:-1]:
                left_indent = len(lines[1]) - len(lines[1].lstrip())
                assert left_indent == 2
            assert lines[-1].strip() == "}"
def to_2tuple(x):
    if isinstance(x, collections.abc.Iterable): return x
    return (x, x)
class SubprocessCallException(Exception): pass
def run_command(command: List[str], return_stdout=False):
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        if return_stdout:
            if hasattr(output, "decode"): output = output.decode("utf-8")
            return output
    except subprocess.CalledProcessError as e: raise SubprocessCallException(f"Command `{' '.join(command)}` failed with the following error:\n\n{e.output.decode()}") from e
class RequestCounter:
    def __enter__(self):
        self._counter = defaultdict(int)
        self.patcher = patch.object(urllib3.connectionpool.log, "debug", wraps=urllib3.connectionpool.log.debug)
        self.mock = self.patcher.start()
        return self
    def __exit__(self, *args, **kwargs) -> None:
        for call in self.mock.call_args_list:
            log = call.args[0] % call.args[1:]
            for method in ("HEAD", "GET", "POST", "PUT", "DELETE", "CONNECT", "OPTIONS", "TRACE", "PATCH"):
                if method in log:
                    self._counter[method] += 1
                    break
        self.patcher.stop()
    def __getitem__(self, key: str) -> int: return self._counter[key]
    @property
    def total_calls(self) -> int: return sum(self._counter.values())
def is_flaky(max_attempts: int = 5, wait_before_retry: Optional[float] = None, description: Optional[str] = None):
    def decorator(test_func_ref):
        @functools.wraps(test_func_ref)
        def wrapper(*args, **kwargs):
            retry_count = 1
            while retry_count < max_attempts:
                try: return test_func_ref(*args, **kwargs)
                except Exception as err:
                    print(f"Test failed with {err} at try {retry_count}/{max_attempts}.", file=sys.stderr)
                    if wait_before_retry is not None: time.sleep(wait_before_retry)
                    retry_count += 1
            return test_func_ref(*args, **kwargs)
        return wrapper
    return decorator
def run_test_in_subprocess(test_case, target_func, inputs=None, timeout=None):
    if timeout is None: timeout = int(os.environ.get("PYTEST_TIMEOUT", 600))
    start_methohd = "spawn"
    ctx = multiprocessing.get_context(start_methohd)
    input_queue = ctx.Queue(1)
    output_queue = ctx.JoinableQueue(1)
    input_queue.put(inputs, timeout=timeout)
    process = ctx.Process(target=target_func, args=(input_queue, output_queue, timeout))
    process.start()
    try:
        results = output_queue.get(timeout=timeout)
        output_queue.task_done()
    except Exception as e:
        process.terminate()
        test_case.fail(e)
    process.join(timeout=timeout)
    if results["error"] is not None: test_case.fail(f'{results["error"]}')
def preprocess_string(string, skip_cuda_tests):
    codeblock_pattern = r"(```(?:python|py)\s*\n\s*>>> )((?:.*?\n)*?.*?```)"
    codeblocks = re.split(re.compile(codeblock_pattern, flags=re.MULTILINE | re.DOTALL), string)
    is_cuda_found = False
    for i, codeblock in enumerate(codeblocks):
        if "load_dataset(" in codeblock and "# doctest: +IGNORE_RESULT" not in codeblock: codeblocks[i] = re.sub(r"(>>> .*load_dataset\(.*)", r"\1 # doctest: +IGNORE_RESULT", codeblock)
        if ((">>>" in codeblock or "..." in codeblock) and re.search(r"cuda|to\(0\)|device=0", codeblock) and skip_cuda_tests):
            is_cuda_found = True
            break
    modified_string = ""
    if not is_cuda_found: modified_string = "".join(codeblocks)
    return modified_string
class HfDocTestParser(doctest.DocTestParser):
    _EXAMPLE_RE = re.compile(r'''
        (?P<source>
            (?:^(?P<indent> [ ]*) >>>    .*)
            (?:\n           [ ]*  \.\.\. .*)*)
        \n?
        (?P<want> (?:(?![ ]*$)
             (?![ ]*>>>)
             (?:(?!```).)*
             (?:\n|$)
          )*)
        ''', re.MULTILINE | re.VERBOSE)
    skip_cuda_tests: bool = bool(os.environ.get("SKIP_CUDA_DOCTEST", False))
    def parse(self, string, name="<string>"):
        string = preprocess_string(string, self.skip_cuda_tests)
        return super().parse(string, name)
class HfDoctestModule(Module):
    def collect(self) -> Iterable[DoctestItem]:
        class MockAwareDocTestFinder(doctest.DocTestFinder):
            def _find_lineno(self, obj, source_lines):
                if isinstance(obj, property): obj = getattr(obj, "fget", obj)
                if hasattr(obj, "__wrapped__"): obj = inspect.unwrap(obj)
                return super()._find_lineno(  # type:ignore[misc]
                obj, source_lines)
            def _find(self, tests, obj, name, module, source_lines, globs, seen) -> None:
                if _is_mocked(obj): return
                with _patch_unwrap_mock_aware():
                    super()._find(  # type:ignore[misc]
                    tests, obj, name, module, source_lines, globs, seen)
        if self.path.name == "conftest.py": module = self.config.pluginmanager._importconftest(self.path, self.config.getoption("importmode"), rootpath=self.config.rootpath)
        else:
            try: module = import_path(self.path, root=self.config.rootpath, mode=self.config.getoption("importmode"))
            except ImportError:
                if self.config.getvalue("doctest_ignore_import_errors"): skip("unable to import module %r" % self.path)
                else: raise
        finder = MockAwareDocTestFinder(parser=HfDocTestParser())
        optionflags = get_optionflags(self)
        runner = _get_runner(verbose=False, optionflags=optionflags, checker=_get_checker(), continue_on_failure=_get_continue_on_failure(self.config))
        for test in finder.find(module, module.__name__):
            if test.examples: yield DoctestItem.from_parent(self, name=test.name, runner=runner, dtest=test)
def _device_agnostic_dispatch(device: str, dispatch_table: Dict[str, Callable], *args, **kwargs):
    if device not in dispatch_table: return dispatch_table["default"](*args, **kwargs)
    fn = dispatch_table[device]
    if fn is None: return None
    return fn(*args, **kwargs)
if is_torch_available():
    BACKEND_MANUAL_SEED = {"cuda": torch.cuda.manual_seed, "cpu": torch.manual_seed, "default": torch.manual_seed}
    BACKEND_EMPTY_CACHE = {"cuda": torch.cuda.empty_cache, "cpu": None, "default": None}
    BACKEND_DEVICE_COUNT = {"cuda": torch.cuda.device_count, "cpu": lambda: 0, "default": lambda: 1}
else:
    BACKEND_MANUAL_SEED = {"default": None}
    BACKEND_EMPTY_CACHE = {"default": None}
    BACKEND_DEVICE_COUNT = {"default": lambda: 0}
def backend_manual_seed(device: str, seed: int): return _device_agnostic_dispatch(device, BACKEND_MANUAL_SEED, seed)
def backend_empty_cache(device: str): return _device_agnostic_dispatch(device, BACKEND_EMPTY_CACHE)
def backend_device_count(device: str): return _device_agnostic_dispatch(device, BACKEND_DEVICE_COUNT)
if is_torch_available():
    if "TRANSFORMERS_TEST_DEVICE_SPEC" in os.environ:
        device_spec_path = os.environ["TRANSFORMERS_TEST_DEVICE_SPEC"]
        if not Path(device_spec_path).is_file(): raise ValueError(f"Specified path to device spec file is not a file or not found. Received '{device_spec_path}")
        try: import_name = device_spec_path[: device_spec_path.index(".py")]
        except ValueError as e: raise ValueError(f"Provided device spec file was not a Python file! Received '{device_spec_path}") from e
        device_spec_module = importlib.import_module(import_name)
        try: device_name = device_spec_module.DEVICE_NAME
        except AttributeError as e: raise AttributeError("Device spec file did not contain `DEVICE_NAME`") from e
        if "TRANSFORMERS_TEST_DEVICE" in os.environ and torch_device != device_name:
            msg = f"Mismatch between environment variable `TRANSFORMERS_TEST_DEVICE` '{torch_device}' and device found in spec '{device_name}'\n"
            msg += "Either unset `TRANSFORMERS_TEST_DEVICE` or ensure it matches device spec name."
            raise ValueError(msg)
        torch_device = device_name
        def update_mapping_from_spec(device_fn_dict: Dict[str, Callable], attribute_name: str):
            try:
                spec_fn = getattr(device_spec_module, attribute_name)
                device_fn_dict[torch_device] = spec_fn
            except AttributeError as e:
                if "default" not in device_fn_dict: raise AttributeError(f"`{attribute_name}` not found in '{device_spec_path}' and no default fallback function found.") from e
        update_mapping_from_spec(BACKEND_MANUAL_SEED, "MANUAL_SEED_FN")
        update_mapping_from_spec(BACKEND_EMPTY_CACHE, "EMPTY_CACHE_FN")
        update_mapping_from_spec(BACKEND_DEVICE_COUNT, "DEVICE_COUNT_FN")
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
