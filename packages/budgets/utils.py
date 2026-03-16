from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

USD_SCALE = Decimal("0.000001")
TOKENS_PER_CHAR_ESTIMATE = Decimal("0.25")


def to_decimal(value: str | float | int | Decimal) -> Decimal:
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def round_usd(value: Decimal) -> Decimal:
    return value.quantize(USD_SCALE, rounding=ROUND_HALF_UP)
