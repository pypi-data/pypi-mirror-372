def b2gb(bytes_: int, precision: int = 0) -> float:
    return float(round(bytes_ / 1024 / 1024 / 1024, precision))
