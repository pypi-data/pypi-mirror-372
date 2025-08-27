import importlib
import inspect
import sys
from pathlib import Path

from litellm.utils import function_to_dict

from keystroke.settings import DISABLED_TOOLS


def get_all_tool_functions(skip: list[str] = []):
    """Get all functions from modules in the tools directory."""
    # Get the directory where this file is located
    tools_dir = Path(__file__).parent.absolute()

    # Add the tools directory to sys.path to help with imports
    if str(tools_dir) not in sys.path:
        sys.path.append(str(tools_dir))

    tool_map = {}

    # Get all Python files in the tools directory
    for file_path in tools_dir.glob("*.py"):
        if file_path.name == "__init__.py":
            continue
        if file_path.stem in skip:
            continue

        module_name = file_path.stem
        try:
            # Import the module
            module = importlib.import_module(f"keystroke.tools.{module_name}")

            # Find all non-private functions in the module
            for name, func in inspect.getmembers(
                module, lambda x: inspect.isfunction(x) and not x.__name__.startswith("_")
            ):
                _schema = function_to_dict(func)
                schema = {
                    "type": "function",
                    "function": {
                        "name": name,
                        "description": _schema["description"],
                        "parameters": _schema["parameters"],
                    },
                }
                tool_map[name] = (func, schema)

        except ImportError as e:
            print(f"Error importing {module_name}: {e}")

    return tool_map


_all_functions = get_all_tool_functions(DISABLED_TOOLS)

TOOLS = [item[1] for item in _all_functions.values()]
TOOLS_MAP = {key: val[0] for key, val in _all_functions.items()}
