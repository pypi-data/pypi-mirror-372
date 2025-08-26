class AgentError(Exception):
    """Base exception class for all agent exceptions"""


class AgentAuthError(AgentError):
    """Agent failed to authenticate properly"""

    def __init__(self, reason: str):
        self.reason = reason

    def __str__(self) -> str:
        return f"agent failed to authenticate: {self.reason}"
