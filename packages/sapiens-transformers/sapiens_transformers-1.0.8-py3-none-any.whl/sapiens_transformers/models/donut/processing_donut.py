"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import re
import warnings
from contextlib import contextmanager
from ...processing_utils import ProcessorMixin
class DonutProcessor(ProcessorMixin):
    attributes = ["image_processor", "tokenizer"]
    image_processor_class = "AutoImageProcessor"
    tokenizer_class = "AutoTokenizer"
    def __init__(self, image_processor=None, tokenizer=None, **kwargs):
        feature_extractor = None
        if "feature_extractor" in kwargs:
            warnings.warn("The `feature_extractor` argument is deprecated and will be removed in v5, use `image_processor` instead.", FutureWarning)
            feature_extractor = kwargs.pop("feature_extractor")
        image_processor = image_processor if image_processor is not None else feature_extractor
        if image_processor is None: raise ValueError("You need to specify an `image_processor`.")
        if tokenizer is None: raise ValueError("You need to specify a `tokenizer`.")
        super().__init__(image_processor, tokenizer)
        self.current_processor = self.image_processor
        self._in_target_context_manager = False
    def __call__(self, *args, **kwargs):
        if self._in_target_context_manager: return self.current_processor(*args, **kwargs)
        images = kwargs.pop("images", None)
        text = kwargs.pop("text", None)
        if len(args) > 0:
            images = args[0]
            args = args[1:]
        if images is None and text is None: raise ValueError("You need to specify either an `images` or `text` input to process.")
        if images is not None: inputs = self.image_processor(images, *args, **kwargs)
        if text is not None: encodings = self.tokenizer(text, **kwargs)
        if text is None: return inputs
        elif images is None: return encodings
        else:
            inputs["labels"] = encodings["input_ids"]
            return inputs
    def batch_decode(self, *args, **kwargs): return self.tokenizer.batch_decode(*args, **kwargs)
    def decode(self, *args, **kwargs): return self.tokenizer.decode(*args, **kwargs)
    @contextmanager
    def as_target_processor(self):
        warnings.warn("`as_target_processor` is deprecated and will be removed in v1 of Sapiens Transformers. You can process your labels by using the argument `text` of the regular `__call__` method (either in the same call as your images inputs, or in a separate call.")
        self._in_target_context_manager = True
        self.current_processor = self.tokenizer
        yield
        self.current_processor = self.image_processor
        self._in_target_context_manager = False
    def token2json(self, tokens, is_inner_value=False, added_vocab=None):
        if added_vocab is None: added_vocab = self.tokenizer.get_added_vocab()
        output = {}
        while tokens:
            start_token = re.search(r"<s_(.*?)>", tokens, re.IGNORECASE)
            if start_token is None: break
            key = start_token.group(1)
            key_escaped = re.escape(key)
            end_token = re.search(rf"</s_{key_escaped}>", tokens, re.IGNORECASE)
            start_token = start_token.group()
            if end_token is None: tokens = tokens.replace(start_token, "")
            else:
                end_token = end_token.group()
                start_token_escaped = re.escape(start_token)
                end_token_escaped = re.escape(end_token)
                content = re.search(f"{start_token_escaped}(.*?){end_token_escaped}", tokens, re.IGNORECASE | re.DOTALL)
                if content is not None:
                    content = content.group(1).strip()
                    if r"<s_" in content and r"</s_" in content:
                        value = self.token2json(content, is_inner_value=True, added_vocab=added_vocab)
                        if value:
                            if len(value) == 1: value = value[0]
                            output[key] = value
                    else:
                        output[key] = []
                        for leaf in content.split(r"<sep/>"):
                            leaf = leaf.strip()
                            if leaf in added_vocab and leaf[0] == "<" and leaf[-2:] == "/>": leaf = leaf[1:-2]
                            output[key].append(leaf)
                        if len(output[key]) == 1: output[key] = output[key][0]
                tokens = tokens[tokens.find(end_token) + len(end_token) :].strip()
                if tokens[:6] == r"<sep/>": return [output] + self.token2json(tokens[6:], is_inner_value=True, added_vocab=added_vocab)
        if len(output): return [output] if is_inner_value else output
        else: return [] if is_inner_value else {"text_sequence": tokens}
    @property
    def feature_extractor_class(self):
        warnings.warn("`feature_extractor_class` is deprecated and will be removed in v5. Use `image_processor_class` instead.", FutureWarning)
        return self.image_processor_class
    @property
    def feature_extractor(self):
        warnings.warn("`feature_extractor` is deprecated and will be removed in v5. Use `image_processor` instead.", FutureWarning)
        return self.image_processor
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
