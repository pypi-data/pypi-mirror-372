'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from argparse import ArgumentParser, Namespace
from huggingface_hub import hf_hub_download
from . import BaseDiffusersCLICommand
from importlib import import_module
from packaging import version
import huggingface_hub
import torch
import glob
import json
def conversion_command_factory(args: Namespace): return FP16SafetensorsCommand(args.ckpt_id, args.fp16, args.use_safetensors)
class FP16SafetensorsCommand(BaseDiffusersCLICommand):
    @staticmethod
    def register_subcommand(parser: ArgumentParser):
        conversion_parser = parser.add_parser('fp16_safetensors')
        conversion_parser.add_argument('--ckpt_id', type=str, help="Repo id of the checkpoints on which to run the conversion. Example: 'openai/shap-e'.")
        conversion_parser.add_argument('--fp16', action='store_true', help='If serializing the variables in FP16 precision.')
        conversion_parser.add_argument('--use_safetensors', action='store_true', help='If serializing in the safetensors format.')
        conversion_parser.add_argument('--use_auth_token', action='store_true', help='When working with checkpoints having private visibility. When used `huggingface-cli login` needs to be run beforehand.')
        conversion_parser.set_defaults(func=conversion_command_factory)
    def __init__(self, ckpt_id: str, fp16: bool, use_safetensors: bool):
        self.ckpt_id = ckpt_id
        self.local_ckpt_dir = f'/tmp/{ckpt_id}'
        self.fp16 = fp16
        self.use_safetensors = use_safetensors
        if not self.use_safetensors and (not self.fp16): raise NotImplementedError('When `use_safetensors` and `fp16` both are False, then this command is of no use.')
    def run(self):
        if version.parse(huggingface_hub.__version__) < version.parse('0.9.0'): raise ImportError('The huggingface_hub version must be >= 0.9.0 to use this command. Please update your huggingface_hub installation.')
        else:
            from huggingface_hub import create_commit
            from huggingface_hub._commit_api import CommitOperationAdd
        model_index = hf_hub_download(repo_id=self.ckpt_id, filename='model_index.json')
        with open(model_index, 'r') as f: pipeline_class_name = json.load(f)['_class_name']
        pipeline_class = getattr(import_module('sapiens_transformers.diffusers'), pipeline_class_name)
        pipeline = pipeline_class.from_pretrained(self.ckpt_id, torch_dtype=torch.float16 if self.fp16 else torch.float32)
        pipeline.save_pretrained(self.local_ckpt_dir, safe_serialization=True if self.use_safetensors else False, variant='fp16' if self.fp16 else None)
        if self.fp16: modified_paths = glob.glob(f'{self.local_ckpt_dir}/*/*.fp16.*')
        elif self.use_safetensors: modified_paths = glob.glob(f'{self.local_ckpt_dir}/*/*.safetensors')
        commit_message = f'Serialize variables with FP16: {self.fp16} and safetensors: {self.use_safetensors}.'
        operations = []
        for path in modified_paths: operations.append(CommitOperationAdd(path_in_repo='/'.join(path.split('/')[4:]), path_or_fileobj=path))
        commit_description = "Variables converted by the [`diffusers`' `fp16_safetensors` CLI](https://github.com/huggingface/diffusers/blob/main/src/diffusers/commands/fp16_safetensors.py)."
        hub_pr_url = create_commit(repo_id=self.ckpt_id, operations=operations, commit_message=commit_message, commit_description=commit_description, repo_type='model', create_pr=True).pr_url
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
