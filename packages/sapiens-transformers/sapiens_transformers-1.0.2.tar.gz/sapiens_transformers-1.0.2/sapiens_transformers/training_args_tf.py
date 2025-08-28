"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from .utils import cached_property, is_tf_available, logging, requires_backends
from .training_args import TrainingArguments
from dataclasses import dataclass, field
from typing import Optional, Tuple
import warnings
logger = logging.get_logger(__name__)
if is_tf_available():
    import tensorflow as tf
    from .modeling_tf_utils import keras
@dataclass
class TFTrainingArguments(TrainingArguments):
    framework = "tf"
    tpu_name: Optional[str] = field(default=None, metadata={"help": "Name of TPU"})
    tpu_zone: Optional[str] = field(default=None, metadata={"help": "Zone of TPU"})
    gcp_project: Optional[str] = field(default=None, metadata={"help": "Name of Cloud TPU-enabled project"})
    poly_power: float = field(default=1.0, metadata={"help": "Power for the Polynomial decay LR scheduler."})
    xla: bool = field(default=False, metadata={"help": "Whether to activate the XLA compilation or not"})
    @cached_property
    def _setup_strategy(self) -> Tuple["tf.distribute.Strategy", int]:
        requires_backends(self, ["tf"])
        logger.info("Tensorflow: setting up strategy")
        gpus = tf.config.list_physical_devices("GPU")
        if self.fp16: keras.mixed_precision.set_global_policy("mixed_float16")
        if self.no_cuda: strategy = tf.distribute.OneDeviceStrategy(device="/cpu:0")
        else:
            try:
                if self.tpu_name: tpu = tf.distribute.cluster_resolver.TPUClusterResolver(self.tpu_name, zone=self.tpu_zone, project=self.gcp_project)
                else: tpu = tf.distribute.cluster_resolver.TPUClusterResolver()
            except ValueError:
                if self.tpu_name: raise RuntimeError(f"Couldn't connect to TPU {self.tpu_name}!")
                else: tpu = None
            if tpu:
                if self.fp16: keras.mixed_precision.set_global_policy("mixed_bfloat16")
                tf.config.experimental_connect_to_cluster(tpu)
                tf.tpu.experimental.initialize_tpu_system(tpu)
                strategy = tf.distribute.TPUStrategy(tpu)
            elif len(gpus) == 0: strategy = tf.distribute.OneDeviceStrategy(device="/cpu:0")
            elif len(gpus) == 1: strategy = tf.distribute.OneDeviceStrategy(device="/gpu:0")
            elif len(gpus) > 1: strategy = tf.distribute.MirroredStrategy()
            else: raise ValueError("Cannot find the proper strategy, please check your environment properties.")
        return strategy
    @property
    def strategy(self) -> "tf.distribute.Strategy":
        requires_backends(self, ["tf"])
        return self._setup_strategy
    @property
    def n_replicas(self) -> int:
        requires_backends(self, ["tf"])
        return self._setup_strategy.num_replicas_in_sync
    @property
    def should_log(self): return False
    @property
    def train_batch_size(self) -> int:
        if self.per_gpu_train_batch_size: logger.warning("Using deprecated `--per_gpu_train_batch_size` argument which will be removed in a future version. Using `--per_device_train_batch_size` is preferred.")
        per_device_batch_size = self.per_gpu_train_batch_size or self.per_device_train_batch_size
        return per_device_batch_size * self.n_replicas
    @property
    def eval_batch_size(self) -> int:
        if self.per_gpu_eval_batch_size: logger.warning("Using deprecated `--per_gpu_eval_batch_size` argument which will be removed in a future version. Using `--per_device_eval_batch_size` is preferred.")
        per_device_batch_size = self.per_gpu_eval_batch_size or self.per_device_eval_batch_size
        return per_device_batch_size * self.n_replicas
    @property
    def n_gpu(self) -> int:
        requires_backends(self, ["tf"])
        warnings.warn("The n_gpu argument is deprecated and will be removed in a future version, use n_replicas instead.", FutureWarning)
        return self._setup_strategy.num_replicas_in_sync
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
