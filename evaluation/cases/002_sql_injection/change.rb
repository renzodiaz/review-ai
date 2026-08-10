email = params[:email]

User.where(
  "email = '#{email}'"
)