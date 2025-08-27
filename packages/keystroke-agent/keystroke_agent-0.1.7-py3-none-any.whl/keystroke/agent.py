import asyncio
import warnings
from typing import AsyncGenerator

from keystroke.events import Event, EventType
from keystroke.llm_tools import llm_response, tool_response
from keystroke.settings import (
    AGENT_NAME,
    DEFAULT_LLM_MODEL,
    DEFAULT_SYSTEM_MESSAGE,
    ENABLE_TOOLS,
    HISTORY_LIMIT,
)
from keystroke.tools import TOOLS

# Ignore warnings
warnings.filterwarnings("ignore")


class Agent:
    def __init__(self, name:str=AGENT_NAME) -> None:
        self.name = name
        self.history: list[dict] = []
        self.sys_msg = {"role": "system", "content": DEFAULT_SYSTEM_MESSAGE}
        self.llm_model = DEFAULT_LLM_MODEL
        self.tools_schema = TOOLS if ENABLE_TOOLS else None
        self.queue: asyncio.Queue[Event] = asyncio.Queue()

    async def run(self, prompt: str, ctx: dict|None = None) -> AsyncGenerator[str, None]:
        msg = {"role": "user", "content": prompt}
        self.history.append(msg)
        asyncio.create_task(self.call_llm())
        while True:
            event = await self.queue.get()
            if event.type == EventType.END:
                break
            if event.type in [EventType.TOOL_CALL, EventType.TOOL_RESPONSE]:
                yield "\n" + event.content + "\n"
            else:
                yield event.content

    async def call_llm(self) -> dict:
        msg = await llm_response(self.history, self.llm_model, self.queue, tools=self.tools_schema)
        if msg["content"]:
            self.history.append({"role": "assistant", "content": msg["content"]})
        return await self.call_controller(msg)

    async def call_tool(self, msg: dict) -> dict:
        result = await tool_response(msg, self.queue)
        self.history.append(result)
        return await self.call_llm()

    async def call_controller(self, msg: dict) -> dict:
        if msg.get("tool_calls"):
            return await self.call_tool(msg)
        return await self.summarize_history()

    async def summarize_history(self) -> dict:
        if len(self.history) > HISTORY_LIMIT:
            prompt = [{"role": "user", "content": "Summarize the conversation in a concise manner"}]
            msg = prompt + self.history[:-3]
            summary = await llm_response(msg, self.llm_model, self.queue, stream=False)
            self.history = [{"role": "user", "content": summary["content"]}] + self.history[-3:]
        await self.queue.put(Event(type=EventType.END, content=""))
        return self.history[-1]
