"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from argparse import ArgumentParser
from . import BaseTransformersCLICommand
def download_command_factory(args): return DownloadCommand(args.model, args.cache_dir, args.force, args.trust_remote_code)
class DownloadCommand(BaseTransformersCLICommand):
    @staticmethod
    def register_subcommand(parser: ArgumentParser):
        download_parser = parser.add_parser("download")
        download_parser.add_argument("--cache-dir", type=str, default=None, help="Path to location to store the models")
        download_parser.add_argument("--force", action="store_true", help="Force the model to be download even if already in cache-dir")
        download_parser.add_argument("--trust-remote-code", action="store_true", help="Whether or not to allow for custom models defined on the Hub in their own modeling files. Use only if you've reviewed the code as it will execute on your local machine")
        download_parser.add_argument("model", type=str, help="Name of the model to download")
        download_parser.set_defaults(func=download_command_factory)
    def __init__(self, model: str, cache: str, force: bool, trust_remote_code: bool):
        self._model = model
        self._cache = cache
        self._force = force
        self._trust_remote_code = trust_remote_code
    def run(self):
        from ..models.auto import AutoModel, AutoTokenizer
        AutoModel.from_pretrained(self._model, cache_dir=self._cache, force_download=self._force, trust_remote_code=self._trust_remote_code)
        AutoTokenizer.from_pretrained(self._model, cache_dir=self._cache, force_download=self._force, trust_remote_code=self._trust_remote_code)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
