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