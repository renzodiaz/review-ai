# Passwords

Never compare plaintext passwords.

Bad

user.password == params[:password]

Good

user.authenticate(params[:password])

----------------------------------

# SQL Injection

Avoid

User.where("email='#{params[:email]}'")

Use

User.where(email: params[:email])

----------------------------------

# Strong Parameters

Never

permit!

Prefer

permit(:name,:email)