from src.schema import ReviewIssue, ReviewResult


def normalize_text(text: str) -> str:
    """
    Normalize text for simple comparison.
    """

    return (
        text.lower()
        .strip()
        .replace(".", "")
        .replace(",", "")
    )


def is_duplicate(
    issue_a: ReviewIssue,
    issue_b: ReviewIssue,
) -> bool:
    """
    Determine whether two issues are probably
    referring to the same problem.
    """

    if issue_a.file != issue_b.file:
        return False

    if issue_a.category != issue_b.category:
        return False

    title_a = normalize_text(
        issue_a.title
    )

    title_b = normalize_text(
        issue_b.title
    )

    return (
        title_a in title_b
        or title_b in title_a
    )


def deduplicate_issues(
    issues: list[ReviewIssue],
) -> list[ReviewIssue]:
    """
    Remove obvious duplicate findings.
    """

    unique = []

    for issue in issues:

        duplicate = any(
            is_duplicate(
                issue,
                existing,
            )
            for existing in unique
        )

        if not duplicate:
            unique.append(issue)

    return unique


def merge_review(
    ai_result: ReviewResult,
    static_issues: list[ReviewIssue],
) -> ReviewResult:
    """
    Combine AI and static-analysis findings.
    """

    all_issues = [
        *static_issues,
        *ai_result.issues,
    ]

    unique_issues = deduplicate_issues(
        all_issues
    )

    return ReviewResult(
        summary=ai_result.summary,
        score=ai_result.score,
        issues=unique_issues,
        positive_findings=(
            ai_result.positive_findings
        ),
    )

def rubocop_to_issues(
    offenses: list[dict],
) -> list[ReviewIssue]:
    """
    Convert RuboCop findings into the common
    ReviewIssue format.
    """

    issues = []

    for offense in offenses:

        severity = map_rubocop_severity(
            offense["severity"]
        )

        issues.append(
            ReviewIssue(
                title=(
                    f"RuboCop: "
                    f"{offense['cop']}"
                ),
                type="rubocop",
                severity=severity,
                category="style",
                file=offense["file"],
                line=offense["line"],
                explanation=(
                    offense["message"]
                ),
                recommendation=(
                    "Apply the recommended "
                    "RuboCop correction."
                ),
                evidence=[
                    "RuboCop"
                ],
            )
        )

    return issues


def map_rubocop_severity(
    severity: str,
) -> str:
    """
    Map RuboCop severity to our schema.
    """

    mapping = {
        "fatal": "critical",
        "error": "high",
        "warning": "medium",
        "convention": "low",
        "refactor": "low",
    }

    return mapping.get(
        severity,
        "low",
    )