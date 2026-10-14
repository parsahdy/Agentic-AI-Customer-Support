from dataclasses import dataclass
from enum import Enum
from typing import Protocol
import unicodedata

from agent import config


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


class InputRule(Protocol):
    def check(self, query:str) -> GuardrailViolation | None:
        ...


class RequiredInputRule:
    def check(self, query: str) -> GuardrailViolation | None:
        if not query.strip():
            return GuardrailViolation(
                code="empty_input",
                message="Input cannot be empty.",
            )

        return None


class MaxInputLengthRule:
    def __init__(self, max_input_length: int) -> None:
        if max_input_length <= 0:
            raise ValueError("max_length must be greater than zero.")

        self.max_length = config.MAX_INPUT_LENGTH

    def check(self, query: str) -> GuardrailViolation | None:
        if len(query) > self.max_length:
            return GuardrailViolation(
                code="input_too_long",
                message="Input exceeds the maximum allowed length.",
            )

        return None


class ControlCharacterRule:
    def check(self, query: str) -> GuardrailViolation | None:
        for character in query:
            if (
                unicodedata.category(character) == "Cc"
                and character not in "\n\r\t"
            ):
                return GuardrailViolation(
                            code="invalid_control_character",
                            message="Input contains an invalid control character.",
                        )
        return None


class InputGuardrail:
    def __init__(
        self,
        rules: list[InputRule],
    ) -> None:
        if not rules:
            raise ValueError(
                "At least one input validation rule is required."
            )

        self.rules = tuple(rules)


    def validate(self, query: object) -> GuardrailResult:
        if not isinstance(query, str):
            return GuardrailResult(
                decision=GuardrailDecision.BLOCK,
                violations=(
                    GuardrailViolation(
                        code="invalid_input_type",
                        message="Input must be a string.",
                    )
                )
            )

        violations: list[GuardrailViolation] = []

        try:
            for rule in self.rules:
                violation = rule.check(query)

                if violation is not None:
                    violations.append(violation)

        except Exception:
            return GuardrailResult(
                decision=GuardrailDecision.ERROR,
                violations=(
                    GuardrailViolation(
                        code="guardrail_execution_error",
                        message="Input validation could not be completed.",
                    ),
                ),
            )

        return GuardrailResult(
            decision=(
            GuardrailDecision.BLOCK
            if violations
            else GuardrailDecision.ALLOW
            ),
            violations=tuple(violations),
        )
