from typing import Protocol
import unicodedata

from agent import config

from .schemas import (
    GuardrailResult,
    GuardrailDecision,
    GuardrailViolation,
)


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
    def __init__(
        self, 
        max_input_length: int = config.MAX_INPUT_LENGTH
    ) -> None:
        if (
            not isinstance(max_input_length, int)
            or isinstance(max_input_length, bool)
            or max_input_length <= 0
        ):
            raise ValueError(
                "max_input_length must be a positive integer."
            )

        self.max_length = max_input_length

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
