class AgentError(Exception):
    """Base class for every error the agent reports to the user."""


class ToolError(Exception):
    """A tool could not do what was asked. The agent sees the message."""
