"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from sapiens_transformers.utils import ModelOutput, is_tf_available, is_torch_available
from sapiens_transformers.tokenization_utils import BatchEncoding
from sapiens_transformers.pipelines import Pipeline, pipeline
from typing import Dict, List, Optional, Tuple
from packaging.version import Version, parse
from argparse import ArgumentParser
from os import listdir, makedirs
from pathlib import Path
import warnings
ORT_QUANTIZE_MINIMUM_VERSION = parse("1.4.0")
SUPPORTED_PIPELINES = ["feature-extraction", "ner", "sentiment-analysis", "fill-mask", "question-answering", "text-generation", "translation_en_to_fr", "translation_en_to_de", "translation_en_to_ro"]
class OnnxConverterArgumentParser(ArgumentParser):
    def __init__(self):
        super().__init__("ONNX Converter")
        self.add_argument("--pipeline", type=str, choices=SUPPORTED_PIPELINES, default="feature-extraction")
        self.add_argument("--model", type=str, required=True, help="Model's id or path (ex: google-bert/bert-base-cased)")
        self.add_argument("--tokenizer", type=str, help="Tokenizer's id or path (ex: google-bert/bert-base-cased)")
        self.add_argument("--framework", type=str, choices=["pt", "tf"], help="Framework for loading the model")
        self.add_argument("--opset", type=int, default=11, help="ONNX opset to use")
        self.add_argument("--check-loading", action="store_true", help="Check ONNX is able to load the model")
        self.add_argument("--use-external-format", action="store_true", help="Allow exporting model >= than 2Gb")
        self.add_argument("--quantize", action="store_true", help="Quantize the neural network to be run with int8")
        self.add_argument("output")
def generate_identified_filename(filename: Path, identifier: str) -> Path: return filename.parent.joinpath(filename.stem + identifier).with_suffix(filename.suffix)
def check_onnxruntime_requirements(minimum_version: Version):
    try:
        import onnxruntime
        ort_version = parse(onnxruntime.__version__)
        if ort_version < ORT_QUANTIZE_MINIMUM_VERSION: raise ImportError(f"We found an older version of onnxruntime ({onnxruntime.__version__}) but we require onnxruntime to be >= {minimum_version} to enable all the conversions options.\nPlease update onnxruntime by running `pip install --upgrade onnxruntime`")
    except ImportError: raise ImportError("onnxruntime doesn't seem to be currently installed. Please install the onnxruntime by running `pip install onnxruntime` and relaunch the conversion.")
def ensure_valid_input(model, tokens, input_names):
    print("Ensuring inputs are in correct order")
    model_args_name = model.forward.__code__.co_varnames
    model_args, ordered_input_names = [], []
    for arg_name in model_args_name[1:]:
        if arg_name in input_names:
            ordered_input_names.append(arg_name)
            model_args.append(tokens[arg_name])
        else:
            print(f"{arg_name} is not present in the generated input list.")
            break
    print(f"Generated inputs order: {ordered_input_names}")
    return ordered_input_names, tuple(model_args)
def infer_shapes(nlp: Pipeline, framework: str) -> Tuple[List[str], List[str], Dict, BatchEncoding]:
    def build_shape_dict(name: str, tensor, is_input: bool, seq_len: int):
        if isinstance(tensor, (tuple, list)): return [build_shape_dict(name, t, is_input, seq_len) for t in tensor]
        else:
            axes = {[axis for axis, numel in enumerate(tensor.shape) if numel == 1][0]: "batch"}
            if is_input:
                if len(tensor.shape) == 2: axes[1] = "sequence"
                else: raise ValueError(f"Unable to infer tensor axes ({len(tensor.shape)})")
            else:
                seq_axes = [dim for dim, shape in enumerate(tensor.shape) if shape == seq_len]
                axes.update({dim: "sequence" for dim in seq_axes})
        print(f"Found {'input' if is_input else 'output'} {name} with shape: {axes}")
        return axes
    tokens = nlp.tokenizer("This is a sample output", return_tensors=framework)
    seq_len = tokens.input_ids.shape[-1]
    outputs = nlp.model(**tokens) if framework == "pt" else nlp.model(tokens)
    if isinstance(outputs, ModelOutput): outputs = outputs.to_tuple()
    if not isinstance(outputs, (list, tuple)): outputs = (outputs,)
    input_vars = list(tokens.keys())
    input_dynamic_axes = {k: build_shape_dict(k, v, True, seq_len) for k, v in tokens.items()}
    outputs_flat = []
    for output in outputs:
        if isinstance(output, (tuple, list)): outputs_flat.extend(output)
        else: outputs_flat.append(output)
    output_names = [f"output_{i}" for i in range(len(outputs_flat))]
    output_dynamic_axes = {k: build_shape_dict(k, v, False, seq_len) for k, v in zip(output_names, outputs_flat)}
    dynamic_axes = dict(input_dynamic_axes, **output_dynamic_axes)
    return input_vars, output_names, dynamic_axes, tokens
def load_graph_from_args(pipeline_name: str, framework: str, model: str, tokenizer: Optional[str] = None, **models_kwargs) -> Pipeline:
    if tokenizer is None: tokenizer = model
    if framework == "pt" and not is_torch_available(): raise Exception("Cannot convert because PyTorch is not installed. Please install torch first.")
    if framework == "tf" and not is_tf_available(): raise Exception("Cannot convert because TF is not installed. Please install tensorflow first.")
    print(f"Loading pipeline (model: {model}, tokenizer: {tokenizer})")
    return pipeline(pipeline_name, model=model, tokenizer=tokenizer, framework=framework, model_kwargs=models_kwargs)
def convert_pytorch(nlp: Pipeline, opset: int, output: Path, use_external_format: bool):
    if not is_torch_available(): raise Exception("Cannot convert because PyTorch is not installed. Please install torch first.")
    import torch
    from torch.onnx import export
    print(f"Using framework PyTorch: {torch.__version__}")
    with torch.no_grad():
        input_names, output_names, dynamic_axes, tokens = infer_shapes(nlp, "pt")
        ordered_input_names, model_args = ensure_valid_input(nlp.model, tokens, input_names)
        export(nlp.model, model_args, f=output.as_posix(), input_names=ordered_input_names, output_names=output_names, dynamic_axes=dynamic_axes, do_constant_folding=True, opset_version=opset)
def convert_tensorflow(nlp: Pipeline, opset: int, output: Path):
    if not is_tf_available(): raise Exception("Cannot convert because TF is not installed. Please install tensorflow first.")
    print("/!\\ Please note TensorFlow doesn't support exporting model > 2Gb /!\\")
    try:
        import tensorflow as tf
        import tf2onnx
        from tf2onnx import __version__ as t2ov
        print(f"Using framework TensorFlow: {tf.version.VERSION}, tf2onnx: {t2ov}")
        input_names, output_names, dynamic_axes, tokens = infer_shapes(nlp, "tf")
        nlp.model.predict(tokens.data)
        input_signature = [tf.TensorSpec.from_tensor(tensor, name=key) for key, tensor in tokens.items()]
        model_proto, _ = tf2onnx.convert.from_keras(nlp.model, input_signature, opset=opset, output_path=output.as_posix())
    except ImportError as e: raise Exception(f"Cannot import {e.name} required to convert TF model to ONNX. Please install {e.name} first. {e}")
def convert(framework: str, model: str, output: Path, opset: int, tokenizer: Optional[str] = None, use_external_format: bool = False, pipeline_name: str = "feature-extraction", **model_kwargs):
    warnings.warn("The `sapiens_transformers.convert_graph_to_onnx` package is deprecated and will be removed in version 1 of Sapiens Transformers", FutureWarning)
    print(f"ONNX opset version set to: {opset}")
    nlp = load_graph_from_args(pipeline_name, framework, model, tokenizer, **model_kwargs)
    if not output.parent.exists():
        print(f"Creating folder {output.parent}")
        makedirs(output.parent.as_posix())
    elif len(listdir(output.parent.as_posix())) > 0: raise Exception(f"Folder {output.parent.as_posix()} is not empty, aborting conversion")
    if framework == "pt": convert_pytorch(nlp, opset, output, use_external_format)
    else: convert_tensorflow(nlp, opset, output)
def optimize(onnx_model_path: Path) -> Path:
    from onnxruntime import InferenceSession, SessionOptions
    opt_model_path = generate_identified_filename(onnx_model_path, "-optimized")
    sess_option = SessionOptions()
    sess_option.optimized_model_filepath = opt_model_path.as_posix()
    _ = InferenceSession(onnx_model_path.as_posix(), sess_option)
    print(f"Optimized model has been written at {opt_model_path}: \N{HEAVY CHECK MARK}")
    print("/!\\ Optimized model contains hardware specific operators which might not be portable. /!\\")
    return opt_model_path
def quantize(onnx_model_path: Path) -> Path:
    import onnx
    import onnxruntime
    from onnx.onnx_pb import ModelProto
    from onnxruntime.quantization import QuantizationMode
    from onnxruntime.quantization.onnx_quantizer import ONNXQuantizer
    from onnxruntime.quantization.registry import IntegerOpsRegistry
    onnx_model = onnx.load(onnx_model_path.as_posix())
    if parse(onnx.__version__) < parse("1.5.0"): print("Models larger than 2GB will fail to quantize due to protobuf constraint.\nPlease upgrade to onnxruntime >= 1.5.0.")
    copy_model = ModelProto()
    copy_model.CopyFrom(onnx_model)
    if parse(onnxruntime.__version__) < parse("1.13.1"): quantizer = ONNXQuantizer(model=copy_model, per_channel=False, reduce_range=False, mode=QuantizationMode.IntegerOps, static=False, weight_qType=True, input_qType=False, tensors_range=None, nodes_to_quantize=None, nodes_to_exclude=None, op_types_to_quantize=list(IntegerOpsRegistry))
    else: quantizer = ONNXQuantizer(model=copy_model, per_channel=False, reduce_range=False, mode=QuantizationMode.IntegerOps, static=False, weight_qType=True, activation_qType=False, tensors_range=None, nodes_to_quantize=None, nodes_to_exclude=None, op_types_to_quantize=list(IntegerOpsRegistry))
    quantizer.quantize_model()
    quantized_model_path = generate_identified_filename(onnx_model_path, "-quantized")
    print(f"Quantized model has been written at {quantized_model_path}: \N{HEAVY CHECK MARK}")
    onnx.save_model(quantizer.model.model, quantized_model_path.as_posix())
    return quantized_model_path
def verify(path: Path):
    from onnxruntime import InferenceSession, SessionOptions
    from onnxruntime.capi.onnxruntime_pybind11_state import RuntimeException
    print(f"Checking ONNX model loading from: {path} ...")
    try:
        onnx_options = SessionOptions()
        _ = InferenceSession(path.as_posix(), onnx_options, providers=["CPUExecutionProvider"])
        print(f"Model {path} correctly loaded: \N{HEAVY CHECK MARK}")
    except RuntimeException as re: print(f"Error while loading the model {re}: \N{HEAVY BALLOT X}")
if __name__ == "__main__":
    parser = OnnxConverterArgumentParser()
    args = parser.parse_args()
    args.output = Path(args.output).absolute()
    try:
        print("\n====== Converting model to ONNX ======")
        convert(args.framework, args.model, args.output, args.opset, args.tokenizer, args.use_external_format, args.pipeline)
        if args.quantize:
            check_onnxruntime_requirements(ORT_QUANTIZE_MINIMUM_VERSION)
            if args.framework == "tf": print("\t Using TensorFlow might not provide the same optimization level compared to PyTorch.\n\t For TensorFlow users you can try optimizing the model directly through onnxruntime_tools.\n\t For more information, please refer to the onnxruntime documentation:\n\t\thttps://github.com/microsoft/onnxruntime/tree/master/onnxruntime/python/tools/transformers\n")
            print("\n====== Optimizing ONNX model ======")
            args.optimized_output = optimize(args.output)
            args.quantized_output = quantize(args.optimized_output)
        if args.check_loading:
            print("\n====== Check exported ONNX model(s) ======")
            verify(args.output)
            if hasattr(args, "optimized_output"): verify(args.optimized_output)
            if hasattr(args, "quantized_output"): verify(args.quantized_output)
    except Exception as e:
        print(f"Error while converting the model: {e}")
        exit(1)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
