users = User
  .includes(:orders)
  .where(active: true)

users.each do |user|
  puts user.orders.count
end
