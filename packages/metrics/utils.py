from decimal import Decimal, ROUND_HALF_UP

ZERO_USD = Decimal("0")


def round_usd(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)


def safe_decimal_divide(numerator: Decimal, denominator: int) -> Decimal:
    if denominator <= 0:
        return ZERO_USD
    return round_usd(numerator / Decimal(denominator))


def normalize_scope_key(scope_key: str | None) -> str:
    return scope_key or "default"
