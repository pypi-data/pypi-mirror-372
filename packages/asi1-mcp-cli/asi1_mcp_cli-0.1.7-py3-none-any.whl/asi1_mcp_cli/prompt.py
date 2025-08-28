# Prompt templates for the FETCH.AI MCP CLI
# Each template can be used with the CLI to quickly generate high-quality prompts for common tasks.
prompt_templates = {
    # Code review prompt
    "review": ("You are an expert software engineer with a good taste on how a code should be. "
               "Assume that in current working directory, you are in a git repository. "
               "Get the current git status and diff. Review the change and provide feedback."
    ),
    # Commit message prompt
    "commit": ("You are an expert software engineer. Assume that in current working directory, you are in a git repository. "
               "Get the current git status and diff. Reason why the change was made. "
               "Then commit with a concise, descriptive message that follows Conventional Commits specification."
    ),
    # YouTube video summary prompt
    "yt": ("Retell and summarize the video in a concise and descriptive manner. "
           "Use bullet points and markdown formatting. The url is {url}"
    ),
    # Agent call example prompt
    "agent": ("You are an agent communicating with another agent. "
              "Send a message to the agent at address {address} with the following content: {message}"
    ),
    # MCP server call example prompt
    "mcp": ("You are interacting with the MCP server. "
            "Send the following query to the MCP server: {query}"
    ),
    # LLM call example prompt
    "llm": ("Answer the following question: {question}"
    ),
    # Command execution prompt
    "command": ("Use the run_command tool to execute the following command: {command}"
    ),
}
