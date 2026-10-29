# structured.py: get JSON that matches a schema, parsed into a Python object
from pydantic import BaseModel, Field

from offline import lesson_client


class Question(BaseModel):
    question: str
    options: list[str] = Field(min_length=4, max_length=4)
    answer_index: int = Field(ge=0, le=3)
    explanation: str


class Quiz(BaseModel):
    topic: str
    questions: list[Question]


client = lesson_client()
response = client.messages.parse(
    model="claude-opus-5-5",
    max_tokens=16000,
    output_format=Quiz,              # the SDK turns the class into a JSON schema
    messages=[{"role": "user",
               "content": "Write 2 multiple-choice questions about HTTP."}],
)
quiz = response.parsed_output        # a validated Quiz object
print(type(quiz).__name__, "-", quiz.topic)
for q in quiz.questions:
    print(q.question, q.options[q.answer_index])
