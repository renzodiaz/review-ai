import requests

def download_pr(pr_url: str) -> str:
    """
    Download the unified diff for a GitHub Pull Request.

    Example:
        https://github.com/rails/rails/pull/123

    becomes:
        https://github.com/rails/rails/pull/123.diff
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
    Download a diff directly from a URL.
    """

    response = requests.get(
        diff_url,
        timeout=30,
    )

    response.raise_for_status()

    return response.text