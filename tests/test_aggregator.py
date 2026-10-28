from src.aggregator import (
    deduplicate_issues,
    map_rubocop_severity,
    merge_review,
    rubocop_to_issues,
)
from src.schema import ReviewIssue, ReviewResult


def make_issue(title, file="a.rb", category="security"):
    return ReviewIssue(
        title=title,
        type="other",
        severity="high",
        category=category,
        file=file,
        line=1,
        explanation="e",
        recommendation="r",
    )


def test_map_rubocop_severity():
    assert map_rubocop_severity("fatal") == "critical"
    assert map_rubocop_severity("error") == "high"
    assert map_rubocop_severity("convention") == "low"
    assert map_rubocop_severity("unknown") == "low"


def test_rubocop_to_issues():
    issues = rubocop_to_issues(
        [
            {
                "file": "a.rb",
                "line": 3,
                "severity": "warning",
                "cop": "Style/Foo",
                "message": "bad style",
            }
        ]
    )

    assert len(issues) == 1
    assert issues[0].category == "style"
    assert issues[0].severity == "medium"
    assert "Style/Foo" in issues[0].title


def test_deduplicate_merges_similar_titles_same_file():
    issues = [
        make_issue("SQL injection"),
        make_issue("SQL injection risk"),
    ]

    assert len(deduplicate_issues(issues)) == 1


def test_deduplicate_keeps_different_files():
    issues = [
        make_issue("SQL injection", file="a.rb"),
        make_issue("SQL injection", file="b.rb"),
    ]

    assert len(deduplicate_issues(issues)) == 2


def test_merge_review_preserves_rag_sources():
    ai = ReviewResult(
        summary="s",
        score=70,
        issues=[make_issue("N+1 query", category="performance")],
        positive_findings=["clear naming"],
        rag_sources=["performance.md", "rails.md"],
    )

    static = rubocop_to_issues(
        [
            {
                "file": "a.rb",
                "line": 2,
                "severity": "error",
                "cop": "Lint/Bar",
                "message": "m",
            }
        ]
    )

    merged = merge_review(ai, static)

    # Regression guard: rag_sources used to be dropped here.
    assert merged.rag_sources == ["performance.md", "rails.md"]
    assert merged.positive_findings == ["clear naming"]
    assert len(merged.issues) == 2
