from dataclasses import dataclass


@dataclass
class StreamResponse:
    role: str
    content: str
    tool_calls: list[dict]


@dataclass
class LLMResponse:
    role: str
    content: str
    tool_calls: list[dict]
