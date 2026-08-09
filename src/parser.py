import re


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


def extract_changed_files(diff: str) -> list[dict]:
    """
    Split a Git diff into individual files.
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

        files.append(
            {
                "filename": filename,
                "is_ruby": filename.endswith(".rb"),
                "is_test": is_test_file(filename),
                "hunks": extract_hunks(section),
            }
        )

    return files


def extract_hunks(file_diff: str) -> list[dict]:
    """
    Extract Git diff hunks.

    Example:

    @@ -20,6 +20,8 @@

    """

    sections = re.split(
        r"(?=^@@ )",
        file_diff,
        flags=re.MULTILINE,
    )

    hunks = []

    for section in sections:

        if not section.startswith("@@"):
            continue

        lines = section.splitlines()

        header = lines[0]

        changed_lines = []

        added_lines = []

        removed_lines = []

        context_lines = []

        for line in lines[1:]:

            if line.startswith("+"):

                if not line.startswith("+++"):
                    added_lines.append(
                        line[1:]
                    )

            elif line.startswith("-"):

                if not line.startswith("---"):
                    removed_lines.append(
                        line[1:]
                    )

            else:

                context_lines.append(
                    line
                )

            if (
                not line.startswith("+++")
                and not line.startswith("---")
            ):
                changed_lines.append(line)

        hunks.append(
            {
                "header": header,
                "added_lines": added_lines,
                "removed_lines": removed_lines,
                "context_lines": context_lines,
                "changed_lines": changed_lines,
            }
        )

    return hunks


def extract_ruby_files(diff: str) -> list[str]:
    """
    Return Ruby files modified by the PR.
    """

    files = extract_changed_files(diff)

    return [
        file["filename"]
        for file in files
        if file["is_ruby"]
    ]


def extract_added_ruby_code(diff: str) -> str:
    """
    Return formatted changed Ruby code.
    """

    files = extract_changed_files(diff)

    sections = []

    for file in files:

        if not file["is_ruby"]:
            continue

        for hunk in file["hunks"]:

            if not hunk["added_lines"]:
                continue

            sections.append(
                f"""
FILE: {file["filename"]}

HUNK:
{hunk["header"]}

ADDED CODE:
{chr(10).join(hunk["added_lines"])}

REMOVED CODE:
{chr(10).join(hunk["removed_lines"])}

CONTEXT:
{chr(10).join(hunk["context_lines"])}
"""
            )

    return "\n".join(sections)


def parse_diff(diff: str) -> dict:
    """
    Parse the complete Pull Request diff.
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