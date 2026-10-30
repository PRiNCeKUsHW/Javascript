# Glossary

Every technical term used in the course, in plain words. The module where a term first appears is
in brackets. New terms are added with each module.

## Python and tools

| Term | Meaning |
|---|---|
| **async / await** [1] | A way to start several slow tasks (like web requests) and wait for them together instead of one after another. |
| **CLI** (command-line interface) [1] | A program you run by typing a command in the terminal, such as `python -m resume analyze ...`. |
| **dataclass** [1] | A Python class that mainly holds data; `@dataclass` writes the boring `__init__` code for you. |
| **dict** (dictionary) [1] | Python's key-to-value container: `{"name": "Sam", "years": 4}`. |
| **environment variable** [1] | A setting stored outside your code, read with `os.environ`. Used for API keys so they never appear in code. |
| **exception** [1] | Python's way of reporting an error. You `raise` one and `except` (catch) it. |
| **exit code** [1] | The number a program returns when it finishes: 0 means success, anything else means an error. |
| **f-string** [1] | A string with values inside: `f"Hello {name}"`. |
| **JSON** [1] | A text format for data that every language understands: `{"skills": ["Python"]}`. |
| **mypy** [1] | A tool that checks your type hints and finds type mistakes before you run the code. |
| **package / module** [1] | A module is one `.py` file; a package is a folder of modules with an `__init__.py`. |
| **pip** [1] | Python's package installer: `pip install -r requirements.txt`. |
| **pytest** [1] | The testing tool used in every project. A test is a function that `assert`s something is true. |
| **stdout / stderr** [1] | A program's two output streams: normal output, and messages or errors. |
| **terminal** [1] | The text window where you type commands (Terminal on macOS, PowerShell or Git Bash on Windows). |
| **type hint** [1] | A note about what type a value should be: `def add(a: int, b: int) -> int`. |
| **virtual environment (venv)** [1] | A private folder of packages for one project, so projects don't break each other. |

## Language models and the API

| Term | Meaning |
|---|---|
| **API** [2] | A way for programs to talk to a service. Your code sends a request to the Claude API and gets a response. |
| **API key** [2] | A secret password that identifies you to the API. Keep it in an environment variable; never commit it. |
| **context window** [2] | The most text (in tokens) a model can consider in one request, input and output together. |
| **cost per million tokens** [2] | How API usage is priced: separate prices for input and output tokens. |
| **effort** [2] | A setting (`low` to `max`) that controls how much the model reasons before answering. More effort, more tokens. |
| **fake API / offline mode** [2] | A local stand-in that speaks the same protocol as the real API, so code runs and tests pass without a key. Its replies are not real model output. |
| **hallucination** [2] | When a model states something false with confidence. Models produce plausible text, not looked-up facts. |
| **LLM** (large language model) [2] | A model trained on huge amounts of text that predicts the next token, over and over. |
| **max_tokens** [2] | The most tokens a reply may use. If it's reached, the reply is cut off. |
| **message history** [2] | The list of earlier messages your app sends with every request. The API itself remembers nothing. |
| **rate limit / 429** [2] | A cap on how many requests or tokens you may use per minute. Exceeding it returns error 429. |
| **refusal** [2] | When the model declines a request; the reply's `stop_reason` is `refusal`. |
| **retry with backoff** [2] | Trying a failed request again after a short wait that grows each time. The SDK does this for you. |
| **SDK** (software development kit) [2] | A library that makes an API easy to use from a language. Here: the `anthropic` Python package. |
| **stop_reason** [2] | Why the model stopped: finished (`end_turn`), hit the limit (`max_tokens`), declined (`refusal`), and others. |
| **streaming** [2] | Receiving the reply piece by piece as it's generated, instead of waiting for all of it. |
| **system prompt** [2] | Instructions that set the model's role, rules and style for the whole conversation. |
| **token** [2] | A chunk of text a model reads and writes: often a short word or part of a word. About 4 characters in English. |

## Prompts and structured output

| Term | Meaning |
|---|---|
| **eval** (evaluation) [3] | A set of labelled examples plus a grader that scores a prompt version, so changes can be compared with numbers. |
| **example (few-shot)** [3] | A sample input and output in the prompt that shows the model what you mean. Use a few varied ones. |
| **fingerprint** [3] | A short hash of a prompt's exact text. If one character changes, the fingerprint changes. |
| **grader** [3] | The code (or model) that decides whether an output is right. Prefer exact checks in code. |
| **grounding check** [3] | Verifying in code that the model's output is supported by the input, e.g. a skill really appears in the resume. |
| **prefill** [3] | Starting the assistant's reply for it. Current Claude models reject it; use structured outputs instead. |
| **prompt** [3] | Everything you send the model: context, task, data, constraints and examples. |
| **prompt injection** [3] | Text inside your data that tries to act as instructions ("ignore your rules..."). |
| **prompt versioning** [3] | Giving every prompt a version and never editing a released one, so results stay traceable. |
| **Pydantic** [3] | A Python library that defines data shapes (schemas) as classes and validates data against them. |
| **schema** [3] | A description of the shape data must have: which fields, which types, which limits. |
| **structured output** [3] | Asking the API to return JSON that matches your schema, e.g. `messages.parse(output_format=Model)`. |
| **task decomposition** [3] | Splitting a big task into steps: the model for judgment, plain code for everything deterministic. |
| **validation / ValidationError** [3] | Checking data against a schema; Pydantic raises `ValidationError` when it doesn't fit. |
| **XML tags** [3] | Markers like `<resume>...</resume>` that show the model exactly where data starts and ends. |
