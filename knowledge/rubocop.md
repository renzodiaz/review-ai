# Ruby RuboCop Guidelines

## General

Ruby code should follow the project's configured RuboCop rules.

Run RuboCop before submitting changes.

Do not disable a RuboCop rule without a clear reason.

## Style

Prefer readable and idiomatic Ruby.

Follow the project's existing conventions for:

- naming
- method structure
- class structure
- formatting
- string literals
- collections
- conditionals

Consistency within the codebase is more important than personal style preferences.

## Methods

Methods should have a clear and focused responsibility.

Avoid unnecessarily long methods.

Prefer simple control flow over deeply nested conditionals.

Extract complex logic when doing so improves readability.

## Complexity

Avoid unnecessary:

- deeply nested conditionals
- large methods
- large classes
- complex boolean expressions
- excessive branching

Do not blindly extract code only to satisfy a metric. The resulting code should remain easier to understand.

## Naming

Use descriptive names for:

- methods
- variables
- classes
- modules
- constants

Avoid unclear abbreviations unless they are established domain terminology.

## Comments

Prefer clear code over comments explaining obvious implementation details.

Use comments when explaining:

- non-obvious business rules
- technical constraints
- workarounds
- decisions that future developers may question

Comments should explain why, not simply repeat what the code does.

## Disabled Rules

Avoid inline RuboCop disables unless necessary.

When disabling a rule, keep the scope as small as possible.

Prefer:

# rubocop:disable Some/Cop

only around the code that requires the exception.

Document the reason when the exception is not obvious.

## Configuration

Changes to `.rubocop.yml` should be intentional.

Do not weaken project-wide rules simply to make individual code changes pass.

If a rule creates a legitimate project-wide problem, discuss the configuration change with the team.

## Auto-correction

Use RuboCop auto-correction when the change is safe.

Review automatically corrected code before committing it.

Do not blindly commit large formatting changes together with functional changes.

## Pull Requests

A pull request should not introduce new RuboCop violations.

Existing violations may be addressed separately unless they are directly related to the change.

Avoid mixing unrelated formatting changes with business logic changes.

## Testing

RuboCop compliance does not replace automated tests.

Code should satisfy both:

- project style and quality rules
- appropriate automated test coverage