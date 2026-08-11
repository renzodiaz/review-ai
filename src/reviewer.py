from src.open_ai_client import ask_structured
from src.rag import retrieve
from src.schema import ReviewResult


def create_prompt(
    changed_code: str,
    relevant_documents,
    rubocop_context: str,
) -> str:
    """
    Build the structured review prompt.
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

Analyze the changed Ruby code using:

1. The code itself
2. Retrieved engineering guidelines
3. RuboCop static analysis

Your goal is to identify meaningful engineering
problems.

Focus on:

- Security
- Performance
- Rails best practices
- Maintainability
- Team Convention
- Testing
- Style when it has meaningful impact

IMPORTANT RULES:

- Do not invent issues.
- Do not report generic advice.
- Only report problems supported by evidence.
- Do not blindly trust RuboCop.
- Distinguish real engineering problems from
  harmless style preferences.
- Prefer fewer high-confidence issues over many
  speculative issues.
- The score should reflect the severity and number
  of meaningful issues.

RETRIEVED KNOWLEDGE
===================

{knowledge}


CHANGED RUBY CODE
=================

{changed_code}


RUBOCOP RESULTS
===============

{rubocop_context}

Every issue must have a normalized type.

Use one of these types when applicable:

- n_plus_one
- sql_injection
- authorization
- authentication
- missing_test
- validation_bypass
- mass_assignment
- insecure_file_access
- race_condition
- inefficient_query
- error_handling
- maintainability
- code_duplication
- style

If none applies, use:

other


SCORING GUIDELINES
==================

90-100:
Excellent change with no meaningful issues.

80-89:
Good change with minor concerns.

70-79:
Acceptable but contains meaningful issues.

50-69:
Significant engineering problems.

0-49:
Critical problems or unsafe implementation.

Return only the structured review.
"""


def review(
    changed_code: str,
    db,
    rubocop_context: str = "No RuboCop results.",
) -> ReviewResult:
    """
    Run RAG + RuboCop + OpenAI.
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

    result = ask_structured(
        prompt,
        ReviewResult,
    )

    rag_sources = []

    for document in relevant_documents:
        source = document.metadata.get("source")

        if source and source not in rag_sources:
            rag_sources.append(source)

    result.rag_sources = rag_sources

    return result