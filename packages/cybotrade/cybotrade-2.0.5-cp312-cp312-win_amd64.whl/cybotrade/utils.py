from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP


def truncate_decimal(number: Decimal, precision: int) -> Decimal:
    if precision < 0:
        raise ValueError("Precision must be non-negative")
    quantizer = Decimal(f"1e-{precision}")
    return number.quantize(quantizer, rounding=ROUND_DOWN)


def round_to_tick(number: Decimal, tick_size: Decimal) -> Decimal:
    if tick_size <= 0:
        raise ValueError("Tick size must be positive")
    # Divide, round to nearest integer, then multiply back
    return (number / tick_size).to_integral_value(rounding=ROUND_HALF_UP) * tick_size


def extract_precision(number: Decimal) -> int:
    return int(abs(abs(number).log10()))
