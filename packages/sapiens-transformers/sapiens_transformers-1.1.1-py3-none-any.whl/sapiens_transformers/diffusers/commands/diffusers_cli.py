'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from .fp16_safetensors import FP16SafetensorsCommand
from argparse import ArgumentParser
from .env import EnvironmentCommand
def main():
    parser = ArgumentParser('Diffusers CLI tool', usage='sapiens_transformers.diffusers-cli <command> [<args>]')
    commands_parser = parser.add_subparsers(help='sapiens_transformers.diffusers-cli command helpers')
    EnvironmentCommand.register_subcommand(commands_parser)
    FP16SafetensorsCommand.register_subcommand(commands_parser)
    args = parser.parse_args()
    if not hasattr(args, 'func'):
        parser.print_help()
        exit(1)
    service = args.func(args)
    service.run()
if __name__ == '__main__': main()
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
