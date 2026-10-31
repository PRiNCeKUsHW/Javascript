"""Who may do what: the permission check that runs before every tool call.

read    always allowed: looking never changes anything
write   allowed, unless the agent runs in read-only mode
danger  needs a human "yes" for every single call (deleting, sending, paying)
"""
from collections.abc import Callable
from dataclasses import dataclass, field

from pydantic import BaseModel

from productivity.errors import ToolError
from productivity.tools import Context, Tool


@dataclass
class Policy:
    ctx: Context
    read_only: bool = False
    ask_human: Callable[[str], bool] | None = None   # None: nobody to ask, so deny
    log: list[str] = field(default_factory=list)      # every decision, for the trace

    def __call__(self, t: Tool, args: BaseModel) -> None:
        if t.permission == "read":
            return
        if self.read_only:
            self.log.append(f"blocked {t.name} (read-only)")
            raise ToolError(f"{t.name} is not allowed: the agent is in read-only "
                            f"mode, so it can only look, not change anything")
        if t.permission == "danger":
            try:
                question = t.confirm(self.ctx, args) if t.confirm else f"Allow {t.name}?"
            except LookupError as exc:                 # e.g. the task doesn't exist
                raise ToolError(str(exc)) from None
            approved = bool(self.ask_human and self.ask_human(question))
            self.log.append(f"{'approved' if approved else 'declined'} {t.name}")
            if not approved:
                raise ToolError(f"the user declined {t.name}; don't retry it, "
                                f"tell the user it was not done")
