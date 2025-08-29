'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import re
def replace_example_docstring(example_docstring):
    def docstring_decorator(fn):
        func_doc = fn.__doc__
        lines = func_doc.split('\n')
        i = 0
        while i < len(lines) and re.search('^\\s*Examples?:\\s*$', lines[i]) is None: i += 1
        if i < len(lines):
            lines[i] = example_docstring
            func_doc = '\n'.join(lines)
        else: raise ValueError(f"The function {fn} should have an empty 'Examples:' in its docstring as placeholder, current docstring is:\n{func_doc}")
        fn.__doc__ = func_doc
        return fn
    return docstring_decorator
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
