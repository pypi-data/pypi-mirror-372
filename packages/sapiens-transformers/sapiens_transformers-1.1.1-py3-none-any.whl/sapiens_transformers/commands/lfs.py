"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import json
import os
import subprocess
import sys
import warnings
from argparse import ArgumentParser
from contextlib import AbstractContextManager
from typing import Dict, List, Optional
import requests
from ..utils import logging
from . import BaseTransformersCLICommand
logger = logging.get_logger(__name__)
LFS_MULTIPART_UPLOAD_COMMAND = "lfs-multipart-upload"
class LfsCommands(BaseTransformersCLICommand):
    @staticmethod
    def register_subcommand(parser: ArgumentParser):
        enable_parser = parser.add_parser("lfs-enable-largefiles", help=("Deprecated: use `huggingface-cli` instead. Configure your repository to enable upload of files > 5GB."))
        enable_parser.add_argument("path", type=str, help="Local path to repository you want to configure.")
        enable_parser.set_defaults(func=lambda args: LfsEnableCommand(args))
        upload_parser = parser.add_parser(LFS_MULTIPART_UPLOAD_COMMAND, help=("Deprecated: use `huggingface-cli` instead. Command will get called by git-lfs, do not call it directly."))
        upload_parser.set_defaults(func=lambda args: LfsUploadCommand(args))
class LfsEnableCommand:
    def __init__(self, args): self.args = args
    def run(self):
        warnings.warn("Managing repositories through transformers-cli is deprecated. Please use `huggingface-cli` instead.")
        local_path = os.path.abspath(self.args.path)
        if not os.path.isdir(local_path):
            print("This does not look like a valid git repo.")
            exit(1)
        subprocess.run("git config lfs.customtransfer.multipart.path transformers-cli".split(), check=True, cwd=local_path)
        subprocess.run(f"git config lfs.customtransfer.multipart.args {LFS_MULTIPART_UPLOAD_COMMAND}".split(), check=True, cwd=local_path)
        print("Local repo set up for largefiles")
def write_msg(msg: Dict):
    msg = json.dumps(msg) + "\n"
    sys.stdout.write(msg)
    sys.stdout.flush()
def read_msg() -> Optional[Dict]:
    msg = json.loads(sys.stdin.readline().strip())
    if "terminate" in (msg.get("type"), msg.get("event")): return None
    if msg.get("event") not in ("download", "upload"):
        logger.critical("Received unexpected message")
        sys.exit(1)
    return msg
class FileSlice(AbstractContextManager):
    def __init__(self, filepath: str, seek_from: int, read_limit: int):
        self.filepath = filepath
        self.seek_from = seek_from
        self.read_limit = read_limit
        self.n_seen = 0
    def __enter__(self):
        self.f = open(self.filepath, "rb")
        self.f.seek(self.seek_from)
        return self
    def __len__(self):
        total_length = os.fstat(self.f.fileno()).st_size
        return min(self.read_limit, total_length - self.seek_from)
    def read(self, n=-1):
        if self.n_seen >= self.read_limit: return b""
        remaining_amount = self.read_limit - self.n_seen
        data = self.f.read(remaining_amount if n < 0 else min(n, remaining_amount))
        self.n_seen += len(data)
        return data
    def __iter__(self): yield self.read(n=4 * 1024 * 1024)
    def __exit__(self, *args): self.f.close()
class LfsUploadCommand:
    def __init__(self, args): self.args = args
    def run(self):
        init_msg = json.loads(sys.stdin.readline().strip())
        if not (init_msg.get("event") == "init" and init_msg.get("operation") == "upload"):
            write_msg({"error": {"code": 32, "message": "Wrong lfs init operation"}})
            sys.exit(1)
        write_msg({})
        while True:
            msg = read_msg()
            if msg is None: sys.exit(0)
            oid = msg["oid"]
            filepath = msg["path"]
            completion_url = msg["action"]["href"]
            header = msg["action"]["header"]
            chunk_size = int(header.pop("chunk_size"))
            presigned_urls: List[str] = list(header.values())
            parts = []
            for i, presigned_url in enumerate(presigned_urls):
                with FileSlice(filepath, seek_from=i * chunk_size, read_limit=chunk_size) as data:
                    r = requests.put(presigned_url, data=data)
                    r.raise_for_status()
                    parts.append({"etag": r.headers.get("etag"), "partNumber": i + 1})
                    write_msg({"event": "progress", "oid": oid, "bytesSoFar": (i + 1) * chunk_size, "bytesSinceLast": chunk_size})
            r = requests.post(completion_url, json={"oid": oid, "parts": parts})
            r.raise_for_status()
            write_msg({"event": "complete", "oid": oid})
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
