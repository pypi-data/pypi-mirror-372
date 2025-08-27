# Agent default settings
AGENT_NAME = "AI Assistant"
DEFAULT_LLM_MODEL = "bedrock/anthropic.claude-3-5-sonnet-20240620-v1:0"
DEFAULT_SYSTEM_MESSAGE = "You are a helpful assistant named AI Assistant."
MAX_TOKENS = 1000

# Tool settings
ENABLE_TOOLS = True
DISABLED_TOOLS = ["presigned_url"]  # List of tool names to disable

# Other settings
HISTORY_LIMIT = 10  # Max number of messages to keep in history before summarizing

# Add more settings as needed
