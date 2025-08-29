from __future__ import annotations
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import sys
import traceback
import time
from re import compile, Match, Pattern
from typing import Callable, Coroutine, Optional, Tuple, Union, Dict
from typing_extensions import TypedDict
from fastapi import (Request, Response, HTTPException)
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from .types import (CreateCompletionRequest, CreateEmbeddingRequest, CreateChatCompletionRequest)
class ErrorResponse(TypedDict):
    message: str
    type: str
    param: Optional[str]
    code: Optional[str]
class ErrorResponseFormatters:
    @staticmethod
    def context_length_exceeded(request: Union["CreateCompletionRequest", "CreateChatCompletionRequest"], match) -> Tuple[int, ErrorResponse]:
        context_window = int(match.group(2))
        prompt_tokens = int(match.group(1))
        completion_tokens = request.max_tokens
        if hasattr(request, "messages"): message = ("This model's maximum context length is {} tokens. However, you requested {} tokens ({} in the messages, {} in the completion). Please reduce the length of the messages or completion.")
        else: message = ("This model's maximum context length is {} tokens, however you requested {} tokens ({} in your prompt; {} for the completion). Please reduce your prompt; or completion length.")
        return 400, ErrorResponse(message=message.format(context_window, (completion_tokens or 0) + prompt_tokens, prompt_tokens, completion_tokens),
        type="invalid_request_error", param="messages", code="context_length_exceeded")
    @staticmethod
    def model_not_found(request: Union["CreateCompletionRequest", "CreateChatCompletionRequest"], match) -> Tuple[int, ErrorResponse]:
        model_path = str(match.group(1))
        message = f"The model `{model_path}` does not exist"
        return 400, ErrorResponse(message=message, type="invalid_request_error", param=None, code="model_not_found")
class RouteErrorHandler(APIRoute):
    pattern_and_formatters: Dict["Pattern[str]", Callable[[Union["CreateCompletionRequest", "CreateChatCompletionRequest"], "Match[str]"], Tuple[int, ErrorResponse]]] = {
    compile(r"Requested tokens \((\d+)\) exceed context window of (\d+)"): ErrorResponseFormatters.context_length_exceeded,
    compile(r"Model path does not exist: (.+)"): ErrorResponseFormatters.model_not_found}
    def error_message_wrapper(self, error: Exception, body: Optional[Union["CreateChatCompletionRequest", "CreateCompletionRequest", "CreateEmbeddingRequest"]] = None) -> Tuple[int, ErrorResponse]:
        if body is not None and isinstance(body, (CreateCompletionRequest, CreateChatCompletionRequest)):
            for pattern, callback in self.pattern_and_formatters.items():
                match = pattern.search(str(error))
                if match is not None: return callback(body, match)
        print(f"Exception: {str(error)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return 500, ErrorResponse(message=str(error), type="internal_server_error", param=None, code=None)
    def get_route_handler(self) -> Callable[[Request], Coroutine[None, None, Response]]:
        original_route_handler = super().get_route_handler()
        async def custom_route_handler(request: Request) -> Response:
            try:
                start_sec = time.perf_counter()
                response = await original_route_handler(request)
                elapsed_time_ms = int((time.perf_counter() - start_sec) * 1000)
                response.headers["openai-processing-ms"] = f"{elapsed_time_ms}"
                return response
            except HTTPException as unauthorized: raise unauthorized
            except Exception as exc:
                json_body = await request.json()
                try:
                    if "messages" in json_body:
                        body: Optional[Union[CreateChatCompletionRequest, CreateCompletionRequest, CreateEmbeddingRequest]] = CreateChatCompletionRequest(**json_body)
                    elif "prompt" in json_body: body = CreateCompletionRequest(**json_body)
                    else: body = CreateEmbeddingRequest(**json_body)
                except Exception: body = None
                (status_code, error_message) = self.error_message_wrapper(error=exc, body=body)
                return JSONResponse({"error": error_message}, status_code=status_code)
        return custom_route_handler
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
