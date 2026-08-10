class InvoiceCalculator
  def total(items)
    items.sum { |item| item.price * item.quantity }
  end
end
