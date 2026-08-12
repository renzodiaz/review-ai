def update
  @user = User.find(params[:id])
  @user.update(params[:user])
  redirect_to @user
end
