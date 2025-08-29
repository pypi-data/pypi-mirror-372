"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import os
import warnings
from dataclasses import asdict
from enum import Enum
from typing import List, Optional, Union
from ...tokenization_utils import PreTrainedTokenizer
from ...utils import is_tf_available, logging
from .utils import DataProcessor, InputExample, InputFeatures
if is_tf_available(): import tensorflow as tf
logger = logging.get_logger(__name__)
DEPRECATION_WARNING = ("This {0} will be removed from the library soon, preprocessing should be handled with the HF Datasets library.")
def glue_convert_examples_to_features(examples: Union[List[InputExample], "tf.data.Dataset"], tokenizer: PreTrainedTokenizer, max_length: Optional[int] = None, task=None, label_list=None, output_mode=None):
    warnings.warn(DEPRECATION_WARNING.format("function"), FutureWarning)
    if is_tf_available() and isinstance(examples, tf.data.Dataset):
        if task is None: raise ValueError("When calling glue_convert_examples_to_features from TF, the task parameter is required.")
        return _tf_glue_convert_examples_to_features(examples, tokenizer, max_length=max_length, task=task)
    return _glue_convert_examples_to_features(examples, tokenizer, max_length=max_length, task=task, label_list=label_list, output_mode=output_mode)
if is_tf_available():
    def _tf_glue_convert_examples_to_features(examples: tf.data.Dataset, tokenizer: PreTrainedTokenizer, task=str, max_length: Optional[int] = None) -> tf.data.Dataset:
        processor = glue_processors[task]()
        examples = [processor.tfds_map(processor.get_example_from_tensor_dict(example)) for example in examples]
        features = glue_convert_examples_to_features(examples, tokenizer, max_length=max_length, task=task)
        label_type = tf.float32 if task == "sts-b" else tf.int64
        def gen():
            for ex in features:
                d = {k: v for k, v in asdict(ex).items() if v is not None}
                label = d.pop("label")
                yield (d, label)
        input_names = tokenizer.model_input_names
        return tf.data.Dataset.from_generator(gen, ({k: tf.int32 for k in input_names}, label_type), ({k: tf.TensorShape([None]) for k in input_names}, tf.TensorShape([])))
def _glue_convert_examples_to_features(examples: List[InputExample], tokenizer: PreTrainedTokenizer, max_length: Optional[int] = None, task=None, label_list=None, output_mode=None):
    if max_length is None: max_length = tokenizer.model_max_length
    if task is not None:
        processor = glue_processors[task]()
        if label_list is None:
            label_list = processor.get_labels()
            logger.info(f"Using label list {label_list} for task {task}")
        if output_mode is None:
            output_mode = glue_output_modes[task]
            logger.info(f"Using output mode {output_mode} for task {task}")
    label_map = {label: i for i, label in enumerate(label_list)}
    def label_from_example(example: InputExample) -> Union[int, float, None]:
        if example.label is None: return None
        if output_mode == "classification": return label_map[example.label]
        elif output_mode == "regression": return float(example.label)
        raise KeyError(output_mode)
    labels = [label_from_example(example) for example in examples]
    batch_encoding = tokenizer([(example.text_a, example.text_b) for example in examples], max_length=max_length, padding="max_length", truncation=True)
    features = []
    for i in range(len(examples)):
        inputs = {k: batch_encoding[k][i] for k in batch_encoding}
        feature = InputFeatures(**inputs, label=labels[i])
        features.append(feature)
    for i, example in enumerate(examples[:5]):
        logger.info("*** Example ***")
        logger.info(f"guid: {example.guid}")
        logger.info(f"features: {features[i]}")
    return features
class OutputMode(Enum):
    classification = "classification"
    regression = "regression"
class MrpcProcessor(DataProcessor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        warnings.warn(DEPRECATION_WARNING.format("processor"), FutureWarning)
    def get_example_from_tensor_dict(self, tensor_dict): return InputExample(tensor_dict["idx"].numpy(), tensor_dict["sentence1"].numpy().decode("utf-8"), tensor_dict["sentence2"].numpy().decode("utf-8"), str(tensor_dict["label"].numpy()))
    def get_train_examples(self, data_dir):
        logger.info(f"LOOKING AT {os.path.join(data_dir, 'train.tsv')}")
        return self._create_examples(self._read_tsv(os.path.join(data_dir, "train.tsv")), "train")
    def get_dev_examples(self, data_dir): return self._create_examples(self._read_tsv(os.path.join(data_dir, "dev.tsv")), "dev")
    def get_test_examples(self, data_dir): return self._create_examples(self._read_tsv(os.path.join(data_dir, "test.tsv")), "test")
    def get_labels(self): return ["0", "1"]
    def _create_examples(self, lines, set_type):
        examples = []
        for i, line in enumerate(lines):
            if i == 0: continue
            guid = f"{set_type}-{i}"
            text_a = line[3]
            text_b = line[4]
            label = None if set_type == "test" else line[0]
            examples.append(InputExample(guid=guid, text_a=text_a, text_b=text_b, label=label))
        return examples
class MnliProcessor(DataProcessor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        warnings.warn(DEPRECATION_WARNING.format("processor"), FutureWarning)
    def get_example_from_tensor_dict(self, tensor_dict): return InputExample(tensor_dict["idx"].numpy(), tensor_dict["premise"].numpy().decode("utf-8"), tensor_dict["hypothesis"].numpy().decode("utf-8"), str(tensor_dict["label"].numpy()))
    def get_train_examples(self, data_dir): return self._create_examples(self._read_tsv(os.path.join(data_dir, "train.tsv")), "train")
    def get_dev_examples(self, data_dir): return self._create_examples(self._read_tsv(os.path.join(data_dir, "dev_matched.tsv")), "dev_matched")
    def get_test_examples(self, data_dir): return self._create_examples(self._read_tsv(os.path.join(data_dir, "test_matched.tsv")), "test_matched")
    def get_labels(self): return ["contradiction", "entailment", "neutral"]
    def _create_examples(self, lines, set_type):
        examples = []
        for i, line in enumerate(lines):
            if i == 0: continue
            guid = f"{set_type}-{line[0]}"
            text_a = line[8]
            text_b = line[9]
            label = None if set_type.startswith("test") else line[-1]
            examples.append(InputExample(guid=guid, text_a=text_a, text_b=text_b, label=label))
        return examples
class MnliMismatchedProcessor(MnliProcessor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        warnings.warn(DEPRECATION_WARNING.format("processor"), FutureWarning)
    def get_dev_examples(self, data_dir): return self._create_examples(self._read_tsv(os.path.join(data_dir, "dev_mismatched.tsv")), "dev_mismatched")
    def get_test_examples(self, data_dir): return self._create_examples(self._read_tsv(os.path.join(data_dir, "test_mismatched.tsv")), "test_mismatched")
class ColaProcessor(DataProcessor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        warnings.warn(DEPRECATION_WARNING.format("processor"), FutureWarning)
    def get_example_from_tensor_dict(self, tensor_dict): return InputExample(tensor_dict["idx"].numpy(), tensor_dict["sentence"].numpy().decode("utf-8"), None, str(tensor_dict["label"].numpy()))
    def get_train_examples(self, data_dir): return self._create_examples(self._read_tsv(os.path.join(data_dir, "train.tsv")), "train")
    def get_dev_examples(self, data_dir): return self._create_examples(self._read_tsv(os.path.join(data_dir, "dev.tsv")), "dev")
    def get_test_examples(self, data_dir): return self._create_examples(self._read_tsv(os.path.join(data_dir, "test.tsv")), "test")
    def get_labels(self): return ["0", "1"]
    def _create_examples(self, lines, set_type):
        test_mode = set_type == "test"
        if test_mode: lines = lines[1:]
        text_index = 1 if test_mode else 3
        examples = []
        for i, line in enumerate(lines):
            guid = f"{set_type}-{i}"
            text_a = line[text_index]
            label = None if test_mode else line[1]
            examples.append(InputExample(guid=guid, text_a=text_a, text_b=None, label=label))
        return examples
class Sst2Processor(DataProcessor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        warnings.warn(DEPRECATION_WARNING.format("processor"), FutureWarning)
    def get_example_from_tensor_dict(self, tensor_dict): return InputExample(tensor_dict["idx"].numpy(), tensor_dict["sentence"].numpy().decode("utf-8"), None, str(tensor_dict["label"].numpy()))
    def get_train_examples(self, data_dir): return self._create_examples(self._read_tsv(os.path.join(data_dir, "train.tsv")), "train")
    def get_dev_examples(self, data_dir): return self._create_examples(self._read_tsv(os.path.join(data_dir, "dev.tsv")), "dev")
    def get_test_examples(self, data_dir): return self._create_examples(self._read_tsv(os.path.join(data_dir, "test.tsv")), "test")
    def get_labels(self): return ["0", "1"]
    def _create_examples(self, lines, set_type):
        examples = []
        text_index = 1 if set_type == "test" else 0
        for i, line in enumerate(lines):
            if i == 0: continue
            guid = f"{set_type}-{i}"
            text_a = line[text_index]
            label = None if set_type == "test" else line[1]
            examples.append(InputExample(guid=guid, text_a=text_a, text_b=None, label=label))
        return examples
class StsbProcessor(DataProcessor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        warnings.warn(DEPRECATION_WARNING.format("processor"), FutureWarning)
    def get_example_from_tensor_dict(self, tensor_dict): return InputExample(tensor_dict["idx"].numpy(), tensor_dict["sentence1"].numpy().decode("utf-8"), tensor_dict["sentence2"].numpy().decode("utf-8"), str(tensor_dict["label"].numpy()))
    def get_train_examples(self, data_dir): return self._create_examples(self._read_tsv(os.path.join(data_dir, "train.tsv")), "train")
    def get_dev_examples(self, data_dir): return self._create_examples(self._read_tsv(os.path.join(data_dir, "dev.tsv")), "dev")
    def get_test_examples(self, data_dir): return self._create_examples(self._read_tsv(os.path.join(data_dir, "test.tsv")), "test")
    def get_labels(self): return [None]
    def _create_examples(self, lines, set_type):
        examples = []
        for i, line in enumerate(lines):
            if i == 0: continue
            guid = f"{set_type}-{line[0]}"
            text_a = line[7]
            text_b = line[8]
            label = None if set_type == "test" else line[-1]
            examples.append(InputExample(guid=guid, text_a=text_a, text_b=text_b, label=label))
        return examples
class QqpProcessor(DataProcessor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        warnings.warn(DEPRECATION_WARNING.format("processor"), FutureWarning)
    def get_example_from_tensor_dict(self, tensor_dict): return InputExample(tensor_dict["idx"].numpy(), tensor_dict["question1"].numpy().decode("utf-8"), tensor_dict["question2"].numpy().decode("utf-8"), str(tensor_dict["label"].numpy()))
    def get_train_examples(self, data_dir): return self._create_examples(self._read_tsv(os.path.join(data_dir, "train.tsv")), "train")
    def get_dev_examples(self, data_dir): return self._create_examples(self._read_tsv(os.path.join(data_dir, "dev.tsv")), "dev")
    def get_test_examples(self, data_dir): return self._create_examples(self._read_tsv(os.path.join(data_dir, "test.tsv")), "test")
    def get_labels(self): return ["0", "1"]
    def _create_examples(self, lines, set_type):
        test_mode = set_type == "test"
        q1_index = 1 if test_mode else 3
        q2_index = 2 if test_mode else 4
        examples = []
        for i, line in enumerate(lines):
            if i == 0: continue
            guid = f"{set_type}-{line[0]}"
            try:
                text_a = line[q1_index]
                text_b = line[q2_index]
                label = None if test_mode else line[5]
            except IndexError: continue
            examples.append(InputExample(guid=guid, text_a=text_a, text_b=text_b, label=label))
        return examples
class QnliProcessor(DataProcessor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        warnings.warn(DEPRECATION_WARNING.format("processor"), FutureWarning)
    def get_example_from_tensor_dict(self, tensor_dict): return InputExample(tensor_dict["idx"].numpy(), tensor_dict["question"].numpy().decode("utf-8"), tensor_dict["sentence"].numpy().decode("utf-8"), str(tensor_dict["label"].numpy()))
    def get_train_examples(self, data_dir): return self._create_examples(self._read_tsv(os.path.join(data_dir, "train.tsv")), "train")
    def get_dev_examples(self, data_dir): return self._create_examples(self._read_tsv(os.path.join(data_dir, "dev.tsv")), "dev")
    def get_test_examples(self, data_dir): return self._create_examples(self._read_tsv(os.path.join(data_dir, "test.tsv")), "test")
    def get_labels(self): return ["entailment", "not_entailment"]
    def _create_examples(self, lines, set_type):
        examples = []
        for i, line in enumerate(lines):
            if i == 0: continue
            guid = f"{set_type}-{line[0]}"
            text_a = line[1]
            text_b = line[2]
            label = None if set_type == "test" else line[-1]
            examples.append(InputExample(guid=guid, text_a=text_a, text_b=text_b, label=label))
        return examples
class RteProcessor(DataProcessor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        warnings.warn(DEPRECATION_WARNING.format("processor"), FutureWarning)
    def get_example_from_tensor_dict(self, tensor_dict): return InputExample(tensor_dict["idx"].numpy(), tensor_dict["sentence1"].numpy().decode("utf-8"), tensor_dict["sentence2"].numpy().decode("utf-8"), str(tensor_dict["label"].numpy()))
    def get_train_examples(self, data_dir): return self._create_examples(self._read_tsv(os.path.join(data_dir, "train.tsv")), "train")
    def get_dev_examples(self, data_dir): return self._create_examples(self._read_tsv(os.path.join(data_dir, "dev.tsv")), "dev")
    def get_test_examples(self, data_dir): return self._create_examples(self._read_tsv(os.path.join(data_dir, "test.tsv")), "test")
    def get_labels(self): return ["entailment", "not_entailment"]
    def _create_examples(self, lines, set_type):
        examples = []
        for i, line in enumerate(lines):
            if i == 0: continue
            guid = f"{set_type}-{line[0]}"
            text_a = line[1]
            text_b = line[2]
            label = None if set_type == "test" else line[-1]
            examples.append(InputExample(guid=guid, text_a=text_a, text_b=text_b, label=label))
        return examples
class WnliProcessor(DataProcessor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        warnings.warn(DEPRECATION_WARNING.format("processor"), FutureWarning)
    def get_example_from_tensor_dict(self, tensor_dict): return InputExample(tensor_dict["idx"].numpy(), tensor_dict["sentence1"].numpy().decode("utf-8"), tensor_dict["sentence2"].numpy().decode("utf-8"), str(tensor_dict["label"].numpy()))
    def get_train_examples(self, data_dir): return self._create_examples(self._read_tsv(os.path.join(data_dir, "train.tsv")), "train")
    def get_dev_examples(self, data_dir): return self._create_examples(self._read_tsv(os.path.join(data_dir, "dev.tsv")), "dev")
    def get_test_examples(self, data_dir): return self._create_examples(self._read_tsv(os.path.join(data_dir, "test.tsv")), "test")
    def get_labels(self): return ["0", "1"]
    def _create_examples(self, lines, set_type):
        examples = []
        for i, line in enumerate(lines):
            if i == 0: continue
            guid = f"{set_type}-{line[0]}"
            text_a = line[1]
            text_b = line[2]
            label = None if set_type == "test" else line[-1]
            examples.append(InputExample(guid=guid, text_a=text_a, text_b=text_b, label=label))
        return examples
glue_tasks_num_labels = {"cola": 2, "mnli": 3, "mrpc": 2, "sst-2": 2, "sts-b": 1, "qqp": 2, "qnli": 2, "rte": 2, "wnli": 2}
glue_processors = {"cola": ColaProcessor, "mnli": MnliProcessor, "mnli-mm": MnliMismatchedProcessor, "mrpc": MrpcProcessor, "sst-2": Sst2Processor, "sts-b": StsbProcessor, "qqp": QqpProcessor, "qnli": QnliProcessor, "rte": RteProcessor, "wnli": WnliProcessor}
glue_output_modes = {"cola": "classification", "mnli": "classification", "mnli-mm": "classification", "mrpc": "classification", "sst-2": "classification", "sts-b": "regression", "qqp": "classification", "qnli": "classification", "rte": "classification", "wnli": "classification"}
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
