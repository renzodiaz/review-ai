# Clean Code Guidelines

## Single Responsibility

A method or class should have a focused responsibility.

Large methods performing unrelated operations should be considered
for refactoring.

## Naming

Use meaningful names that communicate intent.

Avoid vague names such as:

data
thing
x
tmp

when a more descriptive name is possible.

## Duplication

Avoid unnecessary duplication.

If the same business logic appears in several places, consider
extracting a reusable abstraction.

## Complexity

Avoid deeply nested conditionals.

Prefer early returns or smaller methods when they make the code easier
to understand.

## Abstractions

Do not introduce abstractions without a meaningful reason.

The goal is maintainable code rather than maximizing the number of
classes or patterns.