import json
import subprocess
from pathlib import Path


def run_rubocop(
    project_path: str,
    files: list[str],
) -> list[dict]:
    """
    Run RuboCop against Ruby files.

    Returns normalized offenses.
    """

    if not files:
        return []

    existing_files = []

    for filename in files:

        file_path = (
            Path(project_path) / filename
        )

        if file_path.exists():
            existing_files.append(
                filename
            )

    if not existing_files:
        return []

    command = [
        "rubocop",
        "--format",
        "json",
        "--force-exclusion",
        *existing_files,
    ]

    result = subprocess.run(
        command,
        cwd=project_path,
        capture_output=True,
        text=True,
    )

    if not result.stdout:
        return []

    try:

        data = json.loads(
            result.stdout
        )

    except json.JSONDecodeError:

        return []

    offenses = []

    for file_result in data.get(
        "files",
        [],
    ):

        filename = file_result["path"]

        for offense in file_result.get(
            "offenses",
            [],
        ):

            location = offense.get(
                "location",
                {},
            )

            offenses.append(
                {
                    "file": filename,
                    "line": location.get(
                        "start_line"
                    ),
                    "column": location.get(
                        "start_column"
                    ),
                    "severity": offense.get(
                        "severity"
                    ),
                    "cop": offense.get(
                        "cop_name"
                    ),
                    "message": offense.get(
                        "message"
                    ),
                }
            )

    return offenses

def format_offenses(
    offenses: list[dict],
) -> str:
    """
    Format RuboCop offenses for the AI.
    """

    if not offenses:
        return "No RuboCop offenses found."

    sections = []

    for offense in offenses:

        sections.append(
            f"""
File: {offense['file']}
Line: {offense['line']}
Severity: {offense['severity']}
Cop: {offense['cop']}
Message: {offense['message']}
"""
        )

    return "\n".join(sections)