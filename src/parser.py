import re

def extract_ruby_files(diff: str):
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

def extract_added_lines(diff: str):
    """
    Extract added lines from a unified Git diff.

    Lines beginning with +++ are Git metadata,
    so they are ignored.
    """

    added_lines = []

    for line in diff.splitlines():

        if line.startswith("+++"):

            continue

        if line.startswith("+"):

            added_lines.append(line[1:])

    return "\n".join(added_lines)

def parse_diff(diff: str) -> dict:
    """
    Extract useful information from the Pull Request diff.
    """

    ruby_files = extract_ruby_files(diff)

    added_lines = extract_added_lines(diff)

    return {
        "ruby_files": ruby_files,
        "added_lines": added_lines,
    }
