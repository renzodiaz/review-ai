import time
import gradio as gr

from src.aggregator import merge_review, rubocop_to_issues
from src.github import (
    clone_pr_repository,
    download_pr,
    get_pr_metadata,
    parse_pr_url,
)
from src.parser import parse_diff
from src.rag import load_vector_db
from src.reviewer import review
from src.rubocop import format_offenses, run_rubocop


# Build the RAG database once when the application starts.
print("Building RAG vector database...")
DB = load_vector_db()
print("RAG vector database ready.")


def review_pull_request(pr_url: str) -> str:
    """
    Run the complete Pull Request review pipeline.
    """

    if not pr_url or not pr_url.strip():
        return "❌ Please enter a GitHub Pull Request URL."

    start_time = time.perf_counter()

    try:
        # ---------------------------------------------------------
        # 1. Validate PR URL
        # ---------------------------------------------------------

        pr_info = parse_pr_url(pr_url)

        # ---------------------------------------------------------
        # 2. Get PR metadata
        # ---------------------------------------------------------

        metadata = get_pr_metadata(pr_url)

        # ---------------------------------------------------------
        # 3. Download PR diff
        # ---------------------------------------------------------

        diff = download_pr(pr_url)

        # ---------------------------------------------------------
        # 4. Parse diff
        # ---------------------------------------------------------

        parsed = parse_diff(diff)

        changed_code = parsed["added_ruby_code"]

        if not changed_code.strip():
            return (
                "## ℹ️ No Ruby code found\n\n"
                "This Pull Request does not contain "
                "changed Ruby code that can be reviewed."
            )

        # ---------------------------------------------------------
        # 5. Clone repository
        # ---------------------------------------------------------

        repo_path = clone_pr_repository(pr_url)

        # ---------------------------------------------------------
        # 6. Run RuboCop
        # ---------------------------------------------------------

        ruby_files = [
            file["filename"]
            for file in parsed["ruby_files"]
        ]

        offenses = run_rubocop(
            project_path=repo_path,
            files=ruby_files,
        )

        rubocop_context = format_offenses(offenses)

        # ---------------------------------------------------------
        # 7. Convert RuboCop findings
        # ---------------------------------------------------------

        static_issues = rubocop_to_issues(
            offenses
        )

        # ---------------------------------------------------------
        # 8. Run AI + RAG review
        # ---------------------------------------------------------

        ai_result = review(
            changed_code=changed_code,
            db=DB,
            rubocop_context=rubocop_context,
        )

        # ---------------------------------------------------------
        # 9. Merge AI + RuboCop findings
        # ---------------------------------------------------------

        final_result = merge_review(
            ai_result=ai_result,
            static_issues=static_issues,
        )

        # ---------------------------------------------------------
        # 10. Format result for Gradio
        # ---------------------------------------------------------

        elapsed_seconds = time.perf_counter() - start_time

        return format_review(
            result=final_result,
            pr_info=pr_info,
            parsed=parsed,
            offenses=offenses,
            elapsed_seconds=elapsed_seconds,
        )

    except Exception as error:
        return (
            "## ❌ Review failed\n\n"
            f"```text\n{error}\n```"
        )


def format_review(
    result,
    pr_info,
    parsed,
    offenses,
    elapsed_seconds,
) -> str:
    """
    Convert ReviewResult into a human-readable Markdown report.
    """

    output = []

    output.append("# 🤖 Ruby Pull Request Review")
    output.append("")

    output.append(
        f"**Repository:** "
        f"`{pr_info['owner']}/{pr_info['repo']}`"
    )

    output.append(
        f"**Pull Request:** `#{pr_info['number']}`"
    )

    output.append(
        f"**AI review time:** `{elapsed_seconds:.2f} seconds`"
    )

    output.append("")

    # -------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------

    output.append("## 📊 Summary")
    output.append("")

    output.append(
        f"**Score:** `{result.score}/100`"
    )

    output.append(
        f"**Changed files:** "
        f"`{len(parsed['changed_files'])}`"
    )

    output.append(
        f"**Ruby files:** "
        f"`{len(parsed['ruby_files'])}`"
    )

    output.append(
        f"**Test files:** "
        f"`{len(parsed['test_files'])}`"
    )

    output.append(
        f"**RuboCop offenses:** "
        f"`{len(offenses)}`"
    )

    output.append("")

    output.append("### Summary")
    output.append("")
    output.append(result.summary)
    output.append("")

    # -------------------------------------------------------------
    # Issues
    # -------------------------------------------------------------

    if result.issues:
        output.append("## 🚨 Issues")
        output.append("")

        for index, issue in enumerate(
            result.issues,
            start=1,
        ):
            output.append(
                f"### {index}. "
                f"{severity_icon(issue.severity)} "
                f"{issue.title}"
            )

            output.append("")

            output.append(
                f"**Severity:** `{issue.severity}`"
            )

            output.append(
                f"**Type:** `{issue.type}`"
            )

            output.append(
                f"**Category:** `{issue.category}`"
            )

            if issue.file:
                output.append(
                    f"**File:** `{issue.file}`"
                )

            if issue.line:
                output.append(
                    f"**Line:** `{issue.line}`"
                )

            output.append("")

            output.append("**Explanation**")
            output.append("")
            output.append(issue.explanation)

            output.append("")

            output.append("**Recommendation**")
            output.append("")
            output.append(issue.recommendation)

            if issue.evidence:
                output.append("")
                output.append(
                    "**Evidence:** "
                    + ", ".join(
                        f"`{item}`"
                        for item in issue.evidence
                    )
                )

            output.append("")
            output.append("---")
            output.append("")

    else:
        output.append(
            "## ✅ No significant issues detected"
        )
        output.append("")

    # -------------------------------------------------------------
    # Positive findings
    # -------------------------------------------------------------

    if result.positive_findings:
        output.append("## ✅ Positive Findings")
        output.append("")

        for finding in result.positive_findings:
            output.append(f"- {finding}")

        output.append("")

    # -------------------------------------------------------------
    # RuboCop
    # -------------------------------------------------------------

    output.append("## 🔧 RuboCop")
    output.append("")

    if offenses:
        output.append(
            f"RuboCop detected "
            f"**{len(offenses)} offense(s)**."
        )
    else:
        output.append(
            "✅ No RuboCop offenses detected."
        )

    output.append("")

    # -------------------------------------------------------------
    # RAG sources context
    # -------------------------------------------------------------

    if result.rag_sources:
        output.append("## 🧠 RAG Context")
        output.append("")

        for source in result.rag_sources:
            output.append(f"- 📚 `{source}`")

        output.append("")

    # -------------------------------------------------------------
    # Architecture evidence
    # -------------------------------------------------------------

    output.append("## 🧠 AI Pipeline")
    output.append("")

    output.append(
        "```text\n"
        "GitHub PR\n"
        "   ↓\n"
        "Diff Parser\n"
        "   ↓\n"
        "Ruby Code\n"
        "   ↓\n"
        "RAG / FAISS\n"
        "   ↓\n"
        "RuboCop + OpenAI\n"
        "   ↓\n"
        "Pydantic ReviewResult\n"
        "   ↓\n"
        "Final Review\n"
        "```"
    )

    return "\n".join(output)


def severity_icon(severity: str) -> str:
    """
    Return a visual indicator for issue severity.
    """

    icons = {
        "critical": "🔴",
        "high": "🔴",
        "medium": "🟠",
        "low": "🟡",
    }

    return icons.get(
        severity,
        "⚪",
    )


demo = gr.Interface(
    fn=review_pull_request,
    inputs=gr.Textbox(
        label="GitHub Pull Request URL",
        placeholder=(
            "https://github.com/owner/repository/pull/123"
        ),
    ),
    outputs=gr.Markdown(),
    title="🤖 AI Ruby Pull Request Reviewer",
    description=(
        "Automated Ruby/Rails code review using "
        "OpenAI + RAG + FAISS + RuboCop."
    ),
)


if __name__ == "__main__":
    demo.launch(
        share=True
    )