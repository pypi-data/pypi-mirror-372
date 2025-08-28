"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from .sapi_audio_import_variables import ADDITIONAL_DIACRITICS, MULTIPLIERS, REPLACERS
from typing import List, Iterator, Optional, Union, Match
import re as sapiens_technology_re
class EnglishNumberNormalizer:
    def __init__(self):
        super().__init__()
        self.ones = {name: i for i, name in enumerate(["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"], start=1)}
        self.ones_plural, self.zeros = {"sixes" if name == "six" else name + "s": (value, "s") for name, value in self.ones.items()}, {"o", "oh", "zero"}
        self.ones_ordinal = {"zeroth": (0, "th"), "first": (1, "st"), "second": (2, "nd"), "third": (3, "rd"), "fifth": (5, "th"), "twelfth": (12, "th"),
        **{name + ("h" if name.endswith("t") else "th"): (value, "th") for name, value in self.ones.items() if value > 3 and value != 5 and value != 12}}
        self.ones_suffixed, self.tens = {**self.ones_plural, **self.ones_ordinal}, {'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50, 'sixty': 60, 'seventy': 70, 'eighty': 80, 'ninety': 90}
        self.tens_plural, self.tens_ordinal = {name.replace("y", "ies"): (value, "s") for name, value in self.tens.items()}, {name.replace("y", "ieth"): (value, "th") for name, value in self.tens.items()}
        self.tens_suffixed, self.multipliers = {**self.tens_plural, **self.tens_ordinal}, MULTIPLIERS
        self.multipliers_plural = {name + "s": (value, "s") for name, value in self.multipliers.items()}
        self.multipliers_ordinal = {name + "th": (value, "th") for name, value in self.multipliers.items()}
        self.multipliers_suffixed, self.decimals = {**self.multipliers_plural, **self.multipliers_ordinal}, {*self.ones, *self.tens, *self.zeros}
        self.preceding_prefixers = {'minus': '-', 'negative': '-', 'plus': '+', 'positive': '+'}
        self.following_prefixers = {'pound': '£', 'pounds': '£', 'euro': '€', 'euros': '€', 'dollar': '$', 'dollars': '$', 'cent': '¢', 'cents': '¢'}
        self.prefixes = set(list(self.preceding_prefixers.values()) + list(self.following_prefixers.values()))
        self.suffixers, self.specials = {"per": {"cent": "%"}, "percent": "%"}, {"and", "double", "triple", "point"}
        self.words = {key for mapping in [self.zeros, self.ones, self.ones_suffixed, self.tens, self.tens_suffixed, self.multipliers, self.multipliers_suffixed,
        self.preceding_prefixers, self.following_prefixers, self.suffixers, self.specials] for key in mapping}
        self.literal_words = {"one", "ones"}
    def process_words(self, words: List[str]) -> Iterator[str]:
        prefix: Optional[str] = None
        value: Optional[Union[str, int]] = None
        skip = False
        def to_fraction(s: str):
            from fractions import Fraction
            try: return Fraction(s)
            except ValueError: return None
        def output(result: Union[str, int]):
            nonlocal prefix, value
            result = str(result)
            if prefix is not None: result = prefix + result
            value, prefix = None, None
            return result
        if len(words) == 0: return
        for i, current in enumerate(words):
            prev, next = words[i - 1] if i != 0 else None, words[i + 1] if i != len(words) - 1 else None
            if skip:
                skip = False
                continue
            next_is_numeric = next is not None and sapiens_technology_re.match(r"^\d+(\.\d+)?$", next)
            has_prefix, current_without_prefix = current[0] in self.prefixes, current[1:] if has_prefix else current
            if sapiens_technology_re.match(r"^\d+(\.\d+)?$", current_without_prefix):
                f = to_fraction(current_without_prefix)
                if f is None: raise ValueError("Converting the fraction failed")
                if value is not None:
                    if isinstance(value, str) and value.endswith("."):
                        value = str(value) + str(current)
                        continue
                    else: yield output(value)
                prefix = current[0] if has_prefix else prefix
                if f.denominator == 1: value = f.numerator
                else: value = current_without_prefix
            elif current not in self.words:
                if value is not None: yield output(value)
                yield output(current)
            elif current in self.zeros: value = str(value or "") + "0"
            elif current in self.ones:
                ones = self.ones[current]
                if value is None: value = ones
                elif isinstance(value, str) or prev in self.ones:
                    if prev in self.tens and ones < 10: value = value[:-1] + str(ones)
                    else: value = str(value) + str(ones)
                elif ones < 10:
                    if value % 10 == 0: value += ones
                    else: value = str(value) + str(ones)
                else:
                    if value % 100 == 0: value += ones
                    else: value = str(value) + str(ones)
            elif current in self.ones_suffixed:
                ones, suffix = self.ones_suffixed[current]
                if value is None: yield output(str(ones) + suffix)
                elif isinstance(value, str) or prev in self.ones:
                    if prev in self.tens and ones < 10: yield output(value[:-1] + str(ones) + suffix)
                    else: yield output(str(value) + str(ones) + suffix)
                elif ones < 10:
                    if value % 10 == 0: yield output(str(value + ones) + suffix)
                    else: yield output(str(value) + str(ones) + suffix)
                else:
                    if value % 100 == 0: yield output(str(value + ones) + suffix)
                    else: yield output(str(value) + str(ones) + suffix)
                value = None
            elif current in self.tens:
                tens = self.tens[current]
                if value is None: value = tens
                elif isinstance(value, str): value = str(value) + str(tens)
                else:
                    if value % 100 == 0: value += tens
                    else: value = str(value) + str(tens)
            elif current in self.tens_suffixed:
                tens, suffix = self.tens_suffixed[current]
                if value is None: yield output(str(tens) + suffix)
                elif isinstance(value, str): yield output(str(value) + str(tens) + suffix)
                else:
                    if value % 100 == 0: yield output(str(value + tens) + suffix)
                    else: yield output(str(value) + str(tens) + suffix)
            elif current in self.multipliers:
                multiplier = self.multipliers[current]
                if value is None: value = multiplier
                elif isinstance(value, str) or value == 0:
                    f = to_fraction(value)
                    p = f * multiplier if f is not None else None
                    if f is not None and p.denominator == 1: value = p.numerator
                    else:
                        yield output(value)
                        value = multiplier
                else:
                    before, residual = value // 1000 * 1000, value % 1000
                    value = before + residual * multiplier
            elif current in self.multipliers_suffixed:
                multiplier, suffix = self.multipliers_suffixed[current]
                if value is None: yield output(str(multiplier) + suffix)
                elif isinstance(value, str):
                    f = to_fraction(value)
                    p = f * multiplier if f is not None else None
                    if f is not None and p.denominator == 1: yield output(str(p.numerator) + suffix)
                    else:
                        yield output(value)
                        yield output(str(multiplier) + suffix)
                else:
                    before, residual = value // 1000 * 1000, value % 1000
                    value = before + residual * multiplier
                    yield output(str(value) + suffix)
                value = None
            elif current in self.preceding_prefixers:
                if value is not None: yield output(value)
                if next in self.words or next_is_numeric: prefix = self.preceding_prefixers[current]
                else: yield output(current)
            elif current in self.following_prefixers:
                if value is not None:
                    prefix = self.following_prefixers[current]
                    yield output(value)
                else: yield output(current)
            elif current in self.suffixers:
                if value is not None:
                    suffix = self.suffixers[current]
                    if isinstance(suffix, dict):
                        if next in suffix:
                            yield output(str(value) + suffix[next])
                            skip = True
                        else:
                            yield output(value)
                            yield output(current)
                    else: yield output(str(value) + suffix)
                else: yield output(current)
            elif current in self.specials:
                if next not in self.words and not next_is_numeric:
                    if value is not None: yield output(value)
                    yield output(current)
                elif current == "and":
                    if prev not in self.multipliers:
                        if value is not None: yield output(value)
                        yield output(current)
                elif current == "double" or current == "triple":
                    if next in self.ones or next in self.zeros: value, skip = str(value or "") + str(self.ones.get(next, 0)) * (2 if current == "double" else 3), True
                    else:
                        if value is not None: yield output(value)
                        yield output(current)
                elif current == "point":
                    if next in self.decimals or next_is_numeric: value = str(value or "") + "."
                else: raise ValueError(f"Unexpected token: {current}")
            else: raise ValueError(f"Unexpected token: {current}")
        if value is not None: yield output(value)
    def preprocess(self, s: str):
        segments, results = sapiens_technology_re.split(r"\band\s+a\s+half\b", s), []
        for i, segment in enumerate(segments):
            if len(segment.strip()) == 0: continue
            if i == len(segments) - 1: results.append(segment)
            else:
                results.append(segment)
                last_word = segment.rsplit(maxsplit=2)[-1]
                if last_word in self.decimals or last_word in self.multipliers: results.append("point five")
                else: results.append("and a half")
        return sapiens_technology_re.sub(r"([0-9])\s+(st|nd|rd|th|s)\b", r"\1\2", sapiens_technology_re.sub(r"([0-9])([a-z])", r"\1 \2", sapiens_technology_re.sub(r"([a-z])([0-9])", r"\1 \2", " ".join(results))))
    def postprocess(self, s: str):
        def combine_cents(m: Match):
            try: return f"{m.group(1)}{m.group(2)}.{int(m.group(3)):02d}"
            except ValueError: return m.string
        def extract_cents(m: Match):
            try: return f"¢{int(m.group(1))}"
            except ValueError: return m.string
        return sapiens_technology_re.sub(r"\b1(s?)\b", r"one\1", sapiens_technology_re.sub(r"[€£$]0.([0-9]{1,2})\b", extract_cents, sapiens_technology_re.sub(r"([€£$])([0-9]+) (?:and )?¢([0-9]{1,2})\b", combine_cents, s)))
    def __call__(self, s: str): return self.postprocess(" ".join(word for word in self.process_words(self.preprocess(s).split()) if word is not None))
class EnglishSpellingNormalizer:
    def __init__(self, english_spelling_mapping): self.mapping = english_spelling_mapping
    def __call__(self, s: str): return " ".join(self.mapping.get(word, word) for word in s.split())
import unicodedata
def remove_symbols_and_diacritics(s: str, keep=""):
    def replace_character(char):
        if char in keep: return char
        elif char in ADDITIONAL_DIACRITICS: return ADDITIONAL_DIACRITICS[char]
        elif unicodedata.category(char) == "Mn": return ""
        elif unicodedata.category(char)[0] in "MSP": return " "
        return char
    return "".join(replace_character(c) for c in unicodedata.normalize("NFKD", s))
class BasicTextNormalizer:
    def __init__(self, remove_diacritics: bool = False, split_letters: bool = False):
        def remove_symbols(s: str): return "".join(" " if unicodedata.category(c)[0] in "MSP" else c for c in unicodedata.normalize("NFKC", s))
        self.clean, self.split_letters = remove_symbols_and_diacritics if remove_diacritics else remove_symbols, split_letters
    def __call__(self, s: str):
        s = self.clean(sapiens_technology_re.sub(r"\(([^)]+?)\)", "", sapiens_technology_re.sub(r"[<\[][^>\]]*[>\]]", "", s.lower()))).lower()
        import regex as sapiens_technology_regex
        if self.split_letters: s = " ".join(sapiens_technology_regex.findall(r"\X", s, sapiens_technology_regex.U))
        return sapiens_technology_re.sub(r"\s+", " ", s)
class EnglishTextNormalizer:
    def __init__(self, english_spelling_mapping):
        self.ignore_patterns, self.replacers = r"\b(hmm|mm|mhm|mmm|uh|um)\b", REPLACERS
        self.standardize_numbers, self.standardize_spellings = EnglishNumberNormalizer(), EnglishSpellingNormalizer(english_spelling_mapping)
    def __call__(self, s: str):
        s = sapiens_technology_re.sub(r"\s+'", "'", sapiens_technology_re.sub(self.ignore_patterns, "", sapiens_technology_re.sub(r"\(([^)]+?)\)", "", sapiens_technology_re.sub(r"[<\[][^>\]]*[>\]]", "", s.lower()))))
        for pattern, replacement in self.replacers.items(): s = sapiens_technology_re.sub(pattern, replacement, s)
        s = remove_symbols_and_diacritics(sapiens_technology_re.sub(r"\.([^0-9]|$)", r" \1", sapiens_technology_re.sub(r"(\d),(\d)", r"\1\2", s)), keep=".%$¢€£")
        return sapiens_technology_re.sub(r"\s+", " ", sapiens_technology_re.sub(r"([^0-9])%", r"\1 ", sapiens_technology_re.sub(r"[.$¢€£]([^0-9])", r" \1", self.standardize_spellings(self.standardize_numbers(s)))))
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
