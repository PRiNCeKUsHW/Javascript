import pytest

from study.assistant import ChatSession, rough_tokens
from study.errors import BudgetExceeded, StudyError
from study.fake_api import DEMO_MARK


def test_explain_streams_and_reports_usage(assistant, fake):
    pieces = []
    answer = assistant.explain("recursion", on_text=pieces.append)
    assert len(pieces) > 5                       # it arrived in pieces
    assert "".join(pieces) == answer.text
    assert answer.text.startswith(DEMO_MARK)
    assert answer.stop_reason == "end_turn"
    assert answer.input_tokens > 0 and answer.cost_usd > 0
    sent = fake.requests[-1]
    assert sent["stream"] is True
    assert sent["fallbacks"] == "default"
    assert sent["messages"][0]["content"] == \
        "Explain recursion to a beginner learner."


def test_max_tokens_truncates(assistant):
    answer = assistant.explain("recursion", max_tokens=10)
    assert answer.truncated
    assert answer.output_tokens <= 10


def test_quiz_is_validated(assistant, fake):
    quiz, answer = assistant.make_quiz("Python sets", count=3)
    assert quiz.topic == "Python sets"
    assert len(quiz.questions) == 3
    assert all(len(q.options) == 4 for q in quiz.questions)
    assert "format" in fake.requests[-1]["output_config"]


def test_refusal_is_reported(assistant, fake):
    fake.failures = ["refusal"]
    with pytest.raises(StudyError, match="declined"):
        assistant.explain("anything")


def test_rate_limit_is_retried_then_succeeds(assistant, fake):
    fake.failures = ["429", "500"]               # two failures, two retries
    answer = assistant.reply([{"role": "user", "content": "hi"}])
    assert answer.text.startswith(DEMO_MARK)
    assert len(fake.requests) == 3


def test_rate_limit_after_retries_fails_cleanly(assistant, fake):
    fake.failures = ["429", "429", "429"]
    with pytest.raises(StudyError, match="rate limited"):
        assistant.reply([{"role": "user", "content": "hi"}])


def test_bad_key_message(assistant, fake):
    fake.failures = ["401"]
    with pytest.raises(StudyError, match="API key was rejected"):
        assistant.reply([{"role": "user", "content": "hi"}])


def test_budget_stops_before_calling(assistant, fake):
    assistant.tracker.budget_usd = 0
    with pytest.raises(BudgetExceeded):
        assistant.explain("anything")
    assert fake.requests == []


def test_count_tokens(assistant):
    assert assistant.count_tokens("a" * 40) >= 10


def test_chat_sends_whole_history(assistant, fake):
    chat = ChatSession(assistant)
    chat.send("What is a token?")
    chat.send("And a context window?")
    assert len(fake.requests[-1]["messages"]) == 3   # user, assistant, user
    assert len(chat.history) == 4


def test_chat_trims_oldest_turns(assistant):
    chat = ChatSession(assistant, history_budget=60)
    for i in range(4):
        chat.send(f"question {i} " + "x" * 80)
    assert chat.history[0]["role"] == "user"
    assert chat.history_tokens() <= 60 + rough_tokens("x" * 200)
    assert len(chat.history) < 8


def test_failed_turn_keeps_history_valid(assistant, fake):
    chat = ChatSession(assistant)
    fake.failures = ["400"]
    with pytest.raises(StudyError):
        chat.send("hello")
    assert chat.history == []
