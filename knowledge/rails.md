# Ruby on Rails Best Practices

## Controllers

Controllers should remain thin.

Avoid putting complex business logic directly inside controller
actions.

When business logic becomes complex, consider extracting it into an
appropriate service or domain object.

## Active Record

Use Active Record methods that respect validations when updating
records.

Avoid update_attribute when validations should run.

Prefer:

user.update(name: "John")

## Callbacks

Avoid putting complex business workflows inside Active Record
callbacks.

Callbacks can make application behavior difficult to understand and
test.

Consider an explicit service or use case for complex workflows.

## Transactions

Operations that must succeed or fail together should be performed
inside a database transaction.

## Finders

Prefer expressive Active Record methods such as:

find_by
find_by!
exists?
where

over unnecessarily complex custom SQL when Active Record can express
the query safely and clearly.