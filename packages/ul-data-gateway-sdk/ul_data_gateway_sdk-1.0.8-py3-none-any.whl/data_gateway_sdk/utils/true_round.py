def true_round(number: float, precision: int = 1) -> float:
    return round(int(number * 10 ** precision) / 10 ** precision, precision)
