"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import re
from functools import partial
from multiprocessing import Pool
from typing import List, Union
import numpy as np
from sapiens_transformers.tokenization_utils_base import INIT_TOKENIZER_DOCSTRING
from sapiens_transformers.tokenization_utils_fast import PreTrainedTokenizerFast
from sapiens_transformers.utils import add_end_docstrings
from ...utils import is_levenshtein_available, is_nltk_available, logging, requires_backends
if is_levenshtein_available(): from Levenshtein import ratio
if is_nltk_available(): import nltk
logger = logging.get_logger(__name__)
INIT_TOKENIZER_DOCSTRING += """
        tokenizer_object ([`tokenizers.Tokenizer`]):
            A [`tokenizers.Tokenizer`] object from HF tokenizers to instantiate from. See [Using tokenizers from HF
            tokenizers](../fast_tokenizers) for more information.
        tokenizer_file ([`str`]):
            A path to a local JSON file representing a previously serialized [`tokenizers.Tokenizer`] object from HF
            tokenizers.
"""
VOCAB_FILES_NAMES = {"tokenizer_file": "tokenizer.json"}
def markdown_compatible(text: str) -> str:
    text = re.sub(r"^\(([\d.]+[a-zA-Z]?)\) \\\[(.+?)\\\]$", r"\[\2 \\tag{\1}\]", text, flags=re.M)
    text = re.sub(r"^\\\[(.+?)\\\] \(([\d.]+[a-zA-Z]?)\)$", r"\[\1 \\tag{\2}\]", text, flags=re.M)
    text = re.sub(r"^\\\[(.+?)\\\] \(([\d.]+[a-zA-Z]?)\) (\\\[.+?\\\])$", r"\[\1 \\tag{\2}\] \3", text, flags=re.M)
    text = text.replace(r"\. ", ". ")
    text = text.replace(r"\bm{", r"\mathbf{").replace(r"{\\bm ", r"\mathbf{")
    text = re.sub(r"\\mbox{ ?\\boldmath\$(.*?)\$}", r"\\mathbf{\1}", text)
    text = re.sub(r"((?:http|ftp|https):\/\/(?:[\w_-]+(?:(?:\.[\w_-]+)+))(?:[\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-]))", r"[\1](\1)", text)
    text = re.sub(r"```\s*(.+?)\s*```", r"```\n\1\n```", text, flags=re.S)
    return text
def normalize_list_like_lines(generation):
    pattern = r"(?:^)(-|\*)?(?!-|\*) ?((?:\d|[ixv])+ )?.+? (-|\*) (((?:\d|[ixv])+)\.(\d|[ixv]) )?.*(?:$)"
    for match in reversed(list(re.finditer(pattern, generation, flags=re.I | re.M))):
        start, stop = match.span()
        delim = match.group(3) + " "
        splits = match.group(0).split(delim)
        replacement = ""
        if match.group(1) is not None:
            splits = splits[1:]
            delim1 = match.group(1) + " "
        else:
            delim1 = ""
            continue
        pre, post = generation[:start], generation[stop:]
        for i, item in enumerate(splits):
            level = 0
            potential_numeral, _, rest = item.strip().partition(" ")
            if not rest: continue
            if re.match(r"^[\dixv]+((?:\.[\dixv])?)+$", potential_numeral, flags=re.I | re.M): level = potential_numeral.count(".")
            replacement += (("\n" if i > 0 else "") + ("\t" * level) + (delim if i > 0 or start == 0 else delim1) + item.strip())
        if post == "": post = "\n"
        generation = pre + replacement + post
    return generation
def find_next_punctuation(text: str, start_idx=0):
    for i in range(start_idx, len(text)):
        if text[i] in [".", "?", "!", "\n"]: return i
    return None
def truncate_repetitions(text: str, min_len: int = 30) -> str:
    text_lower = text.lower()
    text_length = len(text_lower)
    if text_length < 2 * min_len: return text
    max_repetition_length = None
    for repetition_length in range(min_len, int(text_length / 2)):
        same = True
        for i in range(0, repetition_length):
            if text_lower[text_length - repetition_length - i - 1] != text_lower[text_length - i - 1]:
                same = False
                break
        if same: max_repetition_length = repetition_length
    if max_repetition_length is None: return text
    lcs = text_lower[-max_repetition_length:]
    substituted_text = text
    substituted_text_lower = text_lower
    while substituted_text_lower.endswith(lcs):
        substituted_text = substituted_text[:-max_repetition_length]
        substituted_text_lower = substituted_text_lower[:-max_repetition_length]
    repeating_tail = text_lower[len(substituted_text_lower) :]
    substituted_text_lower_out = substituted_text_lower
    while True:
        sentence_end = find_next_punctuation(text_lower, len(substituted_text_lower_out))
        sentence_start = find_next_punctuation(text_lower[::-1], len(substituted_text_lower_out))
        if sentence_end and sentence_start:
            sentence = text_lower[sentence_start:sentence_end]
            substituted_text_lower_out = text_lower[: sentence_end + 1]
            if sentence in repeating_tail: break
        else: break
    text_out = text[: len(substituted_text_lower_out)]
    return text_out
def remove_numbers(lines):
    def _clean(s): return re.sub(r"(?:[\d_]|\*\*)", "", s).strip()
    if isinstance(lines, str): return _clean(lines)
    out = []
    for l in lines: out.append(_clean(l))
    return out
def get_slices(lines, clean_lines):
    indices = np.zeros(len(lines))
    for i in range(len(lines) - 1):
        j = i + 1
        while not clean_lines[j] and j < len(lines) - 1: j += 1
        if (len(clean_lines[i]) < 200 and len(clean_lines[i]) > 3 and len(clean_lines[j]) < 200 and len(clean_lines[j]) > 3 and not clean_lines[i].startswith("[MISSING_PAGE")
        and (clean_lines[i] == clean_lines[j] or ratio(clean_lines[i], clean_lines[j]) > 0.9)): indices[i:j] = 1
    ids = np.where(indices)[0]
    slices = []
    if len(ids) == 0: return slices
    j0 = 0
    for j, x in enumerate(np.diff(ids) > 3):
        if x:
            slices.append((ids[j0], ids[j] + 2))
            j0 = j + 1
    slices.append((ids[j0], ids[-1] + 2))
    return [sli for sli in slices if sli[1] - sli[0] > 15]
def remove_slice_from_lines(lines, clean_text, slice) -> str:
    base = clean_text[slice[0]]
    section = list(slice)
    check_start_flag = False
    for line_idx in range(max(0, slice[0] - 1), max(0, slice[0] - 5), -1):
        if not lines[line_idx]: continue
        if lines[line_idx] == "## References":
            section[0] = line_idx
            break
        elif ratio(base, remove_numbers(lines[line_idx])) < 0.9:
            section[0] = line_idx + 1
            potential_ref = remove_numbers(lines[max(0, line_idx - 1)].partition("* [")[-1])
            if len(potential_ref) >= 0.75 * len(base) and ratio(base, potential_ref) < 0.9: section[0] = line_idx
            check_start_flag = True
            break
    for line_idx in range(min(len(lines), slice[1]), min(len(lines), slice[1] + 5)):
        if ratio(base, remove_numbers(lines[line_idx])) < 0.9:
            section[1] = line_idx
            break
    if len(lines) <= section[1]: section[1] = len(lines) - 1
    to_delete = "\n".join(lines[section[0] : section[1] + 1])
    itera, iterb = enumerate(lines[section[1] - 1]), enumerate(lines[section[1]])
    while True:
        try:
            (ia, a) = next(itera)
            while a.isnumeric(): (ia, a) = next(itera)
            (ib, b) = next(iterb)
            while b.isnumeric(): (ib, b) = next(iterb)
            if a != b: break
        except StopIteration: break
    if check_start_flag and "* [" in to_delete: to_delete = "* [" + to_delete.partition("* [")[-1]
    try:
        delta = len(lines[section[1]]) - ib - 1
        if delta > 0: to_delete = to_delete[:-delta]
    except UnboundLocalError: pass
    return to_delete.strip()
@add_end_docstrings(INIT_TOKENIZER_DOCSTRING)
class NougatTokenizerFast(PreTrainedTokenizerFast):
    vocab_files_names = VOCAB_FILES_NAMES
    model_input_names = ["input_ids", "attention_mask"]
    slow_tokenizer_class = None
    def __init__(self, vocab_file=None, tokenizer_file=None, clean_up_tokenization_spaces=False, unk_token="<unk>", bos_token="<s>", eos_token="</s>", pad_token="<pad>", **kwargs):
        super().__init__(vocab_file=vocab_file, tokenizer_file=tokenizer_file, clean_up_tokenization_spaces=clean_up_tokenization_spaces, unk_token=unk_token,
        bos_token=bos_token, eos_token=eos_token, pad_token=pad_token, **kwargs)
        self.vocab_file = vocab_file
    def remove_hallucinated_references(self, text: str) -> str:
        lines = text.split("\n")
        if len(lines) == 0: return ""
        clean_lines = remove_numbers(lines)
        slices = get_slices(lines, clean_lines)
        to_delete = []
        for slice in slices: to_delete.append(remove_slice_from_lines(lines, clean_lines, slice))
        for to_delete in reversed(to_delete): text = text.replace(to_delete, "\n\n[MISSING_PAGE_POST]\n\n")
        text = re.sub(r"## References\n+\[MISSING_PAGE_POST(:\d+)?\]", "\n\n[MISSING_PAGE_POST\\1]", text)
        return text
    def correct_tables(self, generation: str) -> str:
        for l in generation.split("\n"):
            if l.count("\\begin{tabular}") > 15 or l.count("\\multicolumn") > 60 or l.count("&") > 400: generation = generation.replace(l, "")
        generation = generation.replace("\\begin{table} \\begin{tabular}", "\\begin{table}\n\\begin{tabular}")
        generation = generation.replace("\\end{tabular} \\end{table}", "\\end{tabular}\n\\end{table}")
        generation = generation.replace("\\end{table} Tab", "\\end{table}\nTab")
        generation = re.sub(r"(^.+)\\begin{tab", r"\1\n\\begin{tab", generation, flags=re.M)
        generation = generation.replace(r"\begin{tabular}{l l}  & \\ \end{tabular}", "")
        generation = generation.replace("\\begin{tabular}{}\n\n\\end{tabular}", "")
        return generation
    def post_process_single(self, generation: str, fix_markdown: bool = True) -> str:
        generation = re.sub(r"(?:\n|^)#+ \d*\W? ?(.{100,})", r"\n\1", generation)
        generation = generation.strip()
        generation = generation.replace("\n* [leftmargin=*]\n", "\n")
        generation = re.sub(r"^#+ (?:\.?(?:\d|[ixv])+)*\s*(?:$|\n\s*)", "", generation, flags=re.M)
        lines = generation.split("\n")
        if lines[-1].startswith("#") and lines[-1].lstrip("#").startswith(" ") and len(lines) > 1:
            logger.info("Likely hallucinated title at the end of the page: " + lines[-1])
            generation = "\n".join(lines[:-1])
        generation = truncate_repetitions(generation)
        generation = self.remove_hallucinated_references(generation)
        generation = re.sub(r"^\* \[\d+\](\s?[A-W]\.+\s?){10,}.*$", "", generation, flags=re.M)
        generation = re.sub(r"^(\* \[\d+\])\[\](.*)$", r"\1\2", generation, flags=re.M)
        generation = re.sub(r"(^\w\n\n|\n\n\w$)", "", generation)
        generation = re.sub(r"([\s.,()])_([a-zA-Z0-9])__([a-zA-Z0-9]){1,3}_([\s.,:()])", r"\1\(\2_{\3}\)\4", generation)
        generation = re.sub(r"([\s.,\d])_([a-zA-Z0-9])_([\s.,\d;])", r"\1\(\2\)\3", generation)
        generation = re.sub(r"(\nFootnote .*?:) (?:footnotetext|thanks):\W*(.*(?:\n\n|$))", r"\1 \2", generation)
        generation = re.sub(r"\[FOOTNOTE:.+?\](.*?)\[ENDFOOTNOTE\]", "", generation)
        generation = normalize_list_like_lines(generation)
        if generation.endswith((".", "}")): generation += "\n\n"
        if re.match(r"[A-Z0-9,;:]$", generation): generation += " "
        elif generation.startswith(("#", "**", "\\begin")): generation = "\n\n" + generation
        elif generation.split("\n")[-1].startswith(("#", "Figure", "Table")): generation = generation + "\n\n"
        else:
            try:
                last_word = generation.split(" ")[-1]
                if last_word in nltk.corpus.words.words(): generation += " "
            except LookupError: generation += " "
        generation = self.correct_tables(generation)
        generation = generation.replace("\\begin{array}[]{", "\\begin{array}{")
        generation = re.sub(r"\\begin{tabular}{([clr ]){2,}}\s*[& ]*\s*(\\\\)? \\end{tabular}", "", generation)
        generation = re.sub(r"(\*\*S\. A\. B\.\*\*\n+){2,}", "", generation)
        generation = re.sub(r"^#+( [\[\d\w])?$", "", generation, flags=re.M)
        generation = re.sub(r"^\.\s*$", "", generation, flags=re.M)
        generation = re.sub(r"\n{3,}", "\n\n", generation)
        if fix_markdown: return markdown_compatible(generation)
        else: return generation
    def post_process_generation(self, generation: Union[str, List[str]], fix_markdown: bool = True, num_workers: int = None) -> Union[str, List[str]]:
        requires_backends(self, ["nltk", "levenshtein"])
        if isinstance(generation, list):
            if num_workers is not None and isinstance(num_workers, int):
                with Pool(num_workers) as p: return p.map(partial(self.post_process_single, fix_markdown=fix_markdown), generation)
            else: return [self.post_process_single(s, fix_markdown=fix_markdown) for s in generation]
        else: return self.post_process_single(generation, fix_markdown=fix_markdown)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
