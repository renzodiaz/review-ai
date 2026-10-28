"""
Defenses for untrusted pull request content.

The code and RuboCop output under review are authored by the pull
request author, who is not trusted. This module keeps that content from
breaking out of its delimiters or smuggling instructions into the
prompt (prompt injection).
"""

import re


# Delimiters used to fence untrusted content inside the prompt.
UNTRUSTED_BEGIN = "<<<BEGIN UNTRUSTED CONTENT>>>"
UNTRUSTED_END = "<<<END UNTRUSTED CONTENT>>>"

# Phrases commonly used to hijack an LLM. Their presence does not prove
# an attack, but it is worth surfacing to the reviewer.
_INJECTION_PATTERNS = [
    r"ignore (?:all |the |your )?(?:previous|above|prior) instructions",
    r"disregard (?:all |the |your )?(?:previous|above|prior)",
    r"forget (?:everything|all|the above)",
    r"you are now",
    r"new instructions?",
    r"system prompt",
    r"developer message",
    r"return (?:a )?(?:score|rating) of",
    r"give (?:it |this )?(?:a )?(?:perfect|full|100)",
    r"approve this (?:pr|pull request|change)",
    r"do not report",
    r"skip the review",
]

_INJECTION_REGEX = re.compile(
    "|".join(_INJECTION_PATTERNS),
    re.IGNORECASE,
)


def neutralize(text: str) -> str:
    """
    Strip the fence delimiters from untrusted text so the author cannot
    close the fence and append their own instructions.
    """

    if not text:
        return ""

    return (
        text.replace(UNTRUSTED_BEGIN, "")
        .replace(UNTRUSTED_END, "")
    )


def wrap_untrusted(text: str) -> str:
    """
    Fence untrusted content between delimiters after neutralizing it.
    """

    return (
        f"{UNTRUSTED_BEGIN}\n"
        f"{neutralize(text)}\n"
        f"{UNTRUSTED_END}"
    )


def detect_injection(text: str) -> list[str]:
    """
    Return the distinct suspicious phrases found in untrusted text.

    Used to warn the reviewer, not to block the review.
    """

    if not text:
        return []

    found = []

    for match in _INJECTION_REGEX.finditer(text):

        phrase = match.group(0).strip().lower()

        if phrase not in found:
            found.append(phrase)

    return found
