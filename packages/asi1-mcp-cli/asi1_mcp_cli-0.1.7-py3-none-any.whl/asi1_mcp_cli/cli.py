#!/usr/bin/env python3
"""ASI1 MCP CLI: A command-line interface for interacting with ASI:One LLM and MCP servers."""

from datetime import datetime
import argparse
import asyncio
import os
from typing import Annotated, TypedDict
import uuid
import sys
import re
import anyio
import json # Added for JSON formatting in handle_init_config

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.prebuilt import create_react_agent
from langgraph.managed import IsLastStep
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model

from rich.console import Console
from rich.table import Table

import base64
import filetype
import mimetypes

from .input import *
from .const import *
from .output import *
from .storage import *
from .tool import *
from .prompt import *
from .memory import *
from .config import AppConfig # Removed copy_example_config import
from .agent_chat import run_agent_chat


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    is_last_step: IsLastStep
    today_datetime: str
    memories: str
    remaining_steps: int


async def run(args) -> None:
    """Run the ASI1 MCP CLI agent."""
    query, is_conversation_continuation = parse_query(args)
    app_config = AppConfig.load()

    if args.list_tools:
        await handle_list_tools(app_config, args)
        return

    if args.show_memories:
        await handle_show_memories()
        return

    if args.list_prompts:
        handle_list_prompts()
        return

    if args.init:
        handle_init_config()
        return

    await handle_conversation(args, query, is_conversation_continuation, app_config)


def setup_argument_parser() -> argparse.Namespace:
    """Setup and return the argument parser and subparsers."""
    parser = argparse.ArgumentParser(
        description='Run ASI:One LLM with MCP servers',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  asi1 run "What is the capital of France?"     Ask a simple question
  asi1 run c "tell me more"                     Continue previous conversation
  asi1 run p review                             Use a prompt template
  cat file.txt | asi1 run                       Process input from a file
  asi1 run --list-tools                         Show available tools
  asi1 run --list-prompts                       Show available prompt templates
  asi1 run --no-confirmations "search web"      Run tools without confirmation
  asi1 agent chat --address <agent_address> --message "..."   Start a chat session with another agent
        """
    )
    subparsers = parser.add_subparsers(dest='subcommand', required=True)

    # Main LLM/MCP CLI subcommand
    run_parser = subparsers.add_parser('run', help='Run LLM/MCP CLI commands')
    run_parser.add_argument('query', nargs='*', default=[],
                            help='The query to process (default: read from stdin). '
                                 'Special prefixes:\n'
                                 '  c: Continue previous conversation\n'
                                 '  p: Use prompt template')
    run_parser.add_argument('--list-tools', action='store_true',
                            help='List all available LLM tools')
    run_parser.add_argument('--list-prompts', action='store_true',
                            help='List all available prompts')
    run_parser.add_argument('--no-confirmations', action='store_true',
                            help='Bypass tool confirmation requirements')
    run_parser.add_argument('--force-refresh', action='store_true',
                            help='Force refresh of tools capabilities')
    run_parser.add_argument('--text-only', action='store_true',
                            help='Print output as raw text instead of parsing markdown')
    run_parser.add_argument('--no-tools', action='store_true',
                            help='Do not add any tools')
    run_parser.add_argument('--no-intermediates', action='store_true',
                            help='Only print the final message')
    run_parser.add_argument('--show-memories', action='store_true',
                            help='Show user memories')
    run_parser.add_argument('--model',
                            help='Override the model specified in config')
    run_parser.add_argument('--init', action='store_true',
                            help='Initialize configuration file')

    # Agent subparser
    agent_parser = subparsers.add_parser('agent', help='Agent related commands')
    agent_subparsers = agent_parser.add_subparsers(dest='agent_command', required=True)

    chat_parser = agent_subparsers.add_parser('chat', help='Start a chat session with another agent')
    chat_parser.add_argument('--address', type=str, help='Recipient agent address')
    chat_parser.add_argument('--message', type=str, help='Message to send')

    return parser


async def handle_list_tools(app_config: AppConfig, args: argparse.Namespace) -> None:
    """Handle the --list-tools command."""
    server_configs = [
        McpServerConfig(
            server_name=name,
            server_param=StdioServerParameters(
                command=config.command,
                args=config.args or [],
                env={**(config.env or {}), **os.environ}
            ),
            exclude_tools=config.exclude_tools or []
        )
        for name, config in app_config.get_enabled_servers().items()
    ]
    toolkits, tools = await load_tools(server_configs, args.no_tools, args.force_refresh)

    console = Console()
    table = Table(title="Available ASI:One MCP Tools")
    table.add_column("Toolkit", style="cyan")
    table.add_column("Tool Name", style="cyan")
    table.add_column("Description", style="green")

    for tool in tools:
        if isinstance(tool, McpTool):
            table.add_row(tool.toolkit_name, tool.name, tool.description)
    console.print(table)

    for toolkit in toolkits:
        await toolkit.close()


async def handle_show_memories() -> None:
    """Handle the --show-memories command."""
    store = SqliteStore(SQLITE_DB)
    memories = await get_memories(store)

    console = Console()
    table = Table(title="ASI:One LLM Memories")
    for memory in memories:
        table.add_row(memory)
    console.print(table)


def handle_list_prompts() -> None:
    """Handle the --list-prompts command."""
    console = Console()
    table = Table(title="Available Prompt Templates")
    table.add_column("Name", style="cyan")
    table.add_column("Template")
    table.add_column("Arguments")

    for name, template in prompt_templates.items():
        table.add_row(name, template, ", ".join(re.findall(r'\{(\w+)\}', template)))
    console.print(table)


def handle_init_config() -> None:
    """Handle the --init command by providing instructions to create a config file."""
    console = Console()
    config_file_path = CONFIG_DIR / "config.json" # Or CONFIG_FILE if you prefer the other path

    console.print(f"📝 To initialize your configuration, please create a file named:")
    console.print(f"   [bold cyan]{config_file_path}[/bold cyan]")
    console.print("\nHere's a basic template you can copy and paste into the file:")

    basic_config_template = {
        "systemPrompt": "You are an AI assistant helping a software engineer. Your user is a professional software engineer who works on various programming projects. Today's date is {today_datetime}. I aim to provide clear, accurate, and helpful responses with a focus on software development best practices. I should be direct, technical, and practical in my communication style. When doing git diff operation, do check the README.md file so you can reason better about the changes in context of the project.",
        "llm": {
            "provider": "asi-one",
            "model": "asi1-mini",
            "api_key": "YOUR_ASI1_API_KEY",
            "temperature": 0,
            "base_url": "https://api.asi1.ai/v1"
        },
        "mcpServers": {
            "brave-search": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-brave-search"],
                "env": {
                    "BRAVE_API_KEY": "YOUR_BRAVE_API_KEY"
                }
            }
        }
    }
    console.print(json.dumps(basic_config_template, indent=2))

    console.print("\nAfter creating and populating the file, remember to replace 'YOUR_ASI1_API_KEY' and 'YOUR_BRAVE_API_KEY' with your actual API keys.")
    console.print("\nThen, you can start using the CLI:")
    console.print("   [bold green]asi1 'Hello, how can you help me?'[/bold green]")


async def load_tools(server_configs: list[McpServerConfig], no_tools: bool, force_refresh: bool) -> tuple[list, list]:
    """Load and convert MCP tools to LangChain tools."""
    if no_tools:
        return [], []

    toolkits = []
    langchain_tools = []

    async def convert_toolkit(server_config: McpServerConfig):
        try:
            toolkit = await convert_mcp_to_langchain_tools(server_config, force_refresh)
            if toolkit and toolkit.get_tools():
                toolkits.append(toolkit)
                langchain_tools.extend(toolkit.get_tools())
        except Exception as e:
            print(f"Warning: Failed to load toolkit for {server_config.server_name}: {e}")
            # Continue with other toolkits even if this one fails
            print(f"Warning: Failed to load toolkit for {server_config.server_name}: {e}")
            # Continue with other toolkits even if this one fails

    # Load toolkits sequentially to avoid task group issues
    for server_config in server_configs:
        await convert_toolkit(server_config)

    langchain_tools.append(save_memory)
    return toolkits, langchain_tools


async def handle_conversation(args: argparse.Namespace, query: HumanMessage, is_conversation_continuation: bool, app_config: AppConfig) -> None:
    """Handle the main conversation flow."""
    server_configs = [
        McpServerConfig(
            server_name=name,
            server_param=StdioServerParameters(
                command=config.command,
                args=config.args or [],
                env={**(config.env or {}), **os.environ}
            ),
            exclude_tools=config.exclude_tools or []
        )
        for name, config in app_config.get_enabled_servers().items()
    ]
    toolkits, tools = await load_tools(server_configs, args.no_tools, args.force_refresh)

    extra_body = {}
    if app_config.llm.base_url and "asi-one" in app_config.llm.base_url:
        extra_body = {"web3_enabled": True}

    if args.model:
        app_config.llm.model = args.model

    # Use OpenAI provider for ASI1 API since it's OpenAI-compatible
    provider = "openai" if app_config.llm.provider == "asi-one" else app_config.llm.provider

    model: BaseChatModel = init_chat_model(
        model=app_config.llm.model,
        model_provider=provider,
        api_key=app_config.llm.api_key,
        temperature=app_config.llm.temperature,
        base_url=app_config.llm.base_url,
        default_headers={
            "X-Title": "asi1-mcp-cli",
            "HTTP-Referer": "https://github.com/asi-one/asi1-mcp-cli",
        },
        extra_body=extra_body
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", app_config.system_prompt),
        ("placeholder", "{messages}")
    ])

    conversation_manager = ConversationManager(SQLITE_DB)
    store = SqliteStore(SQLITE_DB)
    memories = await get_memories(store)
    formatted_memories = "\n".join(f"- {memory}" for memory in memories)

    agent_executor = create_react_agent(
        model, tools, state_schema=AgentState, checkpointer=None, store=store
    )

    thread_id = (await conversation_manager.get_last_id() if is_conversation_continuation else uuid.uuid4().hex)

    input_messages = AgentState(
        messages=[query],
        today_datetime=datetime.now().isoformat(),
        memories=formatted_memories,
        remaining_steps=3
    )

    output = OutputHandler(text_only=args.text_only, only_last_message=args.no_intermediates)
    output.start()

    try:
        async for chunk in agent_executor.astream(
            input_messages,
            stream_mode=["messages", "values"],
            config={"configurable": {"thread_id": thread_id, "user_id": "myself"}, "recursion_limit": 100}
        ):
            output.update(chunk)
            if not args.no_confirmations:
                if not output.confirm_tool_call(app_config.__dict__, chunk):
                    break
    except Exception as e:
        output.update_error(e)
    finally:
        output.finish()
        # No checkpoint connection to save
        for toolkit in toolkits:
            await toolkit.close()


def parse_query(args: argparse.Namespace) -> tuple[HumanMessage, bool]:
    """
    Parse the query from command line arguments.
    Returns a tuple of (HumanMessage, is_conversation_continuation).
    """
    query_parts = ' '.join(args.query).split()
    stdin_content = ""
    stdin_image = None
    is_continuation = False

    if query_parts and query_parts[0] == 'cb':
        query_parts = query_parts[1:]
        clipboard_result = get_clipboard_content()
        if clipboard_result:
            content, mime_type = clipboard_result
            if mime_type:
                stdin_image = base64.b64encode(content).decode('utf-8')
            else:
                stdin_content = content
        else:
            print("No content found in clipboard")
            raise Exception("Clipboard is empty")
    elif not sys.stdin.isatty():
        stdin_data = sys.stdin.buffer.read()
        kind = filetype.guess(stdin_data)
        image_type = kind.extension if kind else None
        if image_type:
            stdin_image = base64.b64encode(stdin_data).decode('utf-8')
            mime_type = mimetypes.guess_type(f"dummy.{image_type}")[0] or f"image/{image_type}"
        else:
            stdin_content = stdin_data.decode('utf-8').strip()

    query_text = ""
    if query_parts:
        if query_parts[0] == 'c':
            is_continuation = True
            query_text = ' '.join(query_parts[1:])
        elif query_parts[0] == 'p' and len(query_parts) >= 2:
            template_name = query_parts[1]
            if template_name not in prompt_templates:
                print(f"Error: Prompt template '{template_name}' not found.")
                print("Available templates:", ", ".join(prompt_templates.keys()))
                return HumanMessage(content=""), False
            template = prompt_templates[template_name]
            template_args = query_parts[2:]
            try:
                var_names = re.findall(r'\{(\w+)\}', template)
                template_vars = dict(zip(var_names, template_args))
                query_text = template.format(**template_vars)
            except KeyError as e:
                print(f"Error: Missing argument {e}")
                return HumanMessage(content=""), False
        else:
            query_text = ' '.join(query_parts)

    if stdin_content and query_text:
        query_text = f"{stdin_content}\n\n{query_text}"
    elif stdin_content:
        query_text = stdin_content
    elif not query_text and not stdin_image:
        return HumanMessage(content=""), False

    if stdin_image:
        content = [
            {"type": "text", "text": query_text or "What do you see in this image?"},
            {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{stdin_image}"}}
        ]
    else:
        content = query_text

    return HumanMessage(content=content), is_continuation


class Colors:
    CYAN = '\033[96m'
    RESET = '\033[0m'


from yaspin import yaspin
import time

def print_header():
    """Print a beautifully enhanced CLI header with branding and status"""
    header = f"""{Colors.CYAN}
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║                          🤖  WELCOME TO ASI MCP CLI  🤖                       ║
║                                                                               ║
║         A Command Line Interface for AI-Powered Interactions,                 ║
║               Backed by the Intelligence of Fetch.ai                          ║
║                                                                               ║
║                     Build. Automate. Discover. Evolve.                        ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝

          [=======]
         |       |
     .-\"\"\"-.   .-\"\"\"-.
    /       \\ /       \\
   |  .--.   |   .--.  |
   | |  | |  |  |  | | |
    \\ \\__/ / \\ \\__/ / /
     '.__.'   '.__.'
     ASI CLI is Alive 🤖
{Colors.RESET}"""
    print(header)
    with yaspin(text="Thinking...", color="cyan") as spinner:
        time.sleep(3)  # Simulate async task
        spinner.ok("✅ ")



def main() -> None:
    import sys
    print_header()
    parser = setup_argument_parser()

    # Backward compatibility: if first arg is not a subcommand, treat as query
    if len(sys.argv) > 1 and sys.argv[1] not in ('run', 'agent', '-h', '--help'):
        sys.argv.insert(1, 'run')

    args = parser.parse_args()

    if args.subcommand == 'agent' and args.agent_command == 'chat':
        run_agent_chat(agent2_address=getattr(args, 'address', None), initial_text=getattr(args, 'message', None))
        return
    elif args.subcommand == 'run':
        asyncio.run(run(args))


if __name__ == "__main__":
    main()
