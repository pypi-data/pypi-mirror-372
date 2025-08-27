from dataclasses import dataclass
from enum import Enum
from typing import Any


class EventType(Enum):
    START = "START"
    LLM_CALL = "LLM_CALL"
    LLM_CHUNK = "LLM_CHUNK"
    LLM_RESPONSE = "LLM_RESPONSE"
    TOOL_CALL = "TOOL_CALL"
    TOOL_RESPONSE = "TOOL_RESPONSE"
    END = "END"
    ERROR = "ERROR"


@dataclass
class Event:
    type: EventType
    content: str
