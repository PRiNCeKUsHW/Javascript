class AgentError(Exception):
    """Base class for every error the agent reports to the user."""


class ToolError(Exception):
    """A tool call could not run. The model sees the message and can react."""
