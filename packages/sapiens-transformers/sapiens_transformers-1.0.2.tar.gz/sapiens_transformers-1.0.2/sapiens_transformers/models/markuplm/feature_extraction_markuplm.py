"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import html
from ...feature_extraction_utils import BatchFeature, FeatureExtractionMixin
from ...utils import is_bs4_available, logging, requires_backends
if is_bs4_available():
    import bs4
    from bs4 import BeautifulSoup
logger = logging.get_logger(__name__)
class MarkupLMFeatureExtractor(FeatureExtractionMixin):
    def __init__(self, **kwargs):
        requires_backends(self, ["bs4"])
        super().__init__(**kwargs)
    def xpath_soup(self, element):
        xpath_tags = []
        xpath_subscripts = []
        child = element if element.name else element.parent
        for parent in child.parents:
            siblings = parent.find_all(child.name, recursive=False)
            xpath_tags.append(child.name)
            xpath_subscripts.append(0 if 1 == len(siblings) else next(i for i, s in enumerate(siblings, 1) if s is child))
            child = parent
        xpath_tags.reverse()
        xpath_subscripts.reverse()
        return xpath_tags, xpath_subscripts
    def get_three_from_single(self, html_string):
        html_code = BeautifulSoup(html_string, "html.parser")
        all_doc_strings = []
        string2xtag_seq = []
        string2xsubs_seq = []
        for element in html_code.descendants:
            if isinstance(element, bs4.element.NavigableString):
                if type(element.parent) is not bs4.element.Tag: continue
                text_in_this_tag = html.unescape(element).strip()
                if not text_in_this_tag: continue
                all_doc_strings.append(text_in_this_tag)
                xpath_tags, xpath_subscripts = self.xpath_soup(element)
                string2xtag_seq.append(xpath_tags)
                string2xsubs_seq.append(xpath_subscripts)
        if len(all_doc_strings) != len(string2xtag_seq): raise ValueError("Number of doc strings and xtags does not correspond")
        if len(all_doc_strings) != len(string2xsubs_seq): raise ValueError("Number of doc strings and xsubs does not correspond")
        return all_doc_strings, string2xtag_seq, string2xsubs_seq
    def construct_xpath(self, xpath_tags, xpath_subscripts):
        xpath = ""
        for tagname, subs in zip(xpath_tags, xpath_subscripts):
            xpath += f"/{tagname}"
            if subs != 0: xpath += f"[{subs}]"
        return xpath
    def __call__(self, html_strings) -> BatchFeature:
        valid_strings = False
        if isinstance(html_strings, str): valid_strings = True
        elif isinstance(html_strings, (list, tuple)):
            if len(html_strings) == 0 or isinstance(html_strings[0], str): valid_strings = True
        if not valid_strings: raise ValueError(f"HTML strings must of type `str`, `List[str]` (batch of examples), but is of type {type(html_strings)}.")
        is_batched = bool(isinstance(html_strings, (list, tuple)) and (isinstance(html_strings[0], str)))
        if not is_batched: html_strings = [html_strings]
        nodes = []
        xpaths = []
        for html_string in html_strings:
            all_doc_strings, string2xtag_seq, string2xsubs_seq = self.get_three_from_single(html_string)
            nodes.append(all_doc_strings)
            xpath_strings = []
            for node, tag_list, sub_list in zip(all_doc_strings, string2xtag_seq, string2xsubs_seq):
                xpath_string = self.construct_xpath(tag_list, sub_list)
                xpath_strings.append(xpath_string)
            xpaths.append(xpath_strings)
        data = {"nodes": nodes, "xpaths": xpaths}
        encoded_inputs = BatchFeature(data=data, tensor_type=None)
        return encoded_inputs
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
