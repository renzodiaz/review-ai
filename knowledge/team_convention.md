# Team Coding Conventions

## General Principles

Code should prioritize:

- readability
- maintainability
- correctness
- simplicity
- consistency

Prefer straightforward solutions over clever implementations.

Follow existing project conventions unless there is a clear reason to change them.

## Naming

Use descriptive names for classes, methods, variables, and constants.

Names should communicate intent rather than implementation details.

Avoid abbreviations unless they are well-established domain terminology.

## Methods

Methods should have one clear responsibility.

Prefer small, focused methods.

Avoid methods that mix:

- validation
- business logic
- persistence
- external API calls
- presentation logic

Extract responsibilities when a method becomes difficult to understand or test.

## Classes

Classes should have a clear responsibility.

Avoid creating classes that contain unrelated functionality.

Use service objects, query objects, or other abstractions when application logic does not naturally belong in a model or controller.

Do not introduce abstractions prematurely.

## Controllers

Controllers should remain thin.

Controllers should primarily:

- receive the request
- authorize the operation
- validate request-level input
- invoke the appropriate application logic
- return the response

Avoid placing complex business logic inside controllers.

## Models

Models should contain domain behavior that naturally belongs in the model.

Avoid using models as containers for large application workflows.

Use service objects when behavior involves multiple domain objects or external systems.

## Service Objects

Service objects should represent meaningful application operations.

Prefer explicit interfaces.

For example:

Orders::Create.call(...)
Orders::Cancel.call(...)

Avoid creating service objects for trivial one-line operations.

## Error Handling

Handle expected errors explicitly.

Do not silently rescue exceptions.

Avoid broad exception handling such as:

rescue StandardError

unless there is a clear reason to handle all standard errors.

Errors should provide enough context to diagnose the problem.

## Database Operations

Use transactions when multiple database changes must succeed or fail together.

Consider race conditions when implementing operations involving:

- balances
- counters
- inventory
- uniqueness
- state transitions

Use database constraints and locking where appropriate.

## External Services

External API calls should be isolated from core domain logic when practical.

External integrations should handle:

- timeouts
- transient failures
- unexpected responses
- retries when appropriate

Do not assume external services are always available.

## Background Jobs

Background jobs should be safe to retry.

Jobs should be designed to be idempotent when practical.

Do not place large amounts of business logic directly inside job classes.

Jobs should delegate business operations to application or service objects.

## Testing

Important business behavior should have automated tests.

Tests should verify behavior rather than implementation details.

Prefer testing public interfaces and observable outcomes.

When fixing a bug, add a regression test when practical.

## Code Duplication

Avoid unnecessary duplication.

Do not abstract code solely because two pieces of code look similar.

Extract shared behavior when the code represents the same concept or business rule.

## Comments

Prefer self-explanatory code.

Use comments to explain why something exists or why a non-obvious decision was made.

Do not use comments to compensate for unclear code.

## Pull Requests

Pull requests should:

- have a clear purpose
- contain focused changes
- include appropriate tests
- avoid unrelated refactoring
- avoid unnecessary formatting changes

Large refactors should be separated from unrelated feature or bug-fix changes when practical.

## Commits

Commits should represent logical changes.

Avoid mixing unrelated changes in the same commit.

Commit messages should clearly describe the change.

## Dependencies

Do not add a dependency when the existing Rails or Ruby ecosystem already provides a simple solution.

New dependencies should have a clear benefit and should be actively maintained.

## Security

Never commit:

- passwords
- API keys
- access tokens
- private credentials
- sensitive production data

Validate and authorize user-controlled input.

Do not assume authentication implies authorization.

## Performance

Do not optimize based only on assumptions.

Identify the actual bottleneck before introducing complexity.

Pay particular attention to:

- N+1 queries
- unnecessary database queries
- excessive object allocation
- large in-memory collections
- unnecessary external API calls

## Consistency

When modifying existing code, follow the conventions already established in that area of the codebase.

Consistency should generally be preferred over introducing a new pattern for a single feature.