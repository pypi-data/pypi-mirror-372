"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import re
import requests
from requests.exceptions import RequestException
from .tools import Tool
class DuckDuckGoSearchTool(Tool):
    name = "web_search"
    description = """Perform a web search based on your query (think a Google search) then returns the top search results as a list of dict elements.
    Each result has keys 'title', 'href' and 'body'."""
    inputs = {"query": {"type": "string", "description": "The search query to perform."}}
    output_type = "any"
    def forward(self, query: str) -> str:
        try: from duckduckgo_search import DDGS
        except ImportError: raise ImportError("You must install package `duckduckgo_search` to run this tool: for instance run `pip install duckduckgo-search`.")
        results = DDGS().text(query, max_results=7)
        return results
class VisitWebpageTool(Tool):
    name = "visit_webpage"
    description = "Visits a wbepage at the given url and returns its content as a markdown string."
    inputs = {"url": {'type': 'string', 'description': 'The url of the webpage to visit.'}}
    output_type = "string"
    def forward(self, url: str) -> str:
        try: from markdownify import markdownify
        except ImportError: raise ImportError("You must install package `markdownify` to run this tool: for instance run `pip install markdownify`.")
        try:
            response = requests.get(url)
            response.raise_for_status()
            markdown_content = markdownify(response.text).strip()
            markdown_content = re.sub(r"\n{3,}", "\n\n", markdown_content)
            return markdown_content
        except RequestException as e: return f"Error fetching the webpage: {str(e)}"
        except Exception as e: return f"An unexpected error occurred: {str(e)}"
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
