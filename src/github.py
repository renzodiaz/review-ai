import re
import tempfile
from pathlib import Path

import requests
from git import Repo


def parse_pr_url(pr_url: str) -> dict:
    """
    Parse a GitHub Pull Request URL.

    Example:

    https://github.com/rails/rails/pull/123

    returns:

    {
        "owner": "rails",
        "repo": "rails",
        "number": 123
    }
    """

    pattern = (
        r"github\.com/"
        r"([^/]+)/"
        r"([^/]+)/"
        r"pull/"
        r"(\d+)"
    )

    match = re.search(pattern, pr_url)

    if not match:
        raise ValueError(
            "Invalid GitHub Pull Request URL."
        )

    return {
        "owner": match.group(1),
        "repo": match.group(2),
        "number": int(match.group(3)),
    }


def download_pr(pr_url: str) -> str:
    """
    Download the unified diff for a GitHub Pull Request.
    """

    diff_url = pr_url.rstrip("/") + ".diff"

    response = requests.get(
        diff_url,
        timeout=30,
    )

    response.raise_for_status()

    return response.text


def download_diff(diff_url: str) -> str:
    """
    Download a diff directly.
    """

    response = requests.get(
        diff_url,
        timeout=30,
    )

    response.raise_for_status()

    return response.text


def get_pr_metadata(pr_url: str) -> dict:
    """
    Retrieve basic Pull Request information
    using the public GitHub API.
    """

    info = parse_pr_url(pr_url)

    api_url = (
        f"https://api.github.com/repos/"
        f"{info['owner']}/{info['repo']}"
        f"/pulls/{info['number']}"
    )

    response = requests.get(
        api_url,
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    return {
        "owner": info["owner"],
        "repo": info["repo"],
        "number": info["number"],
        "clone_url": data["base"]["repo"]["clone_url"],
        "head_branch": data["head"]["ref"],
        "head_sha": data["head"]["sha"],
        "base_branch": data["base"]["ref"],
    }


def clone_pr_repository(
    pr_url: str,
) -> str:
    """
    Clone the repository and checkout the PR branch.

    Returns the local repository path.
    """

    metadata = get_pr_metadata(pr_url)

    temp_directory = tempfile.mkdtemp(
        prefix="review_ai_"
    )

    repository_path = Path(temp_directory)

    Repo.clone_from(
        metadata["clone_url"],
        repository_path,
        branch=metadata["head_branch"],
        depth=1,
    )

    return str(repository_path)