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

You are reviewing a Git diff.

The diff contains:

- the file name
- the changed lines
- removed code
- surrounding context
- Git hunk information

Focus primarily on the NEW code.

Use removed code and context to understand
the behavioral change.

Analyze:

1. Security
2. Performance
3. Ruby on Rails best practices
4. Maintainability
5. Code smells
6. Testing

IMPORTANT RULES:

- Only report issues supported by the code.
- Do not invent vulnerabilities.
- Do not report harmless stylistic preferences.
- Explain why the issue matters.
- Provide a concrete recommendation.
- Reference the relevant knowledge source.
- If no significant problem exists, say so.

RETRIEVED ENGINEERING KNOWLEDGE
===============================

{knowledge}


PULL REQUEST CHANGES
====================

{changed_code}


Return:

# Overall Review

## Summary

Briefly describe what the PR changes.

## Issues

For each issue:

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

List good engineering decisions.

## Final Assessment

Overall score: X/100

Explain the score.
"""



def review(
    changed_code: str,
    db,
) -> str:
    """
    Run the RAG + OpenAI review.
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