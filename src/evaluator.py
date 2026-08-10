import json
from pathlib import Path

from src.reviewer import review


def load_expected_findings(
    path: str = "evaluation/expected_findings.json",
) -> dict:
    """
    Load benchmark expectations.
    """

    data = json.loads(
        Path(path).read_text()
    )

    return {
        item["case_id"]: item["expected"]
        for item in data
    }


def load_cases(
    path: str = "evaluation/cases",
) -> list[dict]:
    """
    Load all benchmark cases.
    """

    cases = []

    root = Path(path)

    print(root)

    for case_dir in sorted(
        root.iterdir()
    ):

        if not case_dir.is_dir():
            continue

        change_file = (
            case_dir / "change.rb"
        )

        if not change_file.exists():
            continue

        cases.append(
            {
                "case_id": case_dir.name,
                "code": change_file.read_text(),
            }
        )

    return cases

def run_case(
    case: dict,
    db,
):
    """
    Run AI review against one benchmark case.
    """

    result = review(
        changed_code=case["code"],
        db=db,
        rubocop_context=(
            "No RuboCop results."
        ),
    )

    return result

def extract_issue_types(result):
    """
    Extract normalized issue types.
    """

    return {
        issue.type
        for issue in result.issues
    }