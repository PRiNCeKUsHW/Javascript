import re

# Different spellings of the same skill. Matching is code's job, not the model's.
ALIASES = {
    "postgres": "postgresql",
    "k8s": "kubernetes",
    "js": "javascript",
    "ts": "typescript",
    "amazon web services": "aws",
    "node": "node.js",
    "nodejs": "node.js",
    "github actions": "ci/cd",
    "ci": "ci/cd",
}


def normalize(skill: str) -> str:
    """'  Postgres ' -> 'postgresql'."""
    key = re.sub(r"\s+", " ", skill).strip().lower()
    return ALIASES.get(key, key)


def mentions(text: str, skill: str) -> bool:
    """Does the text name this skill (or one of its aliases)?"""
    target = normalize(skill)
    names = {target} | {a for a, full in ALIASES.items() if full == target}
    lowered = text.lower()
    return any(re.search(rf"(?<![\w.]){re.escape(n)}(?![\w])", lowered)
               for n in names)


def grounded(skills: list[str], source: str) -> tuple[list[str], list[str]]:
    """Split extracted skills into (found in the source, not found)."""
    kept: list[str] = []
    dropped: list[str] = []
    for skill in skills:
        (kept if mentions(source, skill) else dropped).append(skill)
    return kept, dropped
