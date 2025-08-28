"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import subprocess
from argparse import ArgumentParser
from typing import List, Union
from huggingface_hub.hf_api import HfFolder, create_repo, whoami
from requests.exceptions import HTTPError
from . import BaseTransformersCLICommand
class UserCommands(BaseTransformersCLICommand):
    @staticmethod
    def register_subcommand(parser: ArgumentParser):
        login_parser = parser.add_parser("login", help="Log in.")
        login_parser.set_defaults(func=lambda args: LoginCommand(args))
        whoami_parser = parser.add_parser("whoami", help="Find out which account you are logged in as.")
        whoami_parser.set_defaults(func=lambda args: WhoamiCommand(args))
        logout_parser = parser.add_parser("logout", help="Log out")
        logout_parser.set_defaults(func=lambda args: LogoutCommand(args))
        repo_parser = parser.add_parser("repo", help="Deprecated: use `huggingface-cli` instead.")
        repo_subparsers = repo_parser.add_subparsers(help="Deprecated: use `huggingface-cli` instead.")
        repo_create_parser = repo_subparsers.add_parser("create", help="Deprecated: use `huggingface-cli` instead.")
        repo_create_parser.add_argument("name", type=str, help="Name for your model's repo. Will be namespaced under your username to build the model id.")
        repo_create_parser.add_argument("--organization", type=str, help="Optional: organization namespace.")
        repo_create_parser.add_argument("-y", "--yes", action="store_true", help="Optional: answer Yes to the prompt")
        repo_create_parser.set_defaults(func=lambda args: RepoCreateCommand(args))
class ANSI:
    _bold = "\u001b[1m"
    _red = "\u001b[31m"
    _gray = "\u001b[90m"
    _reset = "\u001b[0m"
    @classmethod
    def bold(cls, s): return f"{cls._bold}{s}{cls._reset}"
    @classmethod
    def red(cls, s): return f"{cls._bold}{cls._red}{s}{cls._reset}"
    @classmethod
    def gray(cls, s): return f"{cls._gray}{s}{cls._reset}"
def tabulate(rows: List[List[Union[str, int]]], headers: List[str]) -> str:
    col_widths = [max(len(str(x)) for x in col) for col in zip(*rows, headers)]
    row_format = ("{{:{}}} " * len(headers)).format(*col_widths)
    lines = []
    lines.append(row_format.format(*headers))
    lines.append(row_format.format(*["-" * w for w in col_widths]))
    for row in rows: lines.append(row_format.format(*row))
    return "\n".join(lines)
class BaseUserCommand:
    def __init__(self, args): self.args = args
class LoginCommand(BaseUserCommand):
    def run(self): print(ANSI.red("ERROR! `huggingface-cli login` uses an outdated login mechanism that is not compatible with the Sapiens Hub backend anymore. Please use `huggingface-cli login instead."))
class WhoamiCommand(BaseUserCommand):
    def run(self):
        print(ANSI.red("WARNING! `transformers-cli whoami` is deprecated and will be removed in v5. Please use `huggingface-cli whoami` instead."))
        token = HfFolder.get_token()
        if token is None:
            print("Not logged in")
            exit()
        try:
            user, orgs = whoami(token)
            print(user)
            if orgs: print(ANSI.bold("orgs: "), ",".join(orgs))
        except HTTPError as e:
            print(e)
            print(ANSI.red(e.response.text))
            exit(1)
class LogoutCommand(BaseUserCommand):
    def run(self): print(ANSI.red("ERROR! `transformers-cli logout` uses an outdated logout mechanism that is not compatible with the Sapiens Hub backend anymore. Please use `huggingface-cli logout instead."))
class RepoCreateCommand(BaseUserCommand):
    def run(self):
        print(ANSI.red("WARNING! Managing repositories through transformers-cli is deprecated. Please use `huggingface-cli` instead."))
        token = HfFolder.get_token()
        if token is None:
            print("Not logged in")
            exit(1)
        try:
            stdout = subprocess.check_output(["git", "--version"]).decode("utf-8")
            print(ANSI.gray(stdout.strip()))
        except FileNotFoundError: print("Looks like you do not have git installed, please install.")
        try:
            stdout = subprocess.check_output(["git-lfs", "--version"]).decode("utf-8")
            print(ANSI.gray(stdout.strip()))
        except FileNotFoundError: print(ANSI.red("Looks like you do not have git-lfs installed, please install. You can install from https://git-lfs.github.com/. Then run `git lfs install` (you only have to do this once)."))
        print("")
        user, _ = whoami(token)
        namespace = self.args.organization if self.args.organization is not None else user
        full_name = f"{namespace}/{self.args.name}"
        print(f"You are about to create {ANSI.bold(full_name)}")
        if not self.args.yes:
            choice = input("Proceed? [Y/n] ").lower()
            if not (choice == "" or choice == "y" or choice == "yes"):
                print("Abort")
                exit()
        try: url = create_repo(repo_id=full_name, token=token)
        except HTTPError as e:
            print(e)
            print(ANSI.red(e.response.text))
            exit(1)
        print("\nYour repo now lives at:")
        print(f"  {ANSI.bold(url)}")
        print("\nYou can clone it locally with the command below, and commit/push as usual.")
        print(f"\n  git clone {url}")
        print("")
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
