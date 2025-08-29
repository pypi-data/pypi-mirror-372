"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import difflib
import json
import os
import re
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from datetime import date
from itertools import chain
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Pattern, Tuple, Union
import yaml
from ..models import auto as auto_module
from ..models.auto.configuration_auto import model_type_to_module_name
from ..utils import is_flax_available, is_tf_available, is_torch_available, logging
from . import BaseTransformersCLICommand
logger = logging.get_logger(__name__)
CURRENT_YEAR = date.today().year
TRANSFORMERS_PATH = Path(__file__).parent.parent
REPO_PATH = TRANSFORMERS_PATH.parent.parent
@dataclass
class ModelPatterns:
    model_name: str
    checkpoint: str
    model_type: Optional[str] = None
    model_lower_cased: Optional[str] = None
    model_camel_cased: Optional[str] = None
    model_upper_cased: Optional[str] = None
    config_class: Optional[str] = None
    tokenizer_class: Optional[str] = None
    image_processor_class: Optional[str] = None
    feature_extractor_class: Optional[str] = None
    processor_class: Optional[str] = None
    def __post_init__(self):
        if self.model_type is None: self.model_type = self.model_name.lower().replace(" ", "-")
        if self.model_lower_cased is None: self.model_lower_cased = self.model_name.lower().replace(" ", "_").replace("-", "_")
        if self.model_camel_cased is None:
            words = self.model_name.split(" ")
            words = list(chain(*[w.split("-") for w in words]))
            words = [w[0].upper() + w[1:] for w in words]
            self.model_camel_cased = "".join(words)
        if self.model_upper_cased is None: self.model_upper_cased = self.model_name.upper().replace(" ", "_").replace("-", "_")
        if self.config_class is None: self.config_class = f"{self.model_camel_cased}Config"
ATTRIBUTE_TO_PLACEHOLDER = {'config_class': '[CONFIG_CLASS]', 'tokenizer_class': '[TOKENIZER_CLASS]', 'image_processor_class': '[IMAGE_PROCESSOR_CLASS]', 'feature_extractor_class': '[FEATURE_EXTRACTOR_CLASS]',
'processor_class': '[PROCESSOR_CLASS]', 'checkpoint': '[CHECKPOINT]', 'model_type': '[MODEL_TYPE]', 'model_upper_cased': '[MODEL_UPPER_CASED]', 'model_camel_cased': '[MODEL_CAMELCASED]', 'model_lower_cased': '[MODEL_LOWER_CASED]', 'model_name': '[MODEL_NAME]'}
def is_empty_line(line: str) -> bool: return len(line) == 0 or line.isspace()
def find_indent(line: str) -> int:
    search = re.search(r"^(\s*)(?:\S|$)", line)
    if search is None: return 0
    return len(search.groups()[0])
def parse_module_content(content: str) -> List[str]:
    objects = []
    current_object = []
    lines = content.split("\n")
    end_markers = [")", "]", "}", '"""']
    for line in lines:
        is_valid_object = len(current_object) > 0
        if is_valid_object and len(current_object) == 1: is_valid_object = not current_object[0].startswith("# Copied from")
        if not is_empty_line(line) and find_indent(line) == 0 and is_valid_object:
            if line in end_markers:
                current_object.append(line)
                objects.append("\n".join(current_object))
                current_object = []
            else:
                objects.append("\n".join(current_object))
                current_object = [line]
        else: current_object.append(line)
    if len(current_object) > 0: objects.append("\n".join(current_object))
    return objects
def extract_block(content: str, indent_level: int = 0) -> str:
    current_object = []
    lines = content.split("\n")
    end_markers = [")", "]", "}", '"""']
    for idx, line in enumerate(lines):
        if idx == 0 and indent_level > 0 and not is_empty_line(line) and find_indent(line) != indent_level: raise ValueError(f"When `indent_level > 0`, the first line in `content` should have indent level {indent_level}. Got {find_indent(line)} instead.")
        if find_indent(line) < indent_level and not is_empty_line(line): break
        is_valid_object = len(current_object) > 0
        if (not is_empty_line(line) and not line.endswith(":") and find_indent(line) == indent_level and is_valid_object):
            if line.lstrip() in end_markers: current_object.append(line)
            return "\n".join(current_object)
        else: current_object.append(line)
    if len(current_object) > 0: return "\n".join(current_object)
def add_content_to_text(text: str, content: str, add_after: Optional[Union[str, Pattern]] = None, add_before: Optional[Union[str, Pattern]] = None, exact_match: bool = False) -> str:
    if add_after is None and add_before is None: raise ValueError("You need to pass either `add_after` or `add_before`")
    if add_after is not None and add_before is not None: raise ValueError("You can't pass both `add_after` or `add_before`")
    pattern = add_after if add_before is None else add_before
    def this_is_the_line(line):
        if isinstance(pattern, Pattern): return pattern.search(line) is not None
        elif exact_match: return pattern == line
        else: return pattern in line
    new_lines = []
    for line in text.split("\n"):
        if this_is_the_line(line):
            if add_before is not None: new_lines.append(content)
            new_lines.append(line)
            if add_after is not None: new_lines.append(content)
        else: new_lines.append(line)
    return "\n".join(new_lines)
def add_content_to_file(file_name: Union[str, os.PathLike], content: str, add_after: Optional[Union[str, Pattern]] = None, add_before: Optional[Union[str, Pattern]] = None, exact_match: bool = False):
    with open(file_name, "r", encoding="utf-8") as f: old_content = f.read()
    new_content = add_content_to_text(old_content, content, add_after=add_after, add_before=add_before, exact_match=exact_match)
    with open(file_name, "w", encoding="utf-8") as f: f.write(new_content)
def replace_model_patterns(text: str, old_model_patterns: ModelPatterns, new_model_patterns: ModelPatterns) -> Tuple[str, str]:
    attributes_to_check = ["config_class"]
    for attr in ["tokenizer_class", "image_processor_class", "feature_extractor_class", "processor_class"]:
        if getattr(old_model_patterns, attr) is not None and getattr(new_model_patterns, attr) is not None: attributes_to_check.append(attr)
    if old_model_patterns.checkpoint not in [old_model_patterns.model_type, old_model_patterns.model_lower_cased]: attributes_to_check.append("checkpoint")
    if old_model_patterns.model_type != old_model_patterns.model_lower_cased: attributes_to_check.append("model_type")
    else: text = re.sub(rf'(\s*)model_type = "{old_model_patterns.model_type}"', r'\1model_type = "[MODEL_TYPE]"', text)
    if old_model_patterns.model_upper_cased == old_model_patterns.model_camel_cased:
        old_model_value = old_model_patterns.model_upper_cased
        if re.search(rf"{old_model_value}_[A-Z_]*[^A-Z_]", text) is not None: text = re.sub(rf"{old_model_value}([A-Z_]*)([^a-zA-Z_])", r"[MODEL_UPPER_CASED]\1\2", text)
    else: attributes_to_check.append("model_upper_cased")
    attributes_to_check.extend(["model_camel_cased", "model_lower_cased", "model_name"])
    for attr in attributes_to_check: text = text.replace(getattr(old_model_patterns, attr), ATTRIBUTE_TO_PLACEHOLDER[attr])
    replacements = []
    for attr, placeholder in ATTRIBUTE_TO_PLACEHOLDER.items():
        if placeholder in text:
            replacements.append((getattr(old_model_patterns, attr), getattr(new_model_patterns, attr)))
            text = text.replace(placeholder, getattr(new_model_patterns, attr))
    old_replacement_values = [old for old, new in replacements]
    if len(set(old_replacement_values)) != len(old_replacement_values): return text, ""
    replacements = simplify_replacements(replacements)
    replacements = [f"{old}->{new}" for old, new in replacements]
    return text, ",".join(replacements)
def simplify_replacements(replacements):
    if len(replacements) <= 1: return replacements
    replacements.sort(key=lambda x: len(x[0]))
    idx = 0
    while idx < len(replacements):
        old, new = replacements[idx]
        j = idx + 1
        while j < len(replacements):
            old_2, new_2 = replacements[j]
            if old_2.replace(old, new) == new_2: replacements.pop(j)
            else: j += 1
        idx += 1
    return replacements
def get_module_from_file(module_file: Union[str, os.PathLike]) -> str:
    full_module_path = Path(module_file).absolute()
    module_parts = full_module_path.with_suffix("").parts
    idx = len(module_parts) - 1
    while idx >= 0 and module_parts[idx] != "sapiens_transformers": idx -= 1
    if idx < 0: raise ValueError(f"{module_file} is not a transformers module.")
    return ".".join(module_parts[idx:])
SPECIAL_PATTERNS = {'_CHECKPOINT_FOR_DOC =': 'checkpoint', '_CONFIG_FOR_DOC =': 'config_class', '_TOKENIZER_FOR_DOC =': 'tokenizer_class', '_IMAGE_PROCESSOR_FOR_DOC =': 'image_processor_class',
'_FEAT_EXTRACTOR_FOR_DOC =': 'feature_extractor_class', '_PROCESSOR_FOR_DOC =': 'processor_class'}
_re_class_func = re.compile(r"^(?:class|def)\s+([^\s:\(]+)\s*(?:\(|\:)", flags=re.MULTILINE)
def remove_attributes(obj, target_attr):
    lines = obj.split(os.linesep)
    target_idx = None
    for idx, line in enumerate(lines):
        if line.lstrip().startswith(f"{target_attr} = "):
            target_idx = idx
            break
        elif line.lstrip().startswith(f"def {target_attr}("):
            target_idx = idx
            break
    if target_idx is None: return obj
    line = lines[target_idx]
    indent_level = find_indent(line)
    parsed = extract_block("\n".join(lines[target_idx:]), indent_level)
    num_lines = len(parsed.split("\n"))
    for idx in range(num_lines): lines[target_idx + idx] = None
    for idx in range(target_idx - 1, -1, -1):
        line = lines[idx]
        if (line.lstrip().startswith("#") or line.lstrip().startswith("@")) and find_indent(line) == indent_level: lines[idx] = None
        else: break
    new_obj = os.linesep.join([x for x in lines if x is not None])
    return new_obj
def duplicate_module(module_file: Union[str, os.PathLike], old_model_patterns: ModelPatterns, new_model_patterns: ModelPatterns, dest_file: Optional[str] = None, add_copied_from: bool = True, attrs_to_remove: List[str] = None):
    if dest_file is None: dest_file = str(module_file).replace(old_model_patterns.model_lower_cased, new_model_patterns.model_lower_cased)
    with open(module_file, "r", encoding="utf-8") as f: content = f.read()
    content = re.sub(r"# Copyright (\d+)\s", f"# Copyright {CURRENT_YEAR} ", content)
    objects = parse_module_content(content)
    new_objects = []
    for obj in objects:
        special_pattern = False
        for pattern, attr in SPECIAL_PATTERNS.items():
            if pattern in obj:
                obj = obj.replace(getattr(old_model_patterns, attr), getattr(new_model_patterns, attr))
                new_objects.append(obj)
                special_pattern = True
                break
        if special_pattern: continue
        old_obj = obj
        obj, replacement = replace_model_patterns(obj, old_model_patterns, new_model_patterns)
        has_copied_from = re.search(r"^#\s+Copied from", obj, flags=re.MULTILINE) is not None
        if add_copied_from and not has_copied_from and _re_class_func.search(obj) is not None and len(replacement) > 0:
            module_name = get_module_from_file(module_file)
            old_object_name = _re_class_func.search(old_obj).groups()[0]
            obj = add_content_to_text(obj, f"# Copied from {module_name}.{old_object_name} with {replacement}", add_before=_re_class_func)
        obj = re.sub("\n[ ]+# Copied from [^\n]*\n", "\n", obj)
        new_objects.append(obj)
    content = "\n".join(new_objects)
    if attrs_to_remove is not None:
        for attr in attrs_to_remove: content = remove_attributes(content, target_attr=attr)
    with open(dest_file, "w", encoding="utf-8") as f: f.write(content)
def filter_framework_files(files: List[Union[str, os.PathLike]], frameworks: Optional[List[str]] = None) -> List[Union[str, os.PathLike]]:
    if frameworks is None: frameworks = get_default_frameworks()
    framework_to_file = {}
    others = []
    for f in files:
        parts = Path(f).name.split("_")
        if "modeling" not in parts:
            others.append(f)
            continue
        if "tf" in parts: framework_to_file["tf"] = f
        elif "flax" in parts: framework_to_file["flax"] = f
        else: framework_to_file["pt"] = f
    return [framework_to_file[f] for f in frameworks if f in framework_to_file] + others
def get_model_files(model_type: str, frameworks: Optional[List[str]] = None) -> Dict[str, Union[Path, List[Path]]]:
    module_name = model_type_to_module_name(model_type)
    model_module = TRANSFORMERS_PATH / "models" / module_name
    model_files = list(model_module.glob("*.py"))
    model_files = filter_framework_files(model_files, frameworks=frameworks)
    doc_file = REPO_PATH / "docs" / "source" / "en" / "model_doc" / f"{model_type}.md"
    test_files = [f"test_modeling_{module_name}.py", f"test_modeling_tf_{module_name}.py", f"test_modeling_flax_{module_name}.py", f"test_tokenization_{module_name}.py",
    f"test_image_processing_{module_name}.py", f"test_feature_extraction_{module_name}.py", f"test_processor_{module_name}.py"]
    test_files = filter_framework_files(test_files, frameworks=frameworks)
    test_files = [REPO_PATH / "tests" / "models" / module_name / f for f in test_files]
    test_files = [f for f in test_files if f.exists()]
    return {"doc_file": doc_file, "model_files": model_files, "module_name": module_name, "test_files": test_files}
_re_checkpoint_for_doc = re.compile(r"^_CHECKPOINT_FOR_DOC\s+=\s+(\S*)\s*$", flags=re.MULTILINE)
def find_base_model_checkpoint(model_type: str, model_files: Optional[Dict[str, Union[Path, List[Path]]]] = None) -> str:
    if model_files is None: model_files = get_model_files(model_type)
    module_files = model_files["model_files"]
    for fname in module_files:
        if "modeling" not in str(fname): continue
        with open(fname, "r", encoding="utf-8") as f:
            content = f.read()
            if _re_checkpoint_for_doc.search(content) is not None:
                checkpoint = _re_checkpoint_for_doc.search(content).groups()[0]
                checkpoint = checkpoint.replace('"', "")
                checkpoint = checkpoint.replace("'", "")
                return checkpoint
    return ""
def get_default_frameworks():
    frameworks = []
    if is_torch_available(): frameworks.append("pt")
    if is_tf_available(): frameworks.append("tf")
    if is_flax_available(): frameworks.append("flax")
    return frameworks
_re_model_mapping = re.compile("MODEL_([A-Z_]*)MAPPING_NAMES")
def retrieve_model_classes(model_type: str, frameworks: Optional[List[str]] = None) -> Dict[str, List[str]]:
    if frameworks is None: frameworks = get_default_frameworks()
    modules = {"pt": auto_module.modeling_auto if is_torch_available() else None, "tf": auto_module.modeling_tf_auto if is_tf_available() else None, "flax": auto_module.modeling_flax_auto if is_flax_available() else None}
    model_classes = {}
    for framework in frameworks:
        new_model_classes = []
        if modules[framework] is None: raise ValueError(f"You selected {framework} in the frameworks, but it is not installed.")
        model_mappings = [attr for attr in dir(modules[framework]) if _re_model_mapping.search(attr) is not None]
        for model_mapping_name in model_mappings:
            model_mapping = getattr(modules[framework], model_mapping_name)
            if model_type in model_mapping: new_model_classes.append(model_mapping[model_type])
        if len(new_model_classes) > 0: model_classes[framework] = list(set(new_model_classes))
    return model_classes
def retrieve_info_for_model(model_type, frameworks: Optional[List[str]] = None):
    if model_type not in auto_module.MODEL_NAMES_MAPPING: raise ValueError(f"{model_type} is not a valid model type.")
    model_name = auto_module.MODEL_NAMES_MAPPING[model_type]
    config_class = auto_module.configuration_auto.CONFIG_MAPPING_NAMES[model_type]
    if model_type in auto_module.tokenization_auto.TOKENIZER_MAPPING_NAMES:
        tokenizer_classes = auto_module.tokenization_auto.TOKENIZER_MAPPING_NAMES[model_type]
        tokenizer_class = tokenizer_classes[0] if tokenizer_classes[0] is not None else tokenizer_classes[1]
    else: tokenizer_class = None
    image_processor_classes = auto_module.image_processing_auto.IMAGE_PROCESSOR_MAPPING_NAMES.get(model_type, None)
    if isinstance(image_processor_classes, tuple): image_processor_class = image_processor_classes[0]
    else: image_processor_class = image_processor_classes
    feature_extractor_class = auto_module.feature_extraction_auto.FEATURE_EXTRACTOR_MAPPING_NAMES.get(model_type, None)
    processor_class = auto_module.processing_auto.PROCESSOR_MAPPING_NAMES.get(model_type, None)
    model_files = get_model_files(model_type, frameworks=frameworks)
    model_camel_cased = config_class.replace("Config", "")
    available_frameworks = []
    for fname in model_files["model_files"]:
        if "modeling_tf" in str(fname): available_frameworks.append("tf")
        elif "modeling_flax" in str(fname): available_frameworks.append("flax")
        elif "modeling" in str(fname): available_frameworks.append("pt")
    if frameworks is None: frameworks = get_default_frameworks()
    frameworks = [f for f in frameworks if f in available_frameworks]
    model_classes = retrieve_model_classes(model_type, frameworks=frameworks)
    model_upper_cased = model_camel_cased.upper()
    model_patterns = ModelPatterns(model_name, checkpoint=find_base_model_checkpoint(model_type, model_files=model_files), model_type=model_type, model_camel_cased=model_camel_cased,
    model_lower_cased=model_files["module_name"], model_upper_cased=model_upper_cased, config_class=config_class, tokenizer_class=tokenizer_class, image_processor_class=image_processor_class,
    feature_extractor_class=feature_extractor_class, processor_class=processor_class)
    return {"frameworks": frameworks, "model_classes": model_classes, "model_files": model_files, "model_patterns": model_patterns}
def clean_frameworks_in_init(init_file: Union[str, os.PathLike], frameworks: Optional[List[str]] = None, keep_processing: bool = True):
    if frameworks is None: frameworks = get_default_frameworks()
    names = {"pt": "torch"}
    to_remove = [names.get(f, f) for f in ["pt", "tf", "flax"] if f not in frameworks]
    if not keep_processing: to_remove.extend(["sentencepiece", "tokenizers", "vision"])
    if len(to_remove) == 0: return
    remove_pattern = "|".join(to_remove)
    re_conditional_imports = re.compile(rf"^\s*if not is_({remove_pattern})_available\(\):\s*$")
    re_try = re.compile(r"\s*try:")
    re_else = re.compile(r"\s*else:")
    re_is_xxx_available = re.compile(rf"is_({remove_pattern})_available")
    with open(init_file, "r", encoding="utf-8") as f: content = f.read()
    lines = content.split("\n")
    new_lines = []
    idx = 0
    while idx < len(lines):
        if (re_conditional_imports.search(lines[idx]) is not None) and (re_try.search(lines[idx - 1]) is not None):
            new_lines.pop()
            idx += 1
            while is_empty_line(lines[idx]) or re_else.search(lines[idx]) is None: idx += 1
            idx += 1
            indent = find_indent(lines[idx])
            while find_indent(lines[idx]) >= indent or is_empty_line(lines[idx]): idx += 1
        elif re_is_xxx_available.search(lines[idx]) is not None:
            line = lines[idx]
            for framework in to_remove:
                line = line.replace(f", is_{framework}_available", "")
                line = line.replace(f"is_{framework}_available, ", "")
                line = line.replace(f"is_{framework}_available,", "")
                line = line.replace(f"is_{framework}_available", "")
            if len(line.strip()) > 0: new_lines.append(line)
            idx += 1
        elif keep_processing or (re.search(r'^\s*"(tokenization|processing|feature_extraction|image_processing)', lines[idx]) is None and re.search(r"^\s*from .(tokenization|processing|feature_extraction|image_processing)", lines[idx]) is None):
            new_lines.append(lines[idx])
            idx += 1
        else: idx += 1
    with open(init_file, "w", encoding="utf-8") as f: f.write("\n".join(new_lines))
def add_model_to_main_init(old_model_patterns: ModelPatterns, new_model_patterns: ModelPatterns, frameworks: Optional[List[str]] = None, with_processing: bool = True):
    with open(TRANSFORMERS_PATH / "__init__.py", "r", encoding="utf-8") as f: content = f.read()
    lines = content.split("\n")
    idx = 0
    new_lines = []
    framework = None
    while idx < len(lines):
        new_framework = False
        if not is_empty_line(lines[idx]) and find_indent(lines[idx]) == 0: framework = None
        elif lines[idx].lstrip().startswith("if not is_torch_available"):
            framework = "pt"
            new_framework = True
        elif lines[idx].lstrip().startswith("if not is_tf_available"):
            framework = "tf"
            new_framework = True
        elif lines[idx].lstrip().startswith("if not is_flax_available"):
            framework = "flax"
            new_framework = True
        if new_framework:
            while lines[idx].strip() != "else:":
                new_lines.append(lines[idx])
                idx += 1
        if framework is not None and frameworks is not None and framework not in frameworks:
            new_lines.append(lines[idx])
            idx += 1
        elif re.search(rf'models.{old_model_patterns.model_lower_cased}( |")', lines[idx]) is not None:
            block = [lines[idx]]
            indent = find_indent(lines[idx])
            idx += 1
            while find_indent(lines[idx]) > indent:
                block.append(lines[idx])
                idx += 1
            if lines[idx].strip() in [")", "]", "],"]:
                block.append(lines[idx])
                idx += 1
            block = "\n".join(block)
            new_lines.append(block)
            add_block = True
            if not with_processing:
                processing_classes = [old_model_patterns.tokenizer_class, old_model_patterns.image_processor_class, old_model_patterns.feature_extractor_class, old_model_patterns.processor_class]
                processing_classes = [c for c in processing_classes if c is not None]
                for processing_class in processing_classes:
                    block = block.replace(f' "{processing_class}",', "")
                    block = block.replace(f', "{processing_class}"', "")
                    block = block.replace(f" {processing_class},", "")
                    block = block.replace(f", {processing_class}", "")
                    if processing_class in block: add_block = False
            if add_block: new_lines.append(replace_model_patterns(block, old_model_patterns, new_model_patterns)[0])
        else:
            new_lines.append(lines[idx])
            idx += 1
    with open(TRANSFORMERS_PATH / "__init__.py", "w", encoding="utf-8") as f: f.write("\n".join(new_lines))
def insert_tokenizer_in_auto_module(old_model_patterns: ModelPatterns, new_model_patterns: ModelPatterns):
    if old_model_patterns.tokenizer_class is None or new_model_patterns.tokenizer_class is None: return
    with open(TRANSFORMERS_PATH / "models" / "auto" / "tokenization_auto.py", "r", encoding="utf-8") as f: content = f.read()
    lines = content.split("\n")
    idx = 0
    while not lines[idx].startswith("    TOKENIZER_MAPPING_NAMES = OrderedDict("): idx += 1
    idx += 1
    while not lines[idx].startswith("TOKENIZER_MAPPING = _LazyAutoMapping"):
        if lines[idx].endswith(","): block = lines[idx]
        else:
            block = []
            while not lines[idx].startswith("            ),"):
                block.append(lines[idx])
                idx += 1
            block = "\n".join(block)
        idx += 1
        if f'"{old_model_patterns.model_type}"' in block and old_model_patterns.tokenizer_class in block: break
    new_block = block.replace(old_model_patterns.model_type, new_model_patterns.model_type)
    new_block = new_block.replace(old_model_patterns.tokenizer_class, new_model_patterns.tokenizer_class)
    new_lines = lines[:idx] + [new_block] + lines[idx:]
    with open(TRANSFORMERS_PATH / "models" / "auto" / "tokenization_auto.py", "w", encoding="utf-8") as f: f.write("\n".join(new_lines))
AUTO_CLASSES_PATTERNS = {"configuration_auto.py": [
    '        ("{model_type}", "{model_name}"),',
    '        ("{model_type}", "{config_class}"),',
    '        ("{model_type}", "{pretrained_archive_map}"),',
],
"feature_extraction_auto.py": ['        ("{model_type}", "{feature_extractor_class}"),'],
"image_processing_auto.py": ['        ("{model_type}", "{image_processor_class}"),'],
"modeling_auto.py": ['        ("{model_type}", "{any_pt_class}"),'],
"modeling_tf_auto.py": ['        ("{model_type}", "{any_tf_class}"),'],
"modeling_flax_auto.py": ['        ("{model_type}", "{any_flax_class}"),'],
"processing_auto.py": ['        ("{model_type}", "{processor_class}"),']}
def add_model_to_auto_classes(old_model_patterns: ModelPatterns, new_model_patterns: ModelPatterns, model_classes: Dict[str, List[str]]):
    for filename in AUTO_CLASSES_PATTERNS:
        new_patterns = []
        for pattern in AUTO_CLASSES_PATTERNS[filename]:
            if re.search("any_([a-z]*)_class", pattern) is not None:
                framework = re.search("any_([a-z]*)_class", pattern).groups()[0]
                if framework in model_classes: new_patterns.extend([pattern.replace("{" + f"any_{framework}_class" + "}", cls) for cls in model_classes[framework]])
            elif "{config_class}" in pattern: new_patterns.append(pattern.replace("{config_class}", old_model_patterns.config_class))
            elif "{image_processor_class}" in pattern:
                if (old_model_patterns.image_processor_class is not None and new_model_patterns.image_processor_class is not None): new_patterns.append(pattern.replace("{image_processor_class}", old_model_patterns.image_processor_class))
            elif "{feature_extractor_class}" in pattern:
                if (old_model_patterns.feature_extractor_class is not None and new_model_patterns.feature_extractor_class is not None): new_patterns.append(pattern.replace("{feature_extractor_class}", old_model_patterns.feature_extractor_class))
            elif "{processor_class}" in pattern:
                if old_model_patterns.processor_class is not None and new_model_patterns.processor_class is not None: new_patterns.append(pattern.replace("{processor_class}", old_model_patterns.processor_class))
            else: new_patterns.append(pattern)
        for pattern in new_patterns:
            full_name = TRANSFORMERS_PATH / "models" / "auto" / filename
            old_model_line = pattern
            new_model_line = pattern
            for attr in ["model_type", "model_name"]:
                old_model_line = old_model_line.replace("{" + attr + "}", getattr(old_model_patterns, attr))
                new_model_line = new_model_line.replace("{" + attr + "}", getattr(new_model_patterns, attr))
            new_model_line = new_model_line.replace(old_model_patterns.model_camel_cased, new_model_patterns.model_camel_cased)
            add_content_to_file(full_name, new_model_line, add_after=old_model_line)
    insert_tokenizer_in_auto_module(old_model_patterns, new_model_patterns)
DOC_OVERVIEW_TEMPLATE = """## Overview
The {model_name} model was proposed in [<INSERT PAPER NAME HERE>](<INSERT PAPER LINK HERE>) by <INSERT AUTHORS HERE>.
<INSERT SHORT SUMMARY HERE>
The abstract from the paper is the following:
*<INSERT PAPER ABSTRACT HERE>*
Tips:
<INSERT TIPS ABOUT MODEL HERE>
The original code can be found [here](<INSERT LINK TO GITHUB REPO HERE>).
"""
def duplicate_doc_file(doc_file: Union[str, os.PathLike], old_model_patterns: ModelPatterns, new_model_patterns: ModelPatterns, dest_file: Optional[Union[str, os.PathLike]] = None, frameworks: Optional[List[str]] = None):
    with open(doc_file, "r", encoding="utf-8") as f: content = f.read()
    content = re.sub(r"<!--\s*Copyright (\d+)\s", f"<!--Copyright {CURRENT_YEAR} ", content)
    if frameworks is None: frameworks = get_default_frameworks()
    if dest_file is None: dest_file = Path(doc_file).parent / f"{new_model_patterns.model_type}.md"
    lines = content.split("\n")
    blocks = []
    current_block = []
    for line in lines:
        if line.startswith("#"):
            blocks.append("\n".join(current_block))
            current_block = [line]
        else: current_block.append(line)
    blocks.append("\n".join(current_block))
    new_blocks = []
    in_classes = False
    for block in blocks:
        if not block.startswith("#"): new_blocks.append(block)
        elif re.search(r"^#\s+\S+", block) is not None: new_blocks.append(f"# {new_model_patterns.model_name}\n")
        elif not in_classes and old_model_patterns.config_class in block.split("\n")[0]:
            in_classes = True
            new_blocks.append(DOC_OVERVIEW_TEMPLATE.format(model_name=new_model_patterns.model_name))
            new_block, _ = replace_model_patterns(block, old_model_patterns, new_model_patterns)
            new_blocks.append(new_block)
        elif in_classes:
            in_classes = True
            block_title = block.split("\n")[0]
            block_class = re.search(r"^#+\s+(\S.*)$", block_title).groups()[0]
            new_block, _ = replace_model_patterns(block, old_model_patterns, new_model_patterns)
            if "Tokenizer" in block_class:
                if old_model_patterns.tokenizer_class != new_model_patterns.tokenizer_class: new_blocks.append(new_block)
            elif "ImageProcessor" in block_class:
                if old_model_patterns.image_processor_class != new_model_patterns.image_processor_class: new_blocks.append(new_block)
            elif "FeatureExtractor" in block_class:
                if old_model_patterns.feature_extractor_class != new_model_patterns.feature_extractor_class: new_blocks.append(new_block)
            elif "Processor" in block_class:
                if old_model_patterns.processor_class != new_model_patterns.processor_class: new_blocks.append(new_block)
            elif block_class.startswith("Flax"):
                if "flax" in frameworks: new_blocks.append(new_block)
            elif block_class.startswith("TF"):
                if "tf" in frameworks: new_blocks.append(new_block)
            elif len(block_class.split(" ")) == 1:
                if "pt" in frameworks: new_blocks.append(new_block)
            else: new_blocks.append(new_block)
    with open(dest_file, "w", encoding="utf-8") as f: f.write("\n".join(new_blocks))
def insert_model_in_doc_toc(old_model_patterns, new_model_patterns):
    toc_file = REPO_PATH / "docs" / "source" / "en" / "_toctree.yml"
    with open(toc_file, "r", encoding="utf8") as f: content = yaml.safe_load(f)
    api_idx = 0
    while content[api_idx]["title"] != "API": api_idx += 1
    api_doc = content[api_idx]["sections"]
    model_idx = 0
    while api_doc[model_idx]["title"] != "Models": model_idx += 1
    model_doc = api_doc[model_idx]["sections"]
    old_model_type = old_model_patterns.model_type
    section_idx = 0
    while section_idx < len(model_doc):
        sections = [entry["local"] for entry in model_doc[section_idx]["sections"]]
        if f"model_doc/{old_model_type}" in sections: break
        section_idx += 1
    if section_idx == len(model_doc):
        old_model = old_model_patterns.model_name
        new_model = new_model_patterns.model_name
        print(f"Did not find {old_model} in the table of content, so you will need to add {new_model} manually.")
        return
    toc_entry = {"local": f"model_doc/{new_model_patterns.model_type}", "title": new_model_patterns.model_name}
    model_doc[section_idx]["sections"].append(toc_entry)
    model_doc[section_idx]["sections"] = sorted(model_doc[section_idx]["sections"], key=lambda s: s["title"].lower())
    api_doc[model_idx]["sections"] = model_doc
    content[api_idx]["sections"] = api_doc
    with open(toc_file, "w", encoding="utf-8") as f: f.write(yaml.dump(content, allow_unicode=True))
def create_new_model_like(model_type: str, new_model_patterns: ModelPatterns, add_copied_from: bool = True, frameworks: Optional[List[str]] = None, old_checkpoint: Optional[str] = None):
    model_info = retrieve_info_for_model(model_type, frameworks=frameworks)
    model_files = model_info["model_files"]
    old_model_patterns = model_info["model_patterns"]
    if old_checkpoint is not None: old_model_patterns.checkpoint = old_checkpoint
    if len(old_model_patterns.checkpoint) == 0: raise ValueError("The old model checkpoint could not be recovered from the model type. Please pass it to the `old_checkpoint` argument.")
    keep_old_processing = True
    for processing_attr in ["image_processor_class", "feature_extractor_class", "processor_class", "tokenizer_class"]:
        if getattr(old_model_patterns, processing_attr) != getattr(new_model_patterns, processing_attr): keep_old_processing = False
    model_classes = model_info["model_classes"]
    old_module_name = model_files["module_name"]
    module_folder = TRANSFORMERS_PATH / "models" / new_model_patterns.model_lower_cased
    os.makedirs(module_folder, exist_ok=True)
    files_to_adapt = model_files["model_files"]
    if keep_old_processing: files_to_adapt = [f for f in files_to_adapt if "tokenization" not in str(f) and "processing" not in str(f) and "feature_extraction" not in str(f) and "image_processing" not in str(f)]
    os.makedirs(module_folder, exist_ok=True)
    for module_file in files_to_adapt:
        new_module_name = module_file.name.replace(old_model_patterns.model_lower_cased, new_model_patterns.model_lower_cased)
        dest_file = module_folder / new_module_name
        duplicate_module(module_file, old_model_patterns, new_model_patterns, dest_file=dest_file, add_copied_from=add_copied_from and "modeling" in new_module_name)
    clean_frameworks_in_init(module_folder / "__init__.py", frameworks=frameworks, keep_processing=not keep_old_processing)
    add_content_to_file(TRANSFORMERS_PATH / "models" / "__init__.py", f"    {new_model_patterns.model_lower_cased},", add_after=f"    {old_module_name},", exact_match=True)
    add_model_to_main_init(old_model_patterns, new_model_patterns, frameworks=frameworks, with_processing=not keep_old_processing)
    files_to_adapt = model_files["test_files"]
    if keep_old_processing: files_to_adapt = [f for f in files_to_adapt if "tokenization" not in str(f) and "processor" not in str(f) and "feature_extraction" not in str(f) and "image_processing" not in str(f)]
    def disable_fx_test(filename: Path) -> bool:
        with open(filename) as fp: content = fp.read()
        new_content = re.sub(r"fx_compatible\s*=\s*True", "fx_compatible = False", content)
        with open(filename, "w") as fp: fp.write(new_content)
        return content != new_content
    disabled_fx_test = False
    tests_folder = REPO_PATH / "tests" / "models" / new_model_patterns.model_lower_cased
    os.makedirs(tests_folder, exist_ok=True)
    with open(tests_folder / "__init__.py", "w"): pass
    for test_file in files_to_adapt:
        new_test_file_name = test_file.name.replace(old_model_patterns.model_lower_cased, new_model_patterns.model_lower_cased)
        dest_file = test_file.parent.parent / new_model_patterns.model_lower_cased / new_test_file_name
        duplicate_module(test_file, old_model_patterns, new_model_patterns, dest_file=dest_file, add_copied_from=False, attrs_to_remove=["pipeline_model_mapping", "is_pipeline_test_to_skip"])
        disabled_fx_test = disabled_fx_test | disable_fx_test(dest_file)
    if disabled_fx_test: print("The tests for symbolic tracing with torch.fx were disabled, you can add those once symbolic tracing works for your new model.")
    add_model_to_auto_classes(old_model_patterns, new_model_patterns, model_classes)
    doc_file = REPO_PATH / "docs" / "source" / "en" / "model_doc" / f"{old_model_patterns.model_type}.md"
    duplicate_doc_file(doc_file, old_model_patterns, new_model_patterns, frameworks=frameworks)
    insert_model_in_doc_toc(old_model_patterns, new_model_patterns)
    if old_model_patterns.model_type == old_model_patterns.checkpoint: print(f"The model you picked has the same name for the model type and the checkpoint name ({old_model_patterns.model_type}). As a result, it's possible some places where the new checkpoint should be, you have {new_model_patterns.model_type} instead. You should search for all instances of {new_model_patterns.model_type} in the new files and check they're not badly used as checkpoints.")
    elif old_model_patterns.model_lower_cased == old_model_patterns.checkpoint: print(f"The model you picked has the same name for the model type and the checkpoint name ({old_model_patterns.model_lower_cased}). As a result, it's possible some places where the new checkpoint should be, you have {new_model_patterns.model_lower_cased} instead. You should search for all instances of {new_model_patterns.model_lower_cased} in the new files and check they're not badly used as checkpoints.")
    if (old_model_patterns.model_type == old_model_patterns.model_lower_cased and new_model_patterns.model_type != new_model_patterns.model_lower_cased): print(f"The model you picked has the same name for the model type and the lowercased model name ({old_model_patterns.model_lower_cased}). As a result, it's possible some places where the new model type should be, you have {new_model_patterns.model_lower_cased} instead. You should search for all instances of {new_model_patterns.model_lower_cased} in the new files and check they're not badly used as the model type.")
    if not keep_old_processing and old_model_patterns.tokenizer_class is not None: print("The constants at the start of the new tokenizer file created needs to be manually fixed. If your new model has a tokenizer fast, you will also need to manually add the converter in the `SLOW_TO_FAST_CONVERTERS` constant of `convert_slow_tokenizer.py`.")
def add_new_model_like_command_factory(args: Namespace): return AddNewModelLikeCommand(config_file=args.config_file, path_to_repo=args.path_to_repo)
class AddNewModelLikeCommand(BaseTransformersCLICommand):
    @staticmethod
    def register_subcommand(parser: ArgumentParser):
        add_new_model_like_parser = parser.add_parser("add-new-model-like")
        add_new_model_like_parser.add_argument("--config_file", type=str, help="A file with all the information for this model creation.")
        add_new_model_like_parser.add_argument("--path_to_repo", type=str, help="When not using an editable install, the path to the Transformers repo.")
        add_new_model_like_parser.set_defaults(func=add_new_model_like_command_factory)
    def __init__(self, config_file=None, path_to_repo=None, *args):
        if config_file is not None:
            with open(config_file, "r", encoding="utf-8") as f: config = json.load(f)
            self.old_model_type = config["old_model_type"]
            self.model_patterns = ModelPatterns(**config["new_model_patterns"])
            self.add_copied_from = config.get("add_copied_from", True)
            self.frameworks = config.get("frameworks", get_default_frameworks())
            self.old_checkpoint = config.get("old_checkpoint", None)
        else: (self.old_model_type, self.model_patterns, self.add_copied_from, self.frameworks, self.old_checkpoint,) = get_user_input()
        self.path_to_repo = path_to_repo
    def run(self):
        if self.path_to_repo is not None:
            global TRANSFORMERS_PATH
            global REPO_PATH
            REPO_PATH = Path(self.path_to_repo)
            TRANSFORMERS_PATH = REPO_PATH / "src" / "sapiens_transformers"
        create_new_model_like(model_type=self.old_model_type, new_model_patterns=self.model_patterns, add_copied_from=self.add_copied_from, frameworks=self.frameworks, old_checkpoint=self.old_checkpoint)
def get_user_field(question: str, default_value: Optional[str] = None, is_valid_answer: Optional[Callable] = None, convert_to: Optional[Callable] = None, fallback_message: Optional[str] = None) -> Any:
    if not question.endswith(" "): question = question + " "
    if default_value is not None: question = f"{question} [{default_value}] "
    valid_answer = False
    while not valid_answer:
        answer = input(question)
        if default_value is not None and len(answer) == 0: answer = default_value
        if is_valid_answer is not None: valid_answer = is_valid_answer(answer)
        elif convert_to is not None:
            try:
                answer = convert_to(answer)
                valid_answer = True
            except Exception: valid_answer = False
        else: valid_answer = True
        if not valid_answer: print(fallback_message)
    return answer
def convert_to_bool(x: str) -> bool:
    if x.lower() in ["1", "y", "yes", "true"]: return True
    if x.lower() in ["0", "n", "no", "false"]: return False
    raise ValueError(f"{x} is not a value that can be converted to a bool.")
def get_user_input():
    model_types = list(auto_module.configuration_auto.MODEL_NAMES_MAPPING.keys())
    valid_model_type = False
    while not valid_model_type:
        old_model_type = input("What is the model you would like to duplicate? Please provide the lowercase `model_type` (e.g. roberta): ")
        if old_model_type in model_types: valid_model_type = True
        else:
            print(f"{old_model_type} is not a valid model type.")
            near_choices = difflib.get_close_matches(old_model_type, model_types)
            if len(near_choices) >= 1:
                if len(near_choices) > 1: near_choices = " or ".join(near_choices)
                print(f"Did you mean {near_choices}?")
    old_model_info = retrieve_info_for_model(old_model_type)
    old_tokenizer_class = old_model_info["model_patterns"].tokenizer_class
    old_image_processor_class = old_model_info["model_patterns"].image_processor_class
    old_feature_extractor_class = old_model_info["model_patterns"].feature_extractor_class
    old_processor_class = old_model_info["model_patterns"].processor_class
    old_frameworks = old_model_info["frameworks"]
    old_checkpoint = None
    if len(old_model_info["model_patterns"].checkpoint) == 0: old_checkpoint = get_user_field("We couldn't find the name of the base checkpoint for that model, please enter it here.")
    model_name = get_user_field("What is the name (with no special casing) for your new model in the paper (e.g. RoBERTa)? ")
    default_patterns = ModelPatterns(model_name, model_name)
    model_type = get_user_field("What identifier would you like to use for the `model_type` of this model? ", default_value=default_patterns.model_type)
    model_lower_cased = get_user_field("What lowercase name would you like to use for the module (folder) of this model? ", default_value=default_patterns.model_lower_cased)
    model_camel_cased = get_user_field("What prefix (camel-cased) would you like to use for the model classes of this model (e.g. Roberta)? ", default_value=default_patterns.model_camel_cased)
    model_upper_cased = get_user_field("What prefix (upper-cased) would you like to use for the constants relative to this model? ", default_value=default_patterns.model_upper_cased)
    config_class = get_user_field("What will be the name of the config class for this model? ", default_value=f"{model_camel_cased}Config")
    checkpoint = get_user_field("Please give a checkpoint identifier (on the model Hub) for this new model (e.g. facebook/FacebookAI/roberta-base): ")
    old_processing_classes = [c if not isinstance(c, tuple) else c[0] for c in [old_image_processor_class, old_feature_extractor_class, old_tokenizer_class, old_processor_class] if c is not None]
    old_processing_classes = ", ".join(old_processing_classes)
    keep_processing = get_user_field(f"Will your new model use the same processing class as {old_model_type} ({old_processing_classes}) (yes/no)? ", convert_to=convert_to_bool, fallback_message="Please answer yes/no, y/n, true/false or 1/0. ")
    if keep_processing:
        image_processor_class = old_image_processor_class
        feature_extractor_class = old_feature_extractor_class
        processor_class = old_processor_class
        tokenizer_class = old_tokenizer_class
    else:
        if old_tokenizer_class is not None: tokenizer_class = get_user_field("What will be the name of the tokenizer class for this model? ", default_value=f"{model_camel_cased}Tokenizer")
        else: tokenizer_class = None
        if old_image_processor_class is not None: image_processor_class = get_user_field("What will be the name of the image processor class for this model? ", default_value=f"{model_camel_cased}ImageProcessor")
        else: image_processor_class = None
        if old_feature_extractor_class is not None: feature_extractor_class = get_user_field("What will be the name of the feature extractor class for this model? ", default_value=f"{model_camel_cased}FeatureExtractor")
        else: feature_extractor_class = None
        if old_processor_class is not None: processor_class = get_user_field("What will be the name of the processor class for this model? ", default_value=f"{model_camel_cased}Processor")
        else: processor_class = None
    model_patterns = ModelPatterns(model_name, checkpoint, model_type=model_type, model_lower_cased=model_lower_cased, model_camel_cased=model_camel_cased, model_upper_cased=model_upper_cased, config_class=config_class, tokenizer_class=tokenizer_class, image_processor_class=image_processor_class, feature_extractor_class=feature_extractor_class, processor_class=processor_class)
    add_copied_from = get_user_field("Should we add # Copied from statements when creating the new modeling file (yes/no)? ", convert_to=convert_to_bool, default_value="yes", fallback_message="Please answer yes/no, y/n, true/false or 1/0.")
    all_frameworks = get_user_field(f"Should we add a version of your new model in all the frameworks implemented by {old_model_type} ({old_frameworks}) (yes/no)? ", convert_to=convert_to_bool, default_value="yes", fallback_message="Please answer yes/no, y/n, true/false or 1/0.")
    if all_frameworks: frameworks = None
    else:
        frameworks = get_user_field("Please enter the list of framworks you want (pt, tf, flax) separated by spaces", is_valid_answer=lambda x: all(p in ["pt", "tf", "flax"] for p in x.split(" ")))
        frameworks = list(set(frameworks.split(" ")))
    return (old_model_type, model_patterns, add_copied_from, frameworks, old_checkpoint)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
