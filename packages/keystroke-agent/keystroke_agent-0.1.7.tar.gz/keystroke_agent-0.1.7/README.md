# Keystroke Agent

A Python project implementing an AI assistant with tool integration, AWS service support, and asynchronous event-driven architecture.

## Features

1. **Advanced AI Integration**: 
   - Uses AWS Bedrock (Claude 3.5 Sonnet) as the default LLM
   - Asynchronous API calls for better performance
   - Configurable model selection
   - Event-driven architecture using asyncio.Queue for handling LLM responses and tool calls

2. **Built-in Tools**:
   - Calculator: Mathematical operations and functions
   - File Management: File operations (create, read, update, delete)
   - Presigned URL: AWS S3 presigned URL generation and file transfer

3. **Interactive CLI**:
   - Rich text formatting for better readability
   - Command history management
   - Dynamic conversation summarization
   - Dot commands for runtime configuration
   - Asynchronous implementation for improved responsiveness

4. **Customizable Settings**:
   - Model selection
   - System message
   - Assistant name
   - History limit
   - Tool enablement

## Installation

```sh
pip install keystroke-agent
```

## Configuration

1. Create a `.env` file with your AWS credentials:
```env
AWS_ACCESS_KEY_ID=your_key_id
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_SESSION_TOKEN=your_session_token
AWS_DEFAULT_REGION=your_region
```

2. Adjust settings in `keystroke/settings.py` as needed:
```python
AGENT_NAME = "AI Assistant"
DEFAULT_LLM_MODEL = "bedrock/anthropic.claude-3-5-sonnet-20240620-v1:0"
HISTORY_LIMIT = 10
ENABLE_TOOLS = True
```

## Usage

Start the agent:
```sh
agent
```

### Available Dot Commands

- `.help` - Show available commands
- `.clear` - Clear conversation history
- `.model <model_name>` - Change the LLM model
- `.view` - View current settings
- `.view history` - View conversation history
- `.system <message>` - Change the system message
- `.name <new_name>` - Change the assistant's name

### Available Tools

1. **Calculator**:
   - Basic arithmetic operations
   - Trigonometric functions
   - Logarithms and exponentials
   - Factorial calculation

2. **File Management**:
   - Create, read, update, and delete files
   - List files in directories
   - Copy and rename files
   - Recursive operations support

3. **AWS S3 Integration**:
   - Generate presigned URLs for upload/download
   - Upload files using presigned URLs
   - Download files using presigned URLs

## Development

Built with:
- `litellm` - LLM integration
- `rich` - Terminal formatting
- `boto3` - AWS SDK
- `python-dotenv` - Environment management
- `asyncio` - Asynchronous I/O

## License

MIT License

## Future Enhancements

- [x] Streaming Support
- [x] Asynchronous event-driven architecture
- [ ] Additional tool integrations
- [ ] Web interface option
- [ ] Enhanced error handling
- [ ] Conversation export functionality
- [ ] Tool usage analytics
- [ ] Custom tool loading system

### WhatsApp Integration
- [ ] WhatsApp Business API integration
  - Message sending and receiving
  - Media file handling (images, documents, voice notes)
  - Group chat support
  - Interactive buttons and list messages
- [ ] Automated responses through AI
- [ ] Contact management and user session handling
- [ ] Message templates and broadcasting
- [ ] Multi-language support for WhatsApp messages
- [ ] Message status tracking and analytics