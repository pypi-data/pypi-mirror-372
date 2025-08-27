import asyncio
import json
from typing import Dict, List, Optional

import litellm

from keystroke.events import Event, EventType
from keystroke.settings import MAX_TOKENS
from keystroke.tools import TOOLS_MAP
from keystroke.utils import build_content, reformat

litellm.suppress_debug_info = True

async def llm_response(
    messages: List[Dict[str, str]], llm_model: str, queue: asyncio.Queue,
    tools: Optional[List[Dict]] = None,
    stream: bool = True
) -> dict:
    try:
        _response = await litellm.acompletion(
        model=llm_model, messages=messages, max_tokens=MAX_TOKENS, tools=tools, stream=stream)
    except Exception as e:
        error_msg = f"[LLM Error: {str(e)}]"
        await queue.put(Event(type=EventType.ERROR, content=error_msg))
        return {"role": "assistant", "content": error_msg, "tool_calls": None}
    if stream:
        chunks = []
        async for chunk in _response:
            _reformated = reformat(chunk)
            chunks.append(_reformated)
            await queue.put(Event(type=EventType.LLM_CHUNK, content=_reformated["content"]))
        response = build_content(chunks)
    else:
        response = _response["choices"][0]["message"]
    return response


async def tool_response(message: dict, queue: asyncio.Queue) -> dict:
    tool_call_text = ""
    tool_return_text = ""
    for tool_call in message["tool_calls"]:
        tool_name = tool_call["function"]["name"]
        tool_args = tool_call["function"]["arguments"]
        if isinstance(tool_args, str):
            tool_args = json.loads(tool_args)
        tool_call_text = f"[Calling tool {tool_name} with args {tool_args}]"
        await queue.put(Event(type=EventType.TOOL_CALL, content=tool_call_text))
        try:
            result = TOOLS_MAP[tool_name](**tool_args)
            tool_return_text = f"[Tool {tool_name} returned: {result}]"
        except Exception as e:
            tool_return_text = f"[Tool {tool_name} failed: {str(e)}]"
        await queue.put(Event(type=EventType.TOOL_RESPONSE, content=tool_return_text))
    msg_content = tool_call_text + "\n" + tool_return_text
    return {"role": "user", "content": msg_content}
