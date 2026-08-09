# Ruby on Rails Security Guidelines

## Password Authentication

Never compare a plaintext password directly with a stored password.

Bad:

user.password == params[:password]

Prefer Rails authentication mechanisms such as has_secure_password
and authenticate.

## SQL Injection

Never interpolate user-controlled values directly into SQL strings.

Bad:

User.where("email = '#{params[:email]}'")

Prefer parameterized Active Record queries.

Good:

User.where(email: params[:email])

## Strong Parameters

Never use permit! when handling user input unless there is a very
specific and justified reason.

Prefer explicitly permitting only the parameters the application needs.

Good:

params.require(:user).permit(:name, :email)

## Authorization

Authentication and authorization are different concerns.

A user being authenticated does not mean they are authorized to
perform every action.

Always verify that the current user has permission to access or
modify the requested resource.