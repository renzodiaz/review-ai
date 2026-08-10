from typing import Literal

from pydantic import BaseModel, Field


Severity = Literal[
    "critical",
    "high",
    "medium",
    "low",
]

Category = Literal[
    "security",
    "performance",
    "rails",
    "maintainability",
    "team_convention",
    "testing",
    "style",
]


class ReviewIssue(BaseModel):
    title: str

    type: str

    severity: Severity

    category: Category

    file: str | None = None

    line: int | None = None

    explanation: str

    recommendation: str

    evidence: list[str] = Field(
        default_factory=list
    )


class ReviewResult(BaseModel):
    summary: str

    score: int = Field(
        ge=0,
        le=100,
    )

    issues: list[ReviewIssue] = Field(
        default_factory=list
    )

    positive_findings: list[str] = Field(
        default_factory=list
    )