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

## Mass Assignment

Never pass raw request parameters directly into a model when creating
or updating records.

Bad:

User.new(params[:user])
user.update(params[:user])

This lets a request set any attribute, including sensitive ones such
as admin or role.

Prefer strong parameters that permit only the expected attributes.

Good:

user.update(params.require(:user).permit(:name, :email))

## Insecure File Access

Never build a filesystem path directly from user-controlled input.

Bad:

File.read("uploads/#{params[:filename]}")

A value such as ../../config/secrets can escape the intended
directory (path traversal).

Prefer validating the name and resolving it against a fixed base
directory.

Good:

base = Rails.root.join("uploads")
path = base.join(File.basename(params[:filename]))

## Command Injection

Never pass user-controlled input into a shell command string.

Bad:

system("convert #{params[:file]} output.png")

Prefer passing arguments as a list so no shell interpolation occurs.

Good:

system("convert", params[:file], "output.png")

## Secure Comparisons

Compare secrets, tokens, and digests using a constant-time comparison
to avoid timing attacks.

Bad:

token == params[:token]

Good:

ActiveSupport::SecurityUtils.secure_compare(token, params[:token])