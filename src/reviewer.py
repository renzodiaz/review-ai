from src.open_ai_client import ask
from src.rag import retrieve

def create_prompt(diff: str, rules: list[dict]) -> str:
    """
    Build the prompt used by the AI reviewer.
    """

    formatted_rules = "\n\n".join(
        f"[{rule['category']}]\n{rule['rule']}"
        for rule in rules
    )

    return f"""
You are a Senior Ruby on Rails Engineer performing
a Pull Request code review.

Review the following Pull Request.

Your job is to identify meaningful engineering problems,
not to complain about harmless stylistic differences.

Review for:

1. Security
2. Performance
3. Ruby on Rails best practices
4. Maintainability
5. Code smells
6. Testing

Use the provided engineering guidelines as context.

IMPORTANT:
- Only report issues that are reasonably supported by the code.
- Do not invent problems.
- Explain why each issue matters.
- Give a concrete recommendation.
- If the code looks good, say so.

ENGINEERING GUIDELINES
======================

{formatted_rules}


PULL REQUEST DIFF
=================

{diff}


Return the review using this structure:

# Overall Review

## Summary

Brief summary of the Pull Request.

## Issues

For every issue provide:

### [Severity] Issue title

Category:
Security / Performance / Rails / Maintainability / Testing

Explanation:
...

Recommendation:
...

## Positive Findings

Mention things that were implemented well.

## Final Assessment

Give an overall score from 0 to 100 and explain the score.
"""


def review(diff: str, db) -> str:
    """
    Review a Pull Request using the knowledge base
    and OpenAI.
    """

    rules = retrieve(db, diff)

    prompt = create_prompt(
        diff=diff,
        rules=rules,
    )

    return ask(prompt)