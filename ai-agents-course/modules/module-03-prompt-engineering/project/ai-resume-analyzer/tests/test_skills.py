from resume.skills import grounded, mentions, normalize


def test_normalize_spelling_and_aliases():
    assert normalize("  Postgres ") == "postgresql"
    assert normalize("K8s") == "kubernetes"
    assert normalize("FastAPI") == "fastapi"


def test_mentions_uses_aliases_and_word_boundaries():
    assert mentions("We run Postgres in production", "PostgreSQL")
    assert mentions("ran k8s clusters", "Kubernetes")
    assert not mentions("JavaScript developer", "Java")


def test_grounded_drops_skills_the_text_does_not_name():
    kept, dropped = grounded(["Python", "COBOL"], "Python developer")
    assert kept == ["Python"]
    assert dropped == ["COBOL"]
