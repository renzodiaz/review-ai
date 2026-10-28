# Ruby on Rails Performance Guidelines

## N+1 Queries

Avoid loading an association separately for every record in a loop.

Bad:

users.each do |user|
  user.posts.each do |post|
    puts post.title
  end
end

If users were loaded without their posts, this can produce an N+1
query problem.

Prefer eager loading when appropriate.

Example:

User.includes(:posts)

## Large Datasets

Avoid loading a very large Active Record relation into memory at once.

Bad:

User.all.each do |user|
  process(user)
end

Prefer:

User.find_each do |user|
  process(user)
end

## Database Queries

Avoid performing database queries repeatedly inside loops when the
same data can be retrieved efficiently beforehand.

## Selecting Columns

When only a small number of columns are required, consider selecting
only those columns instead of loading complete Active Record objects.

## Counting Records

Avoid loading records only to count them in Ruby.

Bad:

User.all.to_a.size
users.select { |u| u.active? }.count

Prefer counting in the database.

Good:

User.count
User.where(active: true).count

## Existence Checks

Avoid loading records just to check whether any exist.

Bad:

User.where(email: email).present?

Prefer an existence query that stops at the first match.

Good:

User.where(email: email).exists?

## Reading Single Columns

When only one column of many records is needed, avoid instantiating
full Active Record objects.

Bad:

User.all.map(&:email)

Prefer pluck.

Good:

User.pluck(:email)

## Bulk Writes

Avoid issuing one query per record when updating many rows with the
same change.

Bad:

users.each { |u| u.update(active: false) }

Prefer a single bulk update when callbacks and validations are not
required.

Good:

User.where(id: ids).update_all(active: false)