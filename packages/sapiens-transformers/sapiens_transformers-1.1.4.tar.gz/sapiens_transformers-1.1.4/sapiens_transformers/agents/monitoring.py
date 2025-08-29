"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from .agent_types import AgentAudio, AgentImage, AgentText
from .agents import ReactAgent
def pull_message(step_log: dict):
    try: from gradio import ChatMessage
    except ImportError: raise ImportError("Gradio should be installed in order to launch a gradio demo.")
    if step_log.get("rationale"): yield ChatMessage(role="assistant", content=step_log["rationale"])
    if step_log.get("tool_call"):
        used_code = step_log["tool_call"]["tool_name"] == "code interpreter"
        content = step_log["tool_call"]["tool_arguments"]
        if used_code: content = f"```py\n{content}\n```"
        yield ChatMessage(role="assistant", metadata={"title": f"🛠️ Used tool {step_log['tool_call']['tool_name']}"}, content=str(content))
    if step_log.get("observation"): yield ChatMessage(role="assistant", content=f"```\n{step_log['observation']}\n```")
    if step_log.get("error"): yield ChatMessage(role="assistant", content=str(step_log["error"]), metadata={"title": "💥 Error"})
def stream_to_gradio(agent: ReactAgent, task: str, **kwargs):
    try: from gradio import ChatMessage
    except ImportError: raise ImportError("Gradio should be installed in order to launch a gradio demo.")
    for step_log in agent.run(task, stream=True, **kwargs):
        if isinstance(step_log, dict):
            for message in pull_message(step_log): yield message
    if isinstance(step_log, AgentText): yield ChatMessage(role="assistant", content=f"**Final answer:**\n```\n{step_log.to_string()}\n```")
    elif isinstance(step_log, AgentImage): yield ChatMessage(role="assistant", content={"path": step_log.to_string(), "mime_type": "image/png"})
    elif isinstance(step_log, AgentAudio): yield ChatMessage(role="assistant", content={"path": step_log.to_string(), "mime_type": "audio/wav"})
    else: yield ChatMessage(role="assistant", content=str(step_log))
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
