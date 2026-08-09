from src.open_ai_client import ask
from src.rag import retrieve


def create_prompt(
    changed_code: str,
    relevant_documents,
) -> str:
    """
    Build the AI review prompt.
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

Review ONLY the changed Ruby code provided below.

Your goal is to identify meaningful engineering
problems rather than harmless stylistic differences.

Analyze:

1. Security
2. Performance
3. Ruby on Rails best practices
4. Maintainability
5. Code smells
6. Testing

Use the retrieved engineering guidelines
as supporting context.

IMPORTANT:

- Only report issues supported by the code.
- Do not invent problems.
- Do not report generic recommendations unless
  they are relevant to this change.
- Explain why each issue matters.
- Provide a concrete recommendation.
- Reference the relevant knowledge source.
- Distinguish between actual problems and suggestions.

RETRIEVED ENGINEERING GUIDELINES
================================

{knowledge}


CHANGED RUBY CODE
=================

{changed_code}


Return the review using this structure:

# Overall Review

## Summary

Briefly summarize what changed.

## Issues

For every issue:

### [Severity] Issue title

Category:
Security / Performance / Rails /
Maintainability / Testing

File:
...

Explanation:
...

Recommendation:
...

Reference:
...

## Positive Findings

Mention good implementation decisions.

## Final Assessment

Overall score: X/100

Explain the score.
"""


def review(
    changed_code: str,
    db,
) -> str:
    """
    Review changed Ruby code using RAG + OpenAI.
    """

    relevant_documents = retrieve(
        db,
        changed_code,
    )

    prompt = create_prompt(
        changed_code=changed_code,
        relevant_documents=relevant_documents,
    )

    return ask(prompt)