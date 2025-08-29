"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import subprocess
import sys
import warnings
from argparse import ArgumentParser
from pathlib import Path
from packaging import version
from .. import AutoFeatureExtractor, AutoImageProcessor, AutoProcessor, AutoTokenizer
from ..utils import logging
from ..utils.import_utils import is_optimum_available
from .convert import export, validate_model_outputs
from .features import FeaturesManager
from .utils import get_preprocessor
MIN_OPTIMUM_VERSION = "1.5.0"
ENCODER_DECODER_MODELS = ["vision-encoder-decoder"]
def export_with_optimum(args):
    if is_optimum_available():
        from optimum.version import __version__ as optimum_version
        parsed_optimum_version = version.parse(optimum_version)
        if parsed_optimum_version < version.parse(MIN_OPTIMUM_VERSION): raise RuntimeError(f"sapiens_transformers.onnx requires optimum >= {MIN_OPTIMUM_VERSION} but {optimum_version} is installed. You can upgrade optimum by running: pip install -U optimum[exporters]")
    else: raise RuntimeError("sapiens_transformers.onnx requires optimum to run, you can install the library by running: pip install optimum[exporters]")
    cmd_line = [sys.executable, "-m", "optimum.exporters.onnx", f"--model {args.model}", f"--task {args.feature}", f"--framework {args.framework}" if args.framework is not None else "", f"{args.output}"]
    proc = subprocess.Popen(cmd_line, stdout=subprocess.PIPE)
    proc.wait()
    logger.info("The export was done by optimum.exporters.onnx. We recommend using to use this package directly in future, as sapiens_transformers.onnx is deprecated, and will be removed in v5.")
def export_with_transformers(args):
    args.output = args.output if args.output.is_file() else args.output.joinpath("model.onnx")
    if not args.output.parent.exists(): args.output.parent.mkdir(parents=True)
    model = FeaturesManager.get_model_from_feature(args.feature, args.model, framework=args.framework, cache_dir=args.cache_dir)
    model_kind, model_onnx_config = FeaturesManager.check_supported_model_or_raise(model, feature=args.feature)
    onnx_config = model_onnx_config(model.config)
    if model_kind in ENCODER_DECODER_MODELS:
        encoder_model = model.get_encoder()
        decoder_model = model.get_decoder()
        encoder_onnx_config = onnx_config.get_encoder_config(encoder_model.config)
        decoder_onnx_config = onnx_config.get_decoder_config(encoder_model.config, decoder_model.config, feature=args.feature)
        if args.opset is None: args.opset = max(encoder_onnx_config.default_onnx_opset, decoder_onnx_config.default_onnx_opset)
        if args.opset < min(encoder_onnx_config.default_onnx_opset, decoder_onnx_config.default_onnx_opset): raise ValueError(f"Opset {args.opset} is not sufficient to export {model_kind}. At least {min(encoder_onnx_config.default_onnx_opset, decoder_onnx_config.default_onnx_opset)} is required.")
        preprocessor = AutoFeatureExtractor.from_pretrained(args.model)
        onnx_inputs, onnx_outputs = export(preprocessor, encoder_model, encoder_onnx_config, args.opset, args.output.parent.joinpath("encoder_model.onnx"))
        validate_model_outputs(encoder_onnx_config, preprocessor, encoder_model, args.output.parent.joinpath("encoder_model.onnx"), onnx_outputs, args.atol if args.atol else encoder_onnx_config.atol_for_validation)
        preprocessor = AutoTokenizer.from_pretrained(args.model)
        onnx_inputs, onnx_outputs = export(preprocessor, decoder_model, decoder_onnx_config, args.opset, args.output.parent.joinpath("decoder_model.onnx"))
        validate_model_outputs(decoder_onnx_config, preprocessor, decoder_model, args.output.parent.joinpath("decoder_model.onnx"), onnx_outputs, args.atol if args.atol else decoder_onnx_config.atol_for_validation)
        logger.info(f"All good, model saved at: {args.output.parent.joinpath('encoder_model.onnx').as_posix()}, {args.output.parent.joinpath('decoder_model.onnx').as_posix()}")
    else:
        if args.preprocessor == "auto": preprocessor = get_preprocessor(args.model)
        elif args.preprocessor == "tokenizer": preprocessor = AutoTokenizer.from_pretrained(args.model)
        elif args.preprocessor == "image_processor": preprocessor = AutoImageProcessor.from_pretrained(args.model)
        elif args.preprocessor == "feature_extractor": preprocessor = AutoFeatureExtractor.from_pretrained(args.model)
        elif args.preprocessor == "processor": preprocessor = AutoProcessor.from_pretrained(args.model)
        else: raise ValueError(f"Unknown preprocessor type '{args.preprocessor}'")
        if args.opset is None: args.opset = onnx_config.default_onnx_opset
        if args.opset < onnx_config.default_onnx_opset: raise ValueError(f"Opset {args.opset} is not sufficient to export {model_kind}. At least  {onnx_config.default_onnx_opset} is required.")
        onnx_inputs, onnx_outputs = export(preprocessor, model, onnx_config, args.opset, args.output)
        if args.atol is None: args.atol = onnx_config.atol_for_validation
        validate_model_outputs(onnx_config, preprocessor, model, args.output, onnx_outputs, args.atol)
        logger.info(f"All good, model saved at: {args.output.as_posix()}")
        warnings.warn("The export was done by sapiens_transformers.onnx which is deprecated and will be removed in v5. We recommend using optimum.exporters.onnx in future.", FutureWarning)
def main():
    parser = ArgumentParser("Sapiens Transformers ONNX exporter")
    parser.add_argument("-m", "--model", type=str, required=True, help="Model ID or path on disk to load model from.")
    parser.add_argument("--feature", default="default", help="The type of features to export the model with.")
    parser.add_argument("--opset", type=int, default=None, help="ONNX opset version to export the model with.")
    parser.add_argument("--atol", type=float, default=None, help="Absolute difference tolerance when validating the model.")
    parser.add_argument("--framework", type=str, choices=["pt", "tf"], default=None, help=("The framework to use for the ONNX export. If not provided, will attempt to use the local checkpoint's original framework or what is available in the environment."))
    parser.add_argument("output", type=Path, help="Path indicating where to store generated ONNX model.")
    parser.add_argument("--cache_dir", type=str, default=None, help="Path indicating where to store cache.")
    parser.add_argument("--preprocessor", type=str, choices=["auto", "tokenizer", "feature_extractor", "image_processor", "processor"], default="auto", help="Which type of preprocessor to use. 'auto' tries to automatically detect it.")
    parser.add_argument("--export_with_transformers", action="store_true", help=("Whether to use sapiens_transformers.onnx instead of optimum.exporters.onnx to perform the ONNX export. It can be useful when exporting a model supported in transformers but not in optimum, otherwise it is not recommended."))
    args = parser.parse_args()
    if args.export_with_transformers or not is_optimum_available(): export_with_transformers(args)
    else: export_with_optimum(args)
if __name__ == "__main__":
    logger = logging.get_logger("sapiens_transformers.onnx")
    logger.setLevel(logging.INFO)
    main()
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
