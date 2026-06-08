from hypothesis import given
from hypothesis import strategies as st

from app.api.helpers import calculate_total, round_currency


@given(st.floats(min_value=0.0, max_value=1_000_000.0))
def test_round_currency_always_two_decimal_places(value):
    result = round_currency(value)
    # Check that rounding to 2 decimal places matches
    assert round(result, 2) == result


@given(
    subtotal=st.floats(min_value=0.0, max_value=1_000_000.0),
    discount=st.floats(min_value=0.0, max_value=1_000_000.0),
)
def test_calculate_total_never_negative(subtotal, discount):
    total = calculate_total(subtotal, discount)
    assert total >= 0.0
    assert round(total, 2) == total
