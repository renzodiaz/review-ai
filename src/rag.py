KNOWLEDGE_BASE = [
    {
        "category": "Security",
        "rule": "Never compare passwords directly. "
                "Use secure password authentication such as "
                "has_secure_password and authenticate."
    },
    {
        "category": "Security",
        "rule": "Never use permit! for controller parameters. "
                "Explicitly permit only the parameters required."
    },
    {
        "category": "Security",
        "rule": "Avoid constructing SQL queries using string interpolation. "
                "Use Active Record parameterized queries."
    },
    {
        "category": "Performance",
        "rule": "Avoid N+1 queries. "
                "Use includes, preload, or eager_load when associations "
                "are accessed inside loops."
    },
    {
        "category": "Performance",
        "rule": "For processing large Active Record datasets, "
                "prefer find_each or find_in_batches instead of loading "
                "all records into memory."
    },
    {
        "category": "Rails",
        "rule": "Avoid update_attribute because it skips validations. "
                "Prefer update or update! when appropriate."
    },
    {
        "category": "Rails",
        "rule": "Keep controllers thin. "
                "Business logic that is complex or reusable should be "
                "moved into an appropriate domain or service object."
    },
    {
        "category": "Testing",
        "rule": "Changes to business-critical behavior should have "
                "appropriate automated tests."
    },
]

def load_vector_db():
    """
    Temporary knowledge-base implementation.

    In Milestone 2 this will be replaced by:
        Markdown files
        +
        Hugging Face embeddings
        +
        FAISS
    """

    return KNOWLEDGE_BASE

def retrieve(db, query: str) -> list[dict]:
    """
    Temporary retrieval implementation.

    For now we return all rules.

    Later this function will perform semantic similarity search
    using FAISS.
    """

    return db