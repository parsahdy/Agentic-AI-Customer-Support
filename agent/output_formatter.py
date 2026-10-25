import re


# Emoji / pictographs / dingbats / variation selectors.
_EMOJI_PATTERN = re.compile(
    "["
    "\U0001F300-\U0001FAFF"
    "\U00002600-\U000027BF"
    "\U00002B00-\U00002BFF"
    "\U0001F000-\U0001F2FF"
    "\U0000FE0F"
    "\U0000200D"
    "]+",
    flags=re.UNICODE,
)

_SENTENCE_END = re.compile(r"[.!?؟。](?=\s|$)")


def _flatten_tables(text: str) -> str:
    """
    Turn markdown tables into plain lines.

    "| a | b |"  ->  "a - b"      (separator rows are dropped)
    """

    lines = []

    for line in text.splitlines():
        stripped = line.strip()

        if re.fullmatch(r"\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?", stripped):
            continue

        if stripped.startswith("|") and stripped.endswith("|"):
            cells = [cell.strip() for cell in stripped.strip("|").split("|")]
            line = " - ".join(cell for cell in cells if cell)

        lines.append(line)

    return "\n".join(lines)


def strip_markdown(text: str) -> str:
    """
    Remove markdown decoration and emojis, keep the words.
    """

    text = _flatten_tables(text)

    # fenced code markers (keep the code text)
    text = re.sub(r"^```[^\n]*\n?", "", text, flags=re.MULTILINE)
    text = text.replace("```", "")

    # headings
    text = re.sub(r"^\s{0,3}#{1,6}\s*", "", text, flags=re.MULTILINE)

    # horizontal rules
    text = re.sub(r"^\s*([-*_]\s*){3,}$", "", text, flags=re.MULTILINE)

    # blockquotes
    text = re.sub(r"^\s*>\s?", "", text, flags=re.MULTILINE)

    # bold / italic / strikethrough / inline code
    text = re.sub(r"(\*\*|__)(.+?)\1", r"\2", text, flags=re.DOTALL)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"\1", text)
    text = re.sub(r"~~(.+?)~~", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)

    # "* item" bullets -> "- item"
    text = re.sub(r"^(\s*)\*\s+", r"\1- ", text, flags=re.MULTILINE)

    text = _EMOJI_PATTERN.sub("", text)

    return text


def trim_incomplete_sentence(text: str) -> str:
    """
    Cut a text that was truncated by max_tokens at its last complete
    sentence, so the user never sees a sentence that stops in the middle.
    """

    text = text.rstrip()

    if not text or _SENTENCE_END.search(text[-1:]):
        return text

    matches = list(_SENTENCE_END.finditer(text))

    if not matches:
        return text

    return text[: matches[-1].end()].rstrip()


def clean_answer(text: str | None, truncated: bool = False) -> str:
    """
    Deterministic last step before an answer reaches the user.

    The prompt asks the model for plain, short text. This function
    guarantees it even when the model ignores part of the instructions.
    """

    if not text:
        return ""

    text = strip_markdown(text)

    # tidy whitespace
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()

    if truncated:
        text = trim_incomplete_sentence(text)

    return text
