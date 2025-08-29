"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from argparse import ArgumentParser, Namespace
from ..utils import logging
from . import BaseTransformersCLICommand
def convert_command_factory(args: Namespace): return ConvertCommand(args.model_type, args.tf_checkpoint, args.pytorch_dump_output, args.config, args.finetuning_task_name)
IMPORT_ERROR_MESSAGE = """
transformers can only be used from the commandline to convert TensorFlow models in PyTorch, In that case, it requires
TensorFlow to be installed. Please see https://www.tensorflow.org/install/ for installation instructions.
"""
class ConvertCommand(BaseTransformersCLICommand):
    @staticmethod
    def register_subcommand(parser: ArgumentParser):
        train_parser = parser.add_parser("convert", help="CLI tool to run convert model from original author checkpoints to Transformers PyTorch checkpoints.")
        train_parser.add_argument("--model_type", type=str, required=True, help="Model's type.")
        train_parser.add_argument("--tf_checkpoint", type=str, required=True, help="TensorFlow checkpoint path or folder.")
        train_parser.add_argument("--pytorch_dump_output", type=str, required=True, help="Path to the PyTorch saved model output.")
        train_parser.add_argument("--config", type=str, default="", help="Configuration file path or folder.")
        train_parser.add_argument("--finetuning_task_name", type=str, default=None, help="Optional fine-tuning task name if the TF model was a finetuned model.")
        train_parser.set_defaults(func=convert_command_factory)
    def __init__(self, model_type: str, tf_checkpoint: str, pytorch_dump_output: str, config: str, finetuning_task_name: str, *args):
        self._logger = logging.get_logger("sapiens_transformers-cli/converting")
        self._logger.info(f"Loading model {model_type}")
        self._model_type = model_type
        self._tf_checkpoint = tf_checkpoint
        self._pytorch_dump_output = pytorch_dump_output
        self._config = config
        self._finetuning_task_name = finetuning_task_name
    def run(self):
        if self._model_type == "albert":
            try: from ..models.albert.convert_albert_original_tf_checkpoint_to_pytorch import (convert_tf_checkpoint_to_pytorch)
            except ImportError: raise ImportError(IMPORT_ERROR_MESSAGE)
            convert_tf_checkpoint_to_pytorch(self._tf_checkpoint, self._config, self._pytorch_dump_output)
        elif self._model_type == "bert":
            try: from ..models.bert.convert_bert_original_tf_checkpoint_to_pytorch import (convert_tf_checkpoint_to_pytorch)
            except ImportError: raise ImportError(IMPORT_ERROR_MESSAGE)
            convert_tf_checkpoint_to_pytorch(self._tf_checkpoint, self._config, self._pytorch_dump_output)
        elif self._model_type == "funnel":
            try: from ..models.funnel.convert_funnel_original_tf_checkpoint_to_pytorch import (convert_tf_checkpoint_to_pytorch)
            except ImportError: raise ImportError(IMPORT_ERROR_MESSAGE)
            convert_tf_checkpoint_to_pytorch(self._tf_checkpoint, self._config, self._pytorch_dump_output)
        elif self._model_type == "t5":
            try: from ..models.t5.convert_t5_original_tf_checkpoint_to_pytorch import convert_tf_checkpoint_to_pytorch
            except ImportError: raise ImportError(IMPORT_ERROR_MESSAGE)
            convert_tf_checkpoint_to_pytorch(self._tf_checkpoint, self._config, self._pytorch_dump_output)
        elif self._model_type == "gpt":
            from ..models.openai.convert_openai_original_tf_checkpoint_to_pytorch import (convert_openai_checkpoint_to_pytorch)
            convert_openai_checkpoint_to_pytorch(self._tf_checkpoint, self._config, self._pytorch_dump_output)
        elif self._model_type == "gpt2":
            try: from ..models.gpt2.convert_gpt2_original_tf_checkpoint_to_pytorch import (convert_gpt2_checkpoint_to_pytorch)
            except ImportError: raise ImportError(IMPORT_ERROR_MESSAGE)
            convert_gpt2_checkpoint_to_pytorch(self._tf_checkpoint, self._config, self._pytorch_dump_output)
        elif self._model_type == "xlnet":
            try: from ..models.xlnet.convert_xlnet_original_tf_checkpoint_to_pytorch import (convert_xlnet_checkpoint_to_pytorch)
            except ImportError: raise ImportError(IMPORT_ERROR_MESSAGE)
            convert_xlnet_checkpoint_to_pytorch(self._tf_checkpoint, self._config, self._pytorch_dump_output, self._finetuning_task_name)
        elif self._model_type == "xlm":
            from ..models.xlm.convert_xlm_original_pytorch_checkpoint_to_pytorch import (convert_xlm_checkpoint_to_pytorch)
            convert_xlm_checkpoint_to_pytorch(self._tf_checkpoint, self._pytorch_dump_output)
        elif self._model_type == "lxmert":
            from ..models.lxmert.convert_lxmert_original_tf_checkpoint_to_pytorch import (convert_lxmert_checkpoint_to_pytorch)
            convert_lxmert_checkpoint_to_pytorch(self._tf_checkpoint, self._pytorch_dump_output)
        elif self._model_type == "rembert":
            from ..models.rembert.convert_rembert_tf_checkpoint_to_pytorch import (convert_rembert_tf_checkpoint_to_pytorch)
            convert_rembert_tf_checkpoint_to_pytorch(self._tf_checkpoint, self._config, self._pytorch_dump_output)
        else: raise ValueError("--model_type should be selected in the list [bert, gpt, gpt2, t5, xlnet, xlm, lxmert]")
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
