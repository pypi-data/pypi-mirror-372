def add(a: float, b: float) -> float:
    return a + b

def mean(values):
    values = list(values)
    if not values:
        return float('nan')
    return sum(values) / len(values)