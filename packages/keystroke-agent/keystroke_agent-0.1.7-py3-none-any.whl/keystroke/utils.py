import json
from typing import Any


def reformat(chunk: Any) -> dict | None: # noqa
    tool_calls = []
    if not hasattr(chunk, "choices") or not chunk.choices:
        return None
    delta = chunk.choices[0].delta
    if delta.content:
        delta_content = delta.content
    else:
        delta_content = ""
    if hasattr(delta, "tool_calls") and delta.tool_calls:
        for tool_call in delta.tool_calls:
            tool_calls.append(
                {
                    "id": tool_call.id,
                    "index": tool_call.index,
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments,
                    },
                }
            )
    return {"role": "assistant", "content": delta_content, "tool_calls": tool_calls}


def build_content(chunks: list[dict]) -> dict:
    content = ""
    tool_calls_map = {}

    for chunk in chunks:
        if not chunk:
            continue

        if chunk["content"]:
            content += chunk["content"]

        for tool_call in chunk["tool_calls"]:
            idx = tool_call["index"]
            if idx not in tool_calls_map:
                tool_calls_map[idx] = {
                    "id": tool_call.get("id", ""),
                    "index": idx,
                    "function": {
                        "name": tool_call["function"].get("name", ""),
                        "arguments": tool_call["function"].get("arguments", ""),
                    },
                }
            else:
                current_tool = tool_calls_map[idx]
                if "id" in tool_call and tool_call["id"]:
                    current_tool["id"] = tool_call["id"]
                if "name" in tool_call["function"] and tool_call["function"]["name"]:
                    current_tool["function"]["name"] = tool_call["function"]["name"]
                if "arguments" in tool_call["function"] and tool_call["function"]["arguments"]:
                    current_tool["function"]["arguments"] += tool_call["function"]["arguments"]

    tool_calls = [
        {
            "id": tool["id"],
            "function": {
                "name": tool["function"]["name"],
                "arguments": json.loads(tool["function"]["arguments"]),
            },
        }
        for tool in tool_calls_map.values()
    ]

    return {"role": "assistant", "content": content, "tool_calls": tool_calls}
