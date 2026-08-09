import json
import subprocess
from pathlib import Path


def run_rubocop(
    project_path: str,
    files: list[str],
) -> list[dict]:
    """
    Run RuboCop against the specified Ruby files.

    Returns a list of offenses.
    """

    if not files:
        return []

    absolute_files = [
        str(Path(project_path) / file)
        for file in files
    ]

    command = [
        "rubocop",
        "--format",
        "json",
        *absolute_files,
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        cwd=project_path,
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

    for file in data.get("files", []):

        for offense in file.get(
            "offenses",
            [],
        ):

            offenses.append(
                {
                    "file": file["path"],
                    "line": offense["location"]["start_line"],
                    "severity": offense["severity"],
                    "cop_name": offense["cop_name"],
                    "message": offense["message"],
                }
            )

    return offenses