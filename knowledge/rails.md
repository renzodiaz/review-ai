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

## Skipping Validations

Be cautious with methods that bypass validations and callbacks.

Bad:

user.update_column(:email, params[:email])
user.update_columns(email: params[:email])
user.save(validate: false)

These write directly to the database and skip the model's validations,
which can persist invalid or unsafe data.

Prefer methods that run validations unless there is a specific,
justified reason to skip them.

Good:

user.update(email: params[:email])

## Race Conditions

Avoid check-then-act patterns that can run concurrently and create
duplicates or inconsistent state.

Bad:

unless Account.exists?(email: email)
  Account.create!(email: email)
end

Two requests can both pass the check before either creates the record.

Prefer a database-level guarantee, such as a unique index combined with
an atomic method.

Good:

Account.find_or_create_by(email: email)

Counters that are read and then written are also vulnerable; prefer
atomic operations such as increment! or update_counters.

## Error Handling

Do not silently rescue and ignore errors.

Bad:

begin
  charge_customer(order)
rescue => e
end

Swallowing exceptions hides failures and makes debugging difficult.

Prefer rescuing specific errors and handling them explicitly, for
example by logging, reporting, or re-raising.