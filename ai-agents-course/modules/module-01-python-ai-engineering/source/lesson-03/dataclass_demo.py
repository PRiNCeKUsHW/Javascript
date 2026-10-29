# dataclass_demo.py: classes that mostly hold data, with less typing
from dataclasses import dataclass, field


@dataclass
class ModelConfig:
    name: str
    max_tokens: int = 500
    temperature: float = 0.2
    stop: list[str] = field(default_factory=list)


small = ModelConfig("model-small")
large = ModelConfig("model-large", max_tokens=2000)
print(small)
print(large.max_tokens)
print(small == ModelConfig("model-small"))
