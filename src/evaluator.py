import json
import time
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


def run_benchmark(
    db,
    path: str = "evaluation/cases",
) -> list[dict]:
    """
    Run every benchmark case and record detected issues,
    latency, and any execution error (reliability).
    """

    cases = load_cases(path)
    expected = load_expected_findings()

    results = []

    for case in cases:

        expected_types = {
            item["type"]
            for item in expected[case["case_id"]]
        }

        start = time.perf_counter()
        detected_types = set()
        error = None

        try:
            result = run_case(case, db)
            detected_types = extract_issue_types(result)
        except Exception as exc:
            error = str(exc)

        results.append(
            {
                "case_id": case["case_id"],
                "expected": expected_types,
                "detected": detected_types,
                "elapsed_seconds": (
                    time.perf_counter() - start
                ),
                "error": error,
            }
        )

    return results


def score_case(
    expected_types: set,
    detected_types: set,
) -> dict:
    """
    Compare expected vs detected issue types for one case.

    A case with expected issues passes only if every expected
    type was detected. A clean case (no expected issues) passes
    only if nothing was flagged (no false positive).
    """

    true_positives = expected_types & detected_types
    false_positives = detected_types - expected_types
    false_negatives = expected_types - detected_types

    if expected_types:
        passed = expected_types.issubset(detected_types)
    else:
        passed = not detected_types

    return {
        "true_positives": len(true_positives),
        "false_positives": len(false_positives),
        "false_negatives": len(false_negatives),
        "passed": passed,
    }


def compute_metrics(benchmark_results: list[dict]) -> dict:
    """
    Aggregate precision, recall, F1, success rate, reliability,
    and average latency across all benchmark cases.
    """

    total_cases = len(benchmark_results)

    total_tp = 0
    total_fp = 0
    total_fn = 0
    passed_cases = 0
    failed_runs = 0
    total_latency = 0.0

    per_case = []

    for result in benchmark_results:

        if result["error"]:
            failed_runs += 1

        score = score_case(
            result["expected"],
            result["detected"],
        )

        total_tp += score["true_positives"]
        total_fp += score["false_positives"]
        total_fn += score["false_negatives"]

        if score["passed"]:
            passed_cases += 1

        total_latency += result["elapsed_seconds"]

        per_case.append(
            {**result, **score}
        )

    precision = (
        total_tp / (total_tp + total_fp)
        if (total_tp + total_fp) else 1.0
    )

    recall = (
        total_tp / (total_tp + total_fn)
        if (total_tp + total_fn) else 1.0
    )

    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) else 0.0
    )

    return {
        "per_case": per_case,
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3),
        "success_rate": (
            round(passed_cases / total_cases, 3)
            if total_cases else 0.0
        ),
        "reliability": (
            round((total_cases - failed_runs) / total_cases, 3)
            if total_cases else 0.0
        ),
        "avg_latency_seconds": (
            round(total_latency / total_cases, 2)
            if total_cases else 0.0
        ),
        "total_cases": total_cases,
    }