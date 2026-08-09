# Ruby on Rails Active Record Guidelines

## Models

Models should represent domain data and important business rules.

Keep models focused on persistence, validations, associations, and simple domain behavior.

Avoid putting large workflows or application orchestration inside models.

## Validations

Important business validations should be defined at the model level when they are database-independent.

Validations should have automated tests.

Do not rely only on controller-level validation.

## Associations

Define associations explicitly using the appropriate Active Record association.

Use `dependent:` behavior deliberately when deleting or modifying associated records.

Association behavior that can delete or modify data should have automated tests.

## Database Constraints

Important data integrity rules should be enforced at the database level when possible.

Use database constraints for rules such as:

- uniqueness
- foreign keys
- non-null requirements
- check constraints

Application-level validations should not be considered a replacement for database constraints when concurrent writes are possible.

## Queries

Avoid N+1 queries.

Use the appropriate eager-loading strategy:

- `includes` for general eager loading
- `preload` when separate queries are preferred
- `eager_load` when joins are required

Only load the data required by the operation.

Avoid unnecessary queries inside loops.

## Scopes

Scopes should be:

- readable
- composable
- focused on querying

Avoid scopes containing complex business workflows.

Prefer explicit query objects or service objects when query logic becomes difficult to understand.

## Transactions

Use database transactions when multiple database operations must succeed or fail together.

Transactions should be kept as small as practical.

Do not perform slow external API calls inside a database transaction unless there is a specific reason.

## Callbacks

Use callbacks only for simple behavior that is intrinsic to the model lifecycle.

Avoid callbacks for complex business workflows.

Avoid callbacks that:

- call external services
- enqueue complex workflows
- perform unexpected database writes
- contain significant business logic

Prefer explicit service objects for complex workflows.

## Concurrency

Code that updates shared records must consider concurrent requests.

Use appropriate database locking when required.

Consider:

- optimistic locking
- pessimistic locking
- unique database constraints
- atomic updates

Do not assume application-level checks are safe under concurrent writes.

## Performance

Avoid loading large datasets into memory unnecessarily.

Prefer:

- `find_each`
- `in_batches`
- `pluck`
- `select`
- database-side aggregation

when appropriate.

Do not use Ruby iteration when the database can efficiently perform the operation.

## Migrations

Migrations should be:

- small
- reversible when practical
- safe for production data
- explicit about data changes

Avoid long-running migrations that block production traffic.

Consider backward-compatible database changes for applications deployed without downtime.

## Testing

Important Active Record behavior should have automated tests.

Tests should cover:

- validations
- associations
- business rules
- database constraints
- scopes
- concurrency-sensitive behavior
- important callbacks

When fixing an Active Record-related bug, add a regression test when practical.