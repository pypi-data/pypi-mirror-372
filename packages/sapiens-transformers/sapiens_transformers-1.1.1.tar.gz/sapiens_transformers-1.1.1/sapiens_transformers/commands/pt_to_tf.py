"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import os
from argparse import ArgumentParser, Namespace
from ..utils import logging
from . import BaseTransformersCLICommand
MAX_ERROR = 5e-5
def convert_command_factory(args: Namespace): return PTtoTFCommand(args.model_name, args.local_dir, args.max_error, args.new_weights, args.no_pr, args.push, args.extra_commit_description, args.override_model_class)
class PTtoTFCommand(BaseTransformersCLICommand):
    @staticmethod
    def register_subcommand(parser: ArgumentParser):
        train_parser = parser.add_parser("pt-to-tf", help=("CLI tool to run convert a transformers model from a PyTorch checkpoint to a TensorFlow checkpoint. Can also be used to validate existing weights without opening PRs, with --no-pr."))
        train_parser.add_argument("--model-name", type=str, required=True, help="The model name, including owner/organization, as seen on the hub.")
        train_parser.add_argument("--local-dir", type=str, default="", help="Optional local directory of the model repository. Defaults to /tmp/{model_name}")
        train_parser.add_argument("--max-error", type=float, default=MAX_ERROR, help=(f"Maximum error tolerance. Defaults to {MAX_ERROR}. This flag should be avoided, use at your own risk."))
        train_parser.add_argument("--new-weights", action="store_true", help="Optional flag to create new TensorFlow weights, even if they already exist.")
        train_parser.add_argument("--no-pr", action="store_true", help="Optional flag to NOT open a PR with converted weights.")
        train_parser.add_argument("--push", action="store_true", help="Optional flag to push the weights directly to `main` (requires permissions)")
        train_parser.add_argument("--extra-commit-description", type=str, default="", help="Optional additional commit description to use when opening a PR (e.g. to tag the owner).")
        train_parser.add_argument("--override-model-class", type=str, default=None, help="If you think you know better than the auto-detector, you can specify the model class here. Can be either an AutoModel class or a specific model class like BertForSequenceClassification.")
        train_parser.set_defaults(func=convert_command_factory)
    def __init__(self, model_name: str, local_dir: str, max_error: float, new_weights: bool, no_pr: bool, push: bool, extra_commit_description: str, override_model_class: str, *args):
        self._logger = logging.get_logger("sapiens_transformers-cli/pt_to_tf")
        self._model_name = model_name
        self._local_dir = local_dir if local_dir else os.path.join("/tmp", model_name)
        self._max_error = max_error
        self._new_weights = new_weights
        self._no_pr = no_pr
        self._push = push
        self._extra_commit_description = extra_commit_description
        self._override_model_class = override_model_class
    def run(self): raise NotImplementedError("\n\nConverting PyTorch weights to TensorFlow weights was removed in v4.43. Instead, we recommend that you convert PyTorch weights to Safetensors, an improved format that can be loaded by any framework, including TensorFlow.\n\n")
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
