import re

def extract_ruby_files(diff: str) -> list[str]:
    """
    Return Ruby files modified by the Pull Request.
    """

    pattern = r"diff --git a/(.*?) b/"

    matches = re.findall(pattern, diff)

    return [
        filename
        for filename in matches
        if filename.endswith(".rb")
    ]

def extract_changed_files(diff: str) -> list[dict]:
    """
    Parse the diff into individual changed files.

    Returns something like:

    [
        {
            "filename": "app/models/user.rb",
            "is_ruby": True,
            "is_test": False,
            "added_lines": [...],
            "removed_lines": [...]
        }
    ]
    """

    sections = re.split(
        r"(?=diff --git )",
        diff,
    )

    files = []

    for section in sections:

        if not section.startswith("diff --git "):
            continue

        match = re.search(
            r"diff --git a/(.*?) b/(.*?)\n",
            section,
        )

        if not match:
            continue

        filename = match.group(2)

        added_lines = []
        removed_lines = []

        for line in section.splitlines():

            if line.startswith("+++"):
                continue

            if line.startswith("---"):
                continue

            if line.startswith("+"):
                added_lines.append(line[1:])

            elif line.startswith("-"):
                removed_lines.append(line[1:])

        files.append(
            {
                "filename": filename,
                "is_ruby": filename.endswith(".rb"),
                "is_test": is_test_file(filename),
                "added_lines": added_lines,
                "removed_lines": removed_lines,
            }
        )

    return files

def is_test_file(filename: str) -> bool:
    """
    Determine whether a Ruby file is probably a test.
    """

    return (
        filename.startswith("spec/")
        or filename.startswith("test/")
        or filename.endswith("_spec.rb")
        or filename.endswith("_test.rb")
    )


def extract_added_ruby_code(diff: str) -> str:
    """
    Extract added code from Ruby files only.
    """

    changed_files = extract_changed_files(diff)

    ruby_sections = []

    for file in changed_files:

        if not file["is_ruby"]:
            continue

        if not file["added_lines"]:
            continue

        code = "\n".join(
            file["added_lines"]
        )

        ruby_sections.append(
            f"""
FILE: {file["filename"]}

{code}
"""
        )

    return "\n".join(ruby_sections)


def parse_diff(diff: str) -> dict:
    """
    Parse a Pull Request diff into useful information.
    """

    changed_files = extract_changed_files(diff)

    ruby_files = [
        file
        for file in changed_files
        if file["is_ruby"]
    ]

    production_files = [
        file
        for file in ruby_files
        if not file["is_test"]
    ]

    test_files = [
        file
        for file in ruby_files
        if file["is_test"]
    ]

    return {
        "changed_files": changed_files,
        "ruby_files": ruby_files,
        "production_files": production_files,
        "test_files": test_files,
        "added_ruby_code": extract_added_ruby_code(diff),
    }