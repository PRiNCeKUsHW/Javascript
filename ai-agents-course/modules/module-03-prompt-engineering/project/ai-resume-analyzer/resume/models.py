from pydantic import BaseModel, Field


class CandidateProfile(BaseModel):
    """What the model extracts from a resume."""

    name: str
    years_experience: int = Field(ge=0, le=60)
    skills: list[str] = Field(
        description="Technical skills the resume names, as written")
    recent_roles: list[str] = Field(max_length=5)


class JobRequirements(BaseModel):
    """What the model extracts from a job posting."""

    title: str
    min_years: int = Field(ge=0, le=30)
    must_have: list[str]
    nice_to_have: list[str]


class Suggestion(BaseModel):
    skill: str
    advice: str


class Suggestions(BaseModel):
    """The model's advice for the gaps that code found."""

    summary: str
    suggestions: list[Suggestion]
