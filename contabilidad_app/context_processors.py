def cart_quantity(request):
    cart = request.session.get('cart', {})
    if not isinstance(cart, dict):
        return {'cart_quantity': 0}
    try:
        quantity = sum(max(0, int(value)) for value in cart.values())
    except (TypeError, ValueError):
        quantity = 0
    return {'cart_quantity': quantity}
