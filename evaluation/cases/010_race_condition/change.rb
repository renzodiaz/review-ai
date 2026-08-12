def redeem
  coupon = Coupon.find(params[:id])

  if coupon.uses_left > 0
    coupon.update(uses_left: coupon.uses_left - 1)
    grant_reward
  end
end
