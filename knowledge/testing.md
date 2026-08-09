# Ruby on Rails Testing Guidelines

## Business Logic

Changes to important business behavior should have automated tests.

## Authentication

Authentication changes should include tests for:

- successful authentication
- invalid credentials
- unauthorized access

## Authorization

Authorization changes should verify both:

- authorized users can perform the operation
- unauthorized users cannot perform the operation

## Regression Testing

When fixing a bug, add a test that reproduces the bug when practical.

## Controllers

Controller or request behavior should be covered by appropriate
request or integration tests.

## Models

Important model validations and business rules should have automated
tests.