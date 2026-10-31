# from_pydantic.py: write the input as a Pydantic class, get the schema for free
import json
from typing import Literal

from pydantic import BaseModel, Field

import project  # noqa: F401
from productivity.tools import schema_for


class AddNote(BaseModel):
    title: str = Field(max_length=80, description="A short title")
    text: str = Field(description="The note itself")
    pinned: bool = Field(description="Show it at the top")
    colour: Literal["yellow", "blue", "green"]


print(json.dumps(schema_for(AddNote), indent=1))
