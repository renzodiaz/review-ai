import html
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

# Custom css for UI
CUSTOM_CSS = """
.review-container,
.review-container * {
    color: initial;
}

.review-container {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    max-width: 900px;
    margin: 0 auto;
    color: #1f2328 !important;
    background: #ffffff;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.4);
}

/* Header */
.review-header {
    background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
    color: #fff !important;
    padding: 24px 28px;
    border-radius: 12px 12px 0 0;
}
.review-header h1 {
    margin: 0;
    font-size: 22px;
    color: #fff !important;
}
.review-header .subtitle {
    margin: 4px 0 0;
    color: #9ca3af !important;
    font-size: 14px;
}

/* Metadata row */
.metadata {
    display: flex;
    gap: 32px;
    background: #f9fafb;
    border-bottom: 1px solid #e5e7eb;
    padding: 14px 28px;
    font-size: 13px;
    color: #1f2328 !important;
}
.metadata strong {
    color: #6b7280 !important;
    font-weight: 500;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}

/* Metrics */
.metrics {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    padding: 20px 28px;
}
.metric {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    padding: 16px 8px;
    text-align: center;
}
.metric-value {
    font-size: 24px;
    font-weight: 700;
    color: #111827 !important;
}
.metric-label {
    font-size: 11px;
    color: #6b7280 !important;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    margin-top: 4px;
}
.metric.score-good .metric-value    { color: #16a34a !important; }
.metric.score-warning .metric-value { color: #d97706 !important; }
.metric.score-danger .metric-value  { color: #dc2626 !important; }

/* Sections */
.section {
    padding: 8px 28px 24px;
}
.section h2 {
    font-size: 17px;
    margin-bottom: 10px;
    border-bottom: 2px solid #f3f4f6;
    padding-bottom: 8px;
    color: #111827 !important;
}
.section p {
    color: #1f2328 !important;
}
.section .muted {
    color: #6b7280 !important;
    font-size: 13px;
    margin-top: -4px;
}

/* Issue cards */
.issue-card {
    border: 1px solid #e5e7eb;
    border-left: 4px solid #9ca3af;
    border-radius: 8px;
    padding: 16px 18px;
    margin-bottom: 14px;
    background: #fff;
}
.issue-card.severity-critical,
.issue-card.severity-high   { border-left-color: #dc2626; background: #fef2f2; }
.issue-card.severity-medium { border-left-color: #d97706; background: #fffbeb; }
.issue-card.severity-low    { border-left-color: #eab308; background: #fefce8; }

.issue-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 15px;
    margin-bottom: 8px;
    color: #111827 !important;
}
.issue-title strong {
    color: #111827 !important;
    font-weight: 600;
}

.issue-meta {
    display: flex;
    gap: 18px;
    font-size: 12px;
    color: #374151 !important;
    margin-bottom: 8px;
}
.issue-meta strong {
    color: #111827 !important;
}
.issue-meta code {
    background: #eef2ff;
    color: #4338ca !important;
    padding: 1px 6px;
    border-radius: 4px;
}

.issue-location {
    font-size: 12px;
    color: #4b5563 !important;
    margin-bottom: 8px;
}

.issue-card h4 {
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    color: #6b7280 !important;
    margin: 10px 0 4px;
}
.issue-card p {
    margin: 0;
    font-size: 14px;
    line-height: 1.5;
    color: #1f2328 !important;
}

.evidence {
    margin-top: 10px;
    font-size: 12px;
    color: #374151 !important;
}
.evidence strong {
    color: #111827 !important;
}
.evidence span {
    display: inline-block;
    background: #f3f4f6;
    color: #111827 !important;
    border-radius: 4px;
    padding: 2px 8px;
    margin: 2px 4px 2px 0;
    font-family: monospace;
}

/* Success card */
.success-card {
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-radius: 8px;
    padding: 16px 18px;
    text-align: center;
}
.success-card h2 {
    border: none;
    margin-bottom: 6px;
    color: #16a34a !important;
}
.success-card p {
    color: #166534 !important;
}

/* RAG sources */
.sources {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}
.source {
    background: #eef2ff;
    color: #4338ca !important;
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 12px;
}

/* RuboCop */
.rubocop-warning {
    background: #fffbeb;
    border: 1px solid #fde68a;
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 14px;
    color: #92400e !important;
}
.rubocop-warning strong {
    color: #78350f !important;
}

/* Pipeline */
.pipeline {
    padding: 8px 28px 28px;
}
.pipeline h2 {
    color: #111827 !important;
}
.pipeline-flow {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 14px;
    font-size: 13px;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    align-items: center;
    color: #374151 !important;
}
.pipeline-flow span {
    color: #9ca3af !important;
}

/* --- Outer page content (title block, status line) on dark theme --- */
.gradio-container .prose h1,
.gradio-container .prose h2,
.gradio-container .prose h3 {
    color: #f9fafb !important;
}
.gradio-container .prose p {
    color: #d1d5db !important;
}
"""

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

        return format_review_html(
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

def format_review_html(
    result,
    pr_info,
    parsed,
    offenses,
    elapsed_seconds,
):
    def escape(value):
        return html.escape(str(value))

    score = result.score

    if score >= 90:
        score_class = "score-good"
    elif score >= 70:
        score_class = "score-warning"
    else:
        score_class = "score-danger"

    output = f"""
    <div class="review-container">

        <div class="review-header">
            <div>
                <h1>🤖 Ruby Pull Request Review</h1>
                <p class="subtitle">
                    AI-assisted Ruby/Rails engineering review
                </p>
            </div>
        </div>

        <div class="metadata">
            <span>
                <strong>Repository</strong><br>
                {escape(pr_info["owner"])}/{escape(pr_info["repo"])}
            </span>

            <span>
                <strong>Pull Request</strong><br>
                #{escape(pr_info["number"])}
            </span>

            <span>
                <strong>Review time</strong><br>
                {elapsed_seconds:.2f}s
            </span>
        </div>

        <div class="metrics">

            <div class="metric {score_class}">
                <div class="metric-value">
                    {score}/100
                </div>
                <div class="metric-label">
                    Review Score
                </div>
            </div>

            <div class="metric">
                <div class="metric-value">
                    {len(parsed["changed_files"])}
                </div>
                <div class="metric-label">
                    Changed Files
                </div>
            </div>

            <div class="metric">
                <div class="metric-value">
                    {len(parsed["ruby_files"])}
                </div>
                <div class="metric-label">
                    Ruby Files
                </div>
            </div>

            <div class="metric">
                <div class="metric-value">
                    {len(offenses)}
                </div>
                <div class="metric-label">
                    RuboCop Offenses
                </div>
            </div>

        </div>

        <div class="section">
            <h2>📋 Summary</h2>
            <p>{escape(result.summary)}</p>
        </div>
    """

    # ---------------------------------------------------------
    # Issues
    # ---------------------------------------------------------

    if result.issues:
        output += """
        <div class="section">
            <h2>🚨 Issues Detected</h2>
        """

        for index, issue in enumerate(
            result.issues,
            start=1,
        ):
            severity = issue.severity.lower()

            if severity in ("critical", "high"):
                icon = "🔴"
            elif severity == "medium":
                icon = "🟠"
            else:
                icon = "🟡"

            output += f"""
            <div class="issue-card severity-{escape(severity)}">

                <div class="issue-title">
                    {icon}
                    <strong>
                        {index}. {escape(issue.title)}
                    </strong>
                </div>

                <div class="issue-meta">
                    <span>
                        Severity:
                        <strong>{escape(issue.severity)}</strong>
                    </span>

                    <span>
                        Type:
                        <code>{escape(issue.type)}</code>
                    </span>

                    <span>
                        Category:
                        <code>{escape(issue.category)}</code>
                    </span>
                </div>
            """

            if issue.file:
                output += f"""
                <div class="issue-location">
                    📁 {escape(issue.file)}
                """

                if issue.line:
                    output += f"""
                    &nbsp;&nbsp; Line {escape(issue.line)}
                    """

                output += "</div>"

            output += f"""
                <h4>Explanation</h4>
                <p>{escape(issue.explanation)}</p>

                <h4>Recommendation</h4>
                <p>{escape(issue.recommendation)}</p>
            """

            if issue.evidence:
                output += """
                <div class="evidence">
                    <strong>Evidence:</strong>
                """

                for evidence in issue.evidence:
                    output += (
                        f"<span>{escape(evidence)}</span>"
                    )

                output += "</div>"

            output += """
            </div>
            """

        output += "</div>"

    else:
        output += """
        <div class="success-card">
            <h2>✅ No Significant Issues Detected</h2>
            <p>
                The AI reviewer did not identify
                meaningful engineering problems.
            </p>
        </div>
        """

    # ---------------------------------------------------------
    # Positive findings
    # ---------------------------------------------------------

    if result.positive_findings:
        output += """
        <div class="section">
            <h2>✅ Positive Findings</h2>
            <ul>
        """

        for finding in result.positive_findings:
            output += (
                f"<li>{escape(finding)}</li>"
            )

        output += """
            </ul>
        </div>
        """

    # ---------------------------------------------------------
    # RAG
    # ---------------------------------------------------------

    if result.rag_sources:
        output += """
        <div class="section">
            <h2>🧠 RAG Knowledge Retrieved</h2>

            <p class="muted">
                Guidelines retrieved from the knowledge base
                and provided to the AI for contextual analysis.
            </p>

            <div class="sources">
        """

        for source in result.rag_sources:
            output += f"""
                <span class="source">
                    📚 {escape(source)}
                </span>
            """

        output += """
            </div>
        </div>
        """

    # ---------------------------------------------------------
    # RuboCop
    # ---------------------------------------------------------

    output += """
        <div class="section">
            <h2>🔧 Static Analysis</h2>
    """

    if offenses:
        output += f"""
            <div class="rubocop-warning">
                ⚠️ RuboCop detected
                <strong>{len(offenses)}</strong>
                offense(s).
            </div>
        """
    else:
        output += """
            <div class="success-card">
                ✅ No RuboCop offenses detected.
            </div>
        """

    output += """
        </div>

        <div class="pipeline">
            <h2>⚙️ Review Pipeline</h2>

            <div class="pipeline-flow">
                GitHub PR
                <span>→</span>
                Diff Parser
                <span>→</span>
                RAG / FAISS
                <span>→</span>
                RuboCop
                <span>→</span>
                OpenAI
                <span>→</span>
                Pydantic
                <span>→</span>
                Review
            </div>
        </div>

    </div>
    """

    return output

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


with gr.Blocks(
    title="AI Ruby Pull Request Reviewer",
    css=CUSTOM_CSS,
) as demo:

    gr.Markdown(
        """
        # 🤖 AI Ruby Pull Request Reviewer

        **Automated Ruby/Rails engineering review**

        🧠 OpenAI &nbsp; · &nbsp;
        🔎 RAG &nbsp; · &nbsp;
        🤗 Hugging Face &nbsp; · &nbsp;
        ⚡ FAISS &nbsp; · &nbsp;
        🔧 RuboCop &nbsp; · &nbsp;
        📋 Pydantic
        """
    )

    with gr.Row():

        with gr.Column(scale=4):

            pr_url = gr.Textbox(
                label="GitHub Pull Request URL",
                placeholder=(
                    "https://github.com/"
                    "owner/repository/pull/123"
                ),
            )

        with gr.Column(scale=1):

            review_button = gr.Button(
                "🔍 Review Pull Request",
                variant="primary",
                size="lg",
            )

    status = gr.Markdown(
        "🟢 Ready to review a Pull Request."
    )

    gr.Markdown("---")

    review_output = gr.HTML(
        label="Review Results"
    )

    review_button.click(
        fn=review_pull_request,
        inputs=pr_url,
        outputs=review_output,
        show_progress="full",
    )


if __name__ == "__main__":
    demo.launch(
        share=True
    )