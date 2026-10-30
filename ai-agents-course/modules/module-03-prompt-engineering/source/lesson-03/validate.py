import pydantic

import project  # noqa: F401  (makes `resume` importable)
from resume.models import CandidateProfile

REPLIES = {
    "good": '{"name": "Ana", "years_experience": 3,'
            ' "skills": ["Python"], "recent_roles": ["Developer"]}',
    "negative years": '{"name": "Ana", "years_experience": -1,'
                      ' "skills": [], "recent_roles": []}',
    "missing field": '{"name": "Ana", "skills": [], "recent_roles": []}',
    "cut off": '{"name": "Ana", "years_experience": 3, "skil',
}

for label, reply in REPLIES.items():
    try:
        profile = CandidateProfile.model_validate_json(reply)
        print(f"{label:15} ok: {profile.name}, {profile.years_experience} yrs")
    except pydantic.ValidationError as exc:
        error = exc.errors()[0]
        where = ".".join(str(p) for p in error["loc"]) or "(whole reply)"
        print(f"{label:15} {error['type']}: {where}")
