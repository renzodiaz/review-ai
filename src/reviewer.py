from src.open_ai_client import ask
from src.rag import retrieve

def create_prompt(diff: str, relevant_documents) -> str:
    """
    Build the prompt using the Pull Request
    and retrieved RAG context.
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
performing a Pull Request review.

Review the following Pull Request.

Your goal is to identify meaningful engineering
problems, not harmless stylistic differences.

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

- Only report issues reasonably supported by the code.
- Do not invent problems.
- Explain why each issue matters.
- Give a concrete recommendation.
- Mention the knowledge source when relevant.
- If no issue exists in a category, do not invent one.

RETRIEVED ENGINEERING GUIDELINES
================================

{knowledge}


PULL REQUEST DIFF
=================

{diff}


Return the review using this structure:

# Overall Review

## Summary

Brief summary.

## Issues

For each issue:

### [Severity] Issue title

Category:
Security / Performance / Rails /
Maintainability / Testing

Explanation:
...

Recommendation:
...

Reference:
...

## Positive Findings

Mention things implemented well.

## Final Assessment

Give an overall score from 0 to 100.
Explain the score.
"""


def review(
    diff: str,
    db,
) -> str:
    """
    Review a Pull Request using RAG + OpenAI.
    """

    relevant_documents = retrieve(
        db,
        diff,
    )

    prompt = create_prompt(
        diff=diff,
        relevant_documents=relevant_documents,
    )

    return ask(prompt)