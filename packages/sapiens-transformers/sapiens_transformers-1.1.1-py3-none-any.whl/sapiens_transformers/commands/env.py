"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import importlib.util
import os
import platform
from argparse import ArgumentParser
import huggingface_hub
from .. import __version__ as version
from ..utils import (is_sapiens_accelerator_available, is_flax_available, is_safetensors_available, is_tf_available, is_torch_available, is_torch_npu_available)
from . import BaseTransformersCLICommand
def info_command_factory(_): return EnvironmentCommand()
def download_command_factory(args): return EnvironmentCommand(args.sapiens_accelerator_config_file)
class EnvironmentCommand(BaseTransformersCLICommand):
    @staticmethod
    def register_subcommand(parser: ArgumentParser):
        download_parser = parser.add_parser("env")
        download_parser.set_defaults(func=info_command_factory)
        download_parser.add_argument("--sapiens_accelerator-config_file", default=None, help="The sapiens_accelerator config file to use for the default values in the launching script.")
        download_parser.set_defaults(func=download_command_factory)
    def __init__(self, sapiens_accelerator_config_file, *args) -> None: self._sapiens_accelerator_config_file = sapiens_accelerator_config_file
    def run(self):
        safetensors_version = "not installed"
        if is_safetensors_available():
            import safetensors
            safetensors_version = safetensors.__version__
        elif importlib.util.find_spec("safetensors") is not None:
            import safetensors
            safetensors_version = f"{safetensors.__version__} but is ignored because of PyTorch version too old."
        sapiens_accelerator_version = "not installed"
        sapiens_accelerator_config = sapiens_accelerator_config_str = "not found"
        if is_sapiens_accelerator_available():
            import sapiens_accelerator
            from sapiens_accelerator.commands.config import default_config_file, load_config_from_file
            sapiens_accelerator_version = sapiens_accelerator.__version__
            if self._sapiens_accelerator_config_file is not None or os.path.isfile(default_config_file): sapiens_accelerator_config = load_config_from_file(self._sapiens_accelerator_config_file).to_dict()
            sapiens_accelerator_config_str = ("\n".join([f"\t- {prop}: {val}" for prop, val in sapiens_accelerator_config.items()]) if isinstance(sapiens_accelerator_config, dict) else f"\t{sapiens_accelerator_config}")
        pt_version = "not installed"
        pt_cuda_available = "NA"
        if is_torch_available():
            import torch
            pt_version = torch.__version__
            pt_cuda_available = torch.cuda.is_available()
            pt_npu_available = is_torch_npu_available()
        tf_version = "not installed"
        tf_cuda_available = "NA"
        if is_tf_available():
            import tensorflow as tf
            tf_version = tf.__version__
            try: tf_cuda_available = tf.test.is_gpu_available()
            except AttributeError: tf_cuda_available = bool(tf.config.list_physical_devices("GPU"))
        flax_version = "not installed"
        jax_version = "not installed"
        jaxlib_version = "not installed"
        jax_backend = "NA"
        if is_flax_available():
            import flax
            import jax
            import jaxlib
            flax_version = flax.__version__
            jax_version = jax.__version__
            jaxlib_version = jaxlib.__version__
            jax_backend = jax.lib.xla_bridge.get_backend().platform
        info = {"`transformers` version": version, "Platform": platform.platform(), "Python version": platform.python_version(), "Huggingface_hub version": huggingface_hub.__version__,
        "Safetensors version": f"{safetensors_version}", "SapiensAccelerator version": f"{sapiens_accelerator_version}", "SapiensAccelerator config": f"{sapiens_accelerator_config_str}", "PyTorch version (GPU?)": f"{pt_version} ({pt_cuda_available})",
        "Tensorflow version (GPU?)": f"{tf_version} ({tf_cuda_available})", "Flax version (CPU?/GPU?/TPU?)": f"{flax_version} ({jax_backend})", "Jax version": f"{jax_version}", "JaxLib version": f"{jaxlib_version}",
        "Using distributed or parallel set-up in script?": "<fill in>"}
        if is_torch_available():
            if pt_cuda_available:
                info["Using GPU in script?"] = "<fill in>"
                info["GPU type"] = torch.cuda.get_device_name()
            elif pt_npu_available:
                info["Using NPU in script?"] = "<fill in>"
                info["NPU type"] = torch.npu.get_device_name()
                info["CANN version"] = torch.version.cann
        print("\nCopy-and-paste the text below in your GitHub issue and FILL OUT the two last points.\n")
        print(self.format_dict(info))
        return info
    @staticmethod
    def format_dict(d): return "\n".join([f"- {prop}: {val}" for prop, val in d.items()]) + "\n"
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
