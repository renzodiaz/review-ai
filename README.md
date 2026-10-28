# Review AI — Ruby on Rails Pull Request Reviewer

An AI agent that reviews **Ruby on Rails** pull requests. It pulls the diff from a
GitHub PR, runs it through a retrieval-augmented LLM review grounded in a curated
engineering knowledge base, cross-checks it with **RuboCop** static analysis, and
returns a structured, scored report — surfaced through a Gradio web UI.

The project also ships a small **evaluation harness** with labelled benchmark cases
so the agent's quality (precision / recall / F1) can be measured, not just asserted.

---

## How it works

```
GitHub PR URL
     │
     ▼
 github.py        download diff + metadata, shallow-clone the PR branch
     │
     ▼
 parser.py        split the unified diff into files / hunks, isolate added Ruby code
     │
     ├────────────────────────────┐
     ▼                             ▼
 rubocop.py                    rag.py
 run RuboCop on the            embed the knowledge base (FAISS) and
 changed files                 retrieve the most relevant guidelines
     │                             │
     └──────────────┬──────────────┘
                    ▼
              reviewer.py
   build a structured prompt (code + retrieved knowledge + RuboCop)
   and ask the LLM for a typed ReviewResult (Pydantic schema)
                    │
                    ▼
             aggregator.py
   merge LLM findings with RuboCop offenses, de-duplicate
                    │
                    ▼
             gradio_app.py
   render an HTML report (score, issues, evidence, sources)
```

### Key ideas

- **Grounded, not generic.** The LLM is given relevant excerpts retrieved from a
  knowledge base (`knowledge/*.md`: Rails, Active Record, security, performance,
  testing, clean code, RuboCop, team conventions) so reviews cite your standards
  instead of inventing generic advice.
- **LLM + static analysis.** RuboCop offenses are normalized into the same
  `ReviewIssue` schema as the LLM findings and merged, so style/lint and
  higher-level engineering concerns live in one report.
- **Structured output.** The model returns a validated Pydantic object
  (`ReviewResult`) — a summary, a 0–100 score, typed/severity-tagged issues with
  evidence and recommendations, and positive findings — not free text.
- **Measurable.** The evaluation harness runs labelled cases and reports
  precision, recall, F1, success rate, reliability, and average latency.

---

## Project layout

| Path | Purpose |
|------|---------|
| `src/github.py` | Parse PR URLs, download diffs, clone the PR branch |
| `src/parser.py` | Split a git diff into files/hunks; extract changed Ruby code |
| `src/rag.py` | Build the FAISS vector store and retrieve relevant knowledge |
| `src/rubocop.py` | Run RuboCop and format offenses |
| `src/reviewer.py` | Build the review prompt and call the LLM for structured output |
| `src/aggregator.py` | Merge + de-duplicate LLM and RuboCop findings |
| `src/schema.py` | Pydantic models (`ReviewIssue`, `ReviewResult`) |
| `src/evaluator.py` | Benchmark harness and metrics |
| `src/gradio_app.py` | Web UI and end-to-end pipeline |
| `src/open_ai_client.py` | Thin OpenAI client wrapper |
| `src/config.py` | Model, embedding, and chunking settings |
| `knowledge/` | Markdown knowledge base used for retrieval |
| `evaluation/` | Benchmark cases and expected findings |
| `notebook.ipynb` | Exploratory / step-by-step walkthrough |

---

## Setup

Requirements: **Python 3.10+** and **Ruby + RuboCop** on your `PATH`
(`gem install rubocop`) if you want static-analysis findings.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=sk-...
GITHUB_TOKEN=ghp_...   # optional: raises GitHub rate limits / enables private PRs
```

> The embedding model (`sentence-transformers/all-MiniLM-L6-v2`) is downloaded
> locally on first run; embeddings and retrieval run on your machine. Only the
> review prompt is sent to OpenAI.

---

## Usage

### Web UI

```bash
python -m src.gradio_app
```

Paste a GitHub PR URL (e.g. `https://github.com/owner/repo/pull/123`) and run the
review. The app builds the knowledge vector store once at startup, then for each PR
it downloads the diff, runs RuboCop, retrieves relevant guidelines, and renders a
scored HTML report.

### As a library

```python
from src.rag import load_vector_db
from src.reviewer import review

db = load_vector_db()
result = review(changed_code=my_ruby_diff, db=db)

print(result.score)
for issue in result.issues:
    print(issue.severity, issue.type, "-", issue.title)
```

---

## Evaluation

The `evaluation/` directory contains ten benchmark cases — vulnerable/problematic
changes (N+1 queries, SQL injection, missing authorization, mass assignment, race
conditions, …) and clean controls — each labelled in
`evaluation/expected_findings.json`.

```python
from src.rag import load_vector_db
from src.evaluator import run_benchmark, compute_metrics

db = load_vector_db()
metrics = compute_metrics(run_benchmark(db))
print(metrics)   # precision, recall, f1, success_rate, reliability, avg_latency_seconds
```

A case with expected issues passes only if **every** expected type is detected; a
clean case passes only if **nothing** is flagged (no false positive). This keeps the
agent honest about both missed issues and noise.

---

## Security & threat model

A code-review agent consumes **untrusted input by design**: the diff and
RuboCop output come from whoever opened the pull request. The agent treats them
accordingly.

- **Prompt injection.** The changed code and RuboCop results are fenced inside
  the prompt and the model is instructed to treat them strictly as data, never
  as instructions ([`src/reviewer.py`](src/reviewer.py)). The fence delimiters
  are stripped from the untrusted content first, so an author cannot close the
  fence and append their own instructions ([`src/sanitize.py`](src/sanitize.py)).
- **Defense in depth on the output.** Independently of the model, the untrusted
  code is scanned for injection phrases; if any are found, the review reports a
  security issue and the score is capped so a manipulated "100 / no issues"
  result cannot pass silently ([`validate_result`](src/reviewer.py)).

Known hardening still worth doing (good next steps): sandbox the clone + RuboCop
run (RuboCop can execute code via a repo's `.rubocop.yml require:`), gate the
public Gradio share link behind an env flag, cap diff size, and clean up the
temp clone directory.

## Testing

Deterministic unit tests cover the pure logic — diff parsing, finding
de-duplication / severity mapping, the injection sanitizer, and the output
guard:

```bash
pip install pytest
pytest -q
```

## Configuration

Tunable in `src/config.py`:

| Setting | Default | Meaning |
|---------|---------|---------|
| `OPENAI_MODEL` | `gpt-5.4-mini` | LLM used for the review |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Local sentence-transformer for retrieval |
| `TOP_K` | `5` | Knowledge chunks retrieved per review |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` | `500` / `50` | Knowledge chunking |

To extend the agent's standards, drop more Markdown files into `knowledge/` — they
are picked up automatically when the vector store is built.

---

## Tech stack

OpenAI · LangChain · FAISS · sentence-transformers · Pydantic · RuboCop · GitPython · Gradio
