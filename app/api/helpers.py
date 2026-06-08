def round_currency(value: float) -> float:
    """Round to 2 decimal places — always use this for money values."""
    return round(value, 2)


def calculate_total(subtotal: float, discount: float) -> float:
    """Total can never go below 0."""
    return round_currency(max(subtotal - discount, 0))
