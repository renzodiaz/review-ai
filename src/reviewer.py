from src.open_ai_client import ask
from src.rag import retrieve


def create_prompt(
    changed_code: str,
    relevant_documents,
    rubocop_context: str,
) -> str:
    """
    Build the final AI review prompt.
    """

    knowledge = "\n\n".join(
        (
            f"Source: {document.metadata.get('source')}\n"
            f"{document.page_content}"
        )
        for document in relevant_documents
    )

    return f"""
You are a Senior Ruby on Rails Engineer
performing a Pull Request code review.

You have three sources of information:

1. Changed Ruby code
2. Retrieved engineering guidelines
3. Static analysis results from RuboCop

Use all three as evidence.

Do not blindly trust static analysis.
Determine whether each finding is actually
important to the Pull Request.

Focus on meaningful engineering problems.

Analyze:

- Security
- Performance
- Rails best practices
- Maintainability
- Code smells
- Testing

IMPORTANT:

- Only report issues supported by evidence.
- Do not invent vulnerabilities.
- Do not report harmless stylistic differences
  as serious problems.
- Explain why each issue matters.
- Provide concrete recommendations.
- Reference the source of the finding.

========================
RETRIEVED KNOWLEDGE
========================

{knowledge}


========================
CHANGED RUBY CODE
========================

{changed_code}


========================
RUBOCOP RESULTS
========================

{rubocop_context}


========================
OUTPUT
========================

# Overall Review

## Summary

Briefly describe what the Pull Request changes.

## Issues

For each issue:

### [Severity] Issue title

Category:
Security / Performance / Rails /
Maintainability / Testing / Style

File:
...

Line:
...

Explanation:
...

Recommendation:
...

Evidence:
RAG / RuboCop / Code Analysis

Reference:
...

## Positive Findings

Mention good engineering decisions.

## Final Assessment

Overall score: X/100

Explain the score.
"""


def review(
    changed_code: str,
    db,
    rubocop_context: str = "No RuboCop results.",
) -> str:
    """
    Run RAG + RuboCop + OpenAI review.
    """

    relevant_documents = retrieve(
        db,
        changed_code,
    )

    prompt = create_prompt(
        changed_code=changed_code,
        relevant_documents=relevant_documents,
        rubocop_context=rubocop_context,
    )

    return ask(prompt)