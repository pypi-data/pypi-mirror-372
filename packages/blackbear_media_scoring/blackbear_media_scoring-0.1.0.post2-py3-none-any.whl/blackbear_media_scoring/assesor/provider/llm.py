from abc import ABC, abstractmethod
from typing import Optional

from pydantic import BaseModel


class Category(BaseModel):
    score: int
    keywords: list[str]
    phrases: list[str]
    reason: str

    def to_dict(self):
        return {
            "score": self.score,
            "keywords": self.keywords,
            "phrases": self.phrases,
            "reason": self.reason,
        }


class ScoreResult(BaseModel):
    pornografi: Category
    sara: Category
    politics: Category
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None

    def to_dict(self):
        return {
            "pornografi": self.pornografi.to_dict(),
            "sara": self.sara.to_dict(),
            "politics": self.politics.to_dict(),
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
        }


class LLM(ABC):
    @abstractmethod
    def score(self, text: str) -> ScoreResult:
        pass
