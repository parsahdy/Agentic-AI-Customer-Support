from dataclasses import dataclass
from enum import Enum


class GuardrailDecision(str, Enum):
    ALLOW = "allow"
    BLOCK = "block"
    ERROR = "error"


@dataclass(frozen=True)
class GuardrailViolation:
    code: str
    message: str


@dataclass(frozen=True)
class GuardrailResult:
    decision: GuardrailDecision
    violations: tuple[GuardrailViolation, ...]

    @property
    def allowed(self) -> bool:
        return self.decision == GuardrailDecision.ALLOW
