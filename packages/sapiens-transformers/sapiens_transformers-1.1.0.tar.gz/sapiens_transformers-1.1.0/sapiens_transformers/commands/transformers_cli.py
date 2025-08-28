"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from argparse import ArgumentParser
from .add_new_model_like import AddNewModelLikeCommand
from .convert import ConvertCommand
from .download import DownloadCommand
from .env import EnvironmentCommand
from .lfs import LfsCommands
from .pt_to_tf import PTtoTFCommand
from .run import RunCommand
from .serving import ServeCommand
from .user import UserCommands
def main():
    parser = ArgumentParser("Transformers CLI tool", usage="sapiens_transformers-cli <command> [<args>]")
    commands_parser = parser.add_subparsers(help="sapiens_transformers-cli command helpers")
    ConvertCommand.register_subcommand(commands_parser)
    DownloadCommand.register_subcommand(commands_parser)
    EnvironmentCommand.register_subcommand(commands_parser)
    RunCommand.register_subcommand(commands_parser)
    ServeCommand.register_subcommand(commands_parser)
    UserCommands.register_subcommand(commands_parser)
    AddNewModelLikeCommand.register_subcommand(commands_parser)
    LfsCommands.register_subcommand(commands_parser)
    PTtoTFCommand.register_subcommand(commands_parser)
    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        exit(1)
    service = args.func(args)
    service.run()
if __name__ == "__main__": main()
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
