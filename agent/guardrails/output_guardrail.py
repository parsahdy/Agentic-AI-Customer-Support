import re
from typing import Callable, Protocol

from agent import config

from .schemas import (
    GuardrailViolation,
    GuardrailDecision,
    GuardrailResult,
)


_DIGIT_MAP = str.maketrans(
    "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩",
    "01234567890123456789",
)


class OutputRule(Protocol):

    def check(self, final_answer: str) -> GuardrailViolation | None:
        ...


class RequiredOutputRule:

    def check(self, final_answer: str) -> GuardrailViolation | None:
        if not final_answer.strip():
            return GuardrailViolation(
                code="empty_output",
                message="Output cannot be empty.",
            )

        return None


class MaxOutputLengthRule:

    def __init__(
        self, 
        max_output_length: int = config.MAX_OUTPUT_LENGTH,
    ) -> None:
        if (
            not isinstance(max_output_length, int)
            or isinstance(max_output_length, bool)
            or max_output_length <= 0
        ):
            raise ValueError(
                "max_output_length must be a positive integer."
            )

        self.max_output_length = max_output_length

    def check(self, final_answer: str) -> GuardrailViolation | None:
        if len(final_answer) > self.max_output_length:
            return GuardrailViolation(
                code="output_too_long",
                message="Output exceeds the maximum allowed length.",
            )

        return None


def normalize(text: str) -> str:
    return text.translate(_DIGIT_MAP)


def luhn_valid(number: str) -> bool:
    digits = [int(d) for d in number][::-1]
    total = sum(digits[0::2])
    total += sum(sum(divmod(d * 2, 10)) for d in digits[1::2])
    return total % 10 == 0


def national_id_valid(code: str) -> bool:
    if len(code) != 10 or len(set(code)) == 1:
        return False
    total = sum(int(code[i]) * (10 - i) for i in range(9))
    remainder = total % 11
    check = int(code[9])
    return check == remainder if remainder < 2 else check == 11 - remainder


def _only_digits(text: str) -> str:
    return re.sub(r"\D", "", text)


@dataclass(frozen=True)
class _Detector:
    code: str
    message: str
    pattern: re.Pattern
    validator: Callable[[str], bool] | None = None


_I = re.IGNORECASE

_DETECTORS: tuple[_Detector, ...] = (
    _Detector(
        "CARD_NUMBER",
        "Output includes a bank card number.",
        re.compile(r"(?<![0-9])(?:[0-9][ \-]?){15}[0-9](?![0-9])"),
        lambda m: luhn_valid(_only_digits(m)),
    ),
    _Detector(
        "IBAN",
        "Output includes an IBAN (Sheba) number.",
        re.compile(r"(?<![A-Za-z0-9])IR(?:[ \-]?[0-9]){24}(?![0-9])", _I),
    ),
    _Detector(
        "CARD_SECRET",
        "Output includes a card CVV2, expiry date, or one-time password.",
        re.compile(
            r"(?:cvv2?|cvc|سی\s?وی\s?وی|رمز\s?دوم|رمز\s?پویا|otp|کد\s?تایید)"
            r"[^0-9]{0,15}[0-9]{3,8}"
            r"|(?:تاریخ\s?انقضا|expiry|exp)[^0-9]{0,15}[0-9]{2}\s?[/\-]\s?[0-9]{2,4}",
            _I,
        ),
    ),
    _Detector(
        "NATIONAL_ID",
        "Output includes a national ID number.",
        re.compile(r"(?<![0-9])[0-9]{10}(?![0-9])"),
        national_id_valid,
    ),
    _Detector(
        "PHONE_NUMBER",
        "Output includes a phone number.",
        re.compile(r"(?<![0-9])(?:\+98|0098|98|0)9[0-9]{9}(?![0-9])"),
    ),
    _Detector(
        "EMAIL",
        "Output includes an email address.",
        re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}"),
    ),
    _Detector(
        "POSTAL_CODE",
        "Output includes a postal code.",
        re.compile(r"(?:کد\s?پستی|postal\s?code|zip)[^0-9]{0,15}[0-9]{10}", _I),
    ),
    _Detector(
        "WALLET_OR_DISCOUNT",
        "Output includes wallet balance or a personal discount code.",
        re.compile(
            r"(?:موجودی\s?کیف\s?پول|wallet\s?balance|کد\s?تخفیف\s?شخصی)"
            r"[^0-9A-Za-z]{0,15}[0-9A-Za-z]+",
            _I,
        ),
    ),
    _Detector(
        "API_KEY",
        "Output includes an API key or access token.",
        re.compile(
            r"sk-[A-Za-z0-9_\-]{20,}"
            r"|AKIA[0-9A-Z]{16}"
            r"|ghp_[A-Za-z0-9]{36}"
            r"|Bearer\s+[A-Za-z0-9._\-]{20,}"
            r"|-----BEGIN (?:RSA |EC )?PRIVATE KEY-----"
        ),
    ),
    _Detector(
        "CREDENTIALS",
        "Output includes a password or a database connection string.",
        re.compile(
            r"(?:password|passwd|pwd|رمز\s?عبور)\s*[:=]\s*\S+"
            r"|(?:postgres(?:ql)?|mysql|mongodb|redis)://[^\s:@]+:[^\s@]+@",
            _I,
        ),
    ),
)


class SensitiveDataRule:

    def find_violations(self, final_answer: str) -> tuple[GuardrailViolation, ...]:
        text = normalize(final_answer)
        violations: list[GuardrailViolation] = []
        for detector in _DETECTORS:
            for match in detector.pattern.finditer(text):
                if detector.validator is None or detector.validator(match.group()):
                    violations.append(
                        GuardrailViolation(
                            detector.code, detector.message
                        )
                    )
                    break
        return tuple(violations)

    def check(self, final_answer: str) -> GuardrailViolation | None:
        violations = self.find_violations(final_answer)
        return violations[0] if violations else None


class OutputGuardrail:

    def __init__(
        self,
        rules: list[OutputRule],
    ) -> None:
        if not rules:
            raise ValueError(
                "At least one output validation rule is required."
            )

        self.rules = tuple(rules)


    def validate(self, final_answer: object) -> GuardrailResult:
        if not isinstance(final_answer, str):
            return GuardrailResult(
                decision=GuardrailDecision.BLOCK,
                violations=(
                    GuardrailViolation(
                        code="invalid_output_type",
                        message="Output must be string.",
                    ),
                ),
            )

        violations: list[GuardrailViolation] = []

        try:
            for rule in self.rules:
                violation = rule.check(final_answer)

                if violation is not None:
                    violations.append(violation)

        except Exception:
            return GuardrailResult(
                decision=GuardrailDecision.ERROR,
                violations=(
                    GuardrailViolation(
                        code="guardrail_execution_error",
                        message="Output validation could not be completed.",
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
