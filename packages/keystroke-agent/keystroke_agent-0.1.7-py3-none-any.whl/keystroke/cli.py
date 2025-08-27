import asyncio

from rich.console import Console
from rich.prompt import Prompt

from keystroke.agent import Agent
from keystroke.settings import HISTORY_LIMIT


def _handle_dot_commands(agent: Agent, console: Console, input_text: str) -> None:
    parts = input_text.lower().split()
    base_cmd = parts[0]
    if base_cmd == ".help":
        console.print("[bold blue]Available commands:[/bold blue]")
        console.print("  .help - Show this help message")
        console.print("  .clear - Clear the conversation history")
        console.print("  .model <model_name> - Change the LLM model")
        console.print("  .view - View current settings")
        console.print("  .system <message> - Change the system message")
        console.print("  .name <new_name> - Change the assistant's name")
    elif base_cmd == ".clear":
        agent.history = []
        console.print("[italic]Conversation history cleared.[/italic]")
    elif base_cmd == ".model" and len(parts) > 1:
        new_model = " ".join(parts[1:])
        agent.llm_model = new_model
        console.print(f"[italic]Model changed to: {new_model}[/italic]")
    elif base_cmd == ".view":
        if len(parts) == 1:
            console.print("[bold blue]Current settings:[/bold blue]")
            console.print(f"  Model: {agent.llm_model}")
            console.print(f"  System message: {agent.sys_msg['content']}")
            console.print(
                f"  History length: {len(agent.history)} messages (limit: {HISTORY_LIMIT})"
            )
            console.print(f"  Assistant name: {agent.name}")
        if len(parts) == 2 and parts[1] == "history":
            console.print("[bold blue]Conversation history:[/bold blue]")
            for msg in agent.history:
                console.print(f"  {msg['role']}: {msg['content']}")
    elif base_cmd == ".system" and len(parts) > 1:
        new_system = " ".join(parts[1:])
        agent.sys_msg = {"role": "system", "content": new_system}
        console.print("[italic]System message updated.[/italic]")
    elif base_cmd == ".name" and len(parts) > 1:
        new_name = " ".join(parts[1:])
        agent.name = new_name.capitalize()
        console.print(f"[italic]Assistant name changed to: {agent.name}[/italic]")


async def cli() -> None:
    agent = Agent()
    console = Console()
    console.print(
        f"[bold green]{agent.name}:[/bold green] Hello! How can I assist you today?"
    )
    while True:
        input_text = Prompt.ask("[bold blue]You:[/bold blue]")
        if input_text.lower() in ["exit", "quit", "q"]:
            console.print("Exiting...")
            return
        if input_text.startswith("."):
            _handle_dot_commands(agent, console, input_text)
            continue
        console.print(f"[bold green]{agent.name}:[/bold green]:", end="")
        async for data in agent.run(input_text):
            console.print(data, end="")
        console.print()


if __name__ == "__main__":
    asyncio.run(cli())
